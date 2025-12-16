"""Layout fingerprinting and symmetry heuristics (opt-in).

This module keeps the core Kivy runtime untouched while exposing metrics that
let Protonox Studio detect visual regressions without relying on screenshots.
All exports are gated by environment flags and designed to be safe for
production when disabled.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from kivy.uix.widget import Widget

from .introspect import snapshot_tree
from ..telemetry import PROTONOX_TELEMETRY, widget_bounds

VISUAL_WARNINGS = os.environ.get("PROTONOX_VISUAL_WARNINGS", "0") == "1"


@dataclass
class Fingerprint:
    hash: str
    nodes: int

    def to_dict(self) -> Dict[str, object]:
        return {"hash": self.hash, "nodes": self.nodes}


@dataclass
class SymmetryScore:
    widget_id: str
    cls: str
    score: float
    delta_x: float
    delta_y: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.widget_id,
            "class": self.cls,
            "score": round(self.score, 2),
            "delta_x": round(self.delta_x, 2),
            "delta_y": round(self.delta_y, 2),
        }


def _serialize(node: Widget) -> Dict[str, object]:
    bounds = widget_bounds(node)
    return {
        "id": getattr(node, "id", None) or node.__class__.__name__,
        "cls": node.__class__.__name__,
        "bounds": {
            "x": round(bounds["x"], 2),
            "y": round(bounds["y"], 2),
            "w": round(bounds["width"], 2),
            "h": round(bounds["height"], 2),
        },
        "size_hint": getattr(node, "size_hint", None),
        "children": [_serialize(child) for child in node.children],
    }


def compute_fingerprint(widget: Widget) -> Optional[Fingerprint]:
    if not PROTONOX_TELEMETRY:
        return None
    tree = _serialize(widget)
    digest = hashlib.sha256(json.dumps(tree, sort_keys=True).encode("utf-8")).hexdigest()
    return Fingerprint(hash=digest, nodes=_count_nodes(widget))


def _count_nodes(widget: Widget) -> int:
    count = 1
    for child in widget.children:
        count += _count_nodes(child)
    return count


def _symmetry_for_widget(widget: Widget) -> SymmetryScore:
    parent = widget.parent
    if parent is None:
        return SymmetryScore(
            widget_id=getattr(widget, "id", None) or widget.__class__.__name__,
            cls=widget.__class__.__name__,
            score=100.0,
            delta_x=0.0,
            delta_y=0.0,
        )

    pb = widget_bounds(parent)
    wb = widget_bounds(widget)
    delta_x = abs((wb["x"] - pb["x"]) - (pb["width"] - (wb["x"] - pb["x"]) - wb["width"]))
    delta_y = abs((wb["y"] - pb["y"]) - (pb["height"] - (wb["y"] - pb["y"]) - wb["height"]))
    score = max(0.0, 100.0 - (delta_x + delta_y))
    return SymmetryScore(
        widget_id=getattr(widget, "id", None) or widget.__class__.__name__,
        cls=widget.__class__.__name__,
        score=score,
        delta_x=delta_x,
        delta_y=delta_y,
    )


def symmetry_report(widget: Widget) -> List[SymmetryScore]:
    if not VISUAL_WARNINGS or not PROTONOX_TELEMETRY:
        return []

    scores: List[SymmetryScore] = []

    def _walk(node: Widget):
        scores.append(_symmetry_for_widget(node))
        for child in node.children:
            _walk(child)

    _walk(widget)
    return scores


def export_snapshot(widget: Widget) -> Dict[str, object]:
    """Export layout snapshot with fingerprint and optional symmetry scores."""

    if not PROTONOX_TELEMETRY:
        return {"enabled": False, "reason": "telemetry disabled"}

    fingerprint = compute_fingerprint(widget)
    data = {
        "fingerprint": fingerprint.to_dict() if fingerprint else None,
        "tree": snapshot_tree(widget).to_dict(),
    }
    sym = symmetry_report(widget)
    if sym:
        data["symmetry"] = [s.to_dict() for s in sym]
    return data


__all__ = [
    "Fingerprint",
    "SymmetryScore",
    "compute_fingerprint",
    "symmetry_report",
    "export_snapshot",
]
