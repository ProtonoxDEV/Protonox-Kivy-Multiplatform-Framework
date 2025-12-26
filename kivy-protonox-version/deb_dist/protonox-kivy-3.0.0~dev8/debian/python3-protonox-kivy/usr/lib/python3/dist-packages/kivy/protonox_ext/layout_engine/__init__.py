"""Layout engine extensions (opt-in) for Kivy 2.3.1 Protonox fork."""

from .antipatterns import AntiPattern, detect_antipatterns
from .fingerprint import Fingerprint, SymmetryScore, compute_fingerprint, export_snapshot, symmetry_report
from .health import LayoutHealth, compute_layout_health
from .introspect import WidgetSnapshot, describe_widget, export_tree, snapshot_tree
from .performance import LayoutCost, overlay_cost_payload, profile_tree

__all__ = [
    "AntiPattern",
    "detect_antipatterns",
    "Fingerprint",
    "SymmetryScore",
    "compute_fingerprint",
    "export_snapshot",
    "symmetry_report",
    "LayoutHealth",
    "compute_layout_health",
    "WidgetSnapshot",
    "describe_widget",
    "export_tree",
    "snapshot_tree",
    "LayoutCost",
    "profile_tree",
    "overlay_cost_payload",
]
