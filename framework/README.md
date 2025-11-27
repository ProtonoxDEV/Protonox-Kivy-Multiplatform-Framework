# Protonox Framework Components

This folder hosts Protonox-maintained forks and toolchain components. Each subfolder should mirror the upstream project structure with Protonox patches applied.

- `python-for-android`: Patched for Android 15+, bundled recipes (Cython, PIL, Pyjnius).
- `kivy-2.3.1-protonox`: Kivy 2.3.1 with emoji/textinput/navigator/clock stability patches.
- `pyjnius-protonox`: Pyjnius with Android 15 compatibility and Firebase SDK interoperability.
- `cython-protonox`: Optimized Cython distribution targeting ARM64.
- `windowser`: Native layer for storage, permissions, notifications, and background services.
- `kibit3` & `bkibit-2.3.1`: Text and emoji rendering engines for cross-platform use.
- `buildozer`: Internal Buildozer snapshot preconfigured for Protonox workflows.
- `protonox-devtools`: Hot reload, wireless debugging, remote console, profiler, and project patcher.

Populate each component by syncing from the upstream sources and applying Protonox patches before shipping releases.
