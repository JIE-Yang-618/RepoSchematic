from __future__ import annotations

from pathlib import PurePosixPath
import posixpath

from .models import Edge, Evidence, FileRecord


def build_edges(files: list[FileRecord]) -> list[Edge]:
    known = {f.path for f in files}
    edges: list[Edge] = []
    seen: set[tuple[str, str, str]] = set()
    for record in files:
        for ref in record.imports:
            target = resolve_import(record.path, ref.target, known)
            if not target:
                continue
            key = (record.path, target, "imports")
            if key in seen:
                continue
            seen.add(key)
            edges.append(Edge(
                source=record.path,
                target=target,
                relation="imports",
                evidence=Evidence("import", ref.target, record.path, ref.line),
            ))
    return edges


def resolve_import(source: str, target: str, known: set[str]) -> str | None:
    src = PurePosixPath(source)
    suffix = src.suffix
    # Python relative imports
    if suffix in {".py", ".pyi"}:
        if target.startswith("."):
            dots = len(target) - len(target.lstrip("."))
            module = target[dots:]
            base = src.parent
            for _ in range(max(0, dots - 1)):
                base = base.parent
            parts = list(base.parts) + ([*module.split(".")] if module else [])
        else:
            parts = target.split(".")
            # support src layout
            candidates = [PurePosixPath(*parts), PurePosixPath("src", *parts)]
            for base in candidates:
                for c in (str(base) + ".py", str(base / "__init__.py")):
                    if c in known:
                        return c
            return None
        base = PurePosixPath(*parts)
        for c in (str(base) + ".py", str(base / "__init__.py")):
            if c in known:
                return c
        return None

    # JS/TS local imports only
    if target.startswith("."):
        base = (src.parent / target)
        raw = str(base)
        candidates = [raw]
        for ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
            candidates.append(raw + ext)
        for ext in ("js", "jsx", "ts", "tsx"):
            candidates.append(str(base / f"index.{ext}"))
        for c in candidates:
            normalized = posixpath.normpath(c)
            if normalized in known:
                return normalized
    return None
