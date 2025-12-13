# Migration Guide — Using kivy-protonox-version in existing projects

The Protonox fork is a drop-in extension of Kivy 2.3.1. Existing apps continue
working as-is; you only opt into new capabilities when you explicitly enable
profiles or flags.

## 1) Install the fork
```
pip install -e kivy-protonox-version  # or your packaged wheel
```

No code changes are required for baseline compatibility.

## 2) Keep behaviour identical (safe mode)
- Environment-only (no code change): set `KIVY_PROTONOX=1` or `PROTONOX_KIVY=1`
  to request safe mode.
- Or a one-liner:

```python
from kivy_protonox import enable
enable()  # activates guard rails, no behavioural changes
```

## 3) Enable diagnostics when you need visibility
```python
from kivy_protonox import enable

# Enables the diagnostic bus + runtime doctor
enable("diagnostics")
```

Collect logs during development:
```python
from kivy.protonox_ext.diagnostics import get_bus
bus = get_bus()
report_path = bus.dump(Path(".protonox/reports/diagnostics.json"))
```

## 4) Opt into UI telemetry (read-only)
```python
from kivy_protonox import enable

enable("ui")
```

This allows layout fingerprints, symmetry reports, and observability exports to
run when called without changing layout behaviour.

## 5) Rollback strategy
All additions are gated by environment variables. Unset them or remove the
`enable_*` calls to return to upstream-equivalent behaviour. The fork does not
modify Kivy core files or your application code.
