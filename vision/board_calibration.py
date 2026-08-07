"""
Calibração do Tabuleiro — UR3 Jogo da Velha
============================================
Interface interativa para marcar os 4 cantos do tabuleiro físico
na imagem da câmera e salvar a homografia.

USO:
    python vision/board_calibration.py

INSTRUÇÕES:
    1. Posicione a câmera acima do tabuleiro (vista aérea)
    2. Clique nos 4 cantos do tabuleiro:
       - Superior-Esquerdo → Superior-Direito → Inferior-Direito → Inferior-Esquerdo
    3. A grade será desenhada por cima para validação
    4. Pressione 'S' para salvar | 'R' para refazer | 'Q' para sair
"""

import cv2
import numpy as np
import json
import os
import sys
import time

CALIBRATION_FILE = "config/calibration.json"
BOARD_SIZE = 300  # Tamanho do tabuleiro normalizado (px)


class BoardCalibrator:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.points = []          # 4 cantos clicados
        self.homography = None    # Matriz de homografia
        self.cap = None
        self.frame = None
        self.window_name = "UR3 - Calibração do Tabuleiro"

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
            print(f"  Ponto {len(self.points)}/4: ({x}, {y})")
            if len(self.points) == 4:
                self._compute_homography()

    def _compute_homography(self):
        """Calcula homografia para transformar perspectiva em vista frontal."""
        src = np.float32(self.points)
        # Destino: quadrado normalizado de BOARD_SIZE x BOARD_SIZE
        dst = np.float32([
            [0, 0],
            [BOARD_SIZE, 0],
            [BOARD_SIZE, BOARD_SIZE],
            [0, BOARD_SIZE]
        ])
        self.homography, _ = cv2.findHomography(src, dst)
        print("\n✓ Homografia calculada. Pressione 'S' para salvar ou 'R' para refazer.")

    def _draw_overlay(self, frame: np.ndarray) -> np.ndarray:
        """Desenha pontos clicados e grade 3x3 sobre o frame."""
        overlay = frame.copy()

        # Desenha pontos clicados
        labels = ["SE", "SD", "ID", "IE"]
        colors = [(0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)]
        for i, pt in enumerate(self.points):
            cv2.circle(overlay, pt, 8, colors[i], -1)
            cv2.putText(overlay, labels[i], (pt[0]+10, pt[1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors[i], 2)

        # Se 4 pontos, desenha linhas do polígono
        if len(self.points) == 4:
            pts = np.array(self.points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(overlay, [pts], True, (0, 255, 0), 2)

            # Desenha grade 3x3 no espaço do tabuleiro
            if self.homography is not None:
                H_inv = np.linalg.inv(self.homography)
                cell = BOARD_SIZE / 3
                # Linhas horizontais
                for i in range(1, 3):
                    p1 = self._warp_point((0, i * cell), H_inv)
                    p2 = self._warp_point((BOARD_SIZE, i * cell), H_inv)
                    cv2.line(overlay, p1, p2, (255, 255, 0), 2)
                # Linhas verticais
                for i in range(1, 3):
                    p1 = self._warp_point((i * cell, 0), H_inv)
                    p2 = self._warp_point((i * cell, BOARD_SIZE), H_inv)
                    cv2.line(overlay, p1, p2, (255, 255, 0), 2)

                # Numera as células (0-8)
                for idx in range(9):
                    row, col = divmod(idx, 3)
                    cx = (col + 0.5) * cell
                    cy = (row + 0.5) * cell
                    pt = self._warp_point((cx, cy), H_inv)
                    cv2.putText(overlay, str(idx), (pt[0]-8, pt[1]+8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Instruções
        n = len(self.points)
        msgs = [
            "Clique no canto SUPERIOR-ESQUERDO do tabuleiro",
            "Clique no canto SUPERIOR-DIREITO",
            "Clique no canto INFERIOR-DIREITO",
            "Clique no canto INFERIOR-ESQUERDO",
        ]
        if n < 4:
            msg = msgs[n]
            color = (0, 200, 255)
        elif self.homography is not None:
            msg = "[S] Salvar  [R] Refazer  [Q] Sair"
            color = (0, 255, 0)
        else:
            msg = "Calculando..."
            color = (255, 255, 0)

        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 40), (0, 0, 0), -1)
        cv2.putText(overlay, msg, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return overlay

    @staticmethod
    def _warp_point(pt, H_inv) -> tuple:
        """Transforma um ponto do espaço normalizado para o espaço da imagem."""
        p = np.array([[[pt[0], pt[1]]]], dtype=np.float32)
        result = cv2.perspectiveTransform(p, H_inv)
        return (int(result[0][0][0]), int(result[0][0][1]))

    def save(self):
        """Salva homografia e pontos de calibração em JSON."""
        os.makedirs(os.path.dirname(CALIBRATION_FILE), exist_ok=True)
        data = {
            "corners": self.points,
            "homography": self.homography.tolist(),
            "board_size": BOARD_SIZE
        }
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n[OK] Calibracao salva em: {CALIBRATION_FILE}")

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.cap.isOpened():
            print(f"[ERRO] Nao foi possivel abrir camera indice {self.camera_index}")
            return False

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Loop de warm-up para aguardar um frame valido da camera USB
        frame = None
        for _ in range(60):
            ret, temp_frame = self.cap.read()
            if ret and temp_frame is not None:
                frame = temp_frame
                break
            time.sleep(0.03)
            
        if frame is not None:
            cv2.imshow(self.window_name, frame)
            cv2.waitKey(100)
        else:
            print("[ERRO] Nao foi possivel ler nenhum frame valido da camera")
            self.cap.release()
            return False
            
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        print("\n=== Calibracao do Tabuleiro ===")
        print("Clique nos 4 cantos do tabuleiro fisico na ordem:")
        print("  1. Superior-Esquerdo")
        print("  2. Superior-Direito")
        print("  3. Inferior-Direito")
        print("  4. Inferior-Esquerdo\n")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERRO] Falha ao capturar frame")
                break

            self.frame = frame
            display = self._draw_overlay(frame)
            cv2.imshow(self.window_name, display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.points = []
                self.homography = None
                print("\n[REFAZENDO] Refazendo calibracao...")
            elif key == ord('s') and self.homography is not None:
                self.save()
                break

        self.cap.release()
        cv2.destroyAllWindows()
        return self.homography is not None


if __name__ == '__main__':
    cam_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    calibrator = BoardCalibrator(camera_index=cam_idx)
    success = calibrator.run()
    sys.exit(0 if success else 1)
