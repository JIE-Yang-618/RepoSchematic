from __future__ import annotations

from collections import Counter, defaultdict

from .models import Edge, EntryPoint, FileRecord, RankedFile


def rank_files(files: list[FileRecord], edges: list[Edge], entry_points: list[EntryPoint]) -> list[RankedFile]:
    incoming = Counter(e.target for e in edges)
    outgoing = Counter(e.source for e in edges)
    entry_paths = {e.path for e in entry_points}
    result: list[RankedFile] = []
    for f in files:
        score = 0.0
        reasons: list[str] = []
        if f.path in entry_paths:
            score += 7
            reasons.append("declared or conventional entry point")
        if incoming[f.path]:
            amount = min(6, incoming[f.path] * 1.5)
            score += amount
            reasons.append(f"imported by {incoming[f.path]} file(s)")
        if outgoing[f.path]:
            score += min(3, outgoing[f.path] * 0.5)
            reasons.append(f"connects to {outgoing[f.path]} internal module(s)")
        if f.symbols:
            score += min(2, len(f.symbols) * 0.2)
            reasons.append(f"defines {len(f.symbols)} symbol(s)")
        if f.category == "config":
            score += 2
            reasons.append("project configuration")
        if f.category == "test":
            score -= 1
        if f.category == "docs":
            score -= 1.5
        level = "critical" if score >= 9 else "high" if score >= 5 else "medium" if score >= 2 else "supporting"
        result.append(RankedFile(f.path, round(score, 2), level, reasons[:4]))
    return sorted(result, key=lambda x: (-x.score, x.path))


def tech_stack(files: list[FileRecord], external_deps: set[str]) -> list[str]:
    labels: set[str] = set()
    langs = Counter(f.language for f in files if f.language not in {"Other", "Markdown", "JSON", "TOML", "YAML"})
    labels.update(lang for lang, count in langs.items() if count)
    for f in files:
        labels.update(f.frameworks)
    dep_map = {
        "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "pytest": "pytest",
        "react": "React", "next": "Next.js", "express": "Express", "typescript": "TypeScript",
        "vite": "Vite", "sqlalchemy": "SQLAlchemy", "pandas": "pandas", "numpy": "NumPy",
    }
    for dep in external_deps:
        key = dep.lower()
        if key in dep_map:
            labels.add(dep_map[key])
    return sorted(labels)


def summarize_stats(files: list[FileRecord], edges: list[Edge], entry_points: list[EntryPoint], *, cached: int, changed: int, skipped: int) -> dict:
    by_lang = Counter(f.language for f in files)
    by_category = Counter(f.category for f in files)
    return {
        "files": len(files),
        "edges": len(edges),
        "entry_points": len(entry_points),
        "symbols": sum(len(f.symbols) for f in files),
        "languages": dict(sorted(by_lang.items())),
        "categories": dict(sorted(by_category.items())),
        "cached_files": cached,
        "reanalyzed_files": changed,
        "skipped_files": skipped,
    }


def reverse_dependencies(edges: list[Edge]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        out[edge.target].append(edge.source)
    return {k: sorted(v) for k, v in out.items()}
