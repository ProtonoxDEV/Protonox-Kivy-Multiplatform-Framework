"""PNG ingestion helpers for Protonox Studio."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

try:
    from PIL import Image, ImageChops
except Exception:  # pragma: no cover - optional dependency guard
    Image = None
    ImageChops = None

from .ui_model import UIModel


@dataclass
class PngCapture:
    path: Path
    width: int
    height: int

    def as_dict(self) -> Dict[str, object]:
        return {"path": str(self.path), "width": self.width, "height": self.height}


def ingest_png(path: Path) -> PngCapture:
    if not path.exists():
        raise FileNotFoundError(f"PNG no encontrado: {path}")
    if Image is None:
        raise RuntimeError("Pillow es obligatorio para leer PNG en este entorno")
    with Image.open(path) as img:
        width, height = img.size
    return PngCapture(path=path.resolve(), width=width, height=height)


def compare_png_to_model(png: PngCapture, model: UIModel) -> Dict[str, object]:
    if not model.screens:
        return {"status": "empty-model", "png": png.as_dict()}
    viewport = model.screens[0].viewport
    size_match = viewport.width == png.width and viewport.height == png.height
    return {
        "status": "ok" if size_match else "viewport-mismatch",
        "png": png.as_dict(),
        "viewport": {"width": viewport.width, "height": viewport.height},
    }


def diff_pngs(baseline: Path, candidate: Path, out_dir: Optional[Path] = None) -> Dict[str, object]:
    """Compute a lightweight visual diff between two PNGs.

    Returns pixel-diff ratios and, if Pillow is available, writes a diff image
    for manual inspection. This is meant for reproducible reporting, not
    byte-perfect QA.
    """

    if Image is None or ImageChops is None:
        raise RuntimeError("Pillow es obligatorio para comparar PNGs en este entorno")

    with Image.open(baseline) as base_img, Image.open(candidate) as cand_img:
        if base_img.size != cand_img.size:
            status = "size-mismatch"
            bbox = None
            diff_ratio = 1.0
            diff_img = None
        else:
            diff = ImageChops.difference(base_img, cand_img)
            bbox = diff.getbbox()
            histogram = diff.histogram()
            diff_pixels = sum(histogram[1:])
            total_pixels = base_img.size[0] * base_img.size[1] * len(base_img.getbands())
            diff_ratio = diff_pixels / total_pixels if total_pixels else 0.0
            status = "ok" if diff_ratio < 0.001 else "drift"
            diff_img = diff

        saved_diff = None
        if out_dir and diff_img:
            out_dir.mkdir(parents=True, exist_ok=True)
            diff_path = out_dir / "visual_diff.png"
            diff_img.save(diff_path)
            saved_diff = str(diff_path.resolve())

        return {
            "status": status,
            "baseline": str(Path(baseline).resolve()),
            "candidate": str(Path(candidate).resolve()),
            "bbox": bbox,
            "diff_ratio": round(diff_ratio, 6),
            "diff_image": saved_diff,
        }

