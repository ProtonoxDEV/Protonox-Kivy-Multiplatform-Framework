"""
Compatibility helpers for KivyMD widget names across versions.
This module attempts to import common widgets from likely locations and
provides `get(name)` to retrieve a class fallback. It also registers
found classes into the Kivy `Factory` so KV language can reference them.

Use case: ensure demo works against KivyMD 1.x and newer variants where some
widgets changed names or lived in different modules.
"""
from importlib import import_module
from kivy.factory import Factory

# mapping of logical widget names -> list of candidate import paths
CANDIDATES = {
    'MDToolbar': [
        'kivymd.uix.toolbar.MDToolbar',
        'kivymd.uix.topappbar.MDTopAppBar',
    ],
    'MDLabel': [
        'kivymd.uix.label.MDLabel',
        'kivymd.uix.label.label.MDLabel',
    ],
    'MDRaisedButton': [
        'kivymd.uix.button.MDRaisedButton',
        'kivymd.uix.button.MDRectangleFlatButton',
        'kivymd.uix.button.MDFlatButton',
    ],
    'MDTextField': [
        'kivymd.uix.textfield.MDTextField',
    ],
    'MDList': [
        'kivymd.uix.list.MDList',
    ],
    'OneLineListItem': [
        'kivymd.uix.list.OneLineListItem',
    ],
    'MDFillRoundFlatIconButton': [
        'kivymd.uix.button.MDFillRoundFlatIconButton',
        'kivymd.uix.button.MDFillRoundFlatButton',
    ],
}

_loaded = {}


def _import_candidate(path):
    module_name, cls_name = path.rsplit('.', 1)
    try:
        mod = import_module(module_name)
        cls = getattr(mod, cls_name)
        return cls
    except Exception:
        return None


def get(name):
    """Return a class for `name` or None."""
    if name in _loaded:
        return _loaded[name]
    candidates = CANDIDATES.get(name, [])
    for cand in candidates:
        cls = _import_candidate(cand)
        if cls:
            _loaded[name] = cls
            try:
                Factory.register(name, cls=cls)
            except Exception:
                # registration may raise if registered twice; ignore
                pass
            return cls
    # fallback: try to fetch from kivymd package directly
    try:
        import kivymd
        if hasattr(kivymd, name):
            cls = getattr(kivymd, name)
            _loaded[name] = cls
            try:
                Factory.register(name, cls=cls)
            except Exception:
                pass
            return cls
    except Exception:
        pass
    _loaded[name] = None
    return None


def ensure(names):
    """Ensure the given iterable of widget names are resolved and registered.
    Returns a dict name->class (or None).
    """
    out = {}
    for n in names:
        out[n] = get(n)
    return out
