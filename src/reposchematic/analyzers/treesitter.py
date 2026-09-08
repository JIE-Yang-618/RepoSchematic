from __future__ import annotations

from pathlib import Path

from reposchematic.models import FileRecord, ImportRef, Symbol


def available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_javascript  # noqa: F401
        import tree_sitter_typescript  # noqa: F401
        return True
    except ImportError:
        return False


class TreeSitterJavaScriptAnalyzer:
    """Optional AST-backed analyzer for JavaScript, TypeScript and TSX."""

    def supports(self, record: FileRecord) -> bool:
        return available() and record.language in {"JavaScript", "TypeScript"}

    def analyze(self, root: Path, record: FileRecord) -> FileRecord:
        from tree_sitter import Language, Parser
        import tree_sitter_javascript as tsjs
        import tree_sitter_typescript as tsts

        suffix = Path(record.path).suffix.lower()
        if record.language == "JavaScript":
            language = Language(tsjs.language())
        elif suffix == ".tsx":
            language = Language(tsts.language_tsx())
        else:
            language = Language(tsts.language_typescript())

        data = (root / record.path).read_bytes()
        tree = Parser(language).parse(data)
        frameworks: set[str] = set()

        stack = [tree.root_node]
        while stack:
            node = stack.pop()
            stack.extend(reversed(node.children))
            if node.type in {"function_declaration", "class_declaration"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = data[name_node.start_byte:name_node.end_byte].decode("utf-8", "replace")
                    kind = "class" if node.type == "class_declaration" else "function"
                    exported = node.parent is not None and node.parent.type == "export_statement"
                    record.symbols.append(Symbol(name, kind, node.start_point.row + 1, exported))
            elif node.type in {"lexical_declaration", "variable_declaration"}:
                for child in node.children:
                    if child.type == "variable_declarator":
                        name_node = child.child_by_field_name("name")
                        value_node = child.child_by_field_name("value")
                        if name_node and value_node and value_node.type in {"arrow_function", "function_expression"}:
                            name = data[name_node.start_byte:name_node.end_byte].decode("utf-8", "replace")
                            exported = node.parent is not None and node.parent.type == "export_statement"
                            record.symbols.append(Symbol(name, "function", node.start_point.row + 1, exported))
            elif node.type in {"import_statement", "call_expression"}:
                target = _extract_module_target(node, data)
                if target:
                    record.imports.append(ImportRef(target, node.start_point.row + 1))
                    _framework(target, frameworks)

        # deduplicate imports emitted by nested traversal patterns
        seen: set[tuple[str, int | None]] = set()
        deduped = []
        for item in record.imports:
            key = (item.target, item.line)
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        record.imports = deduped
        record.frameworks = sorted(frameworks)
        record.parse_status = "ok-tree-sitter"
        record.parse_message = "AST-backed analysis via Tree-sitter."
        return record


def _extract_module_target(node, data: bytes) -> str | None:
    if node.type == "import_statement":
        for child in node.children:
            if child.type == "string":
                return _unquote(data[child.start_byte:child.end_byte].decode("utf-8", "replace"))
    if node.type == "call_expression":
        fn = node.child_by_field_name("function")
        args = node.child_by_field_name("arguments")
        if fn and args:
            fn_text = data[fn.start_byte:fn.end_byte].decode("utf-8", "replace")
            if fn_text == "require":
                for child in args.children:
                    if child.type == "string":
                        return _unquote(data[child.start_byte:child.end_byte].decode("utf-8", "replace"))
    return None


def _unquote(value: str) -> str:
    return value[1:-1] if len(value) >= 2 and value[0] in {'"', "'", "`"} and value[-1] == value[0] else value


def _framework(target: str, out: set[str]) -> None:
    mapping = {
        "react": "React", "next": "Next.js", "vue": "Vue", "express": "Express",
        "fastify": "Fastify", "@nestjs": "NestJS", "vite": "Vite", "typescript": "TypeScript",
    }
    for prefix, label in mapping.items():
        if target == prefix or target.startswith(prefix + "/"):
            out.add(label)
