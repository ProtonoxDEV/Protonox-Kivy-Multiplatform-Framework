"""Live Web→Kivy loop with file watching and manifest signaling.

This watcher re-runs the Web→Kivy pipeline when web sources change and writes
`app_manifest.json` plus a `.reload` sentinel so the running app can hot-reload
only the impacted screens. It stays within controlled paths.
"""

from __future__ import annotations

import json
import threading
import time
from hashlib import sha256
from pathlib import Path
from typing import List

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from protonox_studio.core.project_context import ProjectContext
from protonox_studio.core.web_to_kivy import WebViewDeclaration, bindings_from_views, plan_web_to_kivy
from protonox_studio.web2kivy.mapping import MappingManifest, ScreenBinding


def _compute_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _write_manifest(export_dir: Path, plan, bindings: List[WebViewDeclaration], entrypoint: Path) -> Path:
    screens: List[dict] = []
    kv_hashes = {name: _compute_hash(text) for name, text in plan.kv_files.items()}
    for binding in plan.bindings:
        screen_name = getattr(binding, "name", None) or getattr(binding, "screen", None) or "screen"
        route = getattr(binding, "route", "/")
        kv_file = plan.kv_filenames.get(screen_name) if hasattr(plan, "kv_filenames") else None
        kv_path = kv_file or next(iter(plan.kv_files.keys()), None)
        screen_entry = {
            "screen": screen_name,
            "route": route,
            "kv": kv_path,
            "ui_model": plan.ui_model_filename if hasattr(plan, "ui_model_filename") else "ui-model.json",
            "hash": kv_hashes.get(kv_path, "") if kv_path else "",
            "web_entrypoint": str(entrypoint),
        }
        screens.append(screen_entry)

    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entrypoint": str(entrypoint),
        "screens": screens,
    }

    target = export_dir / "app_manifest.json"
    export_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    # Touch reload sentinel
    (export_dir / ".reload").write_text(str(time.time()), encoding="utf-8")
    return target


def _ensure_mapping(export_dir: Path, bindings: List[WebViewDeclaration], entrypoint: Path) -> Path:
    manifest_path = export_dir / "protonox_studio.yaml"
    manifest = MappingManifest(project_root=str(entrypoint.parent), export_dir=str(export_dir))
    for decl in bindings:
        screen_name = decl.name or entrypoint.stem
        manifest.bind_screen(
            screen_name,
            ScreenBinding(
                route=decl.route or "/",
                kv=f"{screen_name}.kv",
                ui_model="ui-model.json",
                viewport=None,
                strategy="replace_content",
                web_entrypoint=str(decl.url or decl.source),
            ),
        )
    manifest.save(manifest_path)
    return manifest_path


class _DebouncedHandler(FileSystemEventHandler):
    def __init__(self, callback, debounce: float = 0.5):
        self.callback = callback
        self.debounce = debounce
        self._timer: threading.Timer | None = None

    def on_any_event(self, event):  # type: ignore[override]
        if event.is_directory:
            return
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self.debounce, self.callback)
        self._timer.daemon = True
        self._timer.start()


def live_loop(
    context: ProjectContext, watch_dir: Path | None = None, out_dir: Path | None = None, quiet_ms: int = 500
) -> None:
    watch_dir = watch_dir or context.entrypoint.parent
    export_dir = out_dir or (context.state_dir / "protonox-exports")
    export_dir.mkdir(parents=True, exist_ok=True)

    def build_once():
        ui_model = context.build_ui_model()
        declarations = _bindings_from_args(context, ui_model, None)
        bindings = bindings_from_views(declarations, screen_map=context.screen_map)
        plan = plan_web_to_kivy(ui_model, bindings=bindings)

        # Write KV, controllers, manifest
        for filename, content in plan.kv_files.items():
            (export_dir / filename).write_text(content, encoding="utf-8")
        for filename, content in plan.controllers.items():
            (export_dir / filename).write_text(content, encoding="utf-8")
        ui_model.save(export_dir / "ui-model.json")

        _ensure_mapping(export_dir, declarations, context.entrypoint)
        manifest_path = _write_manifest(export_dir, plan, declarations, context.entrypoint)
        print(f"[PXSTUDIO][LIVE] export refreshed → {manifest_path}")

    # Prime once
    build_once()

    handler = _DebouncedHandler(build_once, debounce=quiet_ms / 1000)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=True)
    observer.start()
    print(f"[PXSTUDIO][LIVE] watching {watch_dir} → exporting to {export_dir}")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def _bindings_from_args(context: ProjectContext, ui_model, screen_args: List[str] | None):
    declarations: List[WebViewDeclaration] = []
    if screen_args:
        for raw in screen_args:
            if ":" in raw:
                route, name = raw.split(":", 1)
            else:
                route, name = raw, raw
            declarations.append(WebViewDeclaration(name=name, source=context.entrypoint, url=None, route=route))
    else:
        default_route = ui_model.routes[0] if getattr(ui_model, "routes", []) else None
        declarations.append(
            WebViewDeclaration(
                name=context.entrypoint.stem or "web_screen", source=context.entrypoint, url=None, route=default_route
            )
        )
    return declarations


__all__ = ["live_loop"]
