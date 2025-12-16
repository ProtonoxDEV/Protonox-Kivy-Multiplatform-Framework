from __future__ import annotations

from pathlib import Path


def protonox_dir(base: Path | None = None) -> Path:
    base = base or Path.cwd()
    return base / ".protonox"


def assets_dir(base: Path | None = None) -> Path:
    return protonox_dir(base) / "assets"


def assets_manifest_path(base: Path | None = None) -> Path:
    return protonox_dir(base) / "assets.manifest.json"


def imported_public_dir(base: Path | None = None) -> Path:
    return (base or Path.cwd()) / "public" / "protonox" / "imported"
