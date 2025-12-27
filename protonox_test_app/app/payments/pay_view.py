from kivy.uix.screenmanager import Screen

from ..services.payment_service import PaymentService
from ..services.backend_service import BackendService


class PayView(Screen):
    name = "payments"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PaymentService(BackendService())

    def start_payment(self, amount: float) -> str:
        try:
            data = self.service.init_payment(amount)
            return f"Pago iniciado: {data.get('payment_id', 'N/A')}"
        except Exception as exc:  # noqa: BLE001
            return f"Error iniciando pago: {exc}"
