"""Android bridge utilities for Protonox (opt-in, dev-only)."""

from .adb import (
    ADBError,
    ADBSession,
    Device,
    audit_android15,
    auto_select_device,
    capture_bugreport,
    connect_wireless,
    device_props,
    enable_wireless,
    ensure_adb,
    install_apk,
    list_devices,
    normalize_path_for_push,
    push_reload,
    run_app,
    stream_logcat,
    stream_logcat_structured,
    uninstall,
    watch,
)
from .bridge_server import BridgeServer
from .compat import AndroidCompatReport, PermissionStatus, audit_runtime_compat
from .preflight import AndroidPreflightResult, android_preflight

__all__ = [
    "ADBError",
    "ADBSession",
    "Device",
    "audit_android15",
    "auto_select_device",
    "capture_bugreport",
    "connect_wireless",
    "enable_wireless",
    "device_props",
    "ensure_adb",
    "install_apk",
    "list_devices",
    "normalize_path_for_push",
    "push_reload",
    "run_app",
    "stream_logcat",
    "stream_logcat_structured",
    "uninstall",
    "watch",
    "BridgeServer",
    "AndroidCompatReport",
    "PermissionStatus",
    "audit_runtime_compat",
    "AndroidPreflightResult",
    "android_preflight",
]
