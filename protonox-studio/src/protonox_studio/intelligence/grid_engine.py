"""Grid intelligence: 8px snapping, baseline lock, golden ratio hints."""

from __future__ import annotations

from typing import Dict

from ..core.models import ElementBox, Viewport

GOLDEN_RATIO = 1.618


def snap_to_grid(value: float, grid: int = 8) -> float:
    return round(value / grid) * grid


def snap_element(box: ElementBox, grid: int = 8, baseline: int = 4) -> Dict[str, float]:
    snapped_x = snap_to_grid(box.x, grid)
    snapped_y = snap_to_grid(box.y, grid)
    snapped_w = snap_to_grid(box.width, grid)
    snapped_h = snap_to_grid(box.height, grid)
    baseline_h = snap_to_grid(box.height, baseline)
    return {
        "id": box.id,
        "x": snapped_x,
        "y": snapped_y,
        "width": snapped_w,
        "height": snapped_h,
        "baseline_height": baseline_h,
        "delta": {
            "x": snapped_x - box.x,
            "y": snapped_y - box.y,
            "width": snapped_w - box.width,
            "height": snapped_h - box.height,
        },
    }


def golden_ratio_suggestion(box: ElementBox) -> Dict[str, float]:
    target_height = round(box.width / GOLDEN_RATIO, 2)
    target_width = round(box.height * GOLDEN_RATIO, 2)
    return {
        "id": box.id,
        "target_height": target_height,
        "target_width": target_width,
        "current_ratio": round(box.width / max(box.height, 1), 3),
    }


def safe_area_violations(box: ElementBox, viewport: Viewport) -> Dict[str, bool]:
    safe = viewport.safe_area or {"top": 0, "right": 0, "bottom": 0, "left": 0}
    violations = {
        "top": box.y < safe.get("top", 0),
        "left": box.x < safe.get("left", 0),
        "right": box.x + box.width > viewport.width - safe.get("right", 0),
        "bottom": box.y + box.height > viewport.height - safe.get("bottom", 0),
    }
    return {"id": box.id, "violations": violations, "safe_area": safe}


def breakpoint_magic(box: ElementBox, viewport: Viewport) -> Dict[str, str]:
    guidance = "stable"
    if viewport.width < 640 and box.width > viewport.width * 0.8:
        guidance = "usar ancho completo en móvil"
    elif viewport.width < 960 and box.width > viewport.width * 0.6:
        guidance = "considera stacking en tablet"
    elif viewport.width >= 1280 and box.width < viewport.width * 0.25:
        guidance = "puede crecer para aprovechar desktop"
    return {"id": box.id, "recommendation": guidance}


def focus_visualizer(box: ElementBox, order: int) -> Dict[str, int]:
    return {"id": box.id, "tab_index": order}
