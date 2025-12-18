"""KV asset injector scaffolding for Protonox Studio.

Adds/updates a controlled block inside a KV file so Studio can append widgets
without touching user-owned code. This is intentionally minimal and safe.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from kivy.logger import Logger

BLOCK_START = "# --- PROTONOX_STUDIO:BEGIN media ---"
BLOCK_END = "# --- PROTONOX_STUDIO:END media ---"


class KVAssetInjector:
    """Insert media widgets inside a managed KV block."""

    def __init__(self, block_start: str = BLOCK_START, block_end: str = BLOCK_END) -> None:
        self.block_start = block_start
        self.block_end = block_end

    def insert_video(self, kv_path: Path, source: str, poster: str, controls: bool = True) -> Tuple[int, Path]:
        snippet = [
            "ProtonoxVideo:",
            f'    source: "{source}"',
            f'    poster: "{poster}"',
            f"    controls: {str(bool(controls))}",
        ]
        return self._insert_block(kv_path, snippet)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_block(self, lines: list[str]) -> list[str]:
        if self.block_start in lines and self.block_end in lines:
            return lines
        lines = lines[:]  # copy
        lines.append(self.block_start + "\n")
        lines.append(self.block_end + "\n")
        return lines

    def _insert_block(self, kv_path: Path, snippet: list[str]) -> Tuple[int, Path]:
        kv_path.parent.mkdir(parents=True, exist_ok=True)
        if kv_path.exists():
            lines = kv_path.read_text(encoding="utf-8").splitlines(keepends=True)
        else:
            lines = []
        lines = self._ensure_block(lines)
        try:
            end_idx = lines.index(self.block_end + "\n")
        except ValueError:
            Logger.error(f"protonox.injector: malformed block in {kv_path}")
            return (0, kv_path)

        insertion_point = end_idx
        insert_lines = [s + "\n" for s in snippet]
        lines[insertion_point:insertion_point] = insert_lines
        kv_path.write_text("".join(lines), encoding="utf-8")
        return (insertion_point + 1, kv_path)
