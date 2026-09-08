# Contributing

Thanks for helping improve RepoSchematic.

## Good first contributions

- Add a small fixture repository that exposes a parser edge case.
- Improve import resolution without executing target code.
- Add tests for Windows/macOS/Linux path behavior.
- Correct documentation where behavior and docs disagree.
- Add a language analyzer only when it can degrade gracefully if optional dependencies are unavailable.

## Development setup

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python scripts/smoke_test.py
```

Optional JavaScript/TypeScript AST support:

```bash
python -m pip install -e ".[dev,treesitter]"
pytest
```

## Pull requests

Keep changes focused. Add or update tests for behavior changes. Do not introduce network calls, telemetry, account requirements, or mandatory LLM dependencies into the core without an explicit design discussion.

Generated files under `.reposchematic/` should not be committed.
