#!/usr/bin/env python3
"""Dev-сервер з чистими URL згідно карти сайту."""

from __future__ import annotations

import mimetypes
import os
import re
import socket
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(ROOT, "backend", "media")

CITY_SLUGS = {"kyiv", "lviv", "dnipro", "kharkiv"}

STATIC_ROUTES: list[tuple[str, str]] = [
    (r"^/register/?$", "register.html"),
    (r"^/login/?$", "login.html"),
    (r"^/forgot-password/?$", "forgot-password.html"),
    (r"^/reset-password/?$", "reset-password.html"),
    (r"^/how-it-works/?$", "how-it-works.html"),
    (r"^/contacts/?$", "contacts.html"),
    (r"^/services/?$", "services.html"),
    (r"^/faq/?$", "faq.html"),
    (r"^/public-offer/?$", "public-offer.html"),
    (r"^/terms-of-service/?$", "terms-of-service.html"),
    (r"^/privacy-policy/?$", "privacy-policy.html"),
    (r"^/cookie-policy/?$", "cookie-policy.html"),
    (r"^/nanny/?$", "nanny/index.html"),
    (r"^/blog/?$", "blog/index.html"),
    (r"^/cabinet/parent/?$", "cabinet/parent/index.html"),
    (r"^/cabinet/parent/search/?$", "cabinet/parent/search.html"),
    (r"^/cabinet/parent/profile/?$", "cabinet/parent/profile.html"),
    (r"^/cabinet/parent/favorites/?$", "cabinet/parent/favorites.html"),
    (r"^/cabinet/parent/chat/?$", "cabinet/parent/chat.html"),
    (r"^/cabinet/parent/payments/?$", "cabinet/parent/payments.html"),
    (r"^/cabinet/parent/reviews/?$", "cabinet/parent/reviews.html"),
    (r"^/cabinet/nanny/?$", "cabinet/nanny/index.html"),
    (r"^/cabinet/nanny/profile/?$", "cabinet/nanny/profile.html"),
    (r"^/cabinet/nanny/calendar/?$", "cabinet/nanny/calendar.html"),
    (r"^/cabinet/nanny/documents/?$", "cabinet/nanny/documents.html"),
    (r"^/cabinet/nanny/messages/?$", "cabinet/nanny/messages.html"),
    (r"^/cabinet/nanny/rating/?$", "cabinet/nanny/rating.html"),
    (r"^/admin/?$", "admin/index.html"),
    (r"^/admin/users/?$", "admin/users.html"),
    (r"^/admin/profiles/?$", "admin/profiles.html"),
    (r"^/admin/documents/?$", "admin/documents.html"),
    (r"^/admin/messages/?$", "admin/messages.html"),
    (r"^/admin/content/?$", "admin/content.html"),
    (r"^/admin/finance/?$", "admin/finance.html"),
    (r"^/admin/analytics/?$", "admin/analytics.html"),
]

DYNAMIC_ROUTES: list[tuple[str, str]] = [
    (r"^/nanny/(\d+)/?$", "nanny/profile.html"),
    (r"^/blog/([\w-]+)/?$", "blog/article.html"),
]


def resolve_path(path: str) -> str | None:
    path = path.split("?", 1)[0]
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/") or "/"

    city_match = re.match(r"^/city/([\w-]+)/?$", path)
    if city_match:
        slug = city_match.group(1)
        if slug in CITY_SLUGS:
            return f"city/{slug}.html"

    for pattern, target in DYNAMIC_ROUTES:
        if re.match(pattern, path):
            return target

    for pattern, target in STATIC_ROUTES:
        if re.match(pattern, path):
            return target

    if path.endswith(".html"):
        return path.lstrip("/")

    return None


class DualStackHTTPServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _safe_media_path(self, path: str) -> str | None:
        rel = urllib.parse.unquote(path[len("/media/") :]).lstrip("/")
        if not rel or ".." in rel.split("/"):
            return None
        target = os.path.normpath(os.path.join(MEDIA_ROOT, rel))
        root = os.path.normpath(MEDIA_ROOT)
        if target != root and not target.startswith(root + os.sep):
            return None
        return target if os.path.isfile(target) else None

    def _serve_binary(self, file_path: str) -> None:
        ctype = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        try:
            with open(file_path, "rb") as handle:
                data = handle.read()
        except OSError:
            self.send_error(404, "File not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split("?", 1)[0])
        if path.startswith("/media/"):
            media_file = self._safe_media_path(path)
            if media_file:
                self._serve_binary(media_file)
                return
            self.send_error(404, "File not found")
            return

        mapped = resolve_path(self.path)
        if mapped:
            self.path = "/" + mapped
        elif self.path.endswith("/") and self.path != "/":
            index = self.path.lstrip("/") + "index.html"
            full = os.path.join(ROOT, index)
            if os.path.isfile(full):
                self.path = "/" + index
        return super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def main():
    port = int(os.environ.get("PORT", "8082"))
    server = DualStackHTTPServer(("", port), CleanURLHandler)
    print(f"Frontend (clean URLs): http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
