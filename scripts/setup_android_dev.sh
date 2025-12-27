#!/bin/bash
# Protonox-Kivy Android Development Setup Script
# This script sets up the development environment for Android builds

set -e

echo "🚀 Setting up Protonox-Kivy Android Development Environment"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "framework" ]; then
    echo "❌ Please run this script from the Protonox-Kivy-Multiplatform-Framework root directory"
    exit 1
fi

# Create and activate virtual environment for buildozer
echo "📦 Creating buildozer virtual environment..."
python3 -m venv venv_buildozer
source venv_buildozer/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install buildozer and dependencies
echo "🔧 Installing buildozer and python-for-android..."
pip install buildozer python-for-android

# Install additional dependencies
pip install cython kivy

# Check for Android SDK/NDK
echo "📱 Checking Android development tools..."
if ! command -v adb &> /dev/null; then
    echo "⚠️  ADB not found. Please install Android SDK platform tools."
    echo "   On Ubuntu: sudo apt install android-tools-adb"
fi

if ! command -v java &> /dev/null; then
    echo "⚠️  Java not found. Please install OpenJDK 17+."
    echo "   On Ubuntu: sudo apt install openjdk-17-jdk"
fi

# Create .buildozer directory if it doesn't exist
mkdir -p .buildozer

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your buildozer.spec file"
echo "2. Run: source venv_buildozer/bin/activate"
echo "3. Build: buildozer android debug"
echo ""
echo "📖 See docs/ANDROID_BUILD_LESSONS.md for troubleshooting"