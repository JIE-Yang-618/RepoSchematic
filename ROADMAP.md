# Roadmap

RepoSchematic is deliberately deterministic-first and local-first. Roadmap items are priorities, not promises.

## v0.1.x — Reliability

- Expand fixture coverage for monorepos and nested `src` layouts.
- Improve Windows/path edge cases.
- Improve error reporting for malformed manifests.
- Add more tests for Tree-sitter-enabled environments.

## v0.2 — Deeper graph intelligence

- Resolve more symbol-level relationships without executing repository code.
- Better package-root inference for Python monorepos.
- Framework-aware entry points for FastAPI, Django, Flask, Next.js, Express and Vite.
- Circular-dependency and blast-radius reporting.
- Token-budgeted `AI_CONTEXT.md` profiles.

## Later

- Additional languages where robust parsers are available.
- Optional local/bring-your-own-model explanation layer built on top of deterministic evidence.
- MCP adapter for agent-native repository queries.
- Optional interactive visualization without making a web service mandatory.

## Non-goals

RepoSchematic is not intended to become an IDE, code editor, autonomous patch generator, cloud repository host, or mandatory LLM service.
