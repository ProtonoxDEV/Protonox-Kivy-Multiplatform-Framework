Protonox Kivy 3.0.0.dev7
=========================

Changelog for development release 3.0.0.dev7

- Build: Rebuilt with system SDL3/pango dev packages available; compiled SDL3 window backend.
- Compatibility: `kivy.core.window.window_sdl2` shim continues to re-export `window_sdl3`.
- Packaging: Prepared Debian `.deb` packaging workflow.

This is a development release for internal testing. See `README_DEPENDENCIES.md` for native dependency notes.

Defaults update:

- Default window backend: **SDL3** enabled by default (`USE_SDL3=1`).
- Default text provider: **Pango (pangoft2)** enabled by default (`USE_PANGOFT2=1`).

Notes:

- SDL3 is now the recommended default for modern platforms; SDL2 is disabled by default but kept as a fallback in source.
- `pangoft2` is selected for robust international text shaping. If `pangoft2` is not available on a target system, Kivy will fall back to other available text providers.
- These defaults can be overridden at build time or via environment variables documented in `setup.py`.
