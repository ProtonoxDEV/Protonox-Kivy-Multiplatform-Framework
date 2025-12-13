# Kivy Live Reload Engine (Protonox Studio)

Esta síntesis documenta el motor de Hot Reload para Kivy 2.3.1 manteniendo
compatibilidad total. El objetivo es recargar Python y KV sin reiniciar el
proceso, preservando estado crítico y con rollback seguro.

## Contratos de estado (Level 3)
- `ReloadState`: snapshot serializable con `navigation`, `user` y `runtime`.
- `LiveReloadStateCapable`: interfaz opt-in (`extract_state` / `apply_state`).
- Flujo: cambio de archivo → `extract_state()` → intento de reload →
  éxito: `apply_state(state)` · error: rollback + overlay de error.

## Grafo de módulos y recarga Python
- `ModuleGraphBuilder` inspecciona `sys.modules` y referencias `__module__`
  para armar un grafo de dependencias.
- Orden de recarga: hojas → raíz (toposort) evitando stdlib, kivy/kivymd y
  protonox internals.
- Solo se recargan módulos del usuario o marcados como reloadables.

## Rollback seguro
- Snapshot previo: `sys.modules`, `Factory.classes`, `Builder.rulectx`, y
  estado opcional (`ReloadState`).
- Ante error: se restaura el snapshot completo y se mantiene la app viva.

## Niveles de reload (0–3)
- Level 0: rebuild completo (fallback).
- Level 1: recarga KV + rebuild UI.
- Level 2: recarga módulos Python con grafo seguro.
- Level 3: Python + KV + reinyección de estado (`LiveReloadStateCapable`).
- Escalado seguro: empieza en 0 y sube solo si el archivo y flags lo permiten.

## HotReloadAppBase (KivyMD + overlay rojo)
- Usa `HotReloadEngine` internamente pero mantiene el flujo heredado de
  recarga parcial (`FILE_TO_SCREEN`) si la raíz de la app implementa
  `partial_reload_screen(name)`.
- Watchdog + hash MD5 para ignorar eventos duplicados; patrones ignorados con
  `AUTORELOADER_IGNORE_PATTERNS`.
- Overlay rojo con traceback en modo DEBUG/RAISE_ERROR para diagnosticar
  crasheos sin matar el proceso.
- Fallback automático a rebuild si el plan de reload falla o el archivo no es
  seguro; nunca recarga internals Kivy/KivyMD/Protonox.
- Gancho de estado: si la app implementa `LiveReloadStateCapable`, el Level 3
  reinserta el estado tras el reload; si no, se hace rebuild limpio.

## Flags y ámbito
- `PROTONOX_HOT_RELOAD_MAX`: limita el nivel máximo (por defecto 3).
- Dev-only: no se ejecuta en prod y no toca SDK/NDK.

## Reglas de oro
- No romper compatibilidad Kivy 2.3.1.
- No recargar internals de Kivy/KivyMD/Protonox.
- Siempre posible volver atrás en caso de falla.
