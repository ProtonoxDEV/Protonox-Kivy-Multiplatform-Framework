"""Neutral UI model shared by web and Kivy projects.

The goal is to keep ARC/IA work against this intermediate structure
instead of mutating HTML or KV files directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .engine import ElementBox, Viewport


@dataclass
class Bounds:
    x: float
    y: float
    width: float
    height: float


@dataclass
class ComponentNode:
    identifier: str
    role: str = "component"
    bounds: Optional[Bounds] = None
    children: List["ComponentNode"] = field(default_factory=list)
    source: str = "web"  # web | kivy | synthetic
    meta: Dict[str, Any] = field(default_factory=dict)

    def walk(self) -> Iterable["ComponentNode"]:
        yield self
        for child in self.children:
            yield from child.walk()


@dataclass
class ScreenModel:
    name: str
    viewport: Viewport
    root: ComponentNode


@dataclass
class UIModel:
    screens: List[ScreenModel]
    origin: str
    assets: List[str] = field(default_factory=list)

    def to_element_boxes(self) -> List[ElementBox]:
        boxes: List[ElementBox] = []
        for screen in self.screens:
            for node in screen.root.walk():
                if node.bounds:
                    boxes.append(
                        ElementBox(
                            id=node.identifier,
                            x=node.bounds.x,
                            y=node.bounds.y,
                            width=node.bounds.width,
                            height=node.bounds.height,
                            padding=node.meta.get("padding", []),
                            margin=node.meta.get("margin", []),
                            color=node.meta.get("color"),
                            text_samples=node.meta.get("text_samples", []),
                        )
                    )
        return boxes

    def summary(self) -> Dict[str, Any]:
        return {
            "origin": self.origin,
            "screens": [
                {
                    "name": screen.name,
                    "viewport": {
                        "width": screen.viewport.width,
                        "height": screen.viewport.height,
                    },
                    "components": [node.identifier for node in screen.root.walk()],
                }
                for screen in self.screens
            ],
            "assets": self.assets,
        }


def from_web_snapshot(snapshot: List[dict], origin: str = "web") -> UIModel:
    elements = snapshot or [
        {"id": "hero", "x": 24, "y": 36, "width": 960, "height": 480, "padding": [32, 32, 40, 32], "margin": [0, 0, 48, 0], "color": "#0d1117", "text_samples": [48, 30, 20]},
        {"id": "cta", "x": 64, "y": 560, "width": 320, "height": 96, "padding": [16, 24, 16, 24], "margin": [0, 0, 24, 0], "color": "#58a6ff", "text_samples": [18, 16]},
    ]
    nodes: List[ComponentNode] = []
    for element in elements:
        bounds = Bounds(x=element["x"], y=element["y"], width=element["width"], height=element["height"])
        nodes.append(
            ComponentNode(
                identifier=element.get("id", "component"),
                bounds=bounds,
                source="web",
                meta={
                    "padding": element.get("padding", []),
                    "margin": element.get("margin", []),
                    "color": element.get("color"),
                    "text_samples": element.get("text_samples", []),
                },
            )
        )

    root = ComponentNode(identifier="screen", role="screen", children=nodes, source="web")
    viewport = Viewport(width=1280, height=720)
    return UIModel(screens=[ScreenModel(name="default", viewport=viewport, root=root)], origin=origin)


def from_kivy_tree(name: str, tree: ComponentNode, viewport: Optional[Viewport] = None) -> UIModel:
    vp = viewport or Viewport(width=1280, height=720)
    return UIModel(screens=[ScreenModel(name=name, viewport=vp, root=tree)], origin="kivy")

