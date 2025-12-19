"""Protonox Studio engine – segunda etapa evolutiva.

This iteration wires the intelligence helpers into a single orchestration
surface. The goal is to deliver actionable audit output for the UI panel,
CLI, and future live overlays without blocking on network calls.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from ..intelligence import beauty_scorer, grid_engine, spacing_analyzer, token_detector
from .models import ElementBox, Viewport


class ProtonoxEngine:
    """Aggregates all analyzers and returns a single structured report."""

    def __init__(self, grid_size: int = 8, baseline: int = 4) -> None:
        self.grid_size = grid_size
        self.baseline = baseline

    def audit(self, elements: Iterable[ElementBox], viewport: Viewport) -> Dict[str, Any]:
        elems = list(elements)
        colors = [e.color for e in elems if e.color]
        font_sizes = token_detector.collect_font_sizes(elems)

        grid_snaps = [grid_engine.snap_element(e, grid=self.grid_size, baseline=self.baseline) for e in elems]
        golden = [grid_engine.golden_ratio_suggestion(e) for e in elems]
        safe_flags = [grid_engine.safe_area_violations(e, viewport) for e in elems]
        breakpoints = [grid_engine.breakpoint_magic(e, viewport) for e in elems]

        spacing_rec = spacing_analyzer.recommend_layout_spacing(elems, grid=self.grid_size)
        scale_info = token_detector.detect_typography_scale(font_sizes)
        token_map = token_detector.detect_tokens(colors)
        contrast = token_detector.contrast_guardian(colors)

        score = beauty_scorer.score(
            {
                "grid": grid_snaps,
                "spacing": spacing_rec,
                "tokens": token_map,
                "contrast": contrast,
                "safe": safe_flags,
            }
        )

        return {
            "meta": {
                "grid": self.grid_size,
                "baseline": self.baseline,
                "viewport": {"width": viewport.width, "height": viewport.height},
            },
            "grid": grid_snaps,
            "golden_ratio": golden,
            "safe_area": safe_flags,
            "breakpoints": breakpoints,
            "spacing": spacing_rec,
            "typography_scale": scale_info,
            "tokens": token_map,
            "contrast": contrast,
            "score": score,
        }

    def summarize(self, audit: Dict[str, Any]) -> str:
        """Human-friendly summary for CLI output or panel headline."""
        blocks = []
        scale = audit.get("typography_scale", {})
        score = audit.get("score", 0)
        spacing = audit.get("spacing", {})

        blocks.append(f"Armonía visual: {score}/100")
        if scale:
            blocks.append(
                f"Tipografía: escala detectada {scale.get('scale', 'custom')} (confianza {scale.get('confidence', 0):.2f})"
            )
        if spacing:
            blocks.append(f"Espaciado: grid {spacing.get('grid')}px → {spacing.get('recommendation')}")
        if audit.get("contrast"):
            low = [c for c in audit["contrast"].get("violations", [])]
            if low:
                blocks.append(f"Contraste: {len(low)} violaciones (<4.5:1)")
        return " | ".join(blocks)


def bootstrap_engine() -> ProtonoxEngine:
    """Factory used by CLI and future UI bridge."""
    return ProtonoxEngine()
