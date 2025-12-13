# Feature Flags — Protonox Kivy Fork

All Protonox extensions are controlled via environment variables. Nothing is
enabled by default; set the flags you need in your dev environment or CI.

| Flag | Purpose | Default |
| --- | --- | --- |
| `PROTONOX_COMPAT_MODE` | Marks the runtime as Protonox; set automatically by `enable_safe_mode`/profiles. | unset |
| `PROTONOX_DIAGNOSTIC_BUS` | Enable unified stdout/stderr/warnings/log capture. | `0` |
| `PROTONOX_RUNTIME_DIAGNOSTICS` | Activate doctor-style GPU/GL/DPI checks. | `0` |
| `PROTONOX_LAYOUT_TELEMETRY` | Allow bounds/fingerprint/symmetry exports. | `0` |
| `PROTONOX_UI_OBSERVABILITY` | Aggregate observability exports (tree + metrics). | `0` |
| `PROTONOX_LAYOUT_PROFILER` | Collect per-widget layout cost timings. | `0` |
| `PROTONOX_LAYOUT_HEALTH` | Emit layout health scoring and anti-patterns. | `0` |
| `PROTONOX_PNG_SNAPSHOT` | Enable dual PNG + JSON snapshot capture. | `0` |

Use profiles for convenience:
- `enable_safe_mode()` → sets `PROTONOX_COMPAT_MODE=1` only.
- `enable_diagnostics()` → sets `PROTONOX_COMPAT_MODE=1`, `PROTONOX_RUNTIME_DIAGNOSTICS=1`, `PROTONOX_LAYOUT_TELEMETRY=1`.
- `enable_protonox_ui()` → sets `PROTONOX_COMPAT_MODE=1`, `PROTONOX_UI_OBSERVABILITY=1`, `PROTONOX_LAYOUT_TELEMETRY=1`, `PROTONOX_LAYOUT_PROFILER=1`.
