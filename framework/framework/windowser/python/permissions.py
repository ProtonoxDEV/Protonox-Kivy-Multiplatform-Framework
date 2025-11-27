# framework/windowser/python/permissions.py

"""
Manejo de permisos en Android y fallback seguro en desktop.

En desktop -> siempre devuelve True sin romper nada.
En Android -> usa Pyjnius para consultar y solicitar permisos.
"""

from __future__ import annotations
from typing import List

try:
    from kivy.utils import platform as _kivy_platform
except Exception:
    _kivy_platform = None

IS_ANDROID = _kivy_platform == "android"

if IS_ANDROID:
    try:
        from jnius import autoclass, cast  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        ActivityCompat = autoclass("androidx.core.app.ActivityCompat")
        PackageManager = autoclass("android.content.pm.PackageManager")
    except Exception:  # si algo falla, degradamos
        IS_ANDROID = False


def has_permission(permission: str) -> bool:
    if not IS_ANDROID:
        # En desktop no validamos permisos del SO
        return True

    activity = PythonActivity.mActivity
    context = cast("android.content.Context", activity.getApplicationContext())
    granted = ActivityCompat.checkSelfPermission(context, permission)
    return granted == PackageManager.PERMISSION_GRANTED


def request_permissions(permissions_list: List[str], request_code: int = 1001) -> None:
    if not IS_ANDROID:
        return

    # En Kivy, normalmente PythonActivity maneja onRequestPermissionsResult.
    # Aquí solo lanzamos la petición.
    activity = PythonActivity.mActivity
    perms = [str(p) for p in permissions_list]
    ActivityCompat.requestPermissions(activity, perms, request_code)


def ensure_permissions(permissions_list: List[str]) -> bool:
    """
    Devuelve True si todos los permisos están concedidos,
    False si falta alguno (y lanza petición en Android).
    """
    missing = [p for p in permissions_list if not has_permission(p)]
    if not missing:
        return True

    request_permissions(missing)
    # No podemos saber inmediatamente si se aceptaron, eso va por callback.
    # Devolvemos False para indicar que todavía no están listos.
    return False
