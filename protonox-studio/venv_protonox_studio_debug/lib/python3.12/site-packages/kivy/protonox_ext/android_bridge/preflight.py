"""Environment validation helpers for Android tooling (opt-in, dev-only)."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional

from kivy.logger import Logger


@dataclass
class AndroidPreflightResult:
    ok: bool
    findings: List[str]
    details: Dict[str, str]

    def as_dict(self) -> Dict[str, object]:
        return {"ok": self.ok, "findings": self.findings, "details": self.details}


def _check_cmd(cmd: str, args: list[str]) -> Optional[str]:
    binary = shutil.which(cmd)
    if not binary:
        return None
    try:
        proc = subprocess.run([binary, *args], capture_output=True, text=True, timeout=10)
        if proc.returncode != 0:
            return None
        return proc.stdout.strip() or proc.stderr.strip()
    except Exception:
        return None


def android_preflight(adb_path: str = "adb") -> AndroidPreflightResult:
    """Validate minimal Android tooling presence without mutating anything."""

    findings: List[str] = []
    details: Dict[str, str] = {}

    adb_bin = shutil.which(adb_path)
    if not adb_bin:
        findings.append("adb no encontrado; instala platform-tools o monta el SDK en el contenedor")
    else:
        details["adb"] = adb_bin
        version = _check_cmd(adb_bin, ["version"])
        if version:
            details["adb_version"] = version.splitlines()[0]

    java_home = shutil.which("java")
    if java_home:
        details["java"] = java_home
    else:
        findings.append("Java (JDK) no encontrado en PATH; requerido para buildozer/gradle")

    for var in ["ANDROID_HOME", "ANDROID_SDK_ROOT"]:
        value = os.environ.get(var)
        if value:
            details[var] = value
        else:
            findings.append(f"Variable {var} no definida (requerida para buildozer/adb en contenedor)")

    ok = len(findings) == 0
    if ok:
        Logger.info("[ANDROID_PREFLIGHT] Entorno Android válido: %s", details)
    else:
        Logger.warning("[ANDROID_PREFLIGHT] Faltan dependencias: %s", "; ".join(findings))

    return AndroidPreflightResult(ok=ok, findings=findings, details=details)


__all__ = ["AndroidPreflightResult", "android_preflight"]
