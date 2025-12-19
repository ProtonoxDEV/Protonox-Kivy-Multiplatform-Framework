"""Apply patch ops onto live widget trees.

This is intentionally conservative: unsupported ops return False so callers can
fallback to full rebuild.
"""

from __future__ import annotations

from typing import List, Tuple

from kivy.factory import Factory
from kivy.uix.widget import Widget

from .diff import PatchOp
from .ui_ir_types import UIComponent

WIDGET_MAP = {
    "container": "BoxLayout",
    "button": "Button",
    "label": "Label",
    "image": "Image",
    "input": "TextInput",
    "widget": "Widget",
}


def _get_by_path(root: Widget, path: Tuple[int, ...]) -> Widget | None:
    node = root
    for idx in path:
        if not hasattr(node, "children"):
            return None
        if idx >= len(node.children):
            return None
        # Kivy children are stored in reverse draw order
        node = list(reversed(node.children))[idx]
    return node


def _build_widget(component: UIComponent) -> Widget:
    kind = WIDGET_MAP.get(component.kind, "Widget")
    cls = Factory.get(kind)
    widget: Widget = cls()
    if component.text is not None and hasattr(widget, "text"):
        widget.text = component.text
    for key, value in (component.props or {}).items():
        if hasattr(widget, key):
            try:
                setattr(widget, key, value)
            except Exception:
                pass
    for child in component.children:
        widget.add_widget(_build_widget(child))
    return widget


def _dispose_widget(widget: Widget) -> None:
    if hasattr(widget, "dispose") and callable(getattr(widget, "dispose")):
        try:
            widget.dispose()
        except Exception:
            pass
    if hasattr(widget, "on_unmount") and callable(getattr(widget, "on_unmount")):
        try:
            widget.on_unmount()
        except Exception:
            pass


def apply_patch_ops(root: Widget, ops: List[PatchOp]) -> bool:
    for op in ops:
        if op.op == "update_text":
            target = _get_by_path(root, op.path[1:]) if op.path and isinstance(op.path[0], str) else _get_by_path(root, op.path)
            if target is None or not hasattr(target, "text"):
                return False
            try:
                target.text = op.payload.get("text")
            except Exception:
                return False
        elif op.op == "update_props":
            target = _get_by_path(root, op.path[1:]) if op.path and isinstance(op.path[0], str) else _get_by_path(root, op.path)
            if target is None:
                return False
            for key, value in (op.payload.get("props") or {}).items():
                if hasattr(target, key):
                    try:
                        setattr(target, key, value)
                    except Exception:
                        return False
        elif op.op == "add":
            parent = _get_by_path(root, op.path[:-1])
            if parent is None:
                return False
            comp: UIComponent = op.payload.get("component")  # type: ignore
            if not comp:
                return False
            try:
                parent.add_widget(_build_widget(comp))
            except Exception:
                return False
        elif op.op == "remove":
            parent = _get_by_path(root, op.path[:-1])
            if parent is None:
                return False
            idx = op.path[-1]
            try:
                target_child = list(reversed(parent.children))[idx]
                _dispose_widget(target_child)
                parent.remove_widget(target_child)
            except Exception:
                return False
        elif op.op == "move":
            parent = _get_by_path(root, op.path[:-1])
            if parent is None:
                return False
            try:
                source_idx = op.path[-1]
                target_widget = list(reversed(parent.children))[source_idx]
                parent.remove_widget(target_widget)
                parent.add_widget(target_widget, index=op.payload.get("to", 0))
            except Exception:
                return False
        elif op.op == "replace_subtree":
            parent = _get_by_path(root, op.path[:-1]) if op.path else None
            comp: UIComponent = op.payload.get("component")  # type: ignore
            if comp is None:
                return False
            try:
                if parent is None:
                    return False
                idx = op.path[-1]
                existing = list(reversed(parent.children))[idx]
                _dispose_widget(existing)
                parent.remove_widget(existing)
                parent.add_widget(_build_widget(comp), index=idx)
            except Exception:
                return False
        else:
            return False
    return True
