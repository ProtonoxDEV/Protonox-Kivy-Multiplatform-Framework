"""Drop-in compatibility controls for the Protonox Kivy fork.

The goal of this module is to guarantee that importing the fork behaves exactly
like vanilla Kivy 2.3.1 unless developers **opt in** to Protonox extensions.

Profiles are lightweight helpers that toggle a curated set of environment flags
so downstream modules know whether to activate diagnostics, layout telemetry, or
UI polish. They never modify the core widgets or providers.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Iterable

# Flags are additive; by default nothing is enabled so behaviour matches
# upstream Kivy 2.3.1. Profiles are intentionally explicit.
DEFAULT_PROFILE = {
    "PROTONOX_COMPAT_MODE": "1",  # guard rail: do nothing unless asked
}

DIAGNOSTICS_PROFILE = {
    "PROTONOX_COMPAT_MODE": "1",
    "PROTONOX_RUNTIME_DIAGNOSTICS": "1",
    "PROTONOX_LAYOUT_TELEMETRY": "1",
}

UI_PROFILE = {
    "PROTONOX_COMPAT_MODE": "1",
    "PROTONOX_UI_OBSERVABILITY": "1",
    "PROTONOX_LAYOUT_TELEMETRY": "1",
    "PROTONOX_LAYOUT_PROFILER": "1",
}


@dataclass
class CompatReport:
    """Summary of the compatibility layer state."""

    applied: Dict[str, str] = field(default_factory=dict)
    flags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, str]:
        payload = dict(self.flags)
        payload["applied"] = self.applied
        return payload


def _apply_flags(flags: Dict[str, str]) -> Dict[str, str]:
    applied: Dict[str, str] = {}
    for key, value in flags.items():
        prior = os.environ.get(key)
        if prior == value:
            continue
        os.environ[key] = value
        applied[key] = value
    return applied


def enable_profile(flags: Dict[str, str] | None = None) -> CompatReport:
    """Enable a set of environment flags safely.

    Intended for developers who want to opt into Protonox extensions without
    touching the core. Returns a report of what was applied.
    """

    flags = flags or DEFAULT_PROFILE
    applied = _apply_flags(flags)
    return CompatReport(applied=applied, flags=dict(flags))


def enable_diagnostics() -> CompatReport:
    """Opt into runtime diagnostics (doctor-style checks)."""

    return enable_profile(DIAGNOSTICS_PROFILE)


def enable_protonox_ui() -> CompatReport:
    """Opt into UI-facing Protonox helpers (observability + profiler).

    This does not modify existing layouts; it only enables telemetry so
    opt-in modules can introspect the UI when called explicitly.
    """

    return enable_profile(UI_PROFILE)


def enable_safe_mode() -> CompatReport:
    """Explicitly enforce compatibility defaults.

    Useful for large projects that want the fork installed but fully dormant
    unless a developer later opts into additional features.
    """

    return enable_profile(DEFAULT_PROFILE)


__all__ = [
    "CompatReport",
    "enable_profile",
    "enable_diagnostics",
    "enable_protonox_ui",
    "enable_safe_mode",
]
