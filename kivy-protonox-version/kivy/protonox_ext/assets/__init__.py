"""Asset pipeline scaffolding for Protonox Studio.

Provides lightweight entrypoints to load presets and schedule processing jobs
without blocking the UI. This is intentionally minimal; concrete processors for
images/videos will be plugged in by Studio.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .pipeline import AssetProcessor, AssetPreset, AssetJob, load_presets

__all__ = ["AssetProcessor", "AssetPreset", "AssetJob", "load_presets"]


def presets_path(base: Optional[Path] = None) -> Path:
    """Return the default presets file path (optional base override)."""
    root = base or Path.cwd()
    return root / "protobots" / "assets" / "presets.yaml"
