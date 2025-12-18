#!/usr/bin/env python3
"""
Example Kivy app with wireless debugging enabled.

Run with: PROTONOX_WIRELESS_DEBUG=1 python wireless_debug_example.py

This will start a WebSocket server on port 8765 and display a QR code
with the connection info for Protonox Studio.

- On Android: QR shows IP:5555 for ADB wireless connect
- On other platforms: QR shows ws://IP:8765 for direct WebSocket connect
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.logger import Logger


class WirelessDebugExample(App):
    def build(self):
        Logger.info("Starting Wireless Debug Example App")
        
        layout = BoxLayout(orientation='vertical')
        
        label = Label(text="Wireless Debug Example\nCheck console for QR code")
        layout.add_widget(label)
        
        button = Button(text="Click me!")
        button.bind(on_press=self.on_button_press)
        layout.add_widget(button)
        
        return layout
    
    def on_button_press(self, instance):
        Logger.info("Button pressed!")
        instance.text = "Clicked!"


if __name__ == '__main__':
    app = WirelessDebugExample()
    app.run()