"""Data-only overlay helpers to support interactive inspectors (dev-only)."""

from __future__ import annotations

from typing import Dict

from kivy.uix.widget import Widget

from ..telemetry import PROTONOX_TELEMETRY, widget_bounds


def _node_payload(widget: Widget) -> Dict[str, object]:
    bounds = widget_bounds(widget)
    return {
        "id": getattr(widget, "id", widget.__class__.__name__),
        "cls": widget.__class__.__name__,
        "bounds": bounds,
        "children": [_node_payload(child) for child in reversed(widget.children)],
    }


def overlay_payload(widget: Widget) -> Dict[str, object]:
    """Return a serializable payload for overlay inspectors without mutating UI."""

    if not PROTONOX_TELEMETRY:
        return {"enabled": False, "reason": "telemetry-disabled"}
    return {"enabled": True, "tree": _node_payload(widget)}


def suggest_kv_patch(widget: Widget, **updates) -> Dict[str, object]:
    """Produce a KV-style patch suggestion for a widget without applying it."""

    widget_id = getattr(widget, "id", None) or widget.__class__.__name__
    patch = {"id": widget_id, "class": widget.__class__.__name__, "updates": updates}
    return patch


__all__ = ["overlay_payload", "suggest_kv_patch"]
