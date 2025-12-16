"""Media widgets for Protonox (scaffolding).

Exports ProtonoxVideo, a unified API that will pick the best backend per
platform (ExoPlayer on Android, ffpyplayer/libVLC on desktop).
"""
from __future__ import annotations

from .protonox_video import ProtonoxVideo, build_backend

__all__ = ["ProtonoxVideo", "build_backend"]
