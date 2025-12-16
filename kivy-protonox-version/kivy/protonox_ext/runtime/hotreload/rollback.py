"""Rollback helpers built on existing hotreload_plus hooks."""

from __future__ import annotations

from ...hotreload_plus import hooks


def snapshot_runtime():
    return hooks.snapshot_runtime()


def rollback_runtime(snapshot) -> None:
    try:
        hooks.rollback(snapshot)
    except Exception:
        pass
