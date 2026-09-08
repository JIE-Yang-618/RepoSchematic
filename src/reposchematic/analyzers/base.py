from __future__ import annotations

from pathlib import Path
from typing import Protocol

from reposchematic.models import FileRecord


class Analyzer(Protocol):
    def supports(self, record: FileRecord) -> bool: ...
    def analyze(self, root: Path, record: FileRecord) -> FileRecord: ...
