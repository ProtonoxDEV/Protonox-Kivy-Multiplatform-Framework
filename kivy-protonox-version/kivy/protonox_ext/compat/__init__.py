"""Compatibility surface for the Protonox Kivy fork (opt-in)."""
from .compat_layer import (
    CompatReport,
    enable_diagnostics,
    enable_profile,
    enable_protonox_ui,
    enable_safe_mode,
)
from .deprecated_shims import emit_all_warnings, register_shim
from .warnings_map import COMPAT_WARNINGS, CompatWarning

__all__ = [
    "CompatReport",
    "CompatWarning",
    "COMPAT_WARNINGS",
    "enable_profile",
    "enable_diagnostics",
    "enable_protonox_ui",
    "enable_safe_mode",
    "emit_all_warnings",
    "register_shim",
]
