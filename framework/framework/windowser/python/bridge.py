# framework/windowser/python/bridge.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

try:
    from kivy.utils import platform as _kivy_platform
except Exception:  # si no está Kivy
    _kivy_platform = None


def _get_platform() -> str:
    if _kivy_platform is None:
        return "unknown"
    return _kivy_platform


@dataclass
class WindowserBridge:
    """
    Punto de entrada de alto nivel a la capa nativa Protonox.

    Uso típico:

        from windowser import WindowserBridge

        w = WindowserBridge()
        if w.is_android:
            w.ensure_permissions(["android.permission.INTERNET"])

        app_dir = w.get_app_storage_dir()
    """

    platform: str = _get_platform()

    @property
    def is_android(self) -> bool:
        return self.platform == "android"

    @property
    def is_desktop(self) -> bool:
        return self.platform in {"win", "linux", "macosx"}

    # --- Permisos ---------------------------------------------------------

    def has_permission(self, permission: str) -> bool:
        from . import permissions
        return permissions.has_permission(permission)

    def ensure_permissions(self, permissions_list: List[str]) -> bool:
        from . import permissions
        return permissions.ensure_permissions(permissions_list)

    # --- Storage ----------------------------------------------------------

    def get_app_storage_dir(self) -> str:
        from . import storage
        return storage.get_app_storage_dir()

    def get_external_storage_dir(self) -> Optional[str]:
        from . import storage
        return storage.get_external_storage_dir()

    # --- Servicios --------------------------------------------------------

    def start_background_service(self, name: str, extras: Optional[Dict[str, Any]] = None) -> bool:
        from . import services
        return services.start_service(name, extras or {})

    def stop_background_service(self, name: str) -> bool:
        from . import services
        return services.stop_service(name)

    # --- Notificaciones (stub, primera versión) --------------------------

    def notify(self, title: str, message: str, **kwargs: Any) -> None:
        from . import notifications
        notifications.notify(title, message, **kwargs)
