#!/usr/bin/env python3
"""
Test script for Protonox Kivy window providers
"""
import os
import sys

import kivy
from kivy.config import Config

# Configure basic settings BEFORE importing window
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

# Set headless mode AFTER basic config
os.environ['KIVY_WINDOW'] = 'headless'

try:
    import kivy.core.window
    print("✓ Kivy core window imported successfully")

    # Check available providers
    providers = [attr for attr in dir(kivy.core.window) if not attr.startswith('_') and 'window_' in attr]
    print(f"Available window providers: {providers}")

    # Test window_x11 import
    try:
        from kivy.core.window.window_x11 import WindowX11
        print("✓ window_x11 provider available")
    except ImportError as e:
        print(f"✗ window_x11 provider not available: {e}")

    # Test window creation
    from kivy.core.window import Window
    print(f"✓ Window created successfully: {Window}")

    print("\n🎉 SUCCESS: Protonox Kivy window providers are working!")

except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)