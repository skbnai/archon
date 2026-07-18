# Repo Map: Source (old) → Target (new)

- **Target (this repo):** https://github.com/skbnai/archon — where this scaffold lives and where all migrated content ships.

## Old Repo Access (read-only escrow)

- Source: https://github.com/skbnai/knowledge-docs (branch: main, frozen at
  migration start — tag it `pre-migration`).
- During migration, clone it to `../knowledge-docs-old` (NOT inside this repo).
- Nothing is ever copied verbatim: every file passes through a merge plan +
  migrator transform + reviewer gate.
- After stage-04 completes, archive the old repo (GitHub archive setting) and add
  a README pointer to the new wiki.
