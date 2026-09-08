from __future__ import annotations

import re
from pathlib import Path

from reposchematic.models import FileRecord, ImportRef, Symbol

_IMPORT_RE = re.compile(r"(?:import\s+(?:[^'\"]+?\s+from\s+)?|require\s*\(\s*)['\"]([^'\"]+)['\"]")
_EXPORT_FUNC_RE = re.compile(r"\b(export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)")
_CLASS_RE = re.compile(r"\b(export\s+)?class\s+([A-Za-z_$][\w$]*)")
_ARROW_RE = re.compile(r"\b(export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")


class JavaScriptAnalyzer:
    """Conservative JS/TS analyzer.

    When optional Tree-sitter packages are installed, RepoSchematic records that stronger parser
    capability in diagnostics. The v0.1 extractor intentionally keeps a conservative lexical
    fallback so the tool remains dependency-free by default.
    """

    def supports(self, record: FileRecord) -> bool:
        return record.language in {"JavaScript", "TypeScript"}

    def analyze(self, root: Path, record: FileRecord) -> FileRecord:
        text = (root / record.path).read_text(encoding="utf-8", errors="replace")
        frameworks: set[str] = set()
        for match in _IMPORT_RE.finditer(text):
            target = match.group(1)
            line = text.count("\n", 0, match.start()) + 1
            record.imports.append(ImportRef(target, line))
            _framework(target, frameworks)
        for regex, kind in [(_EXPORT_FUNC_RE, "function"), (_CLASS_RE, "class"), (_ARROW_RE, "function")]:
            for match in regex.finditer(text):
                exported = bool(match.group(1))
                name = match.group(2)
                line = text.count("\n", 0, match.start()) + 1
                record.symbols.append(Symbol(name, kind, line, exported))
        record.frameworks = sorted(frameworks)
        record.parse_status = "ok-fallback"
        record.parse_message = "Conservative JS/TS lexical analysis; install the treesitter extra for future parser enhancements."
        return record


def _framework(target: str, out: set[str]) -> None:
    top = target.split("/", 1)[0]
    mapping = {
        "react": "React", "next": "Next.js", "vue": "Vue", "express": "Express",
        "fastify": "Fastify", "@nestjs": "NestJS", "vite": "Vite", "typescript": "TypeScript",
    }
    for prefix, label in mapping.items():
        if target == prefix or target.startswith(prefix + "/"):
            out.add(label)
