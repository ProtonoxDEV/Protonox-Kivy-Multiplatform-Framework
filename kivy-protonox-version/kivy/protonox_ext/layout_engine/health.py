"""Layout health scoring for Protonox Kivy builds.

This module is strictly opt-in and aggregates existing telemetry, symmetry
signals, and anti-pattern checks into a single score so teams can spot layout
entropy early. Core Kivy behaviour remains untouched.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from kivy.uix.widget import Widget

from .antipatterns import AntiPattern, detect_antipatterns
from .fingerprint import symmetry_report
from ..telemetry import PROTONOX_TELEMETRY, collect_layout_report

HEALTH_FLAG = os.environ.get("PROTONOX_LAYOUT_HEALTH", "0").lower() in {"1", "true", "yes"}


@dataclass
class LayoutHealth:
    score: float
    widgets: int
    overflow: int
    symmetry: Optional[float]
    issues: List[AntiPattern]

    def to_dict(self) -> Dict[str, object]:
        return {
            "score": round(self.score, 1),
            "widgets": self.widgets,
            "overflow": self.overflow,
            "symmetry": self.symmetry,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _score_from_issues(issues: Iterable[AntiPattern]) -> float:
    penalty = 0.0
    for issue in issues:
        if issue.code.startswith("nested_boxlayout"):
            penalty += 5.0
        elif issue.code == "dpi_overflow":
            penalty += 7.0
        else:
            penalty += 3.0
    return penalty


def _overflow_penalty(overflow_count: int) -> float:
    if overflow_count == 0:
        return 0.0
    return min(overflow_count * 2.5, 20.0)


def _symmetry_score(widget: Widget) -> Optional[float]:
    scores = symmetry_report(widget)
    if not scores:
        return None
    return round(sum(s.score for s in scores) / len(scores), 2)


def compute_layout_health(widget: Widget) -> Optional[LayoutHealth]:
    if not (PROTONOX_TELEMETRY and HEALTH_FLAG):
        return None

    metrics = collect_layout_report(widget)
    issues = detect_antipatterns(widget)
    overflow = len([m for m in metrics if m.overflow])

    score = 100.0
    score -= _score_from_issues(issues)
    score -= _overflow_penalty(overflow)

    sym_score = _symmetry_score(widget)
    if sym_score is not None:
        score -= max(0.0, (100.0 - sym_score) * 0.1)

    return LayoutHealth(
        score=max(0.0, min(100.0, score)),
        widgets=len(metrics),
        overflow=overflow,
        symmetry=sym_score,
        issues=issues,
    )


__all__ = ["LayoutHealth", "compute_layout_health"]
