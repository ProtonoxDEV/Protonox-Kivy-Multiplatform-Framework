"""Dynamic screen handling for live Web→Kivy updates."""

from .registry import ScreenRegistry, ManifestEntry
from .dynamic_screen import DynamicScreen

__all__ = ["ScreenRegistry", "ManifestEntry", "DynamicScreen"]
