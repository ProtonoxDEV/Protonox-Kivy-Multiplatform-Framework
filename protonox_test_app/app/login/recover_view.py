from kivy.uix.screenmanager import Screen


class RecoverView(Screen):
    name = "recover"

    def on_recover(self, email: str) -> str:
        if "@" not in email:
            return "Correo inválido"
        # Placeholder recovery flow
        return "Se envió enlace de recuperación"
