"""Shared data models for Protonox Studio."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ElementBox:
    """Normalized element box information coming from the page snapshot."""

    id: str
    x: float
    y: float
    width: float
    height: float
    padding: List[int] = field(default_factory=list)
    margin: List[int] = field(default_factory=list)
    color: Optional[str] = None
    text_samples: List[str] = field(default_factory=list)


@dataclass
class Viewport:
    width: int
    height: int
    safe_area: Dict[str, int] | None = None  # {top,right,bottom,left}