#!/usr/bin/env python3
"""Minimal Kivy demo forcing SDL3 window and PangoFT2 text provider.

Run with the project virtualenv activated or with the full python path:

    KIVY_NO_ARGS=1 /home/protonox/Protonox/venv_kivy/bin/python demo_sdl3_test.py

If SDL3/Pango are missing on the host the app will fail to create a window.
"""
import os
import sys

# Force SDL3 window backend before importing Kivy
os.environ.setdefault('KIVY_WINDOW', 'sdl3')

# Prefer local dev7 `kivy-protonox-version` if present
local_kivy = os.path.join(os.path.dirname(__file__), 'kivy-protonox-version')
if os.path.isdir(local_kivy) and local_kivy not in sys.path:
    sys.path.insert(0, local_kivy)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window

Window.size = (900, 480)

class SDL3DemoApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=20, spacing=12)
        root.add_widget(Label(text='SDL3 + PangoFT2 demo', font_size='36sp', size_hint=(1, 0.2)))
        root.add_widget(Label(text='Hola — prueba de texto renderizado por pangoft2', font_size='20sp'))
        return root


if __name__ == '__main__':
    SDL3DemoApp().run()
