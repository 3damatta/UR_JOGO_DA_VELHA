#!/usr/bin/env python3
import sys

try:
    import onRobot.gripper as gripper
    print("=" * 60)
    print("Instanciando RG2 e verificando atributos do objeto:")
    print("=" * 60)
    
    g = gripper.RG2(0)
    print(f"Objeto instanciado: {g}")
    print("\nAtributos/Variaveis internas (g.__dict__):")
    for k, v in g.__dict__.items():
        print(f" - {k}: {v}")
        
    print("\nMetodos/Atributos disponiveis (dir):")
    for attr in dir(g):
        if not attr.startswith("__"):
            print(f" - {attr}")
            
    print("=" * 60)
except Exception as e:
    print(f"Erro ao instanciar ou inspecionar objeto: {e}")
