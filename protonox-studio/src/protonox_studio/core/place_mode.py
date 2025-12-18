"""Place mode stub: lets Studio choose a target widget before insertion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PlaceSelection:
    widget_id: Optional[str] = None
    kv_path: Optional[str] = None
    hint: Optional[str] = None


def select_target(_inspector) -> PlaceSelection:
    """Placeholder for interactive selection (returns empty for now)."""
    return PlaceSelection()
