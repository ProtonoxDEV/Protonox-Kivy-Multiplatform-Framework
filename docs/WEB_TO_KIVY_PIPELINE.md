# Web → Kivy Pipeline (UI-IR first)

This document explains how Protonox Studio ports a web view (HTML/CSS + static JS
structure) into editable Kivy KV + Python scaffolds without touching user code. It adds
the new integration requirements: explicit mapping to the real ScreenManager, safe
hot‑reload, and Android fast loop.

## Principles
- **No mutation**: existing web or Kivy sources are never modified outside controlled zones (`protobots/protonox_export/**`, `.protonox/**`, `protobots/protonox_studio/**`).
- **UI-IR first**: HTML is parsed into a neutral UI model before any Kivy output.
- **Declarative entrypoint**: the developer decides which HTML to consume.
- **One view ↔ one screen**: every web view maps to a dedicated Kivy screen.
- **Opt-in**: exports live under `.protonox` and can be ignored or edited safely.
- **Mapping is king**: `protonox_studio.yaml` binds routes ↔ screens ↔ kv ↔ ui-model and drives loaders/hotreload.

## Flow
1. Declare the project as `web` and provide the entrypoint (URL or `index.html`).
2. (Optional but recommended) Provide `protonox_studio.yaml|json` with routes ↔ screens, viewport, naming rules, and export dir.
3. Run `protonox web2kivy` to emit UI‑IR (`*-ui-model.json`) + KV + optional scaffolds under `protobots/protonox_export/` (never touching user code).
4. Normalize the UI‑IR (`ui_ir/normalize.py`) to enforce ids, `role/bounds/meta`, fingerprints, and breakpoints.
5. Clean the KV export (`exporters/kivy_kv.py`): scroll strategy for overflow, remove invisible DOM nodes, sanitize `pos_hint`, add placeholders.
6. Map exports to real screens via `protonox map` (interactive “game”) → writes `protonox_studio.yaml`.
7. Inject screens with `replace_content` loader: KV mounts under `ids.export_root` inside the real controller; fallback placeholder if mapping is missing.
8. Enable batch hot‑reload watcher on `protobots/protonox_export/**/*` with sandbox compile + rollback per screen; optional state preservation via `LiveReloadStateCapable`.
9. Validate visually: render PNG from web and Kivy (`protonox validate --baseline ... --candidate ...`), compare diffs, and keep reports in `.protonox/protonox-exports/`.
10. Android fast loop: `protonox android wifi-connect` + `android audit --target 35` + logcat bridge (WSL aware).

## Commands
```bash
protonox audit --project-type web --entrypoint ./site/index.html --png ./capture.png
protonox web-to-kivy --project-type web --entrypoint https://example.com --map prot
onox_studio.yaml --screens home:/ dashboard:/dashboard
protonox map --app protobots --exports protobots/protonox_export
protonox run --app protobots --hotreload
protonox render-web --project-type web --entrypoint ./site/index.html
protonox render-kivy --project-type kivy --entrypoint ./app/main.py
protonox diff --baseline ./captures/web.png --candidate ./.protonox/renders/kivy.png --out ./.protonox/reports
protonox android wifi-connect
protonox android audit --target 35
```

### IR JSON (mínimo)
```json
{
  "origin": "web|kivy",
  "routes": ["/", "/dashboard"],
  "breakpoints": {"/": {"mobile": {"width": 390, "height": 844}}},
  "screens": [
    {
      "name": "home",
      "viewport": {"width": 1280, "height": 720},
      "root": {
        "identifier": "home",
        "role": "screen",
        "bounds": {"x": 0, "y": 0, "width": 1280, "height": 720},
        "children": [{"identifier": "hero", "role": "div", "bounds": {"x": 24, "y": 48, "width": 900, "height": 320}}]
      }
    }
  ]
}
```

## Output
- `*.kv`: clean, nested BoxLayout/Label/Button/TextInput suggestions derived from the UI model (one per screen). Positioning hints respect inline styles (flex/abs) when present and avoid `pos_hint` > 1.
- `*_screen.py`: minimal Screen/ScreenManager scaffold loading the KV file, never replacing user controllers.
- `ui-model.json`: serialized IR with bounds/styles/routes for audits and diffs.
- `protonox_studio.yaml`: manifest that binds route ↔ screen ↔ kv ↔ ui-model and feeds the loader/hotreload.
- `layout_report.json` + `nav_graph.json`: sanity reports and inferred navigation (proposal only).
- `kivy-export.json`: optional IR export from an existing Kivy screen using `kivy.protonox_ext.kv_bridge.importer.model_from_widget`.

## Flags and overrides
- `PROTONOX_WEB_URL`: optional URL linked to the entrypoint for traceability.
- `PROTONOX_WEB_SNAPSHOT`: path to a JSON element snapshot to bypass HTML parsing.
- `PROTONOX_UI_MODEL`: path to a serialized IR (`ui-model.json`) to skip HTML parsing entirely.
- `PROTONOX_STATE_DIR`: location for `.protonox` (defaults to project root/.protonox).
- `PROTONOX_BULK_RELOAD_THRESHOLD` / `PROTONOX_BULK_RELOAD_QUIET_MS`: tune batch hot‑reload behavior.

## Safeguards
- Kivy exports live under `.protonox/protonox-exports` and `protobots/protonox_export` (never overwrites user code).
- KV stays human-readable and hot-reload friendly; rollback restores last stable snapshot.
- Python scaffolds keep logic minimal; real logic remains in user-land. Navigation suggestions are opt‑in only.

## Limitations (current step)
- Layout bounds are approximated for audit/porting; provide PNG or snapshots for higher fidelity.
- CSS/JS execution is not performed; structural mapping is best-effort.
- Device layer features require the native bridge to be present and are dev-only by default.
