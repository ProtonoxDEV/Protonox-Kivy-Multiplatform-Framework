"""Responsive helpers for Kivy layouts (opt-in, non-invasive).

These helpers do not change existing Kivy layouts. They provide lightweight
breakpoint/orientation utilities that can be imported in KV or Python code
to tweak size_hints or spacing without introducing new base classes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from kivy.core.window import Window

Breakpoint = Literal["mobile", "tablet", "desktop"]
Orientation = Literal["portrait", "landscape"]


@dataclass
class ResponsiveMetrics:
    width: int
    height: int
    dpi: float

    @property
    def orientation(self) -> Orientation:
        return "landscape" if self.width >= self.height else "portrait"


DEFAULT_DPI = 160.0


def _current_metrics() -> ResponsiveMetrics:
    try:
        width, height = Window.size
        dpi = getattr(Window, "dpi", DEFAULT_DPI) or DEFAULT_DPI
    except Exception:
        width, height, dpi = 1280, 720, DEFAULT_DPI
    return ResponsiveMetrics(width=int(width), height=int(height), dpi=float(dpi))


def breakpoint(metrics: Optional[ResponsiveMetrics] = None) -> Breakpoint:
    """Return a coarse breakpoint label based on size and DPI."""

    m = metrics or _current_metrics()
    # Adjust thresholds by DPI to keep physical size in mind
    logical_width = m.width * (DEFAULT_DPI / max(m.dpi, 1))
    if logical_width < 720:
        return "mobile"
    if logical_width < 1200:
        return "tablet"
    return "desktop"


def orientation(metrics: Optional[ResponsiveMetrics] = None) -> Orientation:
    m = metrics or _current_metrics()
    return m.orientation


__all__ = ["breakpoint", "orientation", "ResponsiveMetrics", "Breakpoint", "Orientation"]
