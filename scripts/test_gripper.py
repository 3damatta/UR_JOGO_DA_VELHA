#!/usr/bin/env python3
import time
import sys
import xmlrpc.client

print("=" * 60)
print("  Teste de Conexao e Acionamento da Garra OnRobot RG2 (XML-RPC Direto)")
print("=" * 60)

robot_ip = "192.168.1.100"
port = 41414

print(f"Conectando ao servidor XML-RPC da OnRobot em {robot_ip}:{port}...")

try:
    # Cria o proxy XML-RPC diretamente para o IP do robô
    proxy = xmlrpc.client.ServerProxy(f"http://{robot_ip}:{port}")
    
    # Testa a leitura da largura atual
    print("Tentando ler largura atual da garra...")
    # O método rg_get_width espera o ID da garra (0) como argumento
    largura_atual = proxy.rg_get_width(0)
    print(f"✓ Conectado! Largura atual da garra: {largura_atual} mm")
    
    print("\n1. Testando FECHAMENTO da garra para 38mm (forca 20N)...")
    proxy.rg_grip(0, 38.0, 20.0)
    print("Aguardando 3 segundos...")
    time.sleep(3.0)
    
    print("\n2. Testando ABERTURA da garra para 50mm (forca 20N)...")
    proxy.rg_grip(0, 50.0, 20.0)
    print("Aguardando 3 segundos...")
    time.sleep(3.0)
    
    print("\n✓ Teste concluido com sucesso! A garra respondeu aos comandos via XML-RPC.")

except Exception as e:
    print(f"\n[FALHA] Nao foi possivel comunicar com a garra: {e}")
    print("\nVerifique se:")
    print("  1. O robo UR3 esta ligado e na mesma rede do Raspberry.")
    print("  2. O URCap da OnRobot esta ativo no Teach Pendant.")
    print("  3. A garra esta fisicamente conectada e ligada (LED verde aceso).")
    print(f"  4. O IP do robo e realmente {robot_ip}.")
    sys.exit(1)
