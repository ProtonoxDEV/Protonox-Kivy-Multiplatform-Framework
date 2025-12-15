# Protonox CLI cheatsheet (Studio + Web2Kivy)

This guide enumerates the CLI surface required by the Web→Kivy integration plan. All
commands are opt-in, operate inside controlled folders, and avoid mutating user code
unless the developer explicitly enables risky modes.

## Conventions
- Controlled write zones: `protobots/protonox_export/**`, `.protonox/**`, `protobots/protonox_studio/**`.
- Manifests: `protonox_studio.yaml|json` under `protobots/protonox_export/`.
- Flags are available via CLI options or env vars (e.g., `PROTONOX_BULK_RELOAD_THRESHOLD`).
- Prefixed logs: `[PXKIVY]`, `[PXSTUDIO]`, `[HOTRELOAD]`, `[KV]`, `[ANDROID]`, `[UIIR]`, `[VALIDATE]`.

## Core commands
### `protonox doctor`
Environment audit. Detects WSL/Windows, Kivy-Protonox version, buildozer/adb paths (including `adb.exe` on Windows), OpenGL, fonts/emoji, and Android 13–15 permission readiness. Outputs JSON under `.protonox/diagnostics/`.

### `protonox web2kivy --entry <html|url>`
Exports a web entrypoint into UI‑IR + KV + optional scaffolds under `protobots/protonox_export/`. Honors `protonox_studio.yaml` if present for naming and viewport hints. Writes reports to `.protonox/protonox-exports/`.

### `protonox map --app protobots --exports protobots/protonox_export`
Interactive “game” to match detected screens (from the real ScreenManager/router) with exported slugs. Suggests matches by route/name/text. Persists `protonox_studio.yaml` and runs a smoke test (Builder compile) per confirmed screen.

### `protonox run --app protobots [--hotreload]`
Boots the real app with feature flags. When `--hotreload` is enabled, attaches the batch watcher on `protobots/protonox_export/**/*` with sandbox compile + rollback per screen. Honors `LiveReloadStateCapable` methods if implemented by the screen.

### `protonox validate --baseline <web.png> --candidate <kivy.png>`
Visual validation: renders/compares PNGs, emits diff metrics, and stores outputs in `.protonox/protonox-exports/`. Can also consume UI‑IR snapshots to compare tree symmetry.

## Navigation and mapping helpers
### `protonox nav-scan --ui-model <path>`
Runs `web_nav/extract.py` against a UI‑IR to infer routes, anchors, and buttons. Produces `nav_graph.json` (proposal only) and prints a summary table.

### `protonox nav-apply --map protonox_studio.yaml`
Dangerous/opt-in. Applies a confirmed `nav_graph` onto the router/ScreenManager only when the developer accepts a prompt. Default behavior is to refuse unless `--force` and `PROTONOX_ALLOW_APPLY=1` are set.

## Android fast loop
### `protonox android wifi-connect`
WSL-aware helper that discovers `adb` (Linux or `adb.exe`), guides pairing (Android 11+), and stores device aliases in `.protonox/android/devices.json`. Emits connectivity and logcat sanity checks.

### `protonox android audit --target 35`
Runs an audit against targetSdkVersion 35 permissions (Bluetooth, media, notifications, etc.). Outputs `.protonox/android/audit_api35.json`.

### `protonox android bridge [--serve]`
Optional dev-only bridge server for desktop ↔ Android. Streams logcat, pulls/pushes `.protonox/` artifacts, and can execute constrained “actions” (camera open, permission request) for debugging. Disabled by default unless flags are set.

## Examples (end-to-end)
1. Export + map + inject
```bash
protonox web2kivy --entry website/views/articulos.html --out protobots/protonox_export
protonox map --app protobots --exports protobots/protonox_export
protonox run --app protobots --hotreload
```

2. Validate and diff
```bash
protonox validate --baseline snapshots/web-articulos.png --candidate snapshots/kivy-articulos.png
```

3. Android loop
```bash
protonox android wifi-connect
protonox android audit --target 35
```

## Safeguards built into the CLI
- Commands refuse to modify user routers or controllers unless explicitly asked (`apply_router`/`nav-apply`).
- Hot‑reload is transactional with rollback snapshots per screen.
- Mapping is required before injection; missing mappings render a placeholder screen with a warning.
- Bulk reload waits for a quiet period and reports how many screens reloaded/failed.
- Navigation inference is suggestive only; the CLI always asks for confirmation before persisting.
