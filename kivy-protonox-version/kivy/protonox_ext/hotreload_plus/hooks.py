"""Additional hot reload scaffolding that complements Kivy's runtime.

The hooks are deliberately minimal and opt-in. They snapshot modules and KV
registries so Protonox Studio can attempt advanced reloads while providing a
clear rollback path if something goes wrong.
"""
from __future__ import annotations

import copy
import sys
from dataclasses import dataclass
from typing import Dict

from kivy.factory import Factory
from kivy.lang import Builder


@dataclass
class ReloadSnapshot:
    modules: Dict[str, object]
    factory: Dict[str, object]
    rulectx: Dict[str, object]


def snapshot_runtime() -> ReloadSnapshot:
    return ReloadSnapshot(
        modules=dict(sys.modules),
        factory=copy.deepcopy(getattr(Factory, "classes", {})),
        rulectx=copy.deepcopy(getattr(Builder, "rulectx", {})),
    )


def rollback(snapshot: ReloadSnapshot) -> None:
    sys.modules.clear()
    sys.modules.update(snapshot.modules)
    Factory.classes.clear()
    Factory.classes.update(snapshot.factory)
    Builder.rulectx.clear()
    Builder.rulectx.update(snapshot.rulectx)


def safe_unload_module(module_name: str) -> None:
    if module_name in sys.modules:
        sys.modules.pop(module_name, None)
