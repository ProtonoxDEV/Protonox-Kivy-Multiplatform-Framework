"""Opt-in lifecycle helpers that don't alter Kivy's public API.

`ProtonoxWidget` can be mixed into existing widgets to get predictable
mount/unmount/pause/resume callbacks without changing Kivy semantics.
Lifecycle broadcast helpers are intentionally defensive and no-ops when
widgets don't opt in.
"""

from __future__ import annotations

from typing import Iterable

from kivy.uix.widget import Widget


class ProtonoxWidget(Widget):
    """Widget mixin with explicit lifecycle callbacks.

    The callbacks are additive to Kivy's native ones and only fire when the
    widget is present in the tree and the host app dispatches lifecycle
    signals (e.g., via ``HotReloadAppBase``).
    """

    def on_mount(self):  # pragma: no cover - hook
        pass

    def on_unmount(self):  # pragma: no cover - hook
        pass

    def on_pause(self):  # pragma: no cover - hook
        pass

    def on_resume(self):  # pragma: no cover - hook
        pass

    def on_kv_post(self, *largs):  # noqa: ANN002 - Kivy signature
        super().on_kv_post(*largs)
        try:
            self.on_mount()
        except Exception:
            # Lifecycle hooks must never crash the app
            pass

    def on_parent(self, instance, value):  # noqa: ANN001 - Kivy signature
        super().on_parent(instance, value)
        if value is None:
            try:
                self.on_unmount()
            except Exception:
                pass


def iter_lifecycle_widgets(widget: Widget | None) -> Iterable[Widget]:
    if widget is None:
        return []
    stack = [widget]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(getattr(current, "children", []) or [])


def broadcast_lifecycle_event(widget: Widget | None, event: str) -> None:
    """Invoke a lifecycle event on any widget that implements it.

    This is defensive by design: failures in hooks must not bubble up to the
    application, keeping compatibility with non-opt-in widgets.
    """

    if widget is None:
        return
    for node in iter_lifecycle_widgets(widget):
        handler = getattr(node, event, None)
        if handler and callable(handler):
            try:
                handler()
            except Exception:
                # Do not propagate lifecycle hook errors
                pass
