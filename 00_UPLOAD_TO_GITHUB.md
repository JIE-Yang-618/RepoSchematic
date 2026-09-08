# Uploading RepoSchematic to GitHub

This directory is already laid out as a repository root.

1. Create a new empty GitHub repository named `RepoSchematic` (do not ask GitHub to add a README, license, or `.gitignore`; those already exist here).
2. Unzip the release package locally.
3. Upload or push the **contents of the `RepoSchematic/` folder** so GitHub shows `README.md`, `src/`, `tests/`, `docs/`, `.github/`, and `pyproject.toml` at the repository root.
4. Do not upload the outer ZIP file as a repository file.
5. Suggested About description: `Local-first, evidence-backed codebase maps for developers and AI coding agents.`
6. Suggested topics: `static-analysis`, `codebase`, `developer-tools`, `ai-agents`, `repository`, `architecture`, `python`, `typescript`, `local-first`.
7. After the first push, create a GitHub Release tagged `v0.1.0` and use `RELEASE_NOTES_0.1.0.md` as the release notes.

Before publishing analysis generated from a private repository, review the generated Markdown/JSON for confidential filenames, symbol names, dependencies, or architecture details.
