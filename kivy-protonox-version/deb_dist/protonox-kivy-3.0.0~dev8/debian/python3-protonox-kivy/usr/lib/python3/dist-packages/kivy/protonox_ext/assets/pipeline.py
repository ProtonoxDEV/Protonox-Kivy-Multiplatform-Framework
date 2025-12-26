"""Async-friendly asset processing stubs.

This module defines light-weight dataclasses and a coordinator that will later
run ffmpeg/imagemagick style jobs off the UI thread. For now it exposes a
predictable API so Studio can integrate drag/drop and injection flows without
blocking.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import yaml
from kivy.logger import Logger


@dataclass
class AssetPreset:
    name: str
    options: Dict[str, object] = field(default_factory=dict)


@dataclass
class AssetJob:
    source: Path
    preset: str
    kind: str
    future: Future | None = None
    output_dir: Path | None = None
    manifest: Dict[str, object] | None = None


DEFAULT_PRESETS = {
    "hero": {"max_w": 1200, "max_h": 700, "format": "webp"},
    "icon": {"size": 256, "format": "png"},
    "video_hq": {"height": 1080, "bitrate": "5M"},
    "video_mobile": {"height": 720, "bitrate": "2.5M"},
}


def load_presets(path: Path) -> Dict[str, AssetPreset]:
    if not path.exists():
        return {name: AssetPreset(name, opts) for name, opts in DEFAULT_PRESETS.items()}
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - YAML errors should not crash UI
        Logger.warning(f"protonox.assets: Failed to read presets at {path}: {exc}")
        return {name: AssetPreset(name, opts) for name, opts in DEFAULT_PRESETS.items()}
    presets = raw.get("presets", raw) or {}
    return {name: AssetPreset(name, opts or {}) for name, opts in presets.items()}


class AssetProcessor:
    """Schedules asset processing jobs off the UI thread.

    Real transcoding/resizing will be implemented later; this scaffolding keeps
    the API stable for Studio integrations.
    """

    def __init__(self, presets: Optional[Dict[str, AssetPreset]] = None, workers: int = 2):
        self.presets = presets or {name: AssetPreset(name, opts) for name, opts in DEFAULT_PRESETS.items()}
        self.executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="protonox-assets")

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False)

    def process_video(self, source: Path, preset: str = "video_hq", output_dir: Optional[Path] = None) -> AssetJob:
        return self._submit("video", source, preset, output_dir)

    def process_image(self, source: Path, preset: str = "hero", output_dir: Optional[Path] = None) -> AssetJob:
        return self._submit("image", source, preset, output_dir)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _submit(self, kind: str, source: Path, preset: str, output_dir: Optional[Path]) -> AssetJob:
        job = AssetJob(source=source, preset=preset, kind=kind, output_dir=output_dir)
        job.future = self.executor.submit(self._noop_process, job)
        return job

    def _noop_process(self, job: AssetJob) -> AssetJob:
        # Placeholder: later this will call ffmpeg/imagemagick. For now we just
        # write a stub manifest so callers can test the integration path.
        try:
            manifest = {
                "source": str(job.source),
                "preset": job.preset,
                "kind": job.kind,
                "outputs": {},
            }
            if job.output_dir:
                job.output_dir.mkdir(parents=True, exist_ok=True)
                (job.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            job.manifest = manifest
        except Exception as exc:  # noqa: BLE001 - avoid crashing threads
            Logger.exception(f"protonox.assets: job failed ({job.kind}): {exc}")
        return job
