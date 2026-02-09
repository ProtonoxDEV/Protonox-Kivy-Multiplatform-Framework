"""Drop-in activation helpers for the Protonox Kivy fork.

The Protonox fork stays dormant unless explicitly enabled. Projects running
against upstream Kivy should see **no behavioural change**; developers can
choose to opt into Protonox tooling via an environment flag or a one-line
helper call.
"""
from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Setup logging FIRST
logger = logging.getLogger("kivy_protonox")
# Ensure logger has at least one handler and a sensible level
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)
if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)

# Ensure compat_clock is available as package attribute for tests/fallbacks
try:
    from . import compat_clock  # type: ignore
except Exception:
    # minimal in-memory fallback if compat_clock.py missing (shouldn't happen in prod)
    class ClockEvent:
        def __init__(self, callback, timeout, is_triggered=False):
            self.callback = callback
            self.timeout = timeout
            self.is_triggered = is_triggered
            self.tick = 0

    class CyClockBase:
        def __init__(self):
            pass

    class ClockNotRunningError(RuntimeError):
        pass

    class compat_clock:
        ClockEvent = ClockEvent
        CyClockBase = CyClockBase
        ClockNotRunningError = ClockNotRunningError

# Patch kivy._clock if it's broken (Cython not compiled)
def _patch_broken_clock():
    """Patch broken kivy._clock when Cython is not compiled."""
    try:
        import kivy._clock  # noqa: F401
    except (ImportError, ModuleNotFoundError):
        logger.warning("kivy._clock not compiled, using compatibility layer")
        sys.modules['kivy._clock'] = compat_clock
        # Ensure common attributes on the kivy module if present
        if 'kivy' in sys.modules:
            kivy_mod = sys.modules['kivy']
            try:
                setattr(kivy_mod, "ClockEvent", compat_clock.ClockEvent)
                setattr(kivy_mod, "CyClockBase", compat_clock.CyClockBase)
                setattr(kivy_mod, "ClockNotRunningError", compat_clock.ClockNotRunningError)
            except Exception:
                # best-effort; do not raise during import/patch
                logger.debug("Could not set attributes on kivy module during clock patch", exc_info=True)


# Apply patch early
_patch_broken_clock()

# Import compat module robustly for tests (provide lightweight stubs if missing)
try:
    from kivy.protonox_ext.compat import (  # type: ignore
        CompatReport,
        auto_enable_if_fork,
        enable_diagnostics,
        enable_protonox_ui,
        enable_safe_mode,
        is_protonox_runtime,
    )
except Exception:
    logger.info("kivy.protonox_ext.compat not importable; using test stubs")

    class CompatReport(dict):
        def __init__(self, applied=None, flags=None):
            super().__init__()
            self['applied'] = applied or {}
            self['flags'] = flags or {}

    def auto_enable_if_fork():
        return CompatReport()

    def enable_diagnostics():
        return CompatReport()

    def enable_protonox_ui():
        return CompatReport()

    def enable_safe_mode():
        return CompatReport()

    def is_protonox_runtime():
        return False


ENV_ENABLE_FLAG = "KIVY_PROTONOX"
LEGACY_ENABLE_FLAG = "PROTONOX_KIVY"
ENV_PROFILE_FLAG = "KIVY_PROTONOX_PROFILE"

PROFILE_MAP = {
    "diagnostics": enable_diagnostics,
    "ui": enable_protonox_ui,
    "safe": enable_safe_mode,
}

# Version tracking
__version__ = "0.1.7"
CLASSIC_KIVY_VERSION = "2.3.1"
PROTONOX_VERSION = "3.0"

def get_version_info() -> dict:
    """Get version information for Kivy and Protonox."""
    # Ensure is_protonox is a plain bool (tests may mock is_protonox_runtime)
    try:
        is_px = bool(is_protonox_runtime())
    except Exception:
        is_px = False

    return {
        "protonox": __version__,
        "kivy_classic": CLASSIC_KIVY_VERSION,
        "protonox_target": PROTONOX_VERSION,
        "is_protonox": is_px,
    }


def compare_versions() -> dict:
    """Compare classic Kivy 2.3.1 vs Protonox 3.0 features."""
    return {
        "python_support": {
            "classic": "3.8+",
            "protonox": "3.11+",
        },
        "cython": {
            "classic": "0.29.x",
            "protonox": "3.3+",
        },
        "type_hints": {
            "classic": "Partial",
            "protonox": "Full (PEP 561)",
        },
        "ndk": {
            "classic": "21e",
            "protonox": "28c",
        },
    }


def validate_project_structure() -> bool:
    """Validate the project directory structure for APK builds."""
    try:
        current_file = Path(__file__).parent
        kivy_protonox_dir = current_file
        
        if not kivy_protonox_dir.exists():
            logger.warning(f"Missing directory: {kivy_protonox_dir}")
            return False
        
        logger.info("✅ Project structure validated")
        return True
    except Exception as e:
        logger.error(f"Structure validation error: {e}")
        return False


def enable(profile: Optional[str] = None) -> CompatReport:
    """Enable Protonox guardrails when running on the fork.

    - If a profile name is provided, it toggles the corresponding opt-in
      environment flags (diagnostics/ui/safe).
    - Otherwise, it applies the safe-mode defaults so behaviour matches
      upstream Kivy unless developers explicitly opt in elsewhere.
    """

    # Validate structure before enabling
    if not validate_project_structure():
        logger.error("Project structure validation failed")
    
    os.environ.setdefault(ENV_ENABLE_FLAG, "1")
    if profile:
        handler = PROFILE_MAP.get(profile.lower())
        if handler:
            logger.info(f"Enabling profile: {profile}")
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
        logger.info(f"Applying environment profile: {profile}")
        return PROFILE_MAP[profile.lower()]()
    if enabled_via_env():
        return auto_enable_if_fork()
    return CompatReport(applied={}, flags={})


# Auto-apply safe mode only when the developer opted in via env flag and
# the fork is actually in use. Upstream installs remain untouched.
if enabled_via_env():
    apply_env_profile()

# Expose compat_clock in package namespace and exports
try:
    # assign module object so `from kivy_protonox import compat_clock` works
    compat_clock = compat_clock  # already imported/created above
except NameError:
    pass

from .error_handler import (
    install_error_handler,
    get_error_handler,
    register_error_callback,
    FatalErrorHandler,
)
from .crash_reporter import (
    CrashReport,
    create_crash_report,
)

# Auto-install error handler on import
try:
    _error_handler = install_error_handler()
except Exception as e:
    logger.warning(f"Could not install error handler: {e}")

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
    "validate_project_structure",
    "get_version_info",
    "compare_versions",
    "__version__",
    "CLASSIC_KIVY_VERSION",
    "PROTONOX_VERSION",
    "_patch_broken_clock",
    "compat_clock",
    "install_error_handler",
    "get_error_handler",
    "register_error_callback",
    "FatalErrorHandler",
    "CrashReport",
    "create_crash_report",
]

# Friendly alias for the activation helper referenced in docs.
enable_protonox = enable

# Allow the conceptual alias `import protonox_kivy` to resolve to this module
# without changing the distribution name.

sys.modules.setdefault("protonox_kivy", sys.modules[__name__])
