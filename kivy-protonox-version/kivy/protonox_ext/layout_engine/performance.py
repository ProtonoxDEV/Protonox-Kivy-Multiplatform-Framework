"""Layout cost profiling helpers (opt-in, dev-only).

These helpers avoid touching the core Kivy scheduling loop. They are meant for
developers who need to understand *where* layout time is spent without
rewriting widgets. Everything is gated behind `PROTONOX_LAYOUT_PROFILER` and
`PROTONOX_LAYOUT_TELEMETRY` so production builds stay untouched.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from kivy.logger import Logger
from kivy.uix.widget import Widget

from ..telemetry import PROTONOX_TELEMETRY, widget_bounds
from ..visual_state.freeze import freeze_ui


DEV_PROFILE = os.environ.get("PROTONOX_LAYOUT_PROFILER", "0").lower() in {
    "1",
    "true",
    "yes",
}


@dataclass
class LayoutCost:
    """Per-widget layout timing and invalidation hints."""

    widget_id: str
    cls: str
    layout_ms: float
    children: int
    severity: str
    bounds: Dict[str, float]

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.widget_id,
            "class": self.cls,
            "layout_ms": round(self.layout_ms, 3),
            "children": self.children,
            "severity": self.severity,
            "bounds": self.bounds,
        }


def _severity(layout_ms: float) -> str:
    if layout_ms < 1.5:
        return "low"
    if layout_ms < 4.0:
        return "medium"
    return "high"


def _profile_widget(widget: Widget) -> Optional[LayoutCost]:
    # Respect opt-in flags aggressively.
    if not (DEV_PROFILE and PROTONOX_TELEMETRY):
        return None

    do_layout = getattr(widget, "do_layout", None)
    if not callable(do_layout):
        return None

    start = time.perf_counter()
    try:
        do_layout()
    except Exception as exc:  # pragma: no cover - dev-only guardrail
        Logger.warning("[PROTONOX][PROFILE] do_layout failed for %s: %s", widget, exc)
        return None
    layout_ms = (time.perf_counter() - start) * 1000.0

    cost = LayoutCost(
        widget_id=getattr(widget, "id", None) or widget.__class__.__name__,
        cls=widget.__class__.__name__,
        layout_ms=layout_ms,
        children=len(widget.children),
        severity=_severity(layout_ms),
        bounds=widget_bounds(widget),
    )
    return cost


def profile_tree(widget: Widget) -> List[LayoutCost]:
    """Return layout costs for the widget and its subtree.

    The profiler temporarily freezes scheduling (when enabled) to reduce noise
    from concurrent animations. If profiling is disabled, this returns an empty
    list to keep runtime impact at zero.
    """

    if not (DEV_PROFILE and PROTONOX_TELEMETRY):
        return []

    costs: List[LayoutCost] = []

    def _walk(node: Widget):
        cost = _profile_widget(node)
        if cost:
            costs.append(cost)
        for child in node.children:
            _walk(child)

    with freeze_ui(widget):
        _walk(widget)
    return costs


def overlay_cost_payload(widget: Widget) -> Dict[str, object]:
    """Return a serializable payload suitable for overlay visualisation."""

    if not (DEV_PROFILE and PROTONOX_TELEMETRY):
        return {"enabled": False, "reason": "layout-profiler-disabled"}
    costs = [c.to_dict() for c in profile_tree(widget)]
    return {
        "enabled": True,
        "costs": costs,
        "summary": {
            "widgets": len(costs),
            "high": len([c for c in costs if c["severity"] == "high"]),
            "medium": len([c for c in costs if c["severity"] == "medium"]),
        },
    }


__all__ = ["LayoutCost", "profile_tree", "overlay_cost_payload"]
