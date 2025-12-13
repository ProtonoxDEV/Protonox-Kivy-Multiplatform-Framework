# Android Fast Dev Loop (kivy-protonox-version)

These helpers sit outside the Kivy core and provide a thinner dev loop for
Android testing. They are **optional** and only run when explicitly invoked.

## Quick commands
- `protonox_ext.android_bridge.ensure_adb()` – validate adb availability.
- `protonox_ext.android_bridge.list_devices()` – list connected devices.
- `protonox_ext.android_bridge.watch(package, activity=None, reinstall_apk=None)` –
  reinstall (optional), launch the activity, and stream logcat filtered to the
  package. Call `stop()` on the returned session to end streaming.

## Why use it
- Avoids full rebuilds when only KV/logic changed and an APK is already built.
- Restarts only the target activity instead of reinstalling on every change.
- Ships logcat with package-level filtering (`*:S` + `<package>:V`).

## Boundaries
- Does **not** alter buildozer/SDK/NDK.
- No persistent services are started; everything is per-command and opt-in.
- Safe to ignore in production; intended for developers iterating locally.
