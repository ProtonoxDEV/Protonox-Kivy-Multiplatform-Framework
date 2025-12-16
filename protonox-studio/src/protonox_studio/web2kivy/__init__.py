"""Web→Kivy integration helpers for Protonox Studio.

This package tracks the execution plan described in the Web2Kivy
reference documents: mapping manifests, KV sanitization, navigation
extraction, UI-IR normalization, and batch hot-reload orchestration. The
implementations here are intentionally defensive so they can run in user
projects without mutating existing screens or controllers unless
explicitly requested.
"""

from .mapping import MappingManifest, ScreenBinding
from .exporters import KVSanitizer, SanitizedKV
from .hotreload import BatchReloader, FileChange, ReloadCallback, RollbackCallback
from .ui_ir import NormalizedNode, NormalizedUIModel, normalize_ui_model, sanitize_identifier
from .web_nav import NavEdge, NavGraph, extract_navigation

__all__ = [
    "BatchReloader",
    "FileChange",
    "KVSanitizer",
    "MappingManifest",
    "NavEdge",
    "NavGraph",
    "NormalizedNode",
    "NormalizedUIModel",
    "ReloadCallback",
    "RollbackCallback",
    "SanitizedKV",
    "ScreenBinding",
    "extract_navigation",
    "normalize_ui_model",
    "sanitize_identifier",
]
