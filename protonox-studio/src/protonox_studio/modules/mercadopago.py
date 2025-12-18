"""MercadoPago helpers for Protonox Studio dev server.

Keeps a lightweight state file to gate premium actions (Figma sync/export).
All secrets are expected as environment variables; nothing is stored in code.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
STATE_PATH = Path(os.environ.get("PROTONOX_SUBSCRIPTION_FILE") or (ROOT_DIR.parent / ".protonox" / "subscription.json"))
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class SubscriptionStatus:
    active: bool
    plan: str
    active_until: Optional[datetime]
    last_checkout_url: Optional[str]
    last_payment_id: Optional[str]
    preference_id: Optional[str]
    currency: str
    amount: float
    updated_at: datetime
    reason: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "plan": self.plan,
            "active_until": self.active_until.isoformat() if self.active_until else None,
            "last_checkout_url": self.last_checkout_url,
            "last_payment_id": self.last_payment_id,
            "preference_id": self.preference_id,
            "currency": self.currency,
            "amount": self.amount,
            "updated_at": self.updated_at.isoformat(),
            "reason": self.reason,
        }


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def _load_state() -> Dict[str, Any]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_state(payload: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))


def _env(name: str, fallback: Optional[str] = None) -> Optional[str]:
    return os.environ.get(name) or os.environ.get(name.replace("MP_", "MERCADOPAGO_")) or fallback


def _config() -> Tuple[str, str, str, str, str, str]:
    access_token = _env("MP_ACCESS_TOKEN")
    public_key = _env("MP_PUBLIC_KEY")
    success_url = _env("MP_SUCCESS_URL", "http://localhost:4173/pay/success")
    failure_url = _env("MP_FAILURE_URL", "http://localhost:4173/pay/failure")
    pending_url = _env("MP_PENDING_URL", "http://localhost:4173/pay/pending")
    notification_url = _env("MP_NOTIFICATION_URL")

    if not access_token or not public_key:
        raise RuntimeError("Configura MP_ACCESS_TOKEN y MP_PUBLIC_KEY como variables de entorno.")
    return access_token, public_key, success_url, failure_url, pending_url, notification_url


def _plan_amount(plan: str) -> Tuple[float, str]:
    plan_key = (plan or "monthly").lower()
    monthly = float(os.environ.get("PLAN_MONTHLY_USD", "12"))
    yearly = float(os.environ.get("PLAN_YEARLY_USD", "96"))
    currency = os.environ.get("MP_CURRENCY", "USD")
    if plan_key in {"donation", "donate", "tip"}:
        donation_amount = float(os.environ.get("MP_DONATION_AMOUNT", "5"))
        return donation_amount, currency
    if plan_key in {"year", "yearly", "anual"}:
        return yearly, currency
    return monthly, currency


def _is_free_mode() -> bool:
    return os.environ.get("PROTONOX_FREE_MODE") in {"1", "true", "True"} or os.environ.get("MP_FREE_MODE") in {
        "1",
        "true",
        "True",
    }


def subscription_status() -> SubscriptionStatus:
    raw = _load_state()
    plan = raw.get("plan", "monthly")
    amount, currency = _plan_amount(plan)
    active_until = _parse_date(raw.get("active_until"))
    if _is_free_mode():
        return SubscriptionStatus(
            active=True,
            plan=plan,
            active_until=None,
            last_checkout_url=raw.get("last_checkout_url"),
            last_payment_id=raw.get("last_payment_id"),
            preference_id=raw.get("preference_id"),
            currency=currency,
            amount=amount,
            updated_at=_now(),
            reason="free_mode",
        )

    active = bool(active_until and active_until > _now())
    updated_at = _parse_date(raw.get("updated_at")) or _now()
    return SubscriptionStatus(
        active=active,
        plan=plan,
        active_until=active_until,
        last_checkout_url=raw.get("last_checkout_url"),
        last_payment_id=raw.get("last_payment_id"),
        preference_id=raw.get("preference_id"),
        currency=raw.get("currency", currency),
        amount=float(raw.get("amount", amount)),
        updated_at=updated_at,
        reason=raw.get("reason"),
    )


def mark_checkout(preference_id: str, init_point: str, plan: str, amount: float, currency: str) -> SubscriptionStatus:
    status = subscription_status()
    status.active = False
    status.plan = plan
    status.active_until = None
    status.last_checkout_url = init_point
    status.preference_id = preference_id
    status.reason = None
    status.updated_at = _now()
    status.amount = amount
    status.currency = currency
    _save_state(status.as_dict())
    return status


def mark_active(payment_id: Optional[str], plan: Optional[str], status_text: str = "approved") -> SubscriptionStatus:
    status = subscription_status()
    plan = (plan or status.plan or "monthly").lower()
    amount, currency = _plan_amount(plan)
    billing_days = int(os.environ.get("PLAN_BILLING_DAYS", "31"))
    status.active = True
    status.plan = plan
    status.active_until = _now() + timedelta(days=billing_days)
    status.last_payment_id = payment_id
    status.reason = status_text
    status.amount = amount
    status.currency = currency
    status.updated_at = _now()
    _save_state(status.as_dict())
    return status


def mark_inactive(reason: str) -> SubscriptionStatus:
    status = subscription_status()
    if status.reason == "free_mode":
        return status
    status.active = False
    status.reason = reason
    status.updated_at = _now()
    _save_state(status.as_dict())
    return status


def create_preference(
    plan: str = "monthly", email: Optional[str] = None, amount: Optional[float] = None
) -> Dict[str, Any]:
    access_token, public_key, success_url, failure_url, pending_url, notification_url = _config()
    auto_return = "approved"

    # Donation mode: no gating, pure support
    if plan.lower() in {"donation", "donate", "tip"}:
        donation_amount, currency = _plan_amount(plan)
        if amount is not None:
            donation_amount = amount
        payload: Dict[str, Any] = {
            "items": [
                {
                    "title": "Protonox Studio Donation",
                    "quantity": 1,
                    "unit_price": donation_amount,
                    "currency_id": currency,
                }
            ],
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url,
            },
            "auto_return": auto_return,
            "metadata": {"plan": "donation", "product": "protonox-studio"},
            "statement_descriptor": "PROTONOX DONATION",
        }
    else:
        amount_calc, currency = _plan_amount(plan)
        if amount is not None:
            amount_calc = amount
        payload = {
            "items": [
                {
                    "title": f"Protonox Studio {plan.title()} Plan",
                    "quantity": 1,
                    "unit_price": amount_calc,
                    "currency_id": currency,
                }
            ],
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url,
            },
            "auto_return": auto_return,
            "metadata": {"plan": plan, "product": "protonox-studio"},
            "statement_descriptor": "PROTONOX STUDIO",
        }
    payload: Dict[str, Any] = {
        "items": [
            {
                "title": f"Protonox Studio {plan.title()} Plan",
                "quantity": 1,
                "unit_price": amount,
                "currency_id": currency,
            }
        ],
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },
        "auto_return": "approved",
        "metadata": {"plan": plan, "product": "protonox-studio"},
        "statement_descriptor": "PROTONOX STUDIO",
    }
    if notification_url:
        payload["notification_url"] = notification_url
    if email:
        payload["payer"] = {"email": email}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        "https://api.mercadopago.com/checkout/preferences",
        headers=headers,
        json=payload,
        timeout=15,
    )
    if resp.status_code >= 300:
        raise RuntimeError(f"MercadoPago error {resp.status_code}: {resp.text}")
    data = resp.json()
    init_point = data.get("init_point") or data.get("sandbox_init_point")
    preference_id = data.get("id")
    amount_charged = payload["items"][0]["unit_price"]
    mark_checkout(
        preference_id=preference_id, init_point=init_point, plan=plan, amount=amount_charged, currency=currency
    )
    return {
        "preference_id": preference_id,
        "init_point": init_point,
        "sandbox_init_point": data.get("sandbox_init_point"),
        "plan": plan,
        "amount": amount_charged,
        "currency": currency,
        "public_key": public_key,
    }


def verify_webhook(headers: Dict[str, str]) -> bool:
    secret = os.environ.get("MP_WEBHOOK_SECRET")
    if not secret:
        return True
    signature = headers.get("X-Signature") or headers.get("x-signature") or ""
    return secret in signature


def apply_webhook(payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    if not verify_webhook(headers):
        return {"status": "forbidden"}

    data = payload.get("data") or {}
    metadata = payload.get("metadata") or data.get("metadata") or {}
    plan = metadata.get("plan") or payload.get("plan")
    payment_id = data.get("id") or payload.get("id") or payload.get("data_id")
    status_text = (payload.get("status") or data.get("status") or payload.get("action") or "").lower()

    if status_text in {"approved", "authorized"}:
        status = mark_active(payment_id=payment_id, plan=plan, status_text=status_text)
        return {"status": "active", **status.as_dict()}

    status = mark_inactive(reason=status_text or "pending")
    return {"status": status_text or "pending", **status.as_dict()}
