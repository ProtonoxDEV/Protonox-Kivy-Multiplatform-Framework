"""Helpers to fetch and react to Android window insets (status/nav/cutout/ime).

Best-effort only; on non-Android returns zeros and no-ops. On Android, uses
``WindowInsets`` / ``WindowInsetsCompat`` via ``jnius`` to read safe areas and
optionally attach a listener for dynamic changes (orientation, gesture mode,
IME, split-screen, foldables).
"""
from __future__ import annotations

from typing import Callable, Dict

try:
    from jnius import autoclass, cast  # type: ignore
except Exception:  # not on Android or jnius missing
    autoclass = cast = None  # type: ignore


def is_android() -> bool:
    """Return True when running under Android (jnius available)."""
    return autoclass is not None


def _zero_insets() -> Dict[str, int]:
    return {"top": 0, "bottom": 0, "left": 0, "right": 0, "ime_bottom": 0}


def get_current_insets() -> Dict[str, int]:
    """Read current window insets. Fallback: zeros if not available."""
    if not is_android():
        return _zero_insets()
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        window = activity.getWindow()
        decor = window.getDecorView()
        insets = decor.getRootWindowInsets()
        if insets is None:
            return _zero_insets()

        # Types for status/navigation/cutout/ime
        WindowInsetsCompat = autoclass("androidx.core.view.WindowInsetsCompat")
        types = WindowInsetsCompat.Type
        mask = (
            types.statusBars()
            | types.navigationBars()
            | types.displayCutout()
            | types.ime()
        )
        compat = WindowInsetsCompat.toWindowInsetsCompat(insets)
        vals = compat.getInsets(mask)
        return {
            "top": vals.top,
            "bottom": vals.bottom,
            "left": vals.left,
            "right": vals.right,
            "ime_bottom": compat.getInsets(types.ime()).bottom,
        }
    except Exception:
        return _zero_insets()


def add_insets_listener(callback: Callable[[Dict[str, int]], None]) -> None:
    """Attach a listener to receive insets when they change.

    The callback receives a dict with keys: top, bottom, left, right, ime_bottom.
    No-op on non-Android or if any error occurs.
    """
    if not is_android():
        return
    try:
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        View = autoclass("android.view.View")
        activity = PythonActivity.mActivity
        window = activity.getWindow()
        decor = window.getDecorView()

        class InsetsListener(autoclass("java.lang.Object"), View.OnApplyWindowInsetsListener):  # type: ignore
            def onApplyWindowInsets(self, v, insets):  # noqa: N802 - Android signature
                data = get_current_insets()
                try:
                    callback(data)
                except Exception:
                    pass
                return v.onApplyWindowInsets(insets)

        listener = InsetsListener()
        decor.setOnApplyWindowInsetsListener(listener)
        # Force initial dispatch so the callback runs at least once
        decor.requestApplyInsets()
    except Exception:
        return
