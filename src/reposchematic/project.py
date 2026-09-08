from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG = """# RepoSchematic project configuration\nmax_file_bytes = 1000000\nuse_cache = true\n# ignore_dirs = [\"vendor\", \"generated\"]\n"""

@dataclass(slots=True)
class ProjectOptions:
    max_file_bytes: int = 1_000_000
    use_cache: bool = True
    ignore_dirs: set[str] = field(default_factory=set)


def load_project_options(root: Path) -> ProjectOptions:
    path = root / ".reposchematic.toml"
    if not path.exists():
        return ProjectOptions()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return ProjectOptions()
    max_bytes = data.get("max_file_bytes", 1_000_000)
    use_cache = data.get("use_cache", True)
    ignore_dirs = data.get("ignore_dirs", [])
    if not isinstance(max_bytes, int) or max_bytes < 1:
        max_bytes = 1_000_000
    if not isinstance(use_cache, bool):
        use_cache = True
    if not isinstance(ignore_dirs, list):
        ignore_dirs = []
    return ProjectOptions(max_bytes, use_cache, {str(x) for x in ignore_dirs if str(x).strip()})


def initialize_project(root: Path) -> list[str]:
    messages: list[str] = []
    config = root / ".reposchematic.toml"
    if not config.exists():
        config.write_text(DEFAULT_CONFIG, encoding="utf-8")
        messages.append("created .reposchematic.toml")
    state = root / ".reposchematic"
    state.mkdir(exist_ok=True)
    messages.append("local state directory ready")
    _exclude_local_state(root)
    if (root / ".git").exists():
        messages.append("excluded .reposchematic/ from local Git tracking")
    return messages


def _exclude_local_state(root: Path) -> None:
    exclude = root / ".git" / "info" / "exclude"
    if not exclude.parent.exists():
        return
    try:
        text = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
        marker = ".reposchematic/"
        if marker not in {line.strip() for line in text.splitlines()}:
            with exclude.open("a", encoding="utf-8") as f:
                if text and not text.endswith("\n"):
                    f.write("\n")
                f.write("\n# RepoSchematic local analysis state\n.reposchematic/\n")
    except OSError:
        pass
