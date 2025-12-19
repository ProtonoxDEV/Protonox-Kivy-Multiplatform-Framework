# Tests del Framework Protonox Kivy

Este directorio contiene las pruebas unitarias y de integración para el Framework Protonox Kivy Multiplatform.

## Estructura de Tests

### `test_kivy_compatibility.py`
Tests de retrocompatibilidad con Kivy 2.3.1:

- ✅ Verificación de compatibilidad como reemplazo directo de `kivy`
- ✅ Mensajes informativos sobre modificaciones Protonox disponibles
- ✅ Funcionamiento de ScissorPush/ScissorPop (crítico para retrocompatibilidad)
- ✅ Extensiones Protonox disponibles opcionalmente
- ✅ Compatibilidad con código legacy de Kivy 2.3.1
- ✅ Integración con KivyMD (ToggleButtonBehavior.state)
- ✅ Wireless debug disponible
- ✅ No breaking changes con imports comunes

### `test_app_windows.py`
Tests para las ventanas de aplicaciones (requiere entorno gráfico):

- 🟡 Tests de creación de layouts KivyMD y Kivy
- 🟡 Verificación de elementos UI básicos (labels, buttons)
- 🟡 Tests de interacciones (button press events)
- 🟡 Tests de integración entre diferentes tipos de aplicaciones

**Nota:** Los tests de `test_app_windows.py` requieren un entorno gráfico completo y pueden fallar en entornos headless como CI/CD.

## Cómo Ejecutar los Tests

### Opción 1: Script Automático (Recomendado)
```bash
python run_tests.py
```

### Opción 2: Ejecutar Tests Individuales
```bash
# Tests de estructura (siempre pasan)
python -m unittest tests.test_framework_structure -v

# Tests de compatibilidad con Kivy 2.3.1 (siempre pasan)
python -m unittest tests.test_kivy_compatibility -v

# Tests de ventanas (requieren display)
python -m unittest tests.test_app_windows -v
```

### Opción 3: Ejecutar Tests Específicos con Script
```bash
# Solo test de estructura
python run_tests.py -t framework

# Solo test de compatibilidad
python run_tests.py -t compatibility
```

## Requisitos para Tests

### Tests de Estructura
- ✅ Python 3.8+
- ✅ Sin dependencias adicionales

### Tests de Ventanas
- ✅ Python 3.8+
- ✅ Kivy instalado
- ✅ KivyMD instalado
- ✅ Entorno gráfico (X11, Wayland, o similar)
- ✅ Variables de entorno configuradas para headless si es necesario

## Configuración para CI/CD

Para ejecutar en entornos sin display (como GitHub Actions, Docker, etc.):

```bash
export KIVY_HEADLESS=1
export KIVY_NO_ARGS=1
export DISPLAY=
```

Sin embargo, los tests de ventanas probablemente fallarán en entornos headless. Se recomienda ejecutar solo los tests de estructura en CI/CD:

```bash
python -m unittest tests.test_framework_structure -v
```

## Cobertura de Tests

### ✅ Completamente Cubierto
- Estructura del proyecto
- Integridad de archivos
- Sintaxis de aplicaciones de ejemplo
- **Retrocompatibilidad con Kivy 2.3.1**
- **Reemplazo directo de kivy sin breaking changes**
- **Extensiones Protonox opcionales**
- Configuración de dependencias

### 🟡 Parcialmente Cubierto
- Funcionalidad de UI (solo en entornos con display)
- Interacciones de usuario
- Integración con Kivy/KivyMD

### ❌ No Cubierto
- Tests de rendimiento
- Tests de integración con dispositivos móviles
- Tests de compilación cruzada
- Tests de deployment

## Agregar Nuevos Tests

1. Crear un nuevo archivo `test_*.py` en este directorio
2. Seguir la convención de nombres de unittest
3. Agregar documentación clara en docstrings
4. Ejecutar `python run_tests.py` para verificar que pasan

## Reporte de Problemas

Si encuentras fallos en los tests:

1. Verificar que todas las dependencias están instaladas
2. Comprobar que el entorno gráfico está disponible (para tests de UI)
3. Revisar los logs de error para detalles específicos
4. Abrir un issue en el repositorio con la información del fallo