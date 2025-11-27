# Compiling Apps

This document outlines build commands for Android and desktop platforms.

## Android
- Prepare environment: `bash tools/setup_android_env.sh`
- Build: `bash tools/build_android.sh`
- Output APKs are stored under the template's `.buildozer/android/platform/build/outputs` directory.

## Windows
- Use the Windows helper script (requires Python 3.11 and suitable compilers):
  ```bash
  bash tools/build_windows.sh
  ```
- The script packages the app into a standalone directory using PyInstaller.

## Linux/macOS
- Run locally with:
  ```bash
  bash tools/build_linux.sh
  ```
- Adjust environment variables for custom library paths if needed.

## Common tips
- Use virtual environments per project to isolate dependencies.
- Regenerate spec or PyInstaller configuration after adding binary dependencies.
- For Android, clear the `.buildozer` folder if you encounter stale artifacts.
