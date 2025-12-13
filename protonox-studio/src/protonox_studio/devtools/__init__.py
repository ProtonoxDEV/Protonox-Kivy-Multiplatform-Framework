"""Developer-only utilities for diagnostics and safer iteration cycles."""

from .error_overlay import ErrorOverlay, build_error_overlay
from .logger import prefixed_logger
from .clock_guard import ClockGuard
from .kv_strict import enable_kv_strict_mode

__all__ = [
    "ErrorOverlay",
    "build_error_overlay",
    "prefixed_logger",
    "ClockGuard",
    "enable_kv_strict_mode",
]
