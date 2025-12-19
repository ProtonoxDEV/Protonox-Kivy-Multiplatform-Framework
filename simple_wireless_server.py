#!/usr/bin/env python3
"""
Wireless Live Reload Server with Native Android Pairing.
Starts ADB wireless connection (if available) and WebSocket server for live reload.
"""

import os
import sys
import time
import subprocess
from typing import Optional

# Set headless environment before any kivy imports
os.environ['KIVY_HEADLESS'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_WINDOW'] = 'headless'
os.environ['KIVY_GL_BACKEND'] = 'mock'
os.environ['DISPLAY'] = ''

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_adb() -> Optional[str]:
    """Find ADB binary in system PATH."""
    try:
        result = subprocess.run(['which', 'adb'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_android_devices(adb_path: str) -> list:
    """Get list of connected Android devices."""
    try:
        result = subprocess.run([adb_path, 'devices'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        devices = []
        for line in lines:
            if line.strip() and not line.startswith('*'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    serial, status = parts[0], parts[1]
                    devices.append({'serial': serial, 'status': status})
        return devices
    except subprocess.CalledProcessError:
        return []

def enable_adb_wireless(adb_path: str, device_serial: str, port: int = 5555) -> bool:
    """Enable wireless ADB on Android device."""
    try:
        print(f"🔌 Habilitando ADB wireless en dispositivo {device_serial}...")

        # First enable TCP/IP mode
        subprocess.run([adb_path, '-s', device_serial, 'tcpip', str(port)],
                      capture_output=True, check=True, timeout=10)

        print(f"✅ ADB wireless habilitado en puerto {port}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error habilitando ADB wireless: {e}")
        return False

def connect_adb_wireless(adb_path: str, ip: str, port: int = 5555) -> bool:
    """Connect to Android device via wireless ADB."""
    try:
        print(f"📱 Conectando a dispositivo Android en {ip}:{port}...")

        result = subprocess.run([adb_path, 'connect', f'{ip}:{port}'],
                               capture_output=True, text=True, check=True, timeout=15)

        if 'connected' in result.stdout.lower():
            print("✅ Conexión ADB wireless exitosa!")
            return True
        else:
            print(f"⚠️  Respuesta ADB: {result.stdout.strip()}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error conectando ADB wireless: {e}")
        return False

def get_device_ip(adb_path: str, device_serial: str) -> Optional[str]:
    """Get device IP address."""
    try:
        # Try to get IP from device
        result = subprocess.run([adb_path, '-s', device_serial, 'shell', 'ip', 'route'],
                               capture_output=True, text=True, check=True, timeout=5)

        for line in result.stdout.split('\n'):
            if 'wlan0' in line or 'eth0' in line:
                parts = line.split()
                if len(parts) >= 9:
                    ip = parts[8].split('/')[0]  # Remove subnet mask
                    return ip
        return None
    except subprocess.CalledProcessError:
        return None

def setup_android_pairing() -> bool:
    """Setup native Android pairing via ADB wireless."""
    print("🔧 Intentando pair nativo con Android...")
    print("=" * 50)

    adb_path = find_adb()
    if not adb_path:
        print("⚠️  ADB no encontrado. Saltando pair nativo.")
        print("💡 Para pair nativo: instala Android SDK Platform Tools.")
        return False

    print(f"✅ ADB encontrado: {adb_path}")

    devices = get_android_devices(adb_path)
    if not devices:
        print("⚠️  No se encontraron dispositivos Android conectados por USB.")
        print("💡 Para pair nativo: conecta tu celular por USB y habilita 'Depuración USB'.")
        return False

    print(f"📱 Dispositivos encontrados: {len(devices)}")
    for device in devices:
        print(f"  - {device['serial']} ({device['status']})")

    # Use first device in device mode
    usb_device = next((d for d in devices if d['status'] == 'device'), None)
    if not usb_device:
        print("⚠️  No hay dispositivos en modo 'device'. Verifica la conexión USB.")
        return False

    device_serial = usb_device['serial']
    print(f"🎯 Usando dispositivo: {device_serial}")

    # Get device IP
    device_ip = get_device_ip(adb_path, device_serial)
    if not device_ip:
        print("⚠️  No se pudo obtener la IP del dispositivo.")
        print("💡 Asegúrate de que el dispositivo esté conectado a WiFi.")
        return False

    print(f"🌐 IP del dispositivo: {device_ip}")

    # Enable wireless ADB
    if not enable_adb_wireless(adb_path, device_serial):
        return False

    # Wait a moment for the device to be ready
    print("⏳ Esperando que el dispositivo esté listo...")
    time.sleep(3)

    # Connect wirelessly
    if connect_adb_wireless(adb_path, device_ip):
        print("🎉 ¡Pair nativo con Android completado!")
        return True
    else:
        print("❌ Falló la conexión wireless.")
        return False

def start_websocket_server():
    """Start WebSocket server for live reload."""
    try:
        from kivy.protonox_ext.wireless_debug import start_server, generate_qr

        print("\n🌐 Iniciando servidor WebSocket para live reload...")
        print("=" * 50)

        # Generate QR code for WebSocket connection
        ws_url = f"ws://172.24.175.151:8765"
        print(f"🔗 URL WebSocket: {ws_url}")

        qr = generate_qr(ws_url)
        if qr:
            print("\n📱 Escanea este QR para conectar live reload:")
            print("=" * 50)
            print(qr)
            print("=" * 50)
        else:
            print(f"Conéctate manualmente a: {ws_url}")

        print("\n💡 Instrucciones para live reload:")
        print("1. Si tienes ADB: tu celular ya está conectado wireless")
        print("2. Escanea el QR con una app WebSocket o navegador")
        print("3. Los cambios en el código se reflejarán automáticamente")
        print("4. Para testing: modifica ejemplos/wireless_debug_example.py")
        print("\n🔄 Servidor WebSocket corriendo. Presiona Ctrl+C para detener.")

        # Start the server
        start_server(host="0.0.0.0", port=8765)

    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"❌ Error en servidor WebSocket: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    print("🚀 Protonox Live Reload - Con Pair Nativo Android")
    print("=" * 60)

    # Step 1: Try Android pairing (optional)
    android_paired = setup_android_pairing()

    if android_paired:
        print("\n✅ Android conectado por ADB wireless + WebSocket")
    else:
        print("\nℹ️  Modo WebSocket only (sin ADB)")
        print("💡 Para ADB: conecta dispositivo USB y habilita depuración")

    # Step 2: Start WebSocket server
    start_websocket_server()

if __name__ == "__main__":
    main()