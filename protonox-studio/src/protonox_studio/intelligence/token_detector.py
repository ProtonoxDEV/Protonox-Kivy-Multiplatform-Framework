"""Detection helpers for design tokens, typography scales and contrast."""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Tuple

from ..core.models import ElementBox


def _normalize_color(color: str) -> str:
    return color.strip().lower()


def detect_tokens(colors: List[str]) -> Dict[str, str]:
    normalized = [_normalize_color(c) for c in colors]
    counts = Counter(normalized)
    tokens = {}
    for i, (color, freq) in enumerate(counts.most_common(), start=1):
        tokens[f"token-{i}"] = color
    return {"tokens": tokens, "counts": counts}


def _rgb(color: str) -> Tuple[float, float, float]:
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join([c * 2 for c in color])
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    return r / 255, g / 255, b / 255


def _luminance(color: str) -> float:
    r, g, b = _rgb(color)

    def adj(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = adj(r), adj(g), adj(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast_ratio(c1: str, c2: str) -> float:
    l1, l2 = _luminance(c1), _luminance(c2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def contrast_guardian(colors: List[str]) -> Dict[str, object]:
    colors = [_normalize_color(c) for c in colors if c]
    violations = []
    for i, base in enumerate(colors):
        for other in colors[i + 1 :]:
            ratio = _contrast_ratio(base, other)
            if ratio < 4.5:
                violations.append({"pair": (base, other), "ratio": ratio})
    return {"pairs": len(colors), "violations": violations}


def detect_typography_scale(font_sizes: Iterable[float]) -> Dict[str, object]:
    sizes = sorted(fs for fs in font_sizes if fs)
    if not sizes:
        return {"scale": "desconocida", "confidence": 0.0}

    ratios = [sizes[i + 1] / sizes[i] for i in range(len(sizes) - 1) if sizes[i] > 0]
    if not ratios:
        return {"scale": "single", "confidence": 1.0}

    avg_ratio = sum(ratios) / len(ratios)
    known_scales = {1.25: "major third (1.25)", 1.333: "perfect fourth (1.333)", 1.5: "augmented fourth (1.5)"}
    closest = min(known_scales.keys(), key=lambda k: abs(k - avg_ratio))
    confidence = 1 - min(abs(closest - avg_ratio) / closest, 1)
    return {"scale": known_scales[closest], "confidence": round(confidence, 2), "average_ratio": round(avg_ratio, 3)}


def collect_font_sizes(elements: Iterable[ElementBox]) -> List[float]:
    sizes: List[float] = []
    for el in elements:
        for sample in el.text_samples:
            if isinstance(sample, (int, float)):
                sizes.append(float(sample))
    return sizes
