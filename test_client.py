#!/usr/bin/env python3
"""
Cliente de prueba para el servidor de live reload de Protonox.
Conecta al servidor WebSocket y permite probar la comunicación.
"""

import asyncio
import json
import sys
import websockets
from datetime import datetime

async def test_connection(server_url):
    """Test connection to the live reload server"""
    print(f"🔗 Conectando a {server_url}...")

    try:
        async with websockets.connect(server_url) as websocket:
            print("✅ Conexión WebSocket establecida")

            # Receive welcome message
            welcome = await websocket.recv()
            data = json.loads(welcome)
            print(f"📨 Mensaje de bienvenida: {data}")

            # Send a test message
            test_msg = {
                "type": "test",
                "message": "Hola desde el cliente de prueba",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(test_msg))
            print("📤 Mensaje de prueba enviado")

            # Request device list
            device_request = {"type": "request_devices"}
            await websocket.send(json.dumps(device_request))
            print("📤 Solicitud de lista de dispositivos enviada")

            # Listen for responses
            print("\n👂 Escuchando respuestas del servidor...")
            print("Presiona Ctrl+C para salir")

            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    print(f"📨 Respuesta: {json.dumps(data, indent=2)}")
                except asyncio.TimeoutError:
                    # Send ping to keep connection alive
                    ping_msg = {"type": "ping"}
                    await websocket.send(json.dumps(ping_msg))
                    print("🏓 Ping enviado")

    except websockets.exceptions.ConnectionClosed:
        print("👋 Conexión cerrada por el servidor")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    else:
        # Default to local server
        server_url = "ws://172.24.175.151:8765"

    print("🧪 Cliente de Prueba - Protonox Live Reload")
    print("=" * 45)
    print(f"🎯 Servidor objetivo: {server_url}")
    print("\n💡 Este cliente probará la conexión WebSocket")
    print("   y enviará algunos mensajes de prueba")

    try:
        asyncio.run(test_connection(server_url))
    except KeyboardInterrupt:
        print("\n👋 Cliente detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()