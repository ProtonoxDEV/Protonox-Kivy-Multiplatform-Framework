# Protonox App Minimal Template

A minimal template for creating Protonox-Kivy applications optimized for Android deployment.

## Features

- **Protonox-Kivy v3.0.0**: Latest framework with Android 16 support
- **KivyMD Integration**: Material Design components
- **ARM64 Optimized**: Pre-configured for Android ARM64 architecture
- **Hot Reload Ready**: Compatible with Protonox-Studio development tools
- **Cross-Platform**: Works on Android, iOS, Windows, macOS, and Linux

## Quick Start

1. **Copy this template:**
   ```bash
   cp -r templates/protonox-app-minimal my_new_app
   cd my_new_app
   ```

2. **Set up development environment:**
   ```bash
   # Run the automated setup script from the root directory
   ../scripts/setup_android_dev.sh
   ```

3. **Build for Android:**
   ```bash
   # Activate the build environment
   source venv_buildozer/bin/activate

   # Build the APK
   ../scripts/build_android.sh
   ```

4. **Deploy and test:**
   ```bash
   # Deploy to connected Android device
   ../scripts/build_android.sh --deploy

   # Or build and run in one command
   ../scripts/build_android.sh --run
   ```

## Project Structure

```
my_new_app/
├── main.py              # Main application code
├── buildozer.spec       # Build configuration for Android/iOS
├── assets/              # Images, icons, sounds
│   ├── icon.png
│   └── presplash.png
└── README.md           # This file
```

## Configuration

The `buildozer.spec` file is pre-configured with:

- **Android 16 Support**: NDK r28, API 36
- **ARM64 Architecture**: Optimized for modern Android devices
- **Protonox-Kivy Framework**: Custom recipe integration
- **Material Design**: KivyMD components included

## Development

### Using Protonox-Studio

For enhanced development experience with hot reload:

```bash
# Install Protonox-Studio
pip install protonox-studio==0.1.5

# Start development server
protonox-studio dev
```

### Manual Testing

Run the app locally for testing:

```bash
python main.py
```

## Build Customization

### Changing App Details

Edit `buildozer.spec`:

```ini
[app]
title = My Custom App
package.name = my_custom_app
package.domain = com.example
```

### Adding Dependencies

Add Python packages to requirements:

```ini
requirements = python3,protonox-kivy==3.0.0,kivymd==1.2.0,requests
```

### Android Permissions

Add required permissions:

```ini
android.permissions = INTERNET,CAMERA,LOCATION
```

## Troubleshooting

If you encounter build issues:

1. **Check the troubleshooting guide:**
   ```bash
   cat ../docs/ANDROID_BUILD_LESSONS.md
   ```

2. **Clean and rebuild:**
   ```bash
   ../scripts/build_android.sh --clean
   ```

3. **Check logs:**
   ```bash
   tail -f .buildozer/android/platform/build/build.log
   ```

## Support

- **Documentation**: See `../docs/` directory
- **Issues**: Check `../docs/troubleshooting.md`
- **Community**: Protonox Framework Discord/GitHub

## License

This template is part of the Protonox-Kivy framework. See root LICENSE file.