from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import ScanConfig
from .discovery import discover
from .intelligence import reverse_dependencies
from .renderers import render_repo_map, write_outputs
from .project import initialize_project, load_project_options
from .service import analyze_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reposchematic",
        description="Build evidence-backed maps of unfamiliar code repositories.",
    )
    parser.add_argument("--version", action="version", version=f"RepoSchematic {__version__}")
    sub = parser.add_subparsers(dest="command")

    scan = sub.add_parser("scan", help="Discover files without performing static analysis.")
    scan.add_argument("path", nargs="?", default=".")
    scan.add_argument("--json", action="store_true", dest="as_json")
    scan.add_argument("--max-file-bytes", type=int, default=None)

    analyze = sub.add_parser("analyze", help="Analyze a repository and generate RepoSchematic outputs.")
    analyze.add_argument("path", nargs="?", default=".")
    analyze.add_argument("--no-cache", action="store_true")
    analyze.add_argument("--json", action="store_true", dest="as_json")
    analyze.add_argument("--max-file-bytes", type=int, default=None)

    init = sub.add_parser("init", help="Create local RepoSchematic state and run an initial analysis.")
    init.add_argument("path", nargs="?", default=".")

    map_cmd = sub.add_parser("map", help="Print the repository map to stdout.")
    map_cmd.add_argument("path", nargs="?", default=".")

    explain = sub.add_parser("explain", help="Explain one file's role using static evidence.")
    explain.add_argument("file")
    explain.add_argument("--repo", default=".")
    explain.add_argument("--json", action="store_true", dest="as_json")

    deps = sub.add_parser("deps", help="Show internal dependencies for a file.")
    deps.add_argument("file")
    deps.add_argument("--repo", default=".")

    entry = sub.add_parser("entrypoints", help="List detected repository entry points.")
    entry.add_argument("path", nargs="?", default=".")

    stats = sub.add_parser("stats", help="Show repository analysis statistics.")
    stats.add_argument("path", nargs="?", default=".")
    stats.add_argument("--json", action="store_true", dest="as_json")

    doctor = sub.add_parser("doctor", help="Check whether RepoSchematic can analyze this environment.")
    doctor.add_argument("path", nargs="?", default=".")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    try:
        return _dispatch(args)
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:  # friendly CLI boundary; details stay concise
        print(f"RepoSchematic error: {exc}", file=sys.stderr)
        return 1


def _dispatch(args: argparse.Namespace) -> int:
    if args.command == "scan":
        root = _root(args.path)
        options = load_project_options(root)
        cfg = ScanConfig(root=root, max_file_bytes=args.max_file_bytes or options.max_file_bytes)
        cfg.ignore_dirs.update(options.ignore_dirs)
        result = discover(cfg)
        if args.as_json:
            print(json.dumps({
                "root": str(root), "git_mode": result.git_mode,
                "files": [{"path": f.path, "language": f.language, "size": f.size, "category": f.category} for f in result.files],
                "skipped": result.skipped,
            }, indent=2))
        else:
            print(f"RepoSchematic scan: {root}")
            print(f"Files: {len(result.files)} | Skipped: {len(result.skipped)} | Git-aware: {'yes' if result.git_mode else 'no'}")
            for f in result.files:
                print(f"{f.language:12} {f.category:8} {f.path}")
        return 0

    if args.command in {"analyze", "init"}:
        root = _root(args.path)
        if args.command == "init":
            for message in initialize_project(root):
                print(f"  {message}")
        model = analyze_repository(root, use_cache=False if getattr(args, "no_cache", False) else None, max_file_bytes=getattr(args, "max_file_bytes", None))
        outputs = write_outputs(model, root)
        if getattr(args, "as_json", False):
            print(json.dumps(model.to_dict(), indent=2))
        else:
            print(f"RepoSchematic analyzed {model.stats['files']} files in {model.name}.")
            print(f"Internal edges: {model.stats['edges']} | Entry points: {model.stats['entry_points']} | Symbols: {model.stats['symbols']}")
            print(f"Cached: {model.stats['cached_files']} | Reanalyzed: {model.stats['reanalyzed_files']} | Skipped: {model.stats['skipped_files']}")
            print("Generated:")
            for output in outputs:
                print(f"  - {output.relative_to(root)}")
        return 0

    if args.command == "map":
        model = analyze_repository(_root(args.path))
        print(render_repo_map(model))
        return 0

    if args.command == "entrypoints":
        model = analyze_repository(_root(args.path))
        if not model.entry_points:
            print("No entry points detected.")
            return 0
        for entry in model.entry_points:
            command = f" | {entry.command}" if entry.command else ""
            print(f"{entry.confidence:6} | {entry.kind:14} | {entry.path}{command}")
        return 0

    if args.command == "stats":
        model = analyze_repository(_root(args.path))
        if args.as_json:
            print(json.dumps(model.stats, indent=2, sort_keys=True))
        else:
            for key, value in model.stats.items():
                print(f"{key}: {value}")
        return 0

    if args.command == "explain":
        root = _root(args.repo)
        model = analyze_repository(root)
        target = _normalize_requested(args.file, root)
        record = next((f for f in model.files if f.path == target), None)
        if not record:
            print(f"File not found in analysis: {target}", file=sys.stderr)
            return 2
        rank = next((r for r in model.ranked_files if r.path == target), None)
        incoming = reverse_dependencies(model.edges).get(target, [])
        outgoing = [e.target for e in model.edges if e.source == target]
        payload = {
            "path": target,
            "language": record.language,
            "category": record.category,
            "importance": None if not rank else {"level": rank.level, "score": rank.score, "reasons": rank.reasons},
            "symbols": [{"name": s.name, "kind": s.kind, "line": s.line} for s in record.symbols],
            "imports_internal": outgoing,
            "imported_by": incoming,
            "frameworks": record.frameworks,
            "parse_status": record.parse_status,
        }
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"{target} — {record.language} / {record.category}")
            if rank:
                print(f"Importance: {rank.level} ({rank.score:g})")
                for reason in rank.reasons:
                    print(f"  - {reason}")
            print(f"Symbols: {', '.join(s.name for s in record.symbols[:12]) or 'none detected'}")
            print(f"Internal imports: {', '.join(outgoing) or 'none'}")
            print(f"Imported by: {', '.join(incoming) or 'none'}")
        return 0

    if args.command == "deps":
        root = _root(args.repo)
        model = analyze_repository(root)
        target = _normalize_requested(args.file, root)
        outgoing = [e for e in model.edges if e.source == target]
        incoming = [e for e in model.edges if e.target == target]
        print(f"Dependencies for {target}")
        print("Imports:")
        for e in outgoing:
            print(f"  -> {e.target}")
        if not outgoing:
            print("  (none)")
        print("Imported by:")
        for e in incoming:
            print(f"  <- {e.source}")
        if not incoming:
            print("  (none)")
        return 0

    if args.command == "doctor":
        root = _root(args.path)
        checks: list[tuple[str, bool, str]] = []
        checks.append(("repository path", root.is_dir(), str(root)))
        checks.append(("read access", _can_read(root), "directory can be listed"))
        git = (root / ".git").exists()
        checks.append(("git metadata", True, "detected" if git else "not detected (filesystem scan will be used)"))
        state = root / ".reposchematic"
        try:
            state.mkdir(exist_ok=True)
            probe = state / ".doctor"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            writable = True
        except OSError:
            writable = False
        checks.append(("local state", writable, ".reposchematic is writable" if writable else ".reposchematic is not writable"))
        try:
            result = discover(ScanConfig(root=root))
            scans = True
            detail = f"{len(result.files)} analyzable file(s), {len(result.skipped)} skipped"
        except Exception as exc:
            scans = False
            detail = str(exc)
        checks.append(("discovery", scans, detail))
        print(f"RepoSchematic {__version__} doctor")
        failed = False
        for name, ok, detail in checks:
            mark = "OK" if ok else "FAIL"
            print(f"[{mark:4}] {name}: {detail}")
            failed |= not ok
        return 1 if failed else 0

    return 0


def _root(raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"repository path is not a directory: {path}")
    return path


def _normalize_requested(raw: str, root: Path) -> str:
    p = Path(raw)
    if p.is_absolute():
        return p.resolve().relative_to(root).as_posix()
    return p.as_posix().lstrip("./")


def _can_read(root: Path) -> bool:
    try:
        next(root.iterdir(), None)
        return True
    except OSError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
