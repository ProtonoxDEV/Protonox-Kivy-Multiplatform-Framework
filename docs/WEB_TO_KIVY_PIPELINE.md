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
2. (Opcional pero recomendado) Declara un mapa `protonox_studio.yaml|json` con rutas ↔ screens, viewport y nombres de archivos.
3. Protonox descarga la URL si es necesario y parsea HTML (sin ejecutar JS) en un UI-IR con pantallas, jerarquía, texto, bounds aproximados, assets y rutas detectadas.
4. Opcional: aporta un PNG con `--png` para validar viewport durante `audit`.
5. Ejecuta `protonox web2kivy` (alias: `web-to-kivy` o `export`) para emitir KV + scaffolds bajo `.protonox/protonox-exports` sin tocar tu código.
6. Usa `protonox render-web`/`render-kivy` para obtener PNG derivados del UI-IR y `protonox diff --baseline ... --candidate ...` para regresión visual reproducible.
7. Inspecciona el IR serializado (`ui-model.json`) o reutilízalo vía `PROTONOX_UI_MODEL` para auditorías deterministas.
8. Itera: edita KV/Python generado o re-exporta tras cambios en HTML.

## Commands
```bash
protonox audit --project-type web --entrypoint ./site/index.html --png ./capture.png
protonox web-to-kivy --project-type web --entrypoint https://example.com --map protonox_studio.yaml --screens home:/ dashboard:/dashboard
protonox render-web --project-type web --entrypoint ./site/index.html
protonox render-kivy --project-type kivy --entrypoint ./app/main.py
protonox diff --baseline ./captures/web.png --candidate ./.protonox/renders/kivy.png --out ./.protonox/reports
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
- `*.kv`: clean, nested BoxLayout/Label/Button/TextInput suggestions derived from
 the UI model (one per screen). Positioning hints respect inline styles (flex/abs) when present.
- `*_screen.py`: minimal Screen/ScreenManager scaffold loading the KV file.
- `ui-model.json`: serialized IR with bounds/styles/routes for audits and diffs.
- `manifest.json`: bindings, entrypoint/URL, warnings, assets, and generated file list.
- `kivy-export.json`: optional IR export from una pantalla Kivy existente usando
  `kivy.protonox_ext.kv_bridge.importer.model_from_widget` (útil para mapear KV
  previo y hacer round-trip web ↔ Kivy sin tocar código de usuario).

## Flags and overrides
- `PROTONOX_WEB_URL`: optional URL linked to the entrypoint for traceability.
- `PROTONOX_WEB_SNAPSHOT`: path to a JSON element snapshot to bypass HTML parsing.
- `PROTONOX_UI_MODEL`: path to a serialized IR (`ui-model.json`) to skip HTML parsing entirely.
- `PROTONOX_STATE_DIR`: location for `.protonox` (defaults to project root/.protonox).

## Safeguards
- Kivy exports live under `.protonox/protonox-exports` (never overwrites user code).
- KV stays human-readable and hot-reload friendly.
- Python scaffolds keep logic minimal; real logic remains in user-land.

## Limitations (current step)
- Layout bounds are approximated for audit/porting; provide PNG or snapshots for
  higher fidelity.
- CSS/JS execution is not performed; structural mapping is best-effort.
