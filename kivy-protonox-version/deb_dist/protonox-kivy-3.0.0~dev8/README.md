Kivy
====

<img align="right" height="256" src="https://raw.githubusercontent.com/kivy/kivy/master/kivy/data/logo/kivy-icon-256.png"/>

[Kivy](https://www.kivy.org) is an open-source [Python](https://python.org) framework
for developing GUI apps that work cross-platform, including desktop, mobile and
embedded platforms.

**Fork notice (ProtonoxDEV)**: este repositorio es un fork mantenido por ProtonoxDEV. La distribución publicada en PyPI/TestPyPI se llama `protonox-kivy` y funciona como reemplazo directo del paquete `kivy`, pero no es la distribución oficial de Kivy. Se mantienen los avisos de licencia MIT del proyecto original.

### Modern Android readiness (15 → 16)

- Edge-to-edge deja de ser opcional: Android 16 espera barras de sistema transparentes y gestos en bordes; ignorar insets rompe la UI. Safe areas y padding dinámico deben ser parte del layout.
- Insets ahora son dinámicos: notch/hole, barra de gestos y teclado cambian con orientación, modo gestos, split-screen y foldables; el layout debe reaccionar en vivo.
- Ratios extremos (20:9, 22:9, foldables) exponen size_hint y px fijos pobres; assets raster bajos se notan.
- Gestos del sistema mandan: controles pegados a bordes compiten con back gesture; gestos custom deben respetar márgenes.
- IME/reflow: el teclado no siempre redimensiona; ScrollView + foco correcto es obligatorio para no tapar contenido.
- No cambió la GPU (OpenGL ES sigue 3.2 máx): el problema es la capa UI, no el render.

En este fork se prepara la librería para estas exigencias: se añade compatibilidad con widgets legacy de KivyMD (alias `state` en `ToggleButtonBehavior`) para evitar `KeyError` en apps existentes y se documentan los requerimientos de UI mobile-first para Android 16.

#### Helper para insets / notch (Android)
- Archivo: `kivy/protonox_ext/android_insets.py`
- Funciones clave:
  - `get_current_insets()` devuelve `top/bottom/left/right/ime_bottom` (0 en plataformas no Android).
  - `add_insets_listener(callback)` notifica cambios de insets (rotación, gestos, teclado, split-screen).
- Uso sugerido en tu App:
  ```python
  from kivy.protonox_ext import android_insets

  if android_insets.is_android():
      insets = android_insets.get_current_insets()
      # aplica padding dinámico a tu root layout con estos valores
      android_insets.add_insets_listener(lambda data: update_padding(data))
  ```
  Donde `update_padding` ajusta `padding`/`safe_*` en tus layouts para evitar solapes con notch, barras y teclado.

### Instalación vía PyPI

- PyPI: `pip install protonox-kivy==3.0.0.dev1` (se distribuye como sdist, compila una wheel local al instalar).
- TestPyPI (staging): `pip install --index-url https://test.pypi.org/simple protonox-kivy==3.0.0.dev1`.

Si tienes instalaciones previas de `kivy` o `protonox-kivy` en editable, desinstala primero: `pip uninstall -y kivy protonox-kivy`.

The aim is to allow for quick and easy interaction design and rapid prototyping
whilst making your code reusable and deployable: Innovative user interfaces made
easy.

Kivy is written in Python and [Cython](https://cython.org/) and is built on
[OpenGL ES 2.0](https://www.khronos.org/opengles/). It supports various input 
devices and has an extensive (and extensible) widget library. With the
same codebase, you can target Windows, macOS, Linux (including Raspberry Pi OS),
Android, and iOS. All Kivy widgets are built with multitouch support.

Kivy is [MIT licensed](LICENSE), actively developed by a great community and is
supported by many projects managed by the 
[Kivy Organization](https://www.kivy.org/about.html).

[![Backers on Open Collective](https://opencollective.com/kivy/backers/badge.svg)](#backers)
[![Sponsors on Open Collective](https://opencollective.com/kivy/sponsors/badge.svg)](#sponsors)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![GitHub contributors](https://img.shields.io/github/contributors-anon/kivy/kivy)](https://github.com/kivy/kivy/graphs/contributors)

![PyPI - Version](https://img.shields.io/pypi/v/kivy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kivy)

[![Windows Unittests Status](https://github.com/kivy/kivy/workflows/Windows%20Unittests/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22Windows+Unittests%22)
[![Ubuntu Unittests Status](https://github.com/kivy/kivy/workflows/Ubuntu%20Unittests/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22Ubuntu+Unittests%22)
[![OSX Unittests Status](https://github.com/kivy/kivy/workflows/OSX%20Unittests/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22OSX+Unittests%22)
[![Coverage Status](https://coveralls.io/repos/kivy/kivy/badge.svg?branch=master)](https://coveralls.io/r/kivy/kivy?branch=master)

[![Windows wheels Status](https://github.com/kivy/kivy/workflows/Windows%20wheels/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22Windows+wheels%22)
[![Manylinux wheels Status](https://github.com/kivy/kivy/workflows/Manylinux%20wheels/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22Manylinux+wheels%22)
[![Raspberry Pi wheels Status](https://github.com/kivy/kivy/workflows/RPi%20wheels/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22RPi+wheels%22)
[![OSX wheels Status](https://github.com/kivy/kivy/workflows/OSX%20wheels%2Fapp/badge.svg)](https://github.com/kivy/kivy/actions?query=workflow%3A%22OSX+wheels%2Fapp%22)

Installation, Documentation and Examples
----------------------------------------

Extensive installation instructions as well as tutorials and general
documentation, including an API reference, can be found at https://www.kivy.org/docs.
A [PDF version](https://media.readthedocs.org/pdf/kivy/latest/kivy.pdf) is also available.

Kivy ships with many examples which can be found in the `examples` folder.

### Desarrollo en Termux (Android)

`protonox-kivy` es compatible con Termux para desarrollo móvil directo. Incluye ScissorPush/ScissorPop y wireless debug.

#### Instalación en Termux
```bash
pkg install python clang make
pip install protonox-kivy==3.0.0.dev4
```

#### Uso Básico
```python
from kivy.graphics import ScissorPush, ScissorPop  # Funciona en Termux
from kivymd.app import MDApp

class MyApp(MDApp):
    def build(self):
        # Tu app aquí
        pass

if __name__ == '__main__':
    MyApp().run()
```

#### Wireless Debug
```bash
PROTONOX_WIRELESS_DEBUG=1 python app.py  # Muestra QR para conectar Studio
```

Para más detalles, ver el README principal del repositorio.

Support
-------

Are you having trouble using the Kivy framework, or any of its related projects?
Is there an error you don’t understand? Are you trying to figure out how to use 
it? We have volunteers who can help!

The best channels to contact us for support are listed in the latest 
[Contact Us](CONTACT.md) document.

Contributing
------------

We love pull requests and discussing novel ideas. Check out our
[latest contribution guide](CONTRIBUTING.md) and
feel free to improve Kivy.

It gives details of the best places online to discuss the development with the
core developers and other enthusiasts.

Sibling projects
----------------

The Kivy team manages a number of additional projects that support the Kivy 
eco-system.

- [Buildozer](https://github.com/kivy/buildozer):  a development tool for turning Python applications into binary packages ready for installation on
  any of a number of platforms, including mobile devices.
- [Plyer](https://github.com/kivy/plyer): a platform-independent Python API for accessing hardware features of various platforms (Android, iOS,
  macOS, Linux and Windows).
- [PyJNIus](https://github.com/kivy/pyjnius): a Python library for accessing Java classes using the Java Native Interface (JNI).
- [Pyobjus](https://github.com/kivy/pyobjus): Python module for accessing Objective-C classes as Python classes using 
  Objective-C runtime reflection.
- [Python for Android](https://github.com/kivy/python-for-android): a development tool that packages Python apps into binaries that can run on Android devices.
- [Kivy iOS](https://github.com/kivy/kivy-ios): a toolchain to compile the necessary libraries for iOS to run Kivy applications, and manage the
  creation of Xcode projects.
- [Audiostream](https://github.com/kivy/audiostream): library for direct access
  to the microphone and speaker.
- [KivEnt](https://github.com/kivy/kivent): entity-based game engine for Kivy.
- [Oscpy](https://github.com/kivy/oscpy/): a Python implementation of Open Sound Control (OSC) network protocol.
- [Garden](https://github.com/kivy-garden): widgets and libraries created and
  maintained by users.

Licenses
--------

- Kivy is released under the terms of the MIT License. Please refer to the
  [LICENSE](LICENSE) file.
- The provided fonts Roboto and Roboto Mono are licensed and
  distributed under the terms of the
  [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
  The DejaVuSans (used for the virtual keyboard) license can be viewed
  [here](https://github.com/dejavu-fonts/dejavu-fonts/blob/master/LICENSE).
- The current UI design has been adapted from Moblintouch theme's SVGs
  and is licensed under the terms of the
  [LGPLv2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1).


## Code of Conduct

In the interest of fostering an open and welcoming community, we as 
contributors and maintainers need to ensure participation in our project and 
our sister projects is a harassment-free and positive experience for everyone. 
It is vital that all interaction is conducted in a manner conveying respect, 
open-mindedness and gratitude.

Please consult the [latest Code of Conduct](https://github.com/kivy/kivy/blob/master/CODE_OF_CONDUCT.md).

## Bug Fixes and Code Quality Improvements

This section documents the bugs identified and fixes applied during the development of Protonox Kivy 3.0.0.dev2, ensuring code quality and maintainability before publication.

### Identified Bugs and Fixes

#### Syntax Errors and Warnings
- **SyntaxError in `kivy/protonox_ext/device/facade.py`**: Issue with reserved keyword 'from' in NotificationManagerCompat.from. **Fix**: Used `getattr(NotificationManagerCompat, 'from')` to access the attribute dynamically.
- **SyntaxWarnings in `kivy/protonox_ext/android_bridge/adb.py`**: Invalid escape sequences in strings. **Fix**: Converted to raw strings (e.g., `r"path\to\file"`).

#### Linting Issues (Flake8)
- **Unused Imports (F401)**: Numerous unused imports across files (e.g., `Dict`, `Callable`, `Iterable`, `Optional`, `json`, `enable_profile`). **Fix**: Removed using autoflake.
- **Unused Variables (F841)**: Local variables assigned but never used (e.g., `source`, `WifiManager`, `usleep`, `ClipDescription`). **Fix**: Removed using autoflake.
- **Bare Except Clauses (E722)**: `except:` without specifying exception type. **Fix**: Changed to `except Exception:` using sed.
- **Module Level Import Not at Top (E402)**: Imports not at the beginning of files. **Fix**: Sorted and moved imports to top using isort.
- **Trailing Whitespace (W291)**: Extra spaces at end of lines. **Fix**: Removed during cleanup.
- **Indentation Issues (E127, E128)**: Inconsistent indentation. **Fix**: Partially addressed via isort and manual edits.
- **Ambiguous Variable Names (E741)**: Variables named 'l', 'I', etc. **Fix**: Some renamed, others noted for future refactoring.
- **Other Style Issues**: Missing blank lines, semicolons, etc. **Fix**: Cleaned up during automated processing.

#### PyPI Packaging Issues
- **Metadata Errors**: Invalid `license-file` fields in setup.cfg. **Fix**: Removed deprecated fields.
- **Platform Tags**: Incorrect tags causing upload failures. **Fix**: Edited tar.gz artifacts to remove problematic tags.
- **Build Artifacts**: Issues with sdist/wheel generation. **Fix**: Used `python -m build` and twine for proper uploads.

### Tools Used for Code Quality
- **flake8**: Linting and error detection.
- **autoflake**: Automated removal of unused imports and variables.
- **isort**: Import sorting and organization.
- **sed**: Bulk replacement of bare except clauses.
- **py_compile**: Syntax validation.

### Impact
- **Files Modified**: 172 files cleaned up.
- **Commits**: Dedicated commit for linting fixes (ef79a41).
- **Codebase Status**: kivy_protonox/ fully compliant; kivy/ significantly improved.
- **Publication Readiness**: Code compiles without syntax errors, ready for PyPI release.

For full traceability, refer to Git history and commit messages.

## Contributors

This project exists thanks to 
[all the people who contribute](https://github.com/kivy/kivy/graphs/contributors).
[[Become a contributor](CONTRIBUTING.md)].

<img src="https://contrib.nn.ci/api?repo=kivy/kivy&pages=5&no_bot=true&radius=22&cols=18">

## Backers

Thank you to [all of our backers](https://opencollective.com/kivy)! 
🙏 [[Become a backer](https://opencollective.com/kivy#backer)]

<img src="https://opencollective.com/kivy/backers.svg?width=890&avatarHeight=44&button=false">

## Sponsors

Special thanks to 
[all of our sponsors, past and present](https://opencollective.com/kivy).
Support this project by 
[[becoming a sponsor](https://opencollective.com/kivy#sponsor)].

Here are our top current sponsors. Please click through to see their websites,
and support them as they support us. 

<!--- See https://github.com/orgs/kivy/discussions/15 for explanation of this code. -->
<a href="https://opencollective.com/kivy/sponsor/0/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/0/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/1/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/1/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/2/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/2/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/3/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/3/avatar.svg"></a>

<a href="https://opencollective.com/kivy/sponsor/4/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/4/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/5/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/5/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/6/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/6/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/7/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/7/avatar.svg"></a>

<a href="https://opencollective.com/kivy/sponsor/8/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/8/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/9/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/9/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/10/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/10/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/11/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/11/avatar.svg"></a>

<a href="https://opencollective.com/kivy/sponsor/12/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/12/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/13/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/13/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/14/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/14/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/15/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/15/avatar.svg"></a>
