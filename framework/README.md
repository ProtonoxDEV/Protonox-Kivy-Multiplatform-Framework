# Protonox Framework Components

This folder hosts Protonox-maintained forks and toolchain components. Each subfolder mirrors the upstream project structure with Protonox patches applied and a normalized naming scheme.

- `kivy`: Kivy 2.3.1 with emoji/textinput/navigator/clock stability patches.
- `python-for-android`: Patched for Android 15+ with bundled recipes (Cython, PIL, Pyjnius).
- `pyjnius`: Pyjnius with Android 15 compatibility and Firebase SDK interoperability.
- `cython`: Optimized Cython distribution targeting ARM64.
- `windowser`: Native layer for storage, permissions, notifications, and background services.
- `kibit3` & `bkibit`: Text and emoji rendering engines for cross-platform use.
- `build-tools`: Internal Buildozer snapshot and helper utilities preconfigured for Protonox workflows.
- `protonox-devtools`: Hot reload, wireless debugging, remote console, profiler, and project patcher.
- `docs`: Setup and troubleshooting guides for the framework components.
- `templates`: Starter project assets aligned with Protonox defaults.

Populate each component by syncing from the upstream sources and applying Protonox patches before shipping releases.
