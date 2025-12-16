# WSL_SETUP

Windows 11 + WSL2 is treated as a first-class environment. Use these notes to keep adb and paths stable.

## adb resolution
- Protonox tries Windows adb first, then WSL adb. No manual PATH juggling is required.
- Path normalisation bridges `/mnt/c/...` and `C:\...` automatically for push/pull and log collection.

## USB vs Wi‑Fi
- USB is used if detected; otherwise the CLI prefers wireless adb (mdns/tcpip) when available.
- You can force wireless flows with `protonox android wifi-connect`.

## File access
- Keep APKs and build artifacts under the WSL filesystem to avoid permission issues.
- When pointing to a Windows path, use the native form; the CLI will normalise for adb.

## Troubleshooting
- Run `protonox android detect` to confirm which adb binary is active and which devices are visible.
- If Windows Defender blocks adb, allow it once; Protonox will reuse that binary afterward.
- For slow wireless links, fall back to USB and re-run `protonox android logs`.
