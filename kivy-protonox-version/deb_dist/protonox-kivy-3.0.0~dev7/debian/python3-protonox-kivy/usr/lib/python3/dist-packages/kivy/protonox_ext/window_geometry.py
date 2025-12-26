"""Safe window geometry helpers for cross-platform (Linux/Windows/macOS).

These helpers avoid ``NoneType`` crashes when persisting or restoring window
size/position on platforms that may not expose full geometry (e.g. X11 with
no position support, some Wayland shells, or Windows before the window is
shown). All functions are best-effort and return booleans so callers can decide
whether to retry or fall back to defaults.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

try:  # Kivy is required at runtime; keep import local to avoid hard fails at lint time
    from kivy.core.window import Window
except Exception:  # pragma: no cover - handled by callers in non-GUI contexts
    Window = None  # type: ignore

Geometry = Dict[str, Any]


def _is_tuple_of_numbers(value: Any) -> bool:
    return (
        isinstance(value, (tuple, list))
        and len(value) == 2
        and all(isinstance(x, (int, float)) for x in value)
    )


def capture_geometry() -> Geometry:
    """Capture current window geometry in a serializable dict.

    Returns keys: ``size`` (tuple) and ``position`` (tuple) when available,
    plus ``fullscreen`` for completeness. Missing values are omitted to avoid
    persisting ``None`` and causing subscript errors later.
    """

    if Window is None:
        return {}

    data: Geometry = {"fullscreen": getattr(Window, "fullscreen", False)}

    try:
        if _is_tuple_of_numbers(getattr(Window, "size", None)):
            data["size"] = tuple(Window.size)
    except Exception:
        pass

    try:
        pos = getattr(Window, "position", None)
        if _is_tuple_of_numbers(pos):
            data["position"] = tuple(pos)
    except Exception:
        # Some platforms (Wayland) may not support position; skip silently.
        pass

    return data


def apply_geometry(saved: Optional[Geometry]) -> bool:
    """Apply a previously captured geometry safely.

    Returns True on best-effort success, False if nothing was applied.
    No exceptions are raised; failures simply return False so callers can
    fallback to defaults.
    """

    if Window is None or not saved:
        return False

    applied = False

    try:
        size = saved.get("size") if isinstance(saved, dict) else None
        if _is_tuple_of_numbers(size):
            Window.size = tuple(size)
            applied = True
    except Exception:
        pass

    try:
        pos = saved.get("position") if isinstance(saved, dict) else None
        if _is_tuple_of_numbers(pos) and hasattr(Window, "position"):
            Window.position = tuple(pos)
            applied = True
    except Exception:
        pass

    try:
        fullscreen = saved.get("fullscreen") if isinstance(saved, dict) else None
        if isinstance(fullscreen, bool):
            Window.fullscreen = fullscreen
            applied = True
    except Exception:
        pass

    return applied


def apply_or_default(saved: Optional[Geometry], fallback_size: Tuple[int, int] = (1280, 720)) -> None:
    """Try to apply saved geometry; otherwise set a sane default size.

    This is a convenience wrapper to reduce boilerplate in apps.
    """

    if not apply_geometry(saved) and Window is not None:
        try:
            Window.size = fallback_size
        except Exception:
            pass


__all__ = ["capture_geometry", "apply_geometry", "apply_or_default"]
