from __future__ import annotations

import json
import shutil
import socket
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class WebCheck:
    name: str
    ok: bool
    detail: str
    fix: Optional[str] = None


def _bool(ok: bool) -> str:
    return "OK" if ok else "FIX"


def check_node() -> WebCheck:
    node = shutil.which("node")
    if not node:
        return WebCheck("node", False, "node not found", fix="Install Node.js (use nvm)")
    try:
        out = subprocess.check_output([node, "-v"], text=True).strip()
    except Exception:
        out = "unknown"
    return WebCheck("node", True, out)


def check_package_manager(base: Path) -> WebCheck:
    if (base / "pnpm-lock.yaml").exists():
        return WebCheck("package-manager", True, "pnpm", fix=None)
    if (base / "yarn.lock").exists():
        return WebCheck("package-manager", True, "yarn", fix=None)
    if (base / "package-lock.json").exists():
        return WebCheck("package-manager", True, "npm", fix=None)
    return WebCheck("package-manager", False, "no lockfile", fix="Generate lockfile (npm install / pnpm install)")


def check_env_files(base: Path) -> List[WebCheck]:
    env = base / ".env"
    env_example = base / ".env.example"
    return [
        WebCheck(
            "env",
            env.exists(),
            str(env),
            fix="cp .env.example .env" if (not env.exists() and env_example.exists()) else None,
        ),
        WebCheck(
            "env-example",
            env_example.exists(),
            str(env_example),
            fix="create .env.example" if not env_example.exists() else None,
        ),
    ]


def check_port_free(port: int) -> WebCheck:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        result = sock.connect_ex(("127.0.0.1", port))
    ok = result != 0
    return WebCheck(
        "port", ok, f"port {port} free" if ok else f"port {port} busy", fix="use --port or PROTONOX_WEB_PORT"
    )


def check_build_script(base: Path) -> WebCheck:
    pkg = base / "package.json"
    if not pkg.exists():
        return WebCheck("build-script", False, "package.json missing", fix="npm init or install deps")
    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
        scripts = data.get("scripts", {})
        ok = "build" in scripts
        return WebCheck(
            "build-script", ok, "build script present" if ok else "missing", fix="add 'build' script to package.json"
        )
    except Exception:
        return WebCheck("build-script", False, "invalid package.json", fix="fix package.json")


def _read_vite_config(base: Path) -> Optional[str]:
    for name in ["vite.config.ts", "vite.config.js", "vite.config.mjs", "vite.config.cjs"]:
        cfg = base / name
        if cfg.exists():
            try:
                return cfg.read_text(encoding="utf-8")
            except Exception:
                return None
    return None


def check_vite_proxy(base: Path) -> WebCheck:
    cfg = _read_vite_config(base)
    if cfg is None:
        return WebCheck("proxy", False, "vite config missing", fix="add vite.config.* with server.proxy")
    ok = "proxy" in cfg and "server" in cfg
    return WebCheck("proxy", ok, "proxy configured" if ok else "missing", fix="declare server.proxy for API routing")


def check_vite_cors(base: Path) -> WebCheck:
    cfg = _read_vite_config(base)
    if cfg is None:
        return WebCheck("cors", False, "vite config missing", fix="add vite.config.* with server.cors")
    ok = "cors" in cfg or "origin" in cfg
    return WebCheck("cors", ok, "CORS hints found" if ok else "unknown", fix="set server.cors: true or allow origin")


def check_vite_aliases(base: Path) -> WebCheck:
    cfg = _read_vite_config(base)
    if cfg is None:
        return WebCheck("aliases", False, "vite config missing", fix="add resolve.alias for @ and assets")
    ok = "alias" in cfg
    return WebCheck("aliases", ok, "aliases present" if ok else "missing", fix="add resolve.alias (e.g. '@': '/src')")


def run_web_doctor(base: Path = Path.cwd(), port: int = 5173) -> Dict[str, object]:
    base = base.resolve()
    checks: List[WebCheck] = []
    checks.append(check_node())
    checks.append(check_package_manager(base))
    checks.extend(check_env_files(base))
    checks.append(check_port_free(port))
    checks.append(check_build_script(base))
    checks.append(check_vite_proxy(base))
    checks.append(check_vite_cors(base))
    checks.append(check_vite_aliases(base))
    ok = all(c.ok for c in checks)
    return {"ok": ok, "checks": [c.__dict__ for c in checks], "cwd": str(base)}
