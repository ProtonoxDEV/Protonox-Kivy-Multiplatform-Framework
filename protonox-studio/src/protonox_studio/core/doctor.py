from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    fix: str | None = None


def _bool(result: bool) -> str:
    return "OK" if result else "FIX"


def _check_module(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def check_watchdog() -> CheckResult:
    ok = _check_module("watchdog.observers")
    return CheckResult("watchdog", ok, _bool(ok), fix="pip install watchdog" if not ok else None)


def check_pyjnius() -> CheckResult:
    ok = _check_module("jnius")
    return CheckResult("pyjnius", ok, _bool(ok), fix="pip install pyjnius" if not ok else None)


def check_video_backend_desktop() -> CheckResult:
    ok_ffpy = _check_module("ffpyplayer.player")
    ok_vlc = _check_module("vlc")
    ok = ok_ffpy or ok_vlc
    fix = "pip install ffpyplayer" if not ok else None
    return CheckResult("video-backend-desktop", ok, "ffpyplayer or vlc", fix=fix)


def check_assets_layout(base: Path = Path.cwd()) -> List[CheckResult]:
    assets_root = base / "protobots" / "assets"
    presets = assets_root / "presets.yaml"
    results = [
        CheckResult(
            "assets-root",
            assets_root.exists(),
            str(assets_root),
            fix=f"mkdir -p {assets_root}" if not assets_root.exists() else None,
        ),
        CheckResult(
            "assets-presets",
            presets.exists(),
            str(presets),
            fix=f"cp kivy/protonox_ext/assets/presets.yaml {presets}" if not presets.exists() else None,
        ),
    ]
    return results


def check_kv_block(base: Path = Path.cwd()) -> CheckResult:
    marker = "PROTONOX_STUDIO:BEGIN"
    found = False
    for kv in base.rglob("*.kv"):
        try:
            if marker in kv.read_text(encoding="utf-8", errors="ignore"):
                found = True
                break
        except Exception:
            continue
    return CheckResult(
        "kv-managed-block",
        found,
        "block present" if found else "missing",
        fix="Add managed block with PROTONOX_STUDIO:BEGIN/END",
    )


def check_protonox_video_lifecycle() -> CheckResult:
    try:
        from kivy.protonox_ext.media.protonox_video import ProtonoxVideo  # type: ignore

        ok = hasattr(ProtonoxVideo, "on_unmount") and hasattr(ProtonoxVideo, "on_mount")
        return CheckResult(
            "protonox-video-lifecycle", ok, _bool(ok), fix="Update protonox-kivy-version" if not ok else None
        )
    except Exception:
        return CheckResult(
            "protonox-video-lifecycle", False, "import failed", fix="Install/upgrade protonox-kivy-version"
        )


def run_doctor(android: bool = False, base: Path | None = None) -> Dict[str, object]:
    base = base or Path.cwd()
    results: List[CheckResult] = []
    results.append(check_watchdog())
    if android:
        results.append(check_pyjnius())
    else:
        results.append(check_video_backend_desktop())
    results.extend(check_assets_layout(base))
    results.append(check_kv_block(base))
    results.append(check_protonox_video_lifecycle())

    ok = all(r.ok for r in results)
    return {
        "ok": ok,
        "checks": [r.__dict__ for r in results],
    }


__all__ = [
    "CheckResult",
    "run_doctor",
    "check_watchdog",
    "check_pyjnius",
    "check_video_backend_desktop",
    "check_assets_layout",
    "check_kv_block",
    "check_protonox_video_lifecycle",
]
