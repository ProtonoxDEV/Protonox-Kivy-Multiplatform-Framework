"""Plugin interfaces for exporters/adapters (extensible runtime hooks)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any


class ExporterPlugin(Protocol):
    name: str

    def supports(self, capabilities: dict[str, Any]) -> bool:
        ...

    def load(self, export_dir: str) -> None:
        ...


class ScreenAdapter(Protocol):
    def build_screen(self, screen_id: str, ui_model_path: str):
        ...

    def replace_screen(self, manager, screen_id: str, widget) -> None:
        ...


@dataclass
class SandboxPolicy:
    allowed_imports: tuple[str, ...] = ("kivy", "kivymd", "protonox_studio")
    allow_fs_write: bool = False

    def is_allowed_import(self, module: str) -> bool:
        return module.startswith(self.allowed_imports)
