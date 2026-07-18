# Merge Plan: enterprise-ai-platform-auth-survey

## Cluster

| # | old_path | words | last_reviewed | source_type | status_field | disposition |
|---|----------|-------|---------------|-------------|--------------|--------------|
| 1 | `docs/ai-protocols/auth/enterprise-ai-platform-auth-survey.md` | 2603 | 2026-07-10 | converted-pdf | current | MIGRATE (survivor) |
| 2 | `docs/ai-security-governance/security/Part1_Industry_Survey.md` | 49 | 2026-07-17 | (empty) | retired | MERGE-INTO (loser) |

- **target canonical path:** `docs/protocols/02-enterprise-ai-platform-auth-survey.md`
- **domain:** protocols
- **wave:** 4
- **topic_id:** `enterprise-ai-platform-auth-survey` — already present in `governance/CANONICAL_REGISTRY.yaml` (domain: protocols, canonical: the target path above, `supersedes: [docs/ai-security-governance/security/Part1_Industry_Survey.md]`, `pages: []`). No new registry entry is required for the base topic.

## Survivor

Survivor = `docs/ai-protocols/auth/enterprise-ai-platform-auth-survey.md` → target `docs/protocols/02-enterprise-ai-platform-auth-survey.md` (2603 words, `source_type: converted-pdf`, `last_reviewed: 2026-07-10`, `status: current`).

Having read both files in full: the trust-domain member (`docs/ai-security-governance/security/Part1_Industry_Survey.md`) is a 49-word retired redirect stub. Its entire body is a Docusaurus `:::caution` admonition stating the page "was the raw PDF-conversion of the Enterprise AI Authentication Research Part 1," that content "has been fully rewritten," and pointing readers to the exact old path of today's survivor (`../../../ai-protocols/auth/enterprise-ai-platform-auth-survey`). Its own frontmatter carries `status: retired` and an empty `supersedes: ""` (i.e., it is itself already marked as superseded-by the survivor, not the other way around).

**Explicit exception to naive recency-first ordering:** the loser's `last_reviewed` (2026-07-17) is *more recent* than the survivor's (2026-07-10), which would normally argue for treating it as the fresher/authoritative copy. That heuristic does not apply here — the recent review date only reflects someone confirming the redirect stub still points to the right place, not a review of substantive content. The stub carries zero domain content (no auth/identity/platform detail at all), while the survivor carries the full 10-platform survey. Word count and `status_field` (current vs. retired) are the correct signals for this pair, not `last_reviewed`. MIGRATE/MERGE-INTO dispositions in `migration/mapping.csv` are confirmed correct.

## Unique-Content Map

Read in full — the loser has **no unique content**. Its only prose is the admonition block itself (title, a `:::caution` notice, and a link back to the survivor's old path). There is no auth/identity/platform information, no data point, no fact anywhere in the file that isn't also just a pointer to the survivor. Safe to drop entirely; nothing to fold in beyond the redirect intent itself (which is handled structurally by the `supersedes` entry already in the registry, not by copying text).

Action: no content transplant needed from the loser. Its file should be deleted from the old tree at execution time (stage-04); this plan does not perform that deletion.

## Target Structure

Survivor's actual structure (converted-pdf, checked for artifacts — see Transform Notes) is a 10-platform comparative survey plus a cross-platform rollup:

```
# Enterprise AI Platform Authentication Survey
## Overview
   - "Platforms Covered" bullet list (10 platforms)
## 1. Google Gemini
   - prose intro + "Architecture Matrix" table + "Gemini Authentication Flow" numbered steps
## 2. Claude — Anthropic
   - prose intro + "Architecture Matrix" table + "MCP Identity Flow" prose + "Key MCP Security Principles" bullets
## 3. ChatGPT Enterprise — OpenAI
   - prose intro + "Architecture Matrix" table
## 4. Microsoft 365 Copilot
   - prose intro + "Architecture Matrix" table + "M365 Copilot OBO Flow" table + "Why Microsoft's OBO Implementation Matters" bullets
## 5. GitHub Copilot
   - prose intro + "Architecture Matrix" table
## 6. Amazon Q Business
   - prose intro + "Architecture Matrix" table
## 7. Atlassian Rovo
   - prose intro + "Architecture Matrix" table
## 8. ServiceNow AI Agents
   - prose intro + "Architecture Matrix" table
## 9. Glean
   - prose intro + "Architecture Matrix" table
## 10. Moveworks
   - prose intro + "Architecture Matrix" table
## Cross-Platform Comparison
   - rollup table (IdP Integration / OBO / MCP Support / Audit Log) + "Key Takeaways" bullets
```

This maps cleanly onto a per-platform H2 structure and should be preserved — it is the load-bearing organizing principle of the page, not a PDF artifact.

**Word count / soft limit:** 2603 words vs. the ~2000-word soft limit (doc-standards). Recommendation: **trim first, split only if trimming falls short.**

- The overage is modest (~30%), and the registry already models this topic as a single flat page (`pages: []`, no hub entry) — splitting would require a hub conversion and new child `topic_id`s that nothing today asks for.
- Trim candidates that don't lose domain content:
  - Condense each platform's 2-4 sentence prose lead-in to 1-2 sentences — the Architecture Matrix table already carries the substantive detail redundantly restated in prose (Gemini, ChatGPT Enterprise, GitHub Copilot, Amazon Q, Atlassian Rovo, ServiceNow, Glean, Moveworks sections all repeat matrix content in prose).
  - Convert the three narrative/tabular flow walk-throughs (Gemini Authentication Flow, MCP Identity Flow, M365 Copilot OBO Flow) into Mermaid sequence diagrams per the `diagram-standards` skill instead of numbered lists/tables — typically shorter in word count and clearer for a flow.
  - Drop the "Platforms Covered" bullet list in Overview — fully redundant with the Cross-Platform Comparison table and the H2 sequence itself.
- If a post-trim pass still lands meaningfully over 2000 words, fall back to a hub + child-page split (e.g., group platforms 3-4 per child page under a new `docs/protocols/02-enterprise-ai-platform-auth-survey/` hub). Any such split requires new `topic_id`s for the child pages — **NEEDS LIBRARIAN REGISTRATION** — and is out of scope for this plan; the librarian agent must be engaged separately if the trim pass proves insufficient. Do not create child topic_ids preemptively.

## Transform Notes

Converted-PDF artifacts observed and how to handle them:

- **Series-branding artifact:** the italic line directly under the H1 — `*Enterprise AI Authentication Research · Part 1 of 7*` — is a leftover PDF cover/footer tag from the original 7-part research series, not part of the article body. Strip it or fold the "Part 1 of 7" fact into the opening "why this matters" paragraph per `page-styling` if the series context is worth keeping; do not leave it as a floating italic fragment.
- **No broken tables detected:** all 11 pipe tables (10 per-platform Architecture Matrices + Cross-Platform Comparison) and the one plain "M365 Copilot OBO Flow" table render as well-formed GFM tables with consistent column counts — no page-break artifacts, no split/duplicated header rows. No repair needed here.
- **No stray page-number artifacts** (e.g., "Page 3 of 12", running headers/footers mid-body) were found in the body text.
- **Frontmatter fields outside the standard schema:** survivor's frontmatter carries `date_created`, `source_file`, `covers_through`, and `research_date`, none of which are part of the required schema (`title, doc_type, domain, status, canonical, topic_id, maturity, personas, last_reviewed, covers_version, supersedes, sources, tags`). These should be dropped or reconciled at migration time; `source_file: "Part1_Industry_Survey.pdf"` is useful provenance but belongs in a migration note/commit message, not page frontmatter. Required fields not yet present (`domain`, `canonical`, `topic_id`, `maturity`, `personas`, `sources`) must be added.
- **Links needing rewrite:** the loser's redirect target (`../../../ai-protocols/auth/enterprise-ai-platform-auth-survey`) becomes stale once the survivor moves to `docs/protocols/02-enterprise-ai-platform-auth-survey.md`; since the loser file is being dropped rather than kept as a redirect, no live link needs fixing there. Within the survivor itself, the only external reference is prose-mentioned `modelcontextprotocol.io` (not a markdown link) — convert to a proper citation link if kept, per Doc Type note below. No other internal wiki links present in either file.

## Doc Type & Template

- **doc_type:** `research-report` — the survivor's own frontmatter already declares this, and the content matches the definition in `governance/DOC_TYPES.md` ("Grounded deep research," 90-day review cadence, `sources` required tier-1 majority, `covers_version` required) far better than `reference-architecture` (which is for a single proposed/documented architecture, not a comparative survey of ten vendors' patterns).
- **Template:** no `research-report.md` template file exists under `.claude/skills/doc-standards/templates/` (only `concept.md`, `decision-adr.md`, `reference-architecture.md`, `hub-architecture.md`, `hub-strategy.md`, `hub-trust.md` are present) — this is a gap in the template set, not something this plan can resolve. Nearest structural analog is `reference-architecture.md`; adapt its frontmatter block (drop diagram-mandatory framing, add `sources`) rather than its section headings, since the per-platform matrix structure above is the correct shape for this page.
- **research-grounding flag:** per `governance/DOC_TYPES.md`, `research-report` requires a `sources` array with a tier-1 majority. The survivor currently has no citations at all (converted from a PDF with no source list carried over) — this page cannot ship as `research-report` without a `research-grounding` pass to source-verify the vendor-specific claims (auth flows, token lifetimes, product names like "Atlassian Guard," "Purview UAL," etc., several of which read as plausibly time-sensitive/vendor-version-dependent). **Flagging for follow-up** — do not perform that research as part of this merge plan.
