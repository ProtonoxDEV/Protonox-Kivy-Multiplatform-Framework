"""Diagnostics helpers for Protonox Kivy fork (opt-in)."""
from .bus import DiagnosticBus, DiagnosticEvent, BUS_ENABLED, get_bus
from .runtime import DiagnosticItem, DiagnosticReport, as_lines, collect_runtime_diagnostics

__all__ = [
    "DiagnosticItem",
    "DiagnosticReport",
    "DiagnosticBus",
    "DiagnosticEvent",
    "BUS_ENABLED",
    "get_bus",
    "as_lines",
    "collect_runtime_diagnostics",
]
