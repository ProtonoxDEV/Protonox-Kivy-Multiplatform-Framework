from __future__ import annotations

from typing import Optional

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.utils import platform


def build_backend(widget) -> Optional[object]:
    """Return a platform-specific backend instance (stubbed)."""
    try:
        if platform == "android":
            from .backend_android import AndroidVideoBackend

            return AndroidVideoBackend(widget)
    except Exception as exc:  # noqa: BLE001 - avoid breaking UI on missing deps
        Logger.warning(f"protonox.video: android backend unavailable: {exc}")

    try:
        from .backend_desktop import DesktopVideoBackend

        return DesktopVideoBackend(widget)
    except Exception as exc:  # noqa: BLE001
        Logger.warning(f"protonox.video: desktop backend unavailable: {exc}")
    return None


class ProtonoxVideo(Widget):
    """Unified video widget (API stub)."""

    source = StringProperty("")
    poster = StringProperty("")
    autoplay = BooleanProperty(False)
    controls = BooleanProperty(True)
    loop = BooleanProperty(False)
    muted = BooleanProperty(False)
    backend = ObjectProperty(None, rebind=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda _dt: self._ensure_backend(), 0)

    def on_kv_post(self, _base_widget):
        self._ensure_backend()

    def on_parent(self, instance, value):  # noqa: ANN001 - Kivy signature
        if value is None:
            self.on_unmount()
        return super().on_parent(instance, value)

    # ------------------------------------------------------------------
    # Public controls
    # ------------------------------------------------------------------
    def play(self):
        if self.backend:
            self.backend.play()
        else:
            Logger.warning("protonox.video: play() ignored, no backend")

    def pause(self):
        if self.backend:
            self.backend.pause()

    def stop(self):
        if self.backend:
            self.backend.stop()

    def seek(self, seconds: float):
        if self.backend:
            self.backend.seek(seconds)

    # ------------------------------------------------------------------
    # Lifecycle hooks (used by HotReloadAppBase broadcast)
    # ------------------------------------------------------------------
    def on_mount(self):  # pragma: no cover - runtime hook
        if self.autoplay:
            Clock.schedule_once(lambda _dt: self.play(), 0)

    def on_unmount(self):  # pragma: no cover - runtime hook
        if self.backend:
            try:
                self.backend.dispose()
            except Exception:  # noqa: BLE001
                Logger.exception("protonox.video: dispose failed")
            self.backend = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_backend(self):
        if self.backend:
            return
        backend = build_backend(self)
        if backend is None:
            Logger.warning("protonox.video: no backend available; showing poster only. Run 'protonox doctor' to install ffpyplayer/vlc or ExoPlayer deps.")
            return
        self.backend = backend
        try:
            backend.load()
        except Exception:  # noqa: BLE001
            Logger.exception("protonox.video: backend load failed")
