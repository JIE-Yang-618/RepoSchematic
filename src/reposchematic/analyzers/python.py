from __future__ import annotations

import ast
from pathlib import Path

from reposchematic.models import FileRecord, ImportRef, Symbol


class PythonAnalyzer:
    def supports(self, record: FileRecord) -> bool:
        return record.language == "Python"

    def analyze(self, root: Path, record: FileRecord) -> FileRecord:
        path = root / record.path
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=record.path)
        except (SyntaxError, ValueError, RecursionError, MemoryError) as exc:
            record.parse_status = "error"
            record.parse_message = str(exc)
            return record

        frameworks: set[str] = set()
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                record.symbols.append(Symbol(node.name, "function", node.lineno, exported=not node.name.startswith("_")))
            elif isinstance(node, ast.ClassDef):
                record.symbols.append(Symbol(node.name, "class", node.lineno, exported=not node.name.startswith("_")))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    record.imports.append(ImportRef(alias.name, node.lineno))
                    _framework_from_import(alias.name, frameworks)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                prefix = "." * node.level
                target = prefix + module
                record.imports.append(ImportRef(target, node.lineno, "from"))
                _framework_from_import(module, frameworks)
            elif isinstance(node, ast.Call):
                name = _call_name(node.func)
                if name:
                    calls.add(name)
                    lowered = name.lower()
                    if lowered.endswith("fastapi"):
                        frameworks.add("FastAPI")
                    elif lowered.endswith("flask"):
                        frameworks.add("Flask")
                    elif lowered.endswith("typer"):
                        frameworks.add("Typer")

        record.calls = sorted(calls)
        record.frameworks = sorted(frameworks)
        record.parse_status = "ok"
        return record


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = _call_name(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    return None


def _framework_from_import(module: str, out: set[str]) -> None:
    top = module.split(".", 1)[0].lower()
    mapping = {
        "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "typer": "Typer",
        "click": "Click", "pytest": "pytest", "numpy": "NumPy", "pandas": "pandas",
        "torch": "PyTorch", "tensorflow": "TensorFlow", "sqlalchemy": "SQLAlchemy",
    }
    if top in mapping:
        out.add(mapping[top])
