# Architecture

RepoSchematic separates repository facts from presentation so that CLI output, Markdown, JSON, and future integrations can share one model.

```text
Repository
   │
   ├─ Git-aware discovery
   └─ filesystem fallback
   │
   ▼
FileRecord[]
   │
   ▼
Language analyzers
   ├─ Python AST
   ├─ optional JS/TS Tree-sitter
   └─ conservative JS/TS fallback
   │
   ▼
Symbols + imports + framework hints
   │
   ├─ manifest metadata / entry points
   └─ internal import resolution
   │
   ▼
RepositoryModel
   ├─ Edge[]
   ├─ EntryPoint[] + evidence/confidence
   ├─ RankedFile[]
   ├─ tech stack
   └─ stats / warnings
   │
   ▼
Renderers
   ├─ REPO_MAP.md
   ├─ ARCHITECTURE.md
   ├─ AI_CONTEXT.md
   ├─ repo.json
   └─ graph.json
```

## Design choices

### MCP/AI is not the core

The repository model is independent from any agent protocol or LLM. A future MCP adapter can query the model without making the analyzer itself dependent on MCP.

### Static analysis does not execute the target

RepoSchematic parses text and manifests. It does not import target Python modules, run package scripts, or evaluate repository configuration as code.

### Confidence is explicit

A `pyproject.toml` console-script declaration is high-confidence entry-point evidence. A conventional filename such as `main.py` is weaker and is marked medium confidence.

### Cache is an optimization, not truth

Each file receives a SHA-256 content hash. Cached structural results are reused only when that hash matches. Deleting `.reposchematic/cache.json` simply causes a clean reanalysis.

### Local state is separable from shareable output

`.reposchematic/` contains machine state and is intended to stay local. Markdown outputs at the repository root are intentionally easy to inspect, diff, copy into an agent, or commit when the user chooses.
