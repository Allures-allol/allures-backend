# services/payment_service/crud/monobank.py
from __future__ import annotations
import hmac, hashlib, base64, json
import httpx
from typing import Any, Dict, Tuple
from common.config.settings import settings

MONO_API_CREATE = "https://api.monobank.ua/api/merchant/invoice/create"

def _webhook_url() -> str | None:
    # Явный https из настроек приоритетнее
    if settings.MONOBANK_WEBHOOK_URL:
        return settings.MONOBANK_WEBHOOK_URL
    # Иначе не подставляем локальный http — Monobank такое часто отвергает
    return None

async def monobank_create_invoice(*, amount_uah: float, order_id: str, email: str | None = None,
                                  display_type: str = "iframe") -> Dict[str, Any]:
    if not settings.MONOBANK_TOKEN:
        raise RuntimeError("MONOBANK_TOKEN is not set")

    amount_cop = int(round(amount_uah * 100))  # копейки
    body = {
        "amount": amount_cop,
        "ccy": 980,  # UAH
        "merchantPaymInfo": {
            "reference": order_id,
            "destination": f"Order {order_id}",
            "comment": f"Order {order_id}",
            "customerEmails": [email] if email else [],
            "redirectUrl": settings.MONOBANK_REDIRECT_URL,
            # webHookUrl добавляем только если https задан
            **({"webHookUrl": settings.MONOBANK_WEBHOOK_URL} if settings.MONOBANK_WEBHOOK_URL else {}),
        },
        "paymentType": "debit",
        # ВАЖНО: никаких saveCardData / paymentMethod / qrId / ps / ector / ...
    }

    headers = {
        "X-Token": settings.MONOBANK_TOKEN,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as c:
        r = await c.post(MONO_API_CREATE, headers=headers, json=body)
        if r.status_code >= 400:
            raise RuntimeError(f"Monobank {r.status_code}: {r.text}")
        data = r.json()

    if not data.get("pageUrl") or not data.get("invoiceId"):
        raise RuntimeError(f"Monobank response missing fields: {data}")

    return {"pageUrl": data["pageUrl"], "invoiceId": data["invoiceId"]}

def verify_monobank_signature(raw_body: bytes, signature_b64: str | None) -> bool:
    """
    Monobank шлёт подпись в заголовке X-Signature (Base64 от HMAC-SHA256 по телу webhook).
    Некоторые интеграции используют тот же MONOBANK_TOKEN как секрет.
    """
    if not signature_b64 or not settings.MONOBANK_TOKEN:
        return False
    secret = settings.MONOBANK_TOKEN.encode("utf-8")
    mac = hmac.new(secret, msg=raw_body, digestmod=hashlib.sha256).digest()
    calc = base64.b64encode(mac).decode("utf-8")
    # тайминг-безопасное сравнение
    return hmac.compare_digest(calc, signature_b64)
