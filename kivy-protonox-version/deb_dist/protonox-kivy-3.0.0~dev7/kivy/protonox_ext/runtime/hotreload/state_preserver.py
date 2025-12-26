"""Capture and inject state for widgets/screens that declare `state_keys`."""

from __future__ import annotations

from typing import Dict, Iterable

from kivy.uix.widget import Widget


class StatePreserver:
    def capture(self, widget: Widget) -> Dict[str, object]:
        keys = getattr(widget, "state_keys", None) or []
        inferred = [
            key
            for key in ("text", "scroll_y", "scroll_x", "cursor", "focus", "selection_text")
            if hasattr(widget, key)
        ]
        if isinstance(keys, Iterable):
            keys = list(keys) + inferred
        else:
            keys = inferred
        state: Dict[str, object] = {}
        for key in keys:
            if hasattr(widget, key):
                try:
                    state[key] = getattr(widget, key)
                except Exception:
                    continue
        return state

    def inject(self, widget: Widget, state: Dict[str, object]) -> None:
        for key, value in (state or {}).items():
            if hasattr(widget, key):
                try:
                    setattr(widget, key, value)
                except Exception:
                    continue
