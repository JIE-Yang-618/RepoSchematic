from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Evidence:
    kind: str
    detail: str
    path: str | None = None
    line: int | None = None


@dataclass(slots=True)
class Symbol:
    name: str
    kind: str
    line: int | None = None
    exported: bool = False


@dataclass(slots=True)
class ImportRef:
    target: str
    line: int | None = None
    kind: str = "import"


@dataclass(slots=True)
class FileRecord:
    path: str
    language: str
    size: int
    sha256: str
    category: str = "source"
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[ImportRef] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    parse_status: str = "not_analyzed"
    parse_message: str | None = None


@dataclass(slots=True)
class Edge:
    source: str
    target: str
    relation: str
    evidence: Evidence | None = None


@dataclass(slots=True)
class EntryPoint:
    path: str
    kind: str
    command: str | None
    confidence: str
    evidence: list[Evidence] = field(default_factory=list)


@dataclass(slots=True)
class RankedFile:
    path: str
    score: float
    level: str
    reasons: list[str]


@dataclass(slots=True)
class RepositoryModel:
    root: str
    name: str
    generated_at: str
    files: list[FileRecord]
    edges: list[Edge]
    entry_points: list[EntryPoint]
    tech_stack: list[str]
    ranked_files: list[RankedFile]
    stats: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()
