# AGENTS.md

## Project purpose

RepoSchematic is a local-first, deterministic repository understanding CLI. Preserve the core promise: static evidence before AI-generated explanation.

## Engineering constraints

- Python 3.10+.
- No mandatory runtime dependencies in the core.
- Do not execute analyzed repository code.
- No telemetry, cloud requirement, account, or API key in the core.
- Python analysis should use `ast`; JS/TS may use optional Tree-sitter with a safe fallback.
- New analyzers must fail gracefully.
- `.reposchematic/` is local state and must not be recursively analyzed.
- Generated documents must not copy large source bodies or secret values.

## Verification

Run before shipping:

```bash
pytest
python scripts/smoke_test.py
```
