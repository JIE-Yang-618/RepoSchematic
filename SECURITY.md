# Security Policy

## Scope

RepoSchematic reads repository metadata and source structure. It does not intentionally execute analyzed repository code.

The v0.1.0 core makes no network calls and requires no credentials.

## Built-in guardrails

RepoSchematic excludes common secret locations such as `.env`, private-key formats, credential directories, binary files, and oversized files. Generated context documents contain structural metadata rather than copied source bodies.

These guardrails reduce accidental disclosure; they are not a substitute for a dedicated secret scanner.

## Reporting a vulnerability

Please report security problems privately to the repository owner when a private reporting channel is available. Avoid opening a public issue containing credentials, exploit details that endanger users, or private repository content.

## Untrusted repositories

RepoSchematic does not import or execute target modules, but parsers still consume untrusted text. Extremely pathological source files may stress parser memory or recursion limits. File-size limits are enabled by default; analyze untrusted repositories with ordinary OS-level caution.
