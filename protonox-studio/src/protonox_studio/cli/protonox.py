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
from protonox_studio.core.visual import compare_png_to_model, diff_pngs, ingest_png, render_model_to_png

# Android helpers live in the Protonox Kivy fork; import lazily so non-Android
# users are not penalized.
try:  # pragma: no cover - optional dependency
    from kivy.protonox_ext.android_bridge import adb
except Exception:  # pragma: no cover - optional dependency missing
    adb = None
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


def _write_export(plan, ui_model, export_dir: Path, context: ProjectContext) -> None:
    for filename, content in plan.kv_files.items():
        (export_dir / filename).write_text(content, encoding="utf-8")
    for filename, content in plan.controllers.items():
        (export_dir / filename).write_text(content, encoding="utf-8")

    ui_model.save(export_dir / "ui-model.json")

    manifest = {
        "message": "One-Click Fix listo",
        "project_type": context.project_type,
        "entrypoint": str(context.entrypoint),
        "kv_files": list(plan.kv_files.keys()),
        "controllers": list(plan.controllers.keys()),
        "bindings": [binding.__dict__ for binding in plan.bindings],
        "warnings": plan.warnings,
        "assets": ui_model.assets,
        "routes": ui_model.routes,
        "meta": ui_model.meta,
    }
    (export_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Export generado en {export_dir} (no se modificó el código del usuario)")


def _bindings_from_args(context: ProjectContext, ui_model, screen_args: List[str] | None) -> List[WebViewDeclaration]:
    declarations: List[WebViewDeclaration] = []
    if screen_args:
        for raw in screen_args:
            if ":" in raw:
                route, name = raw.split(":", 1)
            else:
                route, name = raw, raw
            declarations.append(
                WebViewDeclaration(
                    name=name,
                    source=context.entrypoint,
                    url=os.environ.get("PROTONOX_WEB_URL"),
                    route=route,
                )
            )
    else:
        if context.screen_map.routes:
            for route_cfg in context.screen_map.routes:
                declarations.append(
                    WebViewDeclaration(
                        name=route_cfg.screen,
                        source=context.entrypoint,
                        url=os.environ.get("PROTONOX_WEB_URL"),
                        route=route_cfg.route,
                    )
                )
        else:
            default_route = ui_model.routes[0] if getattr(ui_model, "routes", []) else None
            declarations.append(
                WebViewDeclaration(
                    name=context.entrypoint.stem or "web_screen",
                    source=context.entrypoint,
                    url=os.environ.get("PROTONOX_WEB_URL"),
                    route=default_route,
                )
            )
    return declarations


def run_export(context: ProjectContext, screen_args: List[str] | None = None, out: Path | None = None) -> None:
    context.ensure_state_tree()
    export_dir = out or context.state_dir / "protonox-exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    ui_model = context.build_ui_model()
    declarations = _bindings_from_args(context, ui_model, screen_args)
    bindings = bindings_from_views(declarations, screen_map=context.screen_map)
    plan = plan_web_to_kivy(ui_model, bindings=bindings)

    _write_export(plan, ui_model, export_dir, context)


def run_validate(
    baseline: Path,
    candidate: Path,
    out_dir: Path | None = None,
    context: ProjectContext | None = None,
) -> None:
    ui_model = None
    if context:
        try:
            ui_model = context.build_ui_model()
        except Exception:
            ui_model = None
    report = diff_pngs(baseline, candidate, out_dir=out_dir, ui_model=ui_model)
    print(json.dumps(report, indent=2, ensure_ascii=False))


def run_web2kivy(context: ProjectContext, screens: List[str] | None = None, out: Path | None = None) -> None:
    context.ensure_state_tree()
    export_dir = out or context.state_dir / "protonox-exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    ui_model = context.build_ui_model()
    declarations = _bindings_from_args(context, ui_model, screens)
    bindings = bindings_from_views(declarations, screen_map=context.screen_map)
    plan = plan_web_to_kivy(ui_model, bindings=bindings)
    _write_export(plan, ui_model, export_dir, context)


def _render_ui_model_png(context: ProjectContext, label: str) -> Path:
    context.ensure_state_tree()
    ui_model = context.build_ui_model()
    out_dir = context.state_dir / "renders"
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{label}.png"
    render_model_to_png(ui_model, target)
    return target


def run_render_web(context: ProjectContext) -> None:
    path = _render_ui_model_png(context, label="web")
    print(json.dumps({"status": "ok", "png": str(path.resolve())}, indent=2, ensure_ascii=False))


def run_render_kivy(context: ProjectContext) -> None:
    path = _render_ui_model_png(context, label="kivy")
    print(json.dumps({"status": "ok", "png": str(path.resolve())}, indent=2, ensure_ascii=False))


def _require_adb():
    if adb is None:
        raise SystemExit(
            "Android bridge no disponible: instala/activa kivy-protonox-version para usar comandos adb"
        )


def run_android_detect(adb_path: str = "adb") -> None:
    _require_adb()
    resolved = adb.ensure_adb(adb_path)
    devices = [device.__dict__ for device in adb.list_devices(adb_path=resolved)]
    print(json.dumps({"adb": resolved, "devices": devices}, indent=2, ensure_ascii=False))


def run_android_logs(package: str, adb_path: str = "adb", wifi_first: bool = True) -> None:
    _require_adb()
    os.environ.setdefault("PROTONOX_ADB_WIRELESS_FIRST", "1" if wifi_first else "0")
    resolved = adb.ensure_adb(adb_path)
    # Prefer wireless if requested
    if wifi_first:
        try:
            adb.connect_wireless(adb_path=resolved)
        except adb.ADBError:
            pass
    try:
        for event in adb.stream_logcat_structured(package=package, adb_path=resolved, include_gl=True):
            print(json.dumps(event, ensure_ascii=False))
    except KeyboardInterrupt:
        return


def run_android_restart(package: str, activity: str | None, adb_path: str = "adb", wifi_first: bool = True) -> None:
    _require_adb()
    os.environ.setdefault("PROTONOX_ADB_WIRELESS_FIRST", "1" if wifi_first else "0")
    resolved = adb.ensure_adb(adb_path)
    if wifi_first:
        try:
            adb.connect_wireless(adb_path=resolved)
        except adb.ADBError:
            pass
    adb.run_app(package=package, activity=activity, adb_path=resolved)
    print(json.dumps({"status": "restarted", "package": package, "activity": activity or ".MainActivity"}, ensure_ascii=False))


def run_android_reinstall(
    package: str,
    apk_path: str,
    activity: str | None,
    adb_path: str = "adb",
    wifi_first: bool = True,
) -> None:
    _require_adb()
    resolved = adb.ensure_adb(adb_path)
    if wifi_first:
        try:
            adb.connect_wireless(adb_path=resolved)
        except adb.ADBError:
            pass
    adb.push_reload(apk_path, package=package, activity=activity, adb_path=resolved)
    print(json.dumps({"status": "reinstalled", "apk": apk_path, "package": package}, ensure_ascii=False))


def run_android_wifi_connect(target: str | None, adb_path: str = "adb") -> None:
    _require_adb()
    resolved = adb.ensure_adb(adb_path)
    devices = [device.__dict__ for device in adb.connect_wireless(target=target, adb_path=resolved)]
    print(json.dumps({"adb": resolved, "devices": devices}, indent=2, ensure_ascii=False))


def run_android_wifi_restart(serial: str | None = None, port: int = 5555, adb_path: str = "adb") -> None:
    _require_adb()
    resolved = adb.ensure_adb(adb_path)
    host = adb.enable_wireless(serial=serial, port=port, adb_path=resolved)
    devices = [device.__dict__ for device in adb.connect_wireless(target=host, adb_path=resolved)] if host else []
    print(json.dumps({"target": host, "devices": devices}, indent=2, ensure_ascii=False))


def run_android_wifi_logs(package: str, adb_path: str = "adb") -> None:
    _require_adb()
    resolved = adb.ensure_adb(adb_path)
    adb.connect_wireless(adb_path=resolved)
    try:
        for event in adb.stream_logcat_structured(package=package, adb_path=resolved, include_gl=True):
            print(json.dumps(event, ensure_ascii=False))
    except KeyboardInterrupt:
        return

def main(argv=None):
    parser = argparse.ArgumentParser(description="Protonox Studio tooling")
    parser.add_argument(
        "command",
        choices=[
            "dev",
            "audit",
            "export",
            "diagnose",
            "web2kivy",
            "web-to-kivy",
            "validate",
            "diff",
            "render-web",
            "render-kivy",
            "android-detect",
            "android-logs",
            "android-restart",
            "android-reinstall",
            "android-wifi-connect",
            "android-wifi-restart",
            "android-wifi-logs",
        ],
        help="Comando a ejecutar",
    )
    parser.add_argument("--path", default=".", help="Ruta del proyecto")
    parser.add_argument("--project-type", choices=["web", "kivy"], help="Tipo de proyecto declarado (obligatorio para IA)")
    parser.add_argument("--entrypoint", help="Punto de entrada (index.html o main.py)")
    parser.add_argument("--map", help="Archivo JSON/YAML que mapea rutas web ↔ pantallas Kivy")
    parser.add_argument("--png", help="Ruta a una captura PNG para comparar con el modelo intermedio")
    parser.add_argument("--out", help="Directorio de salida para exportaciones")
    parser.add_argument("--screens", nargs="*", help="Pantallas o rutas declaradas para el mapeo Web→Kivy (route:name)")
    parser.add_argument("--baseline", help="PNG baseline para validación visual")
    parser.add_argument("--candidate", help="PNG candidato para validación visual")
    parser.add_argument("--package", help="Package Android para comandos adb")
    parser.add_argument("--activity", help="Actividad Android a lanzar (opcional)")
    parser.add_argument("--apk", help="APK para reinstalar con android-reinstall")
    parser.add_argument("--adb-path", dest="adb_path", help="Ruta a adb si no está en PATH")
    parser.add_argument(
        "--wifi-first",
        action="store_true",
        help="Preferir wireless debugging al streamear logs/reiniciar",
    )
    parser.add_argument("--wifi-target", help="Host:puerto opcional para android-wifi-connect")
    parser.add_argument("--serial", help="Serial USB para habilitar modo wireless")
    parser.add_argument("--port", type=int, default=5555, help="Puerto TCP para habilitar wireless tcpip")
    args = parser.parse_args(argv)

    context = ProjectContext.from_cli(
        Path(args.path), project_type=args.project_type, entrypoint=args.entrypoint, map_file=args.map
    )
    if args.command == "dev":
        run_dev_server(context)
    elif args.command == "audit":
        run_audit(context, png=args.png)
    elif args.command == "export":
        run_export(context, screen_args=args.screens, out=Path(args.out) if args.out else None)
    elif args.command in {"web2kivy", "web-to-kivy"}:
        run_web2kivy(context, screens=args.screens, out=Path(args.out) if args.out else None)
    elif args.command in {"validate", "diff"}:
        if not args.baseline or not args.candidate:
            raise SystemExit("validate requiere --baseline y --candidate")
        out_dir = Path(args.out) if args.out else None
        run_validate(Path(args.baseline), Path(args.candidate), out_dir=out_dir, context=context)
    elif args.command == "render-web":
        run_render_web(context)
    elif args.command == "render-kivy":
        run_render_kivy(context)
    elif args.command == "diagnose":
        report = run_bluntmine(context)
        print(json.dumps(report.as_dict(), indent=2, ensure_ascii=False))
    elif args.command == "android-detect":
        run_android_detect(adb_path=args.adb_path or "adb")
    elif args.command == "android-logs":
        if not args.package:
            raise SystemExit("android-logs requiere --package")
        run_android_logs(args.package, adb_path=args.adb_path or "adb", wifi_first=bool(args.wifi_first))
    elif args.command == "android-restart":
        if not args.package:
            raise SystemExit("android-restart requiere --package")
        run_android_restart(
            package=args.package,
            activity=args.activity,
            adb_path=args.adb_path or "adb",
            wifi_first=bool(args.wifi_first),
        )
    elif args.command == "android-reinstall":
        if not args.package or not args.apk:
            raise SystemExit("android-reinstall requiere --package y --apk")
        run_android_reinstall(
            package=args.package,
            apk_path=args.apk,
            activity=args.activity,
            adb_path=args.adb_path or "adb",
            wifi_first=bool(args.wifi_first),
        )
    elif args.command == "android-wifi-connect":
        run_android_wifi_connect(target=args.wifi_target, adb_path=args.adb_path or "adb")
    elif args.command == "android-wifi-restart":
        run_android_wifi_restart(serial=args.serial, port=args.port, adb_path=args.adb_path or "adb")
    elif args.command == "android-wifi-logs":
        if not args.package:
            raise SystemExit("android-wifi-logs requiere --package")
        run_android_wifi_logs(package=args.package, adb_path=args.adb_path or "adb")


if __name__ == "__main__":
    main()
