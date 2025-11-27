from kivy.uix.screenmanager import Screen


class HomeView(Screen):
    name = "home"

    def on_enter(self, *args):  # noqa: ANN001
        return super().on_enter(*args)
