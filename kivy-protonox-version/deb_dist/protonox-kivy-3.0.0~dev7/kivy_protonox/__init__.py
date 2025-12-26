"""Drop-in activation helpers for the Protonox Kivy fork.

The Protonox fork stays dormant unless explicitly enabled. Projects running
against upstream Kivy should see **no behavioural change**; developers can
choose to opt into Protonox tooling via an environment flag or a one-line
helper call.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

from kivy.protonox_ext.compat import (
    CompatReport,
    auto_enable_if_fork,
    enable_diagnostics,
    enable_protonox_ui,
    enable_safe_mode,
    is_protonox_runtime,
)

ENV_ENABLE_FLAG = "KIVY_PROTONOX"
LEGACY_ENABLE_FLAG = "PROTONOX_KIVY"
ENV_PROFILE_FLAG = "KIVY_PROTONOX_PROFILE"

PROFILE_MAP = {
    "diagnostics": enable_diagnostics,
    "ui": enable_protonox_ui,
    "safe": enable_safe_mode,
}


def enable(profile: Optional[str] = None) -> CompatReport:
    """Enable Protonox guardrails when running on the fork.

    - If a profile name is provided, it toggles the corresponding opt-in
      environment flags (diagnostics/ui/safe).
    - Otherwise, it applies the safe-mode defaults so behaviour matches
      upstream Kivy unless developers explicitly opt in elsewhere.
    """

    os.environ.setdefault(ENV_ENABLE_FLAG, "1")
    if profile:
        handler = PROFILE_MAP.get(profile.lower())
        if handler:
            return handler()
    return auto_enable_if_fork()


def enabled_via_env() -> bool:
    """Return True if the Protonox fork has been explicitly requested."""

    return (
        os.environ.get(ENV_ENABLE_FLAG) is not None
        or os.environ.get(LEGACY_ENABLE_FLAG) is not None
    )


def apply_env_profile() -> CompatReport:
    """Apply a profile based on environment variables if present."""

    profile = os.environ.get(ENV_PROFILE_FLAG)
    if profile and profile.lower() in PROFILE_MAP:
        return PROFILE_MAP[profile.lower()]()
    if enabled_via_env():
        return auto_enable_if_fork()
    return CompatReport(applied={}, flags={})


# Auto-apply safe mode only when the developer opted in via env flag and
# the fork is actually in use. Upstream installs remain untouched.
if enabled_via_env():
    apply_env_profile()

__all__ = [
    "enable",
    "enable_protonox",
    "enabled_via_env",
    "apply_env_profile",
    "enable_diagnostics",
    "enable_protonox_ui",
    "enable_safe_mode",
    "CompatReport",
    "is_protonox_runtime",
]

# Friendly alias for the activation helper referenced in docs.
enable_protonox = enable

# Allow the conceptual alias `import protonox_kivy` to resolve to this module
# without changing the distribution name.

sys.modules.setdefault("protonox_kivy", sys.modules[__name__])
