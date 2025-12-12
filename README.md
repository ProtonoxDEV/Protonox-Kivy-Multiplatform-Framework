# Protonox Kivy Multiplatform Framework (Protonox Studio + Kivy 2.3.1)

## Propósito
Modernizar y extender Kivy 2.3.1 sin romper compatibilidad con SDK/NDK ni toolchains externas, integrando Protonox Studio como capa de orquestación y diagnóstico asistido por IA. Enfoques clave:
- Automatización industrial del empaquetado (APK, EXE, MSI, etc.).
- Mejora estructural profunda de la relación `.py` ↔ `.kv` para que sea explícita, trazable y segura.
- Modernización del framework (TextInput con emojis Unicode, fuentes con fallback, limpieza de APIs obsoletas).
- Línea de ensamblaje reproducible: builds rápidos, deterministas, detectables y autocorregibles por IA.
- Separación estricta: no se tocan SDK/NDK/toolchains; se mejora framework + empaquetado + relación `.py/.kv`.

## Componentes en este repo
- `kivy-protonox-version/`: fork consciente de Kivy 2.3.1 para modernización y automatización de empaquetado.
- `protonox-studio/`: herramienta de orquestación y auditoría (hot reload, diagnóstico estructural, IA) reubicada fuera del website.

## Estado inicial
- Artefactos locales limpios (`.venv/` y `dist/` removidos). Usa tu entorno preferido antes de desarrollar.
- Plantillas systemd actualizadas para la nueva ruta del repo.

## Próximos pasos sugeridos
1) Inicializar git y apuntar a `https://github.com/ProtonoxDEV/Protonox-Kivy-Multiplatform-Framework.git`.
2) Trabajar ramas de feature para:
   - Resolver trazabilidad `.py ↔ .kv` (carga ordenada, errores claros, hot reload seguro).
   - Modernizar TextInput y limpiar APIs obsoletas sin romper compatibilidad.
   - Instrumentar pipelines de empaquetado reproducibles y observables.
3) Integrar Protonox Studio como capa de diagnóstico/IA sobre la app Kivy (hot reload, detección de bindings rotos, refactor asistido).
4) Mantener compatibilidad estricta con toolchains externas; solo mejorar framework, empaquetado y ergonomía IA.

## Uso rápido (Protonox Studio)
- `cd protonox-studio && pip install .`
- `protonox dev | audit | export` según necesidad.
- Plantillas systemd/cron en `protonox-studio/cli/systemd-user/` para automatizar auditorías diarias.

## Notas de higiene
- No comitear secretos (`.env` ya está ignorado).
- Ignorar entornos, caches y artefactos generados (ver `.gitignore`).
