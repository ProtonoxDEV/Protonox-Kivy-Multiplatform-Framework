#!/usr/bin/env python3
"""
Script para ejecutar todos los tests del framework Protonox Kivy.

Este script configura el entorno apropiado para ejecutar los tests
de manera headless (sin interfaz gráfica) y ejecuta toda la suite de tests.
"""

import os
import sys
import subprocess
import argparse

def setup_kivy_headless():
    """Configurar Kivy para modo headless."""
    os.environ['KIVY_HEADLESS'] = '1'
    os.environ['KIVY_NO_ARGS'] = '1'
    os.environ['KIVY_WINDOW'] = 'headless'
    os.environ['DISPLAY'] = ''  # Deshabilitar display
    
    # Agregar kivy-protonox-version al path
    kivy_protonox_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kivy-protonox-version')
    sys.path.insert(0, kivy_protonox_path)

def run_tests(test_path=None, verbose=True):
    """Ejecutar los tests."""
    # Cambiar al directorio raíz del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Configurar Kivy para headless
    setup_kivy_headless()

    # Agregar el directorio actual al path de Python
    sys.path.insert(0, project_root)

    # Ejecutar los tests de estructura y compatibilidad
    import subprocess

    if test_path:
        # Ejecutar test específico
        if test_path == 'framework':
            test_file = os.path.join(project_root, 'tests', 'test_framework_structure.py')
        elif test_path == 'compatibility':
            test_file = os.path.join(project_root, 'tests', 'test_kivy_compatibility.py')
        else:
            test_file = os.path.join(project_root, 'tests', f'test_{test_path}.py')
        cmd = [sys.executable, test_file]
    else:
        # Ejecutar todos los tests disponibles
        test_files = [
            os.path.join(project_root, 'tests', 'test_framework_structure.py'),
            os.path.join(project_root, 'tests', 'test_kivy_compatibility.py')
        ]
        # Ejecutar tests uno por uno
        for test_file in test_files:
            if os.path.exists(test_file):
                cmd = [sys.executable, test_file]
                print(f"Ejecutando: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=False)
                if result.returncode != 0:
                    return False
        return True

    print(f"Ejecutando: {' '.join(cmd)}")
    print(f"Directorio de trabajo: {os.getcwd()}")
    print("-" * 50)

    # Ejecutar los tests
    result = subprocess.run(cmd, capture_output=False)

    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description='Ejecutar tests del framework Protonox Kivy')
    parser.add_argument('-t', '--test', help='Ruta específica del test a ejecutar')
    parser.add_argument('-q', '--quiet', action='store_true', help='Modo silencioso (menos verbose)')

    args = parser.parse_args()

    print("🚀 Ejecutando tests del Framework Protonox Kivy")
    print("=" * 50)

    success = run_tests(args.test, not args.quiet)

    if success:
        print("\n✅ Todos los tests pasaron exitosamente!")
        return 0
    else:
        print("\n❌ Algunos tests fallaron.")
        return 1

if __name__ == '__main__':
    sys.exit(main())