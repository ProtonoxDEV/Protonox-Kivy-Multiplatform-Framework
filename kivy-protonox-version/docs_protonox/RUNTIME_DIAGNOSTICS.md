# Runtime Diagnostics (Doctor)

Opt-in doctor-style checks for the Protonox Kivy fork. Provides read-only
inspection of GPU/OpenGL, window provider, DPI, and platform hints without
changing application behaviour.

## How to use
1. Enable diagnostics (dev only):
   ```python
   from kivy.protonox_ext.compat import enable_diagnostics
   enable_diagnostics()
   ```
2. Call the runtime collector from within your app or a debug shell:
   ```python
   from kivy.protonox_ext.diagnostics import collect_runtime_diagnostics, as_lines

   report = collect_runtime_diagnostics()
   for line in as_lines(report):
       print(line)
   ```
3. CLI-style invocation is also available:
   ```bash
   python -m kivy.protonox_ext.diagnostics.runtime
   ```

## What it reports
- OpenGL vendor / renderer / version (when available)
- Window backend and resolution
- DPI hint and scaling warnings
- Platform/session hints (e.g., Wayland)
- Optional diagnostic bus events when `PROTONOX_DIAGNOSTIC_BUS=1` (stdout/stderr/warnings/logs)

## Compatibility
- Guarded by `PROTONOX_RUNTIME_DIAGNOSTICS` flag (off by default).
- Does not modify widgets, providers, or application state.
