# framework/windowser/python/services.py

"""
Capa base para servicios en segundo plano.

Primera versión:
- En desktop -> no hace nada, solo loguea.
- En Android -> deja el esqueleto para hablar con ProtonoxService (Java).
"""

from __future__ import annotations

from typing import Dict, Any

import logging

try:
    from kivy.utils import platform as _kivy_platform
except Exception:
    _kivy_platform = None

IS_ANDROID = _kivy_platform == "android"

logger = logging.getLogger("protonox.windowser.services")

if IS_ANDROID:
    try:
        from jnius import autoclass, cast  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
    except Exception:
        IS_ANDROID = False


def start_service(name: str, extras: Dict[str, Any]) -> bool:
    if not IS_ANDROID:
        logger.info(f"[windowser] start_service('{name}') (desktop, no-op)")
        return False

    try:
        activity = PythonActivity.mActivity
        context = cast("android.content.Context", activity.getApplicationContext())

        service_class = autoclass("com.protonox.framework.ProtonoxService")
        intent = Intent(context, service_class)

        intent.putExtra("service_name", name)
        for k, v in extras.items():
            intent.putExtra(str(k), str(v))

        context.startService(intent)
        logger.info(f"[windowser] Android service '{name}' started.")
        return True
    except Exception as e:
        logger.exception(f"[windowser] Error starting service '{name}': {e}")
        return False


def stop_service(name: str) -> bool:
    if not IS_ANDROID:
        logger.info(f"[windowser] stop_service('{name}') (desktop, no-op)")
        return False

    try:
        activity = PythonActivity.mActivity
        context = cast("android.content.Context", activity.getApplicationContext())

        service_class = autoclass("com.protonox.framework.ProtonoxService")
        intent = Intent(context, service_class)
        intent.putExtra("service_name", name)

        context.stopService(intent)
        logger.info(f"[windowser] Android service '{name}' stopped.")
        return True
    except Exception as e:
        logger.exception(f"[windowser] Error stopping service '{name}': {e}")
        return False
