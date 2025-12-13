"""PNG ingestion helpers for Protonox Studio."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

try:
    from PIL import Image, ImageChops, ImageDraw
except Exception:  # pragma: no cover - optional dependency guard
    Image = None
    ImageChops = None
    ImageDraw = None

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


def render_model_to_png(model: UIModel, target: Path) -> Dict[str, object]:
    """Render the neutral UI model to a simple PNG for diffing and reports.

    This intentionally avoids mutating user code. It relies on bounding boxes
    present in the IR and draws lightweight rectangles to keep visual diffs
    reproducible even without a running browser or Kivy app.
    """

    if Image is None or ImageDraw is None:
        raise RuntimeError("Pillow es obligatorio para renderizar el modelo a PNG")

    if not model.screens:
        raise ValueError("El modelo UI no contiene pantallas renderizables")

    screen = model.screens[0]
    width, height = screen.viewport.width, screen.viewport.height
    img = Image.new("RGBA", (int(width), int(height)), (16, 16, 24, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for node in screen.root.walk():
        if not node.bounds:
            continue
        x0 = node.bounds.x
        y0 = node.bounds.y
        x1 = x0 + node.bounds.width
        y1 = y0 + node.bounds.height
        color = node.meta.get("color") if isinstance(node.meta, dict) else None
        fill = None
        if color and isinstance(color, str) and color.startswith("#") and len(color) in {7, 9}:
            try:
                rgba = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5)) + (80,)
                fill = rgba
            except Exception:
                fill = None
        draw.rectangle([x0, y0, x1, y1], outline=(88, 166, 255, 255), width=2, fill=fill)
        label = node.identifier[:20]
        draw.text((x0 + 4, y0 + 4), label, fill=(255, 255, 255, 230))

    target.parent.mkdir(parents=True, exist_ok=True)
    img.save(target)
    return {"status": "ok", "path": str(target.resolve()), "viewport": {"width": width, "height": height}}

