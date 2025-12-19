"""Simple polling watcher for export directories.

We avoid extra dependencies by polling the `.reload` sentinel and manifest hash.
"""

from __future__ import annotations

import threading
import time
from hashlib import sha256
from pathlib import Path
from typing import Callable, Optional


class ExportWatcher:
    def __init__(self, export_dir: Path, callback: Callable[[Path], None], interval: float = 1.0):
        self.export_dir = export_dir
        self.callback = callback
        self.interval = interval
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._last_hash = ""

    def _fingerprint(self) -> str:
        manifest = self.export_dir / "app_manifest.json"
        if not manifest.exists():
            return ""
        try:
            data = manifest.read_text(encoding="utf-8")
            return sha256(data.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    def _loop(self) -> None:
        while not self._stop.is_set():
            current = self._fingerprint()
            reload_file = self.export_dir / ".reload"
            reload_ts = reload_file.stat().st_mtime if reload_file.exists() else None
            if current and (current != self._last_hash or reload_ts and reload_ts > time.time() - self.interval * 2):
                self._last_hash = current
                try:
                    self.callback(self.export_dir)
                except Exception:
                    pass
            self._stop.wait(self.interval)

    def start(self) -> None:
        if self._thread:
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
