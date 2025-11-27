# framework/windowser/python/storage.py

"""
Funciones de rutas de almacenamiento:
- app_storage_dir: directorio interno seguro
- external_storage_dir: tarjeta SD / externo (Android)
"""

from __future__ import annotations

import os
from typing import Optional

try:
    from kivy.utils import platform as _kivy_platform
except Exception:
    _kivy_platform = None

IS_ANDROID = _kivy_platform == "android"

if IS_ANDROID:
    try:
        from jnius import autoclass, cast  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Environment = autoclass("android.os.Environment")
        Context = autoclass("android.content.Context")
    except Exception:
        IS_ANDROID = False


def get_app_storage_dir() -> str:
    """
    Devuelve un directorio adecuado para almacenar datos de la app.
    - Android: /data/user/0/<package>/files
    - Desktop: ~/.protonox_app  (por ahora genérico)
    """
    if IS_ANDROID:
        activity = PythonActivity.mActivity
        context = cast("android.content.Context", activity.getApplicationContext())
        files_dir = context.getFilesDir().getAbsolutePath()
        path = os.path.join(files_dir, "protonox")
    else:
        home = os.path.expanduser("~")
        path = os.path.join(home, ".protonox_app")

    os.makedirs(path, exist_ok=True)
    return path


def get_external_storage_dir() -> Optional[str]:
    """
    Devuelve el directorio de almacenamiento externo (Android) o None en desktop.
    """
    if not IS_ANDROID:
        return None

    state = Environment.getExternalStorageState()
    if state != Environment.MEDIA_MOUNTED:
        return None

    ext_dir = Environment.getExternalStorageDirectory().getAbsolutePath()
    path = os.path.join(ext_dir, "Protonox")
    os.makedirs(path, exist_ok=True)
    return path
