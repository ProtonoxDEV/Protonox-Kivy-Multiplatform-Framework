"""Android compatibility helpers (dev-only, opt-in).

These helpers provide non-invasive audits for modern Android releases without
changing the core Kivy runtime. They are designed to surface permission and
lifecycle risks introduced in Android 13–15 so developers can react before
shipping. No commands here mutate device state unless explicitly requested.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

from kivy.logger import Logger

from .adb import ADBError, _run, audit_android15, device_props, ensure_adb


_RUNTIME_PERMS = [
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_MEDIA_AUDIO",
]


@dataclass
class PermissionStatus:
    name: str
    granted: bool
    reason: Optional[str] = None


@dataclass
class AndroidCompatReport:
    device_sdk: Optional[int] = None
    target_sdk: Optional[int] = None
    permissions: List[PermissionStatus] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "device_sdk": self.device_sdk,
                "target_sdk": self.target_sdk,
                "permissions": [status.__dict__ for status in self.permissions],
                "warnings": self.warnings,
                "details": self.details,
            },
            indent=2,
        )


def audit_runtime_compat(package: str, adb_path: str = "adb", serial: Optional[str] = None) -> AndroidCompatReport:
    """Audit Android 13–15 compatibility for a package without mutating state."""

    adb_bin = ensure_adb(adb_path)
    props = device_props(serial=serial, adb_path=adb_bin)
    device_sdk = int(props.get("ro.build.version.sdk", "0") or 0)
    report = AndroidCompatReport(device_sdk=device_sdk, details={"props": props})

    audit15 = audit_android15(package=package, adb_path=adb_bin, serial=serial)
    report.warnings.extend(audit15.get("warnings", []))
    report.details.update(audit15.get("details", {}))
    report.target_sdk = audit15.get("details", {}).get("targetSdkVersion")

    perm_status: List[PermissionStatus] = []
    try:
        cmd = [adb_bin]
        if serial:
            cmd += ["-s", serial]
        cmd += ["shell", "dumpsys", "package", package]
        dumpsys = _run(cmd, timeout=10).stdout
        for perm in _RUNTIME_PERMS:
            found_line = next((ln for ln in dumpsys.splitlines() if perm in ln), None)
            granted = found_line and ("granted=true" in found_line or "=granted" in found_line)
            perm_status.append(PermissionStatus(name=perm, granted=bool(granted)))
            if not granted:
                report.warnings.append(f"Runtime permission missing: {perm}")
    except ADBError as exc:
        Logger.warning("[ADB] permission audit failed: %s", exc)
        report.warnings.append(f"Permission audit failed: {exc}")

    report.permissions = perm_status
    return report


__all__ = ["AndroidCompatReport", "PermissionStatus", "audit_runtime_compat"]
