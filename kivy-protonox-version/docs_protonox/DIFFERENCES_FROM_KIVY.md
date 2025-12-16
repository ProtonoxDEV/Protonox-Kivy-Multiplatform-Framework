# Differences from upstream Kivy 2.3.1 (Protonox extension layer)

This document lists Protonox-specific, opt-in additions so downstream projects
can audit behaviour relative to upstream **Kivy 2.3.1**. The core remains
unchanged unless the corresponding Protonox flags are enabled.

## Design guardrails
- Public Kivy APIs remain intact; all additions live under `kivy.protonox_ext`
  and are inert unless explicitly imported or gated by env flags.
- No Android SDK/NDK changes. ADB helpers are thin wrappers only.
- Features are dev-only by default and disabled in production.

## Major Protonox capabilities
- **Layout telemetry**: widget bounds, symmetry scoring, fingerprints, and
  anti-pattern detection behind `PROTONOX_LAYOUT_TELEMETRY`.
- **UI observability**: export of tree + metrics + display context with optional
  layout-health scoring (`PROTONOX_UI_OBSERVABILITY`, `PROTONOX_LAYOUT_HEALTH`).
- **Visual snapshots**: PNG + JSON dual exports for audit pipelines
  (`PROTONOX_VISUAL_WARNINGS`).
- **Layout profiler**: opt-in runtime timing of `do_layout` to surface expensive
  widgets (`PROTONOX_LAYOUT_PROFILER`).
- **Emoji fallback**: optional emoji/font helper that keeps defaults untouched
  unless explicitly enabled.
- **Android fast loop**: ADB wrappers for reinstall/restart/logcat without
  altering build pipelines.
- **Compatibility profiles**: `kivy.protonox_ext.compat` keeps the fork dormant
  until a developer calls `enable_*` helpers.
- **Runtime doctor**: opt-in GPU/GL/DPI/window report via
  `kivy.protonox_ext.diagnostics` when `PROTONOX_RUNTIME_DIAGNOSTICS=1`.

## What never changes automatically
- Core classes (Widget, Layouts, Builder) and their semantics.
- KV syntax and resolution rules.
- Production runtime behaviour unless a Protonox flag is set.

Consumers can keep using Protonox as a drop-in for Kivy 2.3.1 and only opt into
the diagnostics or tooling they need.
