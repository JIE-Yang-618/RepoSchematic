# Privacy

RepoSchematic v0.1.0 is local-only.

## What leaves the machine

Nothing from the core analyzer. There are no network requests, telemetry calls, user accounts, hosted backends, or API-key integrations.

## What is read

RepoSchematic may read eligible text files inside the target repository up to the configured size limit. In a Git repository it prefers Git's tracked/untracked file listing so `.gitignore` exclusions are respected.

## What is stored

`.reposchematic/cache.json` stores structural analysis keyed by file hash. `repo.json` and `graph.json` store the generated repository model. The generated Markdown files contain paths, symbols, import relationships, evidence, ranking reasons, and project metadata.

## Secret handling

Common credential paths and private-key extensions are excluded before parsing. RepoSchematic does not intentionally include source-code bodies in its generated context documents.

This does not guarantee that generated metadata is non-sensitive. Private filenames, symbol names, dependency names, or architecture can themselves be confidential. Review outputs before publishing analysis of a private codebase.
