"""KV sanitization and helper utilities.

The exporter is intentionally conservative: it attempts lightweight
normalizations and records warnings instead of mutating aggressively.
This matches the "safe by default" posture from the Web2Kivy documents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Tuple

_POS_HINT_RE = re.compile(r"pos_hint\s*:\s*\{([^}]+)\}")
_ID_QUOTED_RE = re.compile(r"id:\s*'([^']+)'\s*")


@dataclass
class SanitizedKV:
    text: str
    warnings: List[str] = field(default_factory=list)
    normalized_ids: List[Tuple[str, str]] = field(default_factory=list)


class KVSanitizer:
    """Applies small, deterministic fixes to exported KV strings."""

    def __init__(self, viewport_height: int | None = None):
        self.viewport_height = viewport_height or 720

    def sanitize(self, kv_text: str, slug: str | None = None) -> SanitizedKV:
        warnings: List[str] = []
        normalized_ids: List[Tuple[str, str]] = []
        lines = kv_text.splitlines()
        sanitized_lines: List[str] = []

        for line in lines:
            # Normalize quoted ids to avoid builder collisions
            match_id = _ID_QUOTED_RE.search(line)
            if match_id:
                original = match_id.group(1)
                normalized = original.replace("-", "_")
                normalized_ids.append((original, normalized))
                line = _ID_QUOTED_RE.sub(f"id: {normalized}", line)
                warnings.append(f"Normalized id '{original}' to '{normalized}'")

            # Clamp pos_hint y values >1.0 to avoid runaway layouts
            match_pos = _POS_HINT_RE.search(line)
            if match_pos and "y" in match_pos.group(1):
                parts = match_pos.group(1).split(",")
                rebuilt = []
                clamped = False
                for part in parts:
                    if ":" not in part:
                        rebuilt.append(part)
                        continue
                    key, value = part.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    try:
                        numeric = float(value)
                    except Exception:
                        rebuilt.append(part)
                        continue
                    if key == "y" and numeric > 1:
                        numeric = 1.0
                        clamped = True
                    rebuilt.append(f"{key}: {numeric}")
                if clamped:
                    warnings.append("Clamped pos_hint.y to 1.0 to keep layout within viewport")
                line = line.replace(match_pos.group(0), f"pos_hint: {{{', '.join(rebuilt)}}}")

            sanitized_lines.append(line)

        if slug:
            warnings.append(f"KV sanitized for slug: {slug}")

        return SanitizedKV(text="\n".join(sanitized_lines), warnings=warnings, normalized_ids=normalized_ids)


__all__ = ["KVSanitizer", "SanitizedKV"]
