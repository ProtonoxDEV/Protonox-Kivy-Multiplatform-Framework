# Protonox Extension Design Decisions (Kivy 2.3.1)

## Goals
- Keep Kivy 2.3.1 behaviour unchanged by default.
- Add capabilities as separate modules under `protonox_ext/`.
- Enable Web → Kivy conversions through a neutral UI model.
- Provide geometry/introspection hooks for future visual reasoning.

## Guardrails
- No public API changes; all features are opt-in imports.
- No SDK/NDK tweaks; improvements live in Python space.
- Telemetry and visual comparisons are gated by environment flags.

## Module layout rationale
- `layout_engine/`: serializable layout snapshots for IA and diffing.
- `inspector/`: dev-only export helpers that never mutate widgets.
- `kv_bridge/`: neutral UI IR plus KV generation that targets sandbox paths.
- `hotreload_plus/`: runtime snapshots and rollback helpers for safer reload.
- `web_mapper/`: DOM-to-IR bridge without depending on browser engines.
- `visual_state/`: PNG-aware warnings without pixel-perfect coupling.

## Compatibility stance
- Existing Kivy 2.3.1 apps continue to run untouched.
- Feature flags and explicit imports control every new behaviour.
- All exports are written to caller-provided paths (no in-place edits).
