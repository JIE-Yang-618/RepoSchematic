from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .analyzers import analyzers
from .cache import AnalysisCache
from .config import ScanConfig
from .discovery import discover
from .graph import build_edges
from .intelligence import rank_files, summarize_stats, tech_stack
from .metadata import detect_dependencies, detect_entry_points
from .models import RepositoryModel
from .project import load_project_options


def analyze_repository(root: Path, *, use_cache: bool | None = None, max_file_bytes: int | None = None) -> RepositoryModel:
    root = root.resolve()
    options = load_project_options(root)
    if use_cache is None:
        use_cache = options.use_cache
    if max_file_bytes is None:
        max_file_bytes = options.max_file_bytes
    scan_config = ScanConfig(root=root, max_file_bytes=max_file_bytes)
    scan_config.ignore_dirs.update(options.ignore_dirs)
    discovery = discover(scan_config)
    cache = AnalysisCache(root)
    cached = 0
    changed = 0

    for record in discovery.files:
        restored = cache.restore(record) if use_cache else None
        if restored is not None:
            cached += 1
            continue
        analyzer = next((a for a in analyzers() if a.supports(record)), None)
        if analyzer:
            analyzer.analyze(root, record)
            changed += 1
        else:
            record.parse_status = "metadata-only"

    cache.store(discovery.files)
    edges = build_edges(discovery.files)
    entries = detect_entry_points(root)
    deps = detect_dependencies(root)
    ranks = rank_files(discovery.files, edges, entries)
    stack = tech_stack(discovery.files, deps)
    stats = summarize_stats(discovery.files, edges, entries, cached=cached, changed=changed, skipped=len(discovery.skipped))
    warnings = []
    parse_errors = [f.path for f in discovery.files if f.parse_status == "error"]
    if parse_errors:
        warnings.append(f"{len(parse_errors)} file(s) could not be parsed: {', '.join(parse_errors[:5])}")
    if discovery.skipped:
        warnings.append(f"{len(discovery.skipped)} file(s) skipped because of ignore, size, binary, or sensitive-path rules.")
    return RepositoryModel(
        root=str(root),
        name=root.name,
        generated_at=datetime.now(timezone.utc).isoformat(),
        files=discovery.files,
        edges=edges,
        entry_points=entries,
        tech_stack=stack,
        ranked_files=ranks,
        stats=stats,
        warnings=warnings,
    )
