# Development

## Setup

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

Optional parser path:

```bash
python -m pip install -e ".[dev,treesitter]"
pytest
```

## Release checks

```bash
python scripts/smoke_test.py
python -m pip wheel . --no-deps --no-build-isolation -w dist
```

A release should also be installed into a fresh virtual environment and exercised with `--version`, `doctor`, and `analyze` before tagging.
