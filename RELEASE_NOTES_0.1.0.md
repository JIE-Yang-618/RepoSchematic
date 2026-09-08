# RepoSchematic 0.1.0

The first public release establishes the deterministic local repository-mapping core.

## Highlights

- One-command repository analysis producing three human/agent-readable Markdown documents plus JSON graph data.
- Python AST analysis and optional Tree-sitter parsing for JavaScript/TypeScript.
- Evidence-backed entry points and structural file ranking.
- Incremental SHA-256 cache.
- Git-aware discovery and local-only privacy model.
- CLI commands for repository orientation, file explanation, dependencies, entry points, statistics and diagnostics.

## Install from source

```bash
python -m pip install .
reposchematic doctor .
reposchematic analyze .
```

Optional JS/TS AST support:

```bash
python -m pip install ".[treesitter]"
```

## Known limitations

v0.1.0 does not perform full type inference, runtime tracing, semantic/vector search, cloud AI explanation, or symbol-level call-graph resolution. See `docs/LIMITATIONS.md`.
