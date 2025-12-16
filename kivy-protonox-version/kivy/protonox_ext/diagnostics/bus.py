"""Unified diagnostic bus for Protonox fork (opt-in).

This module captures stdout/stderr writes, Python warnings, and log records
without altering Kivy behaviour. It is entirely gated by the
``PROTONOX_DIAGNOSTIC_BUS`` environment flag and designed to be safe in
production: when disabled it is a no-op.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import threading
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

BUS_ENABLED = os.environ.get("PROTONOX_DIAGNOSTIC_BUS", "0").lower() in {"1", "true", "yes"}


@dataclass
class DiagnosticEvent:
    channel: str
    message: str
    level: str = "info"
    meta: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        data = {"channel": self.channel, "message": self.message, "level": self.level}
        if self.meta:
            data["meta"] = self.meta
        return data


class _StreamProxy:
    def __init__(self, stream, emit: Callable[[DiagnosticEvent], None], channel: str):
        self._stream = stream
        self._emit = emit
        self._channel = channel

    def write(self, data):  # pragma: no cover - passthrough
        if data:
            self._emit(DiagnosticEvent(channel=self._channel, message=str(data)))
        return self._stream.write(data)

    def flush(self):  # pragma: no cover - passthrough
        return self._stream.flush()


class _LogHandler(logging.Handler):
    def __init__(self, emit: Callable[[DiagnosticEvent], None]):
        super().__init__()
        self._emit = emit

    def emit(self, record):  # pragma: no cover - logging
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self._emit(
            DiagnosticEvent(
                channel="log", message=msg, level=record.levelname.lower(), meta={"logger": record.name}
            )
        )


class DiagnosticBus:
    """Capture diagnostic events in-memory and as snapshots."""

    def __init__(self, enabled: bool = False, max_events: int = 1000):
        self.enabled = enabled
        self.max_events = max_events
        self.events: List[DiagnosticEvent] = []
        self._lock = threading.Lock()
        self._stdout = None
        self._stderr = None
        self._warnings = None
        self._log_handler: Optional[_LogHandler] = None

    def start(self) -> None:
        if not self.enabled:
            return
        if self._stdout:
            return
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = _StreamProxy(sys.stdout, self._record, "stdout")
        sys.stderr = _StreamProxy(sys.stderr, self._record, "stderr")
        self._warnings = warnings.showwarning
        warnings.showwarning = self._capture_warning  # type: ignore
        self._log_handler = _LogHandler(self._record)
        logging.getLogger().addHandler(self._log_handler)

    def stop(self) -> None:
        if self._stdout:
            sys.stdout = self._stdout
            self._stdout = None
        if self._stderr:
            sys.stderr = self._stderr
            self._stderr = None
        if self._warnings:
            warnings.showwarning = self._warnings  # type: ignore
            self._warnings = None
        if self._log_handler:
            logging.getLogger().removeHandler(self._log_handler)
            self._log_handler = None

    def _record(self, event: DiagnosticEvent) -> None:
        if not self.enabled:
            return
        with self._lock:
            self.events.append(event)
            if len(self.events) > self.max_events:
                self.events.pop(0)

    def _capture_warning(self, message, category, filename, lineno, file=None, line=None):  # pragma: no cover - passthrough
        text = warnings.formatwarning(message, category, filename, lineno, line)
        self._record(DiagnosticEvent(channel="warning", message=text, level="warning"))
        if self._warnings:
            return self._warnings(message, category, filename, lineno, file, line)
        return None

    def snapshot(self) -> Dict[str, object]:
        return {"enabled": self.enabled, "events": [e.to_dict() for e in self.events]}

    def dump(self, path: Path) -> Optional[Path]:
        if not self.enabled:
            return None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.snapshot(), indent=2), encoding="utf-8")
            return path
        except Exception:
            return None


_GLOBAL_BUS: Optional[DiagnosticBus] = None


def get_bus() -> DiagnosticBus:
    global _GLOBAL_BUS
    if _GLOBAL_BUS is None:
        _GLOBAL_BUS = DiagnosticBus(enabled=BUS_ENABLED)
        _GLOBAL_BUS.start()
    return _GLOBAL_BUS


__all__ = ["DiagnosticBus", "DiagnosticEvent", "get_bus", "BUS_ENABLED"]
