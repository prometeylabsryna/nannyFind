import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.request
import uuid
from abc import ABC, abstractmethod

from django.conf import settings
from django.utils import timezone


class PaymentProviderError(Exception):
    pass


PROVIDER_LABELS = {
    "liqpay": "LiqPay",
    "wayforpay": "WayForPay",
    "fondy": "Fondy",
    "stub": "Тестовий режим",
}


def webhook_url(provider_code: str) -> str:
    return f"{settings.BACKEND_URL}/api/v1/payments/webhooks/{provider_code}/"


def frontend_path(path: str) -> str:
    """Clean URL для return/stub redirect (без .html)."""
    base = settings.FRONTEND_URL.rstrip("/")
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{base}{path}"


def _wfp_hmac(fields: list[str]) -> str:
    raw = ";".join(str(f) for f in fields)
    return hmac.new(
        settings.WAYFORPAY_SECRET_KEY.encode(),
        raw.encode(),
        hashlib.md5,
    ).hexdigest()


def _fondy_sign(params: dict) -> str:
    filtered = {k: v for k, v in params.items() if v not in (None, "") and k != "signature"}
    values = [str(filtered[k]) for k in sorted(filtered.keys())]
    sign_string = "|".join([settings.FONDY_SECRET_KEY] + values)
    return hashlib.sha1(sign_string.encode()).hexdigest()


class BasePaymentProvider(ABC):
    code: str
    label: str

    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    def create_checkout(self, payment) -> dict:
        pass

    @abstractmethod
    def verify_webhook(self, request) -> dict:
        pass

    def build_webhook_response(self, result: dict) -> dict | None:
        return None


class StubPaymentProvider(BasePaymentProvider):
    code = "stub"
    label = "Тестовий режим"

    def is_configured(self) -> bool:
        return True

    def create_checkout(self, payment) -> dict:
        return {
            "provider": self.code,
            "order_reference": payment.order_reference,
            "checkout_url": (
                f"{frontend_path('/cabinet/parent/payments')}"
                f"?stub=1&order={payment.order_reference}"
            ),
            "stub": True,
            "message": "Stub mode: оплата буде підтверджена автоматично.",
        }

    def verify_webhook(self, request) -> dict:
        data = request.data if hasattr(request, "data") else json.loads(request.body)
        return {
            "order_reference": data.get("order_reference"),
            "status": data.get("status", "paid"),
            "external_id": data.get("external_id", f"stub-{uuid.uuid4().hex[:12]}"),
        }


class LiqPayProvider(BasePaymentProvider):
    code = "liqpay"
    label = "LiqPay"

    def is_configured(self) -> bool:
        return bool(settings.LIQPAY_PUBLIC_KEY and settings.LIQPAY_PRIVATE_KEY)

    def _sign(self, data_b64: str) -> str:
        raw = settings.LIQPAY_PRIVATE_KEY + data_b64 + settings.LIQPAY_PRIVATE_KEY
        return base64.b64encode(hashlib.sha1(raw.encode()).digest()).decode()

    def create_checkout(self, payment) -> dict:
        if not self.is_configured():
            raise PaymentProviderError("LiqPay не налаштовано.")
        payload = {
            "public_key": settings.LIQPAY_PUBLIC_KEY,
            "version": 3,
            "action": "pay",
            "amount": payment.amount_uah,
            "currency": "UAH",
            "description": payment.plan.title,
            "order_id": payment.order_reference,
            "result_url": f"{frontend_path('/cabinet/parent/payments')}?success=1",
            "server_url": webhook_url("liqpay"),
        }
        data_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
        return {
            "provider": self.code,
            "data": data_b64,
            "signature": self._sign(data_b64),
            "checkout_url": "https://www.liqpay.ua/api/3/checkout",
        }

    def verify_webhook(self, request) -> dict:
        data_b64 = request.POST.get("data") or (request.data.get("data") if hasattr(request, "data") else None)
        signature = request.POST.get("signature") or (
            request.data.get("signature") if hasattr(request, "data") else None
        )
        if not data_b64 or signature != self._sign(data_b64):
            raise PaymentProviderError("Невалідний LiqPay signature.")
        payload = json.loads(base64.b64decode(data_b64))
        status_map = {"success": "paid", "failure": "failed", "error": "failed"}
        return {
            "order_reference": payload.get("order_id"),
            "status": status_map.get(payload.get("status"), "pending"),
            "external_id": str(payload.get("payment_id", "")),
            "payload": payload,
        }


class WayForPayProvider(BasePaymentProvider):
    code = "wayforpay"
    label = "WayForPay"

    def is_configured(self) -> bool:
        return bool(settings.WAYFORPAY_MERCHANT_ACCOUNT and settings.WAYFORPAY_SECRET_KEY)

    def _domain(self) -> str:
        return settings.FRONTEND_URL.replace("https://", "").replace("http://", "").split("/")[0]

    def create_checkout(self, payment) -> dict:
        if not self.is_configured():
            raise PaymentProviderError("WayForPay не налаштовано.")
        order_date = int(timezone.now().timestamp())
        amount = payment.amount_uah
        product_name = payment.plan.title
        sign_fields = [
            settings.WAYFORPAY_MERCHANT_ACCOUNT,
            self._domain(),
            payment.order_reference,
            order_date,
            amount,
            "UAH",
            product_name,
            1,
            amount,
        ]
        return {
            "provider": self.code,
            "merchantAccount": settings.WAYFORPAY_MERCHANT_ACCOUNT,
            "merchantDomainName": self._domain(),
            "merchantSignature": _wfp_hmac(sign_fields),
            "orderReference": payment.order_reference,
            "orderDate": order_date,
            "amount": amount,
            "currency": "UAH",
            "productName": [product_name],
            "productCount": [1],
            "productPrice": [amount],
            "serviceUrl": webhook_url("wayforpay"),
            "returnUrl": f"{frontend_path('/cabinet/parent/payments')}?success=1",
        }

    def verify_webhook(self, request) -> dict:
        data = request.data if hasattr(request, "data") else json.loads(request.body)
        sign_fields = [
            data.get("merchantAccount", ""),
            data.get("orderReference", ""),
            data.get("amount", ""),
            data.get("currency", ""),
            data.get("authCode", ""),
            data.get("cardPan", ""),
            data.get("transactionStatus", ""),
            data.get("reasonCode", ""),
        ]
        expected = _wfp_hmac(sign_fields)
        if data.get("merchantSignature") and data.get("merchantSignature") != expected:
            raise PaymentProviderError("Невалідний WayForPay signature.")
        status_map = {"Approved": "paid", "Declined": "failed", "Expired": "failed"}
        return {
            "order_reference": data.get("orderReference"),
            "status": status_map.get(data.get("transactionStatus"), "pending"),
            "external_id": str(data.get("authCode", "")),
            "payload": data,
        }

    def build_webhook_response(self, result: dict) -> dict:
        order_ref = result.get("order_reference", "")
        status = "accept"
        ts = int(timezone.now().timestamp())
        signature = _wfp_hmac([order_ref, status, ts])
        return {
            "orderReference": order_ref,
            "status": status,
            "time": ts,
            "signature": signature,
        }


class FondyProvider(BasePaymentProvider):
    code = "fondy"
    label = "Fondy"

    FONDY_API = "https://api.fondy.eu/api/checkout/url/"

    def is_configured(self) -> bool:
        return bool(settings.FONDY_MERCHANT_ID and settings.FONDY_SECRET_KEY)

    def create_checkout(self, payment) -> dict:
        if not self.is_configured():
            raise PaymentProviderError("Fondy не налаштовано.")
        req = {
            "order_id": payment.order_reference,
            "merchant_id": int(settings.FONDY_MERCHANT_ID),
            "order_desc": payment.plan.title,
            "amount": payment.amount_uah * 100,
            "currency": "UAH",
            "response_url": f"{frontend_path('/cabinet/parent/payments')}?success=1",
            "server_callback_url": webhook_url("fondy"),
        }
        req["signature"] = _fondy_sign(req)
        body = json.dumps({"request": req}).encode()
        http_req = urllib.request.Request(
            self.FONDY_API,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_req, timeout=15) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            raise PaymentProviderError(f"Fondy API недоступний: {exc}") from exc
        response = payload.get("response", payload)
        if response.get("response_status") != "success":
            err = response.get("error_message") or response.get("error_code") or "Fondy checkout failed"
            raise PaymentProviderError(str(err))
        checkout_url = response.get("checkout_url")
        if not checkout_url:
            raise PaymentProviderError("Fondy не повернув checkout_url.")
        return {
            "provider": self.code,
            "checkout_url": checkout_url,
            "order_id": payment.order_reference,
        }

    def verify_webhook(self, request) -> dict:
        data = request.data if hasattr(request, "data") else json.loads(request.body)
        inner = data.get("order", data)
        received_sig = inner.get("signature") or data.get("signature")
        if received_sig:
            expected = _fondy_sign(inner)
            if received_sig != expected:
                raise PaymentProviderError("Невалідний Fondy signature.")
        status_map = {"approved": "paid", "declined": "failed"}
        return {
            "order_reference": inner.get("order_id"),
            "status": status_map.get(inner.get("order_status"), "pending"),
            "external_id": str(inner.get("payment_id", "")),
            "payload": data,
        }


PROVIDERS = {
    "liqpay": LiqPayProvider(),
    "wayforpay": WayForPayProvider(),
    "fondy": FondyProvider(),
    "stub": StubPaymentProvider(),
}

PROVIDER_PRIORITY = ("liqpay", "wayforpay", "fondy")


def list_available_providers() -> list[dict]:
    items = []
    configured_any = False
    for code in PROVIDER_PRIORITY:
        provider = PROVIDERS[code]
        ok = provider.is_configured()
        configured_any = configured_any or ok
        items.append(
            {
                "code": code,
                "label": provider.label,
                "configured": ok,
                "default": False,
            }
        )

    if settings.PAYMENTS_STUB_MODE and not configured_any:
        return [
            {
                "code": "stub",
                "label": PROVIDER_LABELS["stub"],
                "configured": True,
                "default": True,
            },
            *items,
        ]

    if not configured_any:
        return [
            {
                "code": "stub",
                "label": PROVIDER_LABELS["stub"],
                "configured": True,
                "default": True,
            }
        ]

    default_code = (
        "liqpay"
        if any(i["code"] == "liqpay" and i["configured"] for i in items)
        else next(i["code"] for i in items if i["configured"])
    )
    for item in items:
        if item["configured"]:
            item["default"] = item["code"] == default_code
    return [i for i in items if i["configured"]]


def get_webhook_provider(name: str) -> BasePaymentProvider:
    provider = PROVIDERS.get(name)
    if not provider:
        raise PaymentProviderError(f"Невідомий провайдер {name}.")
    if name == "stub":
        return provider
    if not provider.is_configured():
        raise PaymentProviderError(f"Провайдер {name} не налаштовано.")
    return provider


def get_provider(name: str) -> BasePaymentProvider:
    if settings.PAYMENTS_STUB_MODE:
        return PROVIDERS["stub"]
    provider = PROVIDERS.get(name)
    if not provider or not provider.is_configured():
        raise PaymentProviderError(f"Провайдер {name} не налаштовано.")
    return provider


def new_order_reference() -> str:
    return f"PP-{uuid.uuid4().hex[:16].upper()}"
