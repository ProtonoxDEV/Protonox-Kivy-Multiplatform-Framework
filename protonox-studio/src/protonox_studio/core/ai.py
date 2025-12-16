"""AI orchestration and caching layer for Protonox Studio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CACHE_DIR = Path(__file__).resolve().parents[2] / "protonox-cache"


class PromptCache:
    """Tiny filesystem-backed cache to avoid repeated prompts."""

    def __init__(self, storage: Path = CACHE_DIR):
        self.storage = storage
        self.storage.mkdir(parents=True, exist_ok=True)

    def _file_for(self, key: str) -> Path:
        return self.storage / f"{key}.json"

    def get(self, key: str) -> Dict[str, Any] | None:
        path = self._file_for(key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except Exception:
            return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        path = self._file_for(key)
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False))
