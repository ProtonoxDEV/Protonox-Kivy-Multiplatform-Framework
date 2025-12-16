"""Router contract expected by Protonox Kivy Core.

Any app root/router can opt in by implementing these methods; absence should
trigger safe fallbacks (full rebuild or no-op navigation).
"""

from __future__ import annotations

from typing import Protocol


class RouterContract(Protocol):
    def has_screen(self, name: str) -> bool:  # pragma: no cover - interface only
        ...

    def navigate(self, name: str) -> None:  # pragma: no cover - interface only
        ...

    def partial_reload_screen(self, name: str) -> None:  # pragma: no cover - interface only
        ...
