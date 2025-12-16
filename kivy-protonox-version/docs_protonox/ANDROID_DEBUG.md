# ANDROID_DEBUG

Android troubleshooting is opt-in and works over USB or Wi‑Fi without changing your app code.

## Quick commands (via Protonox CLI)
- `protonox android detect` — list devices/emulators (USB or Wi‑Fi), normalising WSL ↔ Windows paths.
- `protonox android logs --package <pkg>` — filtered logcat plus Python stdout/stderr and Kivy warnings.
- `protonox android restart --package <pkg> [--activity MainActivity]` — restart the app process without rebuilding.
- `protonox android reinstall --package <pkg> --apk dist/app.apk` — push an APK without a full rebuild.
- `protonox android wifi-connect [--wifi-target host:port]` — prefer wireless adb if available.
- `protonox android wifi-restart [--serial <id>]` — switch a device to tcpip mode.
- `protonox android wifi-logs --package <pkg>` — wireless logcat + structured logs for IA/diagnostics.

## API 35 readiness
- Target/permission audit surfaces POST_NOTIFICATIONS and READ_MEDIA_* hints.
- Log messages call out background limits and blocked operations instead of failing silently.

## When Wi‑Fi fails
- The CLI automatically falls back to USB adb.
- Path normalisation `/mnt/c/...` ↔ `C:\...` happens transparently on WSL.

## What Protonox Studio consumes
- Structured log events (adb + Kivy) and optional snapshots for IA suggestions.
- No code changes are applied automatically; everything stays read-only until you accept a patch.
