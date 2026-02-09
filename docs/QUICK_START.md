# Quick Start — Protonox Kivy in 5 Minutes

**Goal**: Build & run your first Protonox app on Android.

---

## Prerequisites (90 seconds)

✅ **Check if you have**:
- Python 3.9+: `python --version`
- Java JDK 11+: `java -version`
- Android SDK: Installed (API 35 preferred)
- Buildozer: `pip install buildozer`

**On Linux/Ubuntu?** Install system deps:
```bash
sudo apt install build-essential git python3-dev python3-venv libsdl2-dev
```

---

## Setup (2 minutes)

### 1. Clone & enter repo
```bash
git clone https://github.com/ProtonoxDEV/Protonox-Kivy-Multiplatform-Framework.git
cd Protonox-Kivy-Multiplatform-Framework
```

### 2. Create Python virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Protonox
```bash
pip install -e .
pip install -e ./kivy-protonox-version  # Local Kivy fork
```

### 4. Verify installation
```bash
python -c "import kivy; print('Kivy:', kivy.__version__)"
```

---

## Build Your First APK (3 minutes)

### Option A: Production build (Recommended)
```bash
# Build optimized release APK
buildozer android release -v

# Output: bin/output-release-unsigned.apk
```

### Option B: Debug build (Faster)
```bash
# Build debug APK (10-20 min instead of 30-45 min)
buildozer android debug

# Output: bin/output-debug.apk
```

---

## Deploy to Device (1 minute)

### Prerequisites
- **USB cable** connected to device
- **USB debugging enabled** (Developer Options → USB Debugging)

### Install APK
```bash
adb install -r bin/output-debug.apk
# or for release
adb install -r bin/output-release-unsigned.apk
```

### Launch app
```bash
# Find your app's package name (example: org.protonox.app)
adb shell am start -n org.protonox.app/org.protonox.app.MainActivity
```

---

## Having Issues?

**Build fails?** → See [ANDROID16_COMPLETE_GUIDE.md → Troubleshooting](ANDROID16_COMPLETE_GUIDE.md#troubleshooting)

**On Xiaomi?** → See [XIAOMI_COMPLETE_GUIDE.md → Setup](XIAOMI_COMPLETE_GUIDE.md#setup)

**Need help?** → See [docs/INDEX.md](INDEX.md) for full documentation

---

## What's Next?

- 📖 **Learn more**: [docs/INDEX.md](INDEX.md) — Full documentation map
- 🎮 **Graphics guide**: [ANDROID16_COMPLETE_GUIDE.md → Graphics](ANDROID16_COMPLETE_GUIDE.md#graphics-stack)
- ⚙️ **Configure build**: [BUILDOZER_SPECIFICATION_GUIDE.md](BUILDOZER_SPECIFICATION_GUIDE.md)
- 📱 **Device config**: [XIAOMI_COMPLETE_GUIDE.md](XIAOMI_COMPLETE_GUIDE.md) or [ANDROID16_COMPLETE_GUIDE.md](ANDROID16_COMPLETE_GUIDE.md)

---

**✅ Done!** You just built & deployed your first Protonox app.
