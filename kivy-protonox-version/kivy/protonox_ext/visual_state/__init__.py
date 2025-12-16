"""Visual-state helpers (opt-in) for Protonox Kivy fork."""

from .freeze import freeze_ui
from .png_reference import compare_pngs, VisualWarning
from .snapshot import SnapshotResult, capture, capture_with_layout_report

__all__ = [
    "freeze_ui",
    "compare_pngs",
    "VisualWarning",
    "SnapshotResult",
    "capture",
    "capture_with_layout_report",
]
