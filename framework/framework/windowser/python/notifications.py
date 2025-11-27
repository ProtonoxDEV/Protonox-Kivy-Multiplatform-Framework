# framework/windowser/python/notifications.py

"""
Notificaciones locales (stub v1).

Por ahora:
- En desktop: imprime en consola.
- En Android: TODO – integrar con NotificationManager vía Java.
"""

from __future__ import annotations
import logging

try:
    from kivy.utils import platform as _kivy_platform
except Exception:
    _kivy_platform = None

IS_ANDROID = _kivy_platform == "android"

logger = logging.getLogger("protonox.windowser.notifications")


def notify(title: str, message: str, **kwargs) -> None:
    if not IS_ANDROID:
        logger.info(f"[NOTIFY][desktop] {title}: {message}")
        return

    # TODO: implementar integración con NotificationManager en Java
    logger.info(f"[NOTIFY][android:stub] {title}: {message} (not implemented yet)")
