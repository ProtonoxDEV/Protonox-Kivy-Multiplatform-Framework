# Android Bridge (ADB) — Protonox Extensions (opt-in)

Goal: make Android smoke tests and log collection easier without touching the
Kivy core or requiring rebuilds for every KV tweak.

## Capabilities
- Detect and list connected devices (`list_devices`).
- Verify `adb` availability (`ensure_adb`).
- Incremental install/reinstall APKs (`install_apk`, `push_reload`).
- Start activities without rebuilding (`run_app`).
- Filtered logcat streaming for a package (`stream_logcat`).
- Bugreport capture for diagnostics (`capture_bugreport`).
- Read device properties for environment-aware tweaks (`device_props`).

## Usage (dev-only)
```python
from kivy.protonox_ext.android_bridge import adb

adb.ensure_adb()
devices = adb.list_devices()
adb.push_reload("./bin/MyApp-debug.apk", package="com.example.myapp")
session = adb.stream_logcat("com.example.myapp")
# ...read session.process.stdout as needed...
session.stop()
```

## Principles
- **Opt-in only:** nothing runs automatically; you call the helpers explicitly.
- **Zero core changes:** Kivy runtime is untouched.
- **Recoverable:** commands raise `ADBError` with actionable stderr/stdout.
- **Parity:** same commands usable locally or inside Docker when platform-tools
  are available.
