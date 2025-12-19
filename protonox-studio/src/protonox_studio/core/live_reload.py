"""Hot Reload engine for Kivy 2.3.1 with state preservation and safe rollback.

This module implements a conservative, opt-in live reload flow that keeps
compatibility with existing Kivy projects while enabling faster DX during
development. All risky behaviors are gated by environment flags and
reload decisions degrade gracefully to safer levels when necessary.

It also exposes ``HotReloadAppBase`` which adapts the legacy partial screen
reload flow (``FILE_TO_SCREEN`` mapping, watchdog hashing, and the red error
overlay) to the level-based engine. The base class never mutates user code,
falls back to full rebuilds when a change cannot be safely replayed, and
captures contextual information (hashes, stack filenames) to help developers
diagnose crashes quickly.
"""

from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
import importlib
import importlib.util
import os
import threading
import time
import sys
from dataclasses import dataclass, field
from pathlib import Path
import traceback
from types import ModuleType
from typing import Dict, Iterable, List, Optional, Protocol, Set

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock, mainthread
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import BooleanProperty, DictProperty, ListProperty, NumericProperty
from kivymd.app import MDApp

from .lifecycle import broadcast_lifecycle_event
from .runtime_introspection import RuntimeInspector
from protonox_studio.devtools.error_overlay import build_error_overlay
from protonox_studio.devtools.kv_strict import enable_kv_strict_mode
from protonox_studio.devtools.logger import prefixed_logger
from protonox_studio.devtools.clock_guard import ClockGuard
from protonox_studio.flags import is_enabled
from protonox_studio.ui.textinput_unicode import patch_textinput_unicode
try:
    from kivy.protonox_ext.runtime.watch.socket_bridge import SocketReloadBridge  # type: ignore
    from kivy.protonox_ext.device.facade import bootstrap_device  # type: ignore
except ImportError:
    SocketReloadBridge = None
    bootstrap_device = None


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
        self.log = prefixed_logger("hotreload")

    # ------------------------------ Snapshot helpers -------------------------
    def _copy_factory(self) -> Optional[dict]:
        factory_spec = importlib.util.find_spec("kivy.factory")
        if factory_spec is None:
            return None
        from kivy.factory import Factory

        try:
            return copy.deepcopy(Factory.classes)
        except Exception:
            return None

    def _copy_builder_rules(self) -> Optional[dict]:
        builder_spec = importlib.util.find_spec("kivy.lang")
        if builder_spec is None:
            return None
        from kivy.lang import Builder

        try:
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
        return ReloadSnapshot(
            state=state,
            modules=dict(sys.modules),
            factory_classes=self._copy_factory(),
            builder_rules=self._copy_builder_rules(),
        )

    def _restore_snapshot(self, snapshot: ReloadSnapshot) -> None:
        sys.modules.clear()
        sys.modules.update(snapshot.modules)
        if importlib.util.find_spec("kivy.factory") is not None:
            from kivy.factory import Factory

            try:
                if snapshot.factory_classes is not None:
                    Factory.classes = snapshot.factory_classes
            except Exception:
                pass
        if importlib.util.find_spec("kivy.lang") is not None:
            from kivy.lang import Builder

            try:
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


# ------------------------- Kivy integration base class ------------------------


class _ErrorOverlayHandler(ExceptionHandler):
    """Renders a red overlay when the app crashes in DEBUG/RAISE_ERROR mode."""

    def handle_exception(self, inst):
        if isinstance(inst, (KeyboardInterrupt, SystemExit)):
            return ExceptionManager.RAISE

        app = HotReloadAppBase.get_running_app()
        if isinstance(app, HotReloadAppBase):
            return app._handle_exception(inst)
        return ExceptionManager.RAISE


class HotReloadAppBase(MDApp):
    """Base app that wires ``HotReloadEngine`` with partial KV/Python reload.

    Key behaviors inherited from the legacy implementation:
    - ``FILE_TO_SCREEN`` mapping triggers partial screen refreshes when the
      approot exposes ``partial_reload_screen(name)``.
    - Watchdog-based watcher with MD5 hashing to avoid duplicate reloads.
    - Red error overlay with traceback details when the app crashes in debug
      mode.
    - Fallback to full rebuild when the engine cannot safely apply a reload.

    This base class never mutates user code and keeps Kivy/KivyMD internals out
    of the reload graph. ``LiveReloadStateCapable`` apps automatically preserve
    their state when the engine reaches Level 3; others gracefully rebuild.
    """

    DEBUG = BooleanProperty("DEBUG" in os.environ or os.getenv("PROTONOX_DEV") == "1")
    FOREGROUND_LOCK = BooleanProperty(False)
    KV_FILES = ListProperty()
    KV_DIRS = ListProperty()
    AUTORELOADER_PATHS = ListProperty([(".", {"recursive": True})])
    AUTORELOADER_IGNORE_PATTERNS = ListProperty(
        ["*.pyc", "*__pycache__*", ".protonox/**", "protobots/protonox_export/**"]
    )
    CLASSES = DictProperty()
    IDLE_DETECTION = BooleanProperty(False)
    IDLE_TIMEOUT = NumericProperty(60)
    RAISE_ERROR = BooleanProperty(True)

    __events__ = ["on_idle", "on_wakeup"]

    def __init__(self, file_to_screen: Optional[dict[str, str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.reload_engine = HotReloadEngine()
        self.hotreload_log = prefixed_logger("hotreload")
        self.file_hashes: Dict[str, str] = {}
        self.file_to_screen = {str(Path(path).resolve()): name for path, name in (file_to_screen or {}).items()}
        self._exception_handler_added = False
        self.state: Optional[ReloadState] = None
        self.approot = None
        self._clock_guard = ClockGuard()
        self.use_error_overlay = is_enabled("ERROR_OVERLAY", default=self.DEBUG)
        self.export_dir: Optional[Path] = None
        self._export_thread: Optional[threading.Thread] = None
        self._export_stop = threading.Event()
        self.device = bootstrap_device(self)

        # Dev-only safety nets (all opt-in via flags)
        enable_kv_strict_mode()
        patch_textinput_unicode()
        if is_enabled("CLOCK_GUARD", False):
            self._clock_guard.install()

        # Autodetect export dir (cero fricción)
        default_export_dir = Path(os.getenv("PROTONOX_EXPORT_DIR", "protobots/protonox_export"))
        if default_export_dir.exists():
            self.export_dir = default_export_dir
            os.environ.setdefault("PROTONOX_EXPORT_DIR", str(default_export_dir))

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def build(self):
        if self.DEBUG:
            Logger.info(f"{self.appname}: Debug mode activated")
            self.enable_autoreload()
            self.patch_builder()
            self.bind_key(32, self.rebuild)  # Space bar → manual rebuild
            self._install_exception_overlay()

            # Start export bridge if present
            self._start_export_bridge()

        if self.FOREGROUND_LOCK:
            self.prepare_foreground_lock()

        self.root = self.get_root()
        self.rebuild(first=True)

        if self.IDLE_DETECTION:
            self.install_idle(timeout=self.IDLE_TIMEOUT)

        return super().build()

    def get_root(self):
        return Factory.RelativeLayout()

    def get_root_path(self) -> str:
        return str(Path.cwd())

    def build_app(self, first: bool = False):  # pragma: no cover - to be implemented by the app
        raise NotImplementedError("Implementa build_app() en tu subclase")

    def prepare_foreground_lock(self):  # pragma: no cover - platform hook
        Logger.info(f"{self.appname}: FOREGROUND_LOCK is enabled but no handler is registered")

    # ------------------------------------------------------------------
    # Dependency management
    # ------------------------------------------------------------------
    def unload_app_dependencies(self) -> None:
        for path_to_kv_file in self.KV_FILES:
            Builder.unload_file(str(Path(path_to_kv_file).resolve()))

        for name in list(self.CLASSES):
            Factory.unregister(name)

        for path in self.KV_DIRS:
            for path_to_dir, _dirs, files in os.walk(path):
                for name_file in files:
                    if Path(name_file).suffix == ".kv":
                        Builder.unload_file(str(Path(path_to_dir).joinpath(name_file)))

    def load_app_dependencies(self) -> None:
        for path_to_kv_file in self.KV_FILES:
            resolved = Path(path_to_kv_file)
            if not resolved.exists():
                Logger.warning(f"{self.appname}: KV file not found - {resolved}")
                continue
            Builder.load_file(str(resolved))

        for name, module in self.CLASSES.items():
            Factory.register(name, module=module)

        for path in self.KV_DIRS:
            for path_to_dir, _dirs, files in os.walk(path):
                for name_file in files:
                    if Path(name_file).suffix == ".kv":
                        Builder.load_file(str(Path(path_to_dir).joinpath(name_file)))

    # ------------------------------------------------------------------
    # Rebuilds
    # ------------------------------------------------------------------
    def rebuild(self, *args, **kwargs):
        Logger.info(f"{self.appname}: Rebuild the application")
        first = kwargs.get("first", False)
        try:
            if isinstance(self, LiveReloadStateCapable):
                self.state = self.extract_state()
            if not first:
                self.unload_app_dependencies()

            Builder.rulectx = {}
            self.load_app_dependencies()

            self.set_widget(None)
            self.approot = self.build_app(first=first)
            self.set_widget(self.approot)
            self.apply_state(self.state)
            Logger.info(f"{self.appname}: Rebuild completed")
        except Exception as exc:  # noqa: BLE001 - crash overlay is required
            Logger.exception(f"{self.appname}: Error when building app")
            self.set_error(repr(exc), traceback.format_exc())
            if not self.DEBUG and self.RAISE_ERROR:
                raise

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------
    def _handle_exception(self, inst):
        if not self.DEBUG and not self.RAISE_ERROR:
            return ExceptionManager.RAISE
        self.set_error(inst, tb=traceback.format_exc())
        return ExceptionManager.PASS

    def _install_exception_overlay(self) -> None:
        if self._exception_handler_added:
            return
        ExceptionManager.add_handler(_ErrorOverlayHandler())
        self._exception_handler_added = True

    @mainthread
    def set_error(self, exc, tb=None):
        if self.use_error_overlay:
            overlay = build_error_overlay(str(exc), tb or "", on_rebuild=self.rebuild if self.DEBUG else None)
            self.set_widget(overlay)
            return

        from kivy.core.window import Window
        from kivy.utils import get_color_from_hex

        scroll = Factory.MDScrollView(scroll_y=0, md_bg_color=get_color_from_hex("#e50000"))
        lbl = Factory.Label(
            text_size=(Window.width - 100, None),
            size_hint_y=None,
            text=f"{exc}\n\n{tb or ''}",
        )
        lbl.bind(texture_size=lbl.setter("size"))
        scroll.add_widget(lbl)
        self.set_widget(scroll)

    def apply_state(self, state):  # pragma: no cover - opt-in override
        pass

    # ------------------------------------------------------------------
    # Widget helpers
    # ------------------------------------------------------------------
    def set_widget(self, wid):
        previous = getattr(self, "approot", None)
        if previous is not None and wid is not previous:
            broadcast_lifecycle_event(previous, "on_unmount")

        self.root.clear_widgets()
        self.approot = wid
        if wid is not None:
            self.root.add_widget(wid)
            try:
                wid.do_layout()
            except Exception:
                pass
            broadcast_lifecycle_event(wid, "on_mount")
        # Re-bind device lifecycle when widgets change
        try:
            if hasattr(self, "device") and self.device:
                self.device.on_unmount()
                self.device.on_mount()
        except Exception:
            pass

    def on_pause(self):  # pragma: no cover - runtime hook
        broadcast_lifecycle_event(self.approot, "on_pause")
        try:
            return super().on_pause()
        except AttributeError:
            return True

    def on_resume(self):  # pragma: no cover - runtime hook
        broadcast_lifecycle_event(self.approot, "on_resume")
        try:
            return super().on_resume()
        except AttributeError:
            return None

    def on_stop(self):  # pragma: no cover - runtime hook
        self._stop_export_bridge()
        try:
            return super().on_stop()
        except AttributeError:
            return None

    # ------------------------------------------------------------------
    # Key bindings
    # ------------------------------------------------------------------
    def bind_key(self, key, callback):
        from kivy.core.window import Window

        def _on_keyboard(window, keycode, *args):  # noqa: ANN001, ANN401 - Kivy callback
            if key == keycode:
                return callback()

        Window.bind(on_keyboard=_on_keyboard)

    # ------------------------------------------------------------------
    # Idle detection (optional)
    # ------------------------------------------------------------------
    def install_idle(self, timeout: int = 60):
        try:
            import time
            monotonic = time.monotonic
        except AttributeError:
            Logger.exception(f"{self.appname}: Cannot use idle detector, monotonic is missing")
            return

        self.idle_timer = None
        self.idle_timeout = timeout
        Logger.info(f"{self.appname}: Install idle detector, {timeout} seconds")
        Clock.schedule_interval(self._check_idle, 1)
        self.root.bind(on_touch_down=self.rearm_idle, on_touch_up=self.rearm_idle)
        self._monotonic = monotonic

    def rearm_idle(self, *args):
        if not hasattr(self, "idle_timer"):
            return
        if self.idle_timer is None:
            self.dispatch("on_wakeup")
        self.idle_timer = self._monotonic()

    def _check_idle(self, *args):
        if not hasattr(self, "idle_timer"):
            return
        if self.idle_timer is None:
            return
        if self._monotonic() - self.idle_timer > self.idle_timeout:
            self.idle_timer = None
            self.dispatch("on_idle")

    def on_idle(self, *args):  # pragma: no cover - hook
        pass

    def on_wakeup(self, *args):  # pragma: no cover - hook
        pass

    # ------------------------------------------------------------------
    # Watchdog / reload dispatch
    # ------------------------------------------------------------------
    def enable_autoreload(self):
        events_spec = importlib.util.find_spec("watchdog.events")
        observers_spec = importlib.util.find_spec("watchdog.observers")
        if events_spec is None or observers_spec is None:
            Logger.warning(f"{self.appname}: Autoreloader is missing watchdog")
            return

        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer

        Logger.info(f"{self.appname}: Autoreloader activated")
        rootpath = self.get_root_path()
        self.w_handler = handler = FileSystemEventHandler()
        handler.dispatch = self._reload_from_watchdog
        self._observer = observer = Observer()
        for path in self.AUTORELOADER_PATHS:
            options = {"recursive": True}
            if isinstance(path, (tuple, list)):
                path, options = path
            observer.schedule(handler, os.path.join(rootpath, path), **options)
        observer.start()

    def _get_file_hash(self, filename: str) -> str:
        hash_md5 = hashlib.md5()
        try:
            with open(filename, "rb") as stream:
                for chunk in iter(lambda: stream.read(4096), b""):
                    hash_md5.update(chunk)
        except FileNotFoundError:
            return ""
        return hash_md5.hexdigest()

    def _should_ignore(self, path: str) -> bool:
        norm = path.replace("\\", "/")
        # Allow manifest and .reload inside export dir even if under ignore glob
        if self.export_dir:
            export_str = str(self.export_dir.resolve())
            if norm.startswith(export_str):
                if norm.endswith("app_manifest.json") or norm.endswith(".reload"):
                    return False
        for pat in self.AUTORELOADER_IGNORE_PATTERNS:
            if fnmatch.fnmatch(norm, pat) or fnmatch.fnmatch(os.path.relpath(norm, os.getcwd()), pat):
                return True
        return False

    @mainthread
    def _reload_from_watchdog(self, event):  # noqa: ANN001 - watchdog callback
        from watchdog.events import FileModifiedEvent

        if not isinstance(event, FileModifiedEvent):
            return

        changed_file = str(Path(event.src_path).resolve())
        if self._should_ignore(changed_file):
            return

        current_hash = self._get_file_hash(changed_file)
        if self.file_hashes.get(changed_file) == current_hash:
            return
        self.file_hashes[changed_file] = current_hash

        partial_screen = self.file_to_screen.get(changed_file)
        if partial_screen:
            Logger.info(f"{self.appname}: Partial reload triggered for '{partial_screen}'")
            if hasattr(self.approot, "partial_reload_screen"):
                try:
                    self.approot.partial_reload_screen(partial_screen)
                    return
                except Exception:
                    Logger.exception(f"{self.appname}: Partial reload failed; falling back to rebuild")
            else:
                Logger.warning(f"{self.appname}: App root has no partial_reload_screen() method!")

        self._dispatch_change(Path(changed_file))

    # ------------------------------------------------------------------
    # Export bridge (manifest watcher without loops)
    # ------------------------------------------------------------------
    def _start_export_bridge(self):
        socket_endpoint = os.getenv("PROTONOX_EXPORT_SOCKET")
        if socket_endpoint and SocketReloadBridge:
            Logger.info(f"{self.appname}: export bridge ON via socket {socket_endpoint}")
            self._export_stop.clear()
            bridge = SocketReloadBridge(
                socket_endpoint,
                lambda _p: self._dispatch_change(
                    self.export_dir / "app_manifest.json" if self.export_dir else Path("")
                ),
                manifest_path=(self.export_dir / "app_manifest.json") if self.export_dir else None,
            )
            bridge.start()
            self._export_thread = bridge  # type: ignore
            return

        if self.export_dir is None:
            Logger.info(f"{self.appname}: export bridge OFF (no export dir)")
            return
        manifest = self.export_dir / "app_manifest.json"
        if not manifest.exists():
            Logger.info(f"{self.appname}: export bridge OFF (manifest missing at {manifest})")
            return

        Logger.info(f"{self.appname}: export bridge ON ({self.export_dir}), watching manifest/.reload")

        def loop():
            last_hash = ""
            last_reload_ts = 0.0
            while not self._export_stop.is_set():
                try:
                    if manifest.exists():
                        data = manifest.read_bytes()
                        h = hashlib.sha256(data).hexdigest()
                        reload_file = self.export_dir / ".reload"
                        reload_ts = reload_file.stat().st_mtime if reload_file.exists() else 0.0
                        if h != last_hash or reload_ts != last_reload_ts:
                            last_hash = h
                            last_reload_ts = reload_ts
                            self._dispatch_change(manifest)
                    else:
                        last_hash = ""
                    time.sleep(1)
                except Exception:
                    time.sleep(1)

        self._export_stop.clear()
        self._export_thread = threading.Thread(target=loop, daemon=True)
        self._export_thread.start()

    def _stop_export_bridge(self):
        self._export_stop.set()
        if isinstance(self._export_thread, threading.Thread):
            self._export_thread.join(timeout=2)
        elif self._export_thread is not None:
            try:
                self._export_thread.stop()  # type: ignore[attr-defined]
            except Exception:
                pass
        self._export_thread = None

    # Public toggles for UI buttons/overlays
    def start_export_bridge(self):
        self._start_export_bridge()

    def stop_export_bridge(self):
        self._stop_export_bridge()

    def _dispatch_change(self, changed_file: Path) -> None:
        # Export bridge: if manifest changes, treat as rebuild trigger
        if self.export_dir and changed_file.resolve() == (self.export_dir / "app_manifest.json").resolve():
            Logger.info(f"{self.appname}: Export manifest changed → refreshing screens")
            handled = self._handle_export_refresh()
            if handled:
                return
            Clock.unschedule(self.rebuild)
            Clock.schedule_once(self.rebuild, 0.1)
            return
        decision = self.reload_engine.handle_change(changed_file, app=self)
        if decision.applied:
            Logger.info(f"{self.appname}: Applied reload level {decision.level} ({decision.reason})")
            return

        if decision.error:
            Logger.error(f"{self.appname}: Reload error → {decision.error}")
            self.set_error(decision.error)

        Logger.info(f"{self.appname}: Fallback to rebuild (level={decision.level}, reason={decision.reason})")
        Clock.unschedule(self.rebuild)
        Clock.schedule_once(self.rebuild, 0.1)

    def _handle_export_refresh(self) -> bool:
        sm = resolve_screen_manager(self)
        manifest_path = self.export_dir / "app_manifest.json" if self.export_dir else None
        if sm is None or manifest_path is None or not manifest_path.exists():
            return False
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return False
        screens = payload.get("screens", []) or []
        handled = False
        for entry in screens:
            name = entry.get("screen") or entry.get("screen_id") or entry.get("route") or None
            if not name:
                continue
            # Prefer explicit reload hooks
            if hasattr(sm, "reload_screen_instance") and callable(getattr(sm, "reload_screen_instance")):
                try:
                    sm.reload_screen_instance(name, None)
                    handled = True
                    continue
                except Exception:
                    pass
            # Legacy partial reload hook on approot or screen manager
            target = sm if hasattr(sm, "partial_reload_screen") else getattr(self, "approot", None)
            if target and hasattr(target, "partial_reload_screen"):
                try:
                    target.partial_reload_screen(name)
                    handled = True
                    continue
                except Exception:
                    pass
        if handled and os.getenv("PROTONOX_AUDIT_EXPORTS") == "1":
            self._run_export_audit()
        return handled

    def _run_export_audit(self):
        Logger.info(f"{self.appname}: PROTONOX_AUDIT_EXPORTS is set; integrate visual diff runner here")

    # ------------------------------------------------------------------
    # Builder patch: preserve filename context
    # ------------------------------------------------------------------
    def patch_builder(self):
        Builder.orig_load_string = Builder.load_string
        Builder.load_string = self._builder_load_string

    def _builder_load_string(self, string, **kwargs):
        if "filename" not in kwargs:
            from inspect import getframeinfo, stack

            caller = getframeinfo(stack()[1][0])
            kwargs["filename"] = caller.filename
        return Builder.orig_load_string(string, **kwargs)

    # ------------------------------------------------------------------
    # Runtime introspection (DEV only)
    # ------------------------------------------------------------------
    def inspect(self) -> RuntimeInspector:
        enabled = self.DEBUG or os.getenv("PROTONOX_INSPECT", "0") == "1"
        return RuntimeInspector(self, enabled=enabled)


# ------------------------------------------------------------------
# Screen manager resolution helpers (duck-typed, no naming assumptions)
# ------------------------------------------------------------------


def resolve_screen_manager(app) -> Optional[object]:
    getter = getattr(app, "get_screen_manager", None)
    if callable(getter):
        try:
            sm = getter()
            if sm is not None:
                return sm
        except Exception:
            pass
    if hasattr(app, "screen_manager"):
        sm = getattr(app, "screen_manager")
        if sm is not None:
            return sm
    return getattr(app, "approot", None)
