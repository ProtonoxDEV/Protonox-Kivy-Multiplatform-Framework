"""Non-invasive diagnostics (BluntMine)."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .project_context import ProjectContext


@dataclass
class BluntMineReport:
    environment: Dict[str, object]
    recommendations: List[str]
    warnings: List[str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "environment": self.environment,
            "recommendations": self.recommendations,
            "warnings": self.warnings,
        }


def run_bluntmine(context: ProjectContext) -> BluntMineReport:
    recommendations: List[str] = []
    warnings: List[str] = []

    if context.project_type == "kivy" and not context.kv_files:
        warnings.append("No se encontraron archivos .kv en el proyecto Kivy declarado.")
    if context.project_type == "web" and not (context.entrypoint.parent / "index.html").exists():
        warnings.append("No se detectó index.html en la raíz indicada; usando detección heurística.")

    if not Path(context.entrypoint).exists():
        warnings.append(f"El entrypoint declarado no existe: {context.entrypoint}")
    else:
        recommendations.append("Entrypoint verificado: no se modifica ni se ejecuta automáticamente.")

    if context.backend_url.startswith("https://protonox-backend"):
        recommendations.append("IA delegada al backend Protonox en Render (sin claves locales).")

    if context.container_mode:
        recommendations.append("Modo contenedor activo: comportamiento alineado con entorno local.")

    env = {
        "python": platform.python_version(),
        "system": platform.system(),
        "release": platform.release(),
        "project_type": context.project_type,
        "entrypoint": str(context.entrypoint),
        "kv_files": [str(k) for k in context.kv_files],
        "backend": context.backend_url,
        "container": context.container_mode,
    }

    return BluntMineReport(environment=env, recommendations=recommendations, warnings=warnings)
