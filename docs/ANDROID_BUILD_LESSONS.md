# Lecciones Aprendidas: Desarrollo Móvil con Protonox-Kivy

Esta documentación captura las lecciones aprendidas durante el debugging y desarrollo de apps Android con Protonox-Kivy v3.0.0.

## Problemas Resueltos

### 1. Arquitectura de Extensiones Incorrecta (x86_64 vs ARM64)
**Problema**: Las extensiones Cython (.so) se compilaban para x86_64 en lugar de ARM64, causando `ImportError: dlopen failed... is for EM_X86_64 instead of EM_AARCH64`.

**Causa**: 
- `build_ext --inplace` compilaba para la arquitectura del host
- Variables de entorno de cross-compilación no eran suficientes
- setuptools detectaba la plataforma del host

**Solución**:
- Cambiar de `build_ext --inplace` + `install` a solo `install` con `--plat-name=linux-aarch64`
- Configurar variables de entorno agresivas:
  ```python
  env['CC'] = f'{clang} -target aarch64-linux-android{ndk_api}'
  env['C_INCLUDE_PATH'] = f'{ndk_dir}/sysroot/usr/include'
  env['CPLUS_INCLUDE_PATH'] = f'{ndk_dir}/sysroot/usr/include'
  env['LIBRARY_PATH'] = f'{ndk_dir}/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/lib/aarch64-linux-android/{ndk_api}'
  env['_PYTHON_HOST_PLATFORM'] = 'linux-aarch64'
  ```

### 2. NDK y Android 16 Compatibility
**Problema**: Android 16 requiere soporte para 16KB page sizes.

**Solución**: Usar NDK r28+ en buildozer.spec:
```ini
android.ndk = 28
```

### 3. Dependencias de Host Incorrectas
**Problema**: setuptools y Cython no disponibles en hostpython durante build.

**Solución**: 
- Instalar manualmente en hostpython site-packages
- Configurar PYTHONPATH para incluir user site-packages y hostpython Lib

### 4. Variables de Entorno para Cross-Compilación
**Problema**: El compilador usaba headers del sistema host.

**Solución**: Configurar CPATH, C_INCLUDE_PATH, etc. para apuntar solo a NDK sysroot.

### 5. Buildozer Environment Issues
**Problema**: Buildozer usaba Python del sistema en lugar del venv.

**Solución**: 
- Activar venv antes de ejecutar buildozer
- Configurar `python.path = venv_buildozer/bin/python3` en buildozer.spec

## Configuración Recomendada

### buildozer.spec
```ini
[app]
# ...
android.ndk = 28
android.api = 36
android.minapi = 24

[buildozer]
python.path = venv_buildozer/bin/python3

# Para desarrollo local
requirements.source.protonox-kivy = ../kivy-protonox-version
```

### Recipe protonox-kivy/__init__.py
Ver las modificaciones en `get_recipe_env()` para cross-compilación completa.

## Comandos de Build
```bash
# Activar venv
source venv_buildozer/bin/activate

# Build completo
buildozer android debug

# Build limpio
buildozer android clean && buildozer android debug

# Deploy y run
buildozer android debug deploy run
```

## Debugging
- Usar `adb logcat -s python:D SDL:D` para logs de la app
- Verificar arquitectura de .so con `file lib/arm64-v8a/*.so`
- Para 16KB pages: `llvm-objdump -p lib/arm64-v8a/*.so | grep LOAD`

## Mejores Prácticas
1. Siempre usar NDK r28+ para Android 16+
2. Configurar requirements.source para desarrollo local
3. Activar venv antes de buildozer
4. Verificar arquitectura de extensiones después del build
5. Usar --plat-name en recipes personalizados