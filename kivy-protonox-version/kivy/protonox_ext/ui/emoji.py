"""Emoji-safe helpers (opt-in) for consistent rendering across platforms."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, Optional

from kivy.core.text import LabelBase
from kivy.logger import Logger

EMOJI_REGEX = re.compile(
    "[\U0001F600-\U0001F64F]|"  # emoticons
    "[\U0001F300-\U0001F5FF]|"  # symbols & pictographs
    "[\U0001F680-\U0001F6FF]|"  # transport & map
    "[\U0001F1E0-\U0001F1FF]"   # flags
)

DEFAULT_FONT_CANDIDATES = [
    "NotoColorEmoji.ttf",
    "NotoEmoji-Regular.ttf",
    "SegoeUIEmoji.ttf",
    "AppleColorEmoji.ttf",
]


def is_enabled(env: Optional[dict] = None) -> bool:
    environ = env or os.environ
    return environ.get("PROTONOX_EMOJI_FALLBACK", "0").lower() in {"1", "true", "yes", "on"}


def contains_emoji(text: str) -> bool:
    return bool(text and EMOJI_REGEX.search(text))


def register_emoji_font(font_path: Path, font_name: str = "ProtonoxEmoji") -> bool:
    if not font_path.exists():
        return False
    LabelBase.register(name=font_name, fn_regular=str(font_path))
    Logger.info("[EMOJI] Registered fallback font %s", font_path)
    return True


def find_emoji_font(search_paths: Iterable[Path]) -> Optional[Path]:
    for base in search_paths:
        for candidate in DEFAULT_FONT_CANDIDATES:
            path = base / candidate
            if path.exists():
                return path
    return None


def default_search_paths() -> list[Path]:
    home_fonts = Path.home() / ".local" / "share" / "fonts"
    system_paths = [Path("/usr/share/fonts"), Path("/System/Library/Fonts"), Path("C:/Windows/Fonts")]
    return [p for p in [home_fonts, *system_paths] if p.exists()]


def ensure_default_font(search_paths: Optional[Iterable[Path]] = None, font_name: str = "ProtonoxEmoji") -> Optional[str]:
    paths = list(search_paths) if search_paths else default_search_paths()
    found = find_emoji_font(paths)
    if not found:
        Logger.warning("[EMOJI] No fallback emoji font found in %s", paths)
        return None
    register_emoji_font(found, font_name=font_name)
    return font_name


def apply_fallback(widget, font_name: str = "ProtonoxEmoji", auto_detect: bool = True) -> bool:
    """Apply fallback font to a widget if it supports font_name and has emoji."""

    if not hasattr(widget, "font_name"):
        return False
    if auto_detect and hasattr(widget, "text") and not contains_emoji(str(widget.text)):
        return False
    try:
        widget.font_name = font_name
        return True
    except Exception as exc:  # pragma: no cover - defensive guard
        Logger.warning("[EMOJI] Failed to apply fallback: %s", exc)
        return False


def enable(widget, search_paths: Optional[Iterable[Path]] = None, font_name: str = "ProtonoxEmoji", auto_detect: bool = True) -> bool:
    if not is_enabled():
        Logger.debug("[EMOJI] Fallback disabled by env")
        return False
    active_font = font_name
    if not LabelBase.font_exists(font_name):
        resolved = ensure_default_font(search_paths=search_paths, font_name=font_name)
        if not resolved:
            return False
        active_font = resolved
    return apply_fallback(widget, font_name=active_font, auto_detect=auto_detect)


__all__ = [
    "apply_fallback",
    "contains_emoji",
    "enable",
    "ensure_default_font",
    "find_emoji_font",
    "is_enabled",
    "register_emoji_font",
]
