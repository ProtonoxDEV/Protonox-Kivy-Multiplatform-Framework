"""Development-time runtime inspector helpers.

These utilities stay out of production flows and lean on the layout_engine to
provide serializable snapshots that Protonox Studio or other tooling can read
without mutating the widget tree.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from kivy.uix.widget import Widget

from ..layout_engine.introspect import export_tree


def inspect_widget_tree(widget: Widget) -> Dict[str, object]:
    """Return a dict representation of the widget tree (telemetry gated)."""

    return export_tree(widget)


def persist_inspection(widget: Widget, path: Path) -> Optional[Path]:
    """Persist a widget tree snapshot to disk if telemetry is enabled."""

    payload = inspect_widget_tree(widget)
    if not payload or payload.get("enabled") is False:
        return None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
    except Exception:
        return None
