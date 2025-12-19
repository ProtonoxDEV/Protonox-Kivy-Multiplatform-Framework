"""Opt-in Android device layer using modern platform APIs when available.

This module keeps all platform plumbing outside the Kivy core. It exposes thin
helpers that prefer modern Android stacks (CameraX, AudioRecord, SAF, etc.)
without forcing behaviour on non-Android hosts. All calls are best-effort and
should be gated by callers via the PROTONOX_DEVICE_LAYER flag.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Iterable, List, Optional

from kivy.logger import Logger
from kivy.utils import platform

from .spec import (
    AudioRequest,
    CameraRequest,
    ConnectivitySnapshot,
    DeviceCapabilities,
    LocationRequest,
    PermissionResult,
    SensorSnapshot,
    StorageHandle,
)


class DeviceLayerError(RuntimeError):
    """Raised when the device layer cannot satisfy a request."""


def _is_android() -> bool:
    try:
        return platform == "android"
    except Exception:  # pragma: no cover - platform helper should exist
        return False


def _require_android() -> None:
    if not _is_android():
        raise DeviceLayerError("Device layer is Android-only; enable via emulator or device")


def _lazy_autoclass(name: str):  # pragma: no cover - thin lazy accessor
    try:
        from jnius import autoclass
    except ImportError as exc:  # pragma: no cover - jnius missing
        raise DeviceLayerError("pyjnius is required on Android for device access") from exc
    return autoclass(name)


def ensure_permissions(perms: Iterable[str]) -> PermissionResult:
    """Request runtime permissions in a safe, idempotent way."""

    _require_android()
    granted: List[str] = []
    denied: List[str] = []

    try:
        from android.permissions import check_permission, request_permissions  # type: ignore
    except Exception as exc:  # pragma: no cover - permissions module missing
        raise DeviceLayerError("android.permissions not available; ensure python-for-android context") from exc

    perms = list(perms)
    missing = [p for p in perms if not check_permission(p)]
    if missing:
        Logger.info("[DEVICE] Requesting permissions: %s", ", ".join(missing))
        request_permissions(missing)
    for perm in perms:
        if check_permission(perm):
            granted.append(perm)
        else:
            denied.append(perm)
    return PermissionResult(granted=granted, denied=denied)


def capabilities() -> DeviceCapabilities:
    """Detect baseline device capabilities via reflection and permissions."""

    caps = DeviceCapabilities()
    if not _is_android():
        return caps

    try:
        Build = _lazy_autoclass("android.os.Build")
        caps.api_level = int(Build.VERSION.SDK)  # type: ignore[attr-defined]
    except Exception:
        caps.api_level = None

    try:
        PackageManager = _lazy_autoclass("android.content.pm.PackageManager")
        PythonActivity = _lazy_autoclass("org.kivy.android.PythonActivity")
        app = PythonActivity.mActivity
        pm = app.getPackageManager()
        caps.camera = pm.hasSystemFeature(PackageManager.FEATURE_CAMERA_ANY)
        caps.microphone = pm.hasSystemFeature(PackageManager.FEATURE_MICROPHONE)
        caps.bluetooth = pm.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH)
        caps.gps = pm.hasSystemFeature(PackageManager.FEATURE_LOCATION_GPS)
        caps.network = True
        caps.storage = True
    except Exception as exc:  # pragma: no cover - reflection errors
        Logger.warning("[DEVICE] Capability probe failed: %s", exc)
    return caps


def open_camerax(request: Optional[CameraRequest] = None) -> str:
    """Prepare a CameraX provider session and return a diagnostic handle string.

    This does not stream frames by itself; it validates that CameraX plumbing is
    reachable. The handle can be used by downstream layers to attach surfaces.
    """

    _require_android()
    request = request or CameraRequest()
    try:
        ProcessCameraProvider = _lazy_autoclass("androidx.camera.lifecycle.ProcessCameraProvider")
        CameraSelector = _lazy_autoclass("androidx.camera.core.CameraSelector")
        PythonActivity = _lazy_autoclass("org.kivy.android.PythonActivity")

        app = PythonActivity.mActivity
        provider_future = ProcessCameraProvider.getInstance(app)
        provider = provider_future.get()
        lens = CameraSelector.DEFAULT_BACK_CAMERA if request.lens_facing == "back" else CameraSelector.DEFAULT_FRONT_CAMERA
        provider.bindToLifecycle(app, lens)
        handle = {
            "lens_facing": request.lens_facing,
            "resolution": request.resolution,
            "fps": request.fps,
            "autofocus": request.autofocus,
            "exposure": request.exposure_compensation,
        }
        Logger.info("[DEVICE] CameraX ready (%s)", json.dumps(handle))
        return json.dumps(handle)
    except Exception as exc:  # pragma: no cover - runtime reflection only
        raise DeviceLayerError(f"CameraX setup failed: {exc}") from exc


def start_audio_capture(request: Optional[AudioRequest] = None) -> str:
    """Configure AudioRecord with modern defaults and return a descriptor string."""

    _require_android()
    request = request or AudioRequest()
    try:
        AudioRecord = _lazy_autoclass("android.media.AudioRecord")
        MediaRecorder = _lazy_autoclass("android.media.MediaRecorder")
        AudioFormat = _lazy_autoclass("android.media.AudioFormat")

        channel_config = AudioFormat.CHANNEL_IN_MONO
        encoding = AudioFormat.ENCODING_PCM_16BIT
        buffer_size = AudioRecord.getMinBufferSize(request.sample_rate, channel_config, encoding)
        handle = {
            "sample_rate": request.sample_rate,
            "noise_suppression": request.noise_suppression,
            "buffer_size": int(buffer_size),
        }
        Logger.info("[DEVICE] AudioRecord configured (%s)", json.dumps(handle))
        return json.dumps(handle)
    except Exception as exc:  # pragma: no cover
        raise DeviceLayerError(f"AudioRecord setup failed: {exc}") from exc


def fused_location_snapshot(request: Optional[LocationRequest] = None) -> SensorSnapshot:
    """Best-effort fused location snapshot using modern providers."""

    _require_android()
    request = request or LocationRequest()
    try:
        PythonActivity = _lazy_autoclass("org.kivy.android.PythonActivity")
        app = PythonActivity.mActivity
        Context = _lazy_autoclass("android.content.Context")
        location_mgr = app.getSystemService(Context.LOCATION_SERVICE)
        provider = location_mgr.getBestProvider(_lazy_autoclass("android.location.Criteria")(), True)
        loc = location_mgr.getLastKnownLocation(provider)
        if loc is None:
            return SensorSnapshot()
        return SensorSnapshot(
            location=(loc.getLatitude(), loc.getLongitude()),
            altitude=loc.getAltitude(),
            accuracy=loc.getAccuracy(),
        )
    except Exception as exc:  # pragma: no cover
        raise DeviceLayerError(f"Location snapshot failed: {exc}") from exc


def connectivity_snapshot() -> ConnectivitySnapshot:
    """Return a minimal connectivity report for diagnostics."""

    if not _is_android():
        return ConnectivitySnapshot(is_connected=False, transport="unknown")
    try:
        PythonActivity = _lazy_autoclass("org.kivy.android.PythonActivity")
        Context = _lazy_autoclass("android.content.Context")
        ConnectivityManager = _lazy_autoclass("android.net.ConnectivityManager")

        app = PythonActivity.mActivity
        cm = app.getSystemService(Context.CONNECTIVITY_SERVICE)
        active = cm.getActiveNetworkInfo()
        if not active:
            return ConnectivitySnapshot(is_connected=False, transport="unknown")
        transport = "wifi" if active.getType() == ConnectivityManager.TYPE_WIFI else "cellular"
        ssid = None
        if transport == "wifi":
            wifi = app.getApplicationContext().getSystemService(Context.WIFI_SERVICE)
            info = wifi.getConnectionInfo()
            ssid = info.getSSID() if info else None
        return ConnectivitySnapshot(is_connected=active.isConnected(), transport=transport, ssid=ssid)
    except Exception as exc:  # pragma: no cover
        raise DeviceLayerError(f"Connectivity probe failed: {exc}") from exc


def storage_handle(description: str = "") -> StorageHandle:
    """Open a Storage Access Framework document picker request (best-effort)."""

    _require_android()
    try:
        StorageManager = _lazy_autoclass("android.os.storage.StorageManager")
        PythonActivity = _lazy_autoclass("org.kivy.android.PythonActivity")
        app = PythonActivity.mActivity
        sm = app.getSystemService("storage")
        uri = None
        if isinstance(sm, StorageManager):
            volumes = sm.getStorageVolumes()
            if volumes and len(volumes) > 0:
                uri = str(volumes[0].createOpenDocumentTreeIntent().getData())
        return StorageHandle(uri=uri, description=description)
    except Exception as exc:  # pragma: no cover
        raise DeviceLayerError(f"Storage handle request failed: {exc}") from exc


def bluetooth_route_snapshot() -> dict:
    """Return a minimal snapshot of active Bluetooth audio routes."""

    _require_android()
    try:
        BluetoothAdapter = _lazy_autoclass("android.bluetooth.BluetoothAdapter")
        adapter = BluetoothAdapter.getDefaultAdapter()
        if adapter is None:
            return {"enabled": False, "devices": []}
        devices = []
        bonded = adapter.getBondedDevices() or []
        for dev in bonded:
            devices.append({
                "name": dev.getName(),
                "address": dev.getAddress(),
            })
        return {"enabled": adapter.isEnabled(), "devices": devices}
    except Exception as exc:  # pragma: no cover
        raise DeviceLayerError(f"Bluetooth probe failed: {exc}") from exc


def diagnostics_snapshot() -> dict:
    """Aggregate a diagnostics payload for Studio/CI consumers."""

    payload = {
        "capabilities": capabilities().as_dict(),
        "connectivity": None,
    }
    try:
        payload["connectivity"] = asdict(connectivity_snapshot())
    except Exception as exc:  # pragma: no cover
        payload["connectivity"] = {"error": str(exc)}
    return payload
