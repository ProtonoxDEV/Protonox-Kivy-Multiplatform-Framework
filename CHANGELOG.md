# Changelog
All notable changes to this project will be documented in this file.

This project follows a pragmatic versioning strategy based on
Kivy upstream + Protonox compatibility patches.

Version format:
KivyVersion-protonox.PATCH

---

## [2.3.1-protonox.1] — Live Development & DX
**Status:** Stable (DEV-focused)

### Added
- Kivy Live Reload Engine (DEV only)
  - Level-based reload strategy (0–3)
  - Optional state preservation
  - Safe rollback on reload failure
- Decoupled HotReloadAppBase v2
- Error overlay UI (non-destructive, replaces crash in dev) with rebuild CTA
- Prefixed logger channels `[HOTRELOAD]`, `[BUILD]`, `[KV]`, `[UI]`
- Clock duplicate guard (dev-only warning)
- Centralized Protonox flags helper
- Preflight environment validation utilities
- Structured logging for rebuild/reload cycles
- Web → Kivy bridge
  - HTML-to-UIModel parser (entrypoint-driven, non-invasive)
  - KV/Python scaffold export to `.protonox` without touching user code
  - URL ingestion with asset/route detection and serialized UI-IR (`ui-model.json`)
  - Declarative route↔screen mapping via `--map protonox_studio.yaml` (KV/controller hints + viewport)
  - IR-based PNG render + diff commands (`render-web`, `render-kivy`, `diff`/`validate`)
  - PNG baseline/candidate validation via `protonox validate`
- Protonox Kivy extension surface (`kivy-protonox-version/protonox_ext`)
  - Layout engine snapshots and inspector exports gated by flags
  - Neutral UI IR + KV compiler for sandbox generation
  - Hot reload snapshot/rollback helpers that leave core untouched
  - Visual PNG warning helpers (opt-in) for baseline vs candidate
- Kivy vendored telemetry (opt-in)
  - `kivy.protonox_ext.telemetry` exposes bounds/overflow + safe `export_to_png` behind `PROTONOX_LAYOUT_TELEMETRY=1`

### Improved
- Developer iteration speed
- Debugging workflow without restarting the process

### Notes
- No changes to Kivy public API
- No changes to SDK / NDK
- Hot reload disabled by default in production

---

## [2.3.1-protonox.2] — Text & Typography Modernization
**Status:** In progress (opt-in available)

### Added
- Improved Unicode handling in TextInput (opt-in)
- Emoji-safe rendering pipeline
- Font fallback stack per platform (Android/Desktop)
- Emoji fallback helper gated by `PROTONOX_EMOJI_FALLBACK` for Kivy fork
- Dev-only Android bridge helpers (adb availability check, install/run/logcat, bugreport)
- Explicit lifecycle hooks via `ProtonoxWidget` mixin
- Runtime inspector (`app.inspect()`) for widget trees, KV rules, callbacks
- Responsive helpers (`breakpoint()`, `orientation()`) for KV sizing

### Notes
- All changes behind feature flags
- Backward compatible

---

## [2.3.1-protonox.3] — KV Language & Runtime Stability
**Status:** DEV preview (opt-in)

### Added
- KV strict mode (duplicate id detection + parser surfacing)
- Improved KV error reporting (file + line)
- Safe KV reload cleanup to prevent rule leaks

---

## [2.3.1-protonox.4] — Packaging & Industrial Builds
**Status:** Planned

### Added
- Build cache system (pip / gradle / buildozer)
- Build blueprints for Android and Desktop
- Reproducible build reports

---

## Compatibility Guarantee
- Fully compatible with Kivy 2.3.1 public API
- No breaking changes to existing applications
- All risky changes are opt-in and reversible
