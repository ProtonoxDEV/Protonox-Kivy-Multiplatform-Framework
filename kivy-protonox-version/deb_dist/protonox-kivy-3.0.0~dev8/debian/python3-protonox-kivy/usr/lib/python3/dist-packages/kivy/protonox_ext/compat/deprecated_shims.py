"""Non-intrusive shims for compatibility.

These helpers intentionally avoid monkey-patching Kivy. They simply provide
places where downstream projects can hook migrations or warnings while keeping
behaviour identical to upstream unless explicitly activated.
"""
from __future__ import annotations

import warnings
from typing import Callable

from .warnings_map import COMPAT_WARNINGS


def emit_all_warnings() -> None:
    """Emit compatibility warnings to inform developers what flags are active."""

    for warning in COMPAT_WARNINGS:
        warnings.warn(
            f"Protonox compatibility notice: {warning.message} (flag: {warning.flag}; {warning.mitigation})",
            category=UserWarning,
            stacklevel=2,
        )


def register_shim(name: str, handler: Callable[[], None]) -> None:
    """Placeholder for registering migration shims without modifying Kivy core."""

    # Today we only expose a hook; concrete shims should be opt-in and call this
    # function from application code or dedicated extension modules.
    handler()


__all__ = ["emit_all_warnings", "register_shim"]
