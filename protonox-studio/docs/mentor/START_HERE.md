# Protonox Mentor · Onboarding rápido

Bienvenido/a. Este tutorial está pensado para usarse dentro de VS Code con cualquier chatbot (Copilot Chat, Continue, Cursor, Codeium, ChatGPT). Solo sigue estos pasos:

1) Copia el prompt base desde `prompts/mentor.system.md` y pégalo en tu chatbot del editor.
2) Ejecuta en terminal: `protonox mentor start`.
3) Responde a las micro-misiones en orden. Si ya sabes algo, puedes saltarlo.

## Ruta sugerida (30–60 min)
- Lección 01: Run first app — lanzar demo mínima y verificar entorno.
- Lección 02: Understand structure — carpetas, `kv`, `screens`, assets.
- Lección 03: Create new screen — alta en router/ScreenManager.
- Lección 04: Assets pipeline — agregar y referenciar assets.
- Lección 05: Hot reload — ciclo seguro de recarga.
- Lección 06: Navigation/router — rutas y bindings.
- Lección 07: Buildozer first APK — empaquetado inicial.
- Lección 08: Debug common errors — patrones de fallo y fixes.

Las lecciones viven en `docs/mentor/LESSONS/`. Cada una trae meta, pasos, ejercicio y checklist.

## Misiones rápidas
Las misiones están descritas en `prompts/mentor.tasks.md`. El chatbot las usa para darte instrucciones y checklist. Ejemplo: crear pantalla `Settings`, registrar en router, y validar con los scripts de `scripts/mentor`.

## Salvavidas
- Si algo falla, comparte al chatbot: comando usado, log de error, sistema operativo, versión de Python/Kivy.
- Atajos: usa `--skip` o `PROTONOX_NO_WELCOME=1` para saltar el saludo inicial.

¡Listo! Corre `protonox mentor start` para abrir la guía y pegar el prompt en tu chat.
