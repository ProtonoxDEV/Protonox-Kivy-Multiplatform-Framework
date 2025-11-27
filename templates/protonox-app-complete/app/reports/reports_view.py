from kivy.uix.screenmanager import Screen

from ..services.backend_service import BackendService
from ..services.report_service import ReportService
from ..services.firebase_service import FirebaseService


class ReportsView(Screen):
    name = "reports"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        backend = BackendService()
        firebase = FirebaseService()
        self.service = ReportService(backend, firebase)

    def load_reports(self) -> str:
        try:
            reports = self.service.fetch_activity()
            return f"{len(reports)} reportes obtenidos"
        except Exception as exc:  # noqa: BLE001
            return f"Error al cargar reportes: {exc}"
