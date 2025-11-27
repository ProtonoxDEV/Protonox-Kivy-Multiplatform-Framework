#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"


def create_app(app_name: str, template: str) -> None:
    source = TEMPLATES_DIR / template
    if not source.exists():
        raise SystemExit(f"Template '{template}' not found in {TEMPLATES_DIR}")

    destination = REPO_ROOT / app_name
    if destination.exists():
        raise SystemExit(f"Destination '{destination}' already exists")

    shutil.copytree(source, destination)
    print(f"Created app '{app_name}' from template '{template}' at {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new Protonox app from a template")
    parser.add_argument("app_name", help="Name of the app to create")
    parser.add_argument("--template", default="protonox-app-complete", help="Template folder name")
    args = parser.parse_args()

    create_app(args.app_name, args.template)


if __name__ == "__main__":
    main()
