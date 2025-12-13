# Protonox Extensions Overview (kivy-protonox-version)

## Purpose
A controlled extension layer on top of Kivy 2.3.1 that unlocks:
- Web → Kivy translation through a neutral UI IR.
- Layout introspection for geometry-aware IA.
- Visual comparison hooks (PNG) for non-destructive validation.
- Safer hot reload with rollback snapshots.

## What lives where
- `protonox_ext/layout_engine/`: runtime geometry snapshots and alignment hints.
- `protonox_ext/inspector/`: dev-only inspection exports.
- `protonox_ext/kv_bridge/`: UI IR schema and KV compiler (sandbox outputs).
- `protonox_ext/hotreload_plus/`: snapshot/rollback helpers for advanced reload.
- `protonox_ext/web_mapper/`: DOM-to-IR adapter for declared routes.
- `protonox_ext/visual_state/`: PNG-based warnings for baseline vs candidate.
- `protonox_ext/android_bridge/`: dev-only ADB helpers (install/run/logcat/bugreport).
- `protonox_ext/ui/`: emoji fallback helpers for consistent text rendering.

## How to opt-in safely
1. Enable telemetry: `PROTONOX_LAYOUT_TELEMETRY=1` (dev only).
2. Import helpers explicitly, e.g. `from kivy.protonox_ext.layout_engine import introspect`.
3. Export to your own directories; no in-place modifications occur.
4. Use feature flags to disable at any time.

## Non-goals
- Replacing Kivy core classes.
- Forcing KivyMD or other UI kits.
- Shipping AI keys or backend credentials.

## Integration with Protonox Studio
- Protonox Studio consumes the IR (`UIModel`) and telemetry outputs.
- Visual diffs and repair plans run against exported data, not live code.
- The extension layer stays framework-only; Studio handles agents and backend calls.
