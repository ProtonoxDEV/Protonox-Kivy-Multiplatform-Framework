"""Dynamic Screen that can patch or rebuild from UI-IR."""

from __future__ import annotations

from pathlib import Path

from kivy.uix.screenmanager import Screen

from ..hotreload.reload_bus import ReloadBus, get_reload_bus
from ..hotreload.state_preserver import StatePreserver
from ..ui_model.apply import apply_patch_ops
from ..ui_model.diff import diff_models
from ..ui_model.ui_ir_types import UIModel


class DynamicScreen(Screen):
    def __init__(self, screen_id: str, initial_model: UIModel | None, **kwargs):
        super().__init__(name=screen_id, **kwargs)
        self.screen_id = screen_id
        self._model = initial_model or UIModel()
        self._bus: ReloadBus = get_reload_bus()
        self._state = StatePreserver()
        if self._model.screens:
            self._rebuild(self._model)

    def _rebuild(self, model: UIModel) -> None:
        self.clear_widgets()
        if not model.screens:
            return
        screen = model.screens[0]
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.image import Image
        from kivy.uix.textinput import TextInput
        from kivy.uix.widget import Widget

        kind_map = {
            "container": BoxLayout,
            "button": Button,
            "label": Label,
            "image": Image,
            "input": TextInput,
            "widget": Widget,
        }

        def build_widget(component):
            cls = kind_map.get(component.kind, Widget)
            w = cls()
            if component.text and hasattr(w, "text"):
                w.text = component.text
            for key, value in (component.props or {}).items():
                if hasattr(w, key):
                    try:
                        setattr(w, key, value)
                    except Exception:
                        pass
            for child in component.children:
                w.add_widget(build_widget(child))
            return w

        root = build_widget(screen.components[0]) if screen.components else Widget()
        self.add_widget(root)
        self._model = model
        self._bus.emit("screen_changed", screen_id=self.screen_id)

    def update_from_model(self, new_model: UIModel) -> None:
        current_root = self.children[0] if self.children else None
        if current_root is None or not self._model.screens:
            self._rebuild(new_model)
            return

        ops = diff_models(self._model, new_model)
        captured = self._state.capture(current_root)
        ok = apply_patch_ops(current_root, ops)
        if not ok:
            self._rebuild(new_model)
        else:
            self._state.inject(current_root, captured)
            self._model = new_model
            self._bus.emit("screen_changed", screen_id=self.screen_id)

    def load_from_path(self, path: Path) -> None:
        try:
            model = UIModel.from_json(path)
        except Exception:
            return
        self.update_from_model(model)
