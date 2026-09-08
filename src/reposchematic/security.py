from __future__ import annotations

import re
from pathlib import Path

from .config import DEFAULT_SECRET_NAMES

_SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdb", ".jks"}
_SECRET_PATTERNS = [
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{12,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
]


def is_sensitive_path(path: Path) -> bool:
    name = path.name.lower()
    if name in DEFAULT_SECRET_NAMES:
        return True
    if path.suffix.lower() in _SECRET_SUFFIXES:
        return True
    parts = {p.lower() for p in path.parts}
    return bool(parts & {".aws", ".ssh", "secrets", "credentials"})


def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)


def safe_excerpt(text: str, limit: int = 200) -> str:
    if contains_secret(text):
        return "[redacted: potential secret]"
    compact = " ".join(text.split())
    return compact[:limit]
