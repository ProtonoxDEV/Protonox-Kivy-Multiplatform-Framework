from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Iterable, Optional

from PIL import Image

from protonox_studio.web.paths import assets_manifest_path, imported_public_dir

log = logging.getLogger(__name__)

FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
HLS_SEGMENT_SECONDS = int(os.getenv("PROTONOX_HLS_SEGMENT_SECONDS", "4"))


def ensure_assets_manifest(base: Path | None = None) -> Path:
    base = base or Path.cwd()
    manifest_path = assets_manifest_path(base)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")
    return manifest_path


def _load_manifest(manifest_path: Path) -> Dict[str, object]:
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {"items": []}


def _write_manifest(manifest_path: Path, items: Iterable[dict]) -> None:
    manifest_path.write_text(json.dumps({"items": list(items)}, indent=2), encoding="utf-8")


def _run_ffmpeg(args: list[str]) -> bool:
    cmd = [FFMPEG_BIN] + args
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        log.warning("ffmpeg not found; skipping transcodes")
    except subprocess.CalledProcessError as exc:  # noqa: BLE001 - command error handled gracefully
        log.warning("ffmpeg failed (%s)", exc)
    return False


def _generate_webp(src: Path, dest: Path) -> Optional[Path]:
    try:
        with Image.open(src) as img:
            img.convert("RGB").save(dest, "WEBP", quality=90, method=6)
        return dest
    except Exception:
        log.warning("webp generation failed for %s", src)
        return None


def _transcode_mp4(src: Path, dest: Path) -> Optional[Path]:
    ok = _run_ffmpeg(
        [
            "-y",
            "-i",
            str(src),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-movflags",
            "+faststart",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(dest),
        ]
    )
    return dest if ok else None


def _transcode_hls(src: Path, dest_dir: Path) -> Optional[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    playlist = dest_dir / "index.m3u8"
    ok = _run_ffmpeg(
        [
            "-y",
            "-i",
            str(src),
            "-preset",
            "veryfast",
            "-g",
            "48",
            "-sc_threshold",
            "0",
            "-hls_time",
            str(HLS_SEGMENT_SECONDS),
            "-hls_playlist_type",
            "vod",
            "-hls_segment_filename",
            str(dest_dir / "segment%03d.ts"),
            str(playlist),
        ]
    )
    return playlist if ok else None


def _extract_poster(src: Path, dest: Path) -> Optional[Path]:
    ok = _run_ffmpeg(
        [
            "-y",
            "-i",
            str(src),
            "-ss",
            "00:00:00.000",
            "-vframes",
            "1",
            str(dest),
        ]
    )
    return dest if ok else None


def ingest_asset(src: Path, base: Path | None = None) -> Dict[str, object]:
    """Copy asset into public/protonox/imported, generate variants, and update manifest."""

    base = base or Path.cwd()
    target_root = imported_public_dir(base)
    target_root.mkdir(parents=True, exist_ok=True)

    uid = uuid.uuid4().hex[:8]
    ext = src.suffix.lower()
    stem = src.stem
    dest_dir = target_root / uid
    dest_dir.mkdir(parents=True, exist_ok=True)
    original = dest_dir / f"{stem}{ext}"
    shutil.copy2(src, original)

    entry = {
        "id": uid,
        "original_name": src.name,
        "path": str(original.relative_to(base)),
        "size": src.stat().st_size if src.exists() else 0,
        "type": ext.lstrip("."),
        "variants": [],
        "poster": None,
        "status": "processed",
    }

    if ext in {".png", ".jpg", ".jpeg", ".webp"}:
        webp_path = dest_dir / f"{stem}.webp"
        produced = _generate_webp(original, webp_path)
        if produced:
            entry["variants"].append({"kind": "webp", "path": str(produced.relative_to(base))})
    elif ext in {".mp4", ".mov", ".mkv", ".avi", ".m4v"}:
        mp4_path = dest_dir / f"{stem}.mp4"
        hls_dir = dest_dir / "hls"
        mp4_prod = _transcode_mp4(original, mp4_path)
        if mp4_prod:
            entry["variants"].append({"kind": "mp4", "path": str(mp4_prod.relative_to(base))})
        hls_playlist = _transcode_hls(original, hls_dir)
        if hls_playlist:
            entry["variants"].append({"kind": "hls", "path": str(hls_playlist.relative_to(base))})
        poster = _extract_poster(original, dest_dir / f"{stem}-poster.jpg")
        if poster:
            entry["poster"] = str(poster.relative_to(base))

    manifest_path = ensure_assets_manifest(base)
    data = _load_manifest(manifest_path)
    items = [i for i in data.get("items", []) or [] if i.get("id") != uid]
    items.append(entry)
    _write_manifest(manifest_path, items)
    return entry


def watch_assets(src_dir: Path, base: Path | None = None, patterns: Optional[set[str]] = None) -> None:
    """Watch a directory and ingest changed assets automatically."""

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except Exception as exc:  # pragma: no cover - optional runtime dependency
        print(f"[protonox] watchdog not available: {exc}")
        return

    base = base or Path.cwd()
    src_dir = Path(src_dir).resolve()
    patterns = patterns or {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mkv", ".avi", ".m4v"}

    class Handler(FileSystemEventHandler):
        def _should_handle(self, path: Path) -> bool:
            return path.suffix.lower() in patterns

        def on_created(self, event):  # noqa: ANN001 - watchdog signature
            if event.is_directory:
                return
            path = Path(event.src_path)
            if self._should_handle(path):
                log.info("[protonox] ingesting new asset: %s", path)
                ingest_asset(path, base=base)

        def on_modified(self, event):  # noqa: ANN001 - watchdog signature
            if event.is_directory:
                return
            path = Path(event.src_path)
            if self._should_handle(path):
                log.info("[protonox] re-ingesting asset: %s", path)
                ingest_asset(path, base=base)

    observer = Observer()
    handler = Handler()
    observer.schedule(handler, str(src_dir), recursive=True)
    observer.start()
    print(f"[protonox] watching assets under {src_dir}")
    try:
        import time

        while observer.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join(timeout=2)
