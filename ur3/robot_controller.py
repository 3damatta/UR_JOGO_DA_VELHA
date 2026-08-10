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

# Offset de abordagem: 50 mm acima da posição de pouso
APPROACH_OFFSET_M = 0.050


class UR3Controller:
    """
    Gera e envia URScript para o UR3 via TCP socket.
    Suporte a garra OnRobot RG2/RG6 via URCap (rg_grip).
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

    def _gripper_close(self) -> str:
        """Fecha a garra OnRobot (agarra a peca)."""
        force = GRIPPER_CFG['force']
        width = GRIPPER_CFG['close_width']
        wait  = GRIPPER_CFG['wait_time']
        return (
            f"  rg_grip({width}, {force}, 0)\n"
            f"  sleep({wait})\n"
        )

    def _gripper_open(self) -> str:
        """Abre a garra OnRobot (solta a peca)."""
        force = GRIPPER_CFG['force']
        width = GRIPPER_CFG['open_width']
        wait  = GRIPPER_CFG['wait_time']
        return (
            f"  rg_grip({width}, {force}, 0)\n"
            f"  sleep({wait})\n"
        )

    # ── Geração do URScript Principal ─────────────────────────────────────────
    def build_place_script(self, cell: int) -> str:
        """
        Gera o URScript completo com sequência anti-colisão:

          [1]  HOME
          [2]  50mm ACIMA do pick       (Z_pick + 0.050)
          [3]  Desce 50mm → pick        (linear Z)
          [4]  Fecha garra              (pega a peça)
          [5]  Sobe 50mm → above pick   (linear Z)
          [6]  50mm ACIMA da célula     (Z_place + 0.050)
          [7]  Desce 50mm → célula      (linear Z)
          [8]  Abre garra               (solta a peça)
          [9]  Sobe 50mm               (linear Z)
          [10] HOME
        """
        pick   = self.pos['pick']
        board  = self.pos['board']
        home   = self.pos['home_pose']
        orient = board['orientation']

        # -- Coordenadas do pick
        px = pick['x']
        py = pick['y']
        pz = pick['z']
        pz_above = pz + APPROACH_OFFSET_M        # 50 mm acima do pick
        pick_orient = [pick['rx'], pick['ry'], pick['rz']]

        pick_above_pose = self._pose(px, py, pz_above, pick_orient)  # acima
        pick_pose       = self._pose(px, py, pz,       pick_orient)  # exato

        # -- Coordenadas da celula destino
        cell_data = board['cells'][str(cell)]
        cx = cell_data['x']
        cy = cell_data['y']
        cz_place   = board['z_place']
        cz_above   = cz_place + APPROACH_OFFSET_M   # 50 mm acima da celula

        cell_above_pose = self._pose(cx, cy, cz_above,  orient)  # acima
        cell_place_pose = self._pose(cx, cy, cz_place,  orient)  # exato

        lines = [f"def place_piece_cell_{cell}():\n"]

        # [1] HOME
        lines.append("  # [1] HOME\n")
        lines.append(self._movej(home['joint_angles']))

        # [2] Ir para 50mm ACIMA do pick
        lines.append("\n  # [2] Ir para 50mm acima do pick\n")
        lines.append(self._movel(pick_above_pose, blend=self.blend))

        # [3] Descer 50mm linearmente ate o pick
        lines.append("\n  # [3] Descer 50mm linear Z -> posicao de pick\n")
        lines.append(self._movel(pick_pose))

        # [4] Fechar garra
        lines.append("\n  # [4] Fechar garra - pegar peca\n")
        lines.append(self._gripper_close())

        # [5] Subir 50mm linearmente (saida do pick)
        lines.append("\n  # [5] Subir 50mm linear Z - sair do pick\n")
        lines.append(self._movel(pick_above_pose))

        # [6] Ir para 50mm ACIMA da celula destino
        lines.append(f"\n  # [6] Ir para 50mm acima da celula {cell}\n")
        lines.append(self._movel(cell_above_pose, blend=self.blend))

        # [7] Descer 50mm linearmente ate a posicao de pouso
        lines.append(f"\n  # [7] Descer 50mm linear Z -> celula {cell}\n")
        lines.append(self._movel(cell_place_pose))

        # [8] Abrir garra
        lines.append("\n  # [8] Abrir garra - soltar peca\n")
        lines.append(self._gripper_open())

        # [9] Subir 50mm linearmente (saida da celula)
        lines.append("\n  # [9] Subir 50mm linear Z - sair da celula\n")
        lines.append(self._movel(cell_above_pose))

        # [10] HOME
        lines.append("\n  # [10] HOME\n")
        lines.append(self._movej(home['joint_angles']))

        lines.append("end\n")
        lines.append(f"place_piece_cell_{cell}()\n")

        return "".join(lines)

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
                        if data:
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
        Executa a sequência completa de pick & place na célula informada.
        Retorna True se o script foi enviado com sucesso.
        """
        if cell < 0 or cell > 8:
            log.error(f"Célula inválida: {cell} (deve ser 0–8)")
            return False

        label = self.pos['board']['cells'][str(cell)]['label']
        log.info(f"► Robô jogando na célula {cell} ({label})")

        script = self.build_place_script(cell)
        log.debug(f"URScript:\n{script}")

        success = self.send_script(script)
        if success:
            log.info(f"✓ Peça posicionada na célula {cell}")
        return success

    def go_home(self) -> bool:
        """Envia o robô diretamente à pose home."""
        joints = self.pos['home_pose']['joint_angles']
        script = (
            "def go_home():\n"
            f"  movej([{', '.join(f'{j:.4f}' for j in joints)}], a=1.2, v=1.0)\n"
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
