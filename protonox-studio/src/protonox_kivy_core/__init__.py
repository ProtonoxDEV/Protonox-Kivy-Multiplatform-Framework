"""Protonox Kivy Core facade.

Provides stable entrypoints (HotReloadAppBase, router contract, studio bridge)
so apps can depend on a shared runtime instead of inlining hot reload logic.
"""

from .hotreload import HotReloadAppBase, bootstrap_hot_reload_engine
from .router_contract import RouterContract
from .studio_bridge import StudioBridge

__all__ = [
    "HotReloadAppBase",
    "bootstrap_hot_reload_engine",
    "RouterContract",
    "StudioBridge",
]
