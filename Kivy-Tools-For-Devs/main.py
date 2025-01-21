import os
import subprocess
import platform
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock


class MonitorApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Title label
        self.title_label = Label(
            text="Kivy Tools Monitor",
            font_size='28sp',
            bold=True,
            color=(0, 0.5, 1, 1),
            size_hint=(1, 0.15),
            halign="center",
            valign="middle"
        )
        self.add_widget(self.title_label)

        # Button to generate environment report
        self.env_report_button = Button(
            text="Generate Environment Report",
            font_size='20sp',
            size_hint=(1, 0.15),
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1)
        )
        self.env_report_button.bind(on_press=self.generate_env_report)
        self.add_widget(self.env_report_button)

        # Button to generate KV component ID reports
        self.id_report_button = Button(
            text="Generate ID Component Report",
            font_size='20sp',
            size_hint=(1, 0.15),
            background_color=(0, 0.5, 1, 1),
            color=(1, 1, 1, 1)
        )
        self.id_report_button.bind(on_press=self.generate_id_report)
        self.add_widget(self.id_report_button)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.1)
        )
        self.add_widget(self.progress_bar)

        # Status label
        self.status_label = Label(
            text="Status: Ready",
            font_size='18sp',
            size_hint=(1, 0.1),
            halign="center",
            valign="middle",
            color=(0, 0.5, 0, 1)
        )
        self.add_widget(self.status_label)

    def generate_env_report(self, instance):
        """Generates the environment report."""
        self.run_script('kivy_env_info.py', "Environment Report")

    def generate_id_report(self, instance):
        """Generates the KV component ID report in two steps."""
        self.status_label.text = "Status: Running analyze_kv.py..."
        self.status_label.color = (1, 0.5, 0, 1)
        Clock.schedule_once(lambda dt: self.run_script('analyze_kv.py', "Analyze KV Files", next_step=True), 0.1)

    def run_script(self, script_name, report_name, next_step=False):
        """Executes the specified script and handles the result."""
        self.progress_bar.value = 0
        script_path = os.path.join(os.path.dirname(__file__), script_name)

        try:
            subprocess.run(["python3", script_path], check=True)
            if next_step:
                self.status_label.text = "Status: Running generate_kv_id_report.py..."
                self.status_label.color = (1, 0.5, 0, 1)
                Clock.schedule_once(lambda dt: self.run_script('generate_kv_id_report.py', "Generate KV ID Report"), 0.1)
            else:
                self.status_label.text = f"Status: {report_name} generated successfully."
                self.status_label.color = (0, 0.5, 0, 1)
        except subprocess.CalledProcessError as e:
            self.status_label.text = f"Status: Error during {report_name} - {str(e)}"
            self.status_label.color = (1, 0, 0, 1)
        except Exception as e:
            self.status_label.text = f"Status: Unexpected error - {str(e)}"
            self.status_label.color = (1, 0, 0, 1)
        finally:
            self.progress_bar.value = 100

    def update_progress(self, dt):
        if self.progress_bar.value < 100:
            self.progress_bar.value += 5


class KivyToolsApp(App):
    def build(self):
        return MonitorApp()


if __name__ == "__main__":
    KivyToolsApp().run()
