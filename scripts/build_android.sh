#!/bin/bash
# Protonox-Kivy Android Build Script
# Optimized build script with error checking and logging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ Please activate the buildozer virtual environment first:${NC}"
    echo "source venv_buildozer/bin/activate"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "buildozer.spec" ]; then
    echo -e "${RED}❌ buildozer.spec not found. Please run from app directory.${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Starting Protonox-Kivy Android Build${NC}"

# Function to check build success
check_build_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Build completed successfully!${NC}"
        echo -e "${BLUE}📱 APK location: $(pwd)/*.apk${NC}"

        # Check APK architecture
        if [ -f "*.apk" ]; then
            echo -e "${YELLOW}🔍 Checking APK architecture...${NC}"
            # Extract and check .so files (basic check)
            echo "To verify architecture manually:"
            echo "unzip -l *.apk | grep '\.so$' | head -5"
        fi
    else
        echo -e "${RED}❌ Build failed!${NC}"
        echo -e "${YELLOW}📖 Check docs/ANDROID_BUILD_LESSONS.md for common issues${NC}"
        exit 1
    fi
}

# Clean build option
if [ "$1" = "clean" ]; then
    echo -e "${YELLOW}🧹 Cleaning previous build...${NC}"
    buildozer android clean
    echo -e "${GREEN}✅ Clean completed${NC}"
fi

# Build APK
echo -e "${BLUE}🔨 Building Android APK...${NC}"
echo "This may take 30-60 minutes..."
buildozer android debug

check_build_success

# Optional deploy
if [ "$1" = "deploy" ] || [ "$2" = "deploy" ]; then
    echo -e "${BLUE}📤 Deploying to device...${NC}"
    buildozer android debug deploy

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Deploy completed${NC}"

        if [ "$1" = "run" ] || [ "$2" = "run" ]; then
            echo -e "${BLUE}🎮 Launching app...${NC}"
            buildozer android debug deploy run
        fi
    fi
fi

echo -e "${GREEN}🎉 All done! Check your device for the app.${NC}"