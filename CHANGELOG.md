# Changelog

All notable changes to RepoSchematic are documented here.

## 0.1.0 — 2026-09-08

Initial public release.

### Added

- Git-aware repository discovery with conservative filesystem fallback.
- Sensitive-path, binary-file, generated-output, and oversized-file exclusions.
- Python AST extraction for functions, classes, imports, and calls.
- JavaScript/TypeScript conservative analysis with optional Tree-sitter AST support.
- Internal import graph for Python and local JavaScript/TypeScript modules.
- Evidence-backed entry-point detection from `pyproject.toml`, `package.json`, and conventions.
- Structural file importance ranking.
- Incremental SHA-256 analysis cache.
- `REPO_MAP.md`, `ARCHITECTURE.md`, `AI_CONTEXT.md`, `repo.json`, and `graph.json` outputs.
- `init`, `scan`, `analyze`, `map`, `explain`, `deps`, `entrypoints`, `stats`, and `doctor` CLI commands.
- Local project configuration through `.reposchematic.toml`.
- Test suite, smoke test, GitHub Actions, security policy, architecture and privacy documentation.
