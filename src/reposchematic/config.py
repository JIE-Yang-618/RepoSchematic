from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv", "env",
    "node_modules", "dist", "build", "coverage", ".next", ".nuxt", ".cache",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".reposchematic",
}

DEFAULT_SECRET_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development",
    "credentials.json", "secrets.json", "service-account.json",
}

DEFAULT_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz",
    ".tar", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib", ".class", ".jar",
    ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".mov", ".avi",
    ".sqlite", ".sqlite3", ".db", ".pyc",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".mts": "TypeScript",
    ".cts": "TypeScript",
    ".tsx": "TypeScript",
    ".json": "JSON",
    ".toml": "TOML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".html": "HTML",
    ".css": "CSS",
}

GENERATED_OUTPUTS = {"REPO_MAP.md", "ARCHITECTURE.md", "AI_CONTEXT.md"}

CONFIG_NAMES = {
    "pyproject.toml", "package.json", "requirements.txt", "setup.py", "setup.cfg",
    "tox.ini", "pytest.ini", "vite.config.js", "vite.config.ts", "tsconfig.json",
    "webpack.config.js", "dockerfile", "docker-compose.yml", "docker-compose.yaml",
}

@dataclass(slots=True)
class ScanConfig:
    root: Path
    max_file_bytes: int = 1_000_000
    include_untracked: bool = True
    ignore_dirs: set[str] = field(default_factory=lambda: set(DEFAULT_IGNORE_DIRS))
