"""Compatibility shim: provide a ``state`` alias for ToggleButtonBehavior.

Kivy 3.0 replaced the historical 'state' OptionProperty (values 'normal'/'down')
with boolean ``active`` on ToggleButtonBehavior. Some third-party libraries
(notably older KivyMD versions) still bind to and read/write ``state``.

This module defines an AliasProperty named ``state`` on
``kivy.uix.behaviors.togglebutton.ToggleButtonBehavior`` when missing,
mapping 'down' <=> True and 'normal' <=> False. The AliasProperty is bound
to the internal ``active`` storage so EventDispatcher.bind('state', ...) will
work as expected.

This is a minimal, well-scoped compatibility fix intended for development
environments where the application (or KivyMD) expects the legacy ``state``
API.
"""
from __future__ import annotations

from kivy.properties import AliasProperty
from kivy.uix.behaviors import togglebutton


def _get_state(self) -> str:
    return "down" if getattr(self, "active", False) else "normal"


def _set_state(self, value) -> None:
    # accept both 'down'/'normal' and boolean-like values for robustness
    if value in (True, 1, "down"):
        self.active = True
    else:
        self.active = False


def ensure_state_alias():
    cls = togglebutton.ToggleButtonBehavior
    # Only add if not present to avoid overwriting real implementations
    if not hasattr(cls, "state"):
        cls.state = AliasProperty(_get_state, _set_state, bind=["_active"])


try:
    ensure_state_alias()
except Exception:
    # Best-effort compatibility shim; if something goes wrong we don't want to
    # break Kivy's import path during normal operation.
    pass
