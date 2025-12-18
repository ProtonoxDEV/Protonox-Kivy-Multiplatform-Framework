"""Protonox extensions for the Kivy 2.3.1 fork.

All additions are opt-in and live outside the core to preserve backward
compatibility. Production apps see no behavioural changes unless the developer
explicitly imports and enables these helpers.
"""

from .android_bridge import adb
from .compat import (COMPAT_WARNINGS, CompatReport, CompatWarning,
                     auto_enable_if_fork, emit_all_warnings,
                     enable_diagnostics, enable_profile, enable_protonox_ui,
                     enable_safe_mode, is_protonox_runtime, register_shim)
from .device import (AudioRequest, CameraRequest, ConnectivitySnapshot,
                     DeviceCapabilities, DeviceLayerError, LocationRequest,
                     PermissionResult, SensorSnapshot, StorageHandle,
                     bluetooth_route_snapshot, capabilities,
                     connectivity_snapshot, diagnostics_snapshot,
                     ensure_permissions, fused_location_snapshot, open_camerax,
                     start_audio_capture, storage_handle)
from .diagnostics import (BUS_ENABLED, DiagnosticBus, DiagnosticEvent,
                          DiagnosticItem, DiagnosticReport)
from .diagnostics import as_lines as diagnostics_as_lines
from .diagnostics import collect_runtime_diagnostics, get_bus
from .hotreload_plus import hooks
from .inspector import overlay, runtime
from .kv_bridge import compiler, ir
from .layout_engine import antipatterns, fingerprint, health, introspect
from .observability import export_observability
from .telemetry import (collect_layout_report, export_widget_tree,
                        persist_layout_report, safe_export_to_png)
from .ui import emoji
from .visual_state import freeze, png_reference, snapshot
from .web_mapper import dom_bridge
from .wireless_debug import (generate_qr, send_data, send_log, send_touch_event,
                             send_ui_state, start_server, stop_server)

__all__ = [
    "collect_layout_report",
    "export_widget_tree",
    "persist_layout_report",
    "safe_export_to_png",
    "antipatterns",
    "fingerprint",
    "health",
    "introspect",
    "runtime",
    "overlay",
    "compiler",
    "ir",
    "hooks",
    "dom_bridge",
    "png_reference",
    "freeze",
    "snapshot",
    "adb",
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
    "emoji",
    "export_observability",
    "BUS_ENABLED",
    "DiagnosticBus",
    "DiagnosticEvent",
    "DiagnosticItem",
    "DiagnosticReport",
    "diagnostics_as_lines",
    "collect_runtime_diagnostics",
    "get_bus",
    "CompatReport",
    "CompatWarning",
    "COMPAT_WARNINGS",
    "enable_diagnostics",
    "enable_profile",
    "enable_protonox_ui",
    "enable_safe_mode",
    "auto_enable_if_fork",
    "is_protonox_runtime",
    "emit_all_warnings",
    "register_shim",
    "generate_qr",
    "send_data",
    "send_log",
    "send_touch_event",
    "send_ui_state",
    "start_server",
    "stop_server",
]
