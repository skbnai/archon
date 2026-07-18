---
title: "How This Wiki Governs Itself"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: wiki-governance
maturity: foundational
personas: [architect, contributor]
last_reviewed: 2026-07-18
covers_version: ""
supersedes: []
sources: []
tags: [governance, registry, hooks, ci, doc-types, freshness]
---

Every page in this wiki exists because a machine, not a convention, allows it to
exist. This page explains that machinery — the registry, the hooks, the CI
gates, the document types, and the freshness SLAs — so a contributor can
predict what will be blocked before they try it.

## Prerequisites

- Read `AGENTS.md` (the project constitution) and `governance/TAXONOMY.md`
  before writing any page.
- Know your topic's `doc_type` from `governance/DOC_TYPES.md`.

## Steps

### 1. One canonical page per topic — the registry

`governance/CANONICAL_REGISTRY.yaml` is the single source of truth mapping a
`topic_id` to exactly one canonical file path. The **librarian** agent is the
only role permitted to edit it. Before any new page under `docs/` can be
written, its topic must already have an entry here — id, domain, canonical
path, aliases, and (if replacing old content) `supersedes`.

### 2. The write-time guard — PreToolUse hook

`.claude/hooks/guard_write.py` runs on every `Write`/`Edit`/`MultiEdit` call
and blocks (exit code 2) two things before they ever touch disk:

- **Versioned/duplicate filenames** — patterns like `_v2`, `_final`, `_old`,
  `-copy`, `(1)` anywhere in the repo. Updates happen in place; history lives
  in git and in frontmatter (`supersedes`, `last_reviewed`), never in the
  filename.
- **Unregistered new pages** — any new `.md` under `docs/` whose path is not
  already listed in the registry's `canonical` or `pages` entries.

### 3. The write-time check — PostToolUse validator

`.claude/hooks/validate_page.py` runs immediately after a page is written and
calls `scripts/validate_frontmatter.py` on it. It rejects (exit code 2) pages
missing required frontmatter fields, using an invalid `doc_type` or `domain`,
missing `sources` on a `research-report`, missing a Mermaid diagram on a
`reference-architecture`, or exceeding the 2,600-word hard cap. The page must
be fixed before the session continues.

### 4. Document types drive everything

`governance/DOC_TYPES.md` defines 14 `doc_type` values (concept, guide,
reference-architecture, pattern, anti-pattern, decision, runbook, checklist,
research-report, case-study, learning-path, hub, template-asset, glossary).
Each carries a freshness SLA (90–365 days) and, for some types, special
requirements the validator enforces — a `research-report` needs `sources`; a
`reference-architecture` needs a Mermaid diagram and a trade-offs section.

### 5. CI as the second gate

The hooks catch problems at write time inside a session; `.github/workflows/`
re-runs the same checks (frontmatter validation, registry consistency,
dedup) on every PR, so content that somehow bypasses local hooks still
cannot merge.

### 6. Duplicate detection

`scripts/dedup_check.py` computes shingle-based Jaccard similarity between
pages. A pair at or above 0.55 similarity fails the check — the fix is to
merge into one survivor and mark the loser `status: superseded`, never to
ship both as current.

### 7. Freshness SLAs

Each `doc_type`'s SLA (see `governance/DOC_TYPES.md`) is enforced by the
**freshness-auditor** agent via `scripts/freshness_report.py`, which flags
pages whose `last_reviewed` has aged past the SLA (or past 90 days for any
page with `covers_version`). Stale pages are queued for the **researcher**
agent to re-ground, never bulk-touched.

## Verification

- `python3 scripts/registry_check.py` → registry consistent, canonical file
  for every topic exists on disk with matching `topic_id` frontmatter.
- `python3 scripts/dedup_check.py --all` → no page pair at or above the
  similarity threshold.
- `python3 scripts/validate_frontmatter.py <path>` → `OK` for any changed page.
- The **reviewer** agent's checklist (frontmatter, registry consistency,
  dedup, doc-type anatomy, citations, supersede hygiene) returns PASS before
  a PR merges.

## Related

- `governance/TAXONOMY.md` — the 11 domain/track folders and hub rule.
- `governance/DOC_TYPES.md` — full doc type schema and SLAs.
- `governance/NAMING.md` — filename and topic_id conventions.
