"""KV generator from the neutral UIModel.

This module keeps generation minimal and non-invasive. It emits KV strings or
writes KV files in a separate target directory so existing apps remain untouched.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

from .ir import UIComponent, UIModel, UIScreen


WIDGET_MAP: Dict[str, str] = {
    "container": "BoxLayout",
    "button": "Button",
    "label": "Label",
    "image": "Image",
    "input": "TextInput",
}


def _component_to_kv(component: UIComponent, indent: int = 0) -> str:
    widget = WIDGET_MAP.get(component.kind, "Widget")
    lines: List[str] = ["    " * indent + f"{widget}:"]
    if component.text:
        lines.append("    " * (indent + 1) + f"text: {component.text!r}")
    for key, value in (component.props or {}).items():
        lines.append("    " * (indent + 1) + f"{key}: {value!r}")
    for child in component.children:
        lines.append(_component_to_kv(child, indent + 1))
    return "\n".join(lines)


def screen_to_kv(screen: UIScreen) -> str:
    header = [f"<Screen name='{screen.name}'>"]
    body = [_component_to_kv(component, indent=1) for component in screen.components]
    return "\n".join(header + body + ["</Screen>", ""])


def model_to_kv(ui_model: UIModel) -> Tuple[str, Dict[str, str]]:
    """Return consolidated KV string and per-screen fragments.

    The compiler deliberately avoids touching existing files and leaves integration
    to the caller. It enables Protonox Studio to emit KV artifacts into a sandbox
    while keeping the original project intact.
    """

    fragments: Dict[str, str] = {}
    for screen in ui_model.screens:
        fragments[screen.name] = screen_to_kv(screen)
    combined = "\n".join(fragments.values())
    return combined, fragments


def write_kv(ui_model: UIModel, target_dir: Path) -> Dict[str, Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    _, fragments = model_to_kv(ui_model)
    outputs: Dict[str, Path] = {}
    for name, kv in fragments.items():
        path = target_dir / f"{name}.kv"
        path.write_text(kv, encoding="utf-8")
        outputs[name] = path
    return outputs
