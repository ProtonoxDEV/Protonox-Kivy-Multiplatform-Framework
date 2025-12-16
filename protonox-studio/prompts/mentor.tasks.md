Formato de misión (usa el chatbot con este esquema):

Misión: <tarea corta>
- Contexto: <archivo o feature>
- Pasos sugeridos: <lista breve>
- Errores comunes: <bullets>
- Checklist de éxito: <bullets verificables>
- Comandos de validación: <python scripts/mentor/...>

Ejemplo: Crear pantalla Settings
- Contexto: agregar pantalla Settings con botón Volver.
- Pasos sugeridos: crea frontend/settings/SettingsScreen.kv y backend/settings/SettingsScreen.py; registra en router/ScreenManager; agrega navegación.
- Errores comunes: falta de import en router; id duplicado; ruta de asset rota.
- Checklist: la app navega a Settings y regresa; sin traceback en consola.
- Validación: python scripts/mentor/check_kv.py --screen Settings (cuando implementes los checks).

Ejemplo: Pipeline de assets
- Contexto: agregar icono PNG y usarlo en una pantalla.
- Checklist: asset copiado a carpeta declarada; referenciado en KV; carga sin 404.
- Validación: python scripts/mentor/check_assets.py --asset icon.png (placeholder).
