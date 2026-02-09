# FAQ — Frequently Asked Questions

**Got questions?** Most are answered here.

---

## Installation & Setup

### Q1: Where do I start?
**A**: Read [QUICK_START.md](QUICK_START.md) — 5 minutes to get your first APK running.

### Q2: What Python version do I need?
**A**: Python 3.9-3.14. Officially supported: 3.10, 3.11, 3.12. Use `python --version` to check.

### Q3: Do I need Android Studio installed?
**A**: No. You need Android SDK & NDK (buildozer installs them automatically). Android Studio is optional.

### Q4: How long does the first build take?
**A**: 
- **First build**: 45-60 min (downloads SDK, NDK, builds everything)
- **Rebuild**: 10-20 min (uses debug spec)
- **Incremental**: 2-5 min (small changes)

### Q5: Can I build on Windows/Mac?
**A**: Yes, but **Linux is recommended**. See [docs/ENVIRONMENT.md](ENVIRONMENT.md) for platform-specific setup.

### Q6: Do I need a PyPI account to use Protonox?
**A**: No. Protonox is open-source. You only need a PyPI account if you want to publish your own package.

---

## Device & Testing

### Q7: How do I test on my phone?
**A**: 
1. Enable USB Debugging (Settings → Developer Options)
2. Connect via USB
3. Run: `adb install -r bin/output-debug.apk`
4. See [QUICK_REFERENCE.md → Device Commands](QUICK_REFERENCE.md#-device-commands)

### Q8: Can I test wirelessly without USB?
**A**: Yes! Use wireless ADB pairing. See [QUICK_REFERENCE.md → Connect Wireless](QUICK_REFERENCE.md#connect-wireless-xiaomi)

### Q9: I have a Xiaomi phone. What should I know?
**A**: Read [XIAOMI_COMPLETE_GUIDE.md](XIAOMI_COMPLETE_GUIDE.md) — 5 critical quirks that affect your app.

### Q10: What Android versions are supported?
**A**: 
- **Min**: Android 7.0 (API 24)
- **Target**: Android 16 (API 35) — recommended for performance
- **Tested**: API 24-35

### Q11: Can I use Protonox with older Android devices?
**A**: Yes, but performance will be lower. Aim for Android 10+ (API 29+) for good experience. See [ANDROID16_COMPLETE_GUIDE.md](ANDROID16_COMPLETE_GUIDE.md).

---

## Build & Configuration

### Q12: Which buildozer.spec should I use?
**A**: 
- **Production**: `buildozer.spec` (optimized, ProGuard enabled)
- **Development**: `buildozer_dev.spec` (fast, debug symbols)
- **Native code**: `buildozer_native_bridge.spec` (C/C++ via JNI)

See [BUILDOZER_SPECIFICATION_GUIDE.md → Decision Tree](BUILDOZER_SPECIFICATION_GUIDE.md#decision-tree)

### Q13: Can I customize the app permissions?
**A**: Yes. Edit the `android.permissions` line in buildozer.spec. See [PERMISSIONS_REFERENCE.md](PERMISSIONS_REFERENCE.md) for all available permissions.

### Q14: How do I add native C/C++ code?
**A**: Use `buildozer_native_bridge.spec` and place code in `android_app/jni/`. See [NATIVE_COMPONENTS_README.md](../NATIVE_COMPONENTS_README.md).

### Q15: What graphics API does Protonox use?
**A**: **Primary**: OpenGL ES 3.2 (10x faster than ES 2.0). **Optional**: Vulkan 1.4. See [ANDROID16_COMPLETE_GUIDE.md → Graphics](ANDROID16_COMPLETE_GUIDE.md#graphics-stack).

---

## Troubleshooting

### Q16: My build fails with "cython" errors
**A**: Run: `pip install 'cython>=3.0.0,<=3.3.0'`

### Q17: "adb devices" shows offline devices
**A**: 
```bash
adb kill-server
adb start-server
adb devices
```

### Q18: App crashes immediately on launch
**A**: 
1. Check logs: `adb logcat | grep protonox`
2. See [ANDROID16_STABILITY_REQUIREMENTS.md](ANDROID16_STABILITY_REQUIREMENTS.md)
3. Common causes: Missing permissions, library not found, incompatible Kivy version

### Q19: Graphics/video not rendering
**A**: 
1. Check device supports OpenGL ES 3.2: `adb shell getprop ro.opengles.version`
2. See [ANDROID16_COMPLETE_GUIDE.md → Graphics Stack](ANDROID16_COMPLETE_GUIDE.md#graphics-stack)
3. Try fallback to ES 2.0 in buildozer.spec (slower but more compatible)

### Q20: Where are the build logs?
**A**: 
```bash
# Real-time
tail -f .buildozer/android/platform/build-*/build.log

# Full log
cat .buildozer/android/platform/build-*/build.log
```

---

## Version & Release

### Q21: What version of Protonox is current?
**A**: Check [protonox/version.py](../protonox/version.py) for canonical version (currently 3.0.0.dev13).

### Q22: How do I bump the version?
**A**: Edit `protonox/version.py` (single source of truth), then rebuild. See [VERSION_STRATEGY.md](VERSION_STRATEGY.md).

### Q23: Can I publish my app to Google Play?
**A**: Yes. Build with `buildozer android release` and follow Google Play submission process. See [PUBLISHING.md](../PUBLISHING.md).

### Q24: What's the release schedule?
**A**: 
- **v3.0.0**: Feb 2026 (current: dev13)
- **v3.1.0**: Q2 2026
- **v4.0.0**: 2027+ (far future)

See [VERSION_STRATEGY.md](VERSION_STRATEGY.md) for details.

---

## Performance & Optimization

### Q25: How do I make my app faster?
**A**: 
1. Use OpenGL ES 3.2 (not ES 2.0)
2. Enable ProGuard in buildozer.spec
3. Use `buildozer android release` (not debug)
4. Profile with `adb shell dumpsys gfxinfo`

See [ANDROID16_COMPLETE_GUIDE.md → Performance](ANDROID16_COMPLETE_GUIDE.md#performance-optimization).

### Q26: What's the minimum RAM needed?
**A**: 
- **Build machine**: 8GB (4GB min, 16GB recommended)
- **Target device**: 2GB (4GB+ recommended for smooth graphics)

### Q27: How do I debug performance issues?
**A**: 
```bash
# Monitor frame rate
adb shell dumpsys SurfaceFlinger

# Check GPU usage
adb shell top -n 1 | grep grafika

# Profile with built-in tools
# See ANDROID16_COMPLETE_GUIDE.md
```

---

## Kivy-Specific

### Q28: How is Protonox different from vanilla Kivy?
**A**: Protonox is a fork optimized for **Android 16** with:
- Graphics stack: GLES 3.2 + Vulkan 1.4
- Better device integration
- Performance improvements
- Maintained compatibility with Kivy 2.3.1

See [ANDROID16_COMPLETE_GUIDE.md](ANDROID16_COMPLETE_GUIDE.md) for details.

### Q29: Can I use both Protonox and vanilla Kivy in same project?
**A**: Not recommended. Use one or the other. We recommend Protonox for Android apps.

### Q30: Where's the Kivy documentation?
**A**: [Kivy Official Docs](https://kivy.org/doc/current/). Protonox docs at [INDEX.md](INDEX.md).

---

## Not Answered Here?

**See comprehensive guides:**

| Topic | Guide |
|-------|-------|
| Full setup | [QUICK_START.md](QUICK_START.md) |
| Copy-paste snippets | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Device-specific | [XIAOMI_COMPLETE_GUIDE.md](XIAOMI_COMPLETE_GUIDE.md) |
| Build configuration | [BUILDOZER_SPECIFICATION_GUIDE.md](BUILDOZER_SPECIFICATION_GUIDE.md) |
| Android 16 details | [ANDROID16_COMPLETE_GUIDE.md](ANDROID16_COMPLETE_GUIDE.md) |
| Permissions | [PERMISSIONS_REFERENCE.md](PERMISSIONS_REFERENCE.md) |
| All topics | [INDEX.md](INDEX.md) |

---

**Can't find your answer?** Open an issue on GitHub or check [INDEX.md](INDEX.md) for more resources.
