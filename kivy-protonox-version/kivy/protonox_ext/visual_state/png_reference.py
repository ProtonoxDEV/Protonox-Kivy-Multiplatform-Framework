"""PNG-aware visual helpers (opt-in) for Protonox Kivy builds.

The module avoids heavy computer vision; it focuses on basic alignment checks
using bounding boxes and optional image dimensions. All operations are gated by
PROTONOX_VISUAL_WARNINGS to stay out of production.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

try:
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency
    Image = None

VISUAL_WARNINGS = os.environ.get("PROTONOX_VISUAL_WARNINGS", "0") == "1"


@dataclass
class VisualWarning:
    message: str
    widget_id: Optional[str] = None

    def to_dict(self):
        return {"message": self.message, "widget": self.widget_id}


def compare_pngs(baseline: Path, candidate: Path) -> List[VisualWarning]:
    """Return coarse visual warnings comparing two PNGs.

    This avoids pixel-perfect diffing; instead it checks dimensions and reports
    mismatches to guide follow-up adjustments.
    """

    warnings: List[VisualWarning] = []
    if not VISUAL_WARNINGS or Image is None:
        return warnings
    if not baseline.exists() or not candidate.exists():
        return [VisualWarning(message="PNG missing for comparison")]

    try:
        with Image.open(baseline) as base_img, Image.open(candidate) as cand_img:
            if base_img.size != cand_img.size:
                warnings.append(
                    VisualWarning(
                        message=f"Resolution mismatch: baseline {base_img.size}, candidate {cand_img.size}",
                        widget_id=None,
                    )
                )
    except Exception:
        warnings.append(VisualWarning(message="Unable to read PNGs for comparison"))
    return warnings
