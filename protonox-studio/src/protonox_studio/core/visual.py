"""PNG ingestion helpers for Protonox Studio."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

try:
    from PIL import Image
except Exception:  # pragma: no cover - optional dependency guard
    Image = None

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

