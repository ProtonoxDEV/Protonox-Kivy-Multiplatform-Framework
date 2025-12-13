# Protonox UI Debug & Profiling (Kivy 2.3.1 Protonox fork)

This guide covers the dev-only debugging layer that ships with
`kivy-protonox-version`. All capabilities are **opt-in** and keep the upstream
runtime unchanged when disabled.

## Flags
- `PROTONOX_LAYOUT_TELEMETRY=1` – enable geometry snapshots, fingerprints, and
  symmetry/anti-pattern detection.
- `PROTONOX_VISUAL_WARNINGS=1` – attach symmetry scores and layout warnings to
  visual exports.
- `PROTONOX_LAYOUT_PROFILER=1` – time `do_layout` per widget to spot expensive
  nodes; exposed via overlay payloads.
- `PROTONOX_LAYOUT_HEALTH=1` – compute layout health scores (anti-entropy
  engine) that blend overflow counts, anti-patterns, and symmetry.
- `PROTONOX_UI_OBSERVABILITY=1` – export a metadata-rich payload (resolution,
  DPI, platform, tree, metrics, health, fingerprint) for CI/IA pipelines.
- `PROTONOX_UI_FREEZE=1` – temporarily pause scheduling/animations while taking
  snapshots or profiling to avoid race conditions.

## Layout fingerprint & symmetry
- Use `protonox_ext.layout_engine.compute_fingerprint(widget)` to hash the live
  widget tree and detect regressions in CI.
- Use `symmetry_report(widget)` to get per-widget symmetry deltas.

## Cost profiler (new)
- Call `profile_tree(widget)` to collect per-widget `do_layout` timings.
- Feed the result into inspector overlays via `overlay_cost_payload(widget)`;
  severities (`low/medium/high`) help colour overlays.

## Visual snapshots
- `visual_state.snapshot.export_snapshot(widget, png_path)` already emits paired
  PNG + JSON; combine with `freeze_ui` for stable captures when animations run.
- `observability.export_observability(widget)` returns a single structure with
  the display context, widget tree, layout metrics, fingerprint, and layout
  health score for automated checks.

## Anti-pattern detection
- `layout_engine.detect_antipatterns(widget)` surfaces common layout smells
  (oversized hierarchies, conflicting size_hints) without mutating the UI.

## Safety
- None of the helpers patch Kivy core. They are read-only and guard-railed by
  the environment flags above.
