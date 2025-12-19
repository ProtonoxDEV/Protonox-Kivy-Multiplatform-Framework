#!/usr/bin/env python3
"""
Protonox ADB Wireless Pairing Tool - WSL2 Compatible
Soporte completo para pairing ADB wireless en WSL2 sobre Windows 11
"""

import subprocess
import re
import json
import time
import random
import os
import sys

def run_command(command):
    """Run shell command and return output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def generate_pairing_code():
    """Generate a 6-digit pairing code"""
    return f"{random.randint(100000, 999999)}"

def get_local_ip():
    """Get local IP address"""
    try:
        # Try different methods to get IP
        code, stdout, stderr = run_command("hostname -I | awk '{print $1}'")
        if code == 0 and stdout.strip():
            return stdout.strip()

        # Fallback to ip route
        code, stdout, stderr = run_command("ip route get 8.8.8.8 | awk '{print $7}' | head -1")
        if code == 0 and stdout.strip():
            return stdout.strip()

    except Exception as e:
        print(f"⚠️  Error obteniendo IP local: {e}")

    return "172.24.175.151"  # Default WSL IP

def check_wsl_environment():
    """Check if running in WSL and provide warnings"""
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                print("🐧 Detectado entorno WSL2")
                print("ℹ️  Nota: WSL2 puede tener limitaciones con mDNS/multicast")
                print("💡 Recomendación: Usa método de código numérico si el QR falla")
                return True
    except:
        pass
    return False

def start_adb_pairing_server(pairing_code, device_name="ProtonoxWSL"):
    """Start ADB pairing server and show connection methods"""
    local_ip = get_local_ip()

    print("🔧 PROTONOX ADB WIRELESS PAIRING")
    print("=" * 50)
    print(f"📍 IP del servidor: {local_ip}")
    print(f"🏷️  Nombre del dispositivo: {device_name}")
    print(f"🔢 Código de pairing: {pairing_code}")
    print()

    # Method 1: QR Code (ADB format)
    print("📱 MÉTODO 1: Código QR (Recomendado)")
    print("-" * 40)

    qr_payload = f"WIFI:T:ADB;S:{device_name};P:{pairing_code};;"
    print(f"📄 Payload del QR: {qr_payload}")
    print()

    # Generate QR using qrencode
    print("Escanea este QR con tu dispositivo Android:")
    print("(Developer Options → Wireless debugging → Pair device with QR code)")
    print()

    try:
        # Use qrencode to generate QR
        cmd = f"qrencode -t UTF8 '{qr_payload}'"
        code, stdout, stderr = run_command(cmd)
        if code == 0:
            print(stdout)
        else:
            print("❌ Error generando QR con qrencode")
            print(f"Comando fallido: {cmd}")
            print(f"Error: {stderr}")
    except Exception as e:
        print(f"❌ Error generando QR: {e}")

    print("-" * 50)

    # Method 2: Numeric Code
    print("🔢 MÉTODO 2: Código Numérico (Alternativo)")
    print("-" * 40)
    print("Si el QR no funciona (común en WSL2), usa este método:")
    print()
    print("En tu dispositivo Android:")
    print("1. Developer Options → Wireless debugging")
    print("2. Toca 'Pair device with pairing code'")
    print("3. El teléfono mostrará una pantalla con IP, puerto y código")
    print("4. Copia estos datos del teléfono")
    print()
    print("📱 Datos que verás en tu teléfono:")
    print("   • IP Address: [número que aparece en el teléfono]")
    print("   • Port: [número que aparece en el teléfono]")
    print("   • Pairing Code: [código que aparece en el teléfono]")
    print()
    print("Una vez que tengas estos datos del teléfono, ejecuta:")
    print("adb pair [IP del teléfono]:[puerto del teléfono] [código del teléfono]")
    print("adb connect [IP del teléfono]:5555")
    print()

    # Method 3: Manual ADB commands
    print("🖥️  MÉTODO 3: Comandos ADB Manuales")
    print("-" * 40)
    print("Si prefieres usar terminal directamente:")
    print(f"adb pair {local_ip}:37329 {pairing_code}")
    print(f"adb connect {local_ip}:5555")
    print()

    print("⏳ Esperando conexiones...")
    print("💡 Mantén esta ventana abierta y sigue las instrucciones en tu celular")
    print()

    # Start ADB pairing server
    try:
        print("🚀 Iniciando servidor de pairing ADB...")
        cmd = f"adb pair {local_ip}:37329"
        print(f"Comando: {cmd} {pairing_code}")
        print("(Ejecuta este comando en otra terminal si es necesario)")
        print()

        # Keep the script running
        input("Presiona Enter para detener el servidor de pairing...")

    except KeyboardInterrupt:
        print("\n👋 Servidor de pairing detenido")
    except Exception as e:
        print(f"❌ Error en servidor de pairing: {e}")

def check_adb_devices():
    """Check connected ADB devices"""
    print("📱 Verificando dispositivos ADB conectados...")
    code, stdout, stderr = run_command("adb devices -l")

    if code == 0:
        lines = stdout.strip().split('\n')[1:]  # Skip header
        devices = []

        for line in lines:
            if line.strip() and not line.startswith('*'):
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]
                    device_info = ' '.join(parts[2:]) if len(parts) > 2 else ""
                    devices.append({
                        'id': device_id,
                        'status': status,
                        'info': device_info
                    })

        if devices:
            print(f"✅ Encontrados {len(devices)} dispositivo(s):")
            for device in devices:
                status_icon = "🟢" if device['status'] == 'device' else "🟡"
                print(f"   {status_icon} {device['id']} - {device['info']}")
        else:
            print("❌ No hay dispositivos conectados")
            print("💡 Conecta tu dispositivo por USB o configura wireless debugging")

        return devices
    else:
        print(f"❌ Error verificando dispositivos: {stderr}")
        return []

def test_adb_connection():
    """Test ADB connection with a simple command"""
    devices = check_adb_devices()
    if not devices:
        return False

    # Test with first device
    device = devices[0]
    print(f"\n🧪 Probando conexión con {device['id']}...")

    code, stdout, stderr = run_command(f"adb -s {device['id']} shell echo 'ADB connection test'")
    if code == 0 and "ADB connection test" in stdout:
        print("✅ Conexión ADB exitosa")
        return True
    else:
        print(f"❌ Error en conexión ADB: {stderr}")
        return False

def main():
    """Main function"""
    print("🔧 Protonox ADB Wireless Pairing Tool")
    print("🐧 Optimizado para WSL2 sobre Windows 11")
    print("=" * 50)

    # Check WSL environment
    is_wsl = check_wsl_environment()

    # Check ADB availability
    code, stdout, stderr = run_command("adb version")
    if code != 0:
        print("❌ ADB no está disponible")
        print("💡 Instala Android SDK Platform Tools:")
        print("   Windows: https://developer.android.com/studio/releases/platform-tools")
        print("   WSL: sudo apt install android-tools-adb")
        return

    print(f"✅ ADB disponible: {stdout.split()[2] if stdout else 'Unknown'}")

    # Check current devices
    initial_devices = check_adb_devices()

    # Generate pairing code
    pairing_code = generate_pairing_code()
    device_name = "ProtonoxWSL"

    print(f"\n🎯 Código de pairing generado: {pairing_code}")
    print(f"🏷️  Nombre del dispositivo: {device_name}")

    # Start pairing server
    try:
        start_adb_pairing_server(pairing_code, device_name)

        # After pairing attempt, check devices again
        print("\n🔍 Verificando si se conectó algún dispositivo...")
        final_devices = check_adb_devices()

        new_devices = len(final_devices) - len(initial_devices)
        if new_devices > 0:
            print(f"✅ ¡Éxito! {new_devices} dispositivo(s) conectado(s)")

            # Test connection
            if test_adb_connection():
                print("\n🎉 ¡Listo para desarrollo!")
                print("📱 Tu dispositivo Android está conectado vía wireless")
                print("🚀 Puedes usar live reload y debugging remoto")
            else:
                print("\n⚠️  Dispositivo conectado pero la conexión no responde")
                print("💡 Verifica que el dispositivo esté desbloqueado y con debugging activado")
        else:
            print("\n❌ No se detectaron nuevos dispositivos")
            print("💡 Verifica:")
            print("   • Que seguiste las instrucciones correctamente")
            print("   • Que tu dispositivo Android está en la misma red WiFi")
            print("   • Que las opciones de desarrollador están activadas")
            if is_wsl:
                print("   • Que WSL2 tiene conectividad de red (prueba método numérico)")

    except KeyboardInterrupt:
        print("\n👋 Proceso cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()