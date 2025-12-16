"""Runtime integration layer for Protonox Studio live exports.

This package stays opt-in via env flags and keeps all runtime hooks contained so
existing apps continue to behave normally unless enabled explicitly.
"""

from __future__ import annotations

RUNTIME_ENABLED_ENV = "PROTONOX_RUNTIME_LIVE"

__all__ = ["RUNTIME_ENABLED_ENV"]
