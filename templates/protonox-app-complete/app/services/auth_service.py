from typing import Any, Dict, Optional

from .firebase_service import FirebaseService


class AuthService:
    """Facade for Firebase authentication flows."""

    def __init__(self, firebase: FirebaseService):
        self.firebase = firebase

    def register(self, email: str, password: str) -> Dict[str, Any]:
        return self.firebase.register(email, password)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        return self.firebase.login(email, password)

    def logout(self) -> None:
        self.firebase.logout()

    def current_token(self) -> Optional[str]:
        return self.firebase.id_token if self.firebase.validate_token() else None
