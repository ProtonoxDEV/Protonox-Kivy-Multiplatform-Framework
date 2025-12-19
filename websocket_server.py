#!/usr/bin/env python3
"""
Simple WebSocket server for live reload testing.
Shows QR code for mobile connection.
"""

import os
import sys
import asyncio
import json
import websockets
import qrcode
import socket

# Get local IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()
PORT = 8765

async def websocket_handler(websocket, path):
    """Handle WebSocket connections."""
    print(f"📱 Cliente conectado desde: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"📨 Mensaje recibido: {message}")

            # Echo back for testing
            response = {
                "type": "echo",
                "message": f"Recibido: {message}",
                "timestamp": str(asyncio.get_event_loop().time())
            }
            await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print(f"👋 Cliente desconectado: {websocket.remote_address}")

def generate_qr_ascii(text):
    """Generate ASCII QR code."""
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(text)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    qr_lines = []
    for row in matrix:
        line = ""
        for cell in row:
            line += "██" if cell else "  "
        qr_lines.append(line)

    return "\n".join(qr_lines)

async def main():
    """Main WebSocket server."""
    print("🚀 Protonox Live Reload Server")
    print("=" * 40)
    print(f"🌐 IP: {LOCAL_IP}")
    print(f"🔌 Puerto: {PORT}")

    # Generate QR code
    ws_url = f"ws://{LOCAL_IP}:{PORT}"
    print(f"\n🔗 URL: {ws_url}")

    qr_ascii = generate_qr_ascii(ws_url)
    print("\n📱 Escanea este QR con tu app WebSocket:")
    print("=" * 40)
    print(qr_ascii)
    print("=" * 40)

    print("\n💡 Instrucciones:")
    print("1. Escanea el QR con una app WebSocket (ej: WebSocket King)")
    print("2. O conecta manualmente a la URL de arriba")
    print("3. Envía mensajes para probar la conexión")
    print("\n🔄 Servidor corriendo. Presiona Ctrl+C para detener.")

    # Start WebSocket server
    server = await websockets.serve(websocket_handler, "0.0.0.0", PORT)

    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")

if __name__ == "__main__":
    asyncio.run(main())