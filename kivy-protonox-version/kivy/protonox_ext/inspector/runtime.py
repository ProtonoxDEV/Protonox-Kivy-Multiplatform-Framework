"""Development-time runtime inspector helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from kivy.uix.widget import Widget

from ..layout_engine.antipatterns import detect_antipatterns
from ..layout_engine.fingerprint import compute_fingerprint, symmetry_report
from ..layout_engine.introspect import export_tree
from ..visual_state.snapshot import capture_with_layout_report


def inspect_widget_tree(widget: Widget) -> Dict[str, object]:
    """Return a dict representation of the widget tree (telemetry gated)."""

    return export_tree(widget)


def layout_health(widget: Widget) -> Dict[str, object]:
    """Return fingerprint, symmetry, and anti-pattern heuristics."""

    fingerprint = compute_fingerprint(widget)
    symmetry = symmetry_report(widget)
    anti = detect_antipatterns(widget)
    payload: Dict[str, object] = {}
    if fingerprint:
        payload["fingerprint"] = fingerprint.to_dict()
    if symmetry:
        payload["symmetry"] = [s.to_dict() for s in symmetry]
    if anti:
        payload["antipatterns"] = [a.to_dict() for a in anti]
    if not payload:
        payload["enabled"] = False
    return payload


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


def persist_health(widget: Widget, path: Path) -> Optional[Path]:
    """Persist layout health diagnostics (fingerprint/symmetry/anti-patterns)."""

    payload = layout_health(widget)
    if not payload or payload.get("enabled") is False:
        return None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
    except Exception:
        return None


def snapshot_dual(widget: Widget, stem: Path):
    """Capture PNG + JSON snapshot with fingerprint for later comparison."""

    return capture_with_layout_report(widget, stem)


__all__ = ["inspect_widget_tree", "layout_health", "persist_inspection", "persist_health", "snapshot_dual"]
