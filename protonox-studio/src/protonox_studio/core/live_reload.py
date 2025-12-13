"""Hot Reload engine for Kivy 2.3.1 with state preservation and safe rollback.

This module implements a conservative, opt-in live reload flow that keeps
compatibility with existing Kivy projects while enabling faster DX during
development. All risky behaviors are gated by environment flags and
reload decisions degrade gracefully to safer levels when necessary.
"""

from __future__ import annotations

import copy
import importlib
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Protocol, Set


# ----------------------------- State preservation -----------------------------


@dataclass
class ReloadState:
    """Serializable snapshot of the running app state."""

    navigation: dict = field(default_factory=dict)
    user: dict = field(default_factory=dict)
    runtime: dict = field(default_factory=dict)


class LiveReloadStateCapable(Protocol):
    """Opt-in contract for apps that want stateful hot reload."""

    def extract_state(self) -> ReloadState:
        """Return a stable snapshot of the critical state before reloading."""

    def apply_state(self, state: ReloadState) -> None:
        """Reinject the preserved state after a successful reload."""


# --------------------------- Module dependency graph --------------------------


@dataclass
class ModuleNode:
    name: str
    file: str
    dependencies: List[str] = field(default_factory=list)


class ModuleGraphBuilder:
    """Builds a conservative dependency graph for reloadable modules."""

    def __init__(self, blocklist: Optional[Set[str]] = None) -> None:
        self.blocklist = blocklist or set()

    def resolve_module_from_path(self, path: Path) -> Optional[str]:
        target = path.resolve()
        for name, module in sys.modules.items():
            mod_file = getattr(module, "__file__", None)
            if mod_file and Path(mod_file).resolve() == target:
                return name
        return None

    def _is_reloadable(self, name: str, module: ModuleType) -> bool:
        if name in self.blocklist:
            return False
        if name.startswith("kivy") or name.startswith("kivymd"):
            return False
        if name.startswith("protonox_studio"):
            return False

        mod_file = getattr(module, "__file__", None)
        if not mod_file:
            return False
        stdlib_path = Path(sys.base_prefix).joinpath("lib")
        if stdlib_path in Path(mod_file).resolve().parents:
            return False
        return True

    def _collect_dependencies(self, module: ModuleType) -> Set[str]:
        deps: Set[str] = set()
        for value in module.__dict__.values():
            mod_name = getattr(value, "__module__", None)
            if mod_name and mod_name != module.__name__:
                deps.add(mod_name)
            if isinstance(value, ModuleType):
                deps.add(value.__name__)
        return deps

    def build_graph(self, root_module: str) -> Dict[str, ModuleNode]:
        graph: Dict[str, ModuleNode] = {}
        visited: Set[str] = set()

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            module = sys.modules.get(name)
            if not module or not self._is_reloadable(name, module):
                return
            deps = [dep for dep in self._collect_dependencies(module) if dep in sys.modules]
            graph[name] = ModuleNode(name=name, file=getattr(module, "__file__", ""), dependencies=deps)
            for dep in deps:
                visit(dep)

        visit(root_module)
        return graph

    def topological_order(self, graph: Dict[str, ModuleNode]) -> List[str]:
        order: List[str] = []
        temp: Set[str] = set()
        perm: Set[str] = set()

        def visit(node_name: str) -> None:
            if node_name in perm:
                return
            if node_name in temp:
                return  # cycle detected; bail out silently to keep safety first
            temp.add(node_name)
            node = graph.get(node_name)
            if node:
                for dep in node.dependencies:
                    if dep in graph:
                        visit(dep)
                order.append(node_name)
            perm.add(node_name)
            temp.discard(node_name)

        for node_name in graph:
            visit(node_name)
        return order


# ----------------------------- Reload orchestration ---------------------------


@dataclass
class ReloadSnapshot:
    state: Optional[ReloadState]
    modules: Dict[str, ModuleType]
    factory_classes: Optional[dict]
    builder_rules: Optional[dict]


@dataclass
class ReloadDecision:
    level: int
    reason: str
    applied: bool = False
    error: Optional[str] = None


class HotReloadEngine:
    """Coordinates safe hot reload for Python and KV files."""

    def __init__(self, max_level: Optional[int] = None) -> None:
        self.max_level = max_level if max_level is not None else int(os.getenv("PROTONOX_HOT_RELOAD_MAX", "3"))
        self.graph_builder = ModuleGraphBuilder()

    # ------------------------------ Snapshot helpers -------------------------
    def _copy_factory(self) -> Optional[dict]:
        try:
            from kivy.factory import Factory

            return copy.deepcopy(Factory.classes)
        except Exception:
            return None

    def _copy_builder_rules(self) -> Optional[dict]:
        try:
            from kivy.lang import Builder

            return copy.deepcopy(getattr(Builder, "rulectx", {}))
        except Exception:
            return None

    def _snapshot(self, app: object) -> ReloadSnapshot:
        state = None
        if isinstance(app, LiveReloadStateCapable):
            try:
                state = app.extract_state()
            except Exception:
                state = None
        return ReloadSnapshot(state=state, modules=dict(sys.modules), factory_classes=self._copy_factory(), builder_rules=self._copy_builder_rules())

    def _restore_snapshot(self, snapshot: ReloadSnapshot) -> None:
        sys.modules.clear()
        sys.modules.update(snapshot.modules)
        try:
            from kivy.factory import Factory

            if snapshot.factory_classes is not None:
                Factory.classes = snapshot.factory_classes
        except Exception:
            pass
        try:
            from kivy.lang import Builder

            if snapshot.builder_rules is not None:
                Builder.rulectx = snapshot.builder_rules
        except Exception:
            pass

    # ------------------------------- Reload flows ---------------------------
    def _reload_kv(self, kv_path: Path) -> None:
        from kivy.lang import Builder

        Builder.unload_file(str(kv_path))
        Builder.load_file(str(kv_path))

    def _reload_modules(self, module_order: Iterable[str]) -> None:
        for name in module_order:
            module = sys.modules.get(name)
            if module:
                importlib.reload(module)

    def _apply_state_if_needed(self, app: object, state: Optional[ReloadState]) -> None:
        if state is None:
            return
        if isinstance(app, LiveReloadStateCapable):
            app.apply_state(state)

    # ------------------------------- Decision logic -------------------------
    def decide_level(self, changed_file: Path, app: object | None = None) -> ReloadDecision:
        if self.max_level <= 0:
            return ReloadDecision(level=0, reason="Hot reload disabled by flag")

        suffix = changed_file.suffix.lower()
        if suffix == ".kv":
            level = 1
            reason = "KV change detected"
        elif suffix == ".py":
            level = 3 if isinstance(app, LiveReloadStateCapable) else 2
            reason = "Python change detected"
        else:
            return ReloadDecision(level=0, reason="Unsupported file type; full rebuild recommended")

        level = min(level, self.max_level)
        return ReloadDecision(level=level, reason=reason)

    def _module_plan(self, changed_file: Path) -> List[str]:
        module_name = self.graph_builder.resolve_module_from_path(changed_file)
        if not module_name:
            return []
        graph = self.graph_builder.build_graph(module_name)
        return self.graph_builder.topological_order(graph)

    def handle_change(self, changed_file: Path, app: object | None = None) -> ReloadDecision:
        decision = self.decide_level(changed_file, app)
        if decision.level == 0:
            return decision

        snapshot = self._snapshot(app)
        try:
            if decision.level >= 2 and changed_file.suffix.lower() == ".py":
                module_plan = self._module_plan(changed_file)
                if not module_plan:
                    decision.level = 0
                    decision.reason = "No reloadable modules found; fallback to rebuild"
                    return decision
                self._reload_modules(module_plan)
            if decision.level >= 1 and changed_file.suffix.lower() == ".kv":
                self._reload_kv(changed_file)
            if decision.level == 3:
                self._apply_state_if_needed(app, snapshot.state)
            decision.applied = True
            return decision
        except Exception as exc:  # noqa: BLE001 - rollback requires broad catch
            decision.applied = False
            decision.error = str(exc)
            self._restore_snapshot(snapshot)
            return decision


def bootstrap_hot_reload_engine(max_level: Optional[int] = None) -> HotReloadEngine:
    return HotReloadEngine(max_level=max_level)
