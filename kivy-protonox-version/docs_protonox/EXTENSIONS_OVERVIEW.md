# Protonox Extensions Overview (kivy-protonox-version)

## Purpose
A controlled extension layer on top of Kivy 2.3.1 that unlocks:
- Web → Kivy translation through a neutral UI IR.
- Layout introspection for geometry-aware IA and fingerprints.
- Visual comparison hooks (PNG + JSON) for non-destructive validation.
- Safer hot reload with rollback snapshots.
- Multi-DPI, symmetry, and anti-pattern diagnostics without touching the core.

## What lives where
- `protonox_ext/layout_engine/`: runtime geometry snapshots, fingerprints, symmetry scores, anti-pattern detection, and opt-in layout cost profiling.
- `protonox_ext/inspector/`: dev-only inspection exports, layout health payloads, and overlay/patch payloads.
- `protonox_ext/kv_bridge/`: UI IR schema, KV compiler, and Kivy→IR importer (sandbox outputs).
- `protonox_ext/hotreload_plus/`: snapshot/rollback helpers for advanced reload.
- `protonox_ext/web_mapper/`: DOM-to-IR adapter for declared routes.
- `protonox_ext/visual_state/`: PNG-based warnings, UI freeze helper, and dual PNG+JSON snapshots for baseline vs candidate.
- `protonox_ext/android_bridge/`: dev-only ADB helpers (install/run/logcat/bugreport/watch) and environment preflight checks.
- `protonox_ext/ui/`: emoji fallback helpers for consistent text rendering.
- `docs_protonox/CHECKLIST.md`: estado rápido de requisitos obligatorios.
- `docs_protonox/PROTONOX_UI_DEBUG.md`: flags y flujo para perfiles de layout y snapshots duales.
- `docs_protonox/ANDROID_FAST_DEV.md`: loop acelerado ADB sin tocar el core.
- `docs_protonox/DIFFERENCES_FROM_KIVY.md`: diferencias claras contra Kivy 2.3.1.

## How to opt-in safely
1. Enable telemetry: `PROTONOX_LAYOUT_TELEMETRY=1` (dev only).
2. Enable symmetry/anti-pattern warnings when needed: `PROTONOX_VISUAL_WARNINGS=1`.
3. Freeze the UI for stable captures when required: `PROTONOX_UI_FREEZE=1`.
4. Profile layout cost when investigating FPS/layout lag: `PROTONOX_LAYOUT_PROFILER=1`.
5. Import helpers explicitly, e.g. `from kivy.protonox_ext.layout_engine import fingerprint`.
6. Export to your own directories; no in-place modifications occur.
7. Use feature flags to disable at any time.

## Non-goals
- Replacing Kivy core classes.
- Forcing KivyMD or other UI kits.
- Shipping AI keys or backend credentials.

## Integration with Protonox Studio
- Protonox Studio consumes the IR (`UIModel`) and telemetry outputs.
- Visual diffs and repair plans run against exported data, not live code.
- The extension layer stays framework-only; Studio handles agents and backend calls.
