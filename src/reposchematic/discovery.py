from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG_NAMES, DEFAULT_BINARY_EXTENSIONS, GENERATED_OUTPUTS, LANGUAGE_BY_SUFFIX, ScanConfig
from .models import FileRecord, relpath
from .security import is_sensitive_path


@dataclass(slots=True)
class DiscoveryResult:
    files: list[FileRecord]
    skipped: list[str]
    git_mode: bool


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _looks_binary(path: Path) -> bool:
    if path.suffix.lower() in DEFAULT_BINARY_EXTENSIONS:
        return True
    try:
        with path.open("rb") as f:
            sample = f.read(4096)
        return b"\x00" in sample
    except OSError:
        return True


def _language(path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "Other")


def _category(path: Path) -> str:
    name = path.name.lower()
    parts = {p.lower() for p in path.parts}
    if "test" in name or "tests" in parts or "__tests__" in parts:
        return "test"
    if name in CONFIG_NAMES or name.startswith(".") and name.endswith(("rc", "json", "yaml", "yml", "toml")):
        return "config"
    if path.suffix.lower() in {".md", ".rst", ".txt"} or "docs" in parts:
        return "docs"
    return "source"


def _git_files(root: Path, include_untracked: bool) -> list[Path] | None:
    git_dir = root / ".git"
    if not git_dir.exists():
        return None
    args = ["git", "-C", str(root), "ls-files", "-z"]
    if include_untracked:
        args.extend(["--cached", "--others", "--exclude-standard"])
    try:
        out = subprocess.check_output(args, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return None
    names = [n for n in out.decode("utf-8", errors="surrogateescape").split("\x00") if n]
    return [root / n for n in names]


def discover(config: ScanConfig) -> DiscoveryResult:
    root = config.root.resolve()
    candidates = _git_files(root, config.include_untracked)
    git_mode = candidates is not None
    if candidates is None:
        candidates = []
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in config.ignore_dirs]
            cur = Path(current)
            candidates.extend(cur / name for name in files)

    records: list[FileRecord] = []
    skipped: list[str] = []
    for path in sorted(set(candidates)):
        try:
            relative = relpath(path, root)
        except Exception:
            continue
        if not path.is_file():
            continue
        if Path(relative).name in GENERATED_OUTPUTS:
            skipped.append(f"{relative}: RepoSchematic generated output")
            continue
        if any(part in config.ignore_dirs for part in Path(relative).parts):
            skipped.append(f"{relative}: ignored directory")
            continue
        if is_sensitive_path(Path(relative)):
            skipped.append(f"{relative}: sensitive path")
            continue
        try:
            size = path.stat().st_size
        except OSError:
            skipped.append(f"{relative}: unreadable")
            continue
        if size > config.max_file_bytes:
            skipped.append(f"{relative}: larger than {config.max_file_bytes} bytes")
            continue
        if _looks_binary(path):
            skipped.append(f"{relative}: binary")
            continue
        try:
            digest = _sha256(path)
        except OSError:
            skipped.append(f"{relative}: unreadable")
            continue
        records.append(FileRecord(
            path=relative,
            language=_language(path),
            size=size,
            sha256=digest,
            category=_category(Path(relative)),
        ))
    return DiscoveryResult(records, skipped, git_mode)
