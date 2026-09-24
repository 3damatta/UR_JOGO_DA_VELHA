#!/usr/bin/env python3
"""
Atalho para executar o script de calibração em scripts/update_positions.py
"""
import os
import sys
import runpy

script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'update_positions.py')
runpy.run_path(script_path, run_name='__main__')
