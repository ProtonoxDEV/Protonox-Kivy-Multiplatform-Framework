"""Spacing analysis and AI Nudge style recommendations."""

from __future__ import annotations

from statistics import mean
from typing import Dict, Iterable, List, Tuple

from ..core.models import ElementBox


def _flatten(values: Iterable[int]) -> List[int]:
    return [v for v in values if isinstance(v, (int, float))]


def recommend_layout_spacing(elements: Iterable[ElementBox], grid: int = 8) -> Dict[str, object]:
    paddings: List[int] = []
    margins: List[int] = []
    for el in elements:
        paddings.extend(_flatten(el.padding))
        margins.extend(_flatten(el.margin))

    avg_padding = mean(paddings) if paddings else grid
    avg_margin = mean(margins) if margins else grid * 2

    snapped_padding = round(avg_padding / grid) * grid
    snapped_margin = round(avg_margin / grid) * grid

    return {
        "grid": grid,
        "recommendation": f"padding {snapped_padding}px · margin {snapped_margin}px",
        "raw": {"padding": paddings, "margin": margins},
        "ai_nudge": {
            "padding": snapped_padding,
            "margin": snapped_margin,
            "note": "Auto Perfect Spacing (AI Nudge) aplicado al promedio normalizado",
        },
    }


def auto_perfect_spacing(values: Iterable[int], grid: int = 8) -> Tuple[int, str]:
    values = _flatten(values)
    if not values:
        return grid, "Sin datos: se usa la grilla base"
    avg = mean(values)
    snapped = round(avg / grid) * grid
    return snapped, f"Promedio {avg:.1f}px ajustado a {snapped}px (grid {grid})"
