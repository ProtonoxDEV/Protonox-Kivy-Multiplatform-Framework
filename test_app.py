import os
import sys

# Prefer the local `kivy-protonox-version` package (dev8) when running this test.
# Insert it at the front of `sys.path` before any Kivy imports.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_LOCAL_KIVY = os.path.join(_THIS_DIR, 'kivy-protonox-version')
if os.path.isdir(_LOCAL_KIVY) and _LOCAL_KIVY not in sys.path:
    sys.path.insert(0, _LOCAL_KIVY)

# Force SDL3 window provider for this test app. Set before any Kivy imports.
os.environ.setdefault('KIVY_WINDOW', 'sdl3')

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics import ScissorPush, ScissorPop  # Test kivy-protonox imports

class TestApp(MDApp):
    def build(self):
        # Test ScissorPush/ScissorPop from kivy-protonox
        layout = MDBoxLayout(orientation='vertical')
        label = MDLabel(text='Hello from Protonox!\nKivyMD + ScissorPush/ScissorPop working!\nReady for wireless debug')
        layout.add_widget(label)
        return layout

if __name__ == '__main__':
    TestApp().run()