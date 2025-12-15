# Protonox Studio: Web2Kivy Integration Requirements

Este documento consolida los requisitos funcionales y no funcionales para integrar exportaciones Web→Kivy en Protonox Studio. El objetivo es tomar cualquier sitio web (multi‑vista o SPA) y convertirlo en KV/UI model por pantalla, conectándolo a la app Kivy existente de forma segura, repetible y con hot‑reload.

## 0) Restricciones y principios (NO negociables)
- No tocar código del usuario (pantallas existentes, controladores, lógica) salvo petición explícita.
- Todo lo generado vive en carpetas controladas:
  - `.protonox/` (manifiestos, cachés, reportes, fingerprints, logs).
  - `protobots/protonox_export/` (KV exportado + `ui-model.json`).
- Si falta mapping o hay ambigüedad: fallback seguro (placeholder de pantalla + warning).
- Toda magia debe ser opt‑in vía flag/variable de entorno.
- Hot‑reload debe tolerar reemplazos completos de archivos y ofrecer rollback si falla.

## 1) Estándares de artefactos y nombres
### 1.1 Export artefacts
Por cada vista exportada se generan:
- `protobots/protonox_export/<slug>.kv`
- `protobots/protonox_export/<slug>_screen.py` (opcional / scaffold)
- `protobots/protonox_export/<slug>-ui-model.json`

El **slug** es la identidad primaria. Ejemplo: `articulos-articulos`.

### 1.2 Manifiesto canónico de integración
Crear `.protonox/web2kivy/mapping.yaml` (alias `protonox_studio.yaml`). Debe soportar:
- `screens`: mapping explícito `ScreenName ↔ slug KV ↔ ui-model ↔ ruta web`.
- `routes`: rutas detectadas o definidas.
- `viewports`: resoluciones (ej. `1280x720`, `mobile`).
- `assets`: metadata de CSS/JS (solo auditoría).

Ejemplo mínimo:
```yaml
version: 1
project:
  app_root: protobots
  export_dir: protobots/protonox_export
screens:
  ArticulosScreen:
    kivy_name: articulos
    kv: articulos-articulos.kv
    ui_model: articulos-ui-model.json
    web:
      route: /articulos
      entrypoint: website/views/articulos.html
navigation:
  default: home
  links:
    - from: home
      to: articulos
      when: route:/articulos
```

## 2) Integración con ScreenManager real (protobots)
### 2.1 Problema actual
El export genera `PortedWebApp()` con su ScreenManager aislado (p.ej. `articulos-articulos_screen.py`). No sirve para la app real; hay que conectarlo al `ScreenManager` existente.

### 2.2 Screen Injection Layer
Crear módulo `protobots/protonox_studio_integration/` con:
- `__init__.py`
- `mapping_loader.py`
- `kv_loader.py`
- `screen_registry.py`
- `navigation_sync.py`
- `hot_reload_hooks.py` (si hot‑reload activo)

Comportamiento:
- Leer `.protonox/web2kivy/mapping.yaml`.
- Para cada Screen real (existente o wrapper) cargar el KV exportado (Builder).
- Asegurar que el `name` del `Screen` coincide con `kivy_name`.
- Si no existe la Screen en la app: crear wrapper mínima que monte el layout exportado, sin lógica de negocio.

### 2.3 Regla clave de KV exportado
El KV exportado usa reglas `<ArticulosScreen@Screen>`, con riesgos de:
- ids repetidos entre pantallas.
- colisiones con clases reales.
- ids como strings con comillas.
- `pos_hint`/`size_hint` absurdos por conversión.

Requisito: sanitizer previo a integrar:
- Normalizar ids (sin comillas, snake_case).
- Namespaces por pantalla (prefijo `articulos__meta_1`, opcional via flag).
- Bloquear colisiones `<X@Screen>`: renombrar a `<PX_ArticulosScreen@Screen>` si hay conflicto.
- Reportar anti‑patterns (no corregir a ciegas) y generar `layout_report.json`.

Salida de reportes: `.protonox/web2kivy/reports/<slug>.layout_report.json`.

## 3) Navegación Web ↔ Kivy
### 3.1 Inferencia de navegación (no destructiva)
- Del `ui-model.json` detectar anchors (`<a href>`) y botones con intención (`/articulos`, `/login`).
- Construir grafo tentativo `routes_graph.json`.
- Nunca aplicar sin aprobación: usarlo en CLI interactiva para confirmar.

### 3.2 Sync modes
- **Mode A (mínimo)**: mapping manual, sin tocar navegación.
- **Mode B (asistido)**: sugiere navegación desde web y pide confirmación.
- **Mode C (generativo)**: puede crear scaffolding de ScreenManager solo si no existe.

## 4) Hot reload “para IA” (cambios masivos KV)
- El hot‑reload debe ser transaccional y por pantalla.

### 4.1 Recarga por pantalla
- File watcher vigila `protobots/protonox_export/**/*.kv`.
- Al cambiar `articulos-articulos.kv`:
  - Compilar en sandbox (`Builder`). Si falla → rollback.
  - Si pasa → reemplazar solo el contenido de esa Screen.
  - Opcional: preservar estado si la Screen implementa contrato opt‑in.

### 4.2 Rollback real
- Guardar snapshot previo en `.protonox/web2kivy/rollback/<slug>/<timestamp>.kv`.
- Si el nuevo KV rompe: restaurar último estable y loggear `[HOTRELOAD][ROLLBACK] ...`.

## 5) CLI interactivo para mapping y diagnóstico
### 5.1 Comando principal
- `protonox studio doctor`: detecta entorno (Win11 + WSL, ADB, rutas, buildozer), muestra features activas por flags.

### 5.2 Mapping game
- `protonox web2kivy map`: lista Screens detectadas y slugs exportados, sugiere match por similitud, el dev confirma estilo wizard y guarda `mapping.yaml`.

### 5.3 Navigation game
- `protonox web2kivy nav-sync`: muestra grafo tentativo (web routes → kivy screens), permite aceptar/rechazar edges, genera `navigation.yaml` o sección `navigation` en mapping.

### 5.4 Validate / diff
- `protonox web2kivy validate --screen articulos`: render snapshot (PNG) + JSON tree, genera fingerprint + simetría heurística, deja todo en `.protonox/web2kivy/exports/`.

## 6) Consola de dev coherente (sin dañar logs Kivy)
### 6.1 Prefijos de logs
- Añadir prefijos cuando el output proviene de Protonox/Studio: `[PROTONOX]`, `[STUDIO]`, `[WEB2KIVY]`, `[HOTRELOAD]`, `[ANDROID]`, `[KV]`.
- No reemplazar el Logger de Kivy; solo wrapper opt‑in.

### 6.2 Help overlay en CLI
- `protonox help`: imprime features disponibles según flags y ejemplos rápidos (2‑3 líneas por feature). Modo interactivo: “¿Quieres configurar mapping ahora? (y/n)”.

## 7) Android bridge server (idea DEV)
### 7.1 Qué debe hacer (dev only)
- Correr en desktop (WSL o Windows host).
- Exponer comandos: instalar APK, iniciar actividad, logcat streaming filtrado, screenshots, pull/push de artefactos `.protonox/`, canal websocket/http sencillo para eventos (ej. crash → snapshot al host).

### 7.2 Qué NO debe hacer
- Nunca tocar credenciales del usuario.
- Nunca modificar código del proyecto remoto.
- Nunca abrir puertos en producción.

## 8) Wireless debugging y Android 15 (API 35)
### Requerimiento mínimo
- `protonox android wifi-connect`: detecta WSL, usa `adb.exe` del host si es necesario, guía pairing (Android 11+), guarda alias en `.protonox/android/devices.json`.
- `protonox android audit --target 35`: checklist de permisos runtime (Bluetooth, media, etc.), sanity de `targetSdkVersion 35`, reporte en `.protonox/android/audit_api35.json`.

## Checklist final para Codex
Entregables (en orden):
1. `docs/PROTONOX_STUDIO_WEB2KIVY_INTEGRATION.md` (este documento).
2. `.protonox/web2kivy/mapping.yaml` + generador CLI `protonox web2kivy map`.
3. `protobots/protonox_studio_integration/` con `mapping_loader`, `kv_loader`, `screen_registry`.
4. Sanitizer/validator de KV export (reporte JSON).
5. Hot‑reload por pantalla + rollback (adaptar watcher existente si aplica).
6. Navigation inference + CLI de confirmación.
7. Prefijos de logs + `protonox help` interactivo.
8. Android WiFi debugging commands + audit API35.
9. (Opcional) Bridge server DEV (WSL‑aware).

## Prevención de escenarios obvios
- Colisión de IDs: namespacing o reporte si detecta ids repetidas entre pantallas.
- Colisión `@Screen`: no asumir `<X@Screen>` seguro; renombrar si hay clase real.
- `Builder.load_file` duplicado: cache por slug (evitar recarga múltiple del mismo KV).
- Pantalla en blanco: si el KV export no define root visible, mostrar placeholder + warning.
- Ruta web ≠ screen: no inferir navegación sin aprobación humana (CLI).
- Paths WSL: normalizar `/mnt/c/...` ↔ `C:\...` en todo el pipeline.
- Hot‑reload rompe app: siempre transactional con rollback.
