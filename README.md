# Kivy 2.3.1 — Protonox Modernization Fork

This repository provides a **backward-compatible modernization layer** on top of **Kivy 2.3.1**, focused on:

- modern developer experience
- faster iteration cycles
- safer builds
- real hot reload in development

without breaking existing Kivy applications.

---

## PyPI availability

- Framework fork: `pip install protonox-kivy==3.0.0.dev1` (sdist; builds a wheel locally).
- CLI tooling: `pip install protonox-studio==0.1.1` (exposes the `protonox` command).
- TestPyPI mirrors remain available for staging.

If you had previous editable installs, uninstall them first: `pip uninstall -y protonox-kivy kivy protonox-studio`.

## Repository layout
- `kivy-protonox-version/`: Forked Kivy 2.3.1 sources + Protonox extensions (`protonox-kivy` on PyPI).
- `protonox-studio/`: CLI + tooling (`protonox-studio` on PyPI) for audits, web→Kivy export, live reload, and dev server.
- `examples/` and `tools/`: Upstream Kivy examples and helper scripts.
- `docs/`: Guides and internal notes for the modernization fork and tooling.

---

## Why this fork exists

Kivy is a powerful and flexible framework, but it lacks several features that modern developers expect today, such as:

- real hot reload (without restarting the process)
- safer development-time error handling
- faster and more reproducible builds
- clearer diagnostics and tooling

This project addresses those gaps **without modifying Kivy’s public API** and **without touching Android SDK/NDK internals**.

## SDL3 Support

Protonox Kivy includes **complete SDL3 backend support** for modern platforms, with full Android compatibility.

### Key Features
- **SDL3 Window Backend**: Modern window management with improved performance
- **Advanced Text Rendering**: HarfBuzz integration for complex scripts and typography
- **Android SDL3 Bootstrap**: Complete python-for-android bootstrap with SDL3 dependencies
- **OpenGL ES 3.2 Support**: Modern graphics pipeline with Android Extension Pack features
- **Backward Compatibility**: SDL2 remains available as fallback

### OpenGL ES 3.2 Modernization

Protonox Kivy now requires **OpenGL ES 3.2** as minimum version, bringing:

- Enhanced graphics capabilities with tessellation and geometry shaders
- Improved performance on modern Android devices
- Better visual quality and effects
- Compatibility with latest mobile GPUs

**Note**: Requires devices with OpenGL ES 3.2 support (Android 5.0+ with compatible hardware).

### Android Builds with SDL3
```bash
# Build APK with SDL3 backend
p4a apk --private /path/to/app --package=org.example.app --name="My App" --version=1.0 --bootstrap=sdl3 --requirements=kivy,harfbuzz,freetype
```

#### Modern Build System (Meson)
Protonox includes updated python-for-android recipes with modern Meson build system support:
- **Numpy 1.26.4**: Updated to use Meson-based compilation instead of deprecated setup.py
- **Meson Integration**: Added meson and meson-python recipes for proper dependency resolution
- **Cross-compilation**: Automatic generation of Meson cross-files for Android targets
- **Build Reliability**: Fixed "meson not found" errors during Android compilation

### Desktop Usage
SDL3 is enabled by default on desktop platforms. For SDL2 fallback:
```bash
USE_SDL2=1 python your_app.py
```

## Wireless Debugging

Protonox enables **real-time wireless debugging** between Kivy apps running on devices and Protonox Studio on your development machine.

### How it works
1. **Device side**: Kivy app starts a WebSocket server and displays a QR code with the connection URL.
2. **Studio side**: Scan the QR or use the CLI to connect and receive live logs, UI state, and touch events.

### Quick start
```bash
# On device (enable wireless debug)
PROTONOX_WIRELESS_DEBUG=1 python your_app.py

# On development machine (connect Studio)
# For Android via ADB wireless:
protonox wireless-connect --adb-wireless-ip-port 192.168.1.100:5555
# For direct WebSocket:
protonox wireless-connect --wireless-url ws://192.168.1.100:8765
```

### Features
- Live log streaming
- UI state snapshots
- Touch event recording
- QR code pairing
- **Live reload** without app restart
- **Remote file push** for Android devices
- Cross-platform (Android, iOS, Desktop)

### Live Reload Usage
Once connected, you can trigger live reloads remotely:

```bash
# Reload the entire app
protonox wireless-reload

# Reload specific module
protonox wireless-reload --reload-module myapp

# Push and reload a specific file
protonox wireless-reload-file --reload-file main.py
```

For Android devices, files are automatically pushed via ADB before reloading.

See `examples/wireless_debug_example.py` for a complete example.

## Desarrollo en Termux (Android)

Este framework está optimizado para desarrollo móvil directo en Android usando Termux. Ambas librerías (`protonox-kivy` y `protonox-studio`) son compatibles y permiten testing en vivo sin PC.

### Instalación en Termux
```bash
# Instalar Python si no está
pkg install python

# Instalar librerías compatibles
pip install protonox-kivy==3.0.0.dev4 protonox-studio==0.1.3
```

### Conexión Rápida por QR y WiFi

1. **En tu PC:**
   - Inicia el servidor de setup ADB:
     ```bash
     cd Protonox-Kivy-Multiplatform-Framework
     python3 adb_setup_server.py
     ```
     Genera un QR que abre una página web para conectar ADB automáticamente.

2. **En Termux (teléfono):**
   - Escanea el QR con la cámara de Android → Abre navegador con preview de la app y botón "Connect ADB".
   - Haz clic en "Connect ADB" → PC ejecuta `adb connect` y conecta inalámbricamente.
   - Verifica: `adb devices` (debe mostrar el dispositivo).

3. **Prueba la App en Termux:**
   - Copia app al teléfono:
     ```bash
     adb push test_app.py /sdcard/
     ```
   - Ejecuta con debug inalámbrico:
     ```bash
     PROTONOX_WIRELESS_DEBUG=1 python /sdcard/test_app.py
     ```
     Muestra QR para WebSocket y abre app Kivy con ScissorPush/ScissorPop.

4. **Live Reload desde PC:**
   - En PC, inicia servidor:
     ```bash
     cd protonox-studio
     source venv_protonox_studio_debug/bin/activate
     python -m protonox_studio.core.live_reload --host 0.0.0.0 --port 8080
     ```
   - App en Termux se conecta automáticamente para recarga en vivo.

### Comandos Básicos en Termux
- **Desarrollo:** `protonox dev` (servidor web para overlays).
- **Auditoría:** `protonox audit <file>` (analiza diseño).
- **Export:** `protonox export <file>` (tokens y componentes).
- **Conectar:** `protonox wireless-connect --adb-wireless-ip-port <ip:puerto>`
- **Desconectar:** `protonox wireless-disconnect`
- **Estado:** `protonox wireless-status`

### Preview y Debugging
- El QR abre un preview web simple de la app (detecta errores iniciales).
- Usa `PROTONOX_WIRELESS_DEBUG=1` para logs en vivo y snapshots UI.
- Live reload permite editar en PC y ver cambios en teléfono al instante.

### Troubleshooting
- Dependencias faltantes: `pip install protonox-studio[web]==0.1.3` (requiere Rust).
- Builds en Android: Asegura `clang` y `make` en Termux.
- Conexión: Verifica misma red WiFi.

¡Desarrolla apps Kivy directamente en tu teléfono!

## What this project is NOT

✖ A rewrite of Kivy  \
✖ A replacement for upstream Kivy  \
✖ A breaking fork  \
✖ A production hot reload system  

All advanced features are **opt-in** and **development-only**.

---

## Key Features

### 🔥 Kivy Live Reload Engine (DEV)
- Reload Python and KV code without restarting the process
- Optional state preservation
- Automatic rollback on failure
- Level-based reload strategy (safe by default)

### 🌉 Web → Kivy portability (via UI-IR)
- HTML entrypoint parsing (local path **or URL**) into a neutral UI model (no DOM mutation)
- Asset + route discovery for multi-view sites and SPA-like flows
- UI-IR is serializable (`ui-model.json`) for audits/diffs and can be reloaded via env (`PROTONOX_UI_MODEL`)
- One-to-one screen mapping to clean KV + controller scaffolds (no user code touched); pass `--map protonox_studio.yaml` to bind routes↔screens, viewport hints, and filenames explicitly
- CLI coverage: `protonox web2kivy` (alias `web-to-kivy`) for exports, `protonox render-web`/`render-kivy` for IR-based PNGs, and `protonox diff`/`validate` for baseline vs. candidate checks
- Optional PNG comparison against the UI model for viewport sanity and drift detection; outputs stay in `.protonox/protonox-exports`
- See `docs/WEB_TO_KIVY_PIPELINE.md` for the full flow and safeguards.

### 🧭 Explicit State & Lifecycle (opt-in)
- `LiveReloadStateCapable` contract to persist critical app data across reloads
- `ProtonoxWidget` mixin for `on_mount`/`on_unmount`/`on_pause`/`on_resume`
- Lifecycle broadcast stays additive to Kivy’s native events

### 📐 Responsive Layout Helpers (opt-in)
- `breakpoint()` utility for mobile/tablet/desktop tuning
- `orientation()` helper based on real window metrics
- Designed to be consumed directly from KV without new layouts

### 🔎 Runtime Introspection (DEV only)
- `app.inspect().widget_tree()` for live widget hierarchy + bounds snapshots
- `app.inspect().export_json(path)` to persist widget tree/state/callbacks (dev-only)
- `app.inspect().kv_rules()` and `running_callbacks()` for diagnostics

### 🛡️ Compatibility & Diagnostics (opt-in)
- Safe-mode profile keeps the Protonox fork dormant unless explicitly enabled.
- Diagnostic bus captures stdout/stderr/warnings/logs to structured JSON when `PROTONOX_DIAGNOSTIC_BUS=1`.
- Runtime doctor surfaces GPU/GL/DPI/window hints without mutating app state.
- Disabled in production unless explicitly enabled

### 🛡 Dev Safety Nets (opt-in)
- Error overlay with stacktrace + rebuild button in DEBUG
- Prefixed log channels: `[HOTRELOAD]`, `[BUILD]`, `[KV]`, `[UI]`
- Duplicate Clock scheduling warnings (development only)

### 🧾 Dev Flags Registry
- Centralized `protonox_studio.flags.is_enabled()` helper
- Examples: `PROTONOX_KV_STRICT=1`, `PROTONOX_TEXTINPUT_UNICODE=1`, `PROTONOX_HOT_RELOAD_MAX=2`

### 📡 Vendored Kivy telemetry (opt-in)
- `kivy/protonox_ext/telemetry.py` exports widget bounds, overflow flags, and safe PNG captures behind `PROTONOX_LAYOUT_TELEMETRY=1`
- Keeps upstream APIs intact while exposing geometry for Web→Kivy validation and inspector overlays

### 🧠 Safer Development Workflow
- Error overlay instead of application crash
- Clear diagnostics and logs
- Explicit control over reload behavior

### 📱 Android bridge (opt-in)
- Wireless-first ADB helpers with WSL-aware resolution and USB→tcpip enablement
- Structured logcat streaming with `emit=` hooks for DiagnosticBus/IA context
- Android 13–15 runtime/permission audit plus API-35 target checks
- Optional desktop bridge server for Android↔desktop command/event exchange in dev loops

### 🔌 Modern device layer (opt-in)
- Android-first helpers that prefer CameraX/AudioRecord/SAF/Bluetooth over legacy wrappers
- Runtime permission requests and capability probes exposed via structured snapshots
- Guarded by `PROTONOX_DEVICE_LAYER=1` so non-Android hosts remain unaffected

### 🖼️ Visual validation (baseline vs candidate)
- IR-driven PNG rendering for reproducible snapshots
- Bounding-box diff ratios per widget with optional overlay exports
- Layout fingerprints + symmetry heuristics to detect regressions without screenshots (`PROTONOX_VISUAL_WARNINGS=1`)
- Dual snapshots (PNG + JSON + layout report) with optional UI freeze for deterministic captures (`PROTONOX_UI_FREEZE=1`)
- CLI: `protonox validate --baseline web.png --candidate kivy.png`

### 📏 Layout health (opt-in, telemetry-gated)
- Anti-pattern detector for nested layouts, invisible space, empty scrolls, and DPI risks
- Dev-only inspector payloads with fingerprint, symmetry, anti-pattern summaries, and layout cost overlays (`PROTONOX_LAYOUT_PROFILER=1`)
- Layout health scoring + observability export (display context, metrics, tree,
  fingerprint) for CI/IA-driven regressions (`PROTONOX_LAYOUT_HEALTH=1`,
  `PROTONOX_UI_OBSERVABILITY=1`)
- All diagnostics are read-only and exported to caller-provided paths

### ⚡ Layout performance + freeze (DEV only)
- UI-freeze helper to pause scheduling/animations for deterministic captures (`PROTONOX_UI_FREEZE=1`)
- Layout cost profiler timing `do_layout` per widget for FPS/lag triage (`PROTONOX_LAYOUT_PROFILER=1`)
- Overlay payloads include severity buckets (low/medium/high) without mutating the UI

### 🎨 UI & Text Improvements (opt-in)
- Improved Unicode handling (`PROTONOX_TEXTINPUT_UNICODE=1`)
- Emoji-safe TextInput pipeline
- Modern font fallback strategy

### 📱 Android fast loop (opt-in)
- ADB wrappers for install/run/logcat/bugreport plus `watch()` for filtered log streaming and quick activity restarts
- No SDK/NDK mutations; usable alongside Buildozer outputs

### 📦 Packaging Improvements
- Deterministic build helpers
- Build caching
- Reproducible build reports

### 📦 Container parity
- Dockerfile with Kivy 2.3.1 + Protonox extensions preinstalled
- Same CLI inside/outside Docker (mount your project into `/workspace/app`)
- See `docs/DOCKER.md` for build/run examples

### 🧱 Vendored Kivy 2.3.1 (compat-first)
- The forked sources live under `kivy-protonox-version/` with Protonox patches
- Install locally with `pip install -e ./kivy-protonox-version` for reproducible builds
- Compatibility flags are opt-in; default runtime matches upstream 2.3.1

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

## Android Development Experience

Protonox-Kivy provides an enhanced Android development workflow with automated tools, comprehensive documentation, and optimized build configurations to eliminate common cross-compilation issues.

### Quick Android Setup

Get started with Android development in minutes:

```bash
# 1. Run automated setup (creates venv, installs buildozer, checks Android tools)
./scripts/setup_android_dev.sh

# 2. Create new app from template
cp -r templates/protonox-app-minimal my_app
cd my_app

# 3. Build APK (optimized for ARM64, Android 16+)
../scripts/build_android.sh

# 4. Deploy and test on device
../scripts/build_android.sh --deploy
```

### Key Improvements

#### 🔧 Automated Development Environment
- **One-command setup**: `setup_android_dev.sh` handles venv creation, dependency installation, and Android tool verification
- **Build optimization**: `build_android.sh` with colored output, error checking, and deployment options
- **Cross-compilation fixes**: Recipes optimized for ARM64 architecture with proper environment isolation

#### 📚 Comprehensive Documentation
- **Troubleshooting guide**: `docs/ANDROID_BUILD_LESSONS.md` covers common issues and solutions
- **Build lessons learned**: Documented solutions for architecture mismatches, NDK requirements, and environment setup
- **Best practices**: Configuration examples and debugging commands

#### 🏗️ Project Templates
- **Minimal app template**: Pre-configured with optimized `buildozer.spec` for Android 16+
- **ARM64 optimized**: Built specifically for modern Android devices
- **Ready-to-build**: Includes proper dependencies, permissions, and asset placeholders

#### 🚀 CI/CD Integration
- **Automated APK builds**: GitHub Actions workflow for continuous integration
- **Framework testing**: Automated test suite with coverage reporting
- **Release automation**: APK artifacts and release creation

### Android Build Configuration

The framework includes optimized configurations for Android 16+:

- **NDK r28c**: Required for 16KB page sizes and modern Android compatibility
- **ARM64 architecture**: Primary target for current Android devices
- **API 36**: Latest Android API with backward compatibility
- **SDL3 backend**: Modern graphics and input handling
- **Material Design**: KivyMD integration for modern UI

### Common Issues Solved

- ❌ **Architecture mismatch**: Extensions compiled for wrong platform
- ❌ **Complex debugging**: Hours spent on cross-compilation issues
- ❌ **Manual environment setup**: Repeated dependency installation
- ❌ **Poor error messages**: Unclear build failures
- ❌ **Template complexity**: Starting from scratch each time

### Development Workflow

1. **Setup once**: Run `setup_android_dev.sh` to prepare development environment
2. **Create apps**: Copy template and customize for your needs
3. **Build & test**: Use optimized scripts for reliable APK generation
4. **Deploy & debug**: Wireless debugging with Protonox-Studio
5. **Iterate**: Hot reload and live debugging during development

### Files Overview

```
scripts/
├── setup_android_dev.sh    # Automated development environment setup
└── build_android.sh        # Optimized APK build script

templates/
└── protonox-app-minimal/   # Ready-to-use app template
    ├── main.py            # Sample Protonox-Kivy app
    ├── buildozer.spec     # Optimized Android configuration
    ├── README.md          # Template documentation
    └── assets/            # Icon and presplash placeholders

docs/
└── ANDROID_BUILD_LESSONS.md  # Comprehensive troubleshooting guide

.github/workflows/
└── android-ci.yml         # CI/CD pipeline for automated builds
```

See `docs/ANDROID_BUILD_LESSONS.md` for detailed troubleshooting and `templates/protonox-app-minimal/README.md` for template usage.

---

## Status

This project is under active development.
Early versions focus on **developer tooling and live reload**.
UI and packaging improvements follow incrementally.

### CLI quickstart (local or Docker-parity)
- `protonox audit --project-type web --entrypoint ./site/index.html --png ./capture.png`
- `protonox web2kivy --project-type web --entrypoint https://example.com --screens home:home_screen`
- `protonox validate --baseline ./web.png --candidate ./.protonox/protonox-exports/preview.png`
- `protonox render-web --project-type web --entrypoint ./site/index.html`
- `protonox diff --baseline ./.protonox/renders/web.png --candidate ./.protonox/renders/kivy.png`

All outputs land in `.protonox/` to avoid mutating user projects.

---

## License

Same license as Kivy upstream (MIT).

---

## Acknowledgements

Built on top of the excellent work of the Kivy community.
This fork aims to extend Kivy’s capabilities while respecting its design
and ecosystem.
>>>>>>> feature/mentor-packaging
