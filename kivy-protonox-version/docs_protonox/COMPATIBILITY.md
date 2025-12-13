# Compatibility Policy — kivy-protonox-version

- **Baseline:** Fully compatible with upstream Kivy 2.3.1.
- **Opt-in only:** No new behaviour is active unless the developer imports and enables it.
- **No API changes:** Core classes, module paths, and signatures remain intact.
- **Isolation:** All exports target caller-provided paths; the framework does not overwrite user assets.
- **Flags:** Telemetry/visual checks respect `PROTONOX_LAYOUT_TELEMETRY` and `PROTONOX_VISUAL_WARNINGS`; emoji fallback is gated by `PROTONOX_EMOJI_FALLBACK`.
- **Rollback:** Hot reload helpers keep snapshot/restore primitives to avoid corrupting runtime state.

If an app works on vanilla Kivy 2.3.1, it must work the same on this fork when
no extension modules are imported.
