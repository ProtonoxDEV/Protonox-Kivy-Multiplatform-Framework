"""Dual snapshot helpers: PNG + JSON + fingerprint."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from kivy.uix.widget import Widget

from ..layout_engine.fingerprint import export_snapshot
from ..telemetry import persist_layout_report, safe_export_to_png
from .freeze import freeze_ui


@dataclass
class SnapshotResult:
    png: Optional[Path]
    json: Optional[Path]
    fingerprint: Optional[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "png": str(self.png) if self.png else None,
            "json": str(self.json) if self.json else None,
            "fingerprint": self.fingerprint,
        }


def capture(widget: Widget, stem: Path) -> SnapshotResult:
    """Capture a PNG + JSON snapshot while the UI is frozen for stability."""

    png_path = stem.with_suffix(".png")
    json_path = stem.with_suffix(".json")
    fingerprint = None

    with freeze_ui(widget):
        png = safe_export_to_png(widget, png_path)
        payload = export_snapshot(widget)
        if payload and payload.get("enabled", True):
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            fingerprint = payload.get("fingerprint", {}).get("hash") if isinstance(payload.get("fingerprint"), dict) else None
        else:
            json_path = None

    return SnapshotResult(png=png, json=json_path, fingerprint=fingerprint)


def capture_with_layout_report(widget: Widget, stem: Path) -> SnapshotResult:
    """Capture PNG + layout report JSON for pipeline compatibility."""

    result = capture(widget, stem)
    if result.json is None:
        return result
    persist_layout_report(widget, stem.with_suffix(".layout.json"))
    return result


__all__ = ["SnapshotResult", "capture", "capture_with_layout_report"]
