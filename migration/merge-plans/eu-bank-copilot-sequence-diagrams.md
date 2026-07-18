# Merge Plan: eu-bank-copilot-sequence-diagrams

## Cluster

| | old_path | words | last_reviewed | source_type | mermaid_count |
|---|---|---|---|---|---|
| Survivor | `docs/ai-usecases/eu-bank-ai-copilot-part2-sequence-diagrams-and-code.md` | 2456 | 2026-07-17 | converted-pdf | 0 |
| Loser | `docs/ai-usecases/eu-bank-sequence-diagrams.md` | 2518 | 2026-07-10 | native-md | 6 |

- target canonical path: `docs/assets/02-eu-bank-copilot-sequence-diagrams.md`
- domain: `assets`
- wave: `8`

**Series context:** this cluster is Part 2 of the 4-part `eu-bank-copilot` worked
example (see `series_index: ai-usecases/eu-bank-ai-copilot-complete`,
`series_total: 4` in the survivor's frontmatter). Full picture from
`grep -n "eu-bank" migration/mapping.csv`:

- Part 1 — architecture → `eu-bank-copilot-architecture` (handled by another agent, not drafted here)
- **Part 2 — sequence diagrams & code → `eu-bank-copilot-sequence-diagrams` (this plan)**
- Part 3 — agent/MCP/security → `eu-bank-copilot-runtime-security` (not part of this cluster; referenced only for cross-links)
- Part 4 — compliance/infra/observability → `eu-bank-copilot-compliance-observability` (handled by another agent, not drafted here)
- The monolith `eu-bank-ai-copilot-complete.md` is `DROP` (superseded by the 4-part split).

This plan covers Part 2 only. Do not draft Part 1, 3, or 4 content here.

## Survivor

Survivor per `migration/mapping.csv` is
`docs/ai-usecases/eu-bank-ai-copilot-part2-sequence-diagrams-and-code.md` (2456
words, converted-pdf, reviewed 2026-07-17, `mermaid_count: 0`).

Confirmed after reading both files in full:

- The survivor's "## 1. Sequence Diagrams" section (§1.1–§1.6) contains **no
  Mermaid diagrams at all** — only prose "step-by-step trace" bullet lists and a
  single italic caption line per flow (e.g. `*Figure: Diagram 01 — Entra ID OIDC
  + PKCE Authentication & Session Establishment*`). There is no image, no
  embedded diagram markup, not even a broken ASCII table — the PDF conversion
  appears to have **dropped the diagrams entirely**, leaving only the caption
  text and prose trace as a placeholder. (`ascii_art_suspected: False` in the
  cluster data is consistent with this — it's not mangled ASCII, it's simply
  absent.)
- The survivor's own text explicitly points at the loser as the diagram source:
  *"Each was rendered at high resolution (1600–3100px wide) from validated
  Mermaid source — see the companion page [EU Bank Sequence Diagrams]
  (./eu-bank-sequence-diagrams.md)."* — i.e. the survivor was written knowing
  the loser holds the only real diagrams.
- The loser (`eu-bank-sequence-diagrams.md`, 2518 words, native-md, reviewed
  2026-07-10) contains all **6 fenced ```mermaid `sequenceDiagram` blocks**,
  clean and complete, each with `autonumber`, named participants/actors, and
  accompanying security-note callouts (`> **...**`).

**FLAG (high priority):** even though `mapping.csv` picked the PDF version as
survivor (consistent with section-doctrine default — prefer the multi-part
series file as the structural backbone), **the survivor has zero usable
diagram content**. The loser's 6 Mermaid diagrams are not a redundant "earlier
draft" — they are the only surviving machine-renderable diagram source for
this entire wave and **must be ported verbatim into the merged page**, not
redrawn from scratch and not dropped. Losing this file without porting the
diagrams would delete the single most valuable unique-content item in wave 8.
Diagram-standards should validate the ported Mermaid against the current
C4/sequence conventions, but the source of truth for diagram content is the
loser file, not the survivor's prose.

## Unique-Content Map

Loser (`eu-bank-sequence-diagrams.md`) unique content — all 6 diagrams named,
plus prose not present in survivor:

1. **Diagram 01 — Authentication & Session Establishment**: full Entra ID
   OIDC+PKCE sequence (Browser, WAF, BFF, Entra ID, Redis Session); includes
   WAF OWASP-CRS/geo-block hop and Redis TTL=900s detail not in survivor's trace.
2. **Diagram 02 — MCP Tools: Data Query Flow**: CopilotKit UI → BFF → AgentCore
   Strands → Bedrock → Core Banking MCP → Bank API → Audit Kinesis, with
   explicit "Protocol chain" callout and PII-stripping note.
3. **Diagram 03 — MCP Apps: Interactive UI Flow**: `ui://` resource flow, CDN
   bundle fetch/SHA-384 verify, sandboxed iframe render, `postMessage` origin
   validation, ends at `interrupt_before` handoff into Diagram 04.
4. **Diagram 04 — Payment Approval: 4-Eyes Human-in-the-Loop**: full
   Maker/Checker/Approval Service/Notifications/AgentCore/MCP sequence
   including DynamoDB PutItem/UpdateItem detail, SQS notification, HMAC token
   issuance and agent RESUME — more granular than survivor's one-paragraph
   summary of the same flow.
5. **Diagram 05 — Dynamic Tool & UI Registration**: CI/CD parallel security
   gates (SAST/SCA/secret-scan/IaC), container sign+deploy, CDN bundle upload,
   Tool Registry POST, Strands discovery on next session — full 9-participant
   sequence, survivor only has a one-paragraph summary.
6. **Diagram 06 — Full System End-to-End**: 11-participant multi-tool query
   (balance + risk score) across WAF/BFF/Redis/AgentCore/Bedrock/2×MCP/Bank/
   Audit; includes the closing **Data Residency** callout (GDPR Art. 25 / DORA
   Art. 9, eu-west-1/eu-central-1 SCP enforcement) — this compliance callout is
   not present anywhere in the survivor.

Also unique: all `> **note**` security/protocol callout boxes attached to each
diagram (BFF-as-confidential-client note, sandbox `allow-scripts allow-forms`
warning, 4-eyes enforcement note, zero-downtime note) — these are tighter and
more precise than survivor's prose and should be preserved alongside each
diagram, not just the diagram code fences.

## Target Structure

Proposed H2/H3 outline for `docs/assets/02-eu-bank-copilot-sequence-diagrams.md`
(survivor's structure retained as backbone; loser's 6 diagrams inserted at each
matching subsection; loser's callouts inserted immediately below each diagram):

```
# EU Bank AI Copilot Platform — Part 2: Sequence Diagrams & Application Code
## 1. Sequence Diagrams
### 1.1 Authentication & Session — Entra ID OIDC + PKCE
    survivor prose (trace) + Diagram 01 mermaid block + loser's security-note callout
### 1.2 MCP Tools — Data Query Flow
    survivor prose + Diagram 02 mermaid block + loser's protocol-chain callout
### 1.3 MCP Apps — Interactive iframe UI
    survivor prose + Diagram 03 mermaid block + loser's sandbox security-note callout
### 1.4 Payment Approval — 4-Eyes Human-in-the-Loop
    survivor prose (currently 1 caption line only) + Diagram 04 mermaid block
    + loser's 4-eyes enforcement callout
### 1.5 Dynamic Tool & UI Registration
    survivor prose (currently 1 caption line only) + Diagram 05 mermaid block
    + loser's zero-downtime callout
### 1.6 Full System — All Layers End-to-End
    survivor prose (currently 1 caption line only) + Diagram 06 mermaid block
    + loser's Data Residency / GDPR-DORA callout
## 2. Frontend — React + CopilotKit Code Reference
    (unchanged from survivor: 2.1–2.3, code fences)
## 3. BFF — Backend For Frontend Code Reference
    (unchanged from survivor: 3.1–3.3, code fences)
## 4. Approval Service — Complete Implementation
    (unchanged from survivor: 4.1–4.2, schema table + FastAPI code)
```

**Word count and split decision:** loser alone is 2518 words; survivor alone is
2456 words; naive combined ceiling ≈4974 words if nothing is dropped verbatim
(actual will be lower since §1.4/1.5/1.6 survivor captions collapse into the
inserted diagrams' surrounding prose rather than duplicating).
`.claude/skills/doc-standards/SKILL.md` size guidance is "≤ ~2,000 words.
Larger topic → split into a series with a hub/index page." This topic **has
already been split into a series** at the wave-8 level (4 parts, each its own
page) — that satisfies the split doctrine at the topic level. However, Part 2
alone, once merged, will land well above the general 2,000-word guideline
(likely ~3,500–4,000 words after de-duplicating the §1.4–1.6 captions).

Recommendation: **keep as one page** for this merge plan — `mapping.csv`
already fixes `target_path` as the single file
`docs/assets/02-eu-bank-copilot-sequence-diagrams.md`, and diagrams are not
"filler" content that can be pruned to hit a budget. If the migrator finds the
rendered result materially exceeds ~4,000 words, flag to the reviewer/librarian
for a possible further split into "2a: Sequence Diagrams" and "2b: Application
Code Reference" as a follow-up registry change — that decision is out of scope
for this merge plan (registry/mapping changes are not mine to make here).

## Transform Notes

- **Converted-PDF artifacts to strip from the survivor:** watch for PDF-header/
  footer repetition, page-break stray characters, and any residual figure
  placeholders left behind by the conversion (e.g. stray `*Figure: Diagram 0N —
  ...*` caption lines in §1.4–1.6 that have no accompanying diagram — these read
  as broken artifacts once a real diagram is inserted directly above/below
  them and should be merged into the diagram's caption, not kept as orphan
  text). No table-mangling was found in this specific file, but diagram-
  standards should still verify the final merged page's diagrams render
  correctly rather than re-deriving diagram content from the PDF text (the PDF
  has none to derive from — the loser's clean Mermaid is the only valid source,
  per the Survivor section above).
- Loser's `source_file: "eu-bank-sequence-diagrams.html"` and its own
  cross-links (`eu-bank-ai-copilot-complete.md`, `eu-bank-ai-copilot-architecture.md`)
  point at old-repo paths/monolith — drop these, they are superseded.
- **Links needing rewrite** in the merged page:
  - Survivor's link to Part 1 (`./eu-bank-ai-copilot-part1-architecture.md`) →
    rewrite to canonical `docs/assets/01-eu-bank-copilot-architecture.md`.
  - Survivor's link to Part 3 (`./eu-bank-ai-copilot-part3-agent-mcp-security.md`)
    → rewrite to canonical `docs/assets/03-eu-bank-copilot-runtime-security.md`.
  - Survivor's self-referential link to the loser
    (`./eu-bank-sequence-diagrams.md`) → remove entirely once diagrams are
    ported inline (the companion page no longer exists post-merge).
  - Any implicit/expected link to Part 4
    (`docs/assets/04-eu-bank-copilot-compliance-observability.md`) for the
    audit/DORA retention material referenced in Diagram 06's Data Residency
    callout — add a "Related" link per page-anatomy convention, not a redraft.
  - `series_index: "ai-usecases/eu-bank-ai-copilot-complete"` in survivor
    frontmatter → this points at the DROP'd monolith; needs to become a link to
    a Part 1–4 hub/index if one exists in the target structure, else drop the
    field.

## Doc Type & Template

- `doc_type: case-study` (survivor frontmatter currently says
  `multi-part-series`, which is not in the `governance/DOC_TYPES.md` taxonomy —
  `case-study` is the correct type: "Applied example", 365d SLA, "Fictionalization
  note if synthetic" requirement).
- **FLAG: no case-study template exists.** `.claude/skills/doc-standards/templates/`
  contains only `concept.md`, `decision-adr.md`, and `reference-architecture.md`
  — there is no `case-study.md` template. The migrator will need to follow the
  generic page-anatomy rules (frontmatter schema + "why this matters" → body →
  Related → sources) from `doc-standards/SKILL.md` directly, or a template
  should be added to the skill before this page is drafted. This gap applies to
  all 4 parts of the eu-bank-copilot series, not just Part 2.
