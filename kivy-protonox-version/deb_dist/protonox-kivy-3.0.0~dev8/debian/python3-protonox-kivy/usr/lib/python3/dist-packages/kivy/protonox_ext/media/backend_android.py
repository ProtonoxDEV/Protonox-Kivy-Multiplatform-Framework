from __future__ import annotations

from typing import Optional

from kivy.logger import Logger


class AndroidVideoBackend:
    """Stub ExoPlayer-style backend; to be implemented with Pyjnius.

    This keeps API compatibility while real decoding is added later.
    """

    def __init__(self, widget) -> None:
        self.widget = widget
        self.surface: Optional[object] = None

    def load(self):
        Logger.info("protonox.video: Android backend stub loaded")

    def play(self):
        Logger.info("protonox.video: play() (android stub)")

    def pause(self):
        Logger.info("protonox.video: pause() (android stub)")

    def stop(self):
        Logger.info("protonox.video: stop() (android stub)")

    def seek(self, seconds: float):
        Logger.info(f"protonox.video: seek({seconds}) (android stub)")

    def dispose(self):
        Logger.info("protonox.video: dispose() (android stub)")
        self.surface = None
