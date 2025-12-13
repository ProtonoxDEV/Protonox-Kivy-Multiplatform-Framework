# Fork Overview — kivy-protonox-version (2.3.1)

This folder contains the Protonox-controlled extension layer on top of Kivy 2.3.1.
The upstream Kivy source remains intact; every Protonox addition is opt-in and
lives under `kivy/protonox_ext/` so existing applications keep working without
code changes.

## What stays the same
- Public Kivy APIs, widgets, and providers are untouched by default.
- Projects can install the fork as a drop-in replacement without behaviour
  changes unless they explicitly enable Protonox features.

## What Protonox adds (opt-in)
- Compatibility profiles (`enable_safe_mode`, `enable_protonox_ui`,
  `enable_diagnostics`) to guard behaviour and keep the fork dormant unless a
  developer opts in.
- Diagnostic bus and runtime doctor for GPU/GL/DPI/Window visibility.
- Layout observability: fingerprints, symmetry scores, anti-pattern detection,
  and telemetry-powered exports.
- Visual state utilities (freeze mode, PNG/JSON dual snapshots) and hot-reload
  safety helpers.
- Android bridge utilities (ADB fast loop, logcat filtering) and emoji
  fallbacks.

## How to keep Protonox dormant
```python
from kivy_protonox import enable_safe_mode
enable_safe_mode()  # retains upstream behaviour while making the fork detectable
```

## How to opt into telemetry and diagnostics
```python
from kivy_protonox import enable_diagnostics, enable_protonox_ui

# Diagnostics-only (doctor, diagnostic bus, runtime checks)
enable_diagnostics()

# UI telemetry + profiler overlays (still read-only)
enable_protonox_ui()
```

Use environment flags for fine-grained control; see `FEATURE_FLAGS.md`.
