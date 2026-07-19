---
name: doc-standards
description: >
  Use when writing, migrating, splitting, or reviewing any wiki page. Defines
  document types, frontmatter schema, page anatomy, size limits, naming, and
  linking rules. Templates for each doc type are in ./templates/.
---

# Documentation Standards

## Document types (full schema: governance/DOC_TYPES.md)

concept · guide · reference-architecture · pattern · anti-pattern · decision (ADR)
· runbook · checklist · research-report · case-study · learning-path · hub ·
template-asset · glossary

Pick exactly one `doc_type`. Type determines the template (see `./templates/`).
Apply the `page-styling` skill for voice, structure, and Docusaurus components.

## Frontmatter (required on every page)

```yaml
---
title: ""
doc_type: guide            # one of the types above
domain: trust              # one of the 8 domains (governance/TAXONOMY.md)
status: current            # draft | current | superseded | deprecated
canonical: true            # exactly one true per registry topic
topic_id: mcp-security     # must exist in CANONICAL_REGISTRY.yaml
maturity: practitioner     # CLOSED ENUM — exactly one of: foundational | practitioner | expert.
                           # Not free text — "current"/"proven"/"mature"/"research"/etc. all fail validation.
personas: [architect, security]
last_reviewed: 2026-07-18
covers_version: ""         # required for versioned subjects
supersedes: []             # old-repo paths or prior pages this replaces
sources: []                # required for research-report; see research-grounding
tags: []                   # from controlled vocabulary only
---
```

## Page anatomy & size

- ≤ ~2,000 words. Larger topic → split into a series with a hub/index page.
- When authoring a split plan, budget each part to ~1,600-1,800 words, not
  right up to the ceiling — a part that looks fine on paper can land over
  2,000 once real prose is written, forcing a mid-migration re-split (extra
  registry entry, renumbered files, relinking). Leave headroom instead.
- Order: 1-paragraph "why this matters" → body → "Related" links (canonical
  pages only) → sources.
- Architecture content MUST include a Mermaid diagram (see diagram-standards).
- Link via relative paths to canonical pages; never deep-link a superseded page.

## Linking (get this wrong and the build breaks silently until CI)

Links are relative to the *linking file's own directory* — never repeat the
domain folder you're already inside, never use a site-root-absolute path.

- Right, from another file inside `docs/strategy/`: `[Title](12-other-page.md)`
- Wrong: `[Title](docs/strategy/12-other-page.md)` — repeats the folder you're
  already in; resolves to a nonexistent nested path.
- Wrong: `[Title](/docs/strategy/12-other-page)` — root-absolute AND missing
  `.md`; neither survives the Docusaurus build.
- From a numbering-overflow subfolder (see Naming) back to a parent-folder
  page: `[Title](../12-other-page.md)` — the `../` is required, easy to miss.

After writing/migrating a batch, resolve every relative `.md` link against
the filesystem before calling it done — don't eyeball it.

## Naming

`NN-kebab-case.md`; NN = reading order within folder. No dates, versions,
or author names in filenames. When a domain's `00`-`99` range is full, see
`governance/NAMING.md`'s numbering-overflow rule (subfolder + restart at 01
— never a 3+ digit prefix).
