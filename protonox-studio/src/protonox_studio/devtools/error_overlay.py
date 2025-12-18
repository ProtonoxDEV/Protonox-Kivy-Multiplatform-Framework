"""Error overlay widget used during development reload cycles.

The overlay is intentionally lightweight and self-contained so it can be used
from a crash handler without depending on project-specific UI layers.
"""

from __future__ import annotations

from typing import Callable, Optional

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex


class ErrorOverlay(FloatLayout):
    """A simple red overlay that surfaces exceptions during dev reload."""

    def __init__(self, message: str, traceback_text: str, on_rebuild: Optional[Callable[[], None]] = None):
        super().__init__()
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle

            Color(*get_color_from_hex("#330000"))
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        root = BoxLayout(orientation="vertical", padding=20, spacing=10)
        header = Label(
            text="Development Error",
            color=get_color_from_hex("#ffffff"),
            font_size="22sp",
            size_hint=(1, None),
            height=32,
        )
        summary = Label(
            text=message,
            color=get_color_from_hex("#ffdddd"),
            text_size=(0, None),
            halign="left",
            valign="middle",
            size_hint=(1, None),
        )
        summary.bind(texture_size=summary.setter("size"))

        scroll = ScrollView(size_hint=(1, 1))
        details = Label(
            text=traceback_text or "No traceback available",
            color=get_color_from_hex("#ffecec"),
            font_size="14sp",
            text_size=(0, None),
            halign="left",
            valign="top",
            size_hint=(1, None),
        )
        details.bind(texture_size=details.setter("size"))
        scroll.add_widget(details)

        actions = BoxLayout(orientation="horizontal", size_hint=(1, None), height=48, spacing=10)
        actions.add_widget(Label(text="", size_hint=(1, 1)))
        if on_rebuild is not None:
            actions.add_widget(
                Button(text="Rebuild", size_hint=(None, 1), width=120, on_release=lambda *_: on_rebuild())
            )
        root.add_widget(header)
        root.add_widget(summary)
        root.add_widget(scroll)
        root.add_widget(actions)
        self.add_widget(root)

    def _update_rect(self, *_) -> None:
        if hasattr(self, "_bg"):
            self._bg.pos = self.pos
            self._bg.size = self.size


def build_error_overlay(exc: str, tb: str, on_rebuild: Optional[Callable[[], None]] = None) -> ErrorOverlay:
    """Factory helper to build an :class:`ErrorOverlay`."""

    return ErrorOverlay(message=exc, traceback_text=tb, on_rebuild=on_rebuild)


__all__ = ["ErrorOverlay", "build_error_overlay"]
