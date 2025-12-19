"""UI freeze helpers (dev-only) to stabilise layouts for inspection."""
from __future__ import annotations

import contextlib
import os
from typing import Callable, List

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.widget import Widget

DEV_FREEZE = os.environ.get("PROTONOX_UI_FREEZE", "0").lower() in {"1", "true", "yes"}


@contextlib.contextmanager
def freeze_ui(root: Widget):
    """Temporarily block new Clock scheduling and stop animations for snapshots.

    This is intentionally conservative and only activates when
    PROTONOX_UI_FREEZE is enabled. It avoids touching core Kivy behaviour when
    disabled and restores original schedule functions on exit.
    """

    if not DEV_FREEZE:
        yield
        return

    original_once: Callable = Clock.schedule_once
    original_interval: Callable = Clock.schedule_interval
    blocked_calls: List[str] = []

    def _blocked(*args, **kwargs):  # pragma: no cover - defensive dev-only path
        blocked_calls.append(f"blocked {args} {kwargs}")
        return None

    try:
        _stop_animations(root)
        Clock.tick()
        Clock.schedule_once = _blocked  # type: ignore[assignment]
        Clock.schedule_interval = _blocked  # type: ignore[assignment]
        yield
    finally:
        Clock.schedule_once = original_once  # type: ignore[assignment]
        Clock.schedule_interval = original_interval  # type: ignore[assignment]
        Clock.tick()


def _stop_animations(widget: Widget):
    Animation.cancel_all(widget)
    for child in widget.children:
        _stop_animations(child)


__all__ = ["freeze_ui"]
