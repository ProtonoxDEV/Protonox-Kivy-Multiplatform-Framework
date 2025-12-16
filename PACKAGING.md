# Packaging plan (Protonox suite)

This repository currently holds two publishable artifacts side by side:

- **kivy-protonox-version/** → Python distribution name: `protonox-kivy` (drop-in fork of Kivy with Protonox extensions).
- **protonox-studio/** → Python distribution name: `protonox-studio` (tooling/CLI and mentor flow).

To avoid collisions and keep releases coordinated:

1) **Keep two distributions, one repo.** Build/publish each from its own folder.
   - `cd kivy-protonox-version && python -m build` → upload `dist/` to (Test)PyPI as `protonox-kivy`.
   - `cd protonox-studio && python -m build` → upload `dist/` to (Test)PyPI as `protonox-studio`.

2) **Naming sanity.**
   - Distribution names must remain distinct: `protonox-kivy` and `protonox-studio`.
   - Imports: keep Protonox fork under `kivy` (drop-in) but document that it should install in an isolated venv. If you later rename imports to `kivy_protonox`, update Studio to depend on that name instead.

3) **Dependencies between packages.**
   - If/when `protonox-studio` requires the Protonox Kivy fork, declare a versioned dependency range (e.g., `protonox-kivy>=3.0.0.dev1,<3.1`) in `protonox-studio/pyproject.toml`.
   - Avoid circular deps; Studio depends on Kivy fork, not vice versa.

4) **Publish flow recommendation.**
   - Build and upload **protonox-kivy** first; note the published version.
   - Update `protonox-studio` dependency range (if used), bump its version, then build and upload it.
   - Prefer releasing to TestPyPI first: `twine upload -r testpypi dist/*`, then to PyPI.

5) **Future monorepo layout (optional but clean):**
   - Move into `packages/protonox-kivy/` and `packages/protonox-studio/` with separate `pyproject.toml` files, plus a shared `docs/` and `scripts/`.

6) **Drop-in replacement guidance.**
   - When using `protonox-kivy` as a drop-in for `kivy`, install in a clean virtual environment and avoid mixing with the official `kivy` wheel. Document this in user-facing READMEs to reduce surprises.

This document is informational only and does not change build behavior. Follow the steps above to publish without name collisions or lost progress.
