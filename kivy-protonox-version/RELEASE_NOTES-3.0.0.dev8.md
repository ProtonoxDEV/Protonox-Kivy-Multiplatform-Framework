```markdown
Protonox Kivy 3.0.0.dev8
=========================

Changelog for development release 3.0.0.dev8

- Build: Continued validation of SDL3 + pangoft2 defaults; updated packaging notes.
- Fixes: Addressed runtime fallback behavior in `kivy/core/window/window_sdl3.py` for safer subclassing when compiled backends are present.
- Packaging: Prepared instructions for bundling SDL3 sub-libraries into `kivy-dependencies/dist`.

This is a development release for internal testing. See `README_DEPENDENCIES.md` for native dependency notes.

Defaults update:

- Default window backend: **SDL3** enabled by default on desktop (`USE_SDL3=1` on linux/darwin).
- Default text provider: **Pango (pangoft2)** enabled by default (`USE_PANGOFT2=1`).

Notes:

- SDL3 is the recommended default for modern platforms; SDL2 remains available as a fallback when explicitly enabled.
- `pangoft2` is selected for robust international text shaping. If `pangoft2` is not available on a target system, Kivy will fall back to other available text providers.
- These defaults can be overridden at build time or via environment variables documented in `setup.py`.

``` 
