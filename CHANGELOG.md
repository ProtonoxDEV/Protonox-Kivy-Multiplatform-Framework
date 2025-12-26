# Changelog
All notable changes to this project will be documented in this file.

This project follows a pragmatic versioning strategy based on
Kivy upstream + Protonox compatibility patches.

Version format:
MAJOR.MINOR.MICRO-protonox.devX

---

## [3.0.0.dev11] — OpenGL ES 3.2 Modernization
**Status:** DEV preview

### Added
- **OpenGL ES 3.2 Support**: Modernized graphics pipeline
  - Updated minimum OpenGL version requirement to 3.2
  - SDL3 context creation set to OpenGL ES 3.2
  - Enhanced graphics capabilities with Android Extension Pack features
  - Improved performance and visual quality on modern devices

### Improved
- Graphics initialization and version detection
- Compatibility with latest Android devices

### Notes
- Requires devices with OpenGL ES 3.2 support
- Enhanced visual effects and rendering capabilities

---

## [3.0.0.dev10] — SDL3 Integration & Android Builds
**Status:** DEV preview

### Added
- **SDL3 Backend Support**: Complete SDL3 window backend implementation
  - SDL3 window provider (`kivy.core.window.window_sdl3`)
  - SDL3 motion event handling
  - SDL3 input provider integration
- **Android SDL3 Bootstrap**: New bootstrap in python-for-android
  - SDL3 bootstrap with HarfBuzz and FreeType dependencies
  - SDL3_ttf with text shaping support for complex scripts
  - SDL3_image, SDL3_mixer recipes
  - Python shared library integration for Android
- **HarfBuzz Integration**: Advanced text rendering
  - Text shaping for non-Latin scripts
  - Improved typography and font rendering
  - Emoji and complex character support
- **Build System Updates**:
  - SDL3 recipes in python-for-android
  - Bootstrap priority and build configuration
  - Android.mk with proper library linking

### Improved
- Android build compatibility with modern SDL3
- Text rendering quality and internationalization
- Build reproducibility for Android packages

### Fixed
- SDL3 bootstrap missing dependencies (HarfBuzz, Python shared lib)
- Android compilation issues with SDL3_ttf
- Text rendering limitations for complex scripts

### Notes
- SDL3 enabled by default on desktop platforms
- SDL2 remains available as fallback
- Android builds require `--bootstrap=sdl3` flag
- Backward compatible with existing Kivy applications

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
  - PNG baseline/candidate validation via `protonox validate` con diff de bounding-box por widget + overlay opcional
  - Layout fingerprint + symmetry heuristics (`PROTONOX_VISUAL_WARNINGS=1`) and dual PNG+JSON snapshots (`PROTONOX_UI_FREEZE=1`)
  - Anti-pattern + DPI heuristics exported as read-only inspector payloads
- Round-trip importer to convert existing Kivy screens/widgets into the neutral UIModel for audits
- Protonox Kivy extension surface (`kivy-protonox-version/protonox_ext`)
  - Layout engine snapshots and inspector exports gated by flags
  - Inspector overlay payload + KV patch suggestions (dev-only)
  - Layout cost profiler + overlay enrichment (dev-only, `PROTONOX_LAYOUT_PROFILER=1`)
  - Layout health scoring + observability export (context + metrics + fingerprint,
    opt-in via `PROTONOX_LAYOUT_HEALTH`/`PROTONOX_UI_OBSERVABILITY`)
  - Neutral UI IR + KV compiler for sandbox generation
  - Hot reload snapshot/rollback helpers that leave core untouched
  - Visual PNG warning helpers (opt-in) for baseline vs candidate
  - Android preflight validation helper to fail fast in CI/containers
  - ADB `watch()` helper for filtered logcat + quick activity restart (opt-in)
- Wireless-aware ADB helpers (mdns connect, Wi‑Fi preferred selection, WSL path bridge) + Android 15 target/permission audit
- Wireless-first env flags + USB→tcpip helper for cable-free loops
- Android runtime compatibility audit for Android 13–15 permissions/targets
- Structured logcat emit hook for DiagnosticBus ingestion
- Desktop bridge server scaffold for Android↔desktop command/event exchange (dev-only)
- Dockerfile for reproducible Protonox/Kivy environment (opt-in, dev-only)
  - Compatibility profiles (`kivy.protonox_ext.compat`) to keep the fork dormant unless explicitly enabled
  - Runtime doctor (`kivy.protonox_ext.diagnostics`) for GPU/GL/DPI/window checks guarded by `PROTONOX_RUNTIME_DIAGNOSTICS`
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
