from __future__ import annotations

from typing import Optional

from kivy.logger import Logger


class DesktopVideoBackend:
    """Stub desktop backend (ffpyplayer/libVLC placeholder)."""

    def __init__(self, widget) -> None:
        self.widget = widget
        self.player: Optional[object] = None

    def load(self):
        Logger.info("protonox.video: Desktop backend stub loaded")

    def play(self):
        Logger.info("protonox.video: play() (desktop stub)")

    def pause(self):
        Logger.info("protonox.video: pause() (desktop stub)")

    def stop(self):
        Logger.info("protonox.video: stop() (desktop stub)")

    def seek(self, seconds: float):
        Logger.info(f"protonox.video: seek({seconds}) (desktop stub)")

    def dispose(self):
        Logger.info("protonox.video: dispose() (desktop stub)")
        self.player = None
