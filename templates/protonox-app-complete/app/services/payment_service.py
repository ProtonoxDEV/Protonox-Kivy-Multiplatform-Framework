from typing import Any, Dict

from .backend_service import BackendService


class PaymentService:
    """Generic REST-based payment abstraction."""

    def __init__(self, backend: BackendService):
        self.backend = backend

    def init_payment(self, amount: float, currency: str = "USD") -> Dict[str, Any]:
        payload = {"amount": amount, "currency": currency}
        return self.backend.post("payments/init", payload)

    def confirm_payment(self, payment_id: str, method: str) -> Dict[str, Any]:
        payload = {"payment_id": payment_id, "method": method}
        return self.backend.post("payments/confirm", payload)

    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        return self.backend.get(f"payments/status/{payment_id}")
