"""Centralized feature flag utilities for Protonox tooling.

Flags are sourced from environment variables using the ``PROTONOX_`` prefix
and are intentionally opt-in to avoid altering production behavior by
default. The helper keeps parsing lightweight and side-effect free so it can
be safely imported in any context (including build scripts).
"""
from __future__ import annotations

import os
from typing import Optional


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


def get(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return the raw string value for a Protonox flag.

    Flags are read from environment variables prefixed with ``PROTONOX_``.
    The lookup is case-insensitive on the provided ``name`` but will respect
    the exact environment variable casing to avoid surprising overrides.
    """

    key = f"PROTONOX_{name}"
    for candidate in (key, key.upper(), key.lower()):
        if candidate in os.environ:
            return os.environ[candidate]
    return default


def is_enabled(name: str, default: bool = False) -> bool:
    """Return ``True`` if the given flag is enabled.

    Truthy values: ``1``, ``true``, ``yes``, ``on`` (case-insensitive).
    Falsy values: ``0``, ``false``, ``no``, ``off`` (case-insensitive).
    Unset flags fall back to ``default``.
    """

    raw = get(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    return default


__all__ = ["get", "is_enabled"]
