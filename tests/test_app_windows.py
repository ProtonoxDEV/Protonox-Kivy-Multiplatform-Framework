#!/usr/bin/env python3
"""
Tests unitarios para las ventanas de las aplicaciones de prueba.

Estos tests verifican que las ventanas se crean correctamente,
que los elementos de UI están presentes y que las interacciones básicas funcionan.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Configurar Kivy para modo headless ANTES de importar cualquier módulo de Kivy
os.environ['KIVY_HEADLESS'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_WINDOW'] = 'headless'
os.environ['KIVY_GL_BACKEND'] = 'mock'
os.environ['DISPLAY'] = ''

# No mock kivy, usar el real en headless
# Agregar el directorio raíz al path para importar las apps de prueba
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ahora importar las apps
try:
    from test_app import TestApp
    from examples.wireless_debug_example import WirelessDebugExample
    APPS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    APPS_AVAILABLE = False


class TestAppWindowTest(unittest.TestCase):
    """Tests para la ventana de TestApp (KivyMD)"""

    def setUp(self):
        """Configurar el entorno de test"""
        if not APPS_AVAILABLE:
            self.skipTest("Las aplicaciones de prueba no están disponibles")

        self.app = TestApp()

    def tearDown(self):
        """Limpiar después de cada test"""
        if hasattr(self.app, 'root'):
            self.app.root = None

    @patch('kivy.core.window.Window')
    def test_build_creates_layout(self, mock_window):
        """Verificar que build() crea un layout válido"""
        layout = self.app.build()

        # Verificar que se retorna un layout
        self.assertIsNotNone(layout)

        # Verificar que es un MDBoxLayout
        self.assertEqual(layout.__class__.__name__, 'MDBoxLayout')

        # Verificar que tiene orientación vertical
        self.assertEqual(layout.orientation, 'vertical')

        # Verificar que tiene al menos un widget hijo
        self.assertGreater(len(layout.children), 0)

    @patch('kivy.core.window.Window')
    def test_layout_contains_label(self, mock_window):
        """Verificar que el layout contiene una etiqueta con el texto correcto"""
        layout = self.app.build()

        # Buscar el label en los children
        labels = [child for child in layout.children if hasattr(child, 'text')]
        self.assertEqual(len(labels), 1)

        label = labels[0]
        self.assertIn('Hello from Protonox', label.text)
        self.assertIn('KivyMD', label.text)
        self.assertIn('ScissorPush/ScissorPop', label.text)
        self.assertIn('wireless debug', label.text)

    @patch('kivy.core.window.Window')
    def test_label_is_mdlabel(self, mock_window):
        """Verificar que la etiqueta es de tipo MDLabel"""
        layout = self.app.build()

        labels = [child for child in layout.children if hasattr(child, 'text')]
        self.assertEqual(len(labels), 1)

        label = labels[0]
        # Verificar que es MDLabel (de KivyMD)
        self.assertEqual(label.__class__.__name__, 'MDLabel')


class WirelessDebugExampleWindowTest(unittest.TestCase):
    """Tests para la ventana de WirelessDebugExample"""

    def setUp(self):
        """Configurar el entorno de test"""
        if not APPS_AVAILABLE:
            self.skipTest("Las aplicaciones de prueba no están disponibles")

        self.app = WirelessDebugExample()

    def tearDown(self):
        """Limpiar después de cada test"""
        if hasattr(self.app, 'root'):
            self.app.root = None

    @patch('kivy.core.window.Window')
    def test_build_creates_layout(self, mock_window):
        """Verificar que build() crea un layout válido"""
        layout = self.app.build()

        # Verificar que se retorna un layout
        self.assertIsNotNone(layout)

        # Verificar que es un BoxLayout
        self.assertEqual(layout.__class__.__name__, 'BoxLayout')

        # Verificar que tiene orientación vertical
        self.assertEqual(layout.orientation, 'vertical')

        # Verificar que tiene widgets hijos
        self.assertGreater(len(layout.children), 0)

    @patch('kivy.core.window.Window')
    def test_layout_contains_label_and_button(self, mock_window):
        """Verificar que el layout contiene etiqueta y botón"""
        layout = self.app.build()

        # Debería tener 2 widgets: Label y Button
        self.assertEqual(len(layout.children), 2)

        # Encontrar label y button
        labels = [child for child in layout.children if isinstance(child, type(layout.children[0]).__bases__[0].__bases__[0]) and hasattr(child, 'text')]
        buttons = [child for child in layout.children if hasattr(child, 'bind') and hasattr(child, 'text')]

        # Verificar que hay una etiqueta
        self.assertGreaterEqual(len(labels), 1)
        label = labels[0]
        self.assertIn('Wireless Debug Example', label.text)

        # Verificar que hay un botón
        self.assertGreaterEqual(len(buttons), 1)
        button = buttons[0]
        self.assertEqual(button.text, 'Click me!')

    @patch('kivy.core.window.Window')
    @patch('kivy.logger.Logger')
    def test_button_press_changes_text(self, mock_logger, mock_window):
        """Verificar que presionar el botón cambia su texto"""
        layout = self.app.build()

        # Encontrar el botón
        buttons = [child for child in layout.children if hasattr(child, 'bind') and hasattr(child, 'text')]
        self.assertGreaterEqual(len(buttons), 1)

        button = buttons[0]
        original_text = button.text

        # Simular presionar el botón
        self.app.on_button_press(button)

        # Verificar que el texto cambió
        self.assertNotEqual(button.text, original_text)
        self.assertEqual(button.text, 'Clicked!')

    @patch('kivy.core.window.Window')
    @patch('kivy.logger.Logger')
    def test_button_press_logs_message(self, mock_logger, mock_window):
        """Verificar que presionar el botón registra un mensaje de log"""
        layout = self.app.build()

        # Encontrar el botón
        buttons = [child for child in layout.children if hasattr(child, 'bind') and hasattr(child, 'text')]
        button = buttons[0]

        # Simular presionar el botón
        self.app.on_button_press(button)

        # Verificar que se llamó a Logger.info
        mock_logger.info.assert_called_with("Button pressed!")


class WindowIntegrationTest(unittest.TestCase):
    """Tests de integración para verificar que las ventanas funcionan juntas"""

    def setUp(self):
        """Configurar el entorno de test"""
        if not APPS_AVAILABLE:
            self.skipTest("Las aplicaciones de prueba no están disponibles")

    @patch('kivy.core.window.Window')
    def test_both_apps_can_be_imported_and_instantiated(self, mock_window):
        """Verificar que ambas apps pueden ser importadas e instanciadas"""
        # TestApp
        test_app = TestApp()
        self.assertIsNotNone(test_app)
        self.assertIsNotNone(test_app.build())

        # WirelessDebugExample
        wireless_app = WirelessDebugExample()
        self.assertIsNotNone(wireless_app)
        self.assertIsNotNone(wireless_app.build())

    @patch('kivy.core.window.Window')
    def test_apps_have_different_layouts(self, mock_window):
        """Verificar que las apps tienen layouts diferentes"""
        test_app = TestApp()
        wireless_app = WirelessDebugExample()

        test_layout = test_app.build()
        wireless_layout = wireless_app.build()

        # Verificar que son de tipos diferentes
        self.assertNotEqual(test_layout.__class__.__name__, wireless_layout.__class__.__name__)

        # TestApp usa MDBoxLayout, WirelessDebugExample usa BoxLayout
        self.assertEqual(test_layout.__class__.__name__, 'MDBoxLayout')
        self.assertEqual(wireless_layout.__class__.__name__, 'BoxLayout')


if __name__ == '__main__':
    # Configurar unittest para mostrar más detalles
    unittest.main(verbosity=2)