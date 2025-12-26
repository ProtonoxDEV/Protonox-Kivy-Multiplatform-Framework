"""Simple TCP socket listener to trigger reloads without filesystem watch."""

from __future__ import annotations

import socket
import threading
from pathlib import Path
from typing import Callable, Optional


class SocketReloadBridge:
    def __init__(self, endpoint: str, callback: Callable[[Path | None], None], manifest_path: Optional[Path] = None):
        self.endpoint = endpoint
        self.callback = callback
        self.manifest_path = manifest_path
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def _loop(self):
        host, port = self._parse()
        while not self._stop.is_set():
            try:
                with socket.create_connection((host, port), timeout=5) as sock:
                    sock.settimeout(1)
                    while not self._stop.is_set():
                        data = sock.recv(1024)
                        if not data:
                            break
                        # Any message triggers a refresh
                        self.callback(self.manifest_path)
                if not self._stop.is_set():
                    self._stop.wait(1)
            except Exception:
                if not self._stop.is_set():
                    self._stop.wait(2)

    def _parse(self):
        if ":" in self.endpoint:
            host, port = self.endpoint.rsplit(":", 1)
            return host, int(port)
        return self.endpoint, 8765

    def start(self):
        if self._thread:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
