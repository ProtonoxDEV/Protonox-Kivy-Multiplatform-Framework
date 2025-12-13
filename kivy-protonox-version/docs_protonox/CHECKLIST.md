# Protonox Extension Checklist (Kivy 2.3.1)

Este checklist resume los requisitos obligatorios y dónde vive cada entrega en
`kivy-protonox-version`. Todo es **opt-in**, no rompe compatibilidad y deja el
núcleo de Kivy 2.3.1 intacto.

## Identidad y compatibilidad
- [x] Núcleo Kivy 2.3.1 sin modificaciones directas (`kivy/`)
- [x] Extensiones aisladas bajo `kivy/protonox_ext` con prefijo Protonox
- [x] Versionado claro `2.3.1-protonox.x` (ver `docs_protonox/COMPATIBILITY.md`)
- [x] Documentación Protonox separada (`docs_protonox/`), sin tocar docs upstream
- [x] Capa de compatibilidad drop-in (`kivy/protonox_ext/compat/*`) para activar o desactivar flags sin tocar el core

## Web → Kivy (modelo intermedio y pipeline)
- [x] Modelo UI neutral serializable (`kivy/protonox_ext/kv_bridge/ir.py`)
- [x] Generador KV desde el IR (`kivy/protonox_ext/kv_bridge/compiler.py`)
- [x] Importador Kivy→IR para reutilizar pantallas existentes (`kivy/protonox_ext/kv_bridge/importer.py`)
- [x] Introspección de layout para poblar el IR con geometría opt-in (`kivy/protonox_ext/layout_engine/introspect.py`, `kivy/protonox_ext/telemetry.py`)

## Visual / PNG y análisis
- [x] Exportación de PNG y advertencias básicas (`kivy/protonox_ext/visual_state/png_reference.py`)
- [x] Señales de overflow/alineación vía telemetría opt-in (`kivy/protonox_ext/telemetry.py`)
- [x] Logs estructurados para IA sin mutar la app (`kivy/protonox_ext/hotreload_plus/hooks.py`)
- [x] Huella de layout (hash estructural) + simetría visual (`kivy/protonox_ext/layout_engine/fingerprint.py`)
- [x] Snapshot dual PNG + JSON + layout report (`kivy/protonox_ext/visual_state/snapshot.py`)
- [x] Congelado de UI para análisis estable (dev-only, `PROTONOX_UI_FREEZE`) (`kivy/protonox_ext/visual_state/freeze.py`)
- [x] Detección de anti-patrones y heurísticas multi-DPI (`kivy/protonox_ext/layout_engine/antipatterns.py`)
- [x] Perfilado de costo de layout por widget (opt-in, `PROTONOX_LAYOUT_PROFILER`) (`kivy/protonox_ext/layout_engine/performance.py`)
- [x] Score de salud de layout y observabilidad agregada (contexto + métricas +
      fingerprint) (`kivy/protonox_ext/layout_engine/health.py`,
      `kivy/protonox_ext/observability.py`)
- [x] Engine de salud + fingerprint + observabilidad exportable junto con doctor (opt-in)

## Hot Reload + contexto para IA
- [x] Hot reload por niveles con rollback seguro (`protonox-studio` y `kivy/protonox_ext/hotreload_plus`)
- [x] Captura de errores/warnings para bundles de diagnóstico (`protonox-studio/devtools`)

## Android y emojis
- [x] Bridge ADB opt-in para deploy/logcat rápido (`kivy/protonox_ext/android_bridge/adb.py`)
- [x] Modo `watch` para reinstalar opcionalmente y streamear logcat filtrado (`kivy/protonox_ext/android_bridge/adb.py`)
- [x] Fallback de emoji y descubrimiento de fuentes (`kivy/protonox_ext/ui/emoji.py`)
- [x] Doctor runtime GPU/GL/DPI (opt-in, `kivy/protonox_ext/diagnostics/runtime.py`)

## Docs y guías
- [x] Guía de no ruptura y roadmap (`docs/KIVY_231_NO_BREAK_GUIDE.md`, `docs/RELEASES.md`)
- [x] Extensiones descritas sin modificar documentación upstream (`docs_protonox/EXTENSIONS_OVERVIEW.md`)
- [x] Flujo Web→Kivy y comandos CLI documentados (`docs/WEB_TO_KIVY_PIPELINE.md`)
- [x] Compatibilidad y doctor documentados (`docs_protonox/COMPAT_LAYER.md`, `docs_protonox/RUNTIME_DIAGNOSTICS.md`)

## Reproducibilidad / contenedores (en progreso)
- [x] Dockerfile reproducible con Kivy 2.3.1 + extensiones (planificado)
- [x] Validaciones adicionales de entorno Android en contenedor (planificado)

## Pendientes futuros
- [x] Comparador visual más profundo (bounding-box diffs por widget)
- [x] Inspector overlay interactivo con export de parches KV
- [ ] Plantilla Docker “one-command run” con parity local
