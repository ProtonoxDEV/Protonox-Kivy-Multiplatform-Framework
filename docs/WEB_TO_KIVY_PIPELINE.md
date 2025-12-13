# Web → Kivy Pipeline (UI-IR first)

This document explains how Protonox Studio ports a web view (HTML/CSS + static JS
structure) into editable Kivy KV + Python scaffolds without touching user code.

## Principles
- **No mutation**: existing web or Kivy sources are never modified.
- **UI-IR first**: HTML is parsed into a neutral UI model before any Kivy output.
- **Declarative entrypoint**: the developer decides which HTML to consume.
- **One view ↔ one screen**: every web view maps to a dedicated Kivy screen.
- **Opt-in**: exports live under `.protonox` and can be ignored or edited safely.

## Flow
1. Declare the project as `web` and provide the entrypoint (URL or `index.html`).
2. Protonox parses the HTML (no JS execution) into a UI model with screens,
   components, hierarchy, text samples, and approximated bounds.
3. Optional: provide a PNG with `--png` for viewport validation during audit.
4. Run `protonox export` to emit KV + controller stubs under `.protonox/protonox-exports`.
5. Iterate: edit the generated KV/Python or re-run export after HTML changes.

## Commands
```bash
protonox --project-type web --entrypoint ./site/index.html audit --png ./capture.png
protonox --project-type web --entrypoint ./site/index.html export
```

## Output
- `*.kv`: clean, nested BoxLayout/Label/Button/TextInput suggestions derived from
  the UI model (one per screen).
- `*_screen.py`: minimal Screen/ScreenManager scaffold loading the KV file.
- `manifest.json`: bindings, entrypoint, warnings, and generated file list.

## Flags and overrides
- `PROTONOX_WEB_URL`: optional URL linked to the entrypoint for traceability.
- `PROTONOX_WEB_SNAPSHOT`: path to a JSON element snapshot to bypass HTML parsing.
- `PROTONOX_STATE_DIR`: location for `.protonox` (defaults to project root/.protonox).

## Safeguards
- Kivy exports live under `.protonox/protonox-exports` (never overwrites user code).
- KV stays human-readable and hot-reload friendly.
- Python scaffolds keep logic minimal; real logic remains in user-land.

## Limitations (current step)
- Layout bounds are approximated for audit/porting; provide PNG or snapshots for
  higher fidelity.
- CSS/JS execution is not performed; structural mapping is best-effort.
