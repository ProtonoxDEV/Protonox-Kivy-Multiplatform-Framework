"""Web tooling scaffolding for Protonox Studio.

Includes dev runners, doctor checks, env helpers, and asset manifest utilities.
"""

from __future__ import annotations

from .dev import run_web_dev, run_web_dev_generic
from .doctor import run_web_doctor
from .env import write_env_templates
from .assets import ensure_assets_manifest, ingest_asset, watch_assets

__all__ = [
    "run_web_dev",
    "run_web_dev_generic",
    "run_web_doctor",
    "write_env_templates",
    "ensure_assets_manifest",
    "ingest_asset",
    "watch_assets",
]
