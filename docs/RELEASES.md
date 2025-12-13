# RELEASES — Protonox Studio + Kivy 2.3.1 Protonox Fork

Usa este archivo para documentar cada incremento `2.3.1-protonox.<patch>`.
Cada entrada debe ser breve, auditable y anclada a pruebas reales.

### 2.3.1-protonox.0 — 2024-06-XX
- Alcance: Motor de Hot Reload para Kivy 2.3.1 con grafo de dependencias, preservación de estado (`ReloadState`) y rollback seguro.
- Riesgo: Medio; nivel máximo controlable con `PROTONOX_HOT_RELOAD_MAX` (dev-only, fallback a rebuild si falla el plan).
- Compatibilidad: No se recargan internals de Kivy/KivyMD/Protonox; interfaces opt-in (`LiveReloadStateCapable`).
- Pruebas: `python -m compileall protonox-studio/src` (ver chunk de compilación reciente).
- Rollback: establecer `PROTONOX_HOT_RELOAD_MAX=0` o deshabilitar el watcher para usar rebuild completo.

## Formato sugerido

### 2.3.1-protonox.X — YYYY-MM-DD
- Alcance: breve descripción del objetivo del patch.
- Riesgo: bajo/medio/alto + si requiere feature flag.
- Compatibilidad: cómo se mantiene la API estable.
- Pruebas: comandos ejecutados (desktop, Android, lint) + ubicación de logs.
- Rollback: cómo desactivar o revertir (flag o commit).

Añade nuevas entradas encima de este bloque para mantener el orden cronológico inverso.
