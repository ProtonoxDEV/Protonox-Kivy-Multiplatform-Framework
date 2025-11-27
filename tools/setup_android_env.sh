#!/usr/bin/env bash
set -euo pipefail

SDK_ROOT="${ANDROID_HOME:-$HOME/Android/Sdk}"
NDK_VERSION="26.1.10909125"

mkdir -p "$SDK_ROOT"
cd "$SDK_ROOT"

if [ ! -d "$SDK_ROOT/cmdline-tools" ]; then
  echo "Downloading Android command-line tools..."
fi

sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0" "ndk;$NDK_VERSION"

echo "Android SDK/NDK ready at $SDK_ROOT"
