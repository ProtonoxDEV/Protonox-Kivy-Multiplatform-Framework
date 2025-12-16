# Protonox Device Layer (Android-first, opt-in)

This layer exposes modern Android capabilities (CameraX, AudioRecord, Storage
Access Framework, Bluetooth, fused location, connectivity snapshots) without
altering core Kivy behaviour. It is **entirely opt-in** and guarded by
`PROTONOX_DEVICE_LAYER=1` (or explicit imports) so existing apps remain stable.

## Goals
- Prefer modern Android stacks (CameraX, AudioRecord, SAF) over legacy Kivy
  wrappers.
- Provide structured results (JSON-friendly) for Protonox Studio / CI while
  keeping runtime side-effect free by default.
- Keep everything outside the core so upstream Kivy APIs and widgets remain
  untouched.

## Activation
```
PROTONOX_DEVICE_LAYER=1 python main.py
```
Or explicitly import the helpers:
```python
from kivy_protonox import enable
from kivy.protonox_ext.device import (
    capabilities, ensure_permissions, open_camerax, start_audio_capture,
    fused_location_snapshot, connectivity_snapshot, diagnostics_snapshot,
    bluetooth_route_snapshot, storage_handle,
)

enable()  # activates Protonox profiles if desired
```

## Capabilities
- **CameraX probe**: `open_camerax()` validates modern camera plumbing and
  returns a handle describing the requested session.
- **AudioRecord setup**: `start_audio_capture()` prepares AudioRecord with
  sane defaults (48 kHz, NS on) and returns a diagnostic descriptor.
- **Permissions helper**: `ensure_permissions(["android.permission.CAMERA", ...])`
  requests runtime permissions safely.
- **Connectivity snapshot**: `connectivity_snapshot()` reports Wi‑Fi/cellular
  state and SSID for diagnostics.
- **Location snapshot**: `fused_location_snapshot()` fetches the best-known
  location without forcing continuous tracking.
- **Bluetooth routes**: `bluetooth_route_snapshot()` lists bonded devices and
  adapter status.
- **Storage Access Framework**: `storage_handle()` prepares an SAF intent
  descriptor without touching user storage directly.
- **Diagnostics aggregate**: `diagnostics_snapshot()` bundles capabilities and
  connectivity for Protonox Studio consumption.

## Safety / Compatibility
- No behaviour changes unless the developer opts in.
- Lazy imports ensure non-Android hosts simply get capability defaults.
- Any reflection failure surfaces as a `DeviceLayerError` with a clear message
  instead of crashing the app.

## Next steps
- Bind CameraX surfaces and media pipelines once the host app requests them.
- Extend the diagnostics snapshot to include sensor streams when explicitly
  enabled.
- Wire structured device telemetry into Protonox Studio’s AI context bundles.
