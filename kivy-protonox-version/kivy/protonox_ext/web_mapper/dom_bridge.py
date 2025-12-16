"""Lightweight DOM → UIModel bridge (non-invasive).

This keeps parsing responsibilities minimal: it expects a pre-parsed DOM-like
structure (e.g., BeautifulSoup or a serialized tree) and converts it into the
neutral UIModel used by Protonox Studio.
"""
from __future__ import annotations

from typing import Dict, Iterable

from ..kv_bridge.ir import UIComponent, UIModel, UIScreen

ROLE_MAP = {
    "div": "container",
    "section": "container",
    "button": "button",
    "a": "button",
    "p": "label",
    "span": "label",
    "img": "image",
    "input": "input",
}


def _node_to_component(node: Dict[str, object]) -> UIComponent:
    tag = node.get("tag", "div")
    kind = ROLE_MAP.get(tag, "container")
    text = node.get("text")
    props = {"class": node.get("class"), "style": node.get("style")}
    children_payload: Iterable[Dict[str, object]] = node.get("children") or []
    children = [_node_to_component(child) for child in children_payload]
    return UIComponent(role=node.get("role", tag), kind=kind, text=text, props=props, children=children)


def dom_to_ui_model(dom_tree: Dict[str, object], screen_name: str = "screen") -> UIModel:
    root_component = _node_to_component(dom_tree)
    screen = UIScreen(name=screen_name, components=[root_component])
    return UIModel(screens=[screen])
