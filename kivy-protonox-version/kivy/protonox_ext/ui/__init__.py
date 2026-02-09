"""UI helpers for Protonox extensions (auto-enabled emoji support)."""

from .emoji import (
    apply_fallback,
    auto_enable_globally,
    contains_emoji,
    enable,
    ensure_default_font,
    find_emoji_font,
    is_enabled,
    register_emoji_font,
)
from .emoji_autohook import install_hooks

__all__ = [
    "apply_fallback",
    "auto_enable_globally",
    "contains_emoji",
    "enable",
    "ensure_default_font",
    "find_emoji_font",
    "install_hooks",
    "is_enabled",
    "register_emoji_font",
]
