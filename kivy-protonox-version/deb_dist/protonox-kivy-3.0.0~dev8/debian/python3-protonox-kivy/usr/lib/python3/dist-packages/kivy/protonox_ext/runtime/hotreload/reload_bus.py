"""Central event bus for reload-related signals."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, DefaultDict, List


class ReloadBus:
    def __init__(self):
        self._subscribers: DefaultDict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._subscribers[event].append(callback)

    def emit(self, event: str, **payload) -> None:
        for cb in list(self._subscribers.get(event, [])):
            try:
                cb(**payload)
            except Exception:
                continue


_GLOBAL_BUS: ReloadBus | None = None


def get_reload_bus() -> ReloadBus:
    global _GLOBAL_BUS
    if _GLOBAL_BUS is None:
        _GLOBAL_BUS = ReloadBus()
    return _GLOBAL_BUS
