"""Runtime telemetry helpers for Protonox Kivy 2.3.1 builds.

These helpers are intentionally additive and gated by environment flags. They
expose widget geometry and layout metrics to Protonox Studio without changing
Kivy's public API or lifecycle.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from kivy.uix.widget import Widget

PROTONOX_TELEMETRY = os.environ.get("PROTONOX_LAYOUT_TELEMETRY", "0") == "1"


@dataclass
class LayoutMetric:
    widget_id: str
    cls: str
    bbox: Dict[str, float]
    center: Dict[str, float]
    overflow: bool
    parent: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.widget_id,
            "class": self.cls,
            "bbox": self.bbox,
            "center": self.center,
            "overflow": self.overflow,
            "parent": self.parent,
        }


def widget_bounds(widget: Widget) -> Dict[str, float]:
    x, y = widget.to_window(widget.x, widget.y, initial=False)
    return {
        "x": float(x),
        "y": float(y),
        "width": float(widget.width),
        "height": float(widget.height),
    }


def _overflow(widget: Widget) -> bool:
    parent = widget.parent
    if parent is None:
        return False
    return widget.right > parent.right or widget.top > parent.top or widget.x < parent.x or widget.y < parent.y


def export_widget_tree(widget: Widget) -> Dict[str, object]:
    def _build(node: Widget) -> Dict[str, object]:
        data = {
            "id": getattr(node, "id", None) or node.__class__.__name__,
            "class": node.__class__.__name__,
            "children": [_build(child) for child in node.children],
        }
        if PROTONOX_TELEMETRY:
            data["bounds"] = widget_bounds(node)
        return data

    return _build(widget)


def collect_layout_report(widget: Widget) -> List[LayoutMetric]:
    report: List[LayoutMetric] = []
    if not PROTONOX_TELEMETRY:
        return report

    def _walk(node: Widget, parent_id: Optional[str]) -> None:
        bounds = widget_bounds(node)
        metric = LayoutMetric(
            widget_id=getattr(node, "id", None) or node.__class__.__name__,
            cls=node.__class__.__name__,
            bbox=bounds,
            center={"x": bounds["x"] + bounds["width"] / 2, "y": bounds["y"] + bounds["height"] / 2},
            overflow=_overflow(node),
            parent=parent_id,
        )
        report.append(metric)
        for child in node.children:
            _walk(child, metric.widget_id)

    _walk(widget, None)
    return report


def safe_export_to_png(widget: Widget, target: Path) -> Optional[Path]:
    """Best-effort PNG export that avoids crashing production apps.

    Uses Widget.export_to_png when available; otherwise, it no-ops. This keeps
    the feature opt-in and aligned with Protonox Studio's non-invasive stance.
    """

    if not hasattr(widget, "export_to_png"):
        return None
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        widget.export_to_png(str(target))
        return target.resolve()
    except Exception:
        return None


def persist_layout_report(widget: Widget, path: Path) -> Optional[Path]:
    if not PROTONOX_TELEMETRY:
        return None
    payload = [metric.to_dict() for metric in collect_layout_report(widget)]
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
    except Exception:
        return None
