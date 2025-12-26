"""Minimal ADB bridge helpers (opt-in, dev-only).

This module keeps all Android plumbing outside the Kivy core and aims to make
smoke-testing a Kivy app on a connected device less painful without rebuilding
from scratch when only KV or Python code changed.

The helpers are intentionally thin wrappers around `adb` and avoid altering any
runtime behaviour unless explicitly imported and called.
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional

from kivy.logger import Logger


class ADBError(RuntimeError):
    """Raised when an adb command fails."""


@dataclass
class Device:
    """Lightweight representation of an attached Android device."""

    serial: str
    status: str
    model: Optional[str] = None
    transport: str = "unknown"
    connection: str = "unknown"  # usb | wifi | emulator


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


def _is_wsl() -> bool:
    try:
        with open("/proc/version", "r", encoding="utf-8") as fd:
            return "microsoft" in fd.read().lower()
    except FileNotFoundError:
        return False


def _normalize_windows_path_for_wsl(path: str) -> str:
    # Convert paths like C:\Android\platform-tools\adb.exe to /mnt/c/Android/platform-tools/adb.exe
    if ":\\" in path:
        drive, rest = path.split(":\\", 1)
        rest = rest.replace('\\\\', '/').replace('\\', '/')
        return f"/mnt/{drive.lower()}/{rest}"
    return path


def _resolve_adb_candidates(adb_path: str = "adb") -> List[str]:
    candidates: List[str] = []
    candidates.append(adb_path)

    env_override = shlex.split(os.environ.get("PROTONOX_ADB_PATH", "")) if "PROTONOX_ADB_PATH" in os.environ else []
    candidates.extend(env_override)

    if _is_wsl():
        common = [
            r"C:\Windows\System32\adb.exe",
            r"C:\Program Files\Android\Android Studio\platform-tools\adb.exe",
            r"C:\Android\platform-tools\adb.exe",
        ]
        candidates.extend([_normalize_windows_path_for_wsl(p) for p in common])

    # Deduplicate while preserving order
    seen = set()
    unique: List[str] = []
    for cand in candidates:
        if cand and cand not in seen:
            seen.add(cand)
            unique.append(cand)
    return unique


def ensure_adb(adb_path: str = "adb") -> str:
    """Validate that adb is reachable and return its resolved path.

    The resolver prefers WSL→Windows bridges when running under WSL and falls
    back to the default `adb` in PATH. An explicit PROTONOX_ADB_PATH can supply
    multiple candidates (space-separated) to try first.
    """

    for candidate in _resolve_adb_candidates(adb_path):
        binary = shutil.which(candidate) if not candidate.endswith(".exe") else candidate
        if not binary:
            continue
        try:
            proc = _run([binary, "version"], timeout=5)
            Logger.info("[ADB] %s", proc.stdout.strip())
            return binary
        except ADBError:
            continue
    raise ADBError("adb not found; set PROTONOX_ADB_PATH or install platform-tools")


def list_devices(adb_path: str = "adb") -> List[Device]:
    """Return connected devices parsed from `adb devices -l`.

    Adds lightweight transport metadata so callers can prefer wireless over USB
    or emulators when available.
    """

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
        transport = "emulator" if serial.startswith("emulator-") else "device"
        connection = "wifi" if ":" in serial else ("emulator" if transport == "emulator" else "usb")
        devices.append(Device(serial=serial, status=status, model=model, transport=transport, connection=connection))
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


def stream_logcat_structured(
    package: str,
    adb_path: str = "adb",
    extra_filters: Optional[Iterable[str]] = None,
    include_gl: bool = True,
    emit: Optional[Callable[[dict], None]] = None,
):
    """Yield structured logcat lines for the package and optional GL/SDL warnings.

    If ``emit`` is provided, each structured entry is also forwarded to that
    callback (for example, a ``DiagnosticBus._record`` wrapper). This keeps the
    function backwards compatible while enabling structured log capture for IA
    workflows.
    """

    filters = list(extra_filters or [])
    filters.append(f"{package}:V")
    if include_gl:
        filters.extend(["OpenGLRenderer:W", "Adreno:W", "*:S"])
    cmd = [adb_path, "logcat", "-v", "threadtime"] + filters
    Logger.info("[ADB] structured logcat cmd: %s", shlex.join(cmd))
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
        if not proc.stdout:
            return
        for line in proc.stdout:
            payload = {"raw": line.rstrip("\n"), "ts": time.time(), "source": "logcat"}
            if emit:
                try:
                    emit(payload)
                except Exception:
                    Logger.exception("[ADB] emit failed for structured logcat line")
            yield payload


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


def watch(
    package: str,
    activity: Optional[str] = None,
    adb_path: str = "adb",
    reinstall_apk: Optional[str] = None,
    emit: Optional[Callable[[dict], None]] = None,
) -> ADBSession:
    """Fast dev loop: optional reinstall + activity start + filtered logcat.

    This intentionally avoids touching the Kivy runtime. It simply orchestrates
    adb so developers can iterate faster without a full rebuild. Call `stop()`
    on the returned session to end the log stream.
    """

    adb_bin = ensure_adb(adb_path)
    wifi_first = os.environ.get("PROTONOX_ADB_WIRELESS_FIRST", "1").lower() in {"1", "true", "yes"}
    devices = list_devices(adb_path=adb_bin)
    if (not devices or wifi_first) and wifi_first:
        try:
            devices = connect_wireless(adb_path=adb_bin)
        except ADBError as exc:
            Logger.warning("[ADB] wireless connect attempt failed: %s", exc)
    if not devices:
        raise ADBError("No devices/emulators detected via adb")

    if reinstall_apk:
        install_apk(reinstall_apk, adb_path=adb_bin, reinstall=True)

    run_app(package=package, activity=activity, adb_path=adb_bin)
    session = stream_logcat(
        package=package,
        adb_path=adb_bin,
        extra_filters=["*:S"],
    )
    if emit:
        # fan-out structured logcat in a background thread without altering the
        # raw stream returned by ``stream_logcat``
        import threading

        def _pump():
            for event in stream_logcat_structured(package=package, adb_path=adb_bin, emit=emit):
                if not event:
                    break

        threading.Thread(target=_pump, daemon=True).start()
    Logger.info("[ADB] watch started for %s (%s)", package, activity or "auto")
    return session


def auto_select_device(adb_path: str = "adb") -> Device:
    """Prefer wireless → USB → emulator, raising when none are available."""

    adb_bin = ensure_adb(adb_path)
    devices = list_devices(adb_path=adb_bin)
    if not devices:
        raise ADBError("No devices/emulators detected via adb")
    devices_sorted = sorted(
        devices,
        key=lambda d: (0 if d.connection == "wifi" else 1 if d.connection == "usb" else 2, d.serial),
    )
    return devices_sorted[0]


def enable_wireless(serial: Optional[str] = None, port: int = 5555, adb_path: str = "adb") -> Optional[str]:
    """Switch a USB-connected device into wireless debugging mode.

    Returns the suggested host:port target to reconnect to. This is a thin
    wrapper around ``adb tcpip`` and intentionally avoids persisting any
    configuration.
    """

    adb_bin = ensure_adb(adb_path)
    base_cmd = [adb_bin]
    if serial:
        base_cmd += ["-s", serial]
    _run(base_cmd + ["tcpip", str(port)])
    props = device_props(serial=serial, adb_path=adb_bin)
    host = props.get("dhcp.wlan0.ipaddress") or props.get("dhcp.wlan0.ipaddress", "")
    return f"{host}:{port}" if host else None


def connect_wireless(target: Optional[str] = None, adb_path: str = "adb") -> List[Device]:
    """Attempt wireless debugging; prefers explicit target or cached mdns devices.

    If target is not provided, this will try to reconnect to already-known IP
    based devices. The helper is intentionally conservative and will not block
    indefinitely.
    """

    adb_bin = ensure_adb(adb_path)
    targets = []
    if target:
        targets.append(target)
    env_target = os.environ.get("PROTONOX_ADB_WIRELESS_HOST")
    if env_target and env_target not in targets:
        targets.append(env_target)

    # mdns auto-discovery if supported
    try:
        features = _run([adb_bin, "host-features"], timeout=5).stdout
        if "mdns" in features:
            mdns = _run([adb_bin, "mdns", "services"], timeout=5).stdout
            for line in mdns.splitlines():
                if "_adb-tls-pairing" in line or "_adb._tcp" in line:
                    parts = line.split()
                    if parts:
                        host = parts[-1]
                        if host not in targets:
                            targets.append(host)
    except Exception:
        pass

    for host in targets:
        try:
            Logger.info("[ADB] attempting wireless connect to %s", host)
            _run([adb_bin, "connect", host], timeout=10)
        except ADBError as exc:
            Logger.warning("[ADB] wireless connect failed for %s: %s", host, exc)

    return list_devices(adb_path=adb_bin)


def normalize_path_for_push(path: str) -> str:
    """Normalize host paths for adb push when running under WSL."""

    if _is_wsl():
        return _normalize_windows_path_for_wsl(path)
    return path


def audit_android15(package: str, adb_path: str = "adb", serial: Optional[str] = None) -> dict:
    """Collect warnings for Android 15 (API 35) compatibility.

    The audit is non-invasive and reports targetSdkVersion, runtime permission
    expectations (POST_NOTIFICATIONS, READ_MEDIA_*), and device SDK level when
    available.
    """

    adb_bin = ensure_adb(adb_path)
    base_cmd = [adb_bin]
    if serial:
        base_cmd += ["-s", serial]
    warnings = []
    props = device_props(serial=serial, adb_path=adb_bin)
    sdk = int(props.get("ro.build.version.sdk", "0") or 0)
    if sdk and sdk < 35:
        warnings.append(f"Device SDK {sdk} < 35; enable an API 35 emulator or device")
    details = {"device_sdk": sdk, "props": props}

    try:
        dumpsys = _run(base_cmd + ["shell", "dumpsys", "package", package], timeout=10).stdout
        for line in dumpsys.splitlines():
            line = line.strip()
            if line.startswith("targetSdk"):
                try:
                    target = int(line.split("=", 1)[1])
                    details["targetSdkVersion"] = target
                    if target < 35:
                        warnings.append("targetSdkVersion < 35; update build config for Android 15")
                except Exception:
                    continue
            if "permission" in line and any(p in line for p in ["POST_NOTIFICATIONS", "READ_MEDIA_IMAGES", "READ_MEDIA_VIDEO", "READ_MEDIA_AUDIO"]):
                if "=granted" not in line and "granted=true" not in line:
                    warnings.append(f"Runtime permission not granted: {line}")
    except ADBError as exc:
        warnings.append(f"dumpsys package failed: {exc}")

    return {"warnings": warnings, "details": details}


__all__ = [
    "ADBError",
    "ADBSession",
    "Device",
    "capture_bugreport",
    "device_props",
    "ensure_adb",
    "enable_wireless",
    "install_apk",
    "auto_select_device",
    "audit_android15",
    "connect_wireless",
    "list_devices",
    "normalize_path_for_push",
    "push_reload",
    "run_app",
    "stream_logcat",
    "stream_logcat_structured",
    "uninstall",
    "watch",
]
