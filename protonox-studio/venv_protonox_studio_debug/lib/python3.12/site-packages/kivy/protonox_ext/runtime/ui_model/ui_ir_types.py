"""Lightweight UI-IR types for runtime (aligned with Studio exports).

We reuse the same shape as `kv_bridge.ir` but keep this module small and
resilient to partial payloads from live exports.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class UIComponent:
    role: str
    kind: str
    text: Optional[str] = None
    props: Dict[str, Any] = field(default_factory=dict)
    children: List["UIComponent"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UIComponent":
        kids = [cls.from_dict(child) for child in payload.get("children", []) or []]
        return cls(
            role=payload.get("role") or payload.get("id") or payload.get("type") or "node",
            kind=payload.get("type") or payload.get("kind") or "widget",
            text=payload.get("text"),
            props=payload.get("props", {}) or {},
            children=kids,
        )


@dataclass
class UIScreen:
    name: str
    components: List[UIComponent] = field(default_factory=list)
    viewport: Optional[Dict[str, int]] = None

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UIScreen":
        comps = [UIComponent.from_dict(p) for p in payload.get("components", []) or []]
        return cls(name=payload.get("screen") or payload.get("name") or "screen", components=comps, viewport=payload.get("viewport"))


@dataclass
class UIModel:
    screens: List[UIScreen] = field(default_factory=list)
    assets: Dict[str, Any] = field(default_factory=dict)
    routes: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "UIModel":
        screens_payload = payload.get("screens", []) or []
        screens = [UIScreen.from_dict(screen) for screen in screens_payload]
        return cls(screens=screens, assets=payload.get("assets", {}) or {}, routes=payload.get("routes", {}) or {})

    @classmethod
    def from_json(cls, path: Path) -> "UIModel":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "screens": [
                {
                    "screen": screen.name,
                    "components": [self._component_to_dict(c) for c in screen.components],
                    "viewport": screen.viewport,
                }
                for screen in self.screens
            ],
            "assets": self.assets,
            "routes": self.routes,
        }

    def _component_to_dict(self, comp: UIComponent) -> Dict[str, Any]:
        return {
            "role": comp.role,
            "type": comp.kind,
            "text": comp.text,
            "props": comp.props,
            "children": [self._component_to_dict(c) for c in comp.children],
        }

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path


def load_ui_model(path_or_payload) -> UIModel:
    if isinstance(path_or_payload, (str, Path)):
        return UIModel.from_json(Path(path_or_payload))
    if isinstance(path_or_payload, dict):
        return UIModel.from_dict(path_or_payload)
    raise TypeError("Unsupported UIModel input")
