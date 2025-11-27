# Optimizations

Improve performance and shrink package sizes with these practices.

## Android
- Strip debug symbols from native builds when shipping release APKs.
- Enable `--skip-buildozer-clean` only for iterative builds to avoid stale artifacts.
- Use `cython-protonox` for ARM64-tuned modules.

## Assets
- Compress images and audio; prefer vector assets when possible.
- Lazy-load large datasets and cache remote content selectively.

## UI responsiveness
- Preload fonts and emoji resources from `kibit3`/`bkibit` before rendering heavy views.
- Offload blocking operations to background threads using Kivy's `Clock` scheduling.

## Networking
- Batch Firestore writes where possible.
- Use HTTP keep-alive and exponential backoff (already included in services).
