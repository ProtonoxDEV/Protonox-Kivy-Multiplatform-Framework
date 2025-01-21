import os
import re
import json
from collections import defaultdict

# Directorios y archivos
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
LOG_FILE = os.path.join(REPORTS_DIR, "reporte_ids.txt")
JSON_FILE = os.path.join(REPORTS_DIR, "ids.json")

# Asegurarse de que el directorio de reportes existe
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)


def parse_log_file(log_file):
    """
    Parsea el archivo de registro para extraer los IDs encontrados y sus ubicaciones.
    """
    id_map = defaultdict(list)
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            current_file = None
            for line in f:
                # Detectar el archivo escaneado
                if line.startswith("Escaneando archivo:"):
                    current_file = line.split(":", 1)[1].strip()
                # Detectar líneas con IDs
                elif "[DEBUG]" in line and "id:" in line:
                    match = re.search(r'id:\s*([\w_]+)', line)
                    if match and current_file:
                        id_ = match.group(1)
                        id_map[id_].append(current_file)
    except Exception as e:
        print(f"Error al procesar {log_file}: {e}")
    return id_map


def save_to_json(data, json_file):
    """
    Guarda los datos estructurados en un archivo JSON.
    """
    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"JSON generado: {json_file}")
    except Exception as e:
        print(f"Error al guardar el JSON: {e}")


def main():
    print("===== Análisis de IDs en KV =====")
    if not os.path.exists(LOG_FILE):
        print(f"Error: {LOG_FILE} no existe. Por favor, ejecuta primero el análisis.")
        return

    # Parsear el archivo de registro
    print(f"Procesando archivo: {LOG_FILE}")
    id_map = parse_log_file(LOG_FILE)

    # Guardar el mapa de IDs en JSON
    print("Generando archivo JSON...")
    save_to_json(id_map, JSON_FILE)
    print("\n✅ Análisis completado.")


if __name__ == "__main__":
    main()
