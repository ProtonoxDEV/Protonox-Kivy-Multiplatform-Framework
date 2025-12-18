"""Web → Kivy bridge built around the neutral UI model.

This module keeps the conversion non-invasive: it reads HTML (and optional
JSON/PNG hints), produces a UIModel, and emits clean KV/Python scaffolds that
live outside the user's codebase.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from .engine import Viewport
from .screen_map import ScreenMap, ScreenRoute
from .ui_model import Bounds, ComponentNode, ScreenModel, UIModel


@dataclass
class WebViewDeclaration:
    """Declarative mapping for a single web view (URL or local file)."""

    name: str
    source: Path
    url: Optional[str] = None
    route: Optional[str] = None


@dataclass
class ScreenBinding:
    """Maps a web view to a target Kivy screen + KV file name."""

    web_view: str
    screen_name: str
    kv_filename: Optional[str] = None
    controller_name: Optional[str] = None
    route: Optional[str] = None


@dataclass
class KivyExportPlan:
    """Result of a Web → Kivy conversion without touching user code."""

    kv_files: Dict[str, str]
    controllers: Dict[str, str]
    bindings: List[ScreenBinding]
    warnings: List[str] = field(default_factory=list)


class _HtmlTreeBuilder(HTMLParser):
    def __init__(self, entrypoint: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.entrypoint = entrypoint
        self.root = ComponentNode(
            identifier=entrypoint.stem or "web-screen",
            role="screen",
            children=[],
            source="web",
            meta={"tag": "body", "source": str(entrypoint)},
        )
        self.stack: List[ComponentNode] = [self.root]
        self.viewport_hint: Optional[Viewport] = None
        self.assets: Set[str] = set()
        self.routes: Set[str] = set()

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        attrs_dict = {k: v for k, v in attrs if v is not None}
        if tag == "meta" and attrs_dict.get("name") == "viewport":
            content = attrs_dict.get("content", "")
            width = _extract_number(content, "width")
            height = _extract_number(content, "height")
            if width and height:
                self.viewport_hint = Viewport(width=int(width), height=int(height))

        asset = attrs_dict.get("href") or attrs_dict.get("src")
        if tag in {"link", "script", "img", "source", "video"} and asset:
            self.assets.add(str((self.entrypoint.parent / asset).resolve()))

        if tag in {"a", "route", "link"}:
            href = attrs_dict.get("href") or attrs_dict.get("data-route")
            if href:
                self.routes.add(href)

        style_tokens = _parse_style_tokens(attrs_dict.get("style", ""))

        node_id = attrs_dict.get("id") or attrs_dict.get("data-protonox-id")
        classes = attrs_dict.get("class")
        class_suffix = f"-{classes.split()[0]}" if classes else ""
        node_id = node_id or f"{tag}{class_suffix}-{len(self.stack[-1].children)+1}"

        node = ComponentNode(
            identifier=node_id,
            role=tag,
            children=[],
            source="web",
            meta={
                "tag": tag,
                "attrs": attrs_dict,
                "text_samples": [],
                "style": style_tokens,
                "classes": attrs_dict.get("class", "").split() if attrs_dict.get("class") else [],
            },
        )
        self.stack[-1].children.append(node)
        self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        # Pop until matching tag or root to keep parser resilient
        while len(self.stack) > 1:
            current = self.stack.pop()
            if current.role == tag:
                break

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        current = self.stack[-1]
        samples: List[str] = current.meta.setdefault("text_samples", [])  # type: ignore[assignment]
        if len(samples) < 3:
            samples.append(text[:140])


def _extract_number(content: str, key: str) -> Optional[int]:
    for token in content.split(","):
        if key in token:
            try:
                return int(token.split("=")[1])
            except (IndexError, ValueError):
                return None
    return None


def _parse_style_tokens(style: str) -> Dict[str, str]:
    tokens: Dict[str, str] = {}
    for chunk in style.split(";"):
        if not chunk.strip():
            continue
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        tokens[key.strip().lower()] = value.strip().lower()
    return tokens


def _parse_px(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    value = value.strip().lower()
    if value.endswith("px"):
        value = value[:-2]
    try:
        return float(value)
    except ValueError:
        return None


def _assign_bounds(node: ComponentNode, viewport: Viewport, y_offset: float = 0.0) -> float:
    """Very lightweight flow layout to keep boxes usable for audits."""

    x_cursor = 0.0
    y_cursor = y_offset
    gap = 12.0
    for child in node.children:
        style = child.meta.get("style", {}) if isinstance(child.meta, dict) else {}
        text_factor = max(1, len(" ".join(child.meta.get("text_samples", []))) // 20)

        child_width = _parse_px(style.get("width")) or (
            viewport.width * 0.9 if child.children else viewport.width * 0.8
        )
        child_height = _parse_px(style.get("height")) or max(48.0, 64.0 * text_factor)

        x_hint = _parse_px(style.get("left"))
        y_hint = _parse_px(style.get("top"))
        if x_hint is None:
            x_hint = x_cursor
        if y_hint is None:
            y_hint = y_cursor

        child.bounds = Bounds(x=x_hint, y=y_hint, width=child_width, height=child_height)

        y_cursor = _assign_bounds(child, viewport, y_hint + gap) + child_height + gap
        x_cursor = 0.0
    if node is not None and node.bounds is None:
        node.bounds = Bounds(x=0.0, y=0.0, width=viewport.width, height=max(y_cursor, viewport.height * 0.5))
    return y_cursor


def html_to_ui_model(entrypoint: Path, screen_map: Optional[ScreenMap] = None) -> UIModel:
    """Parse a HTML entrypoint into the neutral UI model.

    This avoids executing any JS; the goal is structural mapping, not pixel-perfect
    rendering. Bounds are approximated to keep grid/spacing analyzers working.
    """

    if not entrypoint.exists():
        raise FileNotFoundError(f"No se encontró el entrypoint HTML: {entrypoint}")

    parser = _HtmlTreeBuilder(entrypoint)
    parser.feed(entrypoint.read_text(encoding="utf-8", errors="ignore"))
    viewport = parser.viewport_hint or Viewport(width=1280, height=720)

    if screen_map and screen_map.routes:
        first_route = screen_map.routes[0]
        hint = first_route.viewport or {}
        viewport = Viewport(width=hint.get("width", viewport.width), height=hint.get("height", viewport.height))

    _assign_bounds(parser.root, viewport)
    meta = {"entrypoint": str(entrypoint.resolve())}
    if parser.routes:
        meta["routes_detected"] = sorted(parser.routes)
    screens: List[ScreenModel] = []
    if screen_map and screen_map.routes:
        for route_cfg in screen_map.routes:
            vp_hint = route_cfg.viewport or {}
            vp = Viewport(width=vp_hint.get("width", viewport.width), height=vp_hint.get("height", viewport.height))
            screens.append(ScreenModel(name=route_cfg.screen, viewport=vp, root=copy.deepcopy(parser.root)))
    else:
        screens.append(ScreenModel(name=parser.root.identifier, viewport=viewport, root=parser.root))

    return UIModel(
        screens=screens,
        origin="web",
        assets=sorted({str(entrypoint)} | parser.assets),
        routes=sorted(parser.routes),
        meta=meta,
        breakpoints={r.route: r.breakpoints for r in (screen_map.routes if screen_map else []) if r.breakpoints},
    )


def bindings_from_views(
    views: Iterable[WebViewDeclaration], screen_map: Optional[ScreenMap] = None
) -> List[ScreenBinding]:
    bindings: List[ScreenBinding] = []
    for view in views:
        mapped: Optional[ScreenRoute] = None
        if screen_map:
            mapped = screen_map.binding_for(view.route or view.name or "", view.name)

        screen_name = mapped.screen if mapped else view.name
        kv_filename = mapped.kv if mapped and mapped.kv else f"{screen_name}.kv"
        controller_name = mapped.controller if mapped and mapped.controller else f"{screen_name}_screen.py"
        bindings.append(
            ScreenBinding(
                web_view=view.route or view.url or str(view.source),
                screen_name=screen_name,
                kv_filename=kv_filename,
                controller_name=controller_name,
                route=view.route,
            )
        )
    return bindings


def _widget_for_node(node: ComponentNode) -> str:
    tag = (node.meta.get("tag") or node.role or "").lower()
    style = node.meta.get("style", {}) if isinstance(node.meta, dict) else {}
    if tag in {"button", "a", "cta"}:
        return "Button"
    if tag in {"input", "textarea"}:
        return "TextInput"
    if tag in {"img", "image", "picture"}:
        return "Image"
    if style.get("position") in {"absolute", "fixed"}:
        return "FloatLayout"
    if node.children:
        return "BoxLayout"
    return "Label"


def _kv_for_component(node: ComponentNode, viewport: Viewport, indent: int = 8) -> List[str]:
    pad = " " * indent
    lines: List[str] = []
    widget = _widget_for_node(node)
    lines.append(f"{pad}{widget}:")
    pad_in = " " * (indent + 4)

    node_id = node.identifier.replace("-", "_")
    lines.append(f"{pad_in}id: '{node_id}'")

    if node.bounds:
        width_hint = round(node.bounds.width / viewport.width, 3)
        height_hint = round(node.bounds.height / viewport.height, 3)
        lines.append(f"{pad_in}size_hint: ({min(width_hint, 1.0)}, {min(height_hint, 1.0)})")
        x_hint = round(node.bounds.x / viewport.width, 3)
        y_hint = round(node.bounds.y / viewport.height, 3)
        lines.append(f"{pad_in}pos_hint: {{'x': {max(x_hint, 0)}, 'y': {max(y_hint, 0)} }}")

    text_samples = node.meta.get("text_samples", [])
    if text_samples and widget in {"Label", "Button", "TextInput"}:
        preview = text_samples[0].replace("\n", " ")
        lines.append(f"{pad_in}text: '{preview}'")

    if node.children:
        style = node.meta.get("style", {}) if isinstance(node.meta, dict) else {}
        orientation = style.get("flex-direction") or (
            "horizontal" if node.bounds and node.bounds.width > node.bounds.height * 1.2 else "vertical"
        )
        if widget == "BoxLayout":
            lines.append(f"{pad_in}orientation: '{orientation}'")
            gap = style.get("gap") or style.get("column-gap") or style.get("row-gap")
            if gap:
                gap_val = _parse_px(gap)
                if gap_val is not None:
                    lines.append(f"{pad_in}spacing: {gap_val}")
        for child in node.children:
            lines.extend(_kv_for_component(child, viewport, indent + 4))
    return lines


def _screen_class_name(screen_name: str) -> str:
    return "".join(part.title() for part in screen_name.replace("-", "_").split("_")) + "Screen"


def plan_web_to_kivy(model: UIModel, bindings: Optional[List[ScreenBinding]] = None) -> KivyExportPlan:
    warnings: List[str] = []
    kv_files: Dict[str, str] = {}
    controllers: Dict[str, str] = {}

    for screen in model.screens:
        binding = None
        if bindings:
            binding = next((b for b in bindings if b.screen_name == screen.name or b.web_view == screen.name), None)
        if binding is None:
            binding = ScreenBinding(
                web_view=screen.name,
                screen_name=screen.name,
                kv_filename=f"{screen.name}.kv",
                controller_name=f"{screen.name}_screen.py",
            )

        kv_lines = [f"<{_screen_class_name(binding.screen_name)}@Screen>:"]
        kv_lines.append("    name: '%s'" % binding.screen_name)
        kv_lines.extend(_kv_for_component(screen.root, screen.viewport, indent=4))
        kv_files[binding.kv_filename or f"{binding.screen_name}.kv"] = "\n".join(kv_lines) + "\n"

        controller_name = binding.controller_name or f"{binding.screen_name}_screen.py"
        controllers[controller_name] = _controller_stub(
            binding.screen_name, kv_filename=binding.kv_filename or f"{binding.screen_name}.kv"
        )

    return KivyExportPlan(kv_files=kv_files, controllers=controllers, bindings=bindings or [], warnings=warnings)


def _controller_stub(screen_name: str, kv_filename: str) -> str:
    class_name = _screen_class_name(screen_name)
    return f"""from kivy.app import App\nfrom kivy.lang import Builder\nfrom kivy.uix.screenmanager import Screen, ScreenManager\n\n\nclass {class_name}(Screen):\n    pass\n\n\nclass PortedWebApp(App):\n    def build(self):\n        Builder.load_file('{kv_filename}')\n        sm = ScreenManager()\n        sm.add_widget({class_name}(name='{screen_name}'))\n        return sm\n\n\nif __name__ == '__main__':\n    PortedWebApp().run()\n"""
