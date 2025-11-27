# Android 15+ Setup

This guide covers preparing the Android toolchain for Protonox builds.

## Prerequisites
- Python 3.11+
- Java 17 (preferred) with `keytool`
- Android SDK command-line tools and NDK (r26b+)
- `adb` for device debugging

## Steps
1. Install SDK/NDK using the helper script:
   ```bash
   bash tools/setup_android_env.sh
   ```
2. Confirm environment variables:
   - `ANDROID_HOME` pointing to the SDK root
   - `ANDROID_NDK_HOME` pointing to the selected NDK
   - `PATH` includes `$ANDROID_HOME/platform-tools` and `$ANDROID_HOME/cmdline-tools/latest/bin`
3. Accept licenses:
   ```bash
   yes | sdkmanager --licenses
   ```
4. Connect a device or start an emulator and verify with `adb devices`.
5. Build your app:
   ```bash
   bash tools/build_android.sh
   ```

## Notes
- The Protonox forks inside `framework/` include patches for Android 15+ APIs, emoji handling, and Firebase compatibility.
- Ensure you replace the placeholder `google-services.json` with your own before packaging.
