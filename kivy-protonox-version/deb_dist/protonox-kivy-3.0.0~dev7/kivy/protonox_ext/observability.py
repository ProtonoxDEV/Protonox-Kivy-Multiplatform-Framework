"""UI Observability Layer (opt-in) for the Protonox Kivy fork.

This module converts live widget trees into structured, metadata-rich payloads
so regressions can be detected with data instead of guesswork. It does not
modify widgets or layouts and is fully gated behind telemetry flags.
"""
from __future__ import annotations

import os
import platform
import sys
from typing import Dict

from kivy.core.window import Window
from kivy.uix.widget import Widget

from .layout_engine.antipatterns import detect_antipatterns
from .layout_engine.fingerprint import export_snapshot
from .layout_engine.health import compute_layout_health
from .telemetry import (PROTONOX_TELEMETRY, collect_layout_report,
                        export_widget_tree)

OBS_FLAG = os.environ.get("PROTONOX_UI_OBSERVABILITY", "0").lower() in {"1", "true", "yes"}


def _display_context() -> Dict[str, object]:
    dpi = getattr(Window, "dpi", None)
    scale = dpi / 160.0 if dpi else None
    orientation = "landscape" if Window.width >= Window.height else "portrait"
    return {
        "resolution": {"width": Window.width, "height": Window.height},
        "dpi": dpi,
        "scale": scale,
        "orientation": orientation,
        "platform": sys.platform,
        "system": platform.system(),
    }


def export_observability(widget: Widget) -> Dict[str, object]:
    """Aggregate observability payload for a widget tree.

    Returns an opt-in, serializable structure combining:
    - display metadata (resolution, DPI, platform)
    - widget tree with bounds (when telemetry is enabled)
    - layout metrics
    - anti-pattern detections
    - layout health score
    - fingerprint + symmetry snapshot
    """

    if not (OBS_FLAG or PROTONOX_TELEMETRY):
        return {"enabled": False, "reason": "observability disabled"}

    metrics = [m.to_dict() for m in collect_layout_report(widget)] if PROTONOX_TELEMETRY else []
    issues = [i.to_dict() for i in detect_antipatterns(widget)]
    health = None
    if PROTONOX_TELEMETRY:
        scored = compute_layout_health(widget)
        health = scored.to_dict() if scored else None

    snapshot = export_snapshot(widget) if PROTONOX_TELEMETRY else {"enabled": False, "reason": "telemetry disabled"}

    return {
        "enabled": True,
        "context": _display_context(),
        "tree": export_widget_tree(widget),
        "metrics": metrics,
        "anti_patterns": issues,
        "health": health,
        "snapshot": snapshot,
    }


__all__ = ["export_observability"]
