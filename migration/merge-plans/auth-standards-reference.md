# Merge Plan: auth-standards-reference

## Cluster

| old_path | words | last_reviewed | source_type | status_field | disposition |
| --- | --- | --- | --- | --- | --- |
| `docs/ai-protocols/auth/auth-standards-reference.md` | 2348 | 2026-07-10 | converted-pdf | current | MIGRATE (survivor) |
| `docs/ai-security-governance/security/Part7_Standards_Reference.md` | 59 | 2026-07-17 | (empty) | retired | MERGE-INTO (loser) |

- **target_topic_id:** `auth-standards-reference`
- **target canonical path:** `docs/protocols/01-auth-standards-reference.md`
- **domain:** protocols
- **wave:** 4
- Registry check: `governance/CANONICAL_REGISTRY.yaml` (line ~2160) already registers this
  `topic_id`, with `canonical: docs/protocols/01-auth-standards-reference.md` and
  `supersedes: [docs/ai-security-governance/security/Part7_Standards_Reference.md]`. No
  registry change is needed for this plan — the librarian has already fixed the target as
  a single canonical page.

## Survivor

**Survivor = `docs/ai-protocols/auth/auth-standards-reference.md`** (2348 words,
`source_type: converted-pdf`, `last_reviewed: 2026-07-10`, `status: current`).

Normally this migration applies **recency > completeness > structure**, and by raw
recency the trust-domain stub (`last_reviewed: 2026-07-17`) is *newer* than the
survivor (2026-07-10). This is a genuine exception to "recency first": the stub's
newer review date reflects only that someone touched it to mark it retired and add a
redirect notice — not that its content was refreshed. Having read both files in full:

- The stub is 59 words total, entirely front matter + a single `:::caution` admonition
  block. It contains **zero standards content** — no RFCs, no tables, no checklists.
- Its body is exclusively a pointer: "This page was the raw PDF-conversion of
  Enterprise AI Authentication Research Part 7. The content has been fully rewritten
  and is now maintained at ai-protocols/auth/auth-standards-reference... Please update
  any bookmarks or links."
- Its own `status: retired` field self-declares it as superseded.

So completeness (2348 substantive words vs. 59 pointer words) and structure (full
standards-reference anatomy vs. a bare redirect stub) both override the stub's
slightly newer review timestamp. Survivor confirmed: `docs/ai-protocols/auth/auth-standards-reference.md`.

## Unique-Content Map

Read the loser file in full (all 22 lines). Expected "no unique content — safe to
drop" given the 59-word/retired profile, and this is confirmed with one added check:

- The stub's own caution note claims: *"The unique CAB glossary entry from this
  version has been merged into the canonical page."* This claim was verified against
  the survivor's actual Glossary table — the entry `CAB | Change Advisory Board;
  committee that approves IT change requests in ITSM frameworks` **is already present**
  in the survivor (Glossary section, ~row 20). So even the one piece of content the
  stub asserts as unique has already been folded in previously.
- No other content exists in the stub — front matter (`title`, `date_created`,
  `last_reviewed`, `status`, `supersedes: ""`, `doc_type`, `tags`) is boilerplate that
  duplicates the survivor's own front matter fields.

**Conclusion: no unique content to carry forward. Safe to drop the loser entirely**
once the redirect is honored (i.e., once readers/links pointing at
`docs/ai-security-governance/security/Part7_Standards_Reference.md` are retargeted to
the new canonical path — see Transform Notes).

## Target Structure

Survivor structure checked for converted-pdf damage: tables render cleanly, checkbox
lists are intact, no stray `\f` form-feed characters, no literal "Page N of N" footer
artifacts, and no broken/merged table cells were found. The one PDF-series leftover is
a byline line right under the H1: `*Enterprise AI Authentication Research · Part 7 of
7*` — a cross-reference to a 7-part source series that no longer exists as such in the
new IA and should not carry forward verbatim (see Transform Notes).

Proposed H2/H3 outline for `docs/protocols/01-auth-standards-reference.md` (mirrors the
survivor's existing structure — it is already well-organized and does not need
reorganizing, only trimming and front-matter/link conversion):

```
# Auth Standards Reference: OAuth 2.1, OIDC, RFC 8693 & Implementation Checklists

(1-paragraph "why this matters" intro — replaces the PDF-series byline)

## Key Standards Reference
### OAuth 2.0 and OAuth 2.1
### OpenID Connect (OIDC)
### RFC 8693 — OAuth 2.0 Token Exchange
### RFC 7523 — JWT Bearer Token for OAuth 2.0
### Downscoping and Scope Reduction

## Decision Frameworks
### Choosing an Authentication Method for a New Connector
### Choosing Between Service Account and Delegated Access

## Implementation Checklists
### OAuth 2.1 — Authorization Server
### OAuth 2.1 — Client (AI Platform)
### OAuth 2.1 — Resource Server (MCP Server / API)
### MCP Server Security Checklist
### Audit & Compliance Checklist

## Vendor Documentation References

## Glossary

## Related
## Sources
```

**Word count / split decision:** 2348 words is ~17% over the ~2000-word soft limit —
moderate overage, not a multi-topic sprawl. Recommendation is **trim, not split**:

- The content is one coherent reference topic (auth standards), the registry has
  already fixed a single canonical path/topic_id for it, and splitting would require
  new `topic_id`s that do not yet exist — an out-of-scope registry change for this
  planning stage.
- Trim candidates to close the ~350-word gap without losing practitioner value:
  drop the PDF-series byline (~10 words), tighten the Vendor Documentation References
  table to remove lower-value/redundant rows (currently 24 rows; several are generic
  vendor doc links with marginal AI-agent relevance), and audit the 26-term Glossary
  for terms already defined inline elsewhere in the corpus.
- If a future wave still finds it over budget after trimming, the natural split point
  is Implementation Checklists (5 subsections, currently ~450 words) into its own
  child page — this is **not proposed now**, but if adopted later it would need a new
  `topic_id` (e.g., `auth-implementation-checklists`) under a `docs/protocols/`
  hub, which would be **NEEDS LIBRARIAN REGISTRATION**. Not recommended for this wave.

## Transform Notes

- **Converted-PDF artifacts to strip:** the italic `*Enterprise AI Authentication
  Research · Part 7 of 7*` byline under the H1 (references a 7-part source series that
  isn't part of the new IA) — replace with the required 1-paragraph "why this matters"
  lead per doc-standards page anatomy. No page-number or running header/footer
  artifacts, and no broken tables were found otherwise — this conversion is cleaner
  than the "converted-pdf" `source_type` tag would suggest, but re-verify with a
  visual diff against `archive/ai-protocols/Part7_Standards_Reference.pdf` before
  final sign-off, since tables spanning a PDF page break are the most common place
  such damage hides.
- **Front matter conversion:** old fields `date_created`, `source_file`,
  `covers_through`, and `doc_type: reference` do not exist in the new schema and
  should be dropped/remapped. `supersedes` in the new front matter should list both
  old paths: `docs/ai-protocols/auth/auth-standards-reference.md` and
  `docs/ai-security-governance/security/Part7_Standards_Reference.md`.
- **Links needing rewrite:** the survivor's `> **See also:**` callout links to
  `./entra-3lo-agent-auth-standards-architecture` and
  `./marketplace-connector-auth-patterns` (old sibling-folder relative paths). Per the
  registry these resolve to `docs/protocols/11-entra-3lo-agent-auth-standards-architecture.md`
  and `docs/protocols/03-marketplace-connector-auth-patterns.md` — rewrite as relative
  links within `docs/protocols/` and move into the template's `## Related` section
  rather than an inline admonition (page-styling convention for cross-links).
  Vendor Documentation References table uses bare domains (e.g.
  `learn.microsoft.com/...`) instead of full `https://` URLs — normalize on migration.
- **Redirect obligation:** any external or in-repo links currently pointing at
  `docs/ai-security-governance/security/Part7_Standards_Reference.md` must be
  retargeted to `docs/protocols/01-auth-standards-reference.md` once the loser is
  dropped, consistent with the stub's own redirect notice.

## Doc Type & Template

Old front matter used `doc_type: reference`, which **does not exist** in the current
taxonomy (`governance/DOC_TYPES.md` lists: concept, guide, reference-architecture,
pattern, anti-pattern, decision, runbook, checklist, research-report, case-study,
learning-path, hub, template-asset, glossary — no plain "reference"). Between the two
closest candidates:

- `reference-architecture` requires a Mermaid C4-style diagram and a
  Components/trade-offs section — this page describes no system architecture, so
  forcing that type would require fabricating a diagram that doesn't reflect real
  content.
- **`guide` fits better**: the Decision Frameworks and Implementation Checklists
  sections are practitioner "how do I choose/implement this" content, which matches
  guide's "how to do X" purpose more closely than a static architecture blueprint.

**Recommended `doc_type: guide`.**

Flag: `.claude/skills/doc-standards/templates/` currently contains only
`concept.md`, `decision-adr.md`, and `reference-architecture.md` — **no `guide.md`
template exists yet**, despite `guide` being a valid type in `DOC_TYPES.md`. This is a
gap outside this merge plan's scope (I own only this one file); the stage-04
migrator/doc-standards owner will need either a `guide.md` template added or an
explicit fallback decision before this page can be produced.
