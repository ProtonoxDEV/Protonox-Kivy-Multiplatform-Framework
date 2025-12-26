"""
Compatibility shim: provide `kivy.core.window.window_sdl2` API by re-exporting
from the SDL3 implementation. This avoids ImportError for third-party packages
still importing `window_sdl2` while the codebase uses SDL3.
"""
try:
    # Prefer importing the SDL3 implementation and expose the expected names
    from .window_sdl3 import *  # noqa: F401,F403
except Exception:  # pragma: no cover - fallback to raising the original import error
    raise

# Export a clearer name for code that expects `WindowSDL` from window_sdl2
try:
    WindowSDL  # noqa: F401
except NameError:
    # If the SDL3 module uses a different class name, try to map it here.
    # As a conservative fallback, attempt common alternatives.
    try:
        from .window_sdl3 import Window  as WindowSDL  # type: ignore
    except Exception:
        pass
