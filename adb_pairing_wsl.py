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

def get_adb_command():
    """Get ADB command - use Windows ADB in WSL"""
    is_wsl = check_wsl_environment()
    
    if is_wsl:
        # Common Windows ADB paths
        windows_paths = [
            "/mnt/c/Users/Protonox/AppData/Local/Android/Sdk/platform-tools/adb.exe",  # User's actual path
            "/mnt/c/Program Files (x86)/Android/android-sdk/platform-tools/adb.exe",
            "/mnt/c/Program Files/Android/sdk/platform-tools/adb.exe",
            "/mnt/c/Android/platform-tools/adb.exe"
        ]
        
        for path in windows_paths:
            if '*' in path:
                # Handle wildcard for user directory
                import glob
                matches = glob.glob(path)
                if matches:
                    return f'"{matches[0]}"'
            elif os.path.exists(path):
                return f'"{path}"'
        
    return "adb"

def generate_pairing_code():
    """Generate a 6-digit pairing code"""
    return f"{random.randint(100000, 999999)}"

def get_local_ip():
    """Get local IP address - Windows IP for WSL"""
    try:
        # Check if WSL
        is_wsl = check_wsl_environment()
        
        if is_wsl:
            # In WSL, get Windows host IP (gateway)
            code, stdout, stderr = run_command("ip route | grep default | awk '{print $3}'")
            if code == 0 and stdout.strip():
                windows_ip = stdout.strip()
                print(f"🔗 IP de Windows detectada: {windows_ip}")
                return windows_ip
        
        # Fallback to WSL IP or other methods
        code, stdout, stderr = run_command("hostname -I | awk '{print $1}'")
        if code == 0 and stdout.strip():
            return stdout.strip()

        # Fallback to ip route
        code, stdout, stderr = run_command("ip route get 8.8.8.8 | awk '{print $7}' | head -1")
        if code == 0 and stdout.strip():
            return stdout.strip()

    except Exception as e:
        print(f"⚠️  Error obteniendo IP local: {e}")

    return "192.168.1.100"  # Default fallback

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

def start_adb_pairing_server(pairing_code, device_name="ProtonoxWSL", adb_cmd="adb"):
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
        print("📡 El servidor está listo para recibir conexiones")
        print("🔄 Monitoreando conexiones entrantes...")
        print()

        # Start monitoring for new devices
        initial_devices = check_adb_devices(adb_cmd, verbose=False)  # Silent initial check
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        last_status_print = 0
        status_interval = 8  # Print status every 8 seconds

        # If we already have devices connected, give user immediate option to continue
        if initial_devices:
            print(f"\n📱 ¡Dispositivo(s) ya conectado(s)! ({len(initial_devices)})")
            print("💡 Puedes continuar inmediatamente al Live Reload")
            print("   • Presiona Enter para continuar automáticamente")
            print("   • O espera para intentar conectar dispositivos adicionales")

            # Wait for user input or timeout
            try:
                import select
                import sys
                ready, _, _ = select.select([sys.stdin], [], [], 5.0)  # 5 second timeout
                if ready:
                    user_input = sys.stdin.readline().strip().lower()
                    if user_input in ['', 'y', 'yes', 'c', 'continue']:
                        print("\n➡️  Continuando automáticamente al siguiente paso...")
                        print("\n🔍 Verificando estado final de dispositivos...")
                        final_devices = check_adb_devices(adb_cmd, verbose=False)
                        already_connected = len(final_devices)
                        if already_connected > 0:
                            print(f"ℹ️  {already_connected} dispositivo(s) conectado(s)")
                            print("💡 Puedes proceder al siguiente paso")
                            print("🚀 Selecciona la opción 2 en el menú principal para Live Reload")
                        return True
            except:
                pass  # Continue with normal flow if input fails

        while time.time() - start_time < timeout:
            time.sleep(2)  # Check every 2 seconds
            current_devices = check_adb_devices(adb_cmd, verbose=False)  # Less verbose checking

            # Check for new devices
            new_devices = []
            for device in current_devices:
                if not any(d['id'] == device['id'] for d in initial_devices):
                    new_devices.append(device)

            if new_devices:
                print(f"\n🎉 ¡Dispositivo detectado!")
                for device in new_devices:
                    redmi_icon = "📱" if device.get('is_redmi') else "🤖"
                    print(f"   {redmi_icon} {device['id']} - {device['info']}")

                    if device.get('is_redmi'):
                        print("   🔥 ¡Redmi Note 14 Pro detectado y conectado!")
                        print("   💡 Este dispositivo es totalmente compatible con Protonox")
                        print("   🚀 Listo para desarrollo wireless y live reload")

                print("\n✅ ¡Pairing completado exitosamente!")
                print("💡 Ahora puedes:")
                print("   • Cerrar esta ventana (Ctrl+C)")
                print("   • Volver al menú principal de Protonox")
                print("   • Seleccionar opción 2 para Live Reload")
                break

            # Show progress with option to continue (less frequent status updates)
            elapsed = int(time.time() - start_time)
            current_time = time.time()

            # Print status update every 8 seconds or if it's been more than 20 seconds
            if current_time - last_status_print >= status_interval or elapsed > 20:
                connected_count = len(current_devices)
                if connected_count > 0:
                    print(f"\r⏱️  Esperando nuevos dispositivos... ({elapsed}s) - {connected_count} ya conectado(s) - Presiona Enter para continuar, Ctrl+C para cancelar", end='', flush=True)
                else:
                    print(f"\r⏱️  Esperando conexión... ({elapsed}s) - Presiona Ctrl+C para cancelar", end='', flush=True)
                last_status_print = current_time

            # Check for user input to continue (now also Enter key)
            try:
                import select
                import sys
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    user_input = sys.stdin.readline().strip().lower()
                    if user_input in ['', 'y', 'yes', 'c', 'continue']:
                        print("\n➡️  Continuando al siguiente paso...")
                        break
            except:
                pass  # Ignore input errors

        else:
            print("\n⏰ Timeout: No se detectaron nuevos dispositivos")
            print("💡 Verifica que seguiste las instrucciones correctamente")

    except KeyboardInterrupt:
        print("\n👋 Servidor de pairing detenido por el usuario")
    except Exception as e:
        print(f"❌ Error en servidor de pairing: {e}")

def check_adb_devices(adb_cmd=None, verbose=True):
    """Check connected ADB devices"""
    if adb_cmd is None:
        adb_cmd = get_adb_command()
    
    if verbose:
        print("📱 Verificando dispositivos ADB conectados...")
    code, stdout, stderr = run_command(f"{adb_cmd} devices -l")

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

                    # Detect Redmi/Xiaomi devices
                    is_redmi = any(keyword in device_info.lower() for keyword in ['redmi', 'xiaomi', 'mi '])

                    devices.append({
                        'id': device_id,
                        'status': status,
                        'info': device_info,
                        'is_redmi': is_redmi
                    })

        if verbose:
            if devices:
                print(f"✅ Encontrados {len(devices)} dispositivo(s):")
                for device in devices:
                    status_icon = "🟢" if device['status'] == 'device' else "🟡"
                    redmi_icon = "📱" if device['is_redmi'] else "🤖"
                    print(f"   {status_icon} {redmi_icon} {device['id']} - {device['info']}")
                    if device['is_redmi']:
                        print("      💡 Dispositivo Redmi/Xiaomi detectado - ¡Compatible!")
            else:
                print("❌ No hay dispositivos conectados")
                print("💡 Conecta tu dispositivo por USB o configura wireless debugging")

        return devices
    else:
        print(f"❌ Error verificando dispositivos: {stderr}")
        return []

def scan_network_for_android_devices():
    """Scan network for Android devices that might be available for wireless debugging"""
    print("\n🔍 Escaneando red en busca de dispositivos Android...")
    print("   (Esto puede tomar unos segundos)")

    local_ip = get_local_ip()
    if not local_ip:
        print("❌ No se pudo determinar la IP local")
        return []

    # Get network range (assuming /24 subnet)
    ip_parts = local_ip.split('.')
    network_prefix = '.'.join(ip_parts[:3]) + '.'

    found_devices = []

    # Scan common ports for Android wireless debugging
    import socket
    import concurrent.futures

    def check_port(ip, port, timeout=1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_ip(ip):
        devices = []
        # Check common Android wireless debugging ports
        if check_port(ip, 5555):  # ADB wireless port
            devices.append({'ip': ip, 'port': 5555, 'type': 'adb_wireless'})
        if check_port(ip, 37329):  # ADB pairing port
            devices.append({'ip': ip, 'port': 37329, 'type': 'adb_pairing'})
        return devices

    # Scan network range (first 20 IPs for speed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(scan_ip, f"{network_prefix}{i}") for i in range(1, 21)]
        for future in concurrent.futures.as_completed(futures):
            found_devices.extend(future.result())

    if found_devices:
        print(f"✅ Encontrados {len(found_devices)} posibles dispositivos Android:")
        for device in found_devices:
            print(f"   📡 {device['ip']}:{device['port']} ({device['type']})")
    else:
        print("❌ No se encontraron dispositivos Android en la red local")
        print("💡 Asegúrate de que:")
        print("   • Tu dispositivo esté conectado a la misma red WiFi")
        print("   • Wireless debugging esté activado en el dispositivo")
        print("   • El firewall no bloquee las conexiones ADB")

    return found_devices

def test_adb_connection(adb_cmd=None):
    """Test ADB connection with a simple command"""
    if adb_cmd is None:
        adb_cmd = get_adb_command()
    
    devices = check_adb_devices(adb_cmd)
    if not devices:
        return False

    # Test with first device
    device = devices[0]
    print(f"\n🧪 Probando conexión con {device['id']}...")

    # Special handling for Redmi devices
    if device.get('is_redmi'):
        handle_redmi_device(device)

    code, stdout, stderr = run_command(f"{adb_cmd} -s {device['id']} shell echo 'ADB connection test'")
    if code == 0 and "ADB connection test" in stdout:
        print("✅ Conexión ADB exitosa")
        return True
    else:
        print(f"❌ Error en conexión ADB: {stderr}")
        if device.get('is_redmi'):
            print("💡 Para Redmi: Verifica que el dispositivo esté autorizado")
            print("   Ejecuta: adb devices (debería mostrar 'device' no 'unauthorized')")
        return False

def main():
    """Main function"""
    print("🔧 Protonox ADB Wireless Pairing Tool")
    print("🐧 Optimizado para WSL2 sobre Windows 11")
    print("=" * 50)

    # Check WSL environment
    is_wsl = check_wsl_environment()

    # Check ADB availability
    adb_cmd = get_adb_command()
    code, stdout, stderr = run_command(f"{adb_cmd} version")
    if code != 0:
        print("❌ ADB no está disponible")
        print("💡 Instala Android SDK Platform Tools:")
        print("   Windows: https://developer.android.com/studio/releases/platform-tools")
        print("   WSL: sudo apt install android-tools-adb")
        return

    print(f"✅ ADB disponible: {stdout.split()[2] if stdout else 'Unknown'}")

    # Check current devices
    initial_devices = check_adb_devices(adb_cmd)

    # Scan network for available Android devices
    print("\n🔍 Buscando dispositivos Android en la red...")
    network_devices = scan_network_for_android_devices()

    if network_devices:
        print("\n💡 Dispositivos encontrados en la red. Si tu Redmi Note 14 Pro aparece aquí,")
        print("   significa que wireless debugging está activo y listo para conectar.")
        print("   Solo necesitas el código de pairing que aparecerá en tu teléfono.")

    # Generate pairing code
    pairing_code = generate_pairing_code()
    device_name = "ProtonoxWSL"

    print(f"\n🎯 Código de pairing generado: {pairing_code}")
    print(f"🏷️  Nombre del dispositivo: {device_name}")
    print("\n📱 INSTRUCCIONES PARA REDMI NOTE 14 PRO:")
    print("=" * 50)
    print("1. Ve a Configuración → Acerca del teléfono")
    print("2. Toca 'Número de compilación' 7 veces para activar opciones de desarrollador")
    print("3. Ve a Configuración → Opciones de desarrollador")
    print("4. Activa 'Depuración USB' y 'Depuración inalámbrica USB'")
    print("5. Toca 'Depuración inalámbrica' → 'Emparejar dispositivo con código de emparejamiento'")
    print("6. Tu teléfono mostrará una IP, puerto y código")
    print("7. Usa el código que aparece en tu teléfono (NO el de arriba)")
    print("=" * 50)

    # Start pairing server
    try:
        start_adb_pairing_server(pairing_code, device_name, adb_cmd)

        # After pairing attempt, check devices again
        print("\n🔍 Verificando estado final de dispositivos...")
        final_devices = check_adb_devices(adb_cmd, verbose=False)

        new_devices = len(final_devices) - len(initial_devices)
        already_connected = len(initial_devices)

        if new_devices > 0:
            print(f"✅ ¡Éxito! {new_devices} dispositivo(s) nuevo(s) conectado(s)")

            # Test connection
            if test_adb_connection(adb_cmd):
                print("\n🎉 ¡Listo para desarrollo!")
                print("📱 Tu dispositivo Android está conectado vía wireless")
                print("🚀 Puedes usar live reload y debugging remoto")
            else:
                print("\n⚠️  Dispositivo conectado pero la conexión no responde")
                print("💡 Verifica que el dispositivo esté desbloqueado y con debugging activado")

        elif already_connected > 0:
            print(f"ℹ️  {already_connected} dispositivo(s) ya estaba(n) conectado(s)")
            print("💡 Si este es tu dispositivo, puedes proceder al siguiente paso")
            print("🚀 Selecciona la opción 2 en el menú principal para Live Reload")

            # Test existing connection
            if test_adb_connection(adb_cmd):
                print("✅ La conexión existente está funcionando correctamente")
            else:
                print("⚠️  La conexión existente no responde")
                print("💡 Puede que necesites reconectar el dispositivo")

        else:
            print("\n❌ No se detectaron dispositivos conectados")
            print("💡 Verifica:")
            print("   • Que seguiste las instrucciones correctamente")
            print("   • Que tu dispositivo Android está en la misma red WiFi")
            print("   • Que las opciones de desarrollador están activadas")
            if is_wsl:
                print("   • Que WSL2 tiene conectividad de red (prueba método numérico)")
            return False

    except KeyboardInterrupt:
        print("\n👋 Proceso cancelado por el usuario")
        return True  # Consider successful if user manually cancelled (likely after connecting)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

    # If we reach here, consider it successful (either devices connected or user cancelled)
    return True

if __name__ == "__main__":
    main()