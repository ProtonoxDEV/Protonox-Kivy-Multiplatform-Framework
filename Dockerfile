# Protonox Studio / Kivy 2.3.1 container (dev-only)
# Provides a reproducible environment for the Protonox Kivy fork and tooling.

FROM python:3.11-bullseye

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KIVY_USE_DEFAULT_SDL2=1

# System deps for Kivy and headless rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsdl2-dev libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 \
    libgl1-mesa-dev libgles2-mesa-dev libglu1-mesa \
    libx11-6 libxext6 libxrender1 libxrandr2 libxcursor1 libxinerama1 libxi6 \
    libmtdev-dev libasound2-dev \
    git curl unzip fonts-noto-color-emoji && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/app
COPY . /workspace/app

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -e ./kivy-protonox-version && \
    python -m pip install --no-cache-dir -e ./protonox-studio

# Default command prints help to show available tooling
CMD ["protonox", "--help"]
