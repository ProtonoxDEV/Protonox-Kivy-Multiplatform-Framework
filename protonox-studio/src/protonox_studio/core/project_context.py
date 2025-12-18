"""Project context helpers for Protonox Studio.

This module centralizes the explicit project declarations requested by
Protonox Studio adopters. It keeps the entrypoint, project type and
state directories together so both local and container runs behave the
same way.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen

from .screen_map import ScreenMap, load_screen_map

PROJECT_TYPES = {"web", "kivy"}


def _default_entrypoint(root: Path, project_type: str) -> Path:
    if project_type == "web":
        return root / "index.html"
    return root / "main.py"


def _detect_site_root(path: Path) -> Path:
    """Infer the most likely web root that contains an index.html."""

    def add_candidate(bucket: List[Path], seen: set[Path], candidate: Path) -> None:
        try:
            resolved = candidate.resolve()
        except FileNotFoundError:
            return
        if resolved in seen or not resolved.exists():
            return
        seen.add(resolved)
        bucket.append(resolved)

    candidates: List[Path] = []
    seen: set[Path] = set()

    path = path.resolve()
    add_candidate(candidates, seen, path)

    common_children = ("website", "frontend", "public", "dist", "build")
    for child in common_children:
        add_candidate(candidates, seen, path / child)

    current = path
    for _ in range(3):
        add_candidate(candidates, seen, current.parent)
        for child in common_children:
            add_candidate(candidates, seen, current.parent / child)
        current = current.parent

    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
        for folder in ("public", "dist", "build"):
            nested = candidate / folder
            if (nested / "index.html").is_file():
                return nested

    return path


@dataclass
class ProjectContext:
    root: Path
    project_type: str
    entrypoint: Path
    state_dir: Path
    backend_url: str
    container_mode: bool
    screen_map: ScreenMap
    web_url: Optional[str] = None
    kv_files: List[Path] = field(default_factory=list)

    @classmethod
    def from_cli(
        cls,
        path: Path,
        project_type: Optional[str] = None,
        entrypoint: Optional[str] = None,
        map_file: Optional[str] = None,
    ) -> "ProjectContext":
        root = Path(path).resolve()
        resolved_type = (project_type or os.environ.get("PROTONOX_PROJECT_TYPE") or "web").lower()
        if resolved_type not in PROJECT_TYPES:
            raise ValueError(f"Tipo de proyecto inválido: {resolved_type}. Use: web | kivy")

        default_entry = _default_entrypoint(root, resolved_type)
        web_url: Optional[str] = None
        entry_path = (
            Path(entrypoint).resolve() if entrypoint and not str(entrypoint).startswith("http") else default_entry
        )

        if resolved_type == "web":
            if entrypoint and str(entrypoint).startswith("http"):
                web_url = str(entrypoint)
            if entry_path.is_dir():
                entry_path = entry_path / "index.html"
            if not entry_path.exists() and web_url is None:
                entry_path = _detect_site_root(root) / "index.html"
        else:
            if not entry_path.exists():
                alternative = root / "app/main.py"
                entry_path = alternative if alternative.exists() else entry_path

        state_dir = Path(os.environ.get("PROTONOX_STATE_DIR", root / ".protonox")).resolve()
        state_dir.mkdir(parents=True, exist_ok=True)

        if web_url:
            fetched = state_dir / "web-entrypoint.html"
            try:
                with urlopen(web_url) as response:
                    fetched.write_text(response.read().decode("utf-8", errors="ignore"), encoding="utf-8")
                entry_path = fetched
            except Exception:
                # keep default path; caller will surface missing file later
                pass

        container_mode = os.environ.get("PROTONOX_CONTAINER") == "1" or Path("/.dockerenv").exists()
        backend_url = os.environ.get("PROTONOX_BACKEND_URL", "https://protonox-backend.onrender.com")

        kv_files: List[Path] = []
        if resolved_type == "kivy":
            for pattern in ("*.kv", "**/*.kv"):
                kv_files.extend(Path(p).resolve() for p in root.glob(pattern))

        screen_map = load_screen_map(Path(map_file).resolve() if map_file else None, root)

        return cls(
            root=root,
            project_type=resolved_type,
            entrypoint=entry_path,
            state_dir=state_dir,
            backend_url=backend_url,
            container_mode=container_mode,
            screen_map=screen_map,
            web_url=web_url,
            kv_files=sorted(set(kv_files)),
        )

    def metadata(self) -> Dict[str, object]:
        return {
            "root": str(self.root),
            "entrypoint": str(self.entrypoint),
            "project_type": self.project_type,
            "backend": self.backend_url,
            "container": self.container_mode,
            "web_url": self.web_url,
            "kv_files": [str(k) for k in self.kv_files],
            "screen_map": str(self.screen_map.path) if self.screen_map.path else None,
        }

    def ensure_state_tree(self) -> None:
        for folder in (
            self.state_dir / "visual-errors",
            self.state_dir / "dev-reports",
            self.state_dir / "protonox-exports",
        ):
            folder.mkdir(parents=True, exist_ok=True)

    def build_ui_model(self):
        from . import ui_model

        if self.project_type == "kivy":
            from . import kivy_introspection

            return kivy_introspection.load_kivy_ui_model(self)

        # WEB: prefer declared HTML entrypoints or explicit snapshots
        snapshot_path = os.environ.get("PROTONOX_WEB_SNAPSHOT")
        if snapshot_path:
            path = Path(snapshot_path)
            if path.exists():
                try:
                    snapshot = json.loads(path.read_text(encoding="utf-8"))
                    return ui_model.from_web_snapshot(snapshot, origin="web")
                except Exception:
                    pass

        ui_model_path = os.environ.get("PROTONOX_UI_MODEL")
        if ui_model_path:
            path = Path(ui_model_path)
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    return ui_model.UIModel.from_dict(data)
                except Exception:
                    pass

        try:
            from .web_to_kivy import html_to_ui_model

            model = html_to_ui_model(self.entrypoint, screen_map=self.screen_map)
            model.meta.setdefault("screen_map", str(self.screen_map.path) if self.screen_map.path else None)
            return model
        except Exception:
            # Fall back to a neutral placeholder while keeping the audit path intact
            return ui_model.from_web_snapshot([], origin=self.project_type)
