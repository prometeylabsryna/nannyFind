from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

_ATTACH_SALT = "messaging.chat.attachment"
_ATTACH_MAX_AGE = 60 * 60 * 12  # 12 hours


def make_attachment_token(message_id) -> str:
    return TimestampSigner(salt=_ATTACH_SALT).sign(str(message_id))


def verify_attachment_token(token: str, message_id, max_age: int = _ATTACH_MAX_AGE) -> bool:
    if not token:
        return False
    try:
        value = TimestampSigner(salt=_ATTACH_SALT).unsign(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return False
    return value == str(message_id)
