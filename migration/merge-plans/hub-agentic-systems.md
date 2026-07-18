# Merge Plan: hub-agentic-systems

## Cluster

| old_path | words | last_reviewed | source_type | ascii_art_suspected |
|---|---|---|---|---|
| docs/agentic-systems/config/index.md | 31 | 2026-07-10 | native-md | False |
| docs/agentic-systems/harness/index.md | 98 | 2026-07-10 | native-md | False |
| docs/agentic-systems/index.md | 197 | 2026-07-10 | native-md | False |
| docs/agentic-systems/memory/index.md | 66 | 2026-07-10 | native-md | False |
| docs/agentic-systems/platform/index.md | 64 | 2026-07-10 | native-md | False |
| docs/agentic-systems/skill/coding/index.md | 711 | 2026-07-10 | native-md | False |
| docs/agentic-systems/skill/enterprise/index.md | 606 | 2026-07-10 | native-md | False |
| docs/agentic-systems/skill/index.md | 1578 | 2026-07-10 | native-md | False |
| docs/agentic-ui/index.md | 2066 | 2026-07-10 | native-md | True |
| docs/coding-tools/claude/index.md | 546 | 2026-07-10 | native-md | False |
| docs/coding-tools/code-review/index.md | 72 | 2026-07-10 | native-md | False |
| docs/coding-tools/github-copilot/index.md | 169 | 2026-07-10 | native-md | False |
| docs/coding-tools/index.md | 9 | 2026-07-10 | native-md | False |
| docs/multimodal-ai/index.md | 1370 | 2026-07-16 | native-md | False |
| docs/workflow-orchestration/index.md | 421 | 2026-07-10 | native-md | False |

- target_topic_id: `hub-agentic-systems`
- target_path: `docs/agentic-systems/index.md`
- domain: `agentic-systems`
- wave: 3

All 15 rows are `disposition=MERGE-INTO` per `migration/mapping.csv`,
rationale "Nested section/subfolder index; one hub per domain rule —
folds into hub-agentic-systems." There is no `MIGRATE` row for
`hub-agentic-systems` — confirmed by grep.

Deep content from the same old folders migrates via separate MIGRATE
rows, out of scope for this plan (confirmed by grepping mapping.csv for
the five old-prefix roots):
- `docs/agentic-systems/config/*`, `harness/*`, `memory/*`, `platform/*`,
  `skill/*` (both `coding/` and `enterprise/` sub-series plus the shared
  `00-executive-summary-and-reference-architecture.md`) — ~35 MIGRATE
  rows landing at `docs/agentic-systems/core/01-*.md` through `38-*.md`.
  One skill part (`skill/coding/02-skill-anatomy-and-metadata-schema.md`)
  is itself MERGE-INTO the enterprise variant (`core/01-*.md`) as a
  duplicate-title fold, not part of this hub cluster.
  Two harness parts and several `coding-tools/claude/*` cert files are
  `TRACK`-dispositioned to `docs/career/*` (interview question bank,
  CCAF/CCAO-F/CCDV-F/CCAR-P study guides, cheatsheets, exam preps,
  questionnaires) — out of scope for this domain hub entirely.
- `docs/agentic-ui/*` (excluding `index.md`) — 19 MIGRATE rows landing at
  `docs/agentic-systems/agentic-ui/01-*.md` through `19-*.md`, plus one
  `evaluation-framework.md` MERGE-INTO `docs/operations/01-agent-
  evaluation-framework.md` (wave 8, a different cluster's survivor — not
  this hub).
- `docs/coding-tools/{claude,code-review,github-copilot}/*` — ~46 MIGRATE
  rows landing at `docs/agentic-systems/coding-tools/01-*.md` through
  `54-*.md` (numbering interleaves across the three subfolders).
- `docs/multimodal-ai/*` (excluding `index.md`) — 15 MIGRATE rows landing
  at `docs/agentic-systems/multimodal/01-*.md` through `15-*.md`.
- `docs/workflow-orchestration/*` (excluding `index.md`) — 23 MIGRATE rows
  landing at `docs/agentic-systems/orchestration/01-*.md` through
  `23-*.md`.

## Survivor

Survivor is the already-existing fresh hub stub at
`docs/agentic-systems/index.md` (read in full: frontmatter `doc_type: hub`,
`domain: agentic-systems`, `status: draft`, `topic_id: hub-agentic-systems`,
`maturity: foundational`, `tags: [hub, agentic-systems]`; a one-paragraph
intro on agent loops/orchestration/memory/HITL; a "Scope" bullet list of 7
items — agent architectures & multi-agent topologies, orchestration &
workflow engines, memory hub, skills & tools design, planning/HITL,
agent UX & digital employees, harness design; and a "Related" list linking
to the Protocols Hub and Data & Knowledge Hub).

A hub cluster has no old-file survivor by design: per
`governance/DOC_TYPES.md`, `doc_type: hub` is "Links only canonical pages;
curated, not auto" — a hub is hand-authored fresh, not inherited or rolled
up from any single old section-index page. All 15 old files here are
nested section/subfolder indexes across five old top-level folders
(`agentic-systems/` and its `config/`, `harness/`, `memory/`, `platform/`,
`skill/`, `skill/coding/`, `skill/enterprise/` subfolders; the standalone
`agentic-ui/`, `coding-tools/` root plus its `claude/`, `code-review/`,
`github-copilot/` subfolders; `multimodal-ai/`; and `workflow-orchestration/`),
and the "one hub per domain" rule folds all of them into the single new
`docs/agentic-systems/index.md` as curated link targets, not merged prose.

## Unique-Content Map

Checked against the stub's 7 Scope bullets (agent architectures/multi-agent
topologies; orchestration & workflow engines; memory hub; skills & tools
design; planning/HITL; agent UX & digital employees; harness design).

**docs/agentic-systems/config/index.md** (31w)
- Bare 1-link wrapper over the config MIGRATE target. No unique content —
  safe to drop. Note: "Configuration Management" as a topic is not itself
  a Scope bullet; recommend a short "Configuration" mention folded under a
  Platform sub-area rather than a dedicated Scope line.

**docs/agentic-systems/harness/index.md** (98w)
- Already covered by "Harness design" Scope bullet. One unique cross-link
  worth carrying: `../../enterprise-architecture/ai-architecture/
  ai-harness-architecture-orchestration.md` (8-plane runtime model, 14
  orchestration patterns) — outside this cluster's rows, flag for
  librarian/reviewer before wiring as a hub "Related" link.

**docs/agentic-systems/index.md** (197w, old domain root)
- "Explore this section" table (Skills/Platform/Memory/Configuration/
  Harness with focus + start-here links) — this is exactly what the new
  stub's Scope bullets + a links section replace; no new facts beyond
  wayfinding.
- "Authoritative references" list — 4 external standards links (MCP spec,
  A2A spec, OpenTelemetry GenAI semconv, OWASP prompt-injection guidance).
  **Unique and worth preserving** — the new stub has no equivalent
  "external standards" callout. Recommend adding as a short "Standards &
  References" list on the new hub.

**docs/agentic-systems/memory/index.md** (66w)
- Already covered by "Memory hub" Scope bullet. One unique cross-link:
  `../../enterprise-architecture/ai-architecture/
  agent-memory-planning-architecture.md` (full memory taxonomy,
  extract-consolidate-retrieve pipeline, TTL/GDPR lifecycle, planning
  architecture) — outside this cluster, flag for librarian/reviewer.

**docs/agentic-systems/platform/index.md** (64w)
- "Multi-tenant agentic AI platforms" framing — **not** covered by any
  existing Scope bullet (closest is "harness design", which is a distinct
  concern). Recommend adding a Scope bullet for platform/multi-tenancy, or
  folding under a new "Platform" hub sub-area.

**docs/agentic-systems/skill/index.md** (1578w)
- Rich prose (two-plane model, progressive disclosure, authoring
  guidance, discovery mechanics, placement table, security considerations)
  — all deep content, out of scope for a links-only hub; the corresponding
  MIGRATE targets carry it forward. Already covered by "Skills & tools
  design" Scope bullet at the framing level.
- One reusable framing line worth a hub blurb: "by mid-2026 the SKILL.md
  standard is natively supported by GitHub Copilot, VS Code, Codex CLI,
  Cursor, Antigravity, JetBrains Junie, and 20+ other tools" — useful
  one-line context for a Skills sub-section, not currently on the stub.

**docs/agentic-systems/skill/coding/index.md** (711w) /
**docs/agentic-systems/skill/enterprise/index.md** (606w)
- Both are companion-series navigation pages (12-part coding-assistant
  series / 11-part enterprise-platform series) with "who should read this"
  and part-by-part tables. No unique facts beyond "Skills & tools design"
  Scope bullet; all part-level content preserved via their MIGRATE rows.
  No unique content beyond series navigation — safe to drop, but the
  coding/enterprise split itself is a useful sub-grouping signal for the
  Target Structure below (two audiences: developer-facing vs.
  platform-layer skill governance).

**docs/agentic-ui/index.md** (2066w) — largest loser, flagged
`ascii_art_suspected=True`
- Extensive "Domain Map" (20-page cluster breakdown: Foundations &
  Evolution, Protocol Standards, Reference Architecture, Platform &
  Integration, Operations & Governance) and "Protocol Layer Map" — both
  ASCII-art diagrams, see Transform Notes. Not hub content itself.
- "Navigate by Role" table (Enterprise Architect / Principal AI Architect /
  AI Platform Lead / Security Architect / UX Lead / DevOps Engineer) —
  a useful persona-routing convenience not present on the stub; not
  strictly required for a links-only hub but worth a condensed one-line
  mention if a "Related" audience note is added.
- "What This Section Does NOT Duplicate" box — a scope-boundary list
  pointing at 10 cross-domain destinations (MCP deep dive, A2A protocol,
  HITL patterns, agent memory architecture, OWASP ASI taxonomy, guardrails
  framework, EU AI Act/NIST/ISO compliance, OTel GenAI observability,
  Entra 3LO auth, Kong AI Gateway). **Genuinely unique and not covered by
  the stub's Scope or Related lists** — these are exactly the kind of
  boundary-clarifying cross-links a hub should carry. All 10 targets are
  outside this cluster's rows (different domains/waves — protocols,
  data-knowledge, trust, cloud-platforms); flag for librarian/reviewer to
  confirm current dispositions before wiring into the new hub's "Related".
  "Agent UX and digital employees" Scope bullet is otherwise covered by
  this file's overall framing (chat→agentic→generative UI→ambient shift).

**docs/coding-tools/index.md** (9w)
- Single sentence, zero content. No unique content — safe to drop.

**docs/coding-tools/claude/index.md** (546w)
- Knowledge-guides table and certification-track table are pure
  wayfinding to MIGRATE/TRACK targets already itemized in mapping.csv; no
  unique facts. One notable framing note: the CCAF/CCA-F/CCAR-F naming
  ambiguity callout — useful context but belongs on the career-track
  destination page, not the hub. No Scope bullet currently names
  "coding assistants/tools" as a category — see Target Structure gap.

**docs/coding-tools/code-review/index.md** (72w)
- Bare 5-link wrapper to the PR Review Handbook volumes. No unique
  content — safe to drop.

**docs/coding-tools/github-copilot/index.md** (169w)
- Bare link list (Markdown guides, PDFs, GitHub Platform Deep Dive part
  series). No unique content — safe to drop.

**docs/multimodal-ai/index.md** (1370w)
- Executive summary, 15-part series table, "Quick Reference: Capability
  Matrix" (modality × model support table), and A.R.T. framework
  cross-reference are all deep content preserved via the 15 MIGRATE rows.
  **Multimodal AI as a topic area is entirely absent from the current
  stub's Scope** — this is the single biggest scope gap found in this
  cluster. Recommend a new Scope bullet/sub-section for multimodal
  perception (vision/audio/document) feeding agentic pipelines.
- "Related Sections" list has 6 cross-domain links (A.R.T. Framework,
  AI Foundations, Enterprise Architecture, AI Security Governance, Cloud
  Platforms, Knowledge & RAG) — outside this cluster; flag for
  librarian/reviewer before wiring any into the new hub's Related.

**docs/workflow-orchestration/index.md** (421w)
- "The Fundamental Shift" (BPM → Temporal durable execution → agentic
  adaptive workflows) and "Key Questions" framing are already covered by
  the stub's "Orchestration and workflow engines" Scope bullet at the
  category level; no new facts requiring hub-level preservation beyond
  confirming this sub-area needs its own labeled section (see Target
  Structure) rather than sitting silently under the generic Scope bullet.

## Target Structure

Keep `docs/agentic-systems/index.md` a short, curated, links-only hub.
This is the largest hub in the corpus (5 sub-domains feeding it); group
spokes by sub-area rather than flattening into one link dump. Proposed
final H2/H3 outline:

```
## Scope
## Agent Architectures & Multi-Agent Topologies
## Orchestration & Workflow Engines
## Memory
## Agent Skills
  ### Coding-Assistant Skills
  ### Enterprise Platform Skills
## Harness & Platform
## Agentic UI & Applications
## Multimodal AI
## Coding Tools
  ### Claude
  ### GitHub Copilot
  ### Code Review
## Standards & References
## Related
```

Comparison against current stub:
- `Scope`: expand from 7 to 9 bullets — add **platform/multi-tenancy**
  (currently uncovered; see `platform/index.md` finding) and **multimodal
  AI** (currently entirely uncovered; see `multimodal-ai/index.md`
  finding, the largest scope gap in this cluster).
- `Agent Architectures & Multi-Agent Topologies`, `Orchestration &
  Workflow Engines`, `Memory`: existing Scope bullets promoted to their
  own labeled H2s with a 1-line description each and bullet-links to the
  corresponding `core/*.md` / `orchestration/*.md` MIGRATE targets once
  they land in wave 3 — do not add links until those target pages exist.
- `Agent Skills`: new H2 with two H3s reflecting the coding-vs-enterprise
  split found in `skill/coding/index.md` and `skill/enterprise/index.md` —
  this mirrors the old repo's own audience separation and avoids
  flattening two different audiences (individual engineers vs. platform/
  governance teams) into one undifferentiated list.
- `Harness & Platform`: new H2 combining `harness/index.md` and
  `platform/index.md` (both currently thin, uncovered-by-name categories)
  plus `config/index.md`'s configuration-management link.
- `Agentic UI & Applications`: new H2 for the largest single loser
  (2066w); short description plus links to the 19 `agentic-ui/*.md`
  MIGRATE targets; carry forward the scope-boundary cross-links flagged
  above once librarian confirms their disposition.
- `Multimodal AI`: new H2 — closes the biggest content gap found in this
  review; links to the 15 `multimodal/*.md` MIGRATE targets.
- `Coding Tools`: new H2 with 3 H3s (Claude / GitHub Copilot / Code
  Review) mirroring the old `coding-tools/` subfolder split; links to the
  ~46 `coding-tools/*.md` MIGRATE targets. Certification/exam-prep content
  is explicitly excluded (TRACK-dispositioned to `docs/career/`, a
  different domain).
- `Standards & References`: new H2 — preserves the "Authoritative
  references" list from the old domain-root `agentic-systems/index.md`
  (MCP spec, A2A spec, OpenTelemetry GenAI semconv, OWASP prompt-injection
  guidance) that has no equivalent on the current stub.
- `Related`: keep existing 2 links (Protocols Hub, Data & Knowledge Hub);
  candidate additions (harness architecture deep-dive, memory/planning
  architecture, A.R.T. framework, agentic-ui scope-boundary cross-links)
  all point outside this cluster and need librarian/reviewer disposition
  confirmation first — do not add unconfirmed links.
- No prose sections beyond the existing one-paragraph intro should be
  added — hub stays links-only per `doc_type=hub`; each new H2 gets at
  most 1–2 sentences of framing before its link list.

## Transform Notes

- **ASCII-art → Mermaid (diagram-standards)** — flagged
  `ascii_art_suspected=True` for `docs/agentic-ui/index.md` only:
  - "Domain Map" — a 20-page cluster tree (5 clusters × 3-5 pages each,
    with nested bullet sub-points) rendered as an ASCII tree diagram.
  - "Protocol Layer Map" — a 5-layer box-and-arrow stack diagram (UI →
    AG-UI transport → A2UI surface → MCP/A2A/NLWeb/MCP-Apps branch layer
    → Oracle Open Agent Spec three-layer model).
  Neither diagram belongs on the hub itself (hub is links-only); this is a
  note for whoever runs `diagram-standards` on the corresponding MIGRATE
  destination (likely `docs/agentic-systems/agentic-ui/01-*.md` or a
  dedicated overview page among the 19 agentic-ui targets) so the ASCII
  art doesn't survive verbatim into the new corpus.
  All other 14 members in this cluster have `ascii_art False`, confirmed
  by direct read — no diagram-standards action needed for them.
- **Cross-repo links needing rewrite/verification** (point outside this
  cluster; flag for librarian/reviewer before wiring into hub sections):
  - `../../enterprise-architecture/ai-architecture/
    ai-harness-architecture-orchestration.md` (from `harness/index.md`).
  - `../../enterprise-architecture/ai-architecture/
    agent-memory-planning-architecture.md` (from `memory/index.md`).
  - From `agentic-ui/index.md`'s header "Related" line and "Scope
    Boundaries" box (10 targets): `../ai-protocols/index.md`,
    `../ai-protocols/mcp/MCP_Deep_Research_2026.md`,
    `../enterprise-architecture/ai-architecture/
    agent-interoperability-orchestration.md`,
    `../enterprise-architecture/ai-architecture/
    enterprise-ai-architecture-patterns.md`,
    `agentic-ai-security-identity.md`, `agentic-ai-security-guardrails.md`,
    `enterprise-ai-governance-compliance.md`,
    `agentic-ai-reliability-observability-governance.md`,
    `../ai-protocols/auth/entra-3lo-agent-auth-implementation.md`,
    `../cloud-platforms/ai-gateway/kong-ai-gateway-guide.md`.
  - From `multimodal-ai/index.md`'s "Related Sections":
    `../enterprise-architecture/ai-architecture/
    ART-Framework-Agentic-AI-Execution.md`, `../ai-foundations/index.md`,
    `../enterprise-architecture/ai-architecture/index.md`,
    `../ai-security-governance/index.md`, `../cloud-platforms/index.md`,
    `../knowledge-engineering/knowledge/index.md`.
  - Old-repo absolute-path links of the form
    `/knowledge-docs/agentic-systems/...` and
    `/knowledge-docs/coding-tools/...` throughout `harness/index.md`,
    `platform/index.md`, `skill` pages (none present — skill pages use
    relative links), `coding-tools/claude/index.md`,
    `coding-tools/code-review/index.md`, and
    `coding-tools/github-copilot/index.md` — internal old-site paths, not
    old-repo-relative; must resolve to the new `docs/agentic-systems/
    core/*.md` / `coding-tools/*.md` MIGRATE targets, not be carried over
    verbatim.

## Doc Type & Template

doc_type: `hub`. No template file exists for the `hub` type — per
`governance/DOC_TYPES.md`, a hub is "Links only canonical pages; curated,
not auto": no template — short curated hub page per
`governance/DOC_TYPES.md`.
