# Enterprise AI Wiki — Project Constitution

You are working on a professional-grade enterprise AI knowledge wiki. This file is
loaded every session. Keep behavior aligned with it at all times.

## Non-negotiables (also enforced by hooks/CI — you cannot bypass them)

1. **One canonical page per topic.** Before creating ANY file under `docs/`, the
   topic must exist in `governance/CANONICAL_REGISTRY.yaml`. If it doesn't, ask the
   librarian agent to register it first. Never work around a blocked write by
   choosing a different filename.
2. **Never version via filenames.** No `_v2`, `_final`, `_new`, `_old`, `_copy`,
   `(1)`, `-updated`. Updates happen IN PLACE on the canonical file. History lives
   in git, provenance lives in frontmatter (`supersedes`, `last_reviewed`).
3. **Replacing means superseding.** If new content replaces an old page: update the
   canonical page, set the old one to `status: superseded` with a pointer, update
   the registry — all in the same change. Keeping both as "current" is a defect.
4. **Every page is typed.** Frontmatter must match a type in
   `governance/DOC_TYPES.md`. The validator hook rejects untyped pages.
5. **Ground before you write.** Any factual/technical claim about products, specs,
   standards, or versions must be verified via the `research-grounding` skill and
   cited. No claims from memory for anything that changes.
6. **Search before you create — the graph, not just the registry.** Before
   registering a genuinely new topic, run `graphify`'s `query_graph.py
   --related` / `--concept` / `--topic` against the corpus. A registry miss is
   necessary but not sufficient proof a topic is new; a high `similar_to` edge
   to an existing page is the stronger signal and means enhance, not create.

## Token discipline

- Delegate bulk reading (old-repo files, long web research) to subagents; bring
  back summaries, not raw content.
- Operate on manifests (`migration/inventory.csv`, `CANONICAL_REGISTRY.yaml`)
  instead of re-reading the corpus.
- Read only the files you need; use the registry to find them.
- Do not restate rules from this file in your outputs; just follow them.

## Site & navigation

`docusaurus.config.js`, `sidebars.js`, and `src/css/custom.css` are pre-built —
see `governance/DOCUSAURUS_SETUP.md`. The sidebar must always mirror
`governance/TAXONOMY.md`; apply `page-styling` + `governance/SIDEBAR_GUIDE.md`
to any page or navigation change.

## Layout

- `docs/` — published content only (8 domains + tracks; see `governance/TAXONOMY.md`)
- `governance/` — registry, taxonomy, doc types, naming, trusted sources
- `migration/` — inventory, mapping, merge plans (not published)
- `scripts/`, `.claude/`, `.github/` — machinery

## Naming

`NN-kebab-case.md` inside domain folders. See `governance/NAMING.md`.

## Definition of done for any content change

frontmatter valid → registry consistent → similarity check clean → links resolve →
citations present for factual claims → reviewer agent approves.
