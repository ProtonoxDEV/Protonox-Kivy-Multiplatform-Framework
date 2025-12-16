"""Convert live Kivy widget trees back into the Protonox UIModel.

The importer is intentionally opt-in and read-only so existing apps remain
untouched unless the developer explicitly calls it. Geometry capture is gated
by the PROTONOX_LAYOUT_TELEMETRY flag to avoid leaking layout data in
production builds.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from kivy.lang import Builder
from kivy.uix.widget import Widget

from ..telemetry import PROTONOX_TELEMETRY, widget_bounds
from .ir import UIComponent, UIModel, UIScreen


def _widget_role(widget: Widget) -> str:
    return getattr(widget, "id", None) or widget.__class__.__name__


def widget_to_component(widget: Widget, include_geometry: bool = True) -> UIComponent:
    """Convert a widget (and its children) into a neutral UIComponent."""

    props = {}
    if include_geometry and PROTONOX_TELEMETRY:
        props.update(
            {
                "size": list(widget.size),
                "pos": list(widget.pos),
                "size_hint": list(widget.size_hint) if widget.size_hint else None,
                "pos_hint": getattr(widget, "pos_hint", None),
                "bounds": widget_bounds(widget),
            }
        )
    text = getattr(widget, "text", None)
    component = UIComponent(
        role=_widget_role(widget),
        kind=widget.__class__.__name__.lower(),
        text=text,
        props={k: v for k, v in props.items() if v is not None},
    )
    # Kivy stores children in reverse draw order; preserve visual stacking
    for child in reversed(widget.children):
        component.children.append(widget_to_component(child, include_geometry))
    return component


def screen_from_widget(widget: Widget, name: Optional[str] = None, include_geometry: bool = True) -> UIScreen:
    """Produce a UIScreen from a root widget without mutating the app."""

    screen_name = name or getattr(widget, "name", None) or _widget_role(widget)
    return UIScreen(name=screen_name, components=[widget_to_component(widget, include_geometry)])


def model_from_widget(widget: Widget, name: Optional[str] = None, include_geometry: bool = True) -> UIModel:
    """Build a UIModel containing a single screen from a root widget."""

    return UIModel(screens=[screen_from_widget(widget, name=name, include_geometry=include_geometry)])


def kv_file_to_model(kv_path: Path, root_factory: callable, include_geometry: bool = True) -> UIModel:
    """Load a KV file alongside a factory callable and export it as UIModel.

    The caller supplies ``root_factory`` to avoid importing user code implicitly.
    The KV file is loaded into the current Builder context temporarily and the
    resulting widget tree is converted into the neutral UIModel.
    """

    resolved = Path(kv_path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"KV file not found: {resolved}")
    Builder.load_file(str(resolved))
    root_widget: Widget = root_factory()
    return model_from_widget(root_widget, name=resolved.stem, include_geometry=include_geometry)
