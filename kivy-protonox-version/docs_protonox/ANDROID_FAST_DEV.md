# Android Fast Dev Loop (kivy-protonox-version)

These helpers sit outside the Kivy core and provide a thinner dev loop for
Android testing. They are **optional** and only run when explicitly invoked.

## Quick commands
- `protonox_ext.android_bridge.ensure_adb()` – validate adb availability.
- `protonox_ext.android_bridge.list_devices()` – list connected devices.
- `protonox_ext.android_bridge.connect_wireless(target=None)` – prefer Wi‑Fi debugging when adb mdns or env `PROTONOX_ADB_WIRELESS_HOST` is available.
- `protonox_ext.android_bridge.enable_wireless(serial=None, port=5555)` – switch a USB device to tcpip mode for cable-free loops.
- `protonox_ext.android_bridge.auto_select_device()` – prefer Wi‑Fi → USB → emulator.
- `protonox_ext.android_bridge.watch(package, activity=None, reinstall_apk=None)` –
  reinstall (optional), launch the activity, and stream logcat filtered to the
  package. Call `stop()` on the returned session to end streaming.
- `protonox_ext.android_bridge.audit_android15(package)` – surface targetSdkVersion
  and runtime permission warnings for API 35 devices.
- `protonox_ext.android_bridge.audit_runtime_compat(package)` – non-invasive Android 13–15 runtime permission + target audit.
- `protonox_ext.android_bridge.BridgeServer()` – optional HTTP bridge for events/commands between desktop + Android client.

## Why use it
- Avoids full rebuilds when only KV/logic changed and an APK is already built.
- Restarts only the target activity instead of reinstalling on every change.
- Ships logcat with package-level filtering (`*:S` + `<package>:V`) and optional
  structured GL/SDL warnings.
- Wireless debugging reduces cable swapping; WSL hosts are supported via
  automatic Windows adb path normalization when needed.

## Boundaries
- Does **not** alter buildozer/SDK/NDK.
- No persistent services are started; everything is per-command and opt-in.
- Safe to ignore in production; intended for developers iterating locally.
