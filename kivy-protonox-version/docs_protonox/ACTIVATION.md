# ACTIVATION

This fork stays dormant until you explicitly enable it. Pick one of the activation paths below; if you do nothing, behaviour matches upstream Kivy 2.3.1.

## Environment flags
- `PROTONOX_KIVY=1` or `KIVY_PROTONOX=1` → enable safe-mode defaults.
- Optional profile: `KIVY_PROTONOX_PROFILE=diagnostics|ui|safe` for targeted toggles.
- Optional device layer: `PROTONOX_DEVICE_LAYER=1` to unlock modern Android helpers (CameraX/AudioRecord/SAF) without touching the core.

## In-code toggle
```python
from kivy_protonox import enable_protonox

# Safe defaults (recommended)
enable_protonox()

# Or pick a profile
enable_protonox(profile="diagnostics")
```

## What “safe-mode defaults” do
- Keep public Kivy APIs intact.
- Apply compatibility shims and diagnostics that do not change runtime behaviour.
- Allow you to layer additional Protonox modules later (ADB bridge, layout health, inspector).

## Deactivation / rollback
- Unset the env vars or remove the `enable_protonox()` call.
- Reinstall upstream Kivy if you no longer want the fork.
