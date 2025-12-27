# Release Notes — protonox-kivy 3.0.0

**Release Date:** December 27, 2025

## Overview

This development release focuses on **Android development experience improvements** and **cross-compilation fixes**. Major enhancements include automated build tools, comprehensive documentation, and resolved architecture compatibility issues for modern Android devices.

## 🚀 Key Features

### Android Development Experience Overhaul

#### 🔧 Automated Development Environment
- **One-command setup**: `setup_android_dev.sh` script for complete environment preparation
- **Optimized build script**: `build_android.sh` with colored output, error checking, and deployment options
- **Cross-compilation fixes**: Resolved ARM64 architecture compilation issues
- **Dependency management**: Automated venv creation and package installation

#### 📚 Comprehensive Documentation
- **Troubleshooting guide**: `ANDROID_BUILD_LESSONS.md` covering common issues and solutions
- **Build best practices**: NDK r28c requirements, environment isolation, and debugging techniques
- **Developer onboarding**: Step-by-step guides for Android development setup

#### 🏗️ Project Templates
- **Minimal app template**: Pre-configured `protonox-app-minimal` with optimized buildozer.spec
- **Ready-to-build**: Includes proper Android 16+ configuration and asset placeholders
- **Best practices**: ARM64-focused builds with modern Android API targets

#### 🚀 CI/CD Integration
- **Automated APK builds**: GitHub Actions workflow for continuous integration
- **Multi-platform testing**: Framework and template validation
- **Release automation**: APK artifacts and automated release creation

### Technical Improvements

#### Android Build System
- **Meson build support**: Updated python-for-android recipes with modern Meson integration
- **OpenGL ES 3.2**: Minimum version requirement for modern Android devices
- **SDL3 backend**: Complete SDL3 support with HarfBuzz text rendering
- **Cross-platform wheels**: Improved wheel building and distribution

#### Architecture Fixes
- **ARM64 compilation**: Fixed cross-compilation issues for 64-bit Android devices
- **Environment isolation**: Proper separation of build and target architectures
- **Dependency resolution**: Correct handling of native library dependencies

#### Developer Tools
- **Enhanced error messages**: Detailed logging in p4a recipes with troubleshooting guidance
- **Build validation**: APK verification and architecture checking
- **Wireless debugging**: Improved ADB and network debugging capabilities

## 🔧 Bug Fixes

### Android Compatibility
- Fixed APK runtime failure due to x86_64 extensions on ARM64 devices
- Resolved cross-compilation environment variable conflicts
- Corrected buildozer.spec path configurations for custom recipes

### Build System
- Fixed "meson not found" errors during Android compilation
- Improved NumPy recipe with Meson-based compilation
- Enhanced error handling in build processes

### Documentation
- Added comprehensive Android build troubleshooting guide
- Created developer experience improvement documentation
- Updated setup and deployment guides

## 📦 Distribution

### PyPI
- **Package**: `protonox-kivy==3.0.0`
- **Format**: Source distribution (sdist)
- **Platform**: Cross-platform with Android ARM64 support

### Installation
```bash
pip install protonox-kivy==3.0.0
```

### Android Development Setup
```bash
# Automated setup
./scripts/setup_android_dev.sh

# Build APK
./scripts/build_android.sh

# Deploy to device
./scripts/build_android.sh --deploy
```

## 🔄 Migration Guide

### From Previous Versions
- No breaking changes in public API
- Improved Android build compatibility
- Enhanced development tools (opt-in)

### New Projects
Use the provided templates for best results:
```bash
cp -r templates/protonox-app-minimal my_app
cd my_app
# Follow README.md for build instructions
```

## 📋 Known Issues

### Android Builds
- Wheel distribution limited to source packages
- Some dependencies may require manual compilation
- Testing recommended on target devices

### Development Tools
- CI/CD workflows require GitHub repository setup
- Some scripts require bash environment

## 🔮 Future Plans

### Short Term (dev13+)
- Complete wheel distribution for multiple platforms
- Enhanced error reporting and diagnostics
- Improved template customization options

### Medium Term
- Full Android Studio integration
- Advanced debugging and profiling tools
- Plugin ecosystem for custom recipes

## 🤝 Contributing

This release includes contributions from:
- Android build system improvements
- Cross-compilation fixes
- Developer experience enhancements
- Documentation updates

## 📞 Support

- **Documentation**: See `docs/` directory and `ANDROID_BUILD_LESSONS.md`
- **Issues**: GitHub repository issues
- **Community**: Discord/GitHub discussions

---

**Checksums:**
- SHA256: `protonox_kivy-3.0.0.tar.gz`

**Build Information:**
- Python: 3.9+
- Android NDK: r28c
- Android API: 24-36
- SDL: 3.0+
- OpenGL ES: 3.2+

---

*This development release focuses on stability and developer experience. Production deployments should wait for stable releases.*</content>
<parameter name="filePath">/home/protonox/Protonox-Kivy-Multiplatform-Framework/kivy-protonox-version/RELEASE_NOTES-3.0.0.md