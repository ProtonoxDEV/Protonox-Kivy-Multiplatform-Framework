"""Registry that understands app_manifest.json from Studio exports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from ..ui_model.ui_ir_types import UIModel, load_ui_model


@dataclass
class ManifestEntry:
    screen_id: str
    route: str
    ui_model_path: Path
    kv_path: Optional[Path]
    hash: str
    capabilities: Dict[str, object]
    web_entrypoint: Optional[str]


class ScreenRegistry:
    def __init__(self, export_dir: Path):
        self.export_dir = export_dir
        self.entries: Dict[str, ManifestEntry] = {}
        self._id_cache_path = self.export_dir / "screen_ids.json"
        self._id_cache: Dict[str, str] = {}
        self._load_cache()
        self._load_manifest()

    def _load_manifest(self) -> None:
        manifest_path = self.export_dir / "app_manifest.json"
        if not manifest_path.exists():
            return
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        for screen in payload.get("screens", []) or []:
            screen_id = str(screen.get("screen") or self._stable_id(screen))
            entry = ManifestEntry(
                screen_id=screen_id,
                route=str(screen.get("route", "/")),
                ui_model_path=self.export_dir / (screen.get("ui_model") or screen.get("ui_model_path") or "ui-model.json"),
                kv_path=(self.export_dir / screen["kv"]) if screen.get("kv") else None,
                hash=screen.get("hash") or "",
                capabilities=screen.get("capabilities", {}) or {},
                web_entrypoint=screen.get("web_entrypoint"),
            )
            self.entries[entry.screen_id] = entry
        self._save_cache()

    def _stable_id(self, screen: dict) -> str:
        route = str(screen.get("route", "/"))
        cached = self._id_cache.get(route)
        if cached:
            return cached
        screen_id = route.strip("/").replace("/", "_") or "screen"
        self._id_cache[route] = screen_id
        return screen_id

    def _load_cache(self) -> None:
        if self._id_cache_path.exists():
            try:
                self._id_cache = json.loads(self._id_cache_path.read_text(encoding="utf-8"))
            except Exception:
                self._id_cache = {}

    def _save_cache(self) -> None:
        try:
            self._id_cache_path.write_text(json.dumps(self._id_cache, indent=2), encoding="utf-8")
        except Exception:
            pass

    def refresh(self) -> None:
        self.entries.clear()
        self._load_manifest()

    def get(self, screen_id: str) -> Optional[ManifestEntry]:
        return self.entries.get(screen_id)

    def load_model(self, screen_id: str) -> Optional[UIModel]:
        entry = self.get(screen_id)
        if not entry or not entry.ui_model_path.exists():
            return None
        return load_ui_model(entry.ui_model_path)

    def list_routes(self) -> Dict[str, str]:
        return {entry.route: sid for sid, entry in self.entries.items()}
