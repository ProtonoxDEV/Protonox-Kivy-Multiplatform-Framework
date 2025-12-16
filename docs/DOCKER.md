# Protonox Studio + Kivy 2.3.1 — Docker Guide

This image provides a reproducible environment for the Protonox Kivy fork and
Protonox Studio tooling. It mirrors the local CLI so you can run audits and
Web→Kivy exports without installing system dependencies on the host.

## Build

```bash
docker build -t protonox-kivy-dev .
```

## Run (interactive shell)

```bash
docker run -it --rm \
  -v "$PWD":/workspace/app \
  protonox-kivy-dev bash
```

## Common commands

- `protonox --help` – list available CLI commands
- `protonox audit --project-type web --entrypoint index.html` – run the neutral
  model audit inside the container (no code modifications)
- `protonox web-to-kivy --project-type web --entrypoint index.html --map protonox_studio.yaml`
  – generate KV/controller exports into `.protonox` without touching your code
- `protonox validate --baseline web.png --candidate kivy.png --path .`
  – compute PNG diff ratios and bounding-box deltas (uses the neutral UI model
  derived from `--path` when available)

## Android tooling inside Docker

The base image includes ADB discovery hooks but not the full Android SDK. Mount
`ANDROID_HOME`/`ANDROID_SDK_ROOT` and `platform-tools` from the host to enable
ADB operations:

```bash
docker run -it --rm \
  -v "$PWD":/workspace/app \
  -v "$ANDROID_SDK_ROOT":/android-sdk \
  -e ANDROID_SDK_ROOT=/android-sdk \
  protonox-kivy-dev protonox diagnose
```

The `android_preflight` helper will report missing pieces without mutating the
project or the device.
