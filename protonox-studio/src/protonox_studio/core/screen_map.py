"""Screen and route mapping loader for Web→Kivy flows.

This keeps the CLI explicit: developers declare which web routes map to which
Kivy screens, the target viewport, and optional KV/controller filenames. Both
JSON and YAML are supported. The loader is non-fatal—if a map is missing or
malformed, the caller can continue with defaults while surfacing warnings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


try:  # optional dependency
    import yaml  # type: ignore
except Exception:  # pragma: no cover - optional
    yaml = None


DEFAULT_MAP_FILENAMES = (
    "protonox_studio.yaml",
    "protonox_studio.yml",
    "protonox_studio.json",
)


@dataclass
class ScreenRoute:
    route: str
    screen: str
    kv: Optional[str] = None
    controller: Optional[str] = None
    viewport: Optional[Dict[str, int]] = None
    breakpoints: Dict[str, Dict[str, int]] = field(default_factory=dict)


@dataclass
class ScreenMap:
    routes: List[ScreenRoute] = field(default_factory=list)
    meta: Dict[str, object] = field(default_factory=dict)
    path: Optional[Path] = None

    def binding_for(self, route: str, fallback_name: str) -> ScreenRoute:
        match = next((r for r in self.routes if r.route == route), None)
        return match or ScreenRoute(route=route, screen=fallback_name)


def _load_yaml(path: Path) -> Dict[str, object]:
    if yaml is None:
        raise RuntimeError("PyYAML es requerido para leer archivos YAML. Añade pyyaml al entorno.")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce_screen_routes(raw: Dict[str, object]) -> List[ScreenRoute]:
    routes: List[ScreenRoute] = []
    for item in raw.get("screens", []) if isinstance(raw, dict) else []:
        if not isinstance(item, dict):
            continue
        route = str(item.get("route") or item.get("path") or "").strip()
        screen = str(item.get("screen") or item.get("name") or route or "screen").strip()
        if not route:
            continue
        routes.append(
            ScreenRoute(
                route=route,
                screen=screen,
                kv=item.get("kv"),
                controller=item.get("controller"),
                viewport=item.get("viewport"),
                breakpoints=item.get("breakpoints", {}) if isinstance(item.get("breakpoints"), dict) else {},
            )
        )
    return routes


def load_screen_map(explicit: Optional[Path], root: Path) -> ScreenMap:
    candidates: List[Path] = []
    if explicit:
        candidates.append(explicit)
    candidates.extend(root.joinpath(name) for name in DEFAULT_MAP_FILENAMES)

    for candidate in candidates:
        if not candidate or not candidate.exists():
            continue
        try:
            if candidate.suffix.lower() in {".yaml", ".yml"}:
                raw = _load_yaml(candidate)
            else:
                raw = _load_json(candidate)
        except Exception:
            continue

        if not isinstance(raw, dict):
            continue
        routes = _coerce_screen_routes(raw)
        meta = {k: v for k, v in raw.items() if k not in {"screens"}}
        return ScreenMap(routes=routes, meta=meta, path=candidate)

    return ScreenMap(routes=[], meta={}, path=None)
