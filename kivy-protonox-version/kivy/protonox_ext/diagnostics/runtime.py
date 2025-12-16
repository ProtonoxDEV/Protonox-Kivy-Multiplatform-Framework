"""Runtime diagnostics (doctor-style) for the Protonox Kivy fork.

This is a **read-only**, opt-in module that inspects the running Kivy
environment and surfaces actionable warnings without mutating application
state. It is intended for developers who want to understand GPU/GL/window
capabilities, DPI scaling, and provider choices before enabling heavier
features.
"""
from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass, field
from typing import Dict, List

import kivy
from kivy.config import Config
from kivy.core.window import Window

try:  # Guard OpenGL inspection; not all platforms expose it.
    from kivy.core.gl import gl_info
except Exception:  # pragma: no cover - platform specific
    gl_info = None

RUNTIME_FLAG = os.environ.get("PROTONOX_RUNTIME_DIAGNOSTICS", "0").lower() in {"1", "true", "yes"}


@dataclass
class DiagnosticItem:
    key: str
    status: str
    message: str
    meta: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        payload = {
            "key": self.key,
            "status": self.status,
            "message": self.message,
        }
        if self.meta:
            payload["meta"] = self.meta
        return payload


@dataclass
class DiagnosticReport:
    summary: str
    platform: str
    python: str
    kivy_version: str
    window_backend: str
    resolution: Dict[str, int]
    dpi: float | None
    items: List[DiagnosticItem]

    def to_dict(self) -> Dict[str, object]:
        return {
            "summary": self.summary,
            "platform": self.platform,
            "python": self.python,
            "kivy_version": self.kivy_version,
            "window_backend": self.window_backend,
            "resolution": self.resolution,
            "dpi": self.dpi,
            "items": [item.to_dict() for item in self.items],
        }


def _gl_diagnostics(items: List[DiagnosticItem]) -> None:
    if not gl_info:
        items.append(
            DiagnosticItem(
                key="opengl",
                status="warning",
                message="OpenGL info not available on this platform",
            )
        )
        return

    try:
        items.append(
            DiagnosticItem(
                key="opengl",
                status="ok",
                message=f"OpenGL {gl_info.get_version()} ({gl_info.get_vendor()} / {gl_info.get_renderer()})",
                meta={
                    "version": gl_info.get_version(),
                    "vendor": gl_info.get_vendor(),
                    "renderer": gl_info.get_renderer(),
                },
            )
        )
    except Exception as exc:  # pragma: no cover - defensive
        items.append(
            DiagnosticItem(
                key="opengl",
                status="warning",
                message=f"Unable to query OpenGL info: {exc}",
            )
        )


def _window_diagnostics(items: List[DiagnosticItem]) -> Dict[str, object]:
    dpi = getattr(Window, "dpi", None)
    backend = Config.get("kivy", "window") if Config.has_option("kivy", "window") else ""
    resolution = {"width": Window.width, "height": Window.height}

    if dpi and dpi < 110:
        items.append(
            DiagnosticItem(
                key="dpi_scaling",
                status="warning",
                message="DPI appears low; verify scaling for high-density targets",
                meta={"dpi": dpi},
            )
        )
    if backend:
        items.append(
            DiagnosticItem(
                key="window_provider",
                status="info",
                message=f"Window provider: {backend}",
            )
        )

    return {"dpi": dpi, "resolution": resolution, "window_backend": backend}


def collect_runtime_diagnostics() -> DiagnosticReport:
    """Collect runtime diagnostics without mutating the app."""

    if not RUNTIME_FLAG:
        return DiagnosticReport(
            summary="Runtime diagnostics disabled",
            platform=sys.platform,
            python=sys.version.split()[0],
            kivy_version=kivy.__version__,
            window_backend=Config.get("kivy", "window") if Config.has_option("kivy", "window") else "",
            resolution={"width": Window.width, "height": Window.height},
            dpi=getattr(Window, "dpi", None),
            items=[],
        )

    items: List[DiagnosticItem] = []
    _gl_diagnostics(items)
    window_meta = _window_diagnostics(items)

    # Provider hints
    if platform.system().lower().startswith("linux") and "wayland" in os.environ.get("XDG_SESSION_TYPE", "").lower():
        items.append(
            DiagnosticItem(
                key="wayland_hint",
                status="info",
                message="Wayland session detected; SDL2/Kivy may fall back to XWayland.",
            )
        )

    summary = "Runtime diagnostics completed"
    return DiagnosticReport(
        summary=summary,
        platform=sys.platform,
        python=sys.version.split()[0],
        kivy_version=kivy.__version__,
        window_backend=window_meta.get("window_backend", ""),
        resolution=window_meta.get("resolution", {"width": Window.width, "height": Window.height}),
        dpi=window_meta.get("dpi"),
        items=items,
    )


def as_lines(report: DiagnosticReport) -> List[str]:
    """Human-friendly lines for CLI output."""

    lines = [
        f"Platform: {report.platform} | Python {report.python} | Kivy {report.kivy_version}",
        f"Window backend: {report.window_backend or 'default'} | Resolution: {report.resolution['width']}x{report.resolution['height']} | DPI: {report.dpi}",
        report.summary,
    ]
    for item in report.items:
        line = f"[{item.status.upper()}] {item.key}: {item.message}"
        if item.meta:
            line += f" ({item.meta})"
        lines.append(line)
    return lines


def main() -> None:  # pragma: no cover - convenience CLI
    report = collect_runtime_diagnostics()
    for line in as_lines(report):
        print(line)


if __name__ == "__main__":
    main()
