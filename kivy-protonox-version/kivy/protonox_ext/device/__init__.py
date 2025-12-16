"""Opt-in Protonox device layer (Android-first, non-invasive).

The device layer is designed to provide modern Android bridges (CameraX, AudioRecord,
SAF, Bluetooth) without altering the Kivy core. All helpers are lazy, optional,
and guarded by environment flags so production apps remain unaffected unless the
developer opts in explicitly.
"""
from .android import (
    DeviceLayerError,
    bluetooth_route_snapshot,
    capabilities,
    connectivity_snapshot,
    diagnostics_snapshot,
    ensure_permissions,
    fused_location_snapshot,
    open_camerax,
    start_audio_capture,
    storage_handle,
)
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

__all__ = [
    "AudioRequest",
    "CameraRequest",
    "ConnectivitySnapshot",
    "DeviceCapabilities",
    "DeviceLayerError",
    "LocationRequest",
    "PermissionResult",
    "SensorSnapshot",
    "StorageHandle",
    "bluetooth_route_snapshot",
    "capabilities",
    "connectivity_snapshot",
    "diagnostics_snapshot",
    "ensure_permissions",
    "fused_location_snapshot",
    "open_camerax",
    "start_audio_capture",
    "storage_handle",
]
