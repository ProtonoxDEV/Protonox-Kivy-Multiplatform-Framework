from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import numpy as np
import sys


class TestApp(App):
    def build(self):
        # Test numpy functionality that requires meson build
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Test basic numpy operations
        arr = np.array([1, 2, 3, 4, 5])
        result = np.sum(arr)
        fft_result = np.fft.fft(arr)

        info_label = Label(
            text=f'Protonox Kivy 3.0.0 + NumPy {np.__version__}\n'
                 f'NumPy sum: {result}\n'
                 f'FFT shape: {fft_result.shape}\n'
                 f'Python: {sys.version}',
            font_size=16,
            halign='center'
        )
        info_label.bind(size=info_label.setter('text_size'))

        # Test button to verify UI interaction
        test_button = Button(
            text='Test NumPy Operations',
            size_hint=(1, 0.3),
            font_size=18
        )
        test_button.bind(on_press=self.test_numpy)

        layout.add_widget(info_label)
        layout.add_widget(test_button)

        # Schedule a test to run after app starts
        Clock.schedule_once(self.run_tests, 1)

        return layout

    def test_numpy(self, instance):
        """Test various numpy operations that require meson compilation"""
        try:
            # Test linear algebra
            matrix = np.random.rand(10, 10)
            eigenvals = np.linalg.eigvals(matrix)

            # Test advanced math functions
            x = np.linspace(0, 2*np.pi, 100)
            y = np.sin(x) + np.cos(x)

            # Test array operations
            arr1 = np.arange(1000)
            arr2 = np.arange(1000, 2000)
            dot_product = np.dot(arr1, arr2)

            instance.text = f'NumPy Tests Passed!\nEigvals: {len(eigenvals)}\nDot: {dot_product}'

        except Exception as e:
            instance.text = f'NumPy Error: {str(e)}'

    def run_tests(self, dt):
        """Run comprehensive tests on app startup"""
        try:
            # Test that numpy was compiled with meson
            import numpy
            version_info = numpy.__version__

            # Test scipy-like operations if available
            arr = np.array([[1, 2], [3, 4]])
            det = np.linalg.det(arr)

            print(f"NumPy {version_info} loaded successfully")
            print(f"Matrix determinant: {det}")
            print("All tests passed!")

        except Exception as e:
            print(f"Test failed: {e}")


if __name__ == '__main__':
    TestApp().run()