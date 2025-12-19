#!/usr/bin/env python3
"""
App de ejemplo para demostrar live reload con Protonox.
Esta app se conecta al servidor de live reload y puede recibir actualizaciones.
"""

import asyncio
import json
import os
import sys
import threading
import time
from datetime import datetime

# Set headless environment for server mode
os.environ['KIVY_HEADLESS'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_WINDOW'] = 'headless'
os.environ['KIVY_GL_BACKEND'] = 'mock'
os.environ['DISPLAY'] = ''

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Kivy after setting environment
import kivy
kivy.require('3.0.0.dev5')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.logger import Logger

class LiveReloadDemo(App):
    """Demo app that connects to live reload server"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.websocket = None
        self.connected = False
        self.server_url = "ws://172.24.175.151:8765"

    def build(self):
        Logger.info("🚀 Iniciando Live Reload Demo App")

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title
        title = Label(
            text="🔄 Protonox Live Reload Demo",
            font_size=24,
            size_hint_y=0.2
        )
        layout.add_widget(title)

        # Connection status
        self.status_label = Label(
            text="📡 Estado: Desconectado",
            font_size=16,
            size_hint_y=0.1
        )
        layout.add_widget(self.status_label)

        # Server URL input
        url_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        url_layout.add_widget(Label(text="Server URL:", size_hint_x=0.3))
        self.url_input = TextInput(
            text=self.server_url,
            multiline=False,
            size_hint_x=0.7
        )
        url_layout.add_widget(self.url_input)
        layout.add_widget(url_layout)

        # Buttons
        buttons_layout = BoxLayout(size_hint_y=0.2, spacing=10)

        self.connect_btn = Button(
            text="🔗 Conectar",
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.connect_btn.bind(on_press=self.connect_to_server)
        buttons_layout.add_widget(self.connect_btn)

        self.disconnect_btn = Button(
            text="❌ Desconectar",
            background_color=(0.8, 0.2, 0.2, 1),
            disabled=True
        )
        self.disconnect_btn.bind(on_press=self.disconnect_from_server)
        buttons_layout.add_widget(self.disconnect_btn)

        layout.add_widget(buttons_layout)

        # Message display
        self.message_label = Label(
            text="📨 Mensajes aparecerán aquí",
            font_size=14,
            size_hint_y=0.3
        )
        layout.add_widget(self.message_label)

        # Test button
        test_btn = Button(
            text="📤 Enviar Mensaje de Prueba",
            size_hint_y=0.1,
            background_color=(0.2, 0.6, 1, 1)
        )
        test_btn.bind(on_press=self.send_test_message)
        layout.add_widget(test_btn)

        # Start connection attempt
        Clock.schedule_once(lambda dt: self.connect_to_server(None), 1)

        return layout

    def connect_to_server(self, instance):
        """Connect to the live reload server"""
        if self.connected:
            return

        self.server_url = self.url_input.text
        self.status_label.text = "📡 Estado: Conectando..."
        self.connect_btn.disabled = True

        # Start WebSocket connection in a thread
        threading.Thread(target=self._websocket_thread, daemon=True).start()

    def disconnect_from_server(self, instance):
        """Disconnect from server"""
        if self.websocket:
            asyncio.run(self.websocket.close())
        self._update_connection_status(False)

    def send_test_message(self, instance):
        """Send a test message to the server"""
        if not self.connected:
            self.message_label.text = "❌ No conectado al servidor"
            return

        async def send_msg():
            try:
                test_msg = {
                    "type": "test",
                    "message": f"Hola desde la app! {datetime.now().strftime('%H:%M:%S')}",
                    "app": "LiveReloadDemo"
                }
                await self.websocket.send(json.dumps(test_msg))
                self.message_label.text = f"📤 Mensaje enviado: {test_msg['message']}"
            except Exception as e:
                self.message_label.text = f"❌ Error enviando mensaje: {e}"

        asyncio.run(send_msg())

    def _websocket_thread(self):
        """WebSocket connection thread"""
        async def connect():
            try:
                async with websockets.connect(self.server_url) as websocket:
                    self.websocket = websocket
                    self._update_connection_status(True)

                    # Listen for messages
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            Clock.schedule_once(
                                lambda dt: self._handle_message(data), 0
                            )
                        except json.JSONDecodeError:
                            Logger.warning(f"Invalid JSON received: {message}")

            except Exception as e:
                Logger.error(f"WebSocket error: {e}")
                self._update_connection_status(False)

        asyncio.run(connect())

    def _update_connection_status(self, connected):
        """Update connection status display"""
        def update(dt):
            self.connected = connected
            if connected:
                self.status_label.text = f"📡 Estado: Conectado a {self.server_url}"
                self.connect_btn.disabled = True
                self.disconnect_btn.disabled = False
                self.status_label.color = (0, 1, 0, 1)  # Green
            else:
                self.status_label.text = "📡 Estado: Desconectado"
                self.connect_btn.disabled = False
                self.disconnect_btn.disabled = True
                self.status_label.color = (1, 0, 0, 1)  # Red
                self.websocket = None

        Clock.schedule_once(update, 0)

    def _handle_message(self, data):
        """Handle incoming messages"""
        msg_type = data.get('type', 'unknown')

        if msg_type == 'welcome':
            self.message_label.text = f"🎉 {data.get('message', 'Bienvenido!')}"
        elif msg_type == 'echo':
            self.message_label.text = f"🔄 Echo: {data.get('received', {}).get('message', 'N/A')}"
        elif msg_type == 'device_list':
            devices = data.get('adb_devices', [])
            self.message_label.text = f"📱 Dispositivos detectados: {len(devices)}"
        elif msg_type == 'pong':
            self.message_label.text = f"🏓 Pong recibido: {datetime.fromtimestamp(data.get('timestamp', 0)).strftime('%H:%M:%S')}"
        else:
            self.message_label.text = f"📨 Mensaje: {msg_type}"

if __name__ == '__main__':
    # Run in headless mode for server testing
    if '--headless' in sys.argv:
        print("🖥️  Ejecutando en modo headless (sin ventana)")
        # Just run the WebSocket client without GUI
        import websockets

        async def headless_client():
            server_url = "ws://172.24.175.151:8765"
            print(f"🔗 Conectando a {server_url} en modo headless...")

            try:
                async with websockets.connect(server_url) as websocket:
                    print("✅ Conectado en modo headless")

                    # Send a test message
                    test_msg = {"type": "test", "message": "Mensaje desde modo headless"}
                    await websocket.send(json.dumps(test_msg))
                    print("📤 Mensaje de prueba enviado")

                    # Listen for a few messages
                    for i in range(3):
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            data = json.loads(message)
                            print(f"📨 Respuesta {i+1}: {data}")
                        except asyncio.TimeoutError:
                            print(f"⏰ Timeout esperando mensaje {i+1}")
                            break

                    print("👋 Cerrando conexión headless")

            except Exception as e:
                print(f"❌ Error en modo headless: {e}")

        asyncio.run(headless_client())

    else:
        # Run GUI app
        LiveReloadDemo().run()