"""Lightweight Kivy 2.3.1 inspection helpers.

These helpers avoid mutating user projects and keep the mapping between
`.kv` definitions and Python classes explicit. The goal is to feed the
intermediate UI model, not to render widgets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .engine import Viewport
from .ui_model import Bounds, ComponentNode, UIModel, from_kivy_tree
from .project_context import ProjectContext


@dataclass
class KivyWidget:
    name: str
    rule: Optional[str] = None
    python_class: Optional[str] = None
    children: List["KivyWidget"] = field(default_factory=list)
    bounds: Optional[Bounds] = None
    source: Optional[Path] = None

    def to_component(self) -> ComponentNode:
        return ComponentNode(
            identifier=self.name,
            role=self.rule or "widget",
            bounds=self.bounds,
            children=[child.to_component() for child in self.children],
            source="kivy",
            meta={
                "rule": self.rule,
                "python_class": self.python_class,
                "source": str(self.source) if self.source else None,
            },
        )


def _parse_python_classes(entrypoint: Path) -> Dict[str, str]:
    class_regex = re.compile(r"^class\s+(\w+)\(([^)]*)\):", re.MULTILINE)
    contents = entrypoint.read_text(encoding="utf-8", errors="ignore") if entrypoint.exists() else ""
    matches = class_regex.findall(contents)
    mapping: Dict[str, str] = {}
    for name, parents in matches:
        mapping[name] = parents
    return mapping


def _parse_kv_rules(path: Path) -> List[KivyWidget]:
    widgets: List[KivyWidget] = []
    stack: List[tuple[int, KivyWidget]] = []
    indent_regex = re.compile(r"^(\s*)([^#:][^:]*):(.*)$")
    kv_text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in kv_text:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = indent_regex.match(line)
        if not match:
            continue
        indent, name, _ = match.groups()
        depth = len(indent)
        name = name.strip()
        widget = KivyWidget(name=name, rule=name, source=path)
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            stack[-1][1].children.append(widget)
        else:
            widgets.append(widget)
        stack.append((depth, widget))
    return widgets


def _attach_python_classes(widgets: Iterable[KivyWidget], class_map: Dict[str, str]) -> None:
    for widget in widgets:
        widget.python_class = next((cls for cls in class_map if cls.lower() == widget.name.lower()), None)
        _attach_python_classes(widget.children, class_map)


def build_kivy_tree(context: ProjectContext) -> List[KivyWidget]:
    class_map = _parse_python_classes(context.entrypoint)
    trees: List[KivyWidget] = []
    for kv_file in context.kv_files:
        parsed = _parse_kv_rules(kv_file)
        _attach_python_classes(parsed, class_map)
        trees.extend(parsed)
    return trees


def load_kivy_ui_model(context: ProjectContext) -> UIModel:
    trees = build_kivy_tree(context)
    if not trees:
        placeholder = ComponentNode(identifier="kivy-screen", role="screen", source="kivy")
        return from_kivy_tree("kivy", placeholder, viewport=Viewport(width=1280, height=720))

    # Best effort: assume first top-level widget is the screen root.
    root_widget = trees[0]
    component = root_widget.to_component()
    return from_kivy_tree(root_widget.name, component, viewport=Viewport(width=1280, height=720))
