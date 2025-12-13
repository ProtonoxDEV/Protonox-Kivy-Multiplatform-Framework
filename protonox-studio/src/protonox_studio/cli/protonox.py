"""CLI for Protonox Studio – now wired to the evolving engine."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

import subprocess
import sys

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))

from protonox_studio.core import engine
from protonox_studio.core.bluntmine import run_bluntmine
from protonox_studio.core.project_context import ProjectContext
from protonox_studio.core.visual import compare_png_to_model, ingest_png
from protonox_studio.core.web_to_kivy import (
    WebViewDeclaration,
    bindings_from_views,
    plan_web_to_kivy,
)

# Note: the project uses a directory name with a hyphen (protonox-studio), which
# prevents importing it as a normal Python package when executing this file as
# a script. To keep `protonox dev` working when running this CLI directly, the
# `run_dev_server` command will spawn the server script as a subprocess.

def run_dev_server(context: ProjectContext) -> None:
    # Spawn the local_dev_server.py script as a subprocess so the CLI can be
    # executed as a standalone script (avoids relative import/package issues).
    server_py = Path(__file__).resolve().parents[1] / "core" / "local_dev_server.py"
    if not server_py.exists():
        raise FileNotFoundError(f"Server script not found: {server_py}")

    env = os.environ.copy()
    context.ensure_state_tree()
    env.setdefault("PROTONOX_SITE_ROOT", str(context.entrypoint.parent))
    env.setdefault("PROTONOX_STATE_DIR", str(context.state_dir))
    env.setdefault("PROTONOX_PROJECT_TYPE", context.project_type)
    env.setdefault("PROTONOX_BACKEND_URL", context.backend_url)

    # Use the same Python interpreter that's running this CLI
    subprocess.run([sys.executable, str(server_py)], env=env)


def _audit_from_model(ui_model, png_path: str | None = None) -> dict:
    boxes = ui_model.to_element_boxes()
    viewport = ui_model.screens[0].viewport if ui_model.screens else engine.Viewport(width=1280, height=720)
    eng = engine.bootstrap_engine()
    audit = eng.audit(boxes, viewport)
    summary = eng.summarize(audit)

    png_report = None
    if png_path:
        png_capture = ingest_png(Path(png_path))
        png_report = compare_png_to_model(png_capture, ui_model)

    return {
        "summary": summary,
        "audit": audit,
        "ui_model": ui_model.summary(),
        "png": png_report,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def run_audit(context: ProjectContext, png: str | None = None) -> None:
    ui_model = context.build_ui_model()
    report = _audit_from_model(ui_model, png_path=png)
    print(report["summary"])  # human-friendly line
    print(json.dumps(report, indent=2, ensure_ascii=False))


def run_export(context: ProjectContext) -> None:
    context.ensure_state_tree()
    export_dir = context.state_dir / "protonox-exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    ui_model = context.build_ui_model()
    default_binding = WebViewDeclaration(
        name=context.entrypoint.stem or "web_screen",
        source=context.entrypoint,
        url=os.environ.get("PROTONOX_WEB_URL"),
    )
    bindings = bindings_from_views([default_binding])
    plan = plan_web_to_kivy(ui_model, bindings=bindings)

    for filename, content in plan.kv_files.items():
        (export_dir / filename).write_text(content, encoding="utf-8")
    for filename, content in plan.controllers.items():
        (export_dir / filename).write_text(content, encoding="utf-8")

    manifest = {
        "message": "One-Click Fix listo",
        "project_type": context.project_type,
        "entrypoint": str(context.entrypoint),
        "kv_files": list(plan.kv_files.keys()),
        "controllers": list(plan.controllers.keys()),
        "bindings": [binding.__dict__ for binding in plan.bindings],
        "warnings": plan.warnings,
    }
    (export_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Export generado en {export_dir} (no se modificó el código del usuario)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Protonox Studio tooling")
    parser.add_argument("command", choices=["dev", "audit", "export", "diagnose"], help="Comando a ejecutar")
    parser.add_argument("--path", default=".", help="Ruta del proyecto")
    parser.add_argument("--project-type", choices=["web", "kivy"], help="Tipo de proyecto declarado (obligatorio para IA)")
    parser.add_argument("--entrypoint", help="Punto de entrada (index.html o main.py)")
    parser.add_argument("--png", help="Ruta a una captura PNG para comparar con el modelo intermedio")
    args = parser.parse_args(argv)

    context = ProjectContext.from_cli(Path(args.path), project_type=args.project_type, entrypoint=args.entrypoint)
    if args.command == "dev":
        run_dev_server(context)
    elif args.command == "audit":
        run_audit(context, png=args.png)
    elif args.command == "export":
        run_export(context)
    elif args.command == "diagnose":
        report = run_bluntmine(context)
        print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
