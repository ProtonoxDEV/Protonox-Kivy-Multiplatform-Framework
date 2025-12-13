"""Protonox extensions for the Kivy 2.3.1 fork.

All additions are opt-in and live outside the core to preserve backward
compatibility. Production apps see no behavioural changes unless the developer
explicitly imports and enables these helpers.
"""

from .telemetry import collect_layout_report, export_widget_tree, persist_layout_report, safe_export_to_png
from .layout_engine import antipatterns, fingerprint, introspect
from .inspector import overlay, runtime
from .kv_bridge import compiler, ir
from .hotreload_plus import hooks
from .web_mapper import dom_bridge
from .visual_state import freeze, png_reference, snapshot
from .android_bridge import adb
from .ui import emoji

__all__ = [
    "collect_layout_report",
    "export_widget_tree",
    "persist_layout_report",
    "safe_export_to_png",
    "antipatterns",
    "fingerprint",
    "introspect",
    "runtime",
    "overlay",
    "compiler",
    "ir",
    "hooks",
    "dom_bridge",
    "png_reference",
    "freeze",
    "snapshot",
    "adb",
    "emoji",
]
