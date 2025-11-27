from kivy.uix.screenmanager import Screen

from ..services.auth_service import AuthService
from ..services.firebase_service import FirebaseService
from .validators import validate_credentials


class RegisterView(Screen):
    name = "register"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth = AuthService(FirebaseService())

    def on_register(self, email: str, password: str) -> str:
        valid, msg = validate_credentials(email, password)
        if not valid:
            return msg
        try:
            self.auth.register(email, password)
            return "Registro exitoso"
        except Exception as exc:  # noqa: BLE001
            return f"Error: {exc}"
