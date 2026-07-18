# Merge Plan: marketplace-connector-auth-patterns

## Cluster

| old_path | words | last_reviewed | source_type | status_field | disposition |
| --- | --- | --- | --- | --- | --- |
| `docs/ai-protocols/auth/marketplace-connector-auth-patterns.md` | 1989 (per `wc -w`; mapping.csv lists 1957) | 2026-07-10 | converted-pdf | current | MIGRATE (survivor) |
| `docs/ai-security-governance/security/Part5_Marketplace_Architecture.md` | 46 | 2026-07-17 | (empty) | retired | MERGE-INTO (loser) |

- **target_topic_id:** `marketplace-connector-auth-patterns`
- **target canonical path:** `docs/protocols/03-marketplace-connector-auth-patterns.md`
- **domain:** protocols
- **wave:** 4

## Survivor

**Survivor = `docs/ai-protocols/auth/marketplace-connector-auth-patterns.md`**
(~1957–1989 words, `source_type: converted-pdf`, `last_reviewed: 2026-07-10`,
`status: current`).

Normally this migration orders candidates recency-first, and by raw timestamp
the trust-domain stub (`last_reviewed: 2026-07-17`) is *newer* than the
survivor (2026-07-10) — seven days newer. **This is a deliberate exception to
naive recency-first ordering.** Having read both files in full:

- The stub (`Part5_Marketplace_Architecture.md`) is 46 words total: front
  matter plus a single `:::caution` admonition. Its entire body reads: "This
  page was the raw PDF-conversion of Enterprise AI Authentication Research
  Part 5. The content has been fully rewritten and is now maintained at:
  **Marketplace Connector Auth Patterns → ai-protocols/auth/marketplace-connector-auth-patterns**.
  Please update any bookmarks or links."
- Its own `status: retired` field self-declares it superseded, and its body
  self-declares the survivor as the successor location by relative link
  (`../../../ai-protocols/auth/marketplace-connector-auth-patterns`) — i.e.
  the loser file itself names the survivor as canonical.
- The newer `last_reviewed` date reflects only the act of retiring the page
  and adding the redirect notice, not any content refresh. Zero substantive
  content was touched or added on 2026-07-17.

Completeness (1957+ substantive words of vendor-specific OAuth/token/consent
detail vs. 20 words of redirect prose) and structure (full marketplace-auth
anatomy — six vendor sections, four architecture patterns, lifecycle tables —
vs. a bare pointer stub) both override the stub's slightly newer timestamp.
Survivor confirmed: `docs/ai-protocols/auth/marketplace-connector-auth-patterns.md`.

## Unique-Content Map

Read the loser file in full (all 20 lines). As expected from the 46-word/
retired profile: **no unique content — safe to drop.**

- Front matter (`title`, `date_created`, `last_reviewed`, `status`,
  `supersedes: ""`, `doc_type`, `tags`) is boilerplate that duplicates fields
  already present on the survivor's own front matter.
- The body contains no facts, tables, vendor detail, or lifecycle content of
  any kind — only a redirect notice. Unlike the sibling
  `auth-standards-reference` merge, this stub does not even claim a specific
  piece of content (e.g. a glossary row) was merged forward; it makes no
  content claim at all beyond "fully rewritten, see survivor."
- Nothing from the loser needs to be carried into the target page body.

**Conclusion: drop the loser entirely**, contingent on honoring its redirect
obligation (see Transform Notes) — any link currently pointing at
`docs/ai-security-governance/security/Part5_Marketplace_Architecture.md`
must be retargeted to `docs/protocols/03-marketplace-connector-auth-patterns.md`.

## Target Structure

Survivor checked for converted-pdf damage: tables render cleanly across all
six vendor sections, numbered architecture-layer lists are intact, no stray
`\f` form-feed characters, no literal "Page N of N" footer artifacts, and no
broken/merged table cells were found. The one PDF-series leftover is the
italic byline directly under the H1: `*Enterprise AI Authentication Research
· Part 5 of 7*` — a cross-reference to a 7-part source series that no longer
exists as such in the new IA (see Transform Notes). This conversion is
cleaner than the `converted-pdf` tag alone would suggest, but a visual diff
against `archive/ai-protocols/Part5_Marketplace_Architecture.pdf` is still
recommended at migration time, since tables spanning a PDF page break are the
most common place such damage hides and was not fully verifiable from the
markdown text alone.

Proposed H2/H3 outline for `docs/protocols/03-marketplace-connector-auth-patterns.md`
(mirrors the survivor's existing structure — it is already well-organized and
does not need reorganizing, only trimming and front-matter/link conversion):

```
# Marketplace Connector Auth Patterns & Enterprise Architecture

(1-paragraph "why this matters" intro — replaces the PDF-series byline)

## Architecture overview
(Mermaid C4-style container diagram — see Transform Notes)

## Marketplace Connectors
### GitHub Marketplace
### Atlassian Marketplace
### Microsoft AppSource
### ServiceNow Store
### Google Workspace Marketplace
### AWS Marketplace

## Enterprise Architecture Patterns
### Microsoft Pattern — Copilot + Entra OBO Architecture
### Google Pattern — Gemini + Vertex AI Extensions
### AWS Pattern — Amazon Q Business + IAM Identity Center
### Atlassian Pattern — Rovo + Forge

## Token & Consent Lifecycle Patterns
### Initial Consent & Token Lifecycle
### Refresh Token Rotation Lifecycle
### Revocation Scenarios and Latency
### Token Lifecycle Best Practices

## Related
## Sources
```

**Word count / split decision:** ~1957–1989 words is under the ~2000-word
soft limit. **No split needed.** The content is one coherent topic
(marketplace connector auth across six vendor ecosystems plus the
architecture patterns built on top of them); all three major sections
reference the same underlying six vendors, so splitting by vendor or by
section would fragment a topic readers need to compare across in one place.

## Transform Notes

- **Converted-PDF artifacts to strip:** the italic `*Enterprise AI
  Authentication Research · Part 5 of 7*` byline under the H1 — references a
  7-part source series that isn't part of the new IA — replace with the
  required 1-paragraph "why this matters" lead per doc-standards page
  anatomy. No page-number artifacts, running headers/footers, or visibly
  broken tables found in the markdown, but re-check against the source PDF
  for page-break table damage before final sign-off.
- **New diagram requirement:** the four "Enterprise Architecture Patterns"
  subsections (Microsoft, Google, AWS, Atlassian) are each currently a flat
  numbered list of layers (e.g. `1. **[Identity Layer]** ... 2. **[AI
  Layer]** ...`). Per `diagram-standards`, this is exactly the kind of
  prose/pseudo-diagram content that must become a proper Mermaid C4-style
  diagram at migration time — at minimum one diagram in the new
  "Architecture overview" section, and optionally one per vendor pattern if
  the four layer-lists are kept as subsections rather than collapsed into a
  single comparative diagram. This is new work for stage-04, not present
  verbatim in the source.
- **Front matter conversion:** old fields `date_created`, `source_file`,
  `covers_through`, and `doc_type: guide` (see Doc Type section below) do not
  match the new schema and should be dropped/remapped. `supersedes` in the
  new front matter should list both old paths:
  `docs/ai-protocols/auth/marketplace-connector-auth-patterns.md` and
  `docs/ai-security-governance/security/Part5_Marketplace_Architecture.md`.
- **Links needing rewrite:** the survivor's `> **See also:**` callout links
  to `./tool-authentication-connectors` and `./auth-standards-reference`
  (old sibling-folder relative paths). Per the cluster mapping these should
  resolve under `docs/protocols/` (the `auth-standards-reference` sibling
  merge plan already targets `docs/protocols/01-auth-standards-reference.md`)
  — rewrite as relative links within `docs/protocols/` and move into the
  template's `## Related` section rather than an inline callout, consistent
  with the sibling `auth-standards-reference` merge plan's convention.
- **Redirect obligation:** any link currently pointing at
  `docs/ai-security-governance/security/Part5_Marketplace_Architecture.md`
  must be retargeted to `docs/protocols/03-marketplace-connector-auth-patterns.md`
  once the loser is dropped — this is exactly what the stub's own caution
  notice already asks readers to do.

## Doc Type & Template

Old front matter used `doc_type: guide`. Evaluated against the current
taxonomy (`governance/DOC_TYPES.md`):

- **`pattern`** (Context/Forces/Solution/Consequences) does not fit well:
  the survivor's content is organized as parallel per-vendor reference
  tables and comparative lifecycle data, not a single reusable
  solution-with-forces write-up. Forcing the pattern template would require
  restructuring six vendor sections and four architecture write-ups into an
  awkward single Context/Forces/Solution/Consequences frame that doesn't
  match how the content is actually organized.
- **`reference-architecture`** fits better: the "Enterprise Architecture
  Patterns" section is literally four concrete system blueprints (Microsoft,
  Google, AWS, Atlassian), each decomposed into Identity/AI/Connector/Data/
  Security/Governance/Audit layers — exactly the layered-blueprint shape
  `reference-architecture` is for. The template's required Mermaid C4-style
  diagram and trade-offs section are a natural fit (see Transform Notes on
  the new diagram requirement) and the "Marketplace Connectors" and "Token &
  Consent Lifecycle Patterns" sections slot into `Components &
  responsibilities` / `Operational model` / `Security & governance
  considerations` respectively.

**Recommended `doc_type: reference-architecture`**, using
`.claude/skills/doc-standards/templates/reference-architecture.md`.

Note: this requires authoring at least one new Mermaid diagram that does not
exist verbatim in the source (flagged above under Transform Notes) — this is
in scope for stage-04 migration work, not a registry or template gap.
