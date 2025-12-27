#!/usr/bin/env python3
"""
Minimal Protonox-Kivy Application Template

This is a basic template for creating Protonox-Kivy applications.
It includes the essential structure and configurations for Android deployment.

Features:
- Protonox-Kivy framework integration
- KivyMD material design components
- Optimized for Android 16+ with ARM64 architecture
- Hot reload support (when using protonox-studio)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout


class MainScreen(MDBoxLayout):
    """Main application screen with Protonox-Kivy components."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20

        # Welcome label
        self.welcome_label = MDLabel(
            text="Welcome to Protonox-Kivy!",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        )
        self.add_widget(self.welcome_label)

        # Counter label
        self.counter_label = MDLabel(
            text="Counter: 0",
            halign="center",
            theme_text_color="Secondary",
            font_style="H6"
        )
        self.add_widget(self.counter_label)

        # Counter button
        self.counter_button = MDRaisedButton(
            text="Increment Counter",
            pos_hint={"center_x": 0.5},
            on_release=self.increment_counter
        )
        self.add_widget(self.counter_button)

        # Info label
        self.info_label = MDLabel(
            text="Built with Protonox-Kivy v3.0.0\nOptimized for Android 16+",
            halign="center",
            theme_text_color="Hint",
            font_style="Body2"
        )
        self.add_widget(self.info_label)

    def increment_counter(self, instance):
        """Increment the counter when button is pressed."""
        current_count = int(self.counter_label.text.split(": ")[1])
        self.counter_label.text = f"Counter: {current_count + 1}"


class ProtonoxApp(MDApp):
    """Main Protonox-Kivy application class."""

    def build(self):
        """Build the application UI."""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        return MainScreen()

    def on_start(self):
        """Called when the application starts."""
        print("Protonox-Kivy app started successfully!")
        print(f"Running on platform: {self.platform}")

    def on_pause(self):
        """Called when the application is paused (Android/iOS)."""
        return True

    def on_resume(self):
        """Called when the application resumes (Android/iOS)."""
        pass


if __name__ == '__main__':
    ProtonoxApp().run()