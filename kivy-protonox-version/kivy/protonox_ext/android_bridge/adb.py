"""Minimal ADB bridge helpers (opt-in, dev-only).

This module keeps all Android plumbing outside the Kivy core and aims to make
smoke-testing a Kivy app on a connected device less painful without rebuilding
from scratch when only KV or Python code changed.

The helpers are intentionally thin wrappers around `adb` and avoid altering any
runtime behaviour unless explicitly imported and called.
"""
from __future__ import annotations

import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from kivy.logger import Logger


class ADBError(RuntimeError):
    """Raised when an adb command fails."""


@dataclass
class Device:
    """Lightweight representation of an attached Android device."""

    serial: str
    status: str
    model: Optional[str] = None


@dataclass
class ADBSession:
    """Manage logcat streaming for a single app session."""

    package: str
    process: subprocess.Popen

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()


def _run(cmd: List[str], timeout: int = 15) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - simple passthrough
        raise ADBError(exc.stderr.strip() or exc.stdout.strip() or str(exc)) from exc
    except FileNotFoundError as exc:  # pragma: no cover - adb missing
        raise ADBError("adb not found; ensure Android platform tools are installed") from exc


def ensure_adb(adb_path: str = "adb") -> str:
    """Validate that adb is reachable and return its resolved path."""

    proc = _run([adb_path, "version"], timeout=5)
    Logger.info("[ADB] %s", proc.stdout.strip())
    return adb_path


def list_devices(adb_path: str = "adb") -> List[Device]:
    """Return connected devices parsed from `adb devices -l`."""

    proc = _run([adb_path, "devices", "-l"], timeout=5)
    devices: List[Device] = []
    for line in proc.stdout.splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split()
        serial, status = parts[0], parts[1]
        model = None
        for part in parts[2:]:
            if part.startswith("model:"):
                model = part.split(":", 1)[1]
                break
        devices.append(Device(serial=serial, status=status, model=model))
    return devices


def install_apk(apk_path: str, adb_path: str = "adb", reinstall: bool = True) -> None:
    """Install or reinstall an APK onto the default device."""

    apk = Path(apk_path)
    if not apk.exists():
        raise ADBError(f"APK not found: {apk}")
    cmd = [adb_path, "install"]
    if reinstall:
        cmd.append("-r")
    cmd.append(str(apk))
    proc = _run(cmd, timeout=120)
    Logger.info("[ADB] install output: %s", proc.stdout.strip())


def uninstall(package: str, adb_path: str = "adb") -> None:
    proc = _run([adb_path, "uninstall", package], timeout=30)
    Logger.info("[ADB] uninstall output: %s", proc.stdout.strip())


def run_app(package: str, activity: Optional[str] = None, adb_path: str = "adb") -> None:
    """Start an app activity (defaults to `package/.MainActivity`)."""

    target = activity or f"{package}/.MainActivity"
    proc = _run([adb_path, "shell", "am", "start", "-n", target], timeout=10)
    Logger.info("[ADB] start output: %s", proc.stdout.strip())


def stream_logcat(package: str, adb_path: str = "adb", extra_filters: Optional[Iterable[str]] = None) -> ADBSession:
    """Stream logcat filtered for a specific package. Caller must stop()."""

    filters = list(extra_filters or [])
    filters.append(f"{package}:V")
    cmd = [adb_path, "logcat", "-v", "threadtime"] + filters
    Logger.info("[ADB] logcat cmd: %s", shlex.join(cmd))
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return ADBSession(package=package, process=process)


def push_reload(apk_path: str, package: str, activity: Optional[str] = None, adb_path: str = "adb") -> None:
    """Incremental dev loop: reinstall APK and restart activity."""

    install_apk(apk_path, adb_path=adb_path, reinstall=True)
    run_app(package=package, activity=activity, adb_path=adb_path)


def capture_bugreport(adb_path: str = "adb", out_path: Optional[str] = None) -> Path:
    """Capture a bugreport to a file for diagnostics."""

    timestamp = int(time.time())
    target = Path(out_path) if out_path else Path(f"bugreport_{timestamp}.zip")
    proc = _run([adb_path, "bugreport", str(target)], timeout=120)
    Logger.info("[ADB] bugreport saved to %s", target)
    if proc.stdout.strip():
        Logger.debug("[ADB] bugreport output: %s", proc.stdout.strip())
    return target


def device_props(serial: Optional[str] = None, adb_path: str = "adb") -> dict:
    """Return selected device properties as a dictionary."""

    cmd = [adb_path]
    if serial:
        cmd += ["-s", serial]
    cmd += ["shell", "getprop"]
    proc = _run(cmd, timeout=10)
    props: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if not line.startswith("["):
            continue
        try:
            key, value = line.split("]:", 1)
            props[key.strip("[]")] = value.strip().strip("[]")
        except ValueError:
            continue
    return props


def watch(package: str, activity: Optional[str] = None, adb_path: str = "adb", reinstall_apk: Optional[str] = None) -> ADBSession:
    """Fast dev loop: optional reinstall + activity start + filtered logcat.

    This intentionally avoids touching the Kivy runtime. It simply orchestrates
    adb so developers can iterate faster without a full rebuild. Call `stop()`
    on the returned session to end the log stream.
    """

    ensure_adb(adb_path)
    devices = list_devices(adb_path=adb_path)
    if not devices:
        raise ADBError("No devices/emulators detected via adb")

    if reinstall_apk:
        install_apk(reinstall_apk, adb_path=adb_path, reinstall=True)

    run_app(package=package, activity=activity, adb_path=adb_path)
    session = stream_logcat(package=package, adb_path=adb_path, extra_filters=["*:S"])
    Logger.info("[ADB] watch started for %s (%s)", package, activity or "auto")
    return session


__all__ = [
    "ADBError",
    "ADBSession",
    "Device",
    "capture_bugreport",
    "device_props",
    "ensure_adb",
    "install_apk",
    "list_devices",
    "push_reload",
    "run_app",
    "stream_logcat",
    "uninstall",
    "watch",
]
