Debian/Ubuntu system dependencies for full SDL3 + Pango support
===============================================================

To run Kivy with SDL3 window backend and PangoFT2 text rendering on Debian/Ubuntu
install these system packages. They are required when binary wheels for native
libs are not available for your platform and when building from source:

```bash
sudo apt update
sudo apt install -y pkg-config build-essential cython3 \
  libsdl3-2.0-0 libsdl3-dev libsdl3-ttf-2.0-0 \
  libpango1.0-0 libpango1.0-dev libfreetype6-dev libfontconfig1-dev
```

Notes
- We also publish (and reference via extras) the `kivy_deps.sdl3` and
  `kivy_deps.sdl3_dev` PyPI packages which provide manylinux wheels for SDL3
  where available. Prefer installing `kivy` with the `sdl3` extra so pip can
  pull prebuilt native wheels when possible:

```bash
pip install "protonox-kivy[sdl3]"
```

- If you install via the generated Debian package (`.deb`), the package's
  `Depends` should include the system libraries (libpango, libfreetype, libgl1,
  etc.) and `apt` will install them automatically.

- For a fully self-contained runtime consider distributing an AppImage,
  Flatpak or container that bundles the native libraries; pip wheels cannot
  install system packages via `apt`.
