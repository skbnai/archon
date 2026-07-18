# Naming Convention

- Files: `NN-kebab-case.md` (NN = 2-digit reading order in folder). Hubs: `index.md`.
- Folders: `kebab-case`, max depth 3 under docs/.
- FORBIDDEN anywhere (hook + CI enforced): `_v2 _final _new _old _copy _backup
  -old -copy -final -updated (1)` and dates/author names in filenames.
- Versioning of content = git history + frontmatter (`supersedes`, `last_reviewed`,
  `covers_version`). Never filenames.
- ADRs: `docs/architecture/adr/adr-NNN-kebab-title.md` (NNN monotonic).
- topic_id in registry: kebab-case noun phrase, stable forever (rename the file,
  keep the id).
