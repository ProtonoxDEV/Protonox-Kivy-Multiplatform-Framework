import re
from typing import Tuple


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_credentials(email: str, password: str) -> Tuple[bool, str]:
    if not EMAIL_REGEX.match(email):
        return False, "Correo inválido"
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    return True, ""
