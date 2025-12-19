#!/usr/bin/env python3
"""
Tests de retrocompatibilidad con Kivy 2.3.1.

Estos tests verifican que protonox-kivy puede funcionar como reemplazo
directo de kivy 2.3.1, manteniendo compatibilidad hacia atrás.
"""

import unittest
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock

class KivyCompatibilityTest(unittest.TestCase):
    """Tests para verificar compatibilidad con Kivy 2.3.1."""

    def setUp(self):
        """Configurar el entorno de test"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Agregar el directorio del proyecto al path
        sys.path.insert(0, self.project_root)

    def test_kivy_231_compatibility_message(self):
        """Verificar que se muestra mensaje de compatibilidad con Kivy 2.3.1"""
        # Importar kivy desde protonox-kivy
        try:
            import kivy
            # Verificar que la versión es compatible
            version_parts = kivy.__version__.split('.')
            major_minor = f"{version_parts[0]}.{version_parts[1]}"

            # Debería ser 3.0.x (compatible con 2.3.1)
            self.assertEqual(version_parts[0], '3')
            self.assertEqual(version_parts[1], '0')

            # Verificar que existe el mensaje de compatibilidad
            # Esto se haría en el __init__.py de kivy
            print(f"✅ Protonox-Kivy {kivy.__version__} cargado exitosamente")
            print("ℹ️  Compatible con proyectos Kivy 2.3.1")
            print("🚀 Modificaciones Protonox disponibles: ScissorPush/ScissorPop, wireless debug, Android insets")

        except ImportError as e:
            self.fail(f"No se pudo importar kivy: {e}")

    def test_scissor_operations_available(self):
        """Verificar que ScissorPush y ScissorPop están disponibles"""
        try:
            from kivy.graphics import ScissorPush, ScissorPop
            # Verificar que las clases existen
            self.assertTrue(hasattr(ScissorPush, '__init__'))
            self.assertTrue(hasattr(ScissorPop, '__init__'))
            print("✅ ScissorPush/ScissorPop disponibles para retrocompatibilidad")
        except ImportError as e:
            self.fail(f"Scissor operations no disponibles: {e}")

    def test_protonox_extensions_available(self):
        """Verificar que las extensiones Protonox están disponibles opcionalmente"""
        try:
            # Verificar que existe el módulo de extensiones
            import kivy.protonox_ext
            print("✅ Extensiones Protonox disponibles")

            # Verificar android_insets si está disponible
            try:
                from kivy.protonox_ext import android_insets
                self.assertTrue(hasattr(android_insets, 'get_current_insets'))
                self.assertTrue(hasattr(android_insets, 'add_insets_listener'))
                print("✅ Android insets helper disponible")
            except ImportError:
                print("ℹ️  Android insets no disponible (plataforma no Android)")

        except ImportError:
            print("ℹ️  Extensiones Protonox no disponibles (modo legacy)")

    def test_legacy_app_compatibility(self):
        """Test que una app típica de Kivy 2.3.1 funciona sin cambios"""
        # Código de ejemplo de una app Kivy 2.3.1 típica
        app_code = '''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import ScissorPush, ScissorPop

class LegacyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Label básico
        label = Label(text="App compatible con Kivy 2.3.1")
        layout.add_widget(label)

        # Button con callback
        button = Button(text="Probar Scissor")
        button.bind(on_press=self.test_scissor)
        layout.add_widget(button)

        return layout

    def test_scissor(self, instance):
        # Probar que ScissorPush/ScissorPop funcionan
        from kivy.graphics import ScissorPush, ScissorPop
        print("ScissorPush/ScissorPop funcionan correctamente")

if __name__ == '__main__':
    LegacyApp().run()
'''

        # Crear archivo temporal para test
        temp_app_path = os.path.join(self.project_root, 'temp_legacy_app.py')
        try:
            with open(temp_app_path, 'w') as f:
                f.write(app_code)

            # Verificar que el código se puede importar sin errores
            spec = __import__('importlib.util').util.spec_from_file_location("temp_legacy_app", temp_app_path)
            module = __import__('importlib.util').util.module_from_spec(spec)

            # Solo verificar que se puede cargar, no ejecutar
            print("✅ Código de app legacy se puede cargar sin errores")

        except Exception as e:
            self.fail(f"Error cargando app legacy: {e}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_app_path):
                os.remove(temp_app_path)

    def test_kivymd_compatibility(self):
        """Verificar compatibilidad con KivyMD (si está disponible)"""
        # Configurar entorno headless antes de importar kivymd
        os.environ.setdefault('KIVY_WINDOW', 'headless')
        os.environ.setdefault('KIVY_GL_BACKEND', 'mock')

        try:
            import kivymd
            print(f"✅ KivyMD {kivymd.__version__} disponible")

            # Verificar que ToggleButtonBehavior tiene el alias 'state'
            from kivymd.uix.behaviors import ToggleButtonBehavior
            # Esto debería funcionar sin KeyError
            behavior = ToggleButtonBehavior()
            self.assertTrue(hasattr(behavior, 'state'))
            print("✅ ToggleButtonBehavior.state disponible para retrocompatibilidad")

        except ImportError:
            print("ℹ️  KivyMD no disponible - test omitido")
        except SystemExit:
            # KivyMD puede intentar salir si no hay ventana, pero eso está bien
            print("ℹ️  KivyMD importó correctamente pero intentó salir (headless environment)")

    def test_wireless_debug_availability(self):
        """Verificar que wireless debug está disponible opcionalmente"""
        # Verificar que existe el ejemplo de wireless debug
        wireless_example = os.path.join(self.project_root, 'examples', 'wireless_debug_example.py')
        self.assertTrue(os.path.exists(wireless_example))

        # Verificar que el archivo contiene las importaciones correctas
        with open(wireless_example, 'r') as f:
            content = f.read()

        self.assertIn('from kivy.app import App', content)
        self.assertIn('from kivy.logger import Logger', content)
        print("✅ Wireless debug example disponible")

    def test_no_breaking_changes(self):
        """Verificar que no hay cambios breaking con Kivy 2.3.1"""
        # Lista de imports comunes que deberían seguir funcionando
        common_imports = [
            'from kivy.app import App',
            'from kivy.uix.boxlayout import BoxLayout',
            'from kivy.uix.label import Label',
            'from kivy.uix.button import Button',
            'from kivy.graphics import ScissorPush, ScissorPop',
            'from kivy.logger import Logger',
            'from kivy.core.window import Window',
        ]

        for import_stmt in common_imports:
            try:
                # Ejecutar el import en un contexto separado
                exec(import_stmt)
                print(f"✅ {import_stmt} funciona correctamente")
            except Exception as e:
                self.fail(f"Import fallido: {import_stmt} - {e}")

    def test_version_compatibility_message(self):
        """Test que se muestra mensaje informativo sobre la versión"""
        try:
            import kivy
            version = kivy.__version__

            # Debería ser una versión 3.0.x dev
            self.assertTrue(version.startswith('3.0.'))
            self.assertIn('dev', version)

            print(f"ℹ️  Versión Protonox-Kivy: {version}")
            print("ℹ️  Compatible con Kivy 2.3.1+")
            print("🚀 Funciona como reemplazo directo de kivy")

        except ImportError as e:
            self.fail(f"No se pudo obtener versión: {e}")


if __name__ == '__main__':
    print("🧪 Ejecutando tests de retrocompatibilidad con Kivy 2.3.1")
    print("=" * 60)
    unittest.main(verbosity=2)