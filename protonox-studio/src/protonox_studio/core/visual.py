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


def _diff_ratio_for_region(diff_img: "Image.Image", box: tuple[int, int, int, int]) -> float:
    """Return a normalized diff ratio for a cropped region of the diff image."""

    region = diff_img.crop(box)
    if region.size[0] == 0 or region.size[1] == 0:
        return 0.0
    histogram = region.histogram()
    diff_pixels = sum(histogram[1:])
    total_pixels = region.size[0] * region.size[1] * len(region.getbands())
    return diff_pixels / total_pixels if total_pixels else 0.0


def _diff_elements_by_bounds(diff_img: "Image.Image", model: UIModel) -> list[dict]:
    """Compute per-element diff ratios using IR bounds as regions."""

    results: list[dict] = []
    width, height = diff_img.size
    if not model.screens:
        return results

    for node in model.screens[0].root.walk():
        if not node.bounds:
            continue
        x0 = max(int(node.bounds.x), 0)
        y0 = max(int(node.bounds.y), 0)
        x1 = min(int(node.bounds.x + node.bounds.width), width)
        y1 = min(int(node.bounds.y + node.bounds.height), height)
        if x1 <= x0 or y1 <= y0:
            continue
        ratio = _diff_ratio_for_region(diff_img, (x0, y0, x1, y1))
        results.append(
            {
                "id": node.identifier,
                "role": node.role,
                "bounds": {
                    "x": x0,
                    "y": y0,
                    "width": x1 - x0,
                    "height": y1 - y0,
                },
                "diff_ratio": round(ratio, 6),
            }
        )
    return results


def _save_overlay(canvas: "Image.Image", elements: list[dict], out_dir: Path) -> str:
    """Draw a color-coded overlay of element diffs and persist it."""

    overlay = canvas.copy().convert("RGBA")
    draw = ImageDraw.Draw(overlay, "RGBA")
    for element in elements:
        bounds = element.get("bounds") or {}
        x0, y0 = bounds.get("x", 0), bounds.get("y", 0)
        x1, y1 = x0 + bounds.get("width", 0), y0 + bounds.get("height", 0)
        ratio = element.get("diff_ratio", 0.0)
        # Clamp and map ratio to a red tint
        intensity = max(0.1, min(1.0, ratio * 10))
        fill = (255, 64, 64, int(60 * intensity))
        outline = (255, 64, 64, int(180 * intensity))
        draw.rectangle([x0, y0, x1, y1], outline=outline, width=2, fill=fill)
        draw.text((x0 + 4, y0 + 4), f"{element['id']} ({ratio:.4f})", fill=(255, 255, 255, 230))

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "visual_overlay.png"
    overlay.save(target)
    return str(target.resolve())


def diff_pngs(
    baseline: Path,
    candidate: Path,
    out_dir: Optional[Path] = None,
    ui_model: Optional[UIModel] = None,
) -> Dict[str, object]:
    """Compute a lightweight visual diff between two PNGs.

    Returns pixel-diff ratios and, if Pillow is available, writes a diff image
    for manual inspection. This is meant for reproducible reporting, not
    byte-perfect QA.
    """

    if Image is None or ImageChops is None:
        raise RuntimeError("Pillow es obligatorio para comparar PNGs en este entorno")

    element_diffs: list[dict] = []
    overlay_image: Optional[str] = None

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

        if ui_model and diff_img and status != "size-mismatch":
            element_diffs = _diff_elements_by_bounds(diff_img, ui_model)
            # Build overlay from the candidate image to visualize diffs by widget
            if out_dir:
                overlay_image = _save_overlay(cand_img, element_diffs, out_dir)

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
            "element_diffs": element_diffs,
            "overlay_image": overlay_image,
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
