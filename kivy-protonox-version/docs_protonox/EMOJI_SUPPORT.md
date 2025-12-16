# Emoji Support (opt-in, cross-platform)

Goal: provide predictable emoji rendering on Linux/Windows/Android without
changing default Kivy widgets.

## How it works
- **Fallback registration:** searches for common emoji fonts (e.g. NotoColorEmoji)
  in user/system font paths and registers them as `ProtonoxEmoji`.
- **Env flag:** gated by `PROTONOX_EMOJI_FALLBACK=1` to stay dev-only/opt-in.
- **Widget patching:** `enable(widget)` applies the fallback to widgets that
  expose `font_name`, optionally auto-detecting emoji presence.

## Usage
```python
from kivy.protonox_ext.ui import emoji

# set PROTONOX_EMOJI_FALLBACK=1 in your env
emoji.enable(my_label)
```

## Principles
- **No core overrides:** TextInput/Label classes are untouched; only a font
  fallback is applied when requested.
- **Graceful degradation:** if no emoji font is found, a warning is logged and
  the widget is left unchanged.
- **Cross-platform aware:** searches standard font directories on Linux, macOS,
  and Windows; paths are overridable via `search_paths`.
