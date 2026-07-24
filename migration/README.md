# migration/

This folder is non-published working space. Nothing here is a wiki page —
none of it is governed by `governance/CANONICAL_REGISTRY.yaml`, the
`doc-standards` skill, or the PreToolUse/PostToolUse hooks that gate
`docs/`. Content in `migration/` never ships directly; it only exists to
produce inputs for the `librarian`, `migrator`, and `reviewer` agents during
the old-repo migration (see `governance/MIGRATION_SOURCES.md`).

## What lives here

- `inventory.csv` — manifest of old-repo files: path, topic guess,
  duplicate-cluster id, size, last-touched. Built during stage-01/02.
- `merge-plans/` — one file per duplicate cluster, naming the survivor page,
  target canonical path, topic_id, and which old paths get folded in via
  `supersedes`. The `migrator` agent executes these; it does not write them.
  **Every row a migrator will execute — including simple 1:1 MIGRATE rows,
  not just splits — must carry an explicit source line-range (`lines: N-M`,
  or `lines: 1-<EOF>` for whole files).** The migrator refuses assignments
  without one: vague "migrate this file" scopes caused silent content
  condensing in wave 2 (as low as 15% retained), while exact-range
  transcription assignments were reliably faithful.
- `mapping.csv` — old path → new canonical path, used to rewrite internal
  links during migration.
- `refresh-queue.md` — freshness-auditor output: stale pages ranked for
  re-grounding by the `researcher` agent.

## Rules

- Nothing here is copied verbatim into `docs/`. Every old-repo file passes
  through a merge plan, a `migrator` transform, and a `reviewer` gate before
  any content reaches a canonical page.
- Files in `migration/` are exempt from the `docs/`-only hooks, but they are
  still subject to the naming rule (`governance/NAMING.md`): no versioned
  filenames here either — supersede/update in place.
- Treat this folder as scratch state for the migration project, not as an
  archive. Once stage-04 completes and the old repo is archived, this folder
  should be emptied or removed in a follow-up change — it is not meant to be
  a permanent second copy of the corpus.
