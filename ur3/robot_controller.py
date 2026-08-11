"""
Controlador do UR3 — Jogo da Velha
====================================
Sequência de movimento por jogada:

  1. movej → HOME
  2. movel → posição de pick (fixa, sempre a mesma)
  3. fechar garra OnRobot (pegar peça)
  4. movel → 50 mm ACIMA da célula alvo  (Z_place + 0.050)
  5. movel → célula alvo                  (Z_place) — movimento linear no eixo Z
  6. abrir garra (soltar peça)
  7. movel → 50 mm ACIMA da célula alvo  (Z_place + 0.050) — sobe linear no eixo Z
  8. movej → HOME

Comunicação via TCP socket na porta 30002 (Primary Interface) do UR3.

USO direto (teste):
    python ur3/robot_controller.py --cell 4
    python ur3/robot_controller.py --cell 4 --dry-run   # só imprime o script
    python ur3/robot_controller.py                       # apenas vai à home
"""

import socket
import json
import time
import logging
import yaml
import os
import argparse

import xmlrpc.client

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [UR3] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, 'config', 'settings.yaml'), encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

ROBOT_CFG   = cfg['robot']
GRIPPER_CFG = cfg['gripper']

# Offset de abordagem: 100 mm acima da posição de pouso
APPROACH_OFFSET_M = 0.100


class UR3Controller:
    """
    Gera e envia URScript para o UR3 via TCP socket.
    Suporte a garra OnRobot RG2/RG6 via XML-RPC.
    """

    def __init__(self):
        self.ip    = ROBOT_CFG['ip']
        self.port  = ROBOT_CFG['port']
        self.speed = ROBOT_CFG['speed']
        self.accel = ROBOT_CFG['acceleration']
        self.blend = ROBOT_CFG['blend_radius']

        # Carrega posições do JSON
        pos_file = os.path.join(BASE_DIR, 'ur3', 'positions_config.json')
        with open(pos_file) as f:
            self.pos = json.load(f)

        log.info(f"UR3 Controller pronto → {self.ip}:{self.port}")

        # Inicializa a garra OnRobot via XML-RPC
        self.rg_gripper = None
        log.info(f"Conectando a garra OnRobot em http://{self.ip}:41414...")
        try:
            self.rg_gripper = xmlrpc.client.ServerProxy(f"http://{self.ip}:41414")
            # Configura um timeout curto para evitar travar se o robô estiver offline
            import socket
            socket.setdefaulttimeout(3.0)
            # Testa leitura da largura
            self.rg_gripper.rg_get_width(0)
            log.info("✓ Garra OnRobot conectada com sucesso via XML-RPC!")
        except Exception as e:
            log.warning(f"Nao foi possivel conectar a garra fisica em http://{self.ip}:41414 ({e})")
            log.warning("O robo rodara com garra em modo de simulacao.")
            self.rg_gripper = None


    # ── Helpers de URScript ───────────────────────────────────────────────────
    def _pose(self, x: float, y: float, z: float, orient: list) -> str:
        """Formata uma pose como string URScript p[x,y,z,rx,ry,rz]."""
        rx, ry, rz = orient
        return f"p[{x:.4f},{y:.4f},{z:.4f},{rx:.4f},{ry:.4f},{rz:.4f}]"

    def _movel(self, pose_str: str, speed=None, accel=None, blend=0.0) -> str:
        """Gera instrução movel() — movimento linear no espaço cartesiano."""
        v = speed if speed is not None else self.speed
        a = accel if accel is not None else self.accel
        return f"  movel({pose_str}, a={a}, v={v}, r={blend})\n"

    def _movej(self, joints: list, speed=None, accel=None) -> str:
        """Gera instrução movej() — movimento em espaço de junta (para home)."""
        v = speed if speed is not None else 1.0
        a = accel if accel is not None else 1.2
        jstr = ", ".join(f"{j:.4f}" for j in joints)
        return f"  movej([{jstr}], a={a}, v={v})\n"

    def _gripper_close(self):
        """Fecha a garra na largura da peca usando XML-RPC."""
        width = GRIPPER_CFG['close_width']
        force = GRIPPER_CFG['force']
        wait = GRIPPER_CFG['wait_time']
        
        log.info(f"Garra: Fechando para {width}mm com {force}N...")
        if self.rg_gripper:
            try:
                # O metodo rg_grip no servidor XML-RPC espera (rg_id, target_width, target_force)
                self.rg_gripper.rg_grip(0, float(width), float(force))
            except Exception as e:
                log.error(f"Erro ao acionar fechar garra via XML-RPC: {e}")
                raise e
            time.sleep(wait)
        else:
            time.sleep(wait)
            log.info("Garra: [SIMULADO] Garra fechada.")

    def _gripper_open(self):
        """Abre a garra usando XML-RPC."""
        width = GRIPPER_CFG['open_width']
        force = GRIPPER_CFG['force']
        wait = GRIPPER_CFG['wait_time']
        
        log.info(f"Garra: Abrindo para {width}mm...")
        if self.rg_gripper:
            try:
                # O metodo rg_grip no servidor XML-RPC espera (rg_id, target_width, target_force)
                self.rg_gripper.rg_grip(0, float(width), float(force))
            except Exception as e:
                log.error(f"Erro ao acionar abrir garra via XML-RPC: {e}")
                raise e
            time.sleep(wait)
        else:
            time.sleep(wait)
            log.info("Garra: [SIMULADO] Garra aberta.")

    # ── Geração do URScript Principal ─────────────────────────────────────────
    def build_pick_movement(self) -> str:
        """
        [Movimento Fase 1]
        HOME -> 100mm acima do pick -> desce ate o pick
        """
        home = self.pos['home_pose']['joint_angles']
        pick = self.pos['pick']['joint_angles']
        
        home_str = ", ".join(f"{j:.5f}" for j in home)
        pick_str = ", ".join(f"{j:.5f}" for j in pick)
        
        lines = [
            "def pick_movement():\n",
            f"  home_joints = [{home_str}]\n",
            f"  pick_joints = [{pick_str}]\n",
            "  pick_pose = get_forward_kin(pick_joints)\n",
            f"  pick_above = p[pick_pose[0], pick_pose[1], pick_pose[2] + {APPROACH_OFFSET_M:.3f}, pick_pose[3], pick_pose[4], pick_pose[5]]\n",
            "  movej(home_joints, a=1.2, v=1.0)\n",
            f"  movel(pick_above, a=0.5, v=0.3, r={self.blend})\n",
            "  movel(pick_pose, a=0.5, v=0.3)\n",
            "end\n",
            "pick_movement()\n"
        ]
        return "".join(lines)

    def build_place_movement(self, cell: int) -> str:
        """
        [Movimento Fase 2]
        Sobe do pick -> vai acima da celula -> desce na celula
        """
        pick = self.pos['pick']['joint_angles']
        cell_joints = self.pos['board']['cells'][str(cell)]['joint_angles']
        
        pick_str = ", ".join(f"{j:.5f}" for j in pick)
        cell_str = ", ".join(f"{j:.5f}" for j in cell_joints)
        
        lines = [
            "def place_movement():\n",
            f"  pick_joints = [{pick_str}]\n",
            f"  cell_joints = [{cell_str}]\n",
            "  pick_pose = get_forward_kin(pick_joints)\n",
            "  cell_pose = get_forward_kin(cell_joints)\n",
            f"  pick_above = p[pick_pose[0], pick_pose[1], pick_pose[2] + {APPROACH_OFFSET_M:.3f}, pick_pose[3], pick_pose[4], pick_pose[5]]\n",
            f"  cell_above = p[cell_pose[0], cell_pose[1], cell_pose[2] + {APPROACH_OFFSET_M:.3f}, cell_pose[3], cell_pose[4], cell_pose[5]]\n",
            "  movel(pick_above, a=0.5, v=0.3)\n",
            f"  movel(cell_above, a=0.5, v=0.3, r={self.blend})\n",
            "  movel(cell_pose, a=0.5, v=0.3)\n",
            "end\n",
            "place_movement()\n"
        ]
        return "".join(lines)

    def build_after_place_movement(self, cell: int) -> str:
        """
        [Movimento Fase 3]
        Sobe da celula -> HOME
        """
        home = self.pos['home_pose']['joint_angles']
        cell_joints = self.pos['board']['cells'][str(cell)]['joint_angles']
        
        home_str = ", ".join(f"{j:.5f}" for j in home)
        cell_str = ", ".join(f"{j:.5f}" for j in cell_joints)
        
        lines = [
            "def after_place():\n",
            f"  home_joints = [{home_str}]\n",
            f"  cell_joints = [{cell_str}]\n",
            "  cell_pose = get_forward_kin(cell_joints)\n",
            f"  cell_above = p[cell_pose[0], cell_pose[1], cell_pose[2] + {APPROACH_OFFSET_M:.3f}, cell_pose[3], cell_pose[4], cell_pose[5]]\n",
            "  movel(cell_above, a=0.5, v=0.3)\n",
            "  movej(home_joints, a=1.2, v=1.0)\n",
            "end\n",
            "after_place()\n"
        ]
        return "".join(lines)

    def build_place_script(self, cell: int) -> str:
        """Gera o URScript concatenado apenas para visualizacao e testes em dry-run."""
        return (
            "# === FASE 1: MOVER ATE O PICK ===\n" + self.build_pick_movement() + "\n" +
            "# === FASE 2: MOVER ATE A CELULA ===\n" + self.build_place_movement(cell) + "\n" +
            "# === FASE 3: RETORNAR HOME ===\n" + self.build_after_place_movement(cell)
        )

    # ── Comunicação TCP ───────────────────────────────────────────────────────
    def send_script(self, script: str, timeout: float = 60.0) -> bool:
        """
        Envia URScript ao UR3 via TCP socket na porta 30002.
        Retorna True se enviado com sucesso.
        """
        log.info(f"Conectando ao UR3 em {self.ip}:{self.port}...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((self.ip, self.port))
                log.info("✓ Conectado ao UR3")

                payload = (script + "\n").encode('utf-8')
                s.sendall(payload)
                log.info(f"✓ Script enviado ({len(payload)} bytes)")

                # Aguarda execução lendo respostas do robô
                s.settimeout(timeout)
                start = time.time()
                while time.time() - start < timeout:
                    try:
                        data = s.recv(1024)
                        if not data:
                            break
                        log.debug(f"UR3: {data.decode(errors='ignore').strip()}")
                    except socket.timeout:
                        break

            return True

        except ConnectionRefusedError:
            log.error(
                f"Conexão recusada — verifique o IP {self.ip} "
                f"e se o UR3 está em modo Remoto"
            )
            return False
        except socket.timeout:
            log.error("Timeout ao conectar ao UR3")
            return False
        except Exception as e:
            log.error(f"Erro de comunicação com UR3: {e}")
            return False

    # ── Interface Pública ─────────────────────────────────────────────────────
    def place_piece(self, cell: int) -> bool:
        """
        Executa a sequencia completa de pick & place na celula informada em 3 fases:
        Fase 1: Mover para o pick.
        Fase 2: Fechar garra (Python) e mover para a celula.
        Fase 3: Abrir garra (Python) e retornar para a HOME.
        """
        if cell < 0 or cell > 8:
            log.error(f"Celula invalida: {cell} (deve ser 0–8)")
            return False

        if not self.rg_gripper:
            log.error("[ERRO CRITICO] A garra fisica nao esta conectada via XML-RPC em http://%s:41414!" % self.ip)
            log.error("Por favor, certifique-se de que o teste de garra (python scripts/test_gripper.py) funciona.")
            return False

        label = self.pos['board']['cells'][str(cell)]['label']
        log.info(f"► Robo jogando na celula {cell} ({label})")

        # ── [FASE 1] Mover ate o Pick
        log.info("[FASE 1/3] Movendo para a posicao de captura (PICK)...")
        script_pick = self.build_pick_movement()
        if not self.send_script(script_pick, timeout=30.0):
            log.error("Falha na Fase 1 (Movimento ate o Pick)")
            return False

        # ── [FASE 2] Fechar Garra e Mover ate a Celula
        try:
            self._gripper_close()
        except Exception as e:
            log.error(f"Abortando movimento devido a falha na garra: {e}")
            return False
        
        log.info(f"[FASE 2/3] Elevando e movendo ate a celula {cell} ({label})...")
        script_place = self.build_place_movement(cell)
        if not self.send_script(script_place, timeout=30.0):
            log.error("Falha na Fase 2 (Movimento ate a Celula)")
            return False
            
        # ── [FASE 3] Abrir Garra e Retornar para HOME
        try:
            self._gripper_open()
        except Exception as e:
            log.error(f"Falha ao abrir garra (peca ja posicionada): {e}")
        
        log.info("[FASE 3/3] Afastando e retornando para HOME...")
        script_after = self.build_after_place_movement(cell)
        if not self.send_script(script_after, timeout=30.0):
            log.error("Falha na Fase 3 (Retorno para HOME)")
            return False

        log.info(f"✓ Peca posicionada na celula {cell} com sucesso!")
        return True

    def go_home(self) -> bool:
        """Envia o robô diretamente à pose home."""
        joints = self.pos['home_pose']['joint_angles']
        script = (
            "def go_home():\n"
            f"  movej([{', '.join(f'{j:.5f}' for j in joints)}], a=1.2, v=1.0)\n"
            "end\n"
            "go_home()\n"
        )
        log.info("► Enviando robô à pose home")
        return self.send_script(script, timeout=15.0)


# ── CLI de Teste ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Teste do controlador UR3 — Jogo da Velha",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--cell', type=int, default=-1,
        help='Célula alvo (0-8). Omitir = apenas vai à home'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Gera e imprime o URScript sem enviar ao robô'
    )
    args = parser.parse_args()

    controller = UR3Controller()

    if args.cell >= 0:
        script = controller.build_place_script(args.cell)
        if args.dry_run:
            print("=" * 50)
            print(f"  URScript — Célula {args.cell} (DRY RUN)")
            print("=" * 50)
            print(script)
        else:
            controller.place_piece(args.cell)
    else:
        if args.dry_run:
            print("--dry-run requer --cell <0-8>")
        else:
            controller.go_home()
