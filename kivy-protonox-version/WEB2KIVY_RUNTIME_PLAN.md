# Web→Kivy Runtime Integration Plan (Protonox Kivy Version)

Goal: make Web→Kivy exports from Protonox Studio feel native inside the Kivy fork ("Protonox Kivy Core"). UI-IR becomes first-class, reloads are coordinated by a central bus, and screens patch in-place with state preservation.

## Runtime Modules to Add
- `protonox_ext/runtime/ui_model/`
  - `ui_ir_types.py`: UI-IR dataclasses (reuse/extend `kv_bridge.ir`), helpers to load `ui-model.json`.
  - `diff.py`: tree diff → patch ops (`ADD_NODE`, `REMOVE_NODE`, `UPDATE_PROP`, `MOVE_NODE`).
  - `apply.py`: apply ops to live widget trees; safe fallbacks when ops are unsafe.
- `protonox_ext/runtime/screens/`
  - `registry.py`: ScreenRegistry that reads manifest, resolves routes → screen_id, tracks loaded widgets, and exposes lookup for state capture.
  - `dynamic_screen.py`: Screen that rebuilds/patches from UI-IR; delegates to diff/apply and preserves state contract.
- `protonox_ext/runtime/hotreload/`
  - `reload_bus.py`: central event hub (`emit/subscribe`) for `exports_updated`, `screen_changed`, `rollback`.
  - `rollback.py`: integrates with `hotreload_plus/hooks` snapshots to roll back KV/modules on failure.
  - `state_preserver.py`: opt-in state capture/inject by `state_keys` declared per screen.
- `protonox_ext/runtime/watch/`
  - `fs_watch.py`: desktop watchdog listener for `.reload` + manifest changes.
  - `android_watch.py`: polling/hash watcher for safe device paths.

## Data Contracts (Studio ↔ Runtime)
- `app_manifest.json` per export directory with entries per screen:
  - `screen_id` (string)
  - `route` (string)
  - `ui_model_path` (relative path, default `ui-model.json`)
  - `kv_path` (optional, fallback artifact)
  - `hash` (kv/ui hash for change detection)
  - `capabilities` (e.g. `{"patch": true, "rebuild": true}`)
  - `web_entrypoint` (source HTML/URL)
- Reload sentinel: `.reload` file touched by Studio after each export.
- Optional `patch.json`: precomputed patch ops; runtime can skip diffing when present.

## Runtime Flow
1) Startup: ScreenRegistry loads `app_manifest.json`, wires routes to `dynamic_screen` instances, subscribes to ReloadBus.
2) Watchers: fs/android watcher observes `.reload` and manifest hashes; on change emit `exports_updated` with paths.
3) ReloadBus: decouples reactions (`reload_bus.emit("exports_updated", manifest_path)`). Subscribers: registry, overlay UI, telemetry/log sink.
4) Update cycle per screen:
   - Load new `ui-model.json` (or `patch.json`).
   - Capture state via `state_preserver` using declared `state_keys` on the screen/controller.
   - Diff old vs new UI-IR (`diff.py`) → ops.
   - Apply ops via `apply.py`; if unsafe or fails, fall back to full rebuild or `rollback` snapshot.
   - Re-inject captured state; emit `screen_changed`.
5) Rollback: on exceptions, use `hotreload_plus.rollback(snapshot)` and emit `rollback` event.

## API Sketches (runtime-facing)
- `load_ui_model(path_or_dict) -> UIModel`
- `render_screen(ui_node_tree, screen_id, root_widget=None) -> Widget`
- `apply_patch(widget, ops, state=None) -> None`
- `ReloadBus.subscribe(event, callback)` / `ReloadBus.emit(event, **payload)`
- `ScreenRegistry.register(manifest_entry)`; `get_widget(screen_id)`; `ensure_loaded(screen_id)`
- `StatePreserver.capture(widget, keys)` / `inject(widget, state)`

## Integration with Protonox Studio Live Exports
- Studio already writes `app_manifest.json` + `.reload` into `state_dir/protonox-exports` (see `protonox_studio.web2kivy.live`).
- Runtime should watch that directory by default; allow override via env (`PROTONOX_EXPORT_DIR`).
- Use `hash` field to skip no-op reloads; support route→screen mapping from manifest.

## Phased Delivery
1) Scaffolding: add runtime package skeleton + ReloadBus, manifest loader, basic watcher (desktop).
2) Patching MVP: diff/apply for layout + text/props; fallback to rebuild.
3) State preservation: declare `state_keys` contract, add capture/inject.
4) Android watcher + rollback overlays/logging integration.
5) Optional: accept `patch.json` from Studio to avoid on-device diff cost.

## Notes
- Keep everything opt-in behind env flags (`PROTONOX_RUNTIME_LIVE=1`) to avoid impacting existing apps.
- Preserve KV generation as fallback/audit path; KV files remain usable for manual tweaks.
