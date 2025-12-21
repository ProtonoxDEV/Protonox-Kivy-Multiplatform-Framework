# protonox-kivy 3.0.0.dev6 — Notas de la versión

Fecha: 2025-12-20

Resumen de cambios principales respecto a versiones anteriores (dev5 y previas):

- Compatibilidad y packaging
  - Se generó `USE_SDL2` en `kivy/setupconfig.py` durante el `setup.py` para mantener
    compatibilidad con código legado que importaba `USE_SDL2` (evita ImportError).
  - Se cambió el comportamiento por defecto para seguir usando SDL2. SDL3 ahora es
    opt-in (`c_options['use_sdl3'] = False` por defecto) y puede habilitarse vía
    variable de entorno o flags de build.
  - Se añadió manejo para un directorio local `kivy-dependencies` (detectado en
    el árbol fuente) para permitir bundling de bibliotecas nativas en CI o local.
  - `setup.cfg` limpiado de `license_files` para evitar campos `License-File` inválidos
    que PyPI/Twine rechazaban; se corrigió METADATA antes de subir.

- Artefactos y publicación
  - Bumped `kivy/_version.py` → `3.0.0.dev6`.
  - Construcción de sdist y wheel local (`python -m build`).
  - Se subió el *sdist* de `protonox-kivy==3.0.0.dev6` a PyPI (https://pypi.org/project/protonox-kivy/3.0.0.dev6/).
  - La rueda binaria fue rechazada por PyPI por tener un tag de plataforma `linux_x86_64` no soportado;
    se dejó la publicación del *sdist* y se documenta la opción de generar wheels manylinux.

- Dependencias y entorno de pruebas
  - Se detectó conflicto con `urllib3` durante pruebas en `venv_kivy` (paquete `pyrebase4` requiere `<2`).
  - Se forzó `urllib3==1.26.20` en el entorno de pruebas para resolver compatibilidades locales.
  - `pip check` indicó que `kivymd` espera un paquete `kivy` instalado; nota: `protonox-kivy` actúa como sustituto,
    pero algunos paquetes esperan la distribución oficial; se sugiere añadir `Provides-Dist: Kivy` en metadata
    o instalar un shim `kivy` que dependa de `protonox-kivy` si se requiere compatibilidad con terceros.

- Herramientas y helpers añadidos
  - `kivy-protonox-version/tools/check_kivy_deps.py` — helper para preparar `kivy-dependencies`.
  - `kivy-protonox-version/README_DEPENDENCIES.md` — documentación para bundling de dependencias nativas.

Archivos modificados/añadidos (resumen):
- Modificado: `setup.py` — generación `USE_SDL2`, SDL3 opt-in por defecto, fallback `kivy-dependencies`.
- Modificado: `setup.cfg` — removido `license_files`, añadido extra `sdl3`.
- Modificado: `kivy/_version.py` — bump a `3.0.0.dev6`.
- Añadido: `tools/check_kivy_deps.py`.
- Añadido: `README_DEPENDENCIES.md`.

Pasos realizados para publicar
1. Reconstrucción de artefactos con `python -m build`.
2. Limpieza de METADATA para eliminar `License-File` inválidos.
3. Publicación del *sdist* en PyPI.

Siguientes recomendaciones
- Generar ruedas manylinux con `cibuildwheel` para publicar binaries compatibles en PyPI.
- Considerar añadir `Provides-Dist: Kivy` en metadata para `protonox-kivy` si queremos que paquetes que dependen explícitamente
  de `kivy` reconozcan esta distribución como sustituto.

Contacto/Notas
- Repositorio: https://github.com/ProtonoxDEV/Protonox-Kivy-Multiplatform-Framework
- Paquete en PyPI: https://pypi.org/project/protonox-kivy/3.0.0.dev6/
