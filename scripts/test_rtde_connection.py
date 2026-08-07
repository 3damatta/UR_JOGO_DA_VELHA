#!/usr/bin/env python3
"""
Script de Teste de Conexão e Validação do UR RTDE
=================================================
Conecta ao robô UR3 (IP 192.168.1.1) e executa um movimento linear extremamente
pequeno e lento no eixo Z (+15mm e depois -15mm) para validar a comunicação RTDE de forma segura.

USO:
    python scripts/test_rtde_connection.py
    python scripts/test_rtde_connection.py --ip <IP_REAL_DO_ROBO>
"""

import sys
import time
import argparse

# ── 1. Verifica Instalação da Biblioteca ──────────────────────────────────────
try:
    import rtde_control
    import rtde_receive
    HAS_RTDE = True
except ImportError:
    HAS_RTDE = False

def main():
    parser = argparse.ArgumentParser(description="Validação de comunicação UR RTDE")
    parser.add_argument('--ip', type=str, default="192.168.1.1", 
                        help="IP do UR3 (default: 192.168.1.1)")
    args = parser.parse_args()

    if not HAS_RTDE:
        print("\n[ERRO] A biblioteca 'ur_rtde' não está instalada neste computador.")
        print("Instale utilizando: pip install ur_rtde")
        print("(Nota: No Windows, pode ser necessário instalar o CMake e Boost first. No Raspberry Pi, rode o setup_raspberry.sh).")
        sys.exit(1)

    ip = args.ip
    print("=" * 60)
    print(f"  Iniciando Teste de Comunicação RTDE com UR3 ({ip})")
    print("=" * 60)

    # ── 2. Conectar ao Robô ───────────────────────────────────────────────────
    try:
        print(f"Conectando ao canal de controle RTDE em {ip}:50002...")
        rtde_c = rtde_control.RTDEControlInterface(ip)
        
        print(f"Conectando ao canal de recepção de dados em {ip}:50004...")
        rtde_r = rtde_receive.RTDEReceiveInterface(ip)
        
        print("✓ Conexão RTDE com o UR3 estabelecida com sucesso!\n")
    except Exception as e:
        print(f"✗ FALHA NA CONEXÃO: {e}")
        print("Verifique se:")
        print("  1. O IP do robô está correto.")
        print("  2. O computador está na mesma subrede do robô.")
        print("  3. O modo 'Remote Control' está ativo no Teach Pendant do UR.")
        sys.exit(1)

    # ── 3. Leitura do Estado Atual ────────────────────────────────────────────
    try:
        actual_q = rtde_r.getActualQ()
        actual_pose = rtde_r.getActualTCPPose()
        
        # Formata os valores de junta para graus para facilitar leitura humana
        q_degrees = [round(x * 57.2958, 2) for x in actual_q]
        pose_rounded = [round(x, 4) for x in actual_pose]
        
        print(f"Posição das Juntas (Graus): {q_degrees}")
        print(f"Pose Atual do TCP [X, Y, Z, Rx, Ry, Rz] (m/rad): {pose_rounded}")
        print("-" * 60)
        
    except Exception as e:
        print(f"✗ Erro ao ler dados do robô: {e}")
        rtde_c.disconnect()
        sys.exit(1)

    # ── 4. Execução de Movimento Relativo Seguro ──────────────────────────────
    print("Aviso: O robô fará um movimento curto de 15mm para CIMA e retornará.")
    print("Mantenha a mão próxima ao botão de Emergência (E-Stop) do Teach Pendant por segurança.")
    confirm = input("Deseja iniciar o movimento de teste? (s/N): ").strip().lower()
    
    if confirm != 's':
        print("Movimento cancelado pelo operador. Fechando conexão.")
        rtde_c.disconnect()
        sys.exit(0)

    try:
        # Define alvos relativos baseados na pose atual do robô
        # actual_pose[2] é a coordenada Z (altura)
        target_pose = list(actual_pose)
        target_pose[2] += 0.015  # sobe exatamente 15 milímetros
        
        # Velocidades extremamente baixas para total controle e segurança
        test_speed = 0.02        # 2 cm/s
        test_accel = 0.05        # 5 cm/s²

        print(f"\n[1/2] Movendo 15mm linearmente para CIMA (Z -> {round(target_pose[2], 4)})...")
        # moveL é uma chamada síncrona/bloqueante por padrão
        rtde_c.moveL(target_pose, test_speed, test_accel)
        print("✓ Movimento de subida concluído.")

        time.sleep(1.0)  # Aguarda 1 segundo parado

        print(f"[2/2] Retornando para a altura inicial (Z -> {round(actual_pose[2], 4)})...")
        rtde_c.moveL(actual_pose, test_speed, test_accel)
        print("✓ Retorno concluído.")

    except Exception as e:
        print(f"✗ Erro durante a movimentação: {e}")
    finally:
        # ── 5. Desconexão Organizada ──────────────────────────────────────────
        print("\nDesconectando interfaces RTDE...")
        rtde_c.disconnect()
        print("✓ Desconectado. Teste finalizado.")

if __name__ == '__main__':
    main()
