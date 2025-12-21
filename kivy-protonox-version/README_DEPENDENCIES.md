kivy-dependencies (local bundling for native libs)
===============================================

This repository supports bundling prebuilt native dependencies (SDL3, GStreamer,
etc.) into a local directory so wheels can be built against them and CI can
produce self-contained artifacts.

Layout
------
Place platform-specific libs under `kivy-dependencies/dist/lib` and headers under
`kivy-dependencies/dist/include`. Example:

kivy-dependencies/
  dist/
    lib/
      libSDL3.so
      libSDL3_image.so
    include/
      SDL3/

Usage
-----
- To install an archive into the local deps dir:

  ```bash
  python tools/check_kivy_deps.py --install path/to/kivy-deps-linux.tar.gz
  ```

- To list current contents:

  ```bash
  python tools/check_kivy_deps.py --list
  ```

Building
--------
When `kivy-dependencies` exists, `setup.py` will automatically prefer it as
`KIVY_DEPS_ROOT` so building a wheel will link against those libraries. To
build a wheel that uses them:

```bash
python -m build
pip install dist/protonox-kivy-*.whl
```

Enabling SDL3 explicitly
------------------------
- Default is still SDL2. To enable SDL3 during build use:

```bash
USE_SDL3=1 python -m build
```

CI
--
In CI you can upload prepared `kivy-dependencies` artifacts and extract them into
this directory before running the wheel build. That produces wheels with the
native libs resolved via pkg-config using the local tree.
