#!/usr/bin/env python3
"""
Script de Calibração e Atualização de Posições — UR3 Jogo da Velha
===================================================================
Este script permite atualizar as posições do robô UR3 (HOME, PICK e Células 0-8)
inserindo diretamente os ângulos das articulações em GRAUS (°), exatamente como
exibidos na tela 'Posições da Articulação' do Teach Pendant do UR3.

O script converte os valores em graus para radianos (graus * pi / 180) e salva
no formato utilizado pelo sistema em 'ur3/positions_config.json'.

USO INTERATIVO:
    python scripts/update_positions.py

USO VIA LINHA DE COMANDO:
    python scripts/update_positions.py --view
    python scripts/update_positions.py --home --deg -87.14 -88.12 103.93 -105.88 -89.81 -21.33
    python scripts/update_positions.py --pick --deg -87.14 -88.12 103.93 -105.88 -89.81 -21.33
    python scripts/update_positions.py --cell 7 --deg -87.14 -88.12 103.93 -105.88 -89.81 -21.33
"""

import os
import sys
import json
import math
import shutil
import argparse
from datetime import datetime

# Garante suporte a UTF-8 no console Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Descobre a raiz do projeto independente de onde o script é chamado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == 'scripts':
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
else:
    BASE_DIR = SCRIPT_DIR

POSITIONS_FILE = os.path.join(BASE_DIR, 'ur3', 'positions_config.json')

JOINTS_NAMES = ["Base", "Ombro", "Cotovelo", "Pulso 1", "Pulso 2", "Pulso 3"]

CELL_LABELS = {
    "0": "Superior Esquerdo (0)",
    "1": "Superior Centro (1)",
    "2": "Superior Direito (2)",
    "3": "Meio Esquerdo (3)",
    "4": "Meio Centro (4)",
    "5": "Meio Direito (5)",
    "6": "Inferior Esquerdo (6)",
    "7": "Inferior Centro (7)",
    "8": "Inferior Direito (8)"
}


def deg_to_rad(deg_list: list) -> list:
    """Converte uma lista de 6 ângulos em graus para radianos (arredondado a 5 casas)."""
    return [round(float(d) * math.pi / 180.0, 5) for d in deg_list]


def rad_to_deg(rad_list: list) -> list:
    """Converte uma lista de 6 ângulos em radianos para graus (arredondado a 2 casas)."""
    return [round(float(r) * 180.0 / math.pi, 2) for r in rad_list]


def parse_input_degrees(input_str: str) -> list:
    """
    Trata entrada do usuário em graus.
    Suporta vírgula decimal (ex: -87,14) e separadores de espaço/vírgula.
    """
    clean_str = input_str.replace(',', '.').replace(';', ' ')
    parts = [p.strip() for p in clean_str.split() if p.strip()]
    if len(parts) != 6:
        raise ValueError(f"Foram fornecidos {len(parts)} valores, mas são necessários exatamente 6.")
    return [float(p) for p in parts]


def load_positions() -> dict:
    if not os.path.exists(POSITIONS_FILE):
        raise FileNotFoundError(f"Arquivo não encontrado: {POSITIONS_FILE}")
    with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_positions(pos_data: dict, create_backup: bool = True):
    if create_backup and os.path.exists(POSITIONS_FILE):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{POSITIONS_FILE}.bak_{timestamp}"
        shutil.copy2(POSITIONS_FILE, backup_path)
        print(f"➜ Backup criado em: {os.path.basename(backup_path)}")

    with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pos_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Arquivo '{POSITIONS_FILE}' atualizado com sucesso!")


def print_comparison_table(target_name: str, deg_list: list, rad_list: list):
    print("\n" + "=" * 65)
    print(f"  RESUMO DA ATUALIZAÇÃO — {target_name.upper()}")
    print("=" * 65)
    print(f"{'Junta':<12} | {'Graus (Teach Pendant)':<24} | {'Radianos (Salvo)':<18}")
    print("-" * 65)
    for j_name, deg, rad in zip(JOINTS_NAMES, deg_list, rad_list):
        print(f"{j_name:<12} | {deg:>10.2f}°               | {rad:>12.5f} rad")
    print("=" * 65)


def view_all_positions():
    data = load_positions()
    print("\n" + "=" * 70)
    print("        POSIÇÕES ATUAIS CONFIGURADAS NO SISTEMA (UR3)")
    print("=" * 70)

    # Home
    home_rad = data.get('home_pose', {}).get('joint_angles', [])
    if home_rad:
        home_deg = rad_to_deg(home_rad)
        print(f"\n[ HOME POSE ]")
        for name, d, r in zip(JOINTS_NAMES, home_deg, home_rad):
            print(f"  {name:<10}: {d:>7.2f}°  -->  {r:>9.5f} rad")

    # Pick
    pick_rad = data.get('pick', {}).get('joint_angles', [])
    if pick_rad:
        pick_deg = rad_to_deg(pick_rad)
        print(f"\n[ PONTO DE CAPTURA / PICK ]")
        for name, d, r in zip(JOINTS_NAMES, pick_deg, pick_rad):
            print(f"  {name:<10}: {d:>7.2f}°  -->  {r:>9.5f} rad")

    # Tabuleiro
    cells = data.get('board', {}).get('cells', {})
    print(f"\n[ CÉLULAS DO TABULEIRO (0 a 8) ]")
    for cell_id in sorted(cells.keys(), key=lambda x: int(x)):
        cell_info = cells[cell_id]
        c_rad = cell_info.get('joint_angles', [])
        c_deg = rad_to_deg(c_rad)
        label = CELL_LABELS.get(str(cell_id), cell_info.get('label', f'Célula {cell_id}'))
        print(f"\n  ► Célula {cell_id} ({label}):")
        deg_str = ", ".join(f"{d:.2f}°" for d in c_deg)
        rad_str = ", ".join(f"{r:.5f}" for r in c_rad)
        print(f"     Graus   : [{deg_str}]")
        print(f"     Radianos: [{rad_str}]")
    print("\n" + "=" * 70)


def prompt_for_joint_degrees(location_name: str) -> list:
    print(f"\n--- Inserindo valores em GRAUS para: {location_name} ---")
    print("Você pode colar os 6 valores de uma só vez (ex: -87.14 -88.12 103.93 -105.88 -89.81 -21.33)")
    print("ou pressionar ENTER sem digitar nada para inserir junta por junta.\n")
    
    raw = input("Digite ou cole os 6 valores (ou ENTER para modo individual): ").strip()
    if raw:
        try:
            return parse_input_degrees(raw)
        except Exception as e:
            print(f"Erro ao processar entrada: {e}")
            print("Mudando para o modo individual...\n")

    degrees = []
    for joint in JOINTS_NAMES:
        while True:
            val_str = input(f"  • {joint} (°): ").strip().replace(',', '.')
            try:
                val = float(val_str)
                if val < -360 or val > 360:
                    print("  ⚠ Atenção: Valor fora da faixa comum (-360° a 360°). Confirme o valor.")
                degrees.append(val)
                break
            except ValueError:
                print("  ❌ Valor inválido. Digite um número decimal (ex: -87.14).")
    return degrees


def update_target_position(target_type: str, cell_id: str, degrees: list):
    data = load_positions()
    rads = deg_to_rad(degrees)

    if target_type == 'home':
        data['home_pose']['joint_angles'] = rads
        label = "HOME POSE"
    elif target_type == 'pick':
        data['pick']['joint_angles'] = rads
        label = "PONTO DE CAPTURA (PICK)"
    elif target_type == 'cell':
        if cell_id not in data['board']['cells']:
            raise KeyError(f"Célula '{cell_id}' não existe no arquivo de configuração.")
        data['board']['cells'][cell_id]['joint_angles'] = rads
        label = f"Célula {cell_id} ({CELL_LABELS.get(cell_id, '')})"
    else:
        raise ValueError(f"Tipo de alvo inválido: {target_type}")

    print_comparison_table(label, degrees, rads)
    save_positions(data)


def interactive_wizard_all():
    print("\n" + "=" * 65)
    print("  MODO RECALIBRAÇÃO COMPLETA DO ROBÔ (HOME + PICK + 9 CÉLULAS)")
    print("=" * 65)
    print("Você irá passar por cada uma das posições em sequência.")
    print("Tenha o Teach Pendant do robô em mãos na tela 'Posições da Articulação'.\n")

    targets = [
        ('home', None, 'HOME POSE (Posição Inicial)'),
        ('pick', None, 'PONTO DE CAPTURA (Estoque de Peças)'),
    ]
    for c in range(9):
        str_c = str(c)
        targets.append(('cell', str_c, f'Célula {str_c} - {CELL_LABELS[str_c]}'))

    data = load_positions()
    for target_type, cell_id, title in targets:
        print("\n" + "-" * 65)
        print(f" 📍 PRÓXIMA POSIÇÃO: {title}")
        print("-" * 65)
        confirm = input(f"Deseja atualizar '{title}'? (s/n/sair) [s]: ").strip().lower()
        if confirm == 'sair':
            print("Operação cancelada.")
            break
        if confirm in ['', 's', 'sim', 'y', 'yes']:
            degs = prompt_for_joint_degrees(title)
            rads = deg_to_rad(degs)
            if target_type == 'home':
                data['home_pose']['joint_angles'] = rads
            elif target_type == 'pick':
                data['pick']['joint_angles'] = rads
            elif target_type == 'cell':
                data['board']['cells'][cell_id]['joint_angles'] = rads
            print_comparison_table(title, degs, rads)

    save_confirm = input("\nDeseja salvar TODAS as alterações no arquivo de configuração? (s/n) [s]: ").strip().lower()
    if save_confirm in ['', 's', 'sim', 'y', 'yes']:
        save_positions(data)
    else:
        print("Alterações NÃO foram salvas.")


def interactive_menu():
    while True:
        print("\n" + "=" * 65)
        print("    UR3 TIC-TAC-TOE — CONFIGURADOR DE POSIÇÕES DAS ARTICULAÇÕES")
        print("=" * 65)
        print(" [H] Atualizar Posição HOME (Inicial)")
        print(" [P] Atualizar Ponto de CAPTURA (Pick/Estoque)")
        print(" [0..8] Atualizar uma Célula Específica do Tabuleiro (ex: 7 para Cel 7)")
        print(" [A] Recalibrar TODAS as posições em sequência (Wizard Completo)")
        print(" [V] Visualizar todas as posições atuais (Graus e Radianos)")
        print(" [S] Sair")
        print("=" * 65)

        choice = input("Escolha uma opção: ").strip().upper()

        if choice == 'S':
            print("Saindo do configurador.")
            break
        elif choice == 'V':
            view_all_positions()
        elif choice == 'H':
            degs = prompt_for_joint_degrees("HOME POSE")
            update_target_position('home', None, degs)
        elif choice == 'P':
            degs = prompt_for_joint_degrees("PONTO DE CAPTURA (PICK)")
            update_target_position('pick', None, degs)
        elif choice in [str(i) for i in range(9)]:
            title = f"Célula {choice} ({CELL_LABELS[choice]})"
            degs = prompt_for_joint_degrees(title)
            update_target_position('cell', choice, degs)
        elif choice == 'A':
            interactive_wizard_all()
        else:
            print("❌ Opção inválida! Tente novamente.")


def main():
    parser = argparse.ArgumentParser(description="Configurador de Posições em Graus para o UR3")
    parser.add_argument('--view', action='store_true', help='Visualiza as posições salvas atuais em graus e radianos')
    parser.add_argument('--home', action='store_true', help='Atualiza a posição HOME')
    parser.add_argument('--pick', action='store_true', help='Atualiza o ponto de CAPTURA')
    parser.add_argument('--cell', type=int, choices=range(9), help='Índice da célula do tabuleiro (0 a 8)')
    parser.add_argument('--deg', nargs=6, type=float, help='Lista com os 6 ângulos em graus: Base Ombro Cotovelo Pulso1 Pulso2 Pulso3')

    args = parser.parse_args()

    if args.view:
        view_all_positions()
        return

    if args.deg:
        if args.home:
            update_target_position('home', None, args.deg)
        elif args.pick:
            update_target_position('pick', None, args.deg)
        elif args.cell is not None:
            update_target_position('cell', str(args.cell), args.deg)
        else:
            print("❌ Especifique a posição a ser atualizada: --home, --pick ou --cell <0-8>")
        return

    # Se nenhum argumento CLI de execução rápida foi passado, roda no modo interativo
    interactive_menu()


if __name__ == '__main__':
    main()
