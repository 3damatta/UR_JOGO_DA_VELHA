"""
Orquestrador Principal — UR3 Jogo da Velha (Sem Node-RED)
=========================================================
Inicia o detector de visão, o controlador do robô e o
servidor Flask em threads separadas. Roda no Raspberry Pi.

USO:
    python main.py
    python main.py --no-vision   # sem câmera (testes manuais)
"""

import threading
import logging
import signal
import sys
import argparse
import time
import yaml
import os
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import cv2

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MAIN] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carrega configurações do settings.yaml
def load_config():
    with open(os.path.join(BASE_DIR, 'config', 'settings.yaml'), encoding='utf-8') as f:
        return yaml.safe_load(f)

cfg = load_config()
detector = None
game_manager = None

# ==============================================================================
# CLASSE GERENCIADORA DO JOGO
# ==============================================================================
class GameManager:
    def __init__(self, robot_controller=None):
        self.board = [''] * 9
        self.game_active = False
        self.status = 'idle'  # idle, ongoing, robot_moving, robot_wins, player_wins, draw
        self.last_player_move = -1
        self.last_robot_move = -1
        self.winning_line = []
        self.robot = robot_controller
        self.difficulty = cfg.get('game', {}).get('difficulty', 'medium')
        self.lock = threading.Lock()
        log.info(f"GameManager inicializado. Dificuldade: {self.difficulty}")

    def get_state(self):
        with self.lock:
            return {
                "board": self.board,
                "game_active": self.game_active,
                "status": self.status,
                "last_player_move": self.last_player_move,
                "last_robot_move": self.last_robot_move,
                "winning_line": self.winning_line,
                "difficulty": self.difficulty
            }

    def set_difficulty(self, difficulty: str):
        with self.lock:
            if difficulty in ['easy', 'medium', 'hard', 'impossible']:
                self.difficulty = difficulty
                log.info(f"Dificuldade alterada para: {difficulty}")
                return True
            return False

    def reset(self):
        with self.lock:
            self.board = [''] * 9
            self.game_active = True
            self.status = 'ongoing'
            self.last_player_move = -1
            self.last_robot_move = -1
            self.winning_line = []
            
            # Limpa estado do detector de peças em tempo real
            global detector
            if detector:
                detector.board_state = [''] * 9
                detector.last_player_cells = set()
                detector.stable_count = {}
            
            log.info("✓ Jogo reiniciado. Tabuleiro limpo.")
            
            # Envia robô para a pose home em segundo plano
            if self.robot:
                threading.Thread(target=self._send_robot_home, daemon=True).start()

    def _send_robot_home(self):
        try:
            self.robot.go_home()
        except Exception as e:
            log.error(f"Erro ao mandar robô para home: {e}")

    def player_move(self, cell):
        with self.lock:
            if not self.game_active or self.status != 'ongoing':
                log.warning(f"Movimento na célula {cell} ignorado: jogo inativo ou robô jogando.")
                return False
            if cell < 0 or cell > 8 or self.board[cell] != '':
                log.warning(f"Movimento na célula {cell} rejeitado: inválida ou já ocupada.")
                return False

            log.info(f"► Jogada registrada para o Jogador: célula {cell}")
            self.board[cell] = 'X'
            self.last_player_move = cell

            # Sincroniza estado com o detector se veio da UI/Manual
            global detector
            if detector:
                detector.board_state[cell] = 'X'
                detector.last_player_cells.add(cell)

            # Verifica vitória do jogador
            self._check_game_over()
            if not self.game_active:
                return True

            # Inicia turno do robô
            self.status = 'robot_moving'
            threading.Thread(target=self._robot_turn, daemon=True).start()
            return True

    def _robot_turn(self):
        try:
            from game.minimax import best_move
            
            # 1. Calcula a jogada via Minimax (respeitando a dificuldade configurada)
            with self.lock:
                robot_cell = best_move(self.board, difficulty=self.difficulty)

            if robot_cell == -1:
                with self.lock:
                    self.status = 'draw'
                    self.game_active = False
                log.info("Fim de Jogo: Deu Velha (Empate)")
                return

            log.info(f"► Robô escolheu a célula {robot_cell} (Modo: {self.difficulty}). Iniciando movimento físico...")

            # 2. Executa movimento físico do robô (bloqueante para o robô, assíncrono para a API)
            if self.robot:
                success = self.robot.place_piece(robot_cell)
                if not success:
                    log.error("Erro na movimentação do robô. Prosseguindo logicamente.")

            # 3. Atualiza estado após conclusão da movimentação
            with self.lock:
                self.board[robot_cell] = 'O'
                self.last_robot_move = robot_cell
                
                global detector
                if detector:
                    detector.board_state[robot_cell] = 'O'

                self._check_game_over()
                if self.game_active:
                    self.status = 'ongoing'
                    log.info("Aguardando jogada do Jogador...")
        except Exception as e:
            log.error(f"Erro no turno do robô: {e}")
            with self.lock:
                self.status = 'ongoing'

    def _check_game_over(self):
        from game.minimax import game_status
        res = game_status(self.board)
        if res['status'] != 'ongoing':
            self.status = res['status']
            self.game_active = False
            self.winning_line = res.get('winning_line') or []
            log.info(f"=== FIM DE JOGO: {self.status.upper()} ===")


# ==============================================================================
# CONFIGURAÇÃO DO SERVIDOR API FLASK
# ==============================================================================
app = Flask(__name__)
CORS(app)

@app.route('/api/state', methods=['GET'])
def api_state():
    return jsonify(game_manager.get_state())

@app.route('/api/reset', methods=['POST'])
def api_reset():
    data = request.get_json() or {}
    difficulty = data.get('difficulty')
    if difficulty:
        game_manager.set_difficulty(difficulty)
    game_manager.reset()
    return jsonify({"status": "success", "state": game_manager.get_state()})

@app.route('/api/difficulty', methods=['POST'])
def api_difficulty():
    data = request.get_json() or {}
    difficulty = data.get('difficulty') or request.args.get('difficulty')
    if not difficulty:
        return jsonify({"error": "Parâmetro 'difficulty' ausente"}), 400
    
    success = game_manager.set_difficulty(difficulty)
    if not success:
        return jsonify({"error": f"Dificuldade inválida: '{difficulty}'. Use 'easy', 'medium', 'hard' ou 'impossible'."}), 400
    return jsonify({"status": "success", "state": game_manager.get_state()})

@app.route('/api/move', methods=['POST'])
def api_move():
    data = request.get_json() or {}
    cell = data.get('cell')
    if cell is None:
        return jsonify({"error": "Parâmetro 'cell' ausente"}), 400
    
    success = game_manager.player_move(cell)
    return jsonify({"success": success, "state": game_manager.get_state()})

# Pré-codifica a imagem de fallback "Sem conexao de camera" uma única vez na inicialização
_fallback_jpeg = None
try:
    import numpy as np
    _fallback_img = np.zeros((240, 320, 3), dtype=np.uint8) + 50
    cv2.putText(_fallback_img, "Sem conexao de camera", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    _ret, _jpeg = cv2.imencode('.jpg', _fallback_img)
    if _ret:
        _fallback_jpeg = _jpeg.tobytes()
except Exception as e:
    log.error(f"Erro ao inicializar imagem de fallback: {e}")

@app.route('/api/stream')
def api_stream():
    def generate():
        while True:
            global detector
            frame = None
            if detector:
                with detector.jpeg_lock:
                    frame = detector.latest_jpeg

            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                if _fallback_jpeg is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + _fallback_jpeg + b'\r\n')
            time.sleep(0.06)  # ~15 FPS
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ==============================================================================
# INICIALIZAÇÃO DOS COMPONENTES
# ==============================================================================
def run_vision_thread(on_player_move):
    global detector
    try:
        from vision.detector import PieceDetector
        detector = PieceDetector(on_player_move=on_player_move, show_window=False)
        detector.run()
    except Exception as e:
        log.error(f"Erro ao iniciar o detector de visão: {e}")

def main():
    parser = argparse.ArgumentParser(description="UR3 Jogo da Velha")
    parser.add_argument('--no-vision', action='store_true', help='Desativa o processamento de câmera')
    args = parser.parse_args()

    # Inicializa controlador do UR3
    robot_controller = None
    try:
        from ur3.robot_controller import UR3Controller
        robot_controller = UR3Controller()
    except Exception as e:
        log.error(f"Não foi possível conectar ao UR3 (está em dry-run/modo manual): {e}")

    # Inicializa o GameManager
    global game_manager
    game_manager = GameManager(robot_controller)

    # Função de callback chamada pela visão
    def on_vision_player_move(cell):
        game_manager.player_move(cell)

    # Inicia detector de visão em thread
    if not args.no_vision:
        vision_thread = threading.Thread(
            target=run_vision_thread,
            args=(on_vision_player_move,),
            daemon=True,
            name="Vision"
        )
        vision_thread.start()
        log.info("✓ Thread de Visão iniciada.")
    else:
        log.info("⚠ Modo sem visão ativo. Utilize a interface web para interagir.")

    # Executa o servidor Flask na porta configurada
    api_host = cfg['web']['api_host']
    api_port = cfg['web']['api_port']
    log.info(f"Iniciando API Server em http://{api_host}:{api_port}")
    
    # Executa o Flask (com threaded=True para suportar streaming de vídeo em paralelo com a API)
    app.run(host=api_host, port=api_port, threaded=True, debug=False)

if __name__ == '__main__':
    # Captura Ctrl+C
    def _shutdown(sig, frame):
        log.info("\nEncerrando sistema de jogo...")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    main()
