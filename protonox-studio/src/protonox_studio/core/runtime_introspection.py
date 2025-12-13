"""Developer-only runtime introspection helpers for Kivy apps.

The inspector is deliberately read-only and defensive. It surfaces enough
context (widget tree, KV rules, scheduled callbacks) to guide Codex and
humans during diagnostics without mutating the running app.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.widget import Widget

class _StatefulApp(Protocol):
    def extract_state(self):
        ...


@dataclass
class WidgetSnapshot:
    id: str
    cls: str
    children: List["WidgetSnapshot"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "cls": self.cls,
            "children": [child.to_dict() for child in self.children],
        }


class RuntimeInspector:
    def __init__(self, app, enabled: bool) -> None:
        self.app = app
        self.enabled = enabled

    def _guard(self) -> bool:
        return bool(self.enabled)

    def widget_tree(self) -> Dict[str, Any] | None:
        if not self._guard():
            return None
        root = getattr(self.app, "approot", None) or getattr(self.app, "root", None)
        if root is None:
            return None
        return _serialize_widget(root).to_dict()

    def state(self) -> Any:
        if not self._guard():
            return None
        app = self.app
        if isinstance(app, _StatefulApp):
            try:
                return app.extract_state()
            except Exception:
                return None
        return None

    def kv_rules(self) -> List[str]:
        if not self._guard():
            return []
        try:
            return list(getattr(Builder, "rulectx", {}).keys())
        except Exception:
            return []

    def running_callbacks(self) -> List[str]:
        if not self._guard():
            return []
        callbacks: List[str] = []
        try:
            events = getattr(Clock, "_events", [])
            for event in events:
                cb = getattr(event, "callback", None)
                if cb:
                    callbacks.append(getattr(cb, "__name__", repr(cb)))
        except Exception:
            pass
        return callbacks

    def summary(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "has_root": bool(getattr(self.app, "approot", None) or getattr(self.app, "root", None)),
            "kv_rules": len(self.kv_rules()) if self.enabled else 0,
            "callbacks": len(self.running_callbacks()) if self.enabled else 0,
        }


def _serialize_widget(widget: Widget) -> WidgetSnapshot:
    children = [
        _serialize_widget(child)
        for child in getattr(widget, "children", [])
        if isinstance(child, Widget)
    ]
    identifier = getattr(widget, "id", None) or getattr(widget, "name", None) or widget.__class__.__name__
    return WidgetSnapshot(id=str(identifier), cls=widget.__class__.__name__, children=children)


__all__ = ["RuntimeInspector", "WidgetSnapshot"]
