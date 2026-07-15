"""Акцент у CMS без HTML: *курсив* → <em>курсив</em>."""

import re

_EM_TAG_RE = re.compile(r"<em>(.*?)</em>", re.IGNORECASE | re.DOTALL)
_MARKER_RE = re.compile(r"\*([^*]+)\*")


def html_to_markers(text: str) -> str:
    if not text:
        return ""
    return _EM_TAG_RE.sub(r"*\1*", text)


def markers_to_html(text: str) -> str:
    if not text:
        return ""
    return _MARKER_RE.sub(r"<em>\1</em>", text)
