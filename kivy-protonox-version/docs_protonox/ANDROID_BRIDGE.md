# Android Bridge (ADB) — Protonox Extensions (opt-in)

Goal: make Android smoke tests and log collection easier without touching the
Kivy core or requiring rebuilds for every KV tweak.

## Capabilities
- Detect and list connected devices (`list_devices`).
- Verify `adb` availability (`ensure_adb`).
- Incremental install/reinstall APKs (`install_apk`, `push_reload`).
- Start activities without rebuilding (`run_app`).
- Filtered logcat streaming for a package (`stream_logcat`).
- Structured logcat stream that can merge GL/SDL warnings (`stream_logcat_structured`).
- Bugreport capture for diagnostics (`capture_bugreport`).
- Read device properties for environment-aware tweaks (`device_props`).
- Environment preflight to fail fast in CI/containers (`android_preflight`).
- Wireless debugging helper with mdns autodiscovery (`connect_wireless`).
- Device selection helper that prefers Wi‑Fi → USB → emulator (`auto_select_device`).
- Android 15 (API 35) audit for targetSdk and runtime permissions (`audit_android15`).
- Wireless enablement from USB (`enable_wireless`) for dev-only loops.
- Desktop bridge server for Android↔desktop event/command exchange (`BridgeServer`).
- WSL→Windows adb resolution and path normalization for mixed host setups.
- Structured logcat fan-out to DiagnosticBus via `emit=` callbacks.

## Usage (dev-only)
```python
from kivy.protonox_ext.android_bridge import adb

adb.ensure_adb()
devices = adb.list_devices()
adb.push_reload("./bin/MyApp-debug.apk", package="com.example.myapp")
session = adb.stream_logcat("com.example.myapp")
# Structured log lines with GL warnings included
for evt in adb.stream_logcat_structured("com.example.myapp"):
    print(evt)
# Wireless connect if an IP:port is known or PROTONOX_ADB_WIRELESS_HOST is set
wireless_devices = adb.connect_wireless()
# Switch a USB device to tcpip mode and reconnect when possible
host = adb.enable_wireless()
# Fan-out structured logcat into a DiagnosticBus emitter
from kivy.protonox_ext.diagnostics import get_bus
bus = get_bus()
for evt in adb.stream_logcat_structured("com.example.myapp", emit=lambda e: bus._record(e)):  # type: ignore[attr-defined]
    ...
# API 35 readiness audit
print(adb.audit_android15("com.example.myapp"))
# Android 13–15 permission audit
from kivy.protonox_ext.android_bridge import audit_runtime_compat
print(audit_runtime_compat("com.example.myapp").to_json())
# ...read session.process.stdout as needed...
session.stop()

from kivy.protonox_ext.android_bridge import android_preflight
report = android_preflight()
print(report.as_dict())  # {'ok': False, 'findings': [...], 'details': {...}}
```

### CLI shortcuts (Protonox Studio)
- `protonox android-detect [--adb-path]` — resolve adb (WSL/Windows aware) and list devices/emulators.
- `protonox android-logs --package <pkg> [--wifi-first]` — stream structured logcat with GL/SDL hints.
- `protonox android-restart --package <pkg> [--activity ACT] [--wifi-first]` — relaunch activity without rebuild.
- `protonox android-reinstall --package <pkg> --apk <path> [--activity ACT] [--wifi-first]` — reinstall APK and restart.
- `protonox android-wifi-connect [--wifi-target host:port]` — mdns/Wi‑Fi connect where available.
- `protonox android-wifi-restart [--serial SERIAL] [--port 5555]` — switch USB device to tcpip then reconnect.
- `protonox android-wifi-logs --package <pkg>` — wireless-first structured log stream.

## Principles
- **Opt-in only:** nothing runs automatically; you call the helpers explicitly.
- **Zero core changes:** Kivy runtime is untouched.
- **Recoverable:** commands raise `ADBError` with actionable stderr/stdout.
- **Parity:** same commands usable locally or inside Docker when platform-tools
  are available.
- **Wireless-friendly:** prefers Wi‑Fi when available, with automatic mdns
  discovery where host `adb` supports it.
- **API-35 aware:** `audit_android15` flags missing targetSdkVersion or runtime
  permissions (POST_NOTIFICATIONS, READ_MEDIA_*).
- **Bridge-ready:** optional `BridgeServer` enables Android↔desktop payloads for
  future Protonox Studio iterations without touching app code.
