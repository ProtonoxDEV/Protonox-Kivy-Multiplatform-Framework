"""Layout engine extensions (opt-in) for Kivy 2.3.1 Protonox fork."""

from .antipatterns import AntiPattern, detect_antipatterns
from .fingerprint import Fingerprint, SymmetryScore, compute_fingerprint, export_snapshot, symmetry_report
from .introspect import WidgetSnapshot, describe_widget, export_tree, snapshot_tree

__all__ = [
    "AntiPattern",
    "detect_antipatterns",
    "Fingerprint",
    "SymmetryScore",
    "compute_fingerprint",
    "export_snapshot",
    "symmetry_report",
    "WidgetSnapshot",
    "describe_widget",
    "export_tree",
    "snapshot_tree",
]
