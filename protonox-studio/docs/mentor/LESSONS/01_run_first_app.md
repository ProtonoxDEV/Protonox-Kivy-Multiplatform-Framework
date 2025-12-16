# Lección 01 · Run first app

Meta: verificar entorno y ejecutar la demo mínima.

Pasos:
1) Crea/activa tu venv (Python >=3.10).
2) Instala dependencias del proyecto (`pip install -e .`).
3) Ejecuta: `protonox dev --path . --project-type web` (o el modo que uses).
4) Abre el puerto indicado y confirma que carga la UI.

Errores comunes:
- Falta SDL/GL en sistemas Linux: instala paquetes de OpenGL/SDL3.
- Puerto ocupado: pasa `--port 5173` (web) o ajusta el que uses.

Ejercicio:
- Cambia un color en la UI y recarga para ver el cambio.

Checklist de éxito:
- Comando ejecuta sin traceback.
- UI visible en el navegador o ventana Kivy.
- Log muestra “Dev server running”.
