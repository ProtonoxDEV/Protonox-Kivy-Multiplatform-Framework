# Protonox-Kivy Multiplatform Framework

Protonox-Kivy Multiplatform Framework is a professional-grade toolkit for building Kivy applications that run consistently across Android, Windows, Linux, and macOS. It bundles curated forks of the Kivy toolchain, a set of developer utilities, opinionated templates, and deployment scripts tuned for Firebase and Render (FastAPI) backends.

## What's inside
- **framework/**: Protonox-maintained toolchain components (python-for-android, Kivy, Pyjnius, Cython, Buildozer, devtools, and native helpers).
- **templates/**: Production-ready app starters, including a full intelligent template wired for Firebase and Render.
- **tools/**: Automation scripts to set up Android/desktop build environments and generate new apps from templates.
- **docs/**: Guides for setup, building, troubleshooting, and roadmap planning.

## Quick start
1. Install Python 3.11+ and ensure `git`, `virtualenv`, and the Android SDK/NDK (for mobile builds) are available.
2. Clone the repository and pick a template under `templates/`.
3. Create a new app with the scaffolding tool:
   ```bash
   python tools/create_protonox_app.py MyProtonoxApp --template=protonox-app-complete
   ```
4. Follow `docs/setup_android15.md` and `docs/firebase_integration.md` to configure platform-specific services.

## Supported platforms
- Android 15+ via python-for-android and Buildozer
- Windows, Linux, macOS desktop builds
- Backend integrations with Firebase (Auth, Firestore, Storage) and Render-hosted FastAPI

## Security and credentials
Never commit real API keys or service credentials. The repository includes placeholders—replace them locally via environment variables or secure secret management.
