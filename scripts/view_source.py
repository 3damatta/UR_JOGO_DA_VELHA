#!/usr/bin/env python3
import inspect
import sys

try:
    import onRobot.gripper as gripper
    print("=" * 60)
    print("Codigo Fonte da classe RG2:")
    print("=" * 60)
    
    source = inspect.getsource(gripper.RG2)
    print(source)
    
    print("=" * 60)
except Exception as e:
    print(f"Erro ao ler codigo fonte: {e}")
