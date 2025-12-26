"""Neutral UI Intermediate Representation for Web→Kivy translation.

The IR is intentionally simple and serializable to JSON so that external tools
can diff, version, or patch it without touching KV or HTML directly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class UIComponent:
    role: str
    kind: str
    text: Optional[str] = None
    props: Dict[str, object] = field(default_factory=dict)
    children: List["UIComponent"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "role": self.role,
            "type": self.kind,
            "text": self.text,
            "props": self.props,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass
class UIScreen:
    name: str
    components: List[UIComponent] = field(default_factory=list)
    viewport: Optional[Dict[str, int]] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "screen": self.name,
            "components": [c.to_dict() for c in self.components],
            "viewport": self.viewport,
        }


@dataclass
class UIModel:
    screens: List[UIScreen] = field(default_factory=list)
    assets: Dict[str, object] = field(default_factory=dict)
    routes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "screens": [s.to_dict() for s in self.screens],
            "assets": self.assets,
            "routes": self.routes,
        }

    def to_json(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "UIModel":
        screens_payload = payload.get("screens", []) or []
        screens = []
        for screen in screens_payload:
            comps = [UIComponent(**{k: v for k, v in comp.items() if k != "children"}) for comp in screen.get("components", [])]
            # Rebuild children relationships
            for comp, comp_payload in zip(comps, screen.get("components", [])):
                comp.children = [UIComponent(**child) for child in comp_payload.get("children", [])]
            screens.append(
                UIScreen(
                    name=screen.get("screen", ""),
                    components=comps,
                    viewport=screen.get("viewport"),
                )
            )
        return cls(
            screens=screens,
            assets=payload.get("assets", {}),
            routes=payload.get("routes", {}),
        )

    @classmethod
    def from_json(cls, path: Path) -> "UIModel":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))
