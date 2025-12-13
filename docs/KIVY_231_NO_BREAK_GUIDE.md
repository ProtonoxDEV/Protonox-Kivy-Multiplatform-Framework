# Kivy 2.3.1 — Guía de No-Ruptura (Protonox Kivy Fork)

Objetivo:
Modernizar y acelerar el framework (DX, empaquetado, TextInput/emojis, tooling)
SIN romper compatibilidad con apps existentes basadas en Kivy 2.3.1.

## Principios (reglas de oro)

1) Compatibilidad primero
- No se cambian APIs públicas existentes sin capa de compatibilidad.
- No se rompen nombres, rutas, clases o firmas públicas.
- Cualquier cambio riesgoso debe ir detrás de feature flags.

2) Cambios incrementales y medibles
- Cada PR debe incluir:
  - qué mejora
  - qué podría romper
  - cómo se probó
  - cómo revertir (o flag para apagar)

3) Paridad por plataforma
- Nada que funcione solo en desktop.
- Si aplica a Android, se prueba en Android (mínimo build + smoke test).

4) No tocar SDK/NDK directamente
- No se “arregla” Android alterando NDK/SDK.
- Se arregla el pipeline (build scripts, recipes, buildozer configs) y/o Kivy.

## Qué NO se toca (zona roja)

- API pública estable de Kivy (Widgets, Properties, Events) sin compat layer.
- Semántica de:
  - Clock scheduling
  - input/touch
  - Window provider
  - kivy.lang Builder
- Cambios masivos en kv parser/lexer sin pruebas exhaustivas.
- Cambios en naming/paths de módulos públicos.

## Qué SÍ se puede mejorar con riesgo bajo (zona verde)

A) TextInput / Emojis / Fonts
- Mejoras de rendering y fallback de fuentes
- Mecanismos de selección de fuentes por plataforma
- Sanitización y normalización segura de unicode
- Fallback automático a NotoColorEmoji / compat fonts (sin imponer por defecto)

B) Tooling / DX
- Scripts de build reproducibles
- Logs más claros y “actionable”
- Mejoras en warnings/errores de kv
- Hot reload: solo si es opt-in (flag)

C) Packaging / Build pipeline
- Caches (pip/wheels/gradle) + builds deterministas
- Templates/blueprints para buildozer.spec y pyinstaller.spec
- Validadores de entorno y checks previos (preflight)

## Feature flags (obligatorio para cambios que puedan romper)

Todos los cambios “nuevos” con impacto en runtime deben poder apagarse por:
- variable de entorno, o
- setting central (p.ej. `KIVY_PROTONOX_FLAGS.json`), o
- argumento de arranque.

Ejemplo:
- PROTONOX_TEXTINPUT_EMOJI=1
- PROTONOX_KV_STRICT=0
- PROTONOX_BUILD_CACHE=1
- PROTONOX_LAYOUT_TELEMETRY=1 (exporta bounds/overflow y PNG bajo `kivy.protonox_ext.telemetry`, siempre opt-in)

## Estrategia de versionado

- Base: Kivy upstream tag v2.3.1
- Fork: `2.3.1-protonox.<patch>` vendorizado en `kivy-protonox-version/` (instalable con `pip install -e ./kivy-protonox-version`)
  Ej: `2.3.1-protonox.0`, `2.3.1-protonox.1`

Regla:
- patch++ solo si:
  - compat mantenida
  - tests pasan
  - changelog actualizado

## Plan mínimo de pruebas (smoke + regressions)

1) Desktop (Windows/Linux)
- App mínima: Button, TextInput, ScrollView, ScreenManager
- Cargar 10 pantallas kv (Builder.load_file)
- Input de emoji + copy/paste
- Render de texto largo
- Hot reload OFF por defecto

2) Android
- Build APK en limpio
- Ejecuta app mínima + 1 pantalla con TextInput
- Input y render de emojis (al menos 3)
- Logs sin exceptions

## Checklist PR (no se mergea sin esto)

- [ ] No rompe API pública (o hay compat layer)
- [ ] Changelog actualizado
- [ ] Feature flag si es riesgoso
- [ ] Smoke tests desktop OK
- [ ] Si toca Android: build APK OK
- [ ] Plan de rollback (revert/flag)
