"""Відправка листів через Resend (https://resend.com).

Якщо RESEND_API_KEY не задано (типово для локального develop-середовища),
лист не відправляється реально, а лише пишеться в лог — так само, як
раніше поводився django.core.mail.backends.console.EmailBackend.
"""

import logging

from django.conf import settings

logger = logging.getLogger("apps")


class EmailSendError(Exception):
    """Помилка відправки листа через Resend."""


def send_email(subject: str, to: list[str], text: str, html: str | None = None) -> None:
    if not settings.RESEND_API_KEY:
        logger.info("EMAIL (RESEND_API_KEY не задано, консольний fallback)\nTo: %s\nSubject: %s\n\n%s", to, subject, text)
        return

    import resend

    resend.api_key = settings.RESEND_API_KEY

    params: dict = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": to,
        "subject": subject,
        "text": text,
    }
    if html:
        params["html"] = html

    try:
        resend.Emails.send(params)
    except Exception as exc:
        logger.error("Resend: не вдалося відправити лист до %s: %s", to, exc)
        raise EmailSendError(str(exc)) from exc
