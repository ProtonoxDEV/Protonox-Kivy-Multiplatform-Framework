"""Unified device facade (desktop/Android) with safe fallbacks.

This keeps platform checks out of apps: call ``bootstrap_device(app)`` once and
use ``app.device`` for haptics/clipboard/window/notifications. Adapters are
lazy, best-effort, and no-op when unsupported.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from kivy.utils import platform


def _is_android() -> bool:
    try:
        return platform == "android"
    except Exception:
        return False


@dataclass
class HapticsAPI:
    vibrate: callable


@dataclass
class ClipboardAPI:
    copy: callable
    paste: callable


@dataclass
class WindowAPI:
    set_min_size: callable
    set_title: callable
    set_cursor: callable


@dataclass
class NotificationsAPI:
    notify: callable


@dataclass
class DeviceFacade:
    haptics: HapticsAPI
    clipboard: ClipboardAPI
    window: WindowAPI
    notifications: NotificationsAPI

    def on_mount(self):
        # Adapters can override via bound callables if needed
        pass

    def on_unmount(self):
        # For symmetry; adapters may close handles via wrapped callables
        pass


# ---------------- Desktop adapter ----------------

def _desktop_haptics():
    def vibrate(_ms: int):
        return None  # no-op on desktop
    return HapticsAPI(vibrate=vibrate)


def _desktop_clipboard():
    try:
        from kivy.core.clipboard import Clipboard
    except Exception:
        Clipboard = None

    def copy(text: str):
        if Clipboard:
            try:
                Clipboard.copy(text)
            except Exception:
                pass

    def paste() -> Optional[str]:
        if Clipboard:
            try:
                return Clipboard.paste()
            except Exception:
                return None
        return None

    return ClipboardAPI(copy=copy, paste=paste)


def _desktop_window():
    try:
        from kivy.core.window import Window
    except Exception:
        Window = None

    def set_min_size(w: int, h: int):
        if Window:
            try:
                Window.minimum_width, Window.minimum_height = w, h
            except Exception:
                pass

    def set_title(title: str):
        if Window:
            try:
                Window.title = title
            except Exception:
                pass

    def set_cursor(cursor: str):
        if Window:
            try:
                Window.set_system_cursor(cursor)
            except Exception:
                pass

    return WindowAPI(set_min_size=set_min_size, set_title=set_title, set_cursor=set_cursor)


def _desktop_notifications():
    def notify(title: str, body: str):
        print(f"[NOTIFY] {title}: {body}")
    return NotificationsAPI(notify=notify)


# ---------------- Android adapter (thin, best-effort) ----------------

def _android_haptics():
    def vibrate(ms: int):
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            vib = PythonActivity.mActivity.getSystemService(Context.VIBRATOR_SERVICE)
            if vib:
                vib.vibrate(ms)
        except Exception:
            pass
    return HapticsAPI(vibrate=vibrate)


def _android_clipboard():
    try:
        from kivy.core.clipboard import Clipboard
    except Exception:
        Clipboard = None

    def copy(text: str):
        if Clipboard:
            try:
                Clipboard.copy(text)
            except Exception:
                pass

    def paste() -> Optional[str]:
        if Clipboard:
            try:
                return Clipboard.paste()
            except Exception:
                return None
        return None

    return ClipboardAPI(copy=copy, paste=paste)


def _android_window():
    # Window operations map to Kivy Window; keep same as desktop
    return _desktop_window()


def _android_notifications():
    def notify(title: str, body: str):
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            NotificationCompat = autoclass("androidx.core.app.NotificationCompat")
            NotificationManagerCompat = autoclass("androidx.core.app.NotificationManagerCompat")
            app = PythonActivity.mActivity
            builder = NotificationCompat.Builder(app, "protonox")
            builder.setContentTitle(title)
            builder.setContentText(body)
            builder.setSmallIcon(app.getApplicationInfo().icon)
            getattr(NotificationManagerCompat, 'from')(app).notify(1, builder.build())
        except Exception:
            print(f"[NOTIFY] {title}: {body}")
    return NotificationsAPI(notify=notify)


# ---------------- Bootstrap ----------------

def bootstrap_device(_app=None) -> DeviceFacade:
    if _is_android():
        return DeviceFacade(
            haptics=_android_haptics(),
            clipboard=_android_clipboard(),
            window=_android_window(),
            notifications=_android_notifications(),
        )
    return DeviceFacade(
        haptics=_desktop_haptics(),
        clipboard=_desktop_clipboard(),
        window=_desktop_window(),
        notifications=_desktop_notifications(),
    )


__all__ = ["bootstrap_device", "DeviceFacade"]
