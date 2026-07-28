"""Bounded extraction of evidenced operations from supplied Markdown or HTML."""
from __future__ import annotations

from html.parser import HTMLParser
import re
from typing import Any

MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
MAX_OPERATIONS = 500


class DocumentError(ValueError):
    """User-safe error for document extraction."""


_OPERATION_RE = re.compile(
    r"(?<![A-Za-z])(?P<method>GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(?P<path>(?:https?://[^\s<>]+|/[^\s<>`'\")]+))"
)
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_SECRET_RE = re.compile(r"\b(?:sk|api[_-]?key|token)[_-][A-Za-z0-9_-]{8,}\b", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]*>")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return "\n".join(self.parts)


def _redact(text: str) -> str:
    text = _TAG_RE.sub("", text)
    text = _EMAIL_RE.sub("[REDACTED]", text)
    return _SECRET_RE.sub("[REDACTED]", text)


def _document_text(content: str, source_kind: str) -> str:
    if source_kind == "markdown":
        return content
    if source_kind == "html":
        parser = _TextExtractor()
        parser.feed(content)
        parser.close()
        return parser.text()
    raise DocumentError("document source kind must be markdown or html")


def extract_operations(content: str, *, source_kind: str) -> list[dict[str, Any]]:
    """Extract only explicit METHOD + path candidates from supplied content.

    Every candidate retains redacted local evidence and requires an approval
    receipt; confidence is deliberately not treated as an authorization grant.
    """
    if not isinstance(content, str):
        raise DocumentError("document input must be text")
    if len(content.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"document exceeds {MAX_DOCUMENT_BYTES} byte limit")
    text = _document_text(content, source_kind)
    operations: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in _OPERATION_RE.finditer(line):
            method = match.group("method")
            path = match.group("path").rstrip(".,;:")
            key = (method, path)
            if key in seen:
                continue
            seen.add(key)
            operations.append({
                "method": method,
                "path": path,
                "confidence": "explicit",
                "requires_confirmation": True,
                "evidence": {"line": line_number, "snippet": _redact(line.strip())[:512]},
            })
            if len(operations) > MAX_OPERATIONS:
                raise DocumentError("document exceeds operation extraction limit")
    return operations
