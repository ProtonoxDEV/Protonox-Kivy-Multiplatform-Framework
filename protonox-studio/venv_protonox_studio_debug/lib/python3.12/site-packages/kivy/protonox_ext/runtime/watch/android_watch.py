"""Android-safe watcher using polling + hashes (no watchdog)."""

from __future__ import annotations

import time
from hashlib import sha256
from pathlib import Path
from typing import Callable


class AndroidExportWatcher:
    def __init__(self, export_dir: Path, callback: Callable[[Path], None], interval: float = 2.0):
        self.export_dir = export_dir
        self.callback = callback
        self.interval = interval
        self._last_hash = ""
        self._running = False

    def _fingerprint(self) -> str:
        manifest = self.export_dir / "app_manifest.json"
        if not manifest.exists():
            return ""
        try:
            data = manifest.read_text(encoding="utf-8")
            return sha256(data.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    def run_forever(self) -> None:
        self._running = True
        while self._running:
            current = self._fingerprint()
            if current and current != self._last_hash:
                self._last_hash = current
                try:
                    self.callback(self.export_dir)
                except Exception:
                    pass
            time.sleep(self.interval)

    def stop(self) -> None:
        self._running = False
