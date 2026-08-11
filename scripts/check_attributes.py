#!/usr/bin/env python3
import sys
import inspect

try:
    import onRobot.gripper as gripper
    print("=" * 60)
    print("Inspecionando 'rg2' em onRobot.gripper:")
    print("=" * 60)
    
    if hasattr(gripper, 'rg2'):
        rg2_obj = gripper.rg2
        print(f"Tipo: {type(rg2_obj)}")
        
        # Tenta pegar a assinatura do construtor __init__
        try:
            sig = inspect.signature(rg2_obj.__init__)
            print(f"Assinatura do construtor: {sig}")
        except Exception as e:
            print(f"Nao foi possivel obter a assinatura do construtor: {e}")
            
        # Tenta ver os nomes das variaveis locais do __init__ caso inspect.signature falhe
        try:
            print(f"Argumentos (__init__): {rg2_obj.__init__.__code__.co_varnames}")
        except Exception as e:
            pass
            
        # Docstring
        print(f"Docstring:\n{rg2_obj.__doc__}")
        
    else:
        print("Atributo 'rg2' nao encontrado em onRobot.gripper!")
        
    print("=" * 60)
except Exception as e:
    print(f"Erro geral durante a inspecao: {e}")
