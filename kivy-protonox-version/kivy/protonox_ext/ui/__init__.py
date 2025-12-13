"""UI helpers for Protonox extensions (opt-in)."""

from .emoji import (
    apply_fallback,
    contains_emoji,
    enable,
    ensure_default_font,
    find_emoji_font,
    is_enabled,
    register_emoji_font,
)

__all__ = [
    "apply_fallback",
    "contains_emoji",
    "enable",
    "ensure_default_font",
    "find_emoji_font",
    "is_enabled",
    "register_emoji_font",
]
