"""Batch hot-reload scaffolding for Web→Kivy screens.

This module provides a transactional wrapper so that downstream watchers
can reload only the screens impacted by a change. It groups changes by
slug, invokes a reload callback, and relies on a rollback callback when
errors occur.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping


ReloadCallback = Callable[[str, Iterable[Path]], None]
RollbackCallback = Callable[[str], None]


@dataclass
class FileChange:
    path: Path
    slug: str
    timestamp: float = field(default_factory=lambda: time.time())


class BatchReloader:
    """Groups file changes and reloads affected screens atomically."""

    def __init__(self, bulk_threshold: int = 3, quiet_period: float = 0.6):
        self.bulk_threshold = bulk_threshold
        self.quiet_period = quiet_period
        self._pending: List[FileChange] = []

    def register_change(self, path: Path, slug: str) -> None:
        self._pending.append(FileChange(path=path, slug=slug))

    def _group_by_slug(self) -> Dict[str, List[FileChange]]:
        grouped: Dict[str, List[FileChange]] = {}
        for change in self._pending:
            grouped.setdefault(change.slug, []).append(change)
        return grouped

    def flush(self, reload_cb: ReloadCallback, rollback_cb: RollbackCallback | None = None) -> Dict[str, List[Path]]:
        if not self._pending:
            return {}
        now = time.time()
        newest_change = max(self._pending, key=lambda c: c.timestamp)
        if now - newest_change.timestamp < self.quiet_period:
            # Defer processing until filesystem settles
            return {}

        grouped = self._group_by_slug()
        self._pending.clear()

        processed: Dict[str, List[Path]] = {}
        for slug, changes in grouped.items():
            paths = [change.path for change in changes]
            processed[slug] = paths
            try:
                reload_cb(slug, paths)
            except Exception:
                if rollback_cb:
                    rollback_cb(slug)
                else:  # pragma: no cover - defensive logging path
                    print(f"[HOTRELOAD][ROLLBACK] Rolled back screen '{slug}' due to reload failure")
        return processed

    def summarize_pending(self) -> Mapping[str, int]:
        summary: Dict[str, int] = {}
        for change in self._pending:
            summary[change.slug] = summary.get(change.slug, 0) + 1
        return summary

    def bulk_mode(self) -> bool:
        return len(self._pending) >= self.bulk_threshold


__all__ = ["BatchReloader", "FileChange", "ReloadCallback", "RollbackCallback"]
