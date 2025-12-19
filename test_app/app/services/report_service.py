from typing import Any, Dict, List

from .backend_service import BackendService
from .firebase_service import FirebaseService


class ReportService:
    """Aggregates reporting data from Render and Firebase."""

    def __init__(self, backend: BackendService, firebase: FirebaseService):
        self.backend = backend
        self.firebase = firebase

    def fetch_activity(self) -> List[Dict[str, Any]]:
        try:
            return self.backend.get("reports/activity")
        except Exception:
            # Fallback to Firebase collection
            document = self.firebase.firestore_get("reports/activity")
            return document.get("documents", [])

    def generate_pdf_export(self, content: str) -> str:
        # Placeholder: in a real scenario, integrate a PDF generator
        path = "reports_export.pdf"
        with open(path, "w", encoding="utf-8") as handler:
            handler.write(content)
        return path
