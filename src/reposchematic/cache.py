from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import FileRecord, ImportRef, Symbol


class AnalysisCache:
    def __init__(self, root: Path) -> None:
        self.path = root / ".reposchematic" / "cache.json"
        self.data: dict[str, dict] = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                self.data = {}

    def restore(self, record: FileRecord) -> FileRecord | None:
        item = self.data.get(record.path)
        if not item or item.get("sha256") != record.sha256:
            return None
        try:
            record.symbols = [Symbol(**x) for x in item.get("symbols", [])]
            record.imports = [ImportRef(**x) for x in item.get("imports", [])]
            record.calls = list(item.get("calls", []))
            record.frameworks = list(item.get("frameworks", []))
            record.parse_status = item.get("parse_status", "cached")
            record.parse_message = item.get("parse_message")
            return record
        except (TypeError, KeyError):
            return None

    def store(self, records: list[FileRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            r.path: {
                "sha256": r.sha256,
                "symbols": [asdict(s) for s in r.symbols],
                "imports": [asdict(i) for i in r.imports],
                "calls": r.calls,
                "frameworks": r.frameworks,
                "parse_status": r.parse_status,
                "parse_message": r.parse_message,
            }
            for r in records
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
