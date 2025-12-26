from kivy.lang import Builder
from kivymd.app import MDApp
import os
import sys
# make sure local example package is importable so we can load kivymd_compat
sys.path.insert(0, os.path.dirname(__file__))
import kivymd_compat as compat

KV = """
MDScreen:

    # Simple header text instead of toolbar to maximize compatibility
    MDLabel:
        text: "KivyMD + protonox-kivy"
        halign: "center"
        pos_hint: {"center_y": 0.9}

    MDLabel:
        text: "Hola desde KivyMD 1.1.1+"
        halign: "center"
        pos_hint: {"center_y": 0.6}

    MDRaisedButton:
        text: "Accion rapida"
        pos_hint: {"center_x": 0.5, "center_y": 0.35}
        on_release: app.on_button_press()
    
    MDTextField:
        id: input_field
        hint_text: "Ingrese texto"
        size_hint_x: 0.8
        pos_hint: {"center_x": 0.5, "center_y": 0.2}
    
    MDRaisedButton:
        text: "Agregar"
        pos_hint: {"center_x": 0.85, "center_y": 0.2}
        on_release: app.submit_text()
    
    ScrollView:
        size_hint: 1, 0.25
        pos_hint: {"center_x": 0.5, "center_y": 0.05}
        MDList:
            id: entries_list
"""


class KivyMDDemoApp(MDApp):
    def build(self):
        self.title = "KivyMD Demo"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Teal"
        self.button_pressed_count = 0
        # Flag used by test runner to trigger automated actions from on_start
        self._ci_actions = False
        # ensure common widgets registered for KV compatibility across versions
        compat.ensure([
            'MDLabel', 'MDRaisedButton', 'MDTextField', 'MDList',
            'OneLineListItem', 'MDFillRoundFlatIconButton', 'MDToolbar'
        ])
        return Builder.load_string(KV)

    def on_button_press(self):
        # Simple console feedback to keep the example dependency-light
        self.button_pressed_count += 1
        print(f"MD button pressed; count={self.button_pressed_count}")

    def press_button(self):
        # helper to trigger the same action programmatically
        self.on_button_press()

    def on_start(self):
        # If the test runner enabled CI actions, schedule an automated press and stop
        if getattr(self, "_ci_actions", False):
            # keep for compatibility, but scheduling in run() is more reliable
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.press_button(), 0.5)
            Clock.schedule_once(lambda dt: self.take_screenshot("kivymd_demo_screenshot.png"), 1.0)
            Clock.schedule_once(lambda dt: self.stop(), 1.5)

    def run(self):
        # If CI automation requested, schedule actions before entering the main loop.
        if getattr(self, "_ci_actions", False):
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.press_button(), 0.5)
            Clock.schedule_once(lambda dt: self.take_screenshot("kivymd_demo_screenshot.png"), 1.0)
            Clock.schedule_once(lambda dt: self.stop(), 1.5)
        return super().run()

    def take_screenshot(self, filename: str):
        try:
            import os
            from kivy.core.window import Window
            # ensure screenshots are saved next to this example
            if not os.path.isabs(filename):
                base = os.path.dirname(__file__)
                filename = os.path.join(base, filename)
            Window.screenshot(name=filename)
            print(f"Screenshot saved: {filename}")
        except Exception as e:
            print(f"Screenshot failed: {e}")
    
    # Text-entry helpers for CI
    def type_text(self, text: str):
        try:
            self.root.ids.input_field.text = text
            print(f"Typed text: {text}")
        except Exception as e:
            print(f"type_text failed: {e}")

    def submit_text(self):
        try:
            txt = self.root.ids.input_field.text or ""
            from kivymd.uix.list import OneLineListItem
            self.root.ids.entries_list.add_widget(OneLineListItem(text=txt))
            self.root.ids.input_field.text = ""
            print(f"Submitted text: {txt}")
        except Exception as e:
            print(f"submit_text failed: {e}")

    def get_entries(self):
        try:
            items = [c.text for c in reversed(self.root.ids.entries_list.children)]
            return items
        except Exception as e:
            print(f"get_entries failed: {e}")
            return []

    def clear_entries(self):
        try:
            self.root.ids.entries_list.clear_widgets()
            print("Cleared entries")
        except Exception as e:
            print(f"clear_entries failed: {e}")

    def run_ci_plan(self, plan):
        # plan: list of tuples (action, arg, delay)
        from kivy.clock import Clock
        for action, arg, delay in plan:
            if action == 'press_button':
                Clock.schedule_once(lambda dt: self.press_button(), delay)
            elif action == 'type':
                Clock.schedule_once(lambda dt, t=arg: self.type_text(t), delay)
            elif action == 'submit':
                Clock.schedule_once(lambda dt: self.submit_text(), delay)
            elif action == 'screenshot':
                Clock.schedule_once(lambda dt, f=arg: self.take_screenshot(f), delay)
            elif action == 'stop':
                Clock.schedule_once(lambda dt: self.stop(), delay)


def main():
    KivyMDDemoApp().run()


if __name__ == "__main__":
    main()
