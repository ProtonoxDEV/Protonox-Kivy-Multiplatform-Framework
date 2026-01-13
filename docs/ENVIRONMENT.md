# Entorno de desarrollo recomendado — Protonox & Kivy (completo, reproducible)

Este documento describe un **entorno de desarrollo específico para Kivy** orientado a Protonox. Está pensado para ser completo, claro y con visión de futuro — sin mediocridad, manteniendo pasos prácticos y verificables.

Referencia oficial de Kivy: https://kivy.org/doc/stable/gettingstarted/installation.html

----

## Resumen (recomendación principal)

- Python: **3.12** (soportado: 3.10–3.14). Usar siempre un virtual environment (`venv`) por proyecto.
- Sistema base: Linux (Ubuntu/Debian) recomendado para desarrollo. Añadimos pasos para macOS, Windows y Termux.
- Instalar dependencias de sistema (SDL2, GStreamer opcional, OpenGL headers, compilers) antes de instalar Kivy o `protonox-kivy`.
- Instalar `protonox` y `protonox-kivy` en modo editable para desarrollo local.
- Verificar con `python -c "import kivy; print(kivy.__version__)"` y `python3 run_tests.py`.

----

## Requisitos del sistema (Linux/Ubuntu/Debian)

Ejecuta como usuario con sudo:

```bash
# Actualizar
sudo apt update && sudo apt upgrade -y

# Compiladores y utilidades
sudo apt install -y build-essential git pkg-config cmake libgl1-mesa-dev libgles2-mesa-dev libffi-dev libssl-dev python3-dev python3-venv python3-pip

# Dependencias Kivy recomendadas (SDL2)
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Opcional: GStreamer para soporte multimedia
sudo apt install -y gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad

# Extra (recomendado para builds reproducibles)
sudo apt install -y libfreetype6-dev libjpeg-dev zlib1g-dev libpng-dev libssl-dev libxrandr-dev libxcursor-dev libxi-dev libxinerama-dev libx11-dev
```

Notas: si usas Fedora/Mac/Windows, consulta las instrucciones oficiales de Kivy para paquetes equivalentes.

----

## Preparar Python & venv (reproducible)

```bash
# Usar Python 3.12 (ejemplo con pyenv)
# pyenv install 3.12.x
# pyenv local 3.12.x

# Crear y activar venv en la raíz del repo
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip build setuptools wheel
```

----

## Instalación del entorno Protonox (local / editable)

1. Instala el CLI y librería en modo editable:

```bash
# Desde la raíz del repositorio
pip install -e .

# Instala el fork de Kivy Protonox para dev
pip install -e ./kivy-protonox-version

# Si prefieres instalar desde wheel local (más rápido)
pip install dist_debug_wheel/protonox_kivy-*.whl
```

2. Instalar dependencias del repo (si existen):

```bash
pip install -r requirements.txt || true
```

3. Validar instalación de Kivy:

```bash
python -c "import kivy; print('Kivy', kivy.__version__, kivy.__file__)"
# debe mostrar una versión 3.0.x cuando se usa protonox-kivy
```

----

## Variables de entorno útiles (modo desarrollo)

- `PROTONOX_KIVY=1` — activa compatibilidad Protonox (opt-in)
- `PROTONOX_WIRELESS_DEBUG=1` — activa wireless debug (QR pairing)
- `PROTONOX_DIAGNOSTIC_BUS=1` — estructura logs para debugging

Ejemplo:
```bash
export PROTONOX_KIVY=1
export PROTONOX_WIRELESS_DEBUG=1
```

----

## Docker (opcional, reproducible en CI)

Existe un `Dockerfile` en el repo; recomendamos construir una imagen dev reproducible:

```bash
docker build -t protonox-dev -f Dockerfile .
# Ejecuta shell en contenedor
docker run --rm -it -v "$PWD":/workspace -w /workspace protonox-dev bash
```

En CI: fijar `python-version: 3.12` y ejecutar `pip install -e . && pip install -e ./kivy-protonox-version`.

----

## macOS / Windows / Termux (resumen)

- macOS: usar `brew` para dependencias (sdl2, gstreamer, pkg-config). Instala Python 3.12 con pyenv/homebrew.
- Windows: usar MSYS2/Chocolatey para paquetes y seguir la guía oficial de Kivy para Windows.
- Termux (Android): `pkg install python clang make` — usar `pip install protonox-kivy==<dev>` y activar variables para debug (esto es para desarrollo en device).

----

## Automatización del setup (scripts/setup_dev.sh)

Se recomienda tener un script que automatice los pasos básicos (crear venv, instalar dependencias y validar). También puede incluir un `--ci` mode para reproducible non-interactive setups.

----

## Verificación final & tests

Comandos de verificación:

```bash
# Version check
python -c "import kivy; print('Kivy', kivy.__version__)"

# Ejecutar suite de tests del repo
python3 run_tests.py
```

Si un test falla por versión de Kivy (p.ej. muestra 2.x), revisa que tu venv esté activo y que `kivy` provenga de `kivy-protonox-version` (reinstala con `pip install -e ./kivy-protonox-version`).

----

## Buenas prácticas

- No versionar venvs ni artefactos (están en `.gitignore`).
- Documentar cualquier archivo grande movido a `archive/` (ya añadimos `archive/ARCHIVE_MANIFEST.md`).
- Mantener `pyproject.toml` o `requirements.txt` con versiones ancladas para reproducibilidad (p.ej. `pip freeze --exclude-editable > constraints.txt`).
- Usar CI con `python-version: 3.12` y matrices de dependencias para detectar roturas tempranas.

----

## Troubleshooting rápido

- Problema: `import kivy` carga v2.3.1 en lugar de protonox-kivy -> activa el venv, reinstala `pip install -e ./kivy-protonox-version` y revisa `python -c "import kivy; print(kivy.__file__)"`.
- Problema: build falla por SDL2 -> instala libsdl2-dev del sistema.

----

Si quieres, puedo convertir esta guía en una página más detallada con checkscripts, plantillas de CI y un `make dev` que lo automatice todo.
