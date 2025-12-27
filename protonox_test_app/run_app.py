#!/usr/bin/env python3
"""
Launcher script for Protonox Test App.
Configures Python path correctly for imports.
"""

import sys
from pathlib import Path

# Add the project root to Python path for all imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add the app directory to Python path
app_dir = project_root / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Now import and run the app as a module
if __name__ == "__main__":
    from app.main import ProtonoxApp
    ProtonoxApp().run()