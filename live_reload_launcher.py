#!/usr/bin/env python3
"""
Launcher para el sistema de Live Reload de Protonox.
Permite ejecutar el servidor, cliente de prueba o app demo.
"""

import argparse
import subprocess
import sys
import os

def run_server():
    """Run the live reload server"""
    print("🚀 Iniciando servidor de live reload...")
    cmd = [sys.executable, "live_reload_server.py"]
    subprocess.run(cmd)

def run_client():
    """Run the test client"""
    print("🧪 Iniciando cliente de prueba...")
    cmd = [sys.executable, "test_client.py"]
    subprocess.run(cmd)

def run_demo_app():
    """Run the demo app"""
    print("📱 Iniciando app de demostración...")
    cmd = [sys.executable, "live_reload_demo.py"]
    subprocess.run(cmd)

def run_demo_headless():
    """Run the demo app in headless mode"""
    print("🖥️  Iniciando app de demostración en modo headless...")
    cmd = [sys.executable, "live_reload_demo.py", "--headless"]
    subprocess.run(cmd)

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n🔄 PROTONOX LIVE RELOAD SYSTEM")
        print("=" * 40)
        print("1. 🚀 Iniciar Servidor")
        print("2. 🧪 Ejecutar Cliente de Prueba")
        print("3. 📱 Ejecutar App Demo (GUI)")
        print("4. 🖥️  Ejecutar App Demo (Headless)")
        print("5. 📋 Ver Estado del Sistema")
        print("6. ❌ Salir")
        print()

        try:
            choice = input("Selecciona una opción (1-6): ").strip()

            if choice == '1':
                run_server()
            elif choice == '2':
                run_client()
            elif choice == '3':
                run_demo_app()
            elif choice == '4':
                run_demo_headless()
            elif choice == '5':
                show_system_status()
            elif choice == '6':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Intenta de nuevo.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def show_system_status():
    """Show system status"""
    print("\n📊 ESTADO DEL SISTEMA")
    print("=" * 30)

    # Check if server is running
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8765))
        sock.close()
        if result == 0:
            print("✅ Servidor: Ejecutándose en puerto 8765")
        else:
            print("❌ Servidor: No detectado")
    except:
        print("❌ Servidor: Error al verificar")

    # Check dependencies
    try:
        import websockets
        import qrcode
        import zeroconf
        print("✅ Dependencias: Todas instaladas")
    except ImportError as e:
        print(f"❌ Dependencias: Faltan - {e}")

    # Check ADB
    try:
        result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ ADB: Disponible")
        else:
            print("❌ ADB: No disponible")
    except:
        print("❌ ADB: No encontrado")

    # Show IP
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print(f"📱 IP Local: {ip}")
    except:
        print("📱 IP Local: No disponible")

    print()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Protonox Live Reload System')
    parser.add_argument('command', nargs='?', choices=['server', 'client', 'demo', 'headless', 'status'],
                       help='Comando a ejecutar')
    parser.add_argument('--menu', action='store_true', help='Mostrar menú interactivo')

    args = parser.parse_args()

    if args.menu or not args.command:
        show_menu()
    elif args.command == 'server':
        run_server()
    elif args.command == 'client':
        run_client()
    elif args.command == 'demo':
        run_demo_app()
    elif args.command == 'headless':
        run_demo_headless()
    elif args.command == 'status':
        show_system_status()

if __name__ == "__main__":
    main()