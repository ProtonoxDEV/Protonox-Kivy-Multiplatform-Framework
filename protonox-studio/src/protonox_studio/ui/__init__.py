"""Static UI assets and opt-in UI helpers bundled with Protonox Studio."""

from protonox_studio.ui.textinput_unicode import patch_textinput_unicode
from protonox_studio.ui.font_stack import get_font_stack, DEFAULT_ANDROID, DEFAULT_DESKTOP

__all__ = [
    "patch_textinput_unicode",
    "get_font_stack",
    "DEFAULT_ANDROID",
    "DEFAULT_DESKTOP",
]
