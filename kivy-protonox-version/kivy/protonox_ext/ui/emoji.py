"""Emoji-safe helpers (AUTO-enabled) for consistent rendering across platforms.

Protonox automatically detects and enables emoji font fallback. No env vars needed.
"""
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
    "[\U0001F1E0-\U0001F1FF]|"  # flags
    "[\U0001F900-\U0001F9FF]|"  # supplemental symbols
    "[\U00002600-\U000027BF]"   # miscellaneous symbols
)

DEFAULT_FONT_CANDIDATES = [
    "NotoColorEmoji.ttf",
    "NotoEmoji-Regular.ttf",
    "SegoeUIEmoji.ttf",
    "AppleColorEmoji.ttf",
    "Noto-Color-Emoji.ttf",
    "NotoColorEmoji.otf",
]

# Global state for emoji font
_EMOJI_FONT_REGISTERED = False
_EMOJI_FONT_NAME = "ProtonoxEmoji"


def is_enabled(env: Optional[dict] = None) -> bool:
    """Check if emoji support is enabled (default: True in Protonox)."""
    environ = env or os.environ
    # Protonox defaults to True, can be disabled with explicit flag
    return environ.get("PROTONOX_EMOJI_DISABLE", "0").lower() in {"0", "false", "no", "off"}


def contains_emoji(text: str) -> bool:
    return bool(text and EMOJI_REGEX.search(text))


def register_emoji_font(font_path: Path, font_name: str = "ProtonoxEmoji") -> bool:
    if not font_path.exists():
        return False
    LabelBase.register(name=font_name, fn_regular=str(font_path))
    Logger.info("[EMOJI] Registered fallback font %s", font_path)
    return True


def find_emoji_font(search_paths: Iterable[Path]) -> Optional[Path]:
    """Find emoji font in search paths using efficient recursive search.
    
    Uses os.walk to recursively search for emoji font files, with a depth limit
    to avoid traversing too deep into system directories.
    """
    import os
    
    for base in search_paths:
        base_str = str(base)
        if not os.path.isdir(base_str):
            continue
        
        try:
            # Use os.walk for efficient recursive search
            for root, dirs, files in os.walk(base_str, followlinks=False):
                # Limit depth to 5 levels
                depth = root[len(base_str):].count(os.sep)
                if depth > 5:
                    dirs.clear()  # Don't descend further
                    continue
                
                # Check for emoji fonts in this directory
                for candidate in DEFAULT_FONT_CANDIDATES:
                    if candidate in files:
                        return Path(root) / candidate
        except (OSError, PermissionError):
            # Skip directories we can't read
            pass
    
    return None


def default_search_paths() -> list[Path]:
    home_fonts = Path.home() / ".local" / "share" / "fonts"
    system_paths = [
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path("C:/Windows/Fonts"),
    ]
    # Kivy assets folder
    try:
        from kivy.resources import resource_find
        kivy_data_dir = Path(resource_find(""))
        if kivy_data_dir and kivy_data_dir.exists():
            system_paths.append(kivy_data_dir / "fonts")
    except Exception:
        pass
    return [p for p in [home_fonts, *system_paths] if p.exists()]


def ensure_default_font(search_paths: Optional[Iterable[Path]] = None, font_name: str = "ProtonoxEmoji") -> Optional[str]:
    """Ensure emoji font is registered. Returns the font name or None."""
    global _EMOJI_FONT_REGISTERED, _EMOJI_FONT_NAME
    
    if _EMOJI_FONT_REGISTERED:
        return _EMOJI_FONT_NAME
    
    paths = list(search_paths) if search_paths else default_search_paths()
    found = find_emoji_font(paths)
    if not found:
        Logger.warning("[EMOJI] No emoji font found in %s; emojis may not render", paths)
        return None
    
    register_emoji_font(found, font_name=font_name)
    _EMOJI_FONT_REGISTERED = True
    _EMOJI_FONT_NAME = font_name
    return font_name


def apply_fallback(widget, font_name: str = "ProtonoxEmoji", auto_detect: bool = True) -> bool:
    """Apply emoji font to widget if it contains emoji or auto_detect is False."""
    if not hasattr(widget, "font_name"):
        return False
    if auto_detect and hasattr(widget, "text") and not contains_emoji(str(widget.text)):
        return False
    try:
        widget.font_name = font_name
        Logger.debug("[EMOJI] Applied emoji font to %s", widget.__class__.__name__)
        return True
    except Exception as exc:
        Logger.debug("[EMOJI] Failed to apply font: %s", exc)
        return False


def enable(widget, search_paths: Optional[Iterable[Path]] = None, font_name: str = "ProtonoxEmoji", auto_detect: bool = True) -> bool:
    """Enable emoji rendering on a widget.
    
    Args:
        widget: Kivy widget with font_name support
        search_paths: Paths to search for emoji fonts
        font_name: Font name to use
        auto_detect: Only apply if widget contains emoji
    
    Returns:
        True if successfully applied, False otherwise
    """
    if not is_enabled():
        Logger.debug("[EMOJI] Emoji support disabled by user")
        return False
    
    active_font = font_name
    if not LabelBase.font_exists(font_name):
        resolved = ensure_default_font(search_paths=search_paths, font_name=font_name)
        if not resolved:
            # Emoji support unavailable, but don't fail
            Logger.debug("[EMOJI] Emoji font unavailable, using system default")
            return False
        active_font = resolved
    
    return apply_fallback(widget, font_name=active_font, auto_detect=auto_detect)


def auto_enable_globally(search_paths: Optional[Iterable[Path]] = None) -> bool:
    """Pre-register emoji font at app startup (called automatically by Protonox).
    
    This should be called during app initialization to ensure emoji fonts are
    available before widgets are created.
    
    Returns:
        True if emoji font was successfully registered, False otherwise
    """
    if not is_enabled():
        return False
    
    result = ensure_default_font(search_paths=search_paths)
    if result:
        Logger.info("[EMOJI] Emoji support initialized (font: %s)", result)
    return result is not None


__all__ = [
    "apply_fallback",
    "auto_enable_globally",
    "contains_emoji",
    "enable",
    "ensure_default_font",
    "find_emoji_font",
    "is_enabled",
    "register_emoji_font",
]
