"""CLI for Protonox Studio – now wired to the evolving engine."""

from __future__ import annotations
from protonox_studio.web2kivy.live import live_loop
from protonox_studio.core.web_to_kivy import (
    WebViewDeclaration,
    bindings_from_views,
    plan_web_to_kivy,
)
from protonox_studio.web import (
    run_web_dev,
    run_web_dev_generic,
    run_web_doctor,
    write_env_templates,
    ensure_assets_manifest,
    ingest_asset,
    watch_assets,
)
from protonox_studio.core.doctor_kivy import run_kivy_doctor
from protonox_studio.core.doctor import run_doctor
from protonox_studio.core.visual import compare_png_to_model, diff_pngs, ingest_png, render_model_to_png
from protonox_studio.core.project_context import ProjectContext
from protonox_studio.core.bluntmine import run_bluntmine
from protonox_studio.core import engine
from protonox_studio.core.wireless_client import connect_to_device, disconnect_from_device, is_connected, get_connected_url, reload_remote_app, reload_remote_file

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import shutil

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.append(str(PACKAGE_ROOT))


# Android helpers live in the Protonox Kivy fork; import lazily so non-Android
# users are not penalized.
try:  # pragma: no cover - optional dependency
    from kivy.protonox_ext.android_bridge import adb  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    adb = None


def _state_path() -> Path:
    return Path.home() / ".protonox" / "state.json"


def _load_state() -> dict:
    path = _state_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    path = _state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _maybe_welcome(argv: list[str]) -> None:
    """First-run greeting for the Protonox CLI (Positrón)."""

    if "--skip" in argv or "--no-welcome" in argv:
        return
    if os.getenv("PROTONOX_NO_WELCOME") == "1":
        return
    if not sys.stdin.isatty():
        return

    state = _load_state()
    if state.get("welcome_shown"):
        return

    print("\n👋 Hola, soy Positrón al servicio de Protonox.")
    print("📚 ¿Quieres el tutorial interactivo de la librería?")
    print("   Enter = sí | escribe 'skip' para omitir\n")

    try:
        ans = input("> ").strip().lower()
    except EOFError:
        ans = "skip"

    if ans != "skip":
        print("\n✅ Perfecto. Ejecuta: protonox mentor start\n")
    else:
        print("\n🟦 Entendido. Puedes iniciar cuando quieras con: protonox mentor start\n")

    state["welcome_shown"] = True
    _save_state(state)


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
    # safe defaults for live reload experience
    env.setdefault("PROTONOX_DEV", "1")
    env.setdefault("PROTONOX_ERROR_OVERLAY", "1")
    env.setdefault("PROTONOX_CLOCK_GUARD", "1")
    env.setdefault("PROTONOX_KV_STRICT", "1")

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
        raise SystemExit("Android bridge no disponible: instala/activa kivy-protonox-version para usar comandos adb")


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
    print(
        json.dumps(
            {"status": "restarted", "package": package, "activity": activity or ".MainActivity"}, ensure_ascii=False
        )
    )


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


def run_wireless_connect(url: str = "", adb_ip_port: str = "") -> None:
    """Connect to a wireless debug server."""
    if adb_ip_port:
        # Handle ADB wireless connection
        if not adb:
            print(json.dumps({"status": "failed", "error": "ADB bridge not available"}, indent=2, ensure_ascii=False))
            return
        
        try:
            adb_bin = adb.ensure_adb()
            # Connect ADB wirelessly
            adb.connect_wireless(adb_ip_port, adb_path=adb_bin)
            # Forward WebSocket port
            import subprocess
            subprocess.run([adb_bin, "forward", "tcp:8765", "tcp:8765"], check=True)
            # Connect WebSocket to localhost
            ws_url = "ws://localhost:8765"
            if connect_to_device(ws_url):
                print(json.dumps({"status": "connected", "adb_target": adb_ip_port, "ws_url": ws_url}, indent=2, ensure_ascii=False))
            else:
                print(json.dumps({"status": "failed", "adb_target": adb_ip_port}, indent=2, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"status": "failed", "adb_target": adb_ip_port, "error": str(e)}, indent=2, ensure_ascii=False))
    elif url:
        if connect_to_device(url):
            print(json.dumps({"status": "connected", "url": url}, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": "failed", "url": url}, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"status": "failed", "error": "Either --wireless-url or --adb-wireless-ip-port required"}, indent=2, ensure_ascii=False))


def run_wireless_disconnect() -> None:
    """Disconnect from wireless debug server."""
    disconnect_from_device()
    print(json.dumps({"status": "disconnected"}, indent=2, ensure_ascii=False))


def run_wireless_status() -> None:
    """Check wireless debug connection status."""
    connected = is_connected()
    url = get_connected_url() if connected else None
    print(json.dumps({"connected": connected, "url": url}, indent=2, ensure_ascii=False))


def run_wireless_reload(module: str = None) -> None:
    """Trigger a reload of the remote app."""
    if not is_connected():
        print(json.dumps({"status": "error", "message": "Not connected to wireless debug server"}, indent=2, ensure_ascii=False))
        return
    
    reload_remote_app(module)
    print(json.dumps({"status": "reload_triggered", "module": module}, indent=2, ensure_ascii=False))


def run_wireless_reload_file(file_path: str, file_content: str) -> None:
    """Reload a specific file on the remote app."""
    if not is_connected():
        print(json.dumps({"status": "error", "message": "Not connected to wireless debug server"}, indent=2, ensure_ascii=False))
        return
    
    reload_remote_file(file_path, file_content)
    print(json.dumps({"status": "file_reload_triggered", "file": file_path}, indent=2, ensure_ascii=False))


def run_mentor(open_in_code: bool = False) -> None:
    repo_root = Path(__file__).resolve().parents[4]
    start_here = repo_root / "docs" / "mentor" / "START_HERE.md"
    prompt_path = repo_root / "prompts" / "mentor.system.md"
    tasks_path = repo_root / "prompts" / "mentor.tasks.md"

    print("Mentor (Positrón) listo. Recursos:")
    print(f"- Onboarding: {start_here}")
    print(f"- Prompt base: {prompt_path}")
    print(f"- Misiones: {tasks_path}")
    print("\nUsa en tu chat: pega el prompt base y sigue START_HERE.")

    if open_in_code and shutil.which("code") and start_here.exists():
        try:
            subprocess.run(["code", str(start_here)], check=False)
            print("(Abrí START_HERE en VS Code)")
        except Exception:
            pass

    if not start_here.exists():
        print("⚠️ START_HERE.md no se encontró; revisa que estés en el repo completo.")


def main(argv=None):
    original_argv = argv if argv is not None else sys.argv[1:]

    # Allow "protonox mentor start" by stripping the extra token.
    open_mentor = False
    argv_for_parser = list(original_argv)
    if argv_for_parser[:2] == ["mentor", "start"]:
        open_mentor = True
        argv_for_parser = ["mentor"] + argv_for_parser[2:]

    _maybe_welcome(original_argv)

    parser = argparse.ArgumentParser(description="Protonox Studio tooling")
    parser.add_argument(
        "command",
        choices=[
            "dev",
            "doctor",
            "doctor-web",
            "doctor-kivy",
            "web-dev",
            "web-dev-generic",
            "web-env",
            "web-assets-import",
            "web-assets-watch",
            "audit",
            "export",
            "diagnose",
            "live",
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
            "wireless-connect",
            "wireless-disconnect",
            "wireless-status",
            "wireless-reload",
            "wireless-reload-file",
            "mentor",
        ],
        help="Comando a ejecutar",
    )
    parser.add_argument("--path", default=".", help="Ruta del proyecto")
    parser.add_argument(
        "--project-type", choices=["web", "kivy"], help="Tipo de proyecto declarado (obligatorio para IA)"
    )
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
    parser.add_argument("--watch", help="Directorio a observar en modo live (por defecto el entrypoint)")
    parser.add_argument("--quiet-ms", type=int, default=500, help="Debounce en milisegundos para reconstruir en live")
    parser.add_argument(
        "--wifi-first",
        action="store_true",
        help="Preferir wireless debugging al streamear logs/reiniciar",
    )
    parser.add_argument("--wifi-target", help="Host:puerto opcional para android-wifi-connect")
    parser.add_argument("--serial", help="Serial USB para habilitar modo wireless")
    parser.add_argument("--port", type=int, default=5555, help="Puerto TCP para habilitar wireless tcpip o dev web")
    parser.add_argument("--android", action="store_true", help="Modo Android para doctor")
    parser.add_argument("--preset", help="Preset para web env (firebase/render/local)")
    parser.add_argument("--asset", help="Ruta de asset a importar (web)")
    parser.add_argument("--watch-dir", dest="watch_dir", help="Directorio a observar para assets")
    parser.add_argument("--wireless-url", help="WebSocket URL para conectar wireless debugging")
    parser.add_argument("--adb-wireless-ip-port", help="IP:puerto para ADB wireless connect (Android)")
    parser.add_argument("--reload-module", help="Módulo a recargar (para wireless-reload)")
    parser.add_argument("--reload-file", help="Archivo a recargar (para wireless-reload-file)")
    parser.add_argument("--reload-content", help="Contenido del archivo a recargar (para wireless-reload-file)")
    args = parser.parse_args(argv_for_parser)

    context = ProjectContext.from_cli(
        Path(args.path), project_type=args.project_type, entrypoint=args.entrypoint, map_file=args.map
    )
    if args.command == "dev":
        run_dev_server(context)
    elif args.command == "doctor":
        report = run_doctor(android=bool(args.android), base=Path(args.path))
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.command == "doctor-web":
        report = run_web_doctor(base=Path(args.path), port=args.port or 5173)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.command == "doctor-kivy":
        report = run_kivy_doctor()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.command == "web-dev":
        run_web_dev(base=Path(args.path), port=args.port if args.port not in (None, 5555) else None)
    elif args.command == "web-dev-generic":
        run_web_dev_generic(args.path, overlay_port=args.port or 4173)
    elif args.command == "web-env":
        write_env_templates(base=Path(args.path), preset=args.preset)
    elif args.command == "web-assets-import":
        if not args.asset:
            raise SystemExit("web-assets-import requiere --asset <ruta>")
        manifest = ensure_assets_manifest(Path(args.path))
        entry = ingest_asset(Path(args.asset), base=Path(args.path))
        print(json.dumps({"manifest": str(manifest), "entry": entry}, indent=2, ensure_ascii=False))
    elif args.command == "web-assets-watch":
        watch_dir = Path(args.watch_dir or args.path)
        watch_assets(watch_dir, base=Path(args.path))
    elif args.command == "audit":
        run_audit(context, png=args.png)
    elif args.command == "export":
        run_export(context, screen_args=args.screens, out=Path(args.out) if args.out else None)
    elif args.command == "live":
        watch_dir = Path(args.watch) if args.watch else None
        out_dir = Path(args.out) if args.out else None
        live_loop(context, watch_dir=watch_dir, out_dir=out_dir, quiet_ms=args.quiet_ms)
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
    elif args.command == "wireless-connect":
        if not args.wireless_url and not args.adb_wireless_ip_port:
            raise SystemExit("wireless-connect requiere --wireless-url o --adb-wireless-ip-port")
        run_wireless_connect(url=args.wireless_url or "", adb_ip_port=args.adb_wireless_ip_port or "")
    elif args.command == "wireless-disconnect":
        run_wireless_disconnect()
    elif args.command == "wireless-status":
        run_wireless_status()
    elif args.command == "wireless-reload":
        run_wireless_reload(module=args.reload_module)
    elif args.command == "wireless-reload-file":
        if not args.reload_file:
            raise SystemExit("wireless-reload-file requiere --reload-file")
        if not args.reload_content:
            # Read content from file
            with open(args.reload_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = args.reload_content
        run_wireless_reload_file(file_path=args.reload_file, file_content=content)
    elif args.command == "mentor":
        run_mentor(open_in_code=open_mentor or os.getenv("PROTONOX_MENTOR_OPEN") == "1")


if __name__ == "__main__":
    main()
