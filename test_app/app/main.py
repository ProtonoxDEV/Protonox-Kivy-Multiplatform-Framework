from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from .navigation import NavigationManager
from .services.firebase_service import FirebaseService
from .services.backend_service import BackendService
from .services.payment_service import PaymentService
from .services.report_service import ReportService


class ProtonoxApp(App):
    """Main application entrypoint with centralized service access."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nav_manager = NavigationManager()
        self.firebase = FirebaseService()
        self.backend = BackendService()
        self.payments = PaymentService(self.backend)
        self.reports = ReportService(self.backend, self.firebase)

    def build(self) -> Screen:
        self.title = "Protonox App"
        self._load_kv_files()
        return self.nav_manager.build_initial_screen()

    def _load_kv_files(self) -> None:
        kv_dir = Path(__file__).parent.parent / "kv"
        for kv_file in ["navigation.kv", "login.kv", "home.kv", "payments.kv", "reports.kv"]:
            Builder.load_file(str(kv_dir / kv_file))


if __name__ == "__main__":
    ProtonoxApp().run()
