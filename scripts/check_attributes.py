#!/usr/bin/env python3
import sys
import inspect

try:
    import onRobot.gripper as gripper
    print("=" * 60)
    print("LISTA DE TODOS OS ATRIBUTOS EM onRobot.gripper:")
    print("=" * 60)
    
    attrs = dir(gripper)
    for attr in attrs:
        if not attr.startswith("__"):
            val = getattr(gripper, attr)
            print(f" - {attr} (Tipo: {type(val)})")
            
            # Se for uma classe ou funcao, tenta ver a assinatura
            if inspect.isclass(val) or inspect.isfunction(val):
                try:
                    sig = inspect.signature(val.__init__ if inspect.isclass(val) else val)
                    print(f"   -> Assinatura: {sig}")
                except Exception:
                    pass
    
    print("=" * 60)
except Exception as e:
    print(f"Erro geral durante a inspecao: {e}")
