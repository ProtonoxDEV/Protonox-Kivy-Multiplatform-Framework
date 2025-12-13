"""Protonox extensions for the vendored Kivy 2.3.1 build.

This package remains opt-in and avoids altering Kivy's public API. It provides
helpers for layout telemetry, widget tree export, and safe PNG capture so
Protonox Studio can analyze running apps without mutating user code.
"""

from .telemetry import (
    LayoutMetric,
    collect_layout_report,
    export_widget_tree,
    safe_export_to_png,
    widget_bounds,
)

__all__ = [
    "LayoutMetric",
    "collect_layout_report",
    "export_widget_tree",
    "safe_export_to_png",
    "widget_bounds",
]
