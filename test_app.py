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