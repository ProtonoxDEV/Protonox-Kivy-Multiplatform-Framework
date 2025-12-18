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
- PyPI: `pip install protonox-studio==0.1.1` (expone el comando `protonox`).
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
- Estado: `POST /__dev_tools` con `{ "type": "figma-status" }` devuelve conexión, expiración y scopes; `figma-sync-tokens` y `figma-push-update` se mantienen premium (402 si no hay pago).
- Embedding: `POST /__dev_tools` con `{ "type": "figma-embed-config" }` devuelve `client_id` y `redirect_uri` para kits de incrustación (`?client-id=<id>`).
- Webhooks: `POST /figma-webhook` almacena eventos en `.protonox/figma/webhooks.jsonl` (sin validar firma por ahora); puedes registrar webhooks desde Figma apuntando a esa URL pública o tunelizada.

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
- El objetivo es habilitar auditorías automatizadas, correcciones asistidas por IA (ARC Mode) y sincronización con Figma, cobrando por ello mediante MercadoPago.

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
	- [ ] Configurar planes/checkout con `backend/api/mercadopago.py`.
	- [ ] Crear webhook que marque usuarios como “activos” en la base de datos.
	- [ ] Gatear desde el dev server las acciones premium (`export`, `figma-sync`, reportes completos) según suscripción.
	- [ ] Agregar pricing y CTA en `website/index.html` enlazando a checkout.
4. **Entrega continua y reportes**
	- [x] Completar script `cli/daily_protonox.sh` para que instale deps, ejecute `audit` y `export`, y deje logs por ejecución.
	- [ ] Activar cron o systemd timer.
	- [ ] Almacenar reportes en `dev-reports/` y tokens en `protonox-exports/`.
5. **Preparación de lanzamiento**
	- [ ] Escribir runbook con pasos de soporte (activar/desactivar usuarios, regenerar tokens Figma, reconciliar pagos).
	- [ ] Configurar monitoreo básico (logs del dev server, webhook errors) y fallback.
	- [ ] Redactar tutorial onboarding (texto + demo.mp4) y ubicarlo en overlay de bienvenida.
6. **Distribución pip/CLI**
	- [x] Reorganizar el código bajo `src/protonox_studio` con `pyproject.toml` y `MANIFEST.in`.
	- [x] Exponer el comando global `protonox` y mantener wrappers legacy.
	- [ ] Publicar paquete en index interno o PyPI privado y documentar versionado.

### Indicadores de éxito
- Demo reproducible sin intervención manual (server + overlay + panel).
- Sincronización Figma y export ZIP funcionando tras pago confirmado.
- Reportes diarios generados + enviados.
- Página pública promocionando planes con checkout activo.

### Proximas acciones sugeridas
- Prioridad Alta: implementar `/__dev_tools` con MercadoPago + Figma.
- Prioridad Media: completar script diario y runbook.
- Prioridad Baja: pulir tutorial multimedia y material de marketing.

## Code Quality Assurance

Protonox Studio maintains **extreme code quality** standards, ensuring reliability and maintainability.

### Linting and Formatting
- **Flake8**: All critical errors (E999, E722, F841, etc.) resolved.
- **Black**: Code formatted with 120-character line length.
- **Autoflake**: Unused imports and variables removed.
- **Autopep8**: Consistent style applied.

### Test Coverage
- Test files formatted and linted.
- No critical bugs in core functionality.

### Commit History
- Latest commit: "Achieve extreme code quality: fix all critical bugs, format with black, remove unused imports, correct style issues"
- 44 files updated for quality improvements.

This ensures Protonox Studio is production-ready with high standards.


