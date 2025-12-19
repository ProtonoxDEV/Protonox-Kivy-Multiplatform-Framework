#!/usr/bin/env python3
"""
ADB Wireless Device Discovery and Pairing Tool
Detects Android devices on WiFi network and enables wireless debugging.
"""

import subprocess
import re
import json
import qrcode
import sys
import time
import os

def run_adb_command(command):
    """Run ADB command and return output"""
    try:
        result = subprocess.run(['adb'] + command.split(),
                              capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def check_adb_mdns():
    """Check if ADB mDNS discovery is available"""
    code, stdout, stderr = run_adb_command("mdns check")
    if code == 0 and "mDNS discovery enabled" in stdout:
        return True
    return False

def discover_devices():
    """Discover Android devices on the network using mDNS"""
    print("🔍 Buscando dispositivos Android en la red WiFi...")

    # First check if mDNS is available
    if not check_adb_mdns():
        print("⚠️  mDNS no está disponible. Asegúrate de que ADB esté actualizado.")
        print("💡 Alternativa: Conecta tu dispositivo por USB primero y habilita wireless manualmente.")
        return []

    # Discover devices
    code, stdout, stderr = run_adb_command("mdns services")
    if code != 0:
        print(f"❌ Error al buscar servicios: {stderr}")
        return []

    devices = []
    lines = stdout.strip().split('\n')

    for line in lines:
        if line.strip():
            # Parse mDNS service line
            match = re.search(r'(\w+)\s+(.+)', line)
            if match:
                service_name = match.group(1)
                service_info = match.group(2)
                devices.append({
                    'name': service_name,
                    'info': service_info,
                    'type': 'mdns'
                })

    return devices

def get_connected_devices():
    """Get currently connected ADB devices"""
    code, stdout, stderr = run_adb_command("devices -l")
    if code != 0:
        return []

    devices = []
    lines = stdout.strip().split('\n')[1:]  # Skip header

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
                    'info': device_info,
                    'type': 'connected'
                })

    return devices

def generate_qr_code(data):
    """Generate QR code as ASCII art"""
    try:
        qr = qrcode.QRCode(version=1, box_size=1, border=1)
        qr.add_data(data)
        qr.make(fit=True)

        # Create ASCII art
        matrix = qr.get_matrix()
        qr_art = []
        for row in matrix:
            line = ""
            for cell in row:
                line += "██" if cell else "  "
            qr_art.append(line)

        return "\n".join(qr_art)
    except Exception as e:
        print(f"❌ Error generando QR: {e}")
        return None

def connect_device(ip_port):
    """Connect to Android device wirelessly"""
    print(f"🔗 Conectando a {ip_port}...")
    code, stdout, stderr = run_adb_command(f"connect {ip_port}")

    print(f"📄 Salida ADB: {stdout.strip()}")
    if stderr.strip():
        print(f"⚠️  Error ADB: {stderr.strip()}")

    if code == 0 and ("connected" in stdout.lower() or "already connected" in stdout.lower()):
        print(f"✅ Conectado exitosamente a {ip_port}")
        return True
    else:
        print(f"❌ Error al conectar a {ip_port}")
        print("💡 Posibles causas:")
        print("   - El dispositivo no tiene wireless debugging habilitado")
        print("   - Puerto incorrecto (prueba 5555)")
        print("   - Firewall bloqueando la conexión")
        print("   - Dispositivo en red diferente")
        return False

def enable_wireless_on_device(device_id):
    """Enable wireless debugging on a USB-connected device"""
    print(f"📱 Habilitando wireless debugging en {device_id}...")

    # Set device to listen on port 5555
    code, stdout, stderr = run_adb_command(f"-s {device_id} tcpip 5555")
    if code != 0:
        print(f"❌ Error configurando TCPIP: {stderr}")
        return False

    print("✅ Dispositivo configurado para wireless debugging")
    print("🔌 Ahora puedes desconectar el cable USB")
    print("📱 El dispositivo debería aparecer en la lista de red")

    return True

def get_device_ip(device_id):
    """Get IP address of connected device"""
    # Try to get IP from device
    code, stdout, stderr = run_adb_command(f"-s {device_id} shell ip route")
    if code == 0:
        # Parse IP from route output
        match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', stdout)
        if match:
            return match.group(1)

    return None

def main():
    """Main function"""
    print("🔧 Protonox ADB Wireless Pairing Tool")
    print("=" * 45)

    # Check connected devices first
    connected = get_connected_devices()
    if connected:
        print(f"\n📱 Dispositivos conectados ({len(connected)}):")
        for i, device in enumerate(connected, 1):
            status_icon = "🟢" if device['status'] == 'device' else "🟡"
            print(f"  {i}. {status_icon} {device['id']} - {device['info']}")

        # Ask if user wants to enable wireless on a connected device
        try:
            choice = input("\n¿Quieres habilitar wireless debugging en un dispositivo conectado? (número o 'n'): ")
            if choice.isdigit() and 1 <= int(choice) <= len(connected):
                device = connected[int(choice) - 1]
                if enable_wireless_on_device(device['id']):
                    print("\n🔍 Buscando el dispositivo en la red...")
                    time.sleep(3)  # Wait for device to appear on network

                    # Try to get device IP and suggest connection
                    device_ip = get_device_ip(device['id'])
                    if device_ip:
                        suggested_target = f"{device_ip}:5555"
                        print(f"💡 Sugerencia: intenta conectar a {suggested_target}")
                        try:
                            auto_connect = input("¿Conectar automáticamente? (y/n): ").lower().strip()
                            if auto_connect in ['y', 'yes', 's', 'si']:
                                connect_device(suggested_target)
                        except (EOFError, KeyboardInterrupt):
                            pass
        except (ValueError, EOFError):
            pass

    # Discover network devices
    print("\n🔍 Buscando dispositivos Android en la red...")
    network_devices = discover_devices()

    if network_devices:
        print(f"\n📡 Dispositivos encontrados en la red ({len(network_devices)}):")
        for i, device in enumerate(network_devices, 1):
            print(f"  {i}. 📱 {device['name']} - {device['info']}")

        # Generate QR for the first device or ask user to choose
        if len(network_devices) == 1:
            selected_device = network_devices[0]
        else:
            try:
                choice = input(f"\nElige un dispositivo (1-{len(network_devices)}) o presiona Enter para el primero: ")
                if choice.isdigit() and 1 <= int(choice) <= len(network_devices):
                    selected_device = network_devices[int(choice) - 1]
                else:
                    selected_device = network_devices[0]
            except (ValueError, EOFError):
                selected_device = network_devices[0]

        # Extract IP and port from device info
        device_info = selected_device['info']
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', device_info)

        if ip_match:
            ip = ip_match.group(1)
            port = ip_match.group(2)
            target = f"{ip}:{port}"

            print(f"\n🎯 Dispositivo seleccionado: {selected_device['name']}")
            print(f"📍 Target: {target}")

            # Generate QR code for ADB connect
            print("\n📱 Escanea este QR en tu dispositivo Android:")
            print("=" * 50)

            qr_code = generate_qr_code(target)
            if qr_code:
                print(qr_code)
            else:
                print(f"Conéctate manualmente con: adb connect {target}")

            print("=" * 50)

            # Ask if user wants to connect automatically
            try:
                auto_connect = input("\n¿Conectar automáticamente? (y/n): ").lower().strip()
                if auto_connect in ['y', 'yes', 's', 'si']:
                    connect_device(target)
            except (EOFError, KeyboardInterrupt):
                pass

        else:
            print(f"❌ No se pudo extraer IP:puerto de: {device_info}")

    else:
        print("\n❌ No se encontraron dispositivos en la red.")
        print("\n💡 Asegúrate de que:")
        print("   1. Tu dispositivo Android tenga WiFi encendido")
        print("   2. Las opciones de desarrollador estén activadas")
        print("   3. 'Depuración por WiFi' esté habilitada")
        print("   4. El dispositivo esté en la misma red WiFi")
        print("   5. ADB esté actualizado (mDNS requiere versión reciente)")

        # Show manual connection option
        try:
            manual_ip = input("\n¿Quieres intentar conectar manualmente? Ingresa IP:puerto (ej: 192.168.1.100:5555): ")
            if manual_ip.strip():
                # Try the entered address
                if not connect_device(manual_ip.strip()):
                    # If it fails, try with port 5555
                    ip_part = manual_ip.split(':')[0]
                    if connect_device(f"{ip_part}:5555"):
                        print("💡 Conectado usando el puerto estándar 5555")
        except (EOFError, KeyboardInterrupt):
            pass

if __name__ == "__main__":
    main()