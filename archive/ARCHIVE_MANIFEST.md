# Archive manifest

This folder contains archived build artifacts and environment snapshots moved during cleanup.

Kept files and folders (archived here):
- `archive/buildozer_venv/` (~215M)  — local virtualenv for buildozer
- `archive/test_venv/` (~221M) — test virtualenv
- `archive/.venv_build/` (~42M) — venv used for builds
- `archive/dist_debug_wheel/` (~4.2M) — debug wheels
- `archive/dist/` (~36K) — dist
- `archive/build/` (~60K) — build outputs
- `archive/protonox.egg-info/` (~40K) — egg-info
- `archive/.buildozer/` (~4K) — buildozer state
- `archive/logs/` (~1.8M) — logs
- `archive/protonox_kivy-3.0.0.dev14-py3-none-any.whl` (~2.2M) — wheel

Notes:
- APKs, `android_app/`, and NDK/toolchain files were kept in place (not archived).
- Some archive contents may be large and are ignored by `.gitignore` (left untracked) to avoid repo bloat. See repo history for original files.

