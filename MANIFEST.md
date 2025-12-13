# MANIFEST — Protonox Studio + Kivy 2.3.1 Protonox Fork

## Qué es esto

Este repositorio contiene:
1) Un fork estable de Kivy v2.3.1 con mejoras incrementales y compatibles.
2) Protonox Studio: un toolkit de automatización (DX + build + IA-ready) orientado a:
   - acelerar empaquetado multiplataforma
   - mejorar modernización de UI (sin romper apps)
   - permitir pipelines industrializables (APK/EXE/MSI)

## Filosofía

- “No romper”: compatibilidad con apps existentes es prioridad.
- “Industrial”: builds reproducibles, cacheados y automatizables.
- “IA-friendly”: todo debe ser inspeccionable/modificable por agentes (Codex).

## Alcance (qué sí hacemos)

Kivy Fork:
- Fixes y modernizaciones seguras
- Mejoras de TextInput/emojis/fonts (opt-in si es riesgoso)
- Mejoras del pipeline de build (scripts, preflight, cachés)
- Mejoras de logging y DX

Protonox Studio:
- Comandos/scrips para:
  - preparar entorno
  - validar dependencias
  - construir artefactos
  - empaquetar (Android/desktop)
  - registrar outputs (logs/reportes)
- Integración con hot reload (sin imponer, siempre opt-in)
- Plantillas de proyectos y “blueprints” de empaquetado

## Fuera de alcance (qué NO hacemos)

- No alteramos SDK/NDK directamente.
- No “reinventamos” KivyMD dentro del fork.
- No hacemos cambios masivos sin tests.
- No introducimos dependencias enormes sin razón (evitar sobreingeniería).

## Estructura recomendada del repo

/
├─ kivy_fork/                 # código del fork (o submodule si aplica)
├─ protonox_studio/           # toolkit principal (scripts, CLI, build tools)
├─ templates/                 # templates: buildozer.spec, pyinstaller.spec, etc.
├─ docs/
│  ├─ KIVY_231_NO_BREAK_GUIDE.md
│  ├─ BUILD_PIPELINE.md
│  ├─ EMOJI_TEXTINPUT.md
│  └─ RELEASES.md
├─ examples/
│  ├─ minimal_app/
│  └─ emoji_textinput_demo/
└─ tools/
   ├─ preflight.py
   ├─ build_android.py
   ├─ build_desktop.py
   └─ release.py

## Contrato de estabilidad

- Versionado: `2.3.1-protonox.<patch>`
- Cambios con riesgo: feature flag obligatorio
- PR sin pruebas: no se mergea
- Hot reload: desactivado por defecto

## Definición de éxito

- Build Android reproducible + cacheado
- Build desktop reproducible + cacheado
- TextInput con mejor soporte unicode/emojis (sin romper)
- Pipeline “one-command build” para artefactos
- Capacidad de IA para diagnosticar y corregir fallas de build con logs claros
