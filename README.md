# Kivy 2.3.1 — Protonox Modernization Fork

This repository provides a **backward-compatible modernization layer**
on top of **Kivy 2.3.1**, focused on:

- modern developer experience
- faster iteration cycles
- safer builds
- real hot reload in development

without breaking existing Kivy applications.

---

## Why this fork exists

Kivy is a powerful and flexible framework, but it lacks several features
that modern developers expect today, such as:

- real hot reload (without restarting the process)
- safer development-time error handling
- faster and more reproducible builds
- clearer diagnostics and tooling

This project addresses those gaps **without modifying Kivy’s public API**
and **without touching Android SDK/NDK internals**.

---

## What this project is

✔ A compatibility-first modernization fork  
✔ A developer-experience upgrade  
✔ A foundation for industrialized build pipelines  
✔ A framework-level live reload engine (DEV only)

---

## What this project is NOT

✖ A rewrite of Kivy  
✖ A replacement for upstream Kivy  
✖ A breaking fork  
✖ A production hot reload system  

All advanced features are **opt-in** and **development-only**.

---

## Key Features

### 🔥 Kivy Live Reload Engine (DEV)
- Reload Python and KV code without restarting the process
- Optional state preservation
- Automatic rollback on failure
- Level-based reload strategy (safe by default)

### 🧭 Explicit State & Lifecycle (opt-in)
- `LiveReloadStateCapable` contract to persist critical app data across reloads
- `ProtonoxWidget` mixin for `on_mount`/`on_unmount`/`on_pause`/`on_resume`
- Lifecycle broadcast stays additive to Kivy’s native events

### 📐 Responsive Layout Helpers (opt-in)
- `breakpoint()` utility for mobile/tablet/desktop tuning
- `orientation()` helper based on real window metrics
- Designed to be consumed directly from KV without new layouts

### 🔎 Runtime Introspection (DEV only)
- `app.inspect().widget_tree()` for live widget hierarchy snapshots
- `app.inspect().kv_rules()` and `running_callbacks()` for diagnostics
- Disabled in production unless explicitly enabled

### 🧠 Safer Development Workflow
- Error overlay instead of application crash
- Clear diagnostics and logs
- Explicit control over reload behavior

### 🎨 UI & Text Improvements (opt-in)
- Improved Unicode handling
- Emoji-safe TextInput pipeline
- Modern font fallback strategy

### 📦 Packaging Improvements
- Deterministic build helpers
- Build caching
- Reproducible build reports

---

## Compatibility

- Fully compatible with **Kivy 2.3.1**
- No changes to public APIs
- Existing apps continue to work without modification
- Android SDK/NDK remain untouched

---

## Intended Audience

- Developers with existing Kivy apps
- Teams who need faster iteration cycles
- Projects requiring reproducible builds
- Tooling and framework developers

---

## Development Philosophy

- Stability over novelty
- Explicit over implicit
- Opt-in over forced behavior
- Tooling should never surprise production

---

## Status

This project is under active development.
Early versions focus on **developer tooling and live reload**.
UI and packaging improvements follow incrementally.

---

## License

Same license as Kivy upstream (MIT).

---

## Acknowledgements

Built on top of the excellent work of the Kivy community.
This fork aims to extend Kivy’s capabilities while respecting its design
and ecosystem.
