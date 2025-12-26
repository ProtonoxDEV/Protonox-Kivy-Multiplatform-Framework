"""Detect layout anti-patterns without touching the widget tree."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from ..telemetry import PROTONOX_TELEMETRY, widget_bounds

VISUAL_WARNINGS = os.environ.get("PROTONOX_VISUAL_WARNINGS", "0") == "1"


@dataclass
class AntiPattern:
    code: str
    message: str
    widget_id: Optional[str]

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "widget": self.widget_id}


def _widget_id(widget: Widget) -> str:
    return getattr(widget, "id", None) or widget.__class__.__name__


def detect_antipatterns(widget: Widget) -> List[AntiPattern]:
    if not VISUAL_WARNINGS or not PROTONOX_TELEMETRY:
        return []

    issues: List[AntiPattern] = []
    dpi = getattr(Window, "dpi", 96) or 96
    scale = Window.dpi / 160.0 if hasattr(Window, "dpi") else 1.0

    def _walk(node: Widget):
        _check_size_hints(node, issues)
        _check_nested_boxlayouts(node, issues)
        _check_invisible_space(node, issues)
        _check_scroll(node, issues)
        _check_dpi(node, issues, dpi, scale)
        for child in node.children:
            _walk(child)

    _walk(widget)
    return issues


def _check_size_hints(widget: Widget, issues: List[AntiPattern]):
    if getattr(widget, "size_hint", None) in [(None, None), (None, None)]:
        bounds = widget_bounds(widget)
        if bounds["width"] == 0 or bounds["height"] == 0:
            issues.append(
                AntiPattern(
                    code="size_hint_missing",
                    message="Widget has no size_hint and zero dimension; consider size_hint or fixed size",
                    widget_id=_widget_id(widget),
                )
            )


def _check_nested_boxlayouts(widget: Widget, issues: List[AntiPattern]):
    if isinstance(widget, BoxLayout) and isinstance(widget.parent, BoxLayout):
        issues.append(
            AntiPattern(
                code="nested_boxlayout",
                message="Nested BoxLayouts may be redundant; verify spacing/overlap",
                widget_id=_widget_id(widget),
            )
        )


def _check_invisible_space(widget: Widget, issues: List[AntiPattern]):
    if hasattr(widget, "opacity") and widget.opacity == 0 and hasattr(widget, "size_hint"):
        issues.append(
            AntiPattern(
                code="invisible_space",
                message="Invisible widget still takes layout space; consider removing or size_hint=(0,0)",
                widget_id=_widget_id(widget),
            )
        )


def _check_scroll(widget: Widget, issues: List[AntiPattern]):
    if isinstance(widget, ScrollView) and len(widget.children) == 0:
        issues.append(
            AntiPattern(
                code="empty_scrollview",
                message="ScrollView has no children; verify content binding",
                widget_id=_widget_id(widget),
            )
        )


def _check_dpi(widget: Widget, issues: List[AntiPattern], dpi: float, scale: float):
    bounds = widget_bounds(widget)
    abs_w = bounds["width"]
    abs_h = bounds["height"]
    if dpi < 120 and (abs_w > Window.width * 0.9 or abs_h > Window.height * 0.9):
        issues.append(
            AntiPattern(
                code="dpi_overflow",
                message="Widget nearly fills the screen on low-DPI device; consider responsive hints",
                widget_id=_widget_id(widget),
            )
        )
    if scale > 2 and getattr(widget, "font_size", None) and widget.font_size < 14:
        issues.append(
            AntiPattern(
                code="small_font_high_dpi",
                message="Font size may be too small for high-DPI displays",
                widget_id=_widget_id(widget),
            )
        )


__all__ = ["AntiPattern", "detect_antipatterns"]
