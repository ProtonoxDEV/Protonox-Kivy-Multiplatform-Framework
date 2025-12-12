"""HTML injector for the Protonox Studio client bundle.

Intended behavior:
- Insert a single `<script type="module" src="http://localhost:4173/studio"></script>` line.
- Keep injection idempotent across reloads.
"""

SCRIPT_TAG = '<script type="module" src="http://localhost:4173/studio"></script>'


def inject(html: str) -> str:
    """Inject the studio script tag into an HTML document (placeholder)."""
    if SCRIPT_TAG in html:
        return html
    return html.replace("</body>", f"  {SCRIPT_TAG}\n</body>")
