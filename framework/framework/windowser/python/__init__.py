# framework/windowser/python/__init__.py

"""
windowser – Capa nativa multiplataforma Protonox.

Expone una API de alto nivel para manejar:
- permisos
- rutas de almacenamiento
- servicios
- (futuro) notificaciones

Funciona en:
- Android (usando Pyjnius)
- Desktop (fallbacks seguros, sin romper nada)
"""

from .bridge import WindowserBridge
from . import permissions, storage, services, notifications

__all__ = [
    "WindowserBridge",
    "permissions",
    "storage",
    "services",
    "notifications",
]
