# WHY_PROTONOX

The Protonox fork keeps Kivy 2.3.1 compatible while adding the missing DX pillars: observability, Android friendliness, and visual health tooling. Nothing changes unless you opt in.

## What it solves (no breaking changes)
- Android iteration friction: wireless/USB adb helpers, restart/reinstall shortcuts, and API 35 readiness.
- Visual regressions: layout fingerprints, symmetry/anti-pattern checks, and dual PNG/JSON snapshots.
- Debug blindness: runtime diagnostics bus, inspector exports, and structured logs for Protonox Studio or any CI.

## What stays the same
- Public APIs from Kivy 2.3.1 remain intact.
- Buildozer/python-for-android flow is unchanged unless you enable Protonox helpers.
- Apps run normally if you never enable the fork.

## How to opt in (short form)
- Set `PROTONOX_KIVY=1` or `KIVY_PROTONOX=1`.
- Or call `from kivy_protonox import enable_protonox; enable_protonox()`.

## Why it is safe
- All features are opt-in and reversible.
- Compatibility profiles default to “safe” when enabled.
- Upstream Kivy installs behave exactly the same when the fork is not requested.
