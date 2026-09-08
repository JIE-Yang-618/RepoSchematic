# Limitations

Static analysis is useful precisely because it is cheap and reproducible, but it has boundaries.

## Dynamic behavior

RepoSchematic may miss relationships created through reflection, plugin registries, dependency injection, monkey patching, generated imports, runtime `importlib`, JavaScript dynamic imports, framework conventions, or code generation.

## Python

The Python analyzer uses `ast.parse`. It extracts syntax without executing modules. It does not perform full type inference, control-flow analysis, or symbol resolution across arbitrary packages.

## JavaScript / TypeScript

The dependency-free fallback intentionally extracts only conservative imports and common declaration forms. Install `.[treesitter]` for AST-backed parsing. Even Tree-sitter parsing does not provide a complete TypeScript type checker.

## Entry points

Manifest-declared entry points are high confidence. Filename conventions are medium-confidence navigation hints. Framework-specific route or application discovery is intentionally limited in v0.1.0.

## Importance ranking

File importance is a structural heuristic based on entry-point status, internal connectivity, symbols, category, and configuration role. It is not a measure of business importance or code quality.

## Security

RepoSchematic reduces accidental secret exposure but is not a security scanner. Do not use it as proof that a repository contains no credentials or vulnerabilities.
