"""Layout introspection helpers for Protonox Kivy 2.3.1 builds.

These helpers stay opt-in and avoid mutating Kivy's default behaviour. They
surface geometry, alignment hints, and hierarchy metadata that Protonox Studio
can consume when reasoning about Web→Kivy conversions or layout health.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from kivy.uix.widget import Widget

from ..telemetry import PROTONOX_TELEMETRY, widget_bounds


@dataclass
class WidgetSnapshot:
    """Serializable snapshot of a widget's geometry and hierarchy.

    The fields intentionally avoid Kivy internals and keep a neutral contract so
    that other layers (e.g., UI IR or visual validators) can reason about
    centering, symmetry, and overflow without altering the widget tree.
    """

    kind: str
    identifier: str
    bounds: Dict[str, float]
    centered: bool
    alignment: str
    parent: Optional[str] = None
    children: List["WidgetSnapshot"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "type": self.kind,
            "id": self.identifier,
            "bounds": self.bounds,
            "centered": self.centered,
            "alignment": self.alignment,
            "parent": self.parent,
            "children": [child.to_dict() for child in self.children],
        }


VISUAL_WARNINGS = os.environ.get("PROTONOX_VISUAL_WARNINGS", "0") == "1"


def _alignment_hint(widget: Widget) -> str:
    parent = widget.parent
    if parent is None:
        return "root"

    px = parent.x + parent.width / 2.0
    py = parent.y + parent.height / 2.0
    wx = widget.x + widget.width / 2.0
    wy = widget.y + widget.height / 2.0

    horiz = "center" if abs(wx - px) < 1 else ("left" if wx < px else "right")
    vert = "center" if abs(wy - py) < 1 else ("bottom" if wy < py else "top")
    if horiz == vert == "center":
        return "center"
    return f"{vert}-{horiz}"


def _is_centered(widget: Widget) -> bool:
    parent = widget.parent
    if parent is None:
        return True
    px = parent.x + parent.width / 2.0
    py = parent.y + parent.height / 2.0
    wx = widget.x + widget.width / 2.0
    wy = widget.y + widget.height / 2.0
    return abs(wx - px) < 1 and abs(wy - py) < 1


def describe_widget(widget: Widget) -> WidgetSnapshot:
    bounds = widget_bounds(widget)
    return WidgetSnapshot(
        kind=widget.__class__.__name__,
        identifier=getattr(widget, "id", None) or widget.__class__.__name__,
        bounds=bounds,
        centered=_is_centered(widget),
        alignment=_alignment_hint(widget),
        parent=getattr(widget.parent, "id", None) or getattr(widget.parent, "__class__", type("", (), {})).__name__,
        children=[],
    )


def snapshot_tree(widget: Widget) -> WidgetSnapshot:
    root_snapshot = describe_widget(widget)
    for child in widget.children:
        root_snapshot.children.append(snapshot_tree(child))
    return root_snapshot


def export_tree(widget: Widget) -> Dict[str, object]:
    """Export a widget tree into a serializable dict.

    The export respects the PROTONOX_LAYOUT_TELEMETRY flag, so production apps
    remain untouched when telemetry is disabled.
    """

    if not PROTONOX_TELEMETRY:
        return {"enabled": False, "reason": "telemetry disabled"}
    return snapshot_tree(widget).to_dict()
