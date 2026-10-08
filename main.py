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
import json
import numpy as np
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

@app.route('/api/reset', methods=['GET', 'POST'])
def api_reset():
    data = request.get_json(silent=True) or {}
    difficulty = data.get('difficulty') or request.args.get('difficulty')
    if difficulty:
        game_manager.set_difficulty(difficulty)
    game_manager.reset()
    return jsonify({"status": "success", "state": game_manager.get_state()})

@app.route('/api/difficulty', methods=['GET', 'POST'])
def api_difficulty():
    data = request.get_json(silent=True) or {}
    difficulty = data.get('difficulty') or request.args.get('difficulty')
    if not difficulty:
        return jsonify({"error": "Parâmetro 'difficulty' ausente"}), 400
    
    success = game_manager.set_difficulty(difficulty)
    if not success:
        return jsonify({"error": f"Dificuldade inválida: '{difficulty}'. Use 'easy', 'medium', 'hard' ou 'impossible'."}), 400
    return jsonify({"status": "success", "state": game_manager.get_state()})

@app.route('/api/move', methods=['GET', 'POST'])
def api_move():
    data = request.get_json(silent=True) or {}
    cell_val = data.get('cell') if data.get('cell') is not None else request.args.get('cell')
    if cell_val is None:
        return jsonify({"error": "Parâmetro 'cell' ausente"}), 400
    
    try:
        cell = int(cell_val)
    except ValueError:
        return jsonify({"error": "Célula inválida"}), 400

    success = game_manager.player_move(cell)
    return jsonify({"success": success, "state": game_manager.get_state()})

@app.route('/api/positions', methods=['GET', 'POST'])
def api_positions():
    from scripts.update_positions import load_positions, save_positions, deg_to_rad, rad_to_deg
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        
        # Suporte a salvamento em lote de todas as posições
        all_positions = data.get('all_positions')
        if all_positions:
            try:
                pos_data = load_positions()
                if 'home' in all_positions and 'degrees' in all_positions['home']:
                    pos_data['home_pose']['joint_angles'] = deg_to_rad([float(d) for d in all_positions['home']['degrees']])
                if 'pick' in all_positions and 'degrees' in all_positions['pick']:
                    pos_data['pick']['joint_angles'] = deg_to_rad([float(d) for d in all_positions['pick']['degrees']])
                if 'cells' in all_positions and isinstance(all_positions['cells'], dict):
                    for ck, cv in all_positions['cells'].items():
                        if str(ck) in pos_data.get('board', {}).get('cells', {}) and 'degrees' in cv:
                            pos_data['board']['cells'][str(ck)]['joint_angles'] = deg_to_rad([float(d) for d in cv['degrees']])
                save_positions(pos_data)
                if game_manager and game_manager.robot:
                    game_manager.robot.pos = pos_data
                return jsonify({"status": "success", "message": "Todas as posições foram atualizadas com sucesso!"})
            except Exception as e:
                return jsonify({"error": f"Erro ao atualizar posições em lote: {str(e)}"}), 500

        target = data.get('target')      # 'home', 'pick', or '0'..'8'
        degrees = data.get('degrees')    # [b, o, c, p1, p2, p3]

        if not target or not degrees or len(degrees) != 6:
            return jsonify({"error": "Parâmetros 'target' e 'degrees' (6 valores) são obrigatórios"}), 400

        try:
            degs = [float(d) for d in degrees]
            rads = deg_to_rad(degs)
            pos_data = load_positions()

            if target == 'home':
                pos_data['home_pose']['joint_angles'] = rads
            elif target == 'pick':
                pos_data['pick']['joint_angles'] = rads
            elif str(target) in pos_data.get('board', {}).get('cells', {}):
                pos_data['board']['cells'][str(target)]['joint_angles'] = rads
            else:
                return jsonify({"error": f"Alvo inválido: '{target}'"}), 400

            save_positions(pos_data)

            # Recarrega em memória se o controlador do robô estiver ativo
            if game_manager and game_manager.robot:
                game_manager.robot.pos = pos_data

            return jsonify({"status": "success", "target": target, "degrees": degs, "radians": rads})
        except Exception as e:
            return jsonify({"error": f"Erro ao atualizar posição: {str(e)}"}), 500

    # GET: retorna posições formatadas com graus e radianos
    try:
        pos_data = load_positions()
        res = {
            "home": {
                "radians": pos_data['home_pose']['joint_angles'],
                "degrees": rad_to_deg(pos_data['home_pose']['joint_angles'])
            },
            "pick": {
                "radians": pos_data['pick']['joint_angles'],
                "degrees": rad_to_deg(pos_data['pick']['joint_angles'])
            },
            "cells": {}
        }
        for k, v in pos_data.get('board', {}).get('cells', {}).items():
            res["cells"][k] = {
                "label": v.get("label", ""),
                "radians": v.get("joint_angles", []),
                "degrees": rad_to_deg(v.get("joint_angles", []))
            }
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def api_test():
    from scripts.update_positions import load_positions, deg_to_rad
    data = request.get_json(silent=True) or {}
    action = data.get('action')

    if not action:
        return jsonify({"error": "Parâmetro 'action' é obrigatório"}), 400

    robot = game_manager.robot if game_manager else None

    try:
        if action == 'home':
            if not robot:
                return jsonify({"status": "simulated", "message": "[SIMULAÇÃO] Robô offline. Comando Home executado."})
            success = robot.go_home()
            return jsonify({"status": "success" if success else "error", "message": "Robô movido para HOME com sucesso!" if success else "Falha ao mover robô para HOME."})

        elif action == 'gripper_open':
            if not robot:
                return jsonify({"status": "simulated", "message": "[SIMULAÇÃO] Garra OnRobot aberta."})
            robot._gripper_open()
            return jsonify({"status": "success", "message": "Garra OnRobot aberta com sucesso!"})

        elif action == 'gripper_close':
            if not robot:
                return jsonify({"status": "simulated", "message": "[SIMULAÇÃO] Garra OnRobot fechada."})
            robot._gripper_close()
            return jsonify({"status": "success", "message": "Garra OnRobot fechada com sucesso!"})

        elif action == 'read_joints':
            from scripts.update_positions import rad_to_deg
            from ur3.robot_controller import UR3Controller, ROBOT_CFG
            
            rads = None
            if robot:
                rads = robot.get_current_joints()

            if not rads:
                # Tenta criar leitor temporário caso o robô estivesse offline na inicialização
                try:
                    tmp_robot = UR3Controller()
                    rads = tmp_robot.get_current_joints()
                    if rads and game_manager:
                        game_manager.robot = tmp_robot
                        log.info("✓ Robô UR3 reconectado com sucesso no endpoint /api/test!")
                except Exception as e:
                    log.warning(f"Tentativa de conexão temporária ao UR3 falhou: {e}")

            if rads:
                degs = rad_to_deg(rads)
                log.info(f"✓ Posição real capturada do UR3: {degs}°")
                return jsonify({
                    "status": "success",
                    "radians": rads,
                    "degrees": degs,
                    "message": "Posição real lida do robô com sucesso!"
                })

            log.error(f"Não foi possível ler as articulações reais do robô no IP {ROBOT_CFG['ip']}")
            return jsonify({
                "status": "error",
                "error": f"Sem conexão com o robô UR3 no IP {ROBOT_CFG['ip']}. Verifique se o cabo Ethernet está conectado e o robô está ligado.",
                "message": f"Erro de comunicação com o robô no IP {ROBOT_CFG['ip']}."
            }), 502



        elif action == 'move_joint':
            target = data.get('target')
            degrees = data.get('degrees')
            if degrees and len(degrees) == 6:
                rads = deg_to_rad([float(d) for d in degrees])
            elif target:
                pos_data = load_positions()
                if target == 'home':
                    rads = pos_data['home_pose']['joint_angles']
                elif target == 'pick':
                    rads = pos_data['pick']['joint_angles']
                elif str(target) in pos_data.get('board', {}).get('cells', {}):
                    rads = pos_data['board']['cells'][str(target)]['joint_angles']
                else:
                    return jsonify({"error": f"Alvo inválido: '{target}'"}), 400
            else:
                return jsonify({"error": "Informe 'target' ou 'degrees' (6 valores)"}), 400

            if not robot:
                return jsonify({"status": "simulated", "message": f"[SIMULAÇÃO] Robô movido para articulações: {rads}"})

            success = robot.move_to_joints(rads)
            return jsonify({"status": "success" if success else "error", "message": "Movimento de articulação concluído com sucesso!" if success else "Falha na movimentação do robô."})

        elif action == 'move_cell':
            cell = data.get('cell')
            if cell is None:
                return jsonify({"error": "Parâmetro 'cell' (0-8) é obrigatório"}), 400
            cell = int(cell)
            if not robot:
                return jsonify({"status": "simulated", "message": f"[SIMULAÇÃO] Sequência Pick & Place para célula {cell} simulada com sucesso."})

            success = robot.place_piece(cell)
            return jsonify({"status": "success" if success else "error", "message": f"Peça posicionada na célula {cell} com sucesso!" if success else f"Falha ao posicionar peça na célula {cell}."})

        elif action == 'dry_run':
            cell = int(data.get('cell', 0))
            if robot:
                script = robot.build_place_script(cell)
            else:
                from ur3.robot_controller import UR3Controller
                tmp_ctrl = UR3Controller()
                script = tmp_ctrl.build_place_script(cell)
            return jsonify({"status": "success", "cell": cell, "script": script})

        else:
            return jsonify({"error": f"Ação de teste inválida: '{action}'"}), 400

    except Exception as e:
        log.error(f"Erro em /api/test: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/calibrate', methods=['GET', 'POST'])
def api_calibrate():
    cal_file = os.path.join(BASE_DIR, 'config', 'calibration.json')
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        points = data.get('points')  # [[x0, y0], [x1, y1], [x2, y2], [x3, y3]]
        if not points or len(points) != 4:
            return jsonify({"error": "Parâmetro 'points' com exatamente 4 pontos é obrigatório"}), 400

        try:
            pts = np.float32(points)
            board_size = 300
            dst = np.float32([
                [0, 0],
                [board_size, 0],
                [board_size, board_size],
                [0, board_size]
            ])
            H, _ = cv2.findHomography(pts, dst)

            cal_data = {
                "corners": points,
                "homography": H.tolist(),
                "board_size": board_size
            }
            os.makedirs(os.path.dirname(cal_file), exist_ok=True)
            with open(cal_file, 'w', encoding='utf-8') as f:
                json.dump(cal_data, f, indent=2)

            global detector
            if detector:
                detector.homography = H
                log.info("✓ Nova calibração salva via Web e aplicada na memória do detector!")

            return jsonify({"status": "success", "calibration": cal_data})
        except Exception as e:
            log.error(f"Erro ao calcular/salvar calibração: {e}")
            return jsonify({"error": f"Erro na calibração: {str(e)}"}), 500

    # GET: retorna a calibração atual se existir
    if os.path.exists(cal_file):
        try:
            with open(cal_file, encoding='utf-8') as f:
                return jsonify(json.load(f))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"corners": [], "homography": None, "board_size": 300})

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

@app.route('/api/stream/raw')
def api_stream_raw():
    def generate():
        while True:
            global detector
            frame = None
            if detector:
                with detector.jpeg_lock:
                    frame = getattr(detector, 'latest_raw_jpeg', None) or detector.latest_jpeg

            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                if _fallback_jpeg is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + _fallback_jpeg + b'\r\n')
            time.sleep(0.06)
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
