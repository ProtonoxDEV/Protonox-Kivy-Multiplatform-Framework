# Protonox Studio: Plan de Integración Web→Kivy (Codex)

Este documento define el plan completo para convertir cualquier sitio en `website/` en un conjunto de pantallas Kivy conectadas
al proyecto real `protobots/`, sin modificar código del usuario fuera de las áreas controladas. Se basa en UI‑IR como fuente de
verdad, exporta KV/Python por pantalla, mapea contra el `ScreenManager` existente, habilita hot‑reload por pantalla o por lote,
valida visual/estructuralmente y expone un fast loop Android (USB/WiFi) desde Win11+WSL.

## 0) Objetivo y principios (no negociable)
- **No tocar código del usuario** salvo petición explícita. Solo escribir en:
  - `protobots/protonox_export/**`
  - `protobots/protonox_studio/**` (nuevo módulo de integración)
  - cambios mínimos en `main.py`/router para hooks feature‑flag.
- **Artefactos controlados**: `.protonox/` (manifiestos, caches, reportes, fingerprints, logs) y `protobots/protonox_export/` (KV/UI‑model exportado).
- **UI‑IR como fuente de verdad**: `*-ui-model.json` gobierna la integración y validación.
- **Fallback seguro** si falta mapping o hay ambigüedad (placeholder + warning).
- **Opt‑in para magia** vía flags/env. Nada destructivo por defecto.
- **Hot‑reload transaccional** con rollback si falla (por pantalla o lote).
- **No reescribir ScreenManager real** sin consentimiento explícito (modo “apply”).

## 1) Carpetas y artefactos
### 1.1 Export
Ubicación fija: `protobots/protonox_export/`
- `*-<route>.kv`
- `*-<route>_screen.py` (scaffold opcional; nunca reemplaza controllers reales)
- `*-ui-model.json` (UI‑IR serializado)

### 1.2 Configuración
Ubicación: `protobots/protonox_export/protonox_studio.yaml` (o `.json`). Contiene:
- mapping `routes ↔ screens`
- viewport hints
- reglas de naming

### 1.3 Estado/outputs
Ubicación: `.protonox/protonox-exports/`
- snapshots PNG
- diffs
- reportes
- dumps de Diagnostic Bus

### 1.4 Reglas de “no tocar”
Nada fuera de las rutas anteriores. Los hooks en `main.py`/router deben ser minimalistas y desactivables.

## 2) Núcleo Web→Kivy: UI‑IR y export limpio
### 2.1 Normalización del UI model (`ui_ir/normalize.py`)
- Naming estable: identificador web `html-1` → `html_1` seguro en Kivy.
- Garantizar `role`, `bounds`, `children`, `meta` en cada nodo.
- Generar `layout_fingerprint` (hash estructural) y `route_signature` (hash de assets + entrypoint).
- Detectar breakpoints responsivos (opcional) y guardarlos en el IR.

### 2.2 Export KV limpio (`exporters/kivy_kv.py`)
- Evitar `pos_hint` absurdos (p.ej., `y > 1.0`).
- Si `bounds` excede viewport → usar `ScrollView + BoxLayout` vertical o `size_hint_y=None` con `height` calculado.
- Preferir `Label(text=...)` solo si hay texto real.
- Insertar `# PROTONOX_PLACEHOLDER` donde falte contenido.
- Excluir nodos web invisibles (`head/meta/link`) del árbol KV, pasándolos a metadata.
- KV resultante debe parecerse a la UI real, no al DOM literal.

## 3) Integración con la app real: ScreenManager + navegación
### 3.1 Mapping explícito (`protonox_studio/mapping.py`)
- Fuente principal: `protonox_studio.yaml`.
- Si falta mapping: modo interactivo (`protonox map`) para generarlo.
- Formato mínimo:
  ```yaml
  screens:
    ArticulosScreen:
      route: /articulos
      kv: protobots/protonox_export/articulos-articulos.kv
      ui_model: protobots/protonox_export/articulos-ui-model.json
      viewport: { width: 360, height: 800 }
      strategy: replace_content  # o embed/exported_screen
  routes:
    /articulos: ArticulosScreen
  ```

### 3.2 Estrategias de integración (3 modos)
- **replace_content (default, recomendado):** la pantalla real existe; se monta el KV exportado dentro de `ids.export_root` sin tocar lógica ni navegación.
- **embed/exported_screen:** si no hay pantalla real, crear placeholder en carpeta “generated” y montarlo en la app para demos/prototipos.
- **apply_router (peligroso):** deduce navegación y propone cambios al ScreenManager real. Solo genera PR/patch; no aplica automáticamente.

### 3.3 Deducción de navegación desde web (`web_nav/extract.py`)
- Detectar links internos, rutas, menús, botones.
- Construir `nav_graph.json` con orden sugerido de screens.
- Solo propone; nunca aplica sin confirmación humana.

## 4) HotReload moderno: batch + rollback
### 4.1 Recarga por lote (`hotreload/batch_reload.py`)
- Observa cambios en `protobots/protonox_export/**/*.kv` y `protobots/protonox_export/**/*_screen.py`.
- Agrupa por pantalla usando el mapping.
- Recarga atómica: snapshot de estado (si la pantalla implementa contrato), compila en sandbox, aplica; si falla → rollback y overlay de error.

### 4.2 Preservación de estado (opt‑in)
Contrato `LiveReloadStateCapable`:
- `export_state() -> dict`
- `import_state(state: dict) -> None`
- `on_reload_begin/on_reload_end`

### 4.3 Golpe grande
- Si cambian >N archivos en <T segundos → activar “bulk mode”.
- Esperar quiet period (ej., 600ms) y recargar en orden: KV templates → KV screens → controllers Python (si aplica).
- Reportar resumen OK/fail.

### 4.4 Rollback real
- Snapshots en `.protonox/web2kivy/rollback/<slug>/<timestamp>.kv`.
- Log `[HOTRELOAD][ROLLBACK] ...` en caso de revert.

## 5) CLI interactivo unificado (sin docs web)
Comando `protonox` (entrypoint) con subcomandos:

- `protonox doctor`: detecta WSL/Windows, versión kivy-protonox, buildozer/adb, permisos Android 13–15, rutas, fonts/emoji, OpenGL.
- `protonox web2kivy --entry website/views/articulos.html`: genera UI‑model + KV export + report.
- `protonox map`: juego interactivo de emparejar screens reales vs exports, guarda mapping y ejecuta smoke test (Builder). Similaridad por route/name/text.
- `protonox run --app protobots`: arranca la app con flags y hot‑reload.
- `protonox android wifi-connect`: conecta ADB WiFi y prueba logcat (WSL‑aware).
- `protonox validate --baseline web.png --candidate kivy.png`: validación visual.

### Consola formateada
- Prefijos estandarizados: `[PXKIVY]`, `[PXSTUDIO]`, `[HOTRELOAD]`, `[KV]`, `[ANDROID]`, `[UIIR]`, `[VALIDATE]`.
- Usar `rich`/`textual` opcional para CLI; no ocultar logs de Kivy. Duplicar a stdout normal y JSON (DiagnosticBus) opcional.

## 6) Android 15 + periféricos: Modern Device Layer
### 6.1 Objetivo
Capa opt‑in (Android‑first) para cámara (CameraX), mic (AudioRecord/MediaRecorder), GPS (Fused Location Provider), archivos (SAF), contactos, Bluetooth (BLE + permisos nuevos), llamadas/intents.

### 6.2 Principios
- Bridge nativo (Java/Kotlin) + Pyjnius en `protobots/app/core/java/...`.
- API Python estable, ej.:
  - `protonox.device.camera.open(front=True)`
  - `protonox.device.permissions.request([...])`
  - `protonox.device.bluetooth.scan()`

### 6.3 ADB Bridge + server opcional
- Servidor dev en desktop (WSL/Windows); cliente Android se conecta (websocket/http).
- Permite enviar eventos, pedir snapshots, stream de logs, ejecutar “actions” (cámara, permisos) en modo dev.
- Siempre dev‑only y behind flags.

## 7) Android WiFi + auditoría API35
- `protonox android wifi-connect`: detecta WSL, usa `adb.exe` del host si hace falta, guía pairing Android 11+, guarda alias en `.protonox/android/devices.json`.
- `protonox android audit --target 35`: checklist de permisos runtime (Bluetooth, media, etc.), sanity de `targetSdkVersion 35`, reporte en `.protonox/android/audit_api35.json`.

## 8) Checklist ejecutable para Codex (copiar/pegar como tareas)
1. Crear módulo `protobots/protonox_studio/` con: `mapping.py`, `loader.py`, `integrations.py`, `doctor.py`, `cli.py`.
2. Crear/definir `protonox_studio.yaml` (schema + ejemplo) y soporte de lectura/escritura.
3. Implementar loader “safe”: `replace_content` por defecto, placeholder si falta mapping.
4. Implementar `protonox map` interactivo (juego) y guardar manifest.
5. Implementar `hotreload/batch_reload.py`: agrupar cambios, recargar por pantalla, rollback si falla.
6. Normalizar export KV: remover nodos web invisibles, reparar `pos_hint` > 1, usar `ScrollView` cuando `height > viewport`.
7. Integrar `protonox doctor`: bridge de rutas WSL, localización de `adb` (Windows/WSL), checks Android 13–15, fonts/emoji.
8. Implementar prefijos y consola (`[PXKIVY]`, `[PXSTUDIO]`, etc.) con `rich` opcional sin perder logs.
9. Implementar `android wifi-connect` / logs / restart y validar en Win11+WSL.
10. Implementar extracción `nav_graph` web y sugerencias de mapping (no aplicar).
11. (Opcional) Dev Bridge Server (desktop↔android) dev‑only.
12. Documentar en `docs/WEB_TO_KIVY_PIPELINE.md` y `docs/CLI.md` con ejemplos reales.

## 9) Operativa incremental y criterios de aceptación
- **Fase 1 (IR + export limpio):** UI‑IR normalizado, export KV saneado y reportes de layout en `.protonox/web2kivy/reports/`. Criterio: el KV compila sin colisiones de `@Screen` ni `ids`, y elimina nodos invisibles.
- **Fase 2 (mapping + integración segura):** `protonox map` genera `protonox_studio.yaml`; `replace_content` injerta KV en pantallas reales sin tocar lógica. Criterio: carga en runtime del `ScreenManager` real con placeholder si falta mapping.
- **Fase 3 (hot‑reload transaccional):** watcher por pantalla/batch con rollback. Criterio: modificación deliberada de un KV provoca rollback limpio y log `[HOTRELOAD][ROLLBACK]` ante fallo de compilación.
- **Fase 4 (navegación asistida):** `web_nav/extract.py` produce `nav_graph.json` y el CLI pide confirmación antes de sugerir rutas. Criterio: ningún cambio se aplica sin confirmación explícita.
- **Fase 5 (Android fast loop):** `protonox android wifi-connect` y `android audit` operativos en Win11+WSL con almacenamiento de devices en `.protonox/android/`. Criterio: logcat accesible y pairing registrado.
- **Fase 6 (device layer opt‑in):** API Python estable que envuelve bridge nativo. Criterio: llamadas básicas (`camera.open`, `bluetooth.scan`) funcionan en modo dev cuando el módulo nativo está presente.

## 10) Ejemplo aplicado al caso actual (`articulos-articulos.kv`)
- Artefactos presentes: `*.kv`, `*_screen.py`, `*-ui-model.json` viven como mini‑apps aisladas.
- Próximos pasos inmediatos:
  - Generar `protonox_studio.yaml` con mapping `ArticulosScreen ↔ articulos-articulos.kv` usando `protonox map`.
  - Activar loader `replace_content` para montar el layout exportado dentro de la pantalla real (sin tocar controladores).
  - Encender watcher `hotreload/batch_reload.py` apuntando a `protobots/protonox_export/` para recarga por pantalla con rollback.
  - Ejecutar normalizador de KV para quitar `pos_hint` inválidos y forzar `ScrollView` donde el contenido desborda viewport.
  - Generar `layout_report.json` y `nav_graph.json` como evidencia y guías para el CLI de navegación.
- Resultado esperado: Protonox Studio deja de ser “exportador” aislado y se convierte en un motor de porting repetible: cualquier vista web pasa a ser pantalla Kivy integrada, con navegación confirmada, hot‑reload seguro y ciclo Android listo para pruebas.
