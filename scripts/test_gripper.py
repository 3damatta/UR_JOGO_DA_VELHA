#!/usr/bin/env python3
import time
import sys

print("=" * 60)
print("  Teste de Conexao e Acionamento da Garra OnRobot RG2")
print("=" * 60)

try:
    import onRobot.gripper as gripper
except ImportError:
    print("\n[ERRO] A biblioteca 'onRobot' nao esta instalada no Python do Raspberry.")
    print("Por favor, rode o comando abaixo para instalar:")
    print("  pip install onRobot")
    print("Ou instale usando o requirements.txt:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

robot_ip = "192.168.1.100"
print(f"Tentando conectar a garra OnRobot no IP do robo: {robot_ip}...")

try:
    # O segundo parametro (0) e o ID/canal da garra (tool connector)
    g = gripper.RG(robot_ip, 0)
    print("✓ Objeto da garra instanciado com sucesso!")
    
    print("\n1. Testando FECHAMENTO da garra para 38mm (forca 20N)...")
    g.rg_grip(38, 20.0)
    print("Aguardando 3 segundos...")
    time.sleep(3.0)
    
    print("\n2. Testando ABERTURA da garra para 50mm (forca 20N)...")
    g.rg_grip(50, 20.0)
    print("Aguardando 3 segundos...")
    time.sleep(3.0)
    
    print("\n✓ Teste concluido com sucesso! A garra respondeu aos comandos.")

except Exception as e:
    print(f"\n[FALHA] Nao foi possivel comunicar com a garra: {e}")
    print("\nVerifique se:")
    print("  1. O robo UR3 esta ligado e na mesma rede do Raspberry.")
    print("  2. O URCap da OnRobot esta ativo no Teach Pendant.")
    print("  3. A garra esta fisicamente conectada e ligada (LED verde aceso).")
    sys.exit(1)
