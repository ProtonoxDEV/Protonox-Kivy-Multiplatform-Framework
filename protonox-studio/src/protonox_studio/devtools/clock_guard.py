"""Development-only duplicate scheduling guard for Kivy Clock."""

from __future__ import annotations

from typing import Callable, Dict, Tuple

from kivy.clock import Clock
from kivy.logger import Logger


class ClockGuard:
    """Warns when the same callback is scheduled repeatedly in dev mode."""

    def __init__(self) -> None:
        self._seen: Dict[Tuple[Callable, float], int] = {}
        self._installed = False
        self._orig_schedule_once = Clock.schedule_once
        self._orig_schedule_interval = Clock.schedule_interval

    def _wrap(self, original: Callable, interval: float | None):
        def wrapper(callback: Callable, timeout: float = 0, *args, **kwargs):
            key = (callback, interval if interval is not None else timeout)
            count = self._seen.get(key, 0) + 1
            self._seen[key] = count
            if count > 1:
                name = getattr(callback, "__name__", repr(callback))
                Logger.warning(f"[CLOCK] Duplicate scheduling detected for {name} ({timeout}s)")
            return original(callback, timeout, *args, **kwargs)

        return wrapper

    def install(self) -> None:
        if self._installed:
            return
        Clock.schedule_once = self._wrap(self._orig_schedule_once, None)  # type: ignore[method-assign]
        Clock.schedule_interval = self._wrap(self._orig_schedule_interval, -1)  # type: ignore[method-assign]
        self._installed = True

    def uninstall(self) -> None:
        if not self._installed:
            return
        Clock.schedule_once = self._orig_schedule_once  # type: ignore[method-assign]
        Clock.schedule_interval = self._orig_schedule_interval  # type: ignore[method-assign]
        self._seen.clear()
        self._installed = False


__all__ = ["ClockGuard"]
