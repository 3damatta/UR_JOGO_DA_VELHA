"""
Detector de Peças — UR3 Jogo da Velha
======================================
Captura frames da câmera, detecta peças do jogador (azul)
e do robô (laranja) usando filtros HSV, e publica jogadas
via MQTT para o Node-RED.

USO:
    python vision/detector.py

FLUXO:
    Câmera → HSV Filter → Localiza peças → Mapeia célula → MQTT Publish
"""

import cv2
import numpy as np
import json
import yaml
import time
import logging
import paho.mqtt.client as mqtt
from typing import Optional
import os
import base64

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [VISION] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# ── Carrega Configuração ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'config', 'settings.yaml'), encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

CAM_CFG  = cfg['camera']
DET_CFG  = cfg['detection']
MQTT_CFG = cfg['mqtt']
BOARD_SIZE = 300  # deve coincidir com board_calibration.py


class PieceDetector:
    """
    Detecta peças X (azul) e O (laranja) no tabuleiro e
    publica a célula onde foram posicionadas via MQTT.
    """

    def __init__(self, on_player_move=None, show_window=True):
        self.homography   = None
        self.board_state  = [''] * 9    # estado interno do tabuleiro
        self.stable_count = {}           # contagem de frames estáveis por célula
        self.last_player_cells = set()   # células do jogador já confirmadas
        self.mqtt_client  = None
        self.cap          = None
        self.on_player_move = on_player_move
        self.latest_frame = None
        self.show_window = show_window

        # HSV ranges
        self.player_lower = np.array(DET_CFG['player_hsv_lower'])
        self.player_upper = np.array(DET_CFG['player_hsv_upper'])
        self.robot_lower  = np.array(DET_CFG['robot_hsv_lower'])
        self.robot_upper  = np.array(DET_CFG['robot_hsv_upper'])

        self._load_calibration()
        if MQTT_CFG.get('enabled', True):
            self._setup_mqtt()

    # ── Calibração ────────────────────────────────────────────────────────────
    def _load_calibration(self):
        cal_file = os.path.join(BASE_DIR, CAM_CFG['calibration_file'])
        if not os.path.exists(cal_file):
            log.warning("Arquivo de calibração não encontrado. Execute board_calibration.py primeiro.")
            return
        with open(cal_file) as f:
            data = json.load(f)
        self.homography = np.array(data['homography'])
        log.info("✓ Calibração carregada")

    # ── MQTT ──────────────────────────────────────────────────────────────────
    def _setup_mqtt(self):
        self.mqtt_client = mqtt.Client(client_id="ur3_vision")
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        try:
            self.mqtt_client.connect(MQTT_CFG['broker'], MQTT_CFG['port'], keepalive=60)
            self.mqtt_client.loop_start()
        except Exception as e:
            log.error(f"Falha ao conectar ao broker MQTT: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            log.info(f"✓ MQTT conectado ao broker {MQTT_CFG['broker']}:{MQTT_CFG['port']}")
            # Inscreve no tópico de estado do jogo (Node-RED → Vision)
            client.subscribe(MQTT_CFG['topic_game_state'])
        else:
            log.error(f"MQTT falhou com código: {rc}")

    def _on_message(self, client, userdata, msg):
        """Recebe atualizações de estado do jogo do Node-RED."""
        try:
            payload = json.loads(msg.payload.decode())
            if 'board' in payload:
                self.board_state = payload['board']
                log.debug(f"Board atualizado: {self.board_state}")
        except Exception as e:
            log.warning(f"Erro ao processar mensagem MQTT: {e}")

    def _publish(self, topic: str, data: dict):
        if self.mqtt_client:
            self.mqtt_client.publish(topic, json.dumps(data))

    # ── Processamento de Imagem ───────────────────────────────────────────────
    def _warp_board(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Aplica homografia para obter vista frontal do tabuleiro."""
        if self.homography is None:
            return None
        warped = cv2.warpPerspective(frame, self.homography, (BOARD_SIZE, BOARD_SIZE))
        return warped

    def _detect_color(self, warped: np.ndarray,
                      lower: np.ndarray, upper: np.ndarray) -> list:
        """
        Detecta objetos de uma cor no espaço HSV.
        Retorna lista de (célula, área, centroide_x, centroide_y).
        """
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)

        # Morfologia para limpar ruído
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        cell_size = BOARD_SIZE / 3

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < DET_CFG['min_area']:
                continue
            M = cv2.moments(cnt)
            if M['m00'] == 0:
                continue
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            col = int(cx / cell_size)
            row = int(cy / cell_size)
            if 0 <= col < 3 and 0 <= row < 3:
                cell = row * 3 + col
                detections.append((cell, area, cx, cy))

        return detections

    def _pixel_to_cell(self, cx: float, cy: float) -> int:
        """Converte coordenada (px) no espaço normalizado para índice de célula 0-8."""
        cell_size = BOARD_SIZE / 3
        col = min(int(cx / cell_size), 2)
        row = min(int(cy / cell_size), 2)
        return row * 3 + col

    # ── Loop Principal ────────────────────────────────────────────────────────
    def run(self):
        self.cap = cv2.VideoCapture(CAM_CFG['index'])
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_CFG['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_CFG['height'])
        self.cap.set(cv2.CAP_PROP_FPS,          CAM_CFG['fps'])

        if not self.cap.isOpened():
            log.error("Não foi possível abrir a câmera")
            return

        log.info("=== Detector iniciado. Pressione 'Q' para sair ===")
        threshold = DET_CFG['stable_frames']
        publish_interval = 1.0   # segundos entre publicações de imagem
        last_img_publish = 0.0

        while True:
            ret, frame = self.cap.read()
            if not ret:
                log.warning("Frame vazio — aguardando câmera...")
                time.sleep(0.1)
                continue

            display = frame.copy()

            warped = self._warp_board(frame)
            if warped is None:
                cv2.putText(display, "SEM CALIBRACAO - Execute board_calibration.py",
                            (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                # ── Detecta peças do jogador (azul)
                player_dets = self._detect_color(warped, self.player_lower, self.player_upper)

                for cell, area, cx, cy in player_dets:
                    # Confirma após N frames estáveis
                    key = f"P{cell}"
                    self.stable_count[key] = self.stable_count.get(key, 0) + 1

                    if (self.stable_count[key] == threshold
                            and cell not in self.last_player_cells
                            and self.board_state[cell] == ''):
                        log.info(f"► Jogador colocou X na célula {cell}")
                        self.last_player_cells.add(cell)
                        self.board_state[cell] = 'X'
                        if self.on_player_move:
                            self.on_player_move(cell)
                        self._publish(MQTT_CFG['topic_player_move'], {
                            "cell": cell,
                            "symbol": "X",
                            "board": self.board_state,
                            "timestamp": time.time()
                        })

                # Reseta contador de células sem peça visível
                detected_player_cells = {d[0] for d in player_dets}
                for key in list(self.stable_count.keys()):
                    if key.startswith('P'):
                        c = int(key[1:])
                        if c not in detected_player_cells:
                            self.stable_count[key] = max(0, self.stable_count[key] - 2)

                # ── Visualização: grade no frame original
                self._draw_board_overlay(display, frame, warped, player_dets)
                self.latest_frame = display.copy()

                # ── Publica imagem anotada periodicamente
                now = time.time()
                if now - last_img_publish > publish_interval:
                    _, buf = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 60])
                    b64 = base64.b64encode(buf).decode()
                    self._publish(MQTT_CFG['topic_board_image'], {"image": b64})
                    last_img_publish = now

            if self.show_window:
                if self.latest_frame is not None:
                    cv2.imshow("UR3 - Detecção de Peças", self.latest_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                time.sleep(0.03)

        self.cap.release()
        cv2.destroyAllWindows()
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

    def _draw_board_overlay(self, display, original, warped, player_dets):
        """Desenha grade e indicadores no frame de display."""
        h, w = original.shape[:2]

        # Miniatura do tabuleiro normalizado no canto superior direito
        thumb = cv2.resize(warped, (150, 150))
        display[10:160, w-160:w-10] = thumb

        # Grade sobre a miniatura
        for i in range(1, 3):
            y = 10 + i * 50
            x = (w - 160) + i * 50
            cv2.line(display, (w-160, y), (w-10, y), (255, 255, 0), 1)
            cv2.line(display, (x, 10), (x, 160), (255, 255, 0), 1)

        # Células detectadas (jogador)
        for cell, _, cx, cy in player_dets:
            row, col = divmod(cell, 3)
            tx = (w - 160) + col * 50 + 25
            ty = 10 + row * 50 + 35
            cv2.putText(display, "X", (tx-10, ty),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 80, 0), 2)

        # Estado atual do tabuleiro no canto superior esquerdo
        cv2.rectangle(display, (0, 0), (180, 30), (0, 0, 0), -1)
        cv2.putText(display, f"Board: {self.board_state}",
                    (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)


if __name__ == '__main__':
    detector = PieceDetector()
    detector.run()
