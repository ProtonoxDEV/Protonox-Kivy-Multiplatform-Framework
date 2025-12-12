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
- `pip install .` dentro de `protonox-studio/` instala Protonox Studio como paquete (`protonox` queda disponible en el PATH).
- `protonox audit` devuelve un reporte JSON y un resumen legible (usa el snapshot sintético por defecto).
- `protonox export` crea un manifest base en `protonox-export/`.
- `protonox dev` levanta el servidor local con la inyección Arc Mode.
- Compatibilidad: los comandos legacy continúan funcionando (`python protonox-studio/cli/protonox.py ...`).

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


