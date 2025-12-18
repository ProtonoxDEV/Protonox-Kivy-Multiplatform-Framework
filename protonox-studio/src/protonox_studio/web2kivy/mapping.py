"""Mapping manifest helpers for Web→Kivy integrations.

The manifest is the single source of truth for connecting exported KV
layouts and UI-IR files to real Kivy screens. It is designed to live in
project-controlled paths like ``protobots/protonox_export`` or
``.protonox/web2kivy`` while keeping user code untouched.
"""

from __future__ import annotations

from collections.abc import Mapping

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Mapping as TypingMapping, MutableMapping

import json

try:  # Optional dependency, only needed when users choose YAML
    import yaml
except Exception:  # pragma: no cover - keep runtime lightweight when YAML is absent
    yaml = None


@dataclass
class ScreenBinding:
    """Connects a Kivy Screen to its exported assets and strategy."""

    route: str
    kv: str
    ui_model: str
    viewport: MutableMapping[str, int] | None = None
    strategy: str = "replace_content"
    web_entrypoint: str | None = None

    def to_dict(self) -> dict:
        payload = {
            "route": self.route,
            "kv": self.kv,
            "ui_model": self.ui_model,
            "strategy": self.strategy,
        }
        if self.viewport:
            payload["viewport"] = dict(self.viewport)
        if self.web_entrypoint:
            payload["web_entrypoint"] = self.web_entrypoint
        return payload


@dataclass
class MappingManifest:
    """Canonical manifest describing screen bindings and routes."""

    version: int = 1
    project_root: str | None = None
    export_dir: str | None = None
    screens: Dict[str, ScreenBinding] = field(default_factory=dict)
    routes: Dict[str, str] = field(default_factory=dict)
    navigation: dict | None = None
    meta: dict | None = None

    def bind_screen(self, screen_name: str, binding: ScreenBinding) -> None:
        self.screens[screen_name] = binding
        self.routes.setdefault(binding.route, screen_name)

    def bound_screens(self) -> Iterable[str]:
        return self.screens.keys()

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "project": {
                "root": self.project_root,
                "export_dir": self.export_dir,
            },
            "screens": {name: binding.to_dict() for name, binding in self.screens.items()},
            "routes": dict(self.routes),
            "navigation": self.navigation,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, payload: TypingMapping) -> "MappingManifest":
        project_cfg = payload.get("project") or {}
        screens_payload = payload.get("screens") or {}
        manifest = cls(
            version=payload.get("version", 1),
            project_root=project_cfg.get("root"),
            export_dir=project_cfg.get("export_dir"),
            routes=dict(payload.get("routes") or {}),
            navigation=payload.get("navigation"),
            meta=payload.get("meta"),
        )
        for screen_name, data in screens_payload.items():
            manifest.bind_screen(
                screen_name,
                ScreenBinding(
                    route=data.get("route", "/"),
                    kv=data.get("kv", ""),
                    ui_model=data.get("ui_model", ""),
                    viewport=data.get("viewport"),
                    strategy=data.get("strategy", "replace_content"),
                    web_entrypoint=data.get("web_entrypoint"),
                ),
            )
        return manifest

    @classmethod
    def load(cls, path: Path) -> "MappingManifest":
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")
        if path.suffix.lower() in {".yml", ".yaml"} and yaml is not None:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Mapping manifest must be a dictionary")
        return cls.from_dict(payload)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_dict()
        if path.suffix.lower() in {".yml", ".yaml"}:
            if yaml is None:
                raise RuntimeError("PyYAML is required to write YAML manifests")
            path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def ensure_route(self, route: str, screen_name: str) -> None:
        """Add a route mapping without overwriting existing entries."""
        self.routes.setdefault(route, screen_name)

    def merge_navigation(self, navigation: Mapping | None) -> None:
        if not navigation:
            return
        existing = self.navigation or {}
        merged = dict(existing)
        merged.update(navigation)
        self.navigation = merged


__all__ = ["MappingManifest", "ScreenBinding"]
