# Protonox Compatibility Layer (Drop-in)

Purpose: allow teams to install `kivy-protonox-version` with zero behavioural
changes until they explicitly opt into extensions.

## Principles
- Upstream Kivy 2.3.1 behaviour by default.
- Extensions gated behind environment flags or explicit function calls.
- No monkey patches to core widgets or providers.

## Activation (opt-in)
- Environment flag (no code changes): set `KIVY_PROTONOX=1` or `PROTONOX_KIVY=1`
  to activate safe mode by default. Optionally set `KIVY_PROTONOX_PROFILE` to
  `diagnostics`, `ui`, or `safe` to pick a profile.

- Code-level enable (one-liner):

```python
from kivy_protonox import enable

enable()             # safe mode
enable("diagnostics")  # runtime doctor + telemetry flags
enable("ui")           # UI observability + profiler flags
```

The fork stays dormant unless one of the above is used.

## Profiles
Use from application startup (dev only) if you need finer control:

```python
from kivy.protonox_ext.compat import enable_safe_mode, enable_diagnostics, enable_protonox_ui

# keep fork dormant
enable_safe_mode()

# surface doctor reports (read-only)
enable_diagnostics()

# opt-in to observability + layout telemetry
enable_protonox_ui()
```

Profiles only set environment flags (`PROTONOX_*`) and do not alter widget
behaviour. Leave them unused to run pure Kivy 2.3.1.

## Warnings map
`kivy.protonox_ext.compat.warnings_map` documents what each flag does and how to
turn it off. Call `emit_all_warnings()` to surface them during development.

## Migration shims
`register_shim()` is a safe hook to attach opt-in migration helpers without
touching the core. Nothing is registered by default.
