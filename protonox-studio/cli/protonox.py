"""Backwards-compatible wrapper for the Protonox Studio CLI."""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from protonox_studio.cli.protonox import main  # noqa: E402


if __name__ == "__main__":
    main()
