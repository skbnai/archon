# Merge Plan: eu-bank-copilot-architecture

## Cluster

| | old_path | words | last_reviewed | source_type |
|---|---|---|---|---|
| Survivor | `docs/ai-usecases/eu-bank-ai-copilot-part1-architecture.md` | 2284 | 2026-07-17 | converted-pdf |
| Loser | `docs/ai-usecases/eu-bank-ai-copilot-architecture.md` | 4303 | 2026-07-10 | converted-docx |

- target canonical path: `docs/assets/01-eu-bank-copilot-architecture.md`
- domain: `assets`
- wave: `8`

**Series context:** this cluster is Part 1 of the 4-part `eu-bank-copilot`
worked example (`series_name: "EU Bank AI Copilot Platform"`, `series_part: 1`,
`series_total: 4` in the survivor's frontmatter). Full picture from
`grep -n "eu-bank" migration/mapping.csv`:

- **Part 1 — architecture & design decisions → `eu-bank-copilot-architecture` (this plan)**
- Part 2 — sequence diagrams & code → `eu-bank-copilot-sequence-diagrams` (handled by another agent, not drafted here)
- Part 3 — agent runtime, MCP & security → `eu-bank-copilot-runtime-security` (not part of this cluster; referenced only for cross-links)
- Part 4 — compliance, infra & observability → `eu-bank-copilot-compliance-observability` (handled by another agent, not drafted here)
- The monolith `eu-bank-ai-copilot-complete.md` is `DROP` (superseded by the 4-part split).
- Two EU-Bank evaluation-framework files (`EU_Banking_AI_Agent_Evaluation_Framework.md`,
  `EU_Banking_AI_Evaluation_Compliance_Guide.md`) fold into Part 4, not Part 1.

This plan covers Part 1 only. Do not draft Part 2, 3, or 4 content here.

## Survivor

Survivor per `migration/mapping.csv` is
`docs/ai-usecases/eu-bank-ai-copilot-part1-architecture.md` (2284 words,
converted-pdf, reviewed 2026-07-17).

Confirmed after reading both files in full: the loser
(`eu-bank-ai-copilot-architecture.md`, 4303 words, converted-docx, reviewed
2026-07-10) is indeed nearly 2x longer, but the mapping.csv choice is correct
and **no disagreement is flagged**. Reasoning:

- The loser is explicitly framed as a "Companion code reference" to the old
  monolith (`eu-bank-ai-copilot-complete.md`, itself `DROP`'d) — line 15:
  *"Companion code reference to the [EU Bank AI Copilot Platform guide]
  (./eu-bank-ai-copilot-complete.md)"*. It predates the 4-part restructure.
- Its bulk (§2–§9: frontend code, BFF code, Strands agent code, MCP server
  code, Tool Registry code, Terraform/IAM/Guardrails code, security-header
  code, approval-service code) is **verbatim-equivalent code that was
  redistributed into Parts 2, 3, and 4** of the official series, confirmed by
  grep against the old-repo part files:
  - Frontend/BFF code (loser §2–§3) → Part 2 §2–§3 (`eu-bank-ai-copilot-part2-...md`).
  - Rate-limit token-bucket (10 req/s, burst 20) → same value in Part 2 §"2. Rate limit (token bucket 10 req/s per user)" and exercised in Part 3's test suite.
  - Strands agent / MCP servers / Tool Registry code (loser §4–§6) → Part 3 §1–§3, which additionally adds Testing Strategy and a STRIDE threat model absent from the loser.
  - Terraform/IAM/Guardrails/security-headers/PII-scrub code (loser §7–§8) → Part 4 §2 (IAM matrix, CI/CD gates, Guardrails Terraform) and Part 2 §3.3 (security headers); `PII_PATTERNS`/`scrubPII` literally reappears in Part 4 (line 388) verbatim.
  - Human-in-the-loop approval service (loser §9) → Part 2 §4 "Approval Service — Complete Implementation" (DynamoDB schema + full FastAPI impl, more complete than the loser's version).
  - EU regulatory compliance (loser §10) → Part 4 §1 (GDPR/DORA/EU AI Act), materially expanded there.
  - End-to-end call flow (loser §11) → Part 4 §2.4 "Summary: End-to-End Call Flow".
- The loser is also measurably *less accurate/refined* than the survivor: it
  says "the platform spans **four** security zones" (line 23) while the
  survivor — the corrected, later-reviewed version — says "**five** security
  zones" (line 25) and gives the full 5-row zone table including the
  Data/LLM zone the loser's draft omits. This is a concrete signal the loser
  is an earlier, superseded draft, not a richer one.
- Net: the loser's extra ~2000 words are almost entirely code payload that
  now lives, verbatim or improved, on sibling series pages (Parts 2–4, out of
  scope for this cluster) — not unique architectural content missing from the
  survivor. **Finding: recency > completeness holds cleanly here** — this is
  the opposite situation from the Part 2 (sequence-diagrams) cluster, where
  the loser held irreplaceable Mermaid diagrams; here the loser's bulk is
  redundant, not irreplaceable.

## Unique-Content Map

Content in the loser not present in the survivor (max 20 lines; most items are
already homed on sibling Part 2/3/4 pages, noted per line — see Survivor
section for the full grep evidence):

1. Framing sentence that this doc is a "companion code reference" to the old monolith — obsolete, monolith is DROP'd, do not carry forward.
2. "Four security zones" — superseded by survivor's corrected five-zone model; do not carry forward.
3. Full frontend code (layout.tsx, page.tsx, DynamicToolLoader.tsx, auth.ts, bffClient.ts) — homed in Part 2 §2.
4. Full BFF code (copilotkit/route.ts, session.ts, auth callback, audit.ts, rateLimit.ts) — homed in Part 2 §3 / Part 4 (audit).
5. Strands agent code (main.py, agent.py, prompts.py, audit callback, AgentCore deploy shell) — homed in Part 3 §1.
6. MCP server code (Core Banking, Payment Rail, Risk Engine) + tool manifest JSON — homed in Part 3 §2.
7. Tool Registry FastAPI implementation — homed in Part 3 §3.
8. Terraform (VPC/SGs, IAM roles, Bedrock Guardrails) — homed in Part 4 §2.
9. HTTP security headers middleware + CI/CD security-gates workflow YAML — homed in Part 2 §3.3 / Part 4 §2.2.
10. Approval-service FastAPI (4-eyes maker/checker) — homed in Part 2 §4, more complete there (adds DynamoDB schema).
11. EU regulatory compliance detail (GDPR/DORA/EU AI Act bullets) — homed in Part 4 §1, expanded there.
12. End-to-end call-flow critical-security-rule callout — homed in Part 4 §2.4.
13. `§8.2 "OWASP LLM Controls Summary"` — header only, no body content (broken/truncated by docx conversion); superseded by Part 3 §4.2's full OWASP LLM Top 10 treatment.

**No item above represents net-new architectural fact, decision, or structure
missing from the survivor + Parts 2–4 combined.** Nothing here needs to be
merged into the Part 1 architecture page itself.

## Target Structure

Combined raw word count is ~6587, but per the Unique-Content Map, essentially
all of the loser's incremental ~2000 words is code/detail that belongs to (and
already exists on) sibling Part 2/3/4 pages, not this page. Carrying it here
too would duplicate content across the 4-part series and violate
dedup-canonicalization. **Recommendation: keep as one page, do not split**,
and keep the page close to the survivor's own word count (~2300–2500 words
after transform cleanup), not the naive ~6587 sum.

Proposed H2/H3 outline for `docs/assets/01-eu-bank-copilot-architecture.md`
(survivor's structure retained essentially unchanged — it is already the
correct, de-coded, decision-focused shape for an architecture/design-decisions
page):

```
# EU Bank AI Copilot Platform — Part 1: Architecture & Design Decisions
## 1. Platform Overview & Architecture Zones
    5-zone table + Key Design Principles (unchanged from survivor)
## 2. Technology Stack & Component Map
    package/version/role table (unchanged from survivor)
## 3. CopilotKit MCP Tools vs MCP Apps — Design Decision
### 3.1 The Fundamental Difference
### 3.2 Recommendation for EU Bank
### 3.3 Banking Use Case Assignment
## 4. Server Topology — Where Everything Lives
### 4.1 Package Location Matrix
### 4.2 Network Call Matrix
### 4.3 MCP Tool Inventory by Domain Server
## 5. Architecture Decision Records (ADRs)
    ADR-001 through ADR-005 (unchanged from survivor)
## Related
    cross-links to Part 2 (sequence diagrams & code), Part 3 (runtime & security),
    Part 4 (compliance, infra & observability)
## Sources
```

No new `topic_id` needed — single page, no split, no new registrations.
NEEDS LIBRARIAN REGISTRATION: none (topic_id `eu-bank-copilot-architecture`
is already registered per the cluster data given).

Recommend (non-blocking, migrator's discretion): add one C4-style Mermaid
container diagram under §1 to visualize the 5-zone table per
diagram-standards — both source files have `mermaid_count: 0`, and a
diagram would strengthen this specific page without pulling in the code
payload that belongs to Parts 2–4.

## Transform Notes

- **Converted-PDF artifacts to strip from the survivor:** page-number/header-
  footer residue typical of PDF conversion; verify the two tables (zone table,
  tech-stack table) didn't get column-shifted or row-wrapped by the converter.
- **Converted-docx artifacts in the loser (informational only, since loser is
  not merged in bulk):** list/style numbering artifacts, and at least one
  clearly broken paragraph structure — e.g. `get_account_balance` and
  `get_risk_score` function bodies in the loser are missing their opening
  `return {` line (dict literal starts directly with `"balance": ...,` with no
  enclosing statement) — a docx-conversion casualty. Irrelevant to this page
  since that code isn't being carried over, but worth flagging to whichever
  agent/migrator handles Part 3, in case the same corrupted snippet was
  carried into the old Part 3 source used for polish there.
- **Links needing rewrite** in the merged page:
  - Survivor's link to the series index (`./eu-bank-ai-copilot-complete.md`)
    → this points at the DROP'd monolith; replace with a link to a Part 1–4
    hub/index if one exists in the target IA, else drop the field/link.
  - Survivor §4.3's link to Part 3 (`./eu-bank-ai-copilot-part3-agent-mcp-security.md`)
    → rewrite to canonical `docs/assets/03-eu-bank-copilot-runtime-security.md`.
  - Add explicit "Related" links to `docs/assets/02-eu-bank-copilot-sequence-diagrams.md`
    (Part 2) and `docs/assets/04-eu-bank-copilot-compliance-observability.md`
    (Part 4) — this page will be the entry point for the series and should
    cross-link forward to both, not just Part 3.
  - Loser's self-link to the old part1 file
    (`./eu-bank-ai-copilot-part1-architecture.md#1-platform-overview--architecture-zones`)
    is moot once the loser is not migrated.
  - `series_index: "ai-usecases/eu-bank-ai-copilot-complete"` in survivor
    frontmatter → same monolith problem as above; needs to become a link to
    a Part 1–4 hub/index if one exists, else drop the field.

## Doc Type & Template

- `doc_type: case-study` (survivor frontmatter currently says
  `multi-part-series`, which is not in the `governance/DOC_TYPES.md` taxonomy
  — `case-study` is the correct type: "Applied example", 365d freshness SLA,
  "Fictionalization note if synthetic" requirement). DOC_TYPES.md does not
  carry a distinct word-count override for case-study; the general ≤~2,000-word
  guide guidance from `doc-standards/SKILL.md` is treated as advisory here —
  this page's proposed ~2300–2500 words is a modest, justified overage for a
  worked-example case-study page, not a reason to split.
- **FLAG: no case-study template exists.** `.claude/skills/doc-standards/templates/`
  contains only `concept.md`, `decision-adr.md`, and `reference-architecture.md`
  — no `case-study.md`. The migrator will need to follow generic page-anatomy
  rules (frontmatter schema + context → body → Related → Sources) directly, or
  a `case-study.md` template should be added to the skill before this page (and
  its 3 sibling parts) is drafted. This gap applies to all 4 parts of the
  eu-bank-copilot series, not just Part 1 — flagging here since Part 1 is the
  series entry point, but the fix belongs to whoever owns doc-standards
  templates, not to this merge plan.
- Section 5 (ADRs) could optionally borrow structure from `decision-adr.md`
  per-ADR, but keeping ADRs as subsections of the case-study page (as the
  survivor already does) is simpler and avoids a 5-way page split for content
  that is only ~600 words total.
