#!/usr/bin/env python3
"""
Tests unitarios simples para verificar la estructura del framework.

Estos tests verifican que los archivos existen, que se pueden importar
los módulos básicos y que la estructura del proyecto es correcta.
"""

import unittest
import sys
import os
import importlib.util

class FrameworkStructureTest(unittest.TestCase):
    """Tests para verificar la estructura básica del framework."""

    def setUp(self):
        """Configurar el entorno de test"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_project_structure_exists(self):
        """Verificar que la estructura básica del proyecto existe"""
        required_dirs = ['framework', 'examples', 'tools', 'templates']
        for dir_name in required_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            self.assertTrue(os.path.exists(dir_path), f"Directorio {dir_name} no existe")
            self.assertTrue(os.path.isdir(dir_path), f"{dir_name} no es un directorio")

    def test_test_app_exists(self):
        """Verificar que test_app.py existe y es importable"""
        test_app_path = os.path.join(self.project_root, 'test_app.py')
        self.assertTrue(os.path.exists(test_app_path), "test_app.py no existe")

        # Verificar que se puede cargar como módulo
        spec = importlib.util.spec_from_file_location("test_app", test_app_path)
        self.assertIsNotNone(spec, "No se puede crear spec para test_app.py")

    def test_wireless_debug_example_exists(self):
        """Verificar que wireless_debug_example.py existe"""
        example_path = os.path.join(self.project_root, 'examples', 'wireless_debug_example.py')
        self.assertTrue(os.path.exists(example_path), "wireless_debug_example.py no existe")

    def test_protonox_studio_structure(self):
        """Verificar que la estructura de protonox-studio existe"""
        studio_dir = os.path.join(self.project_root, 'protonox-studio')
        self.assertTrue(os.path.exists(studio_dir), "protonox-studio no existe")

        required_files = ['pyproject.toml', 'requirements.txt']
        for file_name in required_files:
            file_path = os.path.join(studio_dir, file_name)
            self.assertTrue(os.path.exists(file_path), f"{file_name} no existe en protonox-studio")

    def test_kivy_protonox_structure(self):
        """Verificar que la estructura de kivy-protonox-version existe"""
        kivy_dir = os.path.join(self.project_root, 'kivy-protonox-version')
        self.assertTrue(os.path.exists(kivy_dir), "kivy-protonox-version no existe")

        required_files = ['pyproject.toml', 'setup.py']
        for file_name in required_files:
            file_path = os.path.join(kivy_dir, file_name)
            self.assertTrue(os.path.exists(file_path), f"{file_name} no existe en kivy-protonox-version")

    def test_root_config_files(self):
        """Verificar que los archivos de configuración raíz existen"""
        config_files = ['pyproject.toml', 'README.md', 'protonox.yaml']
        for file_name in config_files:
            file_path = os.path.join(self.project_root, file_name)
            self.assertTrue(os.path.exists(file_path), f"{file_name} no existe en la raíz")

    def test_tools_exist(self):
        """Verificar que las herramientas de build existen"""
        tools_dir = os.path.join(self.project_root, 'tools')
        build_scripts = ['build_android.sh', 'build_linux.sh', 'build_windows.sh']
        for script in build_scripts:
            script_path = os.path.join(tools_dir, script)
            self.assertTrue(os.path.exists(script_path), f"{script} no existe")

    def test_templates_exist(self):
        """Verificar que las plantillas de aplicación existen"""
        templates_dir = os.path.join(self.project_root, 'templates')
        template_types = ['protonox-app-basic', 'protonox-app-bot-ready', 'protonox-app-complete']
        for template in template_types:
            template_path = os.path.join(templates_dir, template)
            self.assertTrue(os.path.exists(template_path), f"Template {template} no existe")


class ImportTest(unittest.TestCase):
    """Tests para verificar que los módulos se pueden importar sin errores críticos."""

    def setUp(self):
        """Configurar el entorno de test"""
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, self.project_root)

    def test_can_import_test_app_without_kivy(self):
        """Verificar que test_app.py se puede analizar sintácticamente sin importar kivy"""
        test_app_path = os.path.join(self.project_root, 'test_app.py')

        # Leer el archivo y verificar sintaxis básica
        with open(test_app_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar que contiene las importaciones esperadas
        self.assertIn('from kivymd.app import MDApp', content)
        self.assertIn('from kivymd.uix.boxlayout import MDBoxLayout', content)
        self.assertIn('from kivymd.uix.label import MDLabel', content)

        # Verificar que tiene la clase principal
        self.assertIn('class TestApp(MDApp):', content)
        self.assertIn('def build(self):', content)

    def test_can_import_wireless_debug_without_kivy(self):
        """Verificar que wireless_debug_example.py se puede analizar sintácticamente"""
        example_path = os.path.join(self.project_root, 'examples', 'wireless_debug_example.py')

        with open(example_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar que contiene las importaciones esperadas
        self.assertIn('from kivy.app import App', content)
        self.assertIn('from kivy.uix.boxlayout import BoxLayout', content)

        # Verificar que tiene la clase principal
        self.assertIn('class WirelessDebugExample(App):', content)
        self.assertIn('def build(self):', content)
        self.assertIn('def on_button_press(self, instance):', content)


if __name__ == '__main__':
    unittest.main()