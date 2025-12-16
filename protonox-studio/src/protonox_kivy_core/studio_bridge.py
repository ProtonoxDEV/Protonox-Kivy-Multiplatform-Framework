"""Bridge between Kivy runtime and Protonox Studio.

Minimal stub: establishes shape for WS/HTTP integration without enforcing
transport yet. Future iterations will connect to /__protonox/ws and handle
asset/export/reload events.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)


class StudioBridge:
    """Bridge stub; wire real transport in future iterations."""

    def __init__(self, on_reload: Optional[Callable[[dict], None]] = None, on_event: Optional[Callable[[dict], None]] = None):
        self.on_reload = on_reload
        self.on_event = on_event
        self.connected = False

    def connect(self, url: str) -> None:
        log.info("[bridge] connect stub to %s", url)
        self.connected = True

    def close(self) -> None:
        self.connected = False

    def send_reload_request(self, payload: dict[str, Any]) -> None:
        log.info("[bridge] send reload request stub: %s", payload)

    def handle_event(self, event: dict[str, Any]) -> None:
        if self.on_event:
            self.on_event(event)

    def handle_reload(self, payload: dict[str, Any]) -> None:
        if self.on_reload:
            self.on_reload(payload)
