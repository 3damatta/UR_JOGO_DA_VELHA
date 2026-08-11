#!/usr/bin/env python3
import sys

try:
    import onRobot.gripper as gripper
    print("=" * 50)
    print("Atributos disponiveis em onRobot.gripper:")
    print("=" * 50)
    attrs = dir(gripper)
    for attr in attrs:
        if not attr.startswith("__"):
            print(f" - {attr}")
    print("=" * 50)
except ImportError:
    print("A biblioteca 'onRobot' nao esta instalada.")
