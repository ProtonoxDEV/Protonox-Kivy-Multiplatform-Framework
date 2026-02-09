# Quick Reference — Copy-Paste Snippets

**Busy developer?** Grab the config you need in 30 seconds.

---

## 🔨 Build Commands

### Production Release APK
```bash
buildozer android release -v
# Output: bin/output-release-unsigned.apk
# Time: ~45 min (first build), ~20 min (rebuild)
```

### Fast Debug Build (Development)
```bash
buildozer android debug
# Output: bin/output-debug.apk
# Time: ~10-20 min (uses buildozer_dev.spec)
# Faster: No ProGuard obfuscation, includes debug symbols
```

### Native Code Build
```bash
buildozer -f -v android release -- --private=./android_app --package=org.protonox.app --version 0.1.6 --bootstrap=sdl2 --requirements=python3,kivy
# For native components (C/C++ via JNI)
# Uses: buildozer_native_bridge.spec
```

---

## 📱 Device Commands

### Install & Run
```bash
# Install debug APK
adb install -r bin/output-debug.apk

# Launch app (replace package name)
adb shell am start -n org.protonox.app/org.protonox.app.MainActivity

# View logs
adb logcat | grep protonox

# Uninstall
adb uninstall org.protonox.app
```

### Connect Wireless (Xiaomi)
```bash
# Pair device on same WiFi (scan QR or manual)
adb pair <device_ip>:port <pairing_code>

# After pairing
adb connect <device_ip>:port

# Verify
adb devices
```

### Get Device Info
```bash
adb shell getprop ro.build.version.release  # Android version
adb shell getprop ro.product.model          # Device model
adb shell dumpsys display                   # Screen resolution
adb shell pm list permissions               # Installed permissions
```

---

## ⚙️ buildozer.spec Snippets

### Minimal Permissions (5 items)
```ini
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CHANGE_NETWORK_STATE
```

### Camera + Media Permissions (12 items)
```ini
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,MODIFY_AUDIO_SETTINGS,READ_PHONE_STATE,ACCESS_WIFI_STATE,CHANGE_NETWORK_STATE
```

### All Permissions (40+ items)
See [PERMISSIONS_REFERENCE.md](PERMISSIONS_REFERENCE.md) for complete list.

### Android 16 Graphics (GLES 3.2)
```ini
android.archs = arm64-v8a,armeabi-v7a
android.api = 35
android.minapi = 24
KIVY_GL_BACKEND = gl_redirect
KIVY_GLES_BACKEND = gles2
android.add_src = src/
```

### Development Settings (Debug)
```ini
android.debug = 1
KIVY_GL_DEBUG = 1
android.logcat_filters = *:S python:D
android.enable_proguard = 0
android.add_compile_options = -g
```

### Production Settings (Optimized)
```ini
android.debug = 0
android.enable_proguard = 1
android.proguard_rules = ...
android.release_artifact = aab
android.add_compile_options = -O3
```

---

## 🚀 Python Environment

### Setup Virtual Environment
```bash
# Create
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install Protonox
pip install -e .
pip install -e ./kivy-protonox-version
```

### Check Versions
```bash
python -c "import kivy; print('Kivy:', kivy.__version__)"
python -c "from protonox.version import __version__; print('Protonox:', __version__)"
java -version
buildozer --version
```

### Install Dependencies
```bash
# Linux/Ubuntu
sudo apt install build-essential python3-dev python3-venv libsdl2-dev

# Install Python packages
pip install -r requirements.txt
pip install buildozer cython
```

---

## 🔍 Troubleshooting Commands

### Clear Build Cache
```bash
# Full clean
buildozer android clean

# Remove buildozer folder
rm -rf .buildozer/

# Rebuild everything
buildozer android release -v
```

### Check Build Logs
```bash
# Real-time logs
tail -f .buildozer/android/platform/build-*/build.log

# Full build log (saved)
cat .buildozer/android/platform/build-*/build.log | tail -100
```

### Debug Device Issues
```bash
# Check device connection
adb devices -l

# Check permissions
adb shell pm list permissions -d

# Monitor app crash
adb logcat | grep -i "fatal\|exception\|error"

# Clear app data
adb shell pm clear org.protonox.app
```

### Graphics Debugging
```bash
# Check OpenGL ES support
adb shell getprop ro.opengles.version

# Monitor GPU usage
adb shell dumpsys SurfaceFlinger
```

---

## 📦 Kivy/Android Paths

### Project Structure
```
.
├─ buildozer.spec          (Production config)
├─ buildozer_dev.spec      (Development config)
├─ buildozer.spec.backup   (Backup)
├─ protonox/
│  ├─ __init__.py
│  └─ version.py            (Canonical version)
├─ kivy-protonox-version/  (Kivy fork)
├─ android_app/            (APK source)
└─ docs/
   ├─ INDEX.md              (Start here)
   ├─ QUICK_START.md        (5 min setup)
   ├─ QUICK_REFERENCE.md    (This file)
   └─ ...
```

### Android Build Paths
```
.buildozer/
├─ android/
│  ├─ platform/
│  │  ├─ build-*/
│  │  │  ├─ build.log       (Build output)
│  │  │  └─ src/            (Android source)
│  │  └─ ...
│  └─ ...
```

### Output APK
```
bin/
├─ output-debug.apk               (Debug)
├─ output-release-unsigned.apk    (Production)
└─ ...
```

---

## 🔑 Environment Variables

### Development
```bash
export PROTONOX_KIVY=1                  # Enable Protonox Kivy
export PROTONOX_WIRELESS_DEBUG=1        # Wireless debug mode
export KIVY_GL_DEBUG=1                  # Graphics debugging
export PROTONOX_DIAGNOSTIC_BUS=1        # Detailed logging
```

### Build
```bash
export ANDROID_SDK_ROOT=/path/to/android-sdk
export ANDROID_NDK_ROOT=/path/to/ndk-28c
export JAVA_HOME=/path/to/java
```

---

## 📚 Common Issues & Fixes

### Issue: Build fails with "cython error"
**Fix**: `pip install 'cython>=3.0.0,<=3.3.0'`

### Issue: Device not recognized
**Fix**: `adb kill-server && adb start-server && adb devices`

### Issue: Permissions denied (Xiaomi)
**Fix**: See [XIAOMI_COMPLETE_GUIDE.md → Permissions](XIAOMI_COMPLETE_GUIDE.md)

### Issue: App crashes on launch
**Fix**: See [ANDROID16_STABILITY_REQUIREMENTS.md](ANDROID16_STABILITY_REQUIREMENTS.md)

### Issue: Graphics not rendering
**Fix**: Check [ANDROID16_COMPLETE_GUIDE.md → Graphics Stack](ANDROID16_COMPLETE_GUIDE.md#graphics-stack)

---

## 🔗 Related Guides

**Need more details?** See these comprehensive guides:

| Topic | Guide | Time |
|-------|-------|------|
| Full setup | [QUICK_START.md](QUICK_START.md) | 5 min |
| Device-specific | [XIAOMI_COMPLETE_GUIDE.md](XIAOMI_COMPLETE_GUIDE.md) | 15 min |
| Build config | [BUILDOZER_SPECIFICATION_GUIDE.md](BUILDOZER_SPECIFICATION_GUIDE.md) | 10 min |
| Permissions | [PERMISSIONS_REFERENCE.md](PERMISSIONS_REFERENCE.md) | 5 min |
| Troubleshooting | [ANDROID16_COMPLETE_GUIDE.md](ANDROID16_COMPLETE_GUIDE.md#troubleshooting) | 20 min |
| All docs | [INDEX.md](INDEX.md) | - |

---

**Copy-paste any snippet above and adapt to your needs. For context, see the full guides.**
