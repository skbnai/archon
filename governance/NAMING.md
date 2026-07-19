# Naming Convention

- Files: `NN-kebab-case.md` (NN = 2-digit reading order in folder). Hubs: `index.md`.
- Folders: `kebab-case`, max depth 3 under docs/.
- **Numbering overflow:** if a domain's flat `00`-`99` range is fully allocated,
  do NOT go to a 3+ digit prefix (`100-...md` is invalid — CI rejects it).
  Instead create one topically-named subfolder under the domain (e.g.
  `docs/strategy/vols/`, `docs/strategy/quantum/`) and restart `NN` at `01`
  inside it — still within the max-depth-3 limit. Register the new canonical
  path via the librarian before any file is written there.
- FORBIDDEN anywhere (hook + CI enforced): `_v2 _final _new _old _copy _backup
  -old -copy -final -updated (1)` and dates/author names in filenames.
- Versioning of content = git history + frontmatter (`supersedes`, `last_reviewed`,
  `covers_version`). Never filenames.
- ADRs: `docs/architecture/adr/adr-NNN-kebab-title.md` (NNN monotonic).
- topic_id in registry: kebab-case noun phrase, stable forever (rename the file,
  keep the id).
