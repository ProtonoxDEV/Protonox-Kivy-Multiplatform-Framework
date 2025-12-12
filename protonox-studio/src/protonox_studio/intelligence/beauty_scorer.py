"""Compute a visual harmony score from the aggregated signals."""

from __future__ import annotations

from typing import Dict


def _penalty_for_contrast(contrast: Dict[str, object]) -> int:
    violations = contrast.get("violations", []) if contrast else []
    return min(30, len(violations) * 5)


def _penalty_for_safe_area(safe_area_blocks) -> int:
    hits = 0
    for block in safe_area_blocks or []:
        if any(block.get("violations", {}).values()):
            hits += 1
    return min(20, hits * 3)


def score(data: Dict[str, object]) -> int:
    base = 100
    base -= _penalty_for_contrast(data.get("contrast"))
    base -= _penalty_for_safe_area(data.get("safe"))

    spacing = data.get("spacing", {})
    if spacing and spacing.get("grid") not in {8, 4}:
        base -= 5

    tokens = data.get("tokens", {}).get("tokens", {})
    if len(tokens) < 2:
        base -= 5

    return max(0, min(100, int(base)))
