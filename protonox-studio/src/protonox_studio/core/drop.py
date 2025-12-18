"""Drag/drop and import scaffolding for Studio.

Provides a minimal desktop drop handler and a fallback picker hook. Backend
support varies by OS/window provider; this keeps the API small so callers can
plug their own UI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from kivy.logger import Logger
from kivy.core.window import Window


def install_desktop_drop(callback: Callable[[Path, Optional[tuple]], None]) -> bool:
    """Bind Kivy's on_drop_file to a callback.

    Returns True if the bind succeeded.
    """

    def _on_drop_file(_window, path: bytes, x: int, y: int):  # noqa: ANN001 - Kivy signature
        try:
            callback(Path(path.decode("utf-8")), (x, y))
        except Exception:  # noqa: BLE001
            Logger.exception("protonox.drop: drop handler failed")

    try:
        Window.bind(on_drop_file=_on_drop_file)
        return True
    except Exception as exc:  # noqa: BLE001
        Logger.warning(f"protonox.drop: drop unavailable on this backend ({exc})")
        return False


def import_via_picker(open_file: Callable[[], Optional[str]], callback: Callable[[Path], None]) -> None:
    """Fallback picker wrapper (caller provides UI)."""
    try:
        selected = open_file()
        if selected:
            callback(Path(selected))
    except Exception:  # noqa: BLE001
        Logger.exception("protonox.drop: picker failed")
