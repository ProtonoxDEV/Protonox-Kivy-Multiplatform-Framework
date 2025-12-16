from __future__ import annotations

import platform
import shutil
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Check:
    name: str
    ok: bool
    detail: str
    fix: str | None = None


def _bool(ok: bool) -> str:
    return "OK" if ok else "FIX"


def check_python() -> Check:
    ver = platform.python_version()
    ok = tuple(map(int, ver.split("."))) >= (3, 10)
    return Check("python", ok, ver, fix="Usa Python 3.10+")


def check_pillow() -> Check:
    try:
        import PIL  # noqa: F401

        return Check("pillow", True, "import ok")
    except Exception:
        return Check("pillow", False, "no import", fix="pip install pillow")


def check_watchdog() -> Check:
    try:
        import watchdog  # noqa: F401

        return Check("watchdog", True, "import ok")
    except Exception:
        return Check("watchdog", False, "no import", fix="pip install watchdog")


def check_ffmpeg() -> Check:
    path = shutil.which("ffmpeg")
    return Check("ffmpeg", bool(path), path or "missing", fix="instala ffmpeg en PATH")


def run_kivy_doctor() -> Dict[str, object]:
    checks: List[Check] = [
        check_python(),
        check_pillow(),
        check_watchdog(),
        check_ffmpeg(),
    ]
    ok = all(c.ok for c in checks)
    return {"ok": ok, "checks": [c.__dict__ for c in checks]}
