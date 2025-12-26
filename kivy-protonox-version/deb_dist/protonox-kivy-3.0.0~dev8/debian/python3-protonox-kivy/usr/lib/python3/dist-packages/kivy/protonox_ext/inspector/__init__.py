"""Inspector helpers (dev-only, opt-in)."""

from .overlay import overlay_payload, suggest_kv_patch
from .runtime import inspect_widget_tree, persist_inspection

__all__ = ["inspect_widget_tree", "persist_inspection", "overlay_payload", "suggest_kv_patch"]
