#!/usr/bin/env python3
"""
Advanced Live Reload Server for Protonox Framework.
Supports multiple connection methods: QR code, manual IP/port, ADB device detection.
"""

import asyncio
import json
import os
import socket
import subprocess
import sys
import threading
import time
from typing import List, Dict, Optional

try:
    import qrcode
    import websockets
    from zeroconf import Zeroconf, ServiceBrowser, ServiceListener
    HAS_DEPS = True
except ImportError as e:
    print(f"❌ Faltan dependencias: {e}")
    print("Instala con: pip install qrcode[pil] websockets zeroconf")
    sys.exit(1)

# Global state
_connected_clients = set()
_detected_devices = {}
_adb_devices = []

class AndroidDeviceListener(ServiceListener):
    """Listener for Android devices using mDNS"""

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            device_info = {
                'name': name,
                'address': socket.inet_ntoa(info.addresses[0]) if info.addresses else 'Unknown',
                'port': info.port,
                'type': type
            }
            _detected_devices[name] = device_info
            print(f"📱 Dispositivo Android detectado: {name} - {device_info['address']}:{device_info['port']}")

    def remove_service(self, zeroconf, type, name):
        if name in _detected_devices:
            del _detected_devices[name]
            print(f"📱 Dispositivo removido: {name}")

def get_local_ip() -> str:
    """Get the local IP address"""
    try:
        # Create a socket to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def scan_adb_devices() -> List[Dict]:
    """Scan for ADB devices"""
    devices = []
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header

        for line in lines:
            if line.strip() and not line.startswith('*'):
                parts = line.split('\t')
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]

                    # Get device model
                    try:
                        model_result = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                                                    capture_output=True, text=True, timeout=3)
                        model = model_result.stdout.strip() or "Unknown Model"
                    except:
                        model = "Unknown Model"

                    devices.append({
                        'id': device_id,
                        'status': status,
                        'model': model,
                        'connection_type': 'adb'
                    })

    except FileNotFoundError:
        print("⚠️  ADB no encontrado. Instala Android SDK Platform Tools.")
    except Exception as e:
        print(f"⚠️  Error escaneando ADB: {e}")

    return devices

def generate_qr_code(data: str) -> str:
    """Generate QR code as ASCII art"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create ASCII art with better contrast
        matrix = qr.get_matrix()
        qr_art = []
        for row in matrix:
            line = ""
            for cell in row:
                line += "█" if cell else "░"
            qr_art.append(line)

        return "\n".join(qr_art)
    except Exception as e:
        print(f"❌ Error generando QR: {e}")
        return None

async def websocket_handler(websocket, path):
    """Handle WebSocket connections"""
    client_addr = websocket.remote_address
    print(f"📱 Cliente conectado desde: {client_addr}")

    _connected_clients.add(websocket)

    try:
        # Send welcome message with server info
        welcome_msg = {
            "type": "welcome",
            "message": "Conectado al servidor de live reload de Protonox",
            "server": f"{get_local_ip()}:8765",
            "capabilities": ["live_reload", "file_sync", "adb_connect"]
        }
        await websocket.send(json.dumps(welcome_msg))

        # Keep connection alive and listen for messages
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"📨 Mensaje recibido de {client_addr}: {data.get('type', 'unknown')}")

                # Handle different message types
                if data.get('type') == 'ping':
                    await websocket.send(json.dumps({"type": "pong", "timestamp": time.time()}))
                elif data.get('type') == 'request_devices':
                    devices = scan_adb_devices()
                    await websocket.send(json.dumps({
                        "type": "device_list",
                        "adb_devices": devices,
                        "mdns_devices": list(_detected_devices.values())
                    }))
                elif data.get('type') == 'adb_connect':
                    device_id = data.get('device_id')
                    if device_id:
                        # Attempt ADB connect
                        try:
                            result = subprocess.run(['adb', 'connect', device_id],
                                                  capture_output=True, text=True, timeout=10)
                            await websocket.send(json.dumps({
                                "type": "adb_result",
                                "device_id": device_id,
                                "success": result.returncode == 0,
                                "output": result.stdout + result.stderr
                            }))
                        except Exception as e:
                            await websocket.send(json.dumps({
                                "type": "adb_result",
                                "device_id": device_id,
                                "success": False,
                                "error": str(e)
                            }))
                else:
                    # Echo back unknown messages
                    response = {
                        "type": "echo",
                        "received": data,
                        "status": "ok"
                    }
                    await websocket.send(json.dumps(response))

            except json.JSONDecodeError:
                print(f"❌ Mensaje inválido JSON de {client_addr}: {message}")

    except websockets.exceptions.ConnectionClosed:
        print(f"👋 Cliente desconectado: {client_addr}")
    finally:
        _connected_clients.discard(websocket)

async def broadcast_message(message: dict):
    """Broadcast message to all connected clients"""
    if _connected_clients:
        message_json = json.dumps(message)
        await asyncio.gather(
            *[client.send(message_json) for client in _connected_clients],
            return_exceptions=True
        )

async def device_monitoring_loop():
    """Monitor for device changes"""
    while True:
        try:
            # Scan for ADB devices periodically
            new_devices = scan_adb_devices()
            if new_devices != _adb_devices:
                _adb_devices[:] = new_devices
                await broadcast_message({
                    "type": "device_update",
                    "adb_devices": new_devices
                })

            await asyncio.sleep(5)  # Check every 5 seconds

        except Exception as e:
            print(f"⚠️  Error en monitoreo de dispositivos: {e}")
            await asyncio.sleep(5)

async def start_websocket_server(host="0.0.0.0", port=8765):
    """Start the WebSocket server with device monitoring"""
    print(f"🚀 Iniciando servidor WebSocket en {host}:{port}")

    # Start device monitoring
    monitor_task = asyncio.create_task(device_monitoring_loop())

    # Start WebSocket server
    server = await websockets.serve(websocket_handler, host, port)
    print("✅ Servidor WebSocket iniciado")

    # Start mDNS discovery
    zeroconf = Zeroconf()
    listener = AndroidDeviceListener()
    browser = ServiceBrowser(zeroconf, "_adb-tls-connect._tcp.local.", listener)

    try:
        # Keep servers running
        await asyncio.gather(
            server.wait_closed(),
            monitor_task
        )
    finally:
        zeroconf.close()

def show_connection_options():
    """Show all available connection methods"""
    ip = get_local_ip()
    port = 8765

    print("\n🔗 MÉTODOS DE CONEXIÓN DISPONIBLES:")
    print("=" * 60)

    # QR Code method
    print("\n📱 MÉTODO 1: Código QR")
    print("-" * 30)
    qr_data = f"ws://{ip}:{port}"
    qr_code = generate_qr_code(qr_data)
    if qr_code:
        print("Escanea este código QR con tu celular:")
        print(qr_code)
    else:
        print(f"Conéctate manualmente a: {qr_data}")

    # Manual connection method
    print("\n🔢 MÉTODO 2: Conexión Manual")
    print("-" * 30)
    print(f"IP Address: {ip}")
    print(f"Puerto: {port}")
    print(f"WebSocket URL: ws://{ip}:{port}")
    print("\nIngresa estos datos en tu app móvil")

    # ADB devices
    print("\n📱 MÉTODO 3: Dispositivos ADB Detectados")
    print("-" * 30)
    devices = scan_adb_devices()
    if devices:
        for i, device in enumerate(devices, 1):
            status_icon = "🟢" if device['status'] == 'device' else "🟡"
            print(f"{i}. {status_icon} {device['model']} ({device['id']}) - {device['status']}")
    else:
        print("No se detectaron dispositivos ADB")
        print("Asegúrate de que tu dispositivo esté conectado por USB")
        print("o tenga depuración wireless activada")

    print("\n💡 INSTRUCCIONES:")
    print("1. Elige uno de los métodos de conexión arriba")
    print("2. Conecta tu dispositivo Android")
    print("3. El servidor detectará automáticamente la conexión")
    print("4. ¡Listo para live reload!")

def main():
    """Main function"""
    print("🔄 Protonox Live Reload Server v2.0")
    print("=" * 50)
    print("🚀 Servidor avanzado con múltiples métodos de conexión")

    # Show connection options
    show_connection_options()

    print("\n🔄 Servidor corriendo... Presiona Ctrl+C para detener")
    print("📊 Monitoreando dispositivos cada 5 segundos...")

    try:
        # Start the WebSocket server
        asyncio.run(start_websocket_server())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()