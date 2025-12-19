#!/usr/bin/env python3
"""
Protonox Kivy Debug App
Aplicación dedicada para debugging y testing de características de Kivy en dispositivos Android.
Permite probar widgets, layouts, animaciones y funcionalidades sin necesidad de live reload.
"""

import os
import sys
import json
import time
from datetime import datetime

# Configuración para Android
os.environ['KIVY_ORIENTATION'] = 'portrait'
os.environ['KIVY_ANDROID_API'] = '31'
os.environ['KIVY_ANDROID_MINAPI'] = '21'

# Importar Kivy
import kivy
kivy.require('3.0.0.dev5')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.checkbox import CheckBox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.carousel import Carousel
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.camera import Camera
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.colorpicker import ColorPicker

from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.core.camera import Camera as CoreCamera
from kivy.core.clipboard import Clipboard
from kivy.core.text import Label as CoreLabel
from kivy.utils import get_color_from_hex, platform
from kivy.logger import Logger

class DebugInfo(BoxLayout):
    """Widget para mostrar información de debug del sistema"""

    device_info = StringProperty("")
    kivy_version = StringProperty("")
    platform_info = StringProperty("")
    screen_size = StringProperty("")
    memory_info = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)

        # Actualizar información inicial
        self.update_info()

        # Programar actualización periódica
        Clock.schedule_interval(self.update_info, 5)

    def update_info(self, dt=0):
        """Actualizar información del sistema"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            self.memory_info = f"RAM: {memory.percent:.1f}% usado ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)"
        except ImportError:
            self.memory_info = "psutil no disponible"

        self.device_info = f"Dispositivo: {platform()}"
        self.kivy_version = f"Kivy: {kivy.__version__}"
        self.platform_info = f"Python: {sys.version.split()[0]}"
        self.screen_size = f"Pantalla: {Window.size[0]}x{Window.size[1]}"

class WidgetTester(BoxLayout):
    """Widget para probar diferentes componentes de Kivy"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)

        # Título
        title = Label(text="🧪 Probador de Widgets", font_size=sp(20), bold=True, size_hint_y=None, height=dp(40))
        self.add_widget(title)

        # ScrollView para contener todos los widgets de prueba
        scroll = ScrollView(size_hint=(1, 1))
        test_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(10), size_hint_y=None)
        test_layout.bind(minimum_height=test_layout.setter('height'))

        # Botones
        btn_section = self.create_button_section()
        test_layout.add_widget(btn_section)

        # Inputs
        input_section = self.create_input_section()
        test_layout.add_widget(input_section)

        # Selectores
        selector_section = self.create_selector_section()
        test_layout.add_widget(selector_section)

        # Layouts
        layout_section = self.create_layout_section()
        test_layout.add_widget(layout_section)

        # Media
        media_section = self.create_media_section()
        test_layout.add_widget(media_section)

        # Animaciones
        anim_section = self.create_animation_section()
        test_layout.add_widget(anim_section)

        scroll.add_widget(test_layout)
        self.add_widget(scroll)

    def create_button_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="🔘 Botones", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # Botón normal
        btn_normal = Button(text="Normal", size_hint_x=0.25)
        btn_normal.bind(on_press=self.on_button_press)

        # Botón con ícono
        btn_icon = Button(text="📱 Con Ícono", size_hint_x=0.25)
        btn_icon.bind(on_press=self.on_button_press)

        # Botón deshabilitado
        btn_disabled = Button(text="Deshabilitado", disabled=True, size_hint_x=0.25)

        # Botón toggle
        btn_toggle = Button(text="Toggle OFF", size_hint_x=0.25)
        btn_toggle.bind(on_press=self.on_toggle_button)

        btn_layout.add_widget(btn_normal)
        btn_layout.add_widget(btn_icon)
        btn_layout.add_widget(btn_disabled)
        btn_layout.add_widget(btn_toggle)

        layout.add_widget(title)
        layout.add_widget(btn_layout)
        return layout

    def create_input_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="📝 Entradas de Texto", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        input_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # TextInput normal
        ti_normal = TextInput(hint_text="Texto normal", multiline=False, size_hint_x=0.33)

        # TextInput numérico
        ti_numeric = TextInput(hint_text="Solo números", input_filter='int', size_hint_x=0.33)

        # TextInput contraseña
        ti_password = TextInput(hint_text="Contraseña", password=True, size_hint_x=0.33)

        input_layout.add_widget(ti_normal)
        input_layout.add_widget(ti_numeric)
        input_layout.add_widget(ti_password)

        layout.add_widget(title)
        layout.add_widget(input_layout)
        return layout

    def create_selector_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="🎛️ Selectores", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        selector_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # Slider
        slider_layout = BoxLayout(orientation='vertical', size_hint_x=0.25)
        slider_label = Label(text="Slider: 50", font_size=sp(12), size_hint_y=None, height=dp(20))
        slider = Slider(min=0, max=100, value=50, size_hint_y=None, height=dp(40))
        slider.bind(value=self.on_slider_value)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(slider)

        # Switch
        switch_layout = BoxLayout(orientation='vertical', size_hint_x=0.25)
        switch_label = Label(text="Switch: OFF", font_size=sp(12), size_hint_y=None, height=dp(20))
        switch = Switch(size_hint_y=None, height=dp(40))
        switch.bind(active=self.on_switch_active)
        switch_layout.add_widget(switch_label)
        switch_layout.add_widget(switch)

        # Checkbox
        checkbox_layout = BoxLayout(orientation='vertical', size_hint_x=0.25)
        checkbox_label = Label(text="Checkbox: OFF", font_size=sp(12), size_hint_y=None, height=dp(20))
        checkbox = CheckBox(size_hint_y=None, height=dp(40))
        checkbox.bind(active=self.on_checkbox_active)
        checkbox_layout.add_widget(checkbox_label)
        checkbox_layout.add_widget(checkbox)

        # Spinner
        spinner_layout = BoxLayout(orientation='vertical', size_hint_x=0.25)
        spinner_label = Label(text="Spinner", font_size=sp(12), size_hint_y=None, height=dp(20))
        spinner = Spinner(text='Opción 1', values=['Opción 1', 'Opción 2', 'Opción 3'], size_hint_y=None, height=dp(40))
        spinner_layout.add_widget(spinner_label)
        spinner_layout.add_widget(spinner)

        selector_layout.add_widget(slider_layout)
        selector_layout.add_widget(switch_layout)
        selector_layout.add_widget(checkbox_layout)
        selector_layout.add_widget(spinner_layout)

        layout.add_widget(title)
        layout.add_widget(selector_layout)
        return layout

    def create_layout_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(200))
        title = Label(text="📐 Layouts", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        # Demo de diferentes layouts en un grid
        layout_demo = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(150))

        # BoxLayout demo
        box_demo = BoxLayout(orientation='vertical', size_hint=(None, None), size=(dp(80), dp(70)))
        box_demo.add_widget(Label(text="Box", font_size=sp(10)))
        box_demo.add_widget(Button(text="Btn", font_size=sp(10), size_hint_y=None, height=dp(20)))

        # GridLayout demo
        grid_demo = GridLayout(cols=2, rows=2, size_hint=(None, None), size=(dp(80), dp(70)))
        for i in range(4):
            grid_demo.add_widget(Button(text=str(i+1), font_size=sp(8), size_hint=(None, None), size=(dp(35), dp(30))))

        # FloatLayout demo
        float_demo = FloatLayout(size_hint=(None, None), size=(dp(80), dp(70)))
        float_demo.add_widget(Button(text="Float", pos=(dp(10), dp(10)), size_hint=(None, None), size=(dp(60), dp(25)), font_size=sp(8)))

        # RelativeLayout demo
        rel_demo = RelativeLayout(size_hint=(None, None), size=(dp(80), dp(70)))
        rel_demo.add_widget(Button(text="Rel", pos=(dp(5), dp(5)), size_hint=(None, None), size=(dp(50), dp(20)), font_size=sp(8)))

        layout_demo.add_widget(Label(text="BoxLayout", font_size=sp(10), size_hint_y=None, height=dp(20)))
        layout_demo.add_widget(box_demo)
        layout_demo.add_widget(Label(text="GridLayout", font_size=sp(10), size_hint_y=None, height=dp(20)))
        layout_demo.add_widget(grid_demo)
        layout_demo.add_widget(Label(text="FloatLayout", font_size=sp(10), size_hint_y=None, height=dp(20)))
        layout_demo.add_widget(float_demo)
        layout_demo.add_widget(Label(text="RelativeLayout", font_size=sp(10), size_hint_y=None, height=dp(20)))
        layout_demo.add_widget(rel_demo)

        layout.add_widget(title)
        layout.add_widget(layout_demo)
        return layout

    def create_media_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="🎬 Media", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        media_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # ProgressBar
        progress_layout = BoxLayout(orientation='vertical', size_hint_x=0.33)
        progress_label = Label(text="Progreso: 50%", font_size=sp(12), size_hint_y=None, height=dp(20))
        progress = ProgressBar(max=100, value=50, size_hint_y=None, height=dp(30))
        progress_btn = Button(text="Avanzar", size_hint_y=None, height=dp(30), font_size=sp(12))
        progress_btn.bind(on_press=lambda x: self.advance_progress(progress, progress_label))
        progress_layout.add_widget(progress_label)
        progress_layout.add_widget(progress)
        progress_layout.add_widget(progress_btn)

        # ColorPicker (simplificado)
        color_layout = BoxLayout(orientation='vertical', size_hint_x=0.33)
        color_label = Label(text="Color Picker", font_size=sp(12), size_hint_y=None, height=dp(20))
        color_btn = Button(text="🎨 Elegir Color", background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(60))
        color_btn.bind(on_press=self.show_color_picker)
        color_layout.add_widget(color_label)
        color_layout.add_widget(color_btn)

        # Clipboard test
        clipboard_layout = BoxLayout(orientation='vertical', size_hint_x=0.33)
        clipboard_label = Label(text="Clipboard", font_size=sp(12), size_hint_y=None, height=dp(20))
        clipboard_btn = Button(text="Copiar 'Hola!'", size_hint_y=None, height=dp(30), font_size=sp(12))
        clipboard_btn.bind(on_press=lambda x: self.test_clipboard())
        clipboard_paste_btn = Button(text="Pegar", size_hint_y=None, height=dp(30), font_size=sp(12))
        clipboard_paste_btn.bind(on_press=self.show_clipboard_content)
        clipboard_layout.add_widget(clipboard_label)
        clipboard_layout.add_widget(clipboard_btn)
        clipboard_layout.add_widget(clipboard_paste_btn)

        media_layout.add_widget(progress_layout)
        media_layout.add_widget(color_layout)
        media_layout.add_widget(clipboard_layout)

        layout.add_widget(title)
        layout.add_widget(media_layout)
        return layout

    def create_animation_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="🎭 Animaciones", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        anim_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # Botón animado
        anim_btn = Button(text="Animar!", size_hint_x=0.5, background_color=(0.2, 0.6, 1, 1))
        anim_btn.bind(on_press=self.animate_button)

        # Texto que cambia
        self.anim_label = Label(text="Texto normal", size_hint_x=0.5, font_size=sp(16))

        anim_layout.add_widget(anim_btn)
        anim_layout.add_widget(self.anim_label)

        layout.add_widget(title)
        layout.add_widget(anim_layout)
        return layout

    # Event handlers
    def on_button_press(self, instance):
        popup = Popup(title='Botón Presionado',
                     content=Label(text=f'Presionaste: {instance.text}'),
                     size_hint=(0.8, 0.4))
        popup.open()

    def on_toggle_button(self, instance):
        if instance.text == "Toggle OFF":
            instance.text = "Toggle ON"
            instance.background_color = (0, 1, 0, 1)
        else:
            instance.text = "Toggle OFF"
            instance.background_color = (1, 1, 1, 1)

    def on_slider_value(self, instance, value):
        instance.parent.children[1].text = f"Slider: {int(value)}"

    def on_switch_active(self, instance, value):
        instance.parent.children[1].text = f"Switch: {'ON' if value else 'OFF'}"

    def on_checkbox_active(self, instance, value):
        instance.parent.children[1].text = f"Checkbox: {'ON' if value else 'OFF'}"

    def advance_progress(self, progress_bar, label):
        progress_bar.value = min(100, progress_bar.value + 10)
        label.text = f"Progreso: {int(progress_bar.value)}%"

    def show_color_picker(self, instance):
        # Color picker simplificado
        colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1)]
        import random
        new_color = random.choice(colors)
        instance.background_color = new_color
        instance.text = f"🎨 RGB({int(new_color[0]*255)}, {int(new_color[1]*255)}, {int(new_color[2]*255)})"

    def test_clipboard(self):
        Clipboard.copy("Hola desde Protonox Kivy Debug!")
        popup = Popup(title='Clipboard',
                     content=Label(text="'Hola desde Protonox Kivy Debug!' copiado al clipboard"),
                     size_hint=(0.8, 0.4))
        popup.open()

    def show_clipboard_content(self):
        content = Clipboard.paste()
        popup = Popup(title='Clipboard Content',
                     content=Label(text=f'Contenido: "{content}"'),
                     size_hint=(0.8, 0.4))
        popup.open()

    def animate_button(self, instance):
        # Animación de escala y rotación
        anim = Animation(scale=1.2, duration=0.3) + Animation(scale=1, duration=0.3)
        anim.start(instance)

        # Cambiar texto del label con animación
        texts = ["Texto normal", "¡Animando!", "🎭 Wow!", "✨ Genial!"]
        current_text = self.anim_label.text
        try:
            current_index = texts.index(current_text)
            next_index = (current_index + 1) % len(texts)
        except ValueError:
            next_index = 0

        self.anim_label.text = texts[next_index]

class PerformanceTester(BoxLayout):
    """Widget para probar rendimiento y funcionalidades avanzadas"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)

        title = Label(text="⚡ Performance & Advanced Features", font_size=sp(20), bold=True, size_hint_y=None, height=dp(40))
        self.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        perf_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(10), size_hint_y=None)
        perf_layout.bind(minimum_height=perf_layout.setter('height'))

        # Canvas operations
        canvas_section = self.create_canvas_section()
        perf_layout.add_widget(canvas_section)

        # ScreenManager demo
        screen_section = self.create_screen_section()
        perf_layout.add_widget(screen_section)

        # File operations
        file_section = self.create_file_section()
        perf_layout.add_widget(file_section)

        # Network test
        network_section = self.create_network_section()
        perf_layout.add_widget(network_section)

        scroll.add_widget(perf_layout)
        self.add_widget(scroll)

    def create_canvas_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(200))
        title = Label(text="🎨 Canvas Operations", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        canvas_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(150))

        # Canvas demo widget
        self.canvas_demo = CanvasDemo(size_hint_x=0.6)

        # Controls
        controls = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=0.4)

        add_rect_btn = Button(text="➕ Rect", size_hint_y=None, height=dp(35))
        add_rect_btn.bind(on_press=self.canvas_demo.add_rectangle)

        add_circle_btn = Button(text="⭕ Circle", size_hint_y=None, height=dp(35))
        add_circle_btn.bind(on_press=self.canvas_demo.add_circle)

        clear_btn = Button(text="🗑️ Clear", size_hint_y=None, height=dp(35))
        clear_btn.bind(on_press=self.canvas_demo.clear_canvas)

        controls.add_widget(add_rect_btn)
        controls.add_widget(add_circle_btn)
        controls.add_widget(clear_btn)

        canvas_layout.add_widget(self.canvas_demo)
        canvas_layout.add_widget(controls)

        layout.add_widget(title)
        layout.add_widget(canvas_layout)
        return layout

    def create_screen_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(150))
        title = Label(text="📱 Screen Manager", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        screen_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(100))

        # Simple screen manager demo
        self.screen_manager = ScreenManager()

        screen1 = Screen(name='screen1')
        screen1.add_widget(Label(text="Pantalla 1\n\nPresiona los botones para navegar", font_size=sp(14)))

        screen2 = Screen(name='screen2')
        screen2.add_widget(Label(text="Pantalla 2\n\n¡Navegación funciona!", font_size=sp(14)))

        self.screen_manager.add_widget(screen1)
        self.screen_manager.add_widget(screen2)

        # Controls
        controls = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=0.3)

        to_screen1_btn = Button(text="Ir a Pantalla 1", size_hint_y=None, height=dp(35))
        to_screen1_btn.bind(on_press=lambda x: setattr(self.screen_manager, 'current', 'screen1'))

        to_screen2_btn = Button(text="Ir a Pantalla 2", size_hint_y=None, height=dp(35))
        to_screen2_btn.bind(on_press=lambda x: setattr(self.screen_manager, 'current', 'screen2'))

        controls.add_widget(to_screen1_btn)
        controls.add_widget(to_screen2_btn)

        screen_layout.add_widget(self.screen_manager)
        screen_layout.add_widget(controls)

        layout.add_widget(title)
        layout.add_widget(screen_layout)
        return layout

    def create_file_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="📁 File Operations", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        file_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # File operations buttons
        save_btn = Button(text="💾 Guardar\nArchivo", size_hint_x=0.33)
        save_btn.bind(on_press=self.save_test_file)

        load_btn = Button(text="📂 Cargar\nArchivo", size_hint_x=0.33)
        load_btn.bind(on_press=self.load_test_file)

        list_btn = Button(text="📋 Listar\nArchivos", size_hint_x=0.33)
        list_btn.bind(on_press=self.list_files)

        file_layout.add_widget(save_btn)
        file_layout.add_widget(load_btn)
        file_layout.add_widget(list_btn)

        layout.add_widget(title)
        layout.add_widget(file_layout)
        return layout

    def create_network_section(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(120))
        title = Label(text="🌐 Network Test", font_size=sp(16), bold=True, size_hint_y=None, height=dp(30))

        network_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(80))

        # Network test buttons
        ping_btn = Button(text="🏓 Ping\nTest", size_hint_x=0.33)
        ping_btn.bind(on_press=self.test_ping)

        http_btn = Button(text="🌍 HTTP\nTest", size_hint_x=0.33)
        http_btn.bind(on_press=self.test_http)

        socket_btn = Button(text="🔌 Socket\nTest", size_hint_x=0.33)
        socket_btn.bind(on_press=self.test_socket)

        network_layout.add_widget(ping_btn)
        network_layout.add_widget(http_btn)
        network_layout.add_widget(socket_btn)

        layout.add_widget(title)
        layout.add_widget(network_layout)
        return layout

    # Canvas demo methods
    def save_test_file(self, instance):
        try:
            test_data = {
                "timestamp": str(datetime.now()),
                "app": "Protonox Kivy Debug",
                "test": "file_operations"
            }

            # En Android, guardar en la carpeta de la app
            if platform == 'android':
                from android.storage import primary_external_storage_path
                import os
                directory = primary_external_storage_path()
                filepath = os.path.join(directory, 'protonox_debug_test.json')
            else:
                filepath = 'protonox_debug_test.json'

            with open(filepath, 'w') as f:
                json.dump(test_data, f, indent=2)

            popup = Popup(title='Archivo Guardado',
                         content=Label(text=f'Guardado en:\n{filepath}'),
                         size_hint=(0.8, 0.4))
            popup.open()

        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f'Error guardando archivo:\n{str(e)}'),
                         size_hint=(0.8, 0.4))
            popup.open()

    def load_test_file(self, instance):
        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                import os
                directory = primary_external_storage_path()
                filepath = os.path.join(directory, 'protonox_debug_test.json')
            else:
                filepath = 'protonox_debug_test.json'

            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)

                popup = Popup(title='Archivo Cargado',
                             content=Label(text=f'Contenido:\n{json.dumps(data, indent=2)}'),
                             size_hint=(0.8, 0.6))
                popup.open()
            else:
                popup = Popup(title='Archivo No Encontrado',
                             content=Label(text=f'No se encontró:\n{filepath}'),
                             size_hint=(0.8, 0.4))
                popup.open()

        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f'Error cargando archivo:\n{str(e)}'),
                         size_hint=(0.8, 0.4))
            popup.open()

    def list_files(self, instance):
        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                import os
                directory = primary_external_storage_path()
            else:
                directory = '.'

            files = os.listdir(directory)
            file_list = '\n'.join(files[:20])  # Limitar a 20 archivos

            popup = Popup(title=f'Archivos en {directory}',
                         content=Label(text=file_list, font_size=sp(12)),
                         size_hint=(0.9, 0.8))
            popup.open()

        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f'Error listando archivos:\n{str(e)}'),
                         size_hint=(0.8, 0.4))
            popup.open()

    def test_ping(self, instance):
        # Simple ping test
        import subprocess
        try:
            result = subprocess.run(['ping', '-c', '3', '8.8.8.8'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                popup = Popup(title='Ping Exitoso',
                             content=Label(text='Conexión a internet OK'),
                             size_hint=(0.8, 0.4))
            else:
                popup = Popup(title='Ping Fallido',
                             content=Label(text='Sin conexión a internet'),
                             size_hint=(0.8, 0.4))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f'Error en ping:\n{str(e)}'),
                         size_hint=(0.8, 0.4))
            popup.open()

    def test_http(self, instance):
        # Simple HTTP test
        import urllib.request
        try:
            with urllib.request.urlopen('http://httpbin.org/get', timeout=10) as response:
                popup = Popup(title='HTTP Exitoso',
                             content=Label(text=f'Status: {response.status}\nConexión HTTP OK'),
                             size_hint=(0.8, 0.4))
                popup.open()
        except Exception as e:
            popup = Popup(title='HTTP Error',
                         content=Label(text=f'Error HTTP:\n{str(e)}'),
                         size_hint=(0.8, 0.4))
            popup.open()

    def test_socket(self, instance):
        # Simple socket test
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('8.8.8.8', 53))
            sock.close()

            if result == 0:
                popup = Popup(title='Socket OK',
                             content=Label(text='Conexión de red OK'),
                             size_hint=(0.8, 0.4))
            else:
                popup = Popup(title='Socket Error',
                             content=Label(text='Problema de conexión'),
                             size_hint=(0.8, 0.4))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error',
                         content=Label(text=f'Error de socket:\n{str(e)}'),
                         size_hint=(0.8, 0.4))
            popup.open()

class CanvasDemo(BoxLayout):
    """Demo widget for canvas operations"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shapes = []

        with self.canvas:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.bg = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def add_rectangle(self, *args):
        with self.canvas:
            Color(1, 0, 0, 0.7)  # Red
            import random
            x = random.randint(0, int(self.width - 50))
            y = random.randint(0, int(self.height - 50))
            rect = Rectangle(pos=(self.x + x, self.y + y), size=(50, 50))
            self.shapes.append(('rect', rect))

    def add_circle(self, *args):
        with self.canvas:
            Color(0, 1, 0, 0.7)  # Green
            import random
            x = random.randint(25, int(self.width - 25))
            y = random.randint(25, int(self.height - 25))
            circle = Ellipse(pos=(self.x + x - 25, self.y + y - 25), size=(50, 50))
            self.shapes.append(('circle', circle))

    def clear_canvas(self, *args):
        # Remove all shapes
        for shape_type, shape in self.shapes:
            self.canvas.remove(shape)
        self.shapes.clear()

class ProtonoxKivyDebug(App):
    """Main app class for Protonox Kivy Debug"""

    def build(self):
        Logger.info("🚀 Iniciando Protonox Kivy Debug App")

        # Main layout with tabs
        root = TabbedPanel(do_default_tab=False)

        # Tab 1: System Info
        info_tab = TabbedPanelItem(text='📊 Info Sistema')
        info_tab.add_widget(DebugInfo())
        root.add_widget(info_tab)

        # Tab 2: Widget Tester
        widget_tab = TabbedPanelItem(text='🧪 Widgets')
        widget_tab.add_widget(WidgetTester())
        root.add_widget(widget_tab)

        # Tab 3: Performance & Advanced
        perf_tab = TabbedPanelItem(text='⚡ Performance')
        perf_tab.add_widget(PerformanceTester())
        root.add_widget(perf_tab)

        # Set default tab
        root.default_tab = info_tab

        Logger.info("✅ Protonox Kivy Debug App inicializada correctamente")
        return root

    def on_start(self):
        Logger.info("🎯 Protonox Kivy Debug App iniciada - Lista para debugging!")

    def on_stop(self):
        Logger.info("👋 Protonox Kivy Debug App cerrada")

if __name__ == '__main__':
    ProtonoxKivyDebug().run()