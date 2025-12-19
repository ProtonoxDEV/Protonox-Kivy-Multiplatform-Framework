# Protonox Studio

"Protonox Studio – El Motor de Diseño Inteligente en Tiempo Real" avanza a su segunda etapa: no solo documenta el plan, ahora
produce auditorías accionables (grilla 8px, contraste, safe areas, tokens y escala tipográfica) listas para alimentar el panel y
las futuras sobreposiciones.

Ubicación: ahora vive en `Protonox-Kivy-Multiplatform-Framework/protonox-studio/` (antes en `website/protonox-studio/`).

## Arquitectura
```
protonox-studio/
├── core/                # WebSocket + comando + estado global
├── intelligence/        # 8px, baseline grid, golden ratio, tokens, contraste
├── ui/                  # Panel 100% cliente, servido por el server
├── modules/             # Plug and play (resize, move, grid, AI nudge)
└── cli/                 # Comandos protonox dev/audit/export
```

### Mapa detallado
- **core**: `engine.py`, `injector.py`, `ai.py` (caché y orquestación de IA) y el servidor local de desarrollo.
- **intelligence**: `grid_engine.py`, `token_detector.py`, `spacing_analyzer.py`, `beauty_scorer.py` con lógica utilizable.
- **ui**: `panel.html` más `components/` y `themes/` para overlays, handles y temas visuales.
- **modules**: `resize-pro/`, `move-pro/`, `style-editor/`, `grid-intelligence/`, `ai-nudge/` listos para enchufar nuevas capacidades.
- **cli**: `protonox.py` expone `protonox dev`, `protonox audit`, `protonox export`.

### Live Reload (Kivy 2.3.1)
- `HotReloadEngine` aporta reload real de Python + KV con rollback seguro y preservación de estado (`ReloadState` + `LiveReloadStateCapable`).
- `HotReloadAppBase` mantiene el overlay rojo heredado, soporta mapeo `FILE_TO_SCREEN` para recarga parcial y usa watchdog+hashes para evitar ruido; si falla, cae a rebuild completo.
- Niveles: 0 (rebuild), 1 (KV), 2 (Python con grafo), 3 (Python+KV+estado) con degradación automática.
- Flag de control: `PROTONOX_HOT_RELOAD_MAX` limita el nivel máximo en entornos de desarrollo.

## Requerimientos inteligentes
| Característica               | Qué hace                                               | Por qué es mágico                              |
|------------------------------|--------------------------------------------------------|------------------------------------------------|
| 8px Grid Auto-Snap           | Ajusta a múltiplos de 8px y baseline 4px               | Consistencia instantánea                       |
| Baseline Grid Lock           | Lock vertical para line-height perfecto                | Tipografía impecable                           |
| Golden Ratio Suggestion      | Calcula proporciones 1.618 para héroes/cards           | Belleza matemática automática                  |
| Safe Area Awareness          | Detecta invasiones de notch/home indicator             | Nunca más bugs de iPhone                      |
| Typography Scale Detector    | Detecta escalas 1.25 / 1.333 / 1.5                     | Detecta caos tipográfico                       |
| Auto Perfect Spacing         | Promedia padding/margin y los ajusta a la grilla       | IA decide el espaciado perfecto                |
| Component DNA                | Base para detectar clones y estandarizar componentes   | Nace tu design system solo                     |
| Contrast Guardian            | Revisa pares de colores y alerta < 4.5:1               | Accesibilidad automática                       |
| Focus Order Visualizer       | Expone el orden real de Tab                            | WCAG al instante                               |
| Responsive Breakpoint Magic  | Recomienda width/stacking por viewport                 | Mobile-first sin pensar                        |
| AI Nudge™                    | Tooltip contextual (espaciado, tokens, color)          | Diseñador personal 24/7                        |
| One-Click Fix                | Export rápido de manifest + tokens sugeridos           | Del caos al orden en segundos                  |
| Design Token Sync            | Genera tokens a partir de colores repetidos            | Tokens sin esfuerzo                            |

### Instalación y comandos
- PyPI: `pip install protonox-studio==0.1.5` (expone el comando `protonox`).
- Local editable: `pip install -e ./protonox-studio` (usa tu intérprete/venv). Requiere `pip>=23`.
- `protonox audit` devuelve un reporte JSON y un resumen legible sobre el UI-IR (HTML→modelo intermedio o Kivy introspection).
- `protonox export` genera KV + scaffolds Python en `.protonox/protonox-exports` sin tocar tu código.
- `protonox dev` levanta el servidor local con la inyección Arc Mode.
- `protonox web2kivy` (alias `web-to-kivy`) acepta un `--map protonox_studio.yaml` con rutas↔screens, respeta entrypoints declarativos y exporta bindings reproducibles.
- `protonox render-web` / `protonox render-kivy` generan PNG basados en el UI-IR para comparar (`protonox diff --baseline ... --candidate ...`).
- Compatibilidad: los comandos legacy continúan funcionando (`python protonox-studio/cli/protonox.py ...`).

### Producción (protonox.studio)
- Exponer el servidor detrás de un dominio/proxy: `PROTONOX_HOST=0.0.0.0 PROTONOX_PORT=8080 protonox dev` (ajusta el puerto al que te entregue el proxy o VM).
- Health check listo para load balancers en `/health` (alias `/healthz` o `/ping`), responde JSON con estado, backend y timestamp.
- `PROTONOX_BACKEND_URL` sigue sobreescribible por entorno; no se commitean claves ni URLs privadas.

### Instalación por pip (repo local)
- Local editable: `pip install -e ./protonox-studio` (usa tu intérprete/venv). Requiere `pip>=23`.
- Instalación empaquetada: `pip install ./protonox-studio`.
- Configura tus variables en `.env` copiando `.env.example` (no commits). Mínimos: Figma (`FIGMA_CLIENT_ID/SECRET`) y MercadoPago (`MP_PUBLIC_KEY/ACCESS_TOKEN`).

### MercadoPago (dev)
- Variables requeridas: `MP_PUBLIC_KEY`, `MP_ACCESS_TOKEN`; opcionales `MP_SUCCESS_URL`, `MP_FAILURE_URL`, `MP_PENDING_URL`, `MP_NOTIFICATION_URL`, `MP_WEBHOOK_SECRET`.
- Crear checkout: `POST /__dev_tools` con `{ "type": "mercadopago-create-preference", "plan": "monthly", "email": "test@example.com" }` devuelve `init_point` / `sandbox_init_point`.
- Estado y gating: `POST /__dev_tools` con `{ "type": "mercadopago-status" }` indica si hay suscripción activa y el último `checkout_url`; las acciones premium (`figma-sync-tokens`, `figma-push-update`) responden 402 si no hay pago.
- Webhook: `POST /payments/mercadopago/webhook` con payload de MercadoPago (firma opcional via `MP_WEBHOOK_SECRET`) marca la suscripción como activa y actualiza expiración.
- Modo gratis/donación: si `PROTONOX_FREE_MODE=1` (o `MP_FREE_MODE=1`), todo queda desbloqueado sin cobro; puedes ofrecer un botón “Donar” usando `{ "type": "mercadopago-create-preference", "plan": "donation", "amount": 5 }` y mostrar el `init_point` resultante.

### Figma (OAuth, embedding, webhooks)
- Variables requeridas: `FIGMA_CLIENT_ID`, `FIGMA_CLIENT_SECRET`; opcionales `FIGMA_REDIRECT_URI` (default `http://localhost:4173/figma-callback`) y `FIGMA_SCOPES` (separadas por espacio o coma; por defecto incluyen contenido, comentarios, dev resources, librerías, proyectos, webhooks y perfil).
- Auth: `GET /figma-auth` redirige a Figma con `state` aleatorio; `GET /figma-callback?code=...&state=...` guarda token en `.protonox/figma/figma_token.json`.
- Estado: `POST /__dev_tools` con `{ "type": "figma-status" }` devuelve conexión, expiración y scopes; `figma-sync-tokens` y `figma-push-update` requieren suscripción activa.
- Embedding: `POST /__dev_tools` con `{ "type": "figma-embed-config" }` devuelve `client_id` y `redirect_uri` para kits de incrustación (`?client-id=<id>`).
- Webhooks: `POST /figma-webhook` almacena eventos en `.protonox/figma/webhooks.jsonl` (sin validar firma por ahora); puedes registrar webhooks desde Figma apuntando a esa URL pública o tunelizada.

### MercadoPago (integración segura)
- Variables requeridas: `MP_PUBLIC_KEY`, `MP_ACCESS_TOKEN`; opcionales `MP_SUCCESS_URL`, `MP_FAILURE_URL`, `MP_PENDING_URL`, `MP_NOTIFICATION_URL`, `MP_WEBHOOK_SECRET`.
- Crear checkout: `POST /__dev_tools` con `{ "type": "mercadopago-create-preference", "plan": "monthly", "email": "test@example.com" }` valida con backend y devuelve `init_point` / `sandbox_init_point`.
- Estado y gating: `POST /__dev_tools` con `{ "type": "mercadopago-status" }` consulta backend para suscripción activa; acciones premium (`figma-sync-tokens`, `figma-push-update`) responden 402 si no hay pago.
- Webhook: `POST /payments/mercadopago/webhook` valida firma y actualiza estado en backend.
- Seguridad: Todas las operaciones se validan contra `PROTONOX_BACKEND_URL` para evitar manipulación local.

#### Declaración explícita del proyecto (requisito)
- Protonox Studio no asume tu proyecto: siempre se declara `--project-type web|kivy` y `--entrypoint` (por ejemplo `index.html` o `main.py`).
- El modo contenedor y el modo local usan el mismo flujo: `PROTONOX_PROJECT_TYPE`, `PROTONOX_BACKEND_URL` y `PROTONOX_STATE_DIR` controlan el contexto.
- Ejemplos:
  - `protonox audit --project-type web --entrypoint website/index.html`
  - `protonox audit --project-type kivy --entrypoint app/main.py --png screenshots/home.png`

## Automatización diaria
Para uso diario sin intervención manual, se incluye un script y plantillas de `systemd` para:
- Instalar dependencias si faltan
- Ejecutar `audit` y `export` cada mañana
- Mantener el servidor de desarrollo opcionalmente en ejecución

### Opción A: Cron (simple)
1) Crear el script diario:
	- Archivo: `protonox-studio/cli/daily_protonox.sh` (wrapper que delega al paquete instalado)
	- Uso: `bash protonox-studio/cli/daily_protonox.sh --path /ruta/al/proyecto`
2) Añadir al `crontab` del usuario para correr a las 09:00 todos los días:
```bash
crontab -e
# Añade esta línea (ajusta la ruta si es necesario)
0 9 * * * bash /home/protonox/Protonox/Protonox-Kivy-Multiplatform-Framework/protonox-studio/cli/daily_protonox.sh >> /home/protonox/Protonox/Protonox-Kivy-Multiplatform-Framework/protonox-studio/logs/daily.log 2>&1
```

### Opción B: systemd (recomendado)
Plantillas incluidas en `protonox-studio/cli/systemd-user/`:
- `protonox-studio.service`: corre `audit` y `export` y puede levantar el dev server
- `protonox-studio.timer`: dispara el servicio diariamente a las 09:00

Pasos para habilitar (modo usuario):
```bash
# Copiar las unidades al directorio de systemd del usuario
mkdir -p ~/.config/systemd/user
cp protonox-studio/cli/systemd-user/protonox-studio.service ~/.config/systemd/user/
cp protonox-studio/cli/systemd-user/protonox-studio.timer ~/.config/systemd/user/

# Recargar y habilitar el timer
systemctl --user daemon-reload
systemctl --user enable --now protonox-studio.timer

# Ver estado
systemctl --user status protonox-studio.timer
systemctl --user status protonox-studio.service
```

Logs:
- Cron: `<proyecto>/.protonox/logs/audit.log` y `.../export.log`
- systemd: `journalctl --user -u protonox-studio.service -f`

## Misión: llevar Protonox Studio a producción rentable
Este documento guía el rollout completo. Cualquier agente puede retomarlo leyendo esta sección.

### Visión
- Protonox Studio es el overlay de diseño inteligente que funciona encima de cualquier sitio ya publicado o en desarrollo.
- El objetivo es habilitar auditorías automatizadas, correcciones asistidas por IA (ARC Mode) y sincronización con Figma, monetizando a través de MercadoPago con validación segura en backend.

### Marco de trabajo (seguimiento)
1. **Demo pública sobre el landing actual (`website/index.html`)**
	- [ ] Servir el sitio con `python -m http.server 8080`.
	- [ ] Ejecutar `protonox.py dev` y validar la inyección ARC en `http://localhost:8080/index.html?protonox=1`.
	- [ ] Grabar video demo o capturas (usa Playwright hooks de `core/local_dev_server.py`).
	- [ ] Documentar atajos (Ctrl, Alt x2, Alt+Enter) en la landing o docs públicos.
2. **Integración Figma real**
	- [ ] Implementar endpoint `/__dev_tools` que procese `figma-sync-tokens` y `figma-push-update` con OAuth real.
	- [ ] Guardar tokens sincronizados en `tokens/` y confirmar push de nodos (usar `data-figma-id`).
	- [ ] Añadir sección en panel UI con estado conectado/desconectado.
3. **Monetización vía MercadoPago**
	- [ ] Configurar backend API para MercadoPago con validación segura.
	- [ ] Implementar gating en dev server que consulta backend para suscripción.
	- [ ] Agregar UI de pricing en el overlay inyectado.
4. **Entrega continua y reportes**
	- [x] Completar script `cli/daily_protonox.sh` para que instale deps, ejecute `audit` y `export`, y deje logs por ejecución.
	- [ ] Activar cron o systemd timer.
	- [ ] Almacenar reportes en `dev-reports/` y tokens en `protonox-exports/`.
5. **Preparación de lanzamiento**
	- [ ] Escribir runbook con pasos de soporte (activar/desactivar usuarios, regenerar tokens Figma, reconciliar pagos vía backend).
	- [ ] Configurar monitoreo básico (logs del dev server, webhook errors) y fallback.
	- [ ] Redactar tutorial onboarding (texto + demo.mp4) y ubicarlo en overlay de bienvenida.
6. **Distribución pip/CLI**
	- [x] Reorganizar el código bajo `src/protonox_studio` con `pyproject.toml` y `MANIFEST.in`.
	- [x] Exponer el comando global `protonox` y mantener wrappers legacy.
	- [ ] Publicar paquete en index interno o PyPI privado y documentar versionado.

### Indicadores de éxito
- Demo reproducible sin intervención manual (server + overlay + panel).
- Sincronización Figma funcionando tras pago confirmado.
- Reportes diarios generados + enviados.
- Monetización segura con MercadoPago integrada.

### Proximas acciones sugeridas
- Prioridad Alta: implementar `/__dev_tools` con MercadoPago + Figma con validación backend.
- Prioridad Media: completar script diario y runbook.
- Prioridad Baja: pulir tutorial multimedia y material de marketing.

## Code Quality Assurance

Protonox Studio maintains **extreme code quality** standards, ensuring reliability and maintainability.

### Wireless Debugging con QR
- **Protonox Kivy Core** inicia un servidor WebSocket que transmite logs, estado UI y eventos táctiles en tiempo real.
- **Protonox Studio** se conecta al servidor para recibir datos de debugging.
- El dispositivo muestra un QR con la URL del servidor; escanéalo desde Studio para conectar.

#### Uso
1. En tu app Kivy, habilita wireless debugging: `PROTONOX_WIRELESS_DEBUG=1 python main.py`
2. La app mostrará un QR con la IP:puerto para ADB wireless (en Android) o la URL WebSocket (en otros).
3. En Studio: 
   - Para Android: `protonox wireless-connect --adb-wireless-ip-port IP:5555`
   - Para otros: `protonox wireless-connect --wireless-url ws://192.168.1.100:8765`
4. Los datos de debugging fluyen en tiempo real.

#### Comandos CLI
- `protonox wireless-connect --wireless-url <url>` — Conectar directamente a WebSocket.
- `protonox wireless-connect --adb-wireless-ip-port <ip:puerto>` — Conectar vía ADB wireless (Android).
- `protonox wireless-disconnect` — Desconectar.
- `protonox wireless-status` — Ver estado de conexión.

#### Requerimientos
- Instalar dependencias: `pip install websockets qrcode[pil]`
- Puerto 8765 debe estar abierto en el dispositivo.

### Test Coverage
- Test files formatted and linted.
- No critical bugs in core functionality.

### Commit History
- Latest commit: "Achieve extreme code quality: fix all critical bugs, format with black, remove unused imports, correct style issues"
- 44 files updated for quality improvements.

This ensures Protonox Studio is production-ready with high standards.

## Uso en Termux (Android)

Protonox Studio está optimizado para desarrollo móvil con Termux. Instala las versiones compatibles y conecta rápidamente vía QR y WiFi.

### Instalación en Termux
```bash
# Instalar Python y pip si no están
pkg install python

# Instalar librerías compatibles (sin dependencias pesadas)
pip install protonox-kivy==3.0.0.dev4 protonox-studio==0.1.3
```

### Conexión Rápida al Celular por QR y WiFi

1. **En tu PC (Linux/Mac/Windows):**
   - Inicia el servidor de setup ADB:
     ```bash
     cd Protonox-Kivy-Multiplatform-Framework
     python3 adb_setup_server.py
     ```
     Esto genera un QR que abre una página web para conectar ADB automáticamente.

2. **En tu teléfono (Termux):**
   - Escanea el QR con la cámara de Android → Se abre el navegador con la página de conexión.
   - Haz clic en "Connect ADB" → El PC ejecuta `adb connect` y conecta inalámbricamente.
   - Verifica: `adb devices` (debería mostrar el dispositivo conectado).

3. **Prueba la App en Termux:**
   - Copia `test_app.py` al teléfono:
     ```bash
     adb push test_app.py /sdcard/
     ```
   - Ejecuta con debug inalámbrico:
     ```bash
     PROTONOX_WIRELESS_DEBUG=1 python /sdcard/test_app.py
     ```
     - Muestra un QR para WebSocket (si hay websockets instalado).
     - Abre la app Kivy con ScissorPush/ScissorPop funcionando.

4. **Live Reload desde PC:**
   - En PC, inicia el servidor:
     ```bash
     cd protonox-studio
     source venv_protonox_studio_debug/bin/activate
     python -m protonox_studio.core.live_reload --host 0.0.0.0 --port 8080
     ```
   - La app en Termux se conecta automáticamente y permite recarga en vivo.

### Comandos Básicos de Uso
- **Desarrollo local:** `protonox dev` (inicia servidor web para overlays).
- **Auditoría:** `protonox audit <file>` (analiza diseño y genera reportes).
- **Export:** `protonox export <file>` (exporta tokens y componentes).
- **Conectar wireless:** `protonox wireless-connect --adb-wireless-ip-port 192.168.1.100:5555`
- **Desconectar:** `protonox wireless-disconnect`
- **Estado:** `protonox wireless-status`

### Preview en Termux
El QR generado abre una vista previa web simple de la app (sin Kivy render, pero con estructura). Úsalo para detectar errores iniciales antes de ejecutar la app completa.

### Troubleshooting
- Si faltan dependencias: `pip install protonox-studio[web]==0.1.4` (requiere Rust para FastAPI).
- Para funciones de imagen (comparación PNG, renderizado): `pip install protonox-studio[image]==0.1.5` (requiere compilación de Pillow).
- Para builds en Android: Asegúrate de tener `clang` y `make` en Termux.
- Errores de conexión: Verifica que el teléfono y PC estén en la misma red WiFi.

¡Listo para desarrollo móvil sin complicaciones!


