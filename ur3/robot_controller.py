"""
Controlador do UR3 — Jogo da Velha (Versão RTDE + onRobot Gripper)
=================================================================
Mapeia o movimento e controle físico do UR3 utilizando a biblioteca ur_rtde
(Real-Time Data Exchange) e a garra OnRobot RG2 utilizando a biblioteca onRobot.

Se as bibliotecas não estiverem instaladas ou o robô estiver offline,
o controlador entra em modo de simulação (dry-run).
"""

import time
import logging
import yaml
import os
import json
import argparse

# ── Imports Condicionais para Portabilidade ────────────────────────────────────
try:
    import rtde_control
    HAS_RTDE = True
except ImportError:
    HAS_RTDE = False

try:
    import onRobot.gripper as gripper
    HAS_ONROBOT = True
except ImportError:
    HAS_ONROBOT = False

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [UR3-RTDE] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'config', 'settings.yaml'), encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

ROBOT_CFG   = cfg['robot']
GRIPPER_CFG = cfg['gripper']
APPROACH_OFFSET_M = 0.050  # 50 mm acima


class UR3Controller:
    def __init__(self):
        self.ip    = ROBOT_CFG['ip']
        self.speed = ROBOT_CFG['speed']
        self.accel = ROBOT_CFG['acceleration']
        
        # Carrega as posições calibradas do JSON
        pos_file = os.path.join(BASE_DIR, 'ur3', 'positions_config.json')
        with open(pos_file) as f:
            self.pos = json.load(f)

        self.rtde_c = None
        self.rg_gripper = None
        self.dry_run_mode = False

        # Inicializa o controle do robô (ur_rtde)
        if HAS_RTDE:
            log.info(f"Conectando ao UR3 RTDE em {self.ip}...")
            try:
                self.rtde_c = rtde_control.RTDEControlInterface(self.ip)
                log.info("✓ Conectado ao UR3 via RTDE!")
            except Exception as e:
                log.warning(f"Não foi possível conectar ao UR3 via RTDE ({e}). Rodando em modo de simulação.")
                self.dry_run_mode = True
        else:
            log.warning("Biblioteca 'ur_rtde' não encontrada. Rodando em modo de simulação.")
            self.dry_run_mode = True

        # Inicializa o controle da garra (onRobot)
        if HAS_ONROBOT:
            log.info("Inicializando garra OnRobot RG2...")
            try:
                # O ID da garra é configurado como 0 (padrão do canal da ferramenta)
                self.rg_gripper = gripper.RG(self.ip, 0)
                log.info("✓ Garra OnRobot RG2 inicializada!")
            except Exception as e:
                log.warning(f"Não foi possível inicializar a garra OnRobot ({e}). Rodando em simulação.")
        else:
            log.warning("Biblioteca 'onRobot' não encontrada. Rodando em modo de simulação para a garra.")

    # ── Métodos de Controle da Garra ──────────────────────────────────────────
    def _gripper_close(self):
        """Fecha a garra na largura da peça."""
        width = GRIPPER_CFG['close_width']
        force = GRIPPER_CFG['force']
        wait = GRIPPER_CFG['wait_time']
        
        log.info(f"Garra: Fechando para {width}mm com {force}N...")
        if self.rg_gripper and not self.dry_run_mode:
            self.rg_gripper.rg_grip(width, float(force))
            time.sleep(wait)
        else:
            time.sleep(wait)
            log.info("Garra: [SIMULADO] Garra fechada.")

    def _gripper_open(self):
        """Abre a garra na largura máxima para soltar."""
        width = GRIPPER_CFG['open_width']
        force = GRIPPER_CFG['force']
        wait = GRIPPER_CFG['wait_time']
        
        log.info(f"Garra: Abrindo para {width}mm...")
        if self.rg_gripper and not self.dry_run_mode:
            self.rg_gripper.rg_grip(width, float(force))
            time.sleep(wait)
        else:
            time.sleep(wait)
            log.info("Garra: [SIMULADO] Garra aberta.")

    # ── Métodos de Movimentação ───────────────────────────────────────────────
    def go_home(self) -> bool:
        """Move o robô de volta para a pose Home."""
        joints = self.pos['home_pose']['joint_angles']
        log.info("Movendo robô para pose HOME...")
        
        if self.rtde_c and not self.dry_run_mode:
            try:
                # MoveJ espera os ângulos em radianos
                # Parâmetros: (q, speed, acceleration, asynchronous=False)
                self.rtde_c.moveJ(joints, 1.0, 1.2)
                log.info("✓ Chegou na HOME.")
                return True
            except Exception as e:
                log.error(f"Falha ao mover para HOME via RTDE: {e}")
                return False
        else:
            time.sleep(2.0)
            log.info("✓ [SIMULADO] Chegou na HOME.")
            return True

    def place_piece(self, cell: int) -> bool:
        """
        Executa a sequência de 10 passos para posicionar a peça:
        HOME -> Acima do Pick -> Desce Pick -> Fecha Garra -> Sobe Pick ->
        Acima da Célula -> Desce Célula -> Abre Garra -> Sobe Célula -> HOME
        """
        if cell < 0 or cell > 8:
            log.error(f"Célula inválida: {cell}")
            return False

        # Carrega dados geométricos
        pick_data = self.pos['pick']
        board_data = self.pos['board']
        cell_data = board_data['cells'][str(cell)]
        orient = board_data['orientation']
        joints_home = self.pos['home_pose']['joint_angles']

        # Montagem dos pontos Cartesianos [X, Y, Z, Rx, Ry, Rz]
        # Posições de PICK (estoque)
        p_pick_above = [pick_data['x'], pick_data['y'], pick_data['z'] + APPROACH_OFFSET_M, 
                        pick_data['rx'], pick_data['ry'], pick_data['rz']]
        p_pick       = [pick_data['x'], pick_data['y'], pick_data['z'], 
                        pick_data['rx'], pick_data['ry'], pick_data['rz']]

        # Posições de PLACE (célula alvo)
        p_place_above = [cell_data['x'], cell_data['y'], board_data['z_place'] + APPROACH_OFFSET_M,
                         orient[0], orient[1], orient[2]]
        p_place       = [cell_data['x'], cell_data['y'], board_data['z_place'],
                         orient[0], orient[1], orient[2]]

        log.info(f"Iniciando ciclo de pick & place para célula {cell} ({cell_data['label']})...")

        if self.rtde_c and not self.dry_run_mode:
            try:
                # [1] HOME
                log.info("[1/10] Movendo para HOME...")
                self.rtde_c.moveJ(joints_home, 1.0, 1.2)

                # [2] Acima do Pick
                log.info("[2/10] Aproximando do Estoque (PICK)...")
                self.rtde_c.moveL(p_pick_above, self.speed, self.accel)

                # [3] Descer no Pick
                log.info("[3/10] Descendo até a peça...")
                self.rtde_c.moveL(p_pick, 0.12, self.accel) # velocidade lenta

                # [4] Pegar peça
                log.info("[4/10] Capturando peça...")
                self._gripper_close()

                # [5] Subir do Pick
                log.info("[5/10] Elevando peça...")
                self.rtde_c.moveL(p_pick_above, 0.12, self.accel)

                # [6] Acima da Célula
                log.info(f"[6/10] Transladando para célula {cell}...")
                self.rtde_c.moveL(p_place_above, self.speed, self.accel)

                # [7] Descer na Célula
                log.info("[7/10] Descendo peça no tabuleiro...")
                self.rtde_c.moveL(p_place, 0.12, self.accel)

                # [8] Soltar peça
                log.info("[8/10] Liberando peça...")
                self._gripper_open()

                # [9] Subir da Célula
                log.info("[9/10] Afastando garra...")
                self.rtde_c.moveL(p_place_above, 0.12, self.accel)

                # [10] Retornar HOME
                log.info("[10/10] Retornando para HOME...")
                self.rtde_c.moveJ(joints_home, 1.0, 1.2)

                log.info("✓ Ciclo concluído com sucesso!")
                return True

            except Exception as e:
                log.error(f"Erro durante execução do movimento RTDE: {e}")
                return False
        else:
            # Simulação de Trajetória
            steps = [
                "[1/10] HOME", "[2/10] Aproximação do Estoque", "[3/10] Descida PICK",
                "[4/10] Fechamento Garra", "[5/10] Subida PICK", "[6/10] Aproximação Célula",
                "[7/10] Descida Célula", "[8/10] Abertura Garra", "[9/10] Subida Célula",
                "[10/10] Retorno HOME"
            ]
            for step in steps:
                log.info(f"[SIMULADO] {step}")
                if "Garra" in step:
                    if "Fechamento" in step:
                        self._gripper_close()
                    else:
                        self._gripper_open()
                else:
                    time.sleep(0.5)
            log.info("✓ [SIMULADO] Ciclo concluído.")
            return True


# ── Teste Rápido por CLI ──────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Módulo de Teste UR3 RTDE")
    parser.add_argument('--cell', type=int, default=-1, help='Célula alvo (0-8) para testar pick-and-place')
    parser.add_argument('--home', action='store_true', help='Envia o robô para a HOME')
    args = parser.parse_args()

    controller = UR3Controller()

    if args.home:
        controller.go_home()
    elif args.cell >= 0:
        controller.place_piece(args.cell)
    else:
        log.info("Informe --home para ir à HOME ou --cell <0-8> para executar um ciclo de teste.")
