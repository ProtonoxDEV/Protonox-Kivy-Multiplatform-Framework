"""Platform-aware font stack helper (opt-in)."""

from __future__ import annotations

from typing import List, Optional

from kivy.utils import platform

DEFAULT_ANDROID = [
    "Roboto",
    "NotoSans-Regular",
    "NotoColorEmoji.ttf",
]
DEFAULT_DESKTOP = [
    "Arial",
    "Segoe UI",
    "Noto Sans",
    "Noto Color Emoji",
]


def get_font_stack(target_platform: Optional[str] = None) -> List[str]:
    """Return a conservative font stack for the current platform."""

    target = target_platform or platform
    if target in ("android", "android_emulator"):
        return DEFAULT_ANDROID
    return DEFAULT_DESKTOP


__all__ = ["get_font_stack", "DEFAULT_ANDROID", "DEFAULT_DESKTOP"]
