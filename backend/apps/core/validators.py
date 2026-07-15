import re

from django.core.exceptions import ValidationError

UA_PHONE_RE = re.compile(r"^\+380\d{9}$")


def normalize_ua_phone(value: str) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("380"):
        digits = digits[3:]
    elif digits.startswith("0"):
        digits = digits[1:]
    return f"+380{digits[:9]}"


def validate_ua_phone(value: str) -> str:
    phone = normalize_ua_phone(value)
    if not UA_PHONE_RE.fullmatch(phone):
        raise ValidationError("Формат телефону: +380XXXXXXXXX")
    return phone
