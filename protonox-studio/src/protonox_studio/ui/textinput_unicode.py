"""Unicode-safe TextInput helpers (opt-in)."""

from __future__ import annotations

import unicodedata

from kivy.uix.textinput import TextInput

from protonox_studio.flags import is_enabled
from protonox_studio.devtools.logger import prefixed_logger

UI_LOG = prefixed_logger("ui")


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def patch_textinput_unicode() -> None:
    """Normalize inserted text and clipboard paste operations."""

    if not is_enabled("TEXTINPUT_UNICODE", False):
        return

    UI_LOG.info("Unicode TextInput patch enabled")
    original_insert = TextInput.insert_text

    def insert_text(self, substring: str, from_undo: bool = False):  # type: ignore[override]
        normalized = _normalize(substring)
        return original_insert(self, normalized, from_undo=from_undo)

    TextInput.insert_text = insert_text  # type: ignore[assignment]


__all__ = ["patch_textinput_unicode"]
