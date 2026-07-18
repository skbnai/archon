# Merge Plan: agent-evaluation-framework

## Cluster

| old_path | words | last_reviewed | source_type | status_field | ascii_art_suspected |
|---|---|---|---|---|---|
| docs/agentic-ui/evaluation-framework.md | 10321 | 2026-07-10 | native-md | current | True |
| docs/ai-development/testing/AI_Agent_Evaluation_Framework_Complete.md | 9194 | 2026-07-16 | pdf-converted | current | True |
| docs/ai-development/testing/AI_Agent_Evaluation_Framework_Guide.md | 85 | 2026-07-14 | pdf-converted | archived | False |

- target_topic_id: `agent-evaluation-framework`
- target_path: `docs/operations/01-agent-evaluation-framework.md`
- domain: `operations`
- wave: 8

Already registered in `governance/CANONICAL_REGISTRY.yaml` (line ~3453) with
this exact canonical path and `supersedes:` listing both loser paths — no
registry gap for the parent topic_id itself. Confirmed via grep.

**Domain reassignment note:** two of the three members physically lived
under `agentic-ui/` and `ai-development/testing/` in the old repo, but the
cluster lands in `operations` per mapping.csv rationale ("Lands in
operations — evaluation hub + benchmark catalog scope"). This is intentional:
`governance/TAXONOMY.md` defines `operations` as owning "evaluation hub +
benchmark catalog" city-wide, and this cluster is the single largest,
most complete evaluation-methodology content in the corpus — it belongs at
the hub, not scattered under UI or dev-testing sections. Not an error.

## Survivor

**Survivor = `docs/ai-development/testing/AI_Agent_Evaluation_Framework_Complete.md`**
(9194 words, `pdf-converted`, `last_reviewed: 2026-07-16`) — confirmed as
correct MIGRATE pick per mapping.csv rationale (most recent review date).

**Investigation: survivor is shorter (9194w) than the loser it beats
(`agentic-ui/evaluation-framework.md`, 10321w) — is "most complete" still
justified?**

Read both files in full. Finding: **the two documents are not competing on
the same scope — they cover genuinely different evaluation layers, and the
mapping.csv "most complete" label is accurate only for backend/agent-level
evaluation, not for the corpus as a whole.**

- The survivor is complete and deep on: cloud-provider managed eval services
  (AWS AgentCore / Azure AI Eval / Vertex AI Eval), the SDK/framework
  landscape (DeepEval, RAGAS, Phoenix, LangFuse, Strands, 13-tool matrix),
  observability/OTel instrumentation, the full metric catalogue (45+
  metrics), drift detection, LLM-as-Judge bias/calibration, EU AI Act /
  GDPR / DORA / NIST regulatory compliance, the 9-phase lifecycle, and
  computer-use agent evaluation. This is genuinely the most complete
  treatment of **backend agent evaluation + compliance** in the corpus.
- The loser (`agentic-ui/evaluation-framework.md`) explicitly frames itself
  in its own intro as a **companion** document: "covering the AGUI/UX
  evaluation layer not addressed by backend agent evaluation... For
  agent-level evaluation... see the companion guide." Its bulk (10321w)
  comes from UX/business content the survivor never attempts: UX metrics
  (CSAT/NPS/trust calibration/abandonment), business ROI calculation, three
  full quantitative scorecards (A/B/C, 60 total scoreable rows), a 25-item
  evaluation anti-patterns catalogue, and a daily/weekly/monthly/quarterly
  evaluation calendar.

**Disagreement flagged:** the word-count-based "most complete" framing in
mapping.csv is misleading taken at face value — the loser is not padding or
duplicate content, it is a different, non-overlapping scope that the
survivor lacks entirely. The MIGRATE/survivor **pick itself is still the
right call** (the operations-domain evaluation hub should be anchored on the
backend/compliance treatment, and the UI-layer content is a genuine
sub-topic, not the hub's spine) — but treating the loser as safely
"folded in and mostly discarded" would be wrong. Its unique content is
substantial and must be preserved via the split proposed below, not
summarized away.

## Unique-Content Map

### docs/agentic-ui/evaluation-framework.md (10321w) — genuine unique content, do not undersell

- §2 Evaluation Taxonomy: 18-dimension table incl. UX Quality, Governance,
  User Trust, Adoption, ROI — dimensions absent from survivor entirely.
- §3 UX Evaluation (full): CSAT/NPS adapted for agentic UX, Task Success
  Rate 5-tier classification (Full/Partial/Assisted/Failed/Harmful),
  time-on-task & productivity metrics, error/correction signals, **Trust
  Calibration model** (over-trust vs under-trust framework), abandonment &
  streaming-UX metrics (TTFT, mid-stream cancellation), approval-workflow
  usability metrics, usability testing protocol for agentic UIs.
- §5 Tool Quality Evaluation: tool selection confusion-matrix method, tool
  parameter quality metrics, tool chaining metrics, 4-category tool-call
  error taxonomy (Selection/Parameter/Sequencing/Environmental) — more
  granular than survivor's single agentic-behaviour table.
- §7.2 Red Team Evaluation Protocol — agentic-UI-specific 6-phase protocol
  (incl. UX-level attacks: fake approval prompts, silent action execution)
  not in survivor's compliance-focused adversarial coverage.
- §8.2 LLM-as-Judge concrete prompt templates (Faithfulness / Task
  Completion / Safety judges, full JSON output schemas) — survivor has
  bias/calibration theory but no ready-to-use prompt templates.
- §9 Human Evaluation: rater calibration protocol (gold-set construction,
  Krippendorff's α onboarding gate), inter-rater reliability target table.
- §10 Quantitative Scorecards A/B/C: 20-dim quality scorecard, 25-gate
  production-readiness checklist, 15-dim UX scorecard — entirely unique.
- §11.1 CI/CD eval pipeline (4-stage: unit/golden/integration/production) —
  **overlaps with the separately-registered `agent-testing-monitoring-evaluation`
  topic** (docs/operations/12-..., sourced from a different old file,
  `Agent_Testing_Monitoring_Evaluation.md`, whose own Related-link
  description is "test pyramid, CI/CD gate patterns, and production
  monitoring architecture"). Do not duplicate this pipeline diagram in the
  new split — cross-link to topic 12 instead.
- §12 Business Value Evaluation: productivity/FTE-savings formulas, full ROI
  calculation template, adoption metrics (DAU/MAU, power-user threshold) —
  entirely unique.
- §13 Evaluation Anti-patterns: 25-item catalogue with mitigations —
  entirely unique, high value.
- §14 Evaluation Calendar Template: daily/weekly/monthly/quarterly cadence
  — entirely unique.

### docs/ai-development/testing/AI_Agent_Evaluation_Framework_Guide.md (85w, archived)

- No unique content. The file is a one-paragraph stub that already declares
  itself superseded and links to the survivor, listing the survivor's own
  chapter coverage. Safe to drop entirely — nothing to carry forward beyond
  the redirect, which the registry `supersedes:` entry already handles.

## Target Structure

Combined unique content (survivor ~9194w minus PDF scaffolding, plus ~6000w+
of genuinely unique loser content) is far over the ~2000-word soft limit.
Propose a split: `docs/operations/01-agent-evaluation-framework.md` becomes
a lightweight parent/overview page linking into a
`docs/operations/agent-evaluation-framework/` child series (depth-3, same
pattern already used for `docs/trust/ai-security-governance/NN-*.md`).

**Parent — `docs/operations/01-agent-evaluation-framework.md`** (existing
topic_id, no new registration needed) — reference-architecture, ~1800w:
- H2 The Evaluation Problem (nondeterminism — merged framing from both)
- H2 Framework Architecture — Four-Layer Component Map (Mermaid)
- H2 Evaluation Hierarchy — Session / Trace / Tool (Mermaid, was ASCII)
- H2 Which Tool for Which Job (decision table + Mermaid decision tree)
- H2 Evaluation Taxonomy at a Glance (18-dim summary, links out — notes
  explicitly that UX/business dimensions live in the UX child page)
- H2 Related (links to all child pages below + topic 12 + resolved
  cross-domain links)

**Child pages (NEEDS LIBRARIAN REGISTRATION — new topic_ids, none exist yet):**

| # | Proposed topic_id | Path | Source content | doc_type |
|---|---|---|---|---|
| 1 | `agent-eval-metric-catalogue` | `.../02-metric-catalogue.md` | Survivor Ch5 + Ch12.2 threshold card | reference-architecture |
| 2 | `agent-eval-cloud-provider-services` | `.../03-cloud-provider-services.md` | Survivor Ch3 + Ch11 (multi-cloud) | reference-architecture |
| 3 | `agent-eval-observability-drift` | `.../04-observability-drift-detection.md` | Survivor Ch4 + Ch7 (drift + remediation) | reference-architecture |
| 4 | `agent-eval-llm-as-judge` | `.../05-llm-as-judge-patterns.md` | Survivor Ch8 (biases/calibration) + Loser §8.2/8.3 (prompt templates, meta-eval) | guide |
| 5 | `agent-eval-benchmark-lifecycle-compliance` | `.../06-benchmark-lifecycle-compliance.md` | Survivor Ch6 (benchmarks) + Ch9 (compliance) + Ch10 (lifecycle) | reference-architecture |
| 6 | `agent-eval-ux-and-business-value` | `.../07-ux-and-business-value.md` | Loser §3 (UX) + §5 (tool quality detail) + §12 (business/ROI) — all unique | guide |
| 7 | `agent-eval-scorecards-anti-patterns` | `.../08-scorecards-anti-patterns-cadence.md` | Loser §10 (scorecards) + §13 (anti-patterns) + §14 (calendar) + §7.2 (red-team-UI) — all unique | checklist |

**Overlap check against existing operations/agentic-systems registry
entries (grepped `governance/CANONICAL_REGISTRY.yaml`):**
- `agent-testing-monitoring-evaluation` (`docs/operations/12-...`, sourced
  from a different old file entirely) covers test pyramid / CI/CD gate
  patterns / production monitoring. Proposed child #7 must **cross-link,
  not duplicate**, the CI/CD pipeline content (loser §11.1) — flagged above
  in Unique-Content Map. No true duplicate created as long as #7 omits the
  4-stage pipeline diagram and only links to topic 12.
- `evaluation-reusability-deduplication` (`docs/agentic-systems/core/27-...`,
  sourced from `docs/agentic-systems/skill/coding/11-evaluation-reusability-
  deduplication.md` — a different domain, about skill/coding eval reuse and
  dedup) has no scope overlap with this cluster's metric/UX/compliance
  content. No conflict.

## Transform Notes

**PDF artifacts to strip from survivor:**
- Manual "Table of Contents" chapter/section listing (lines 21-36) —
  redundant with Docusaurus auto-generated sidebar/TOC; drop.
- All-caps `CHAPTER N — TITLE` H2 headings — rewrite as clean sentence-case
  H2s without chapter numbering (chapters become child-page boundaries
  instead).
- Cover blockquote block (`> **Audience:** ... > **Coverage:** ... > **As
  of:**`) — fold `As of: July 2026` into `covers_version` frontmatter;
  fold Audience into `personas` frontmatter; drop the raw blockquote.
- Trailing `*Sources: ...*` prose citation dump (final line) — convert to
  `sources:` frontmatter list per research-grounding conventions rather
  than a prose paragraph, or drop if citations can't be individually
  verified during migration (flag for researcher).

**ASCII-art → Mermaid (flag "diagram-standards") — all 3 members flagged
`ascii_art_suspected=True`; checked each individually:**
- Survivor: confirmed present — self-hosted reference architecture box
  diagram (§11.2), automated remediation pipeline flow (§7.2, `Drift
  Monitor → Alert → Message Bus → Remediation Worker`), evaluation
  hierarchy nested box (§2.7, Session/Trace/Tool). All three need Mermaid
  (flowchart + nested subgraph) conversions.
- `agentic-ui/evaluation-framework.md`: confirmed present — evaluation
  pyramid (§1.2, 4-tier box), continuous eval regression tracking flow
  (§1.4), trust calibration failure-mode box (§3.5), 4-stage CI/CD pipeline
  (§11.1, overlaps topic 12 — convert there, not here), task success
  5-tier classification block (§3.2, mostly a formatted list — check
  whether it needs to be a real diagram or just a table).
- `AI_Agent_Evaluation_Framework_Guide.md`: cluster data marks
  `ascii_art_suspected=False` — confirmed on read, file is a 4-line prose
  stub with no diagrams. Nothing to convert.

**Links needing rewrite** (old relative paths → resolved new canonical
paths per `migration/mapping.csv` grep):
| Old link (in survivor or loser) | Resolved target |
|---|---|
| `./Agent_Testing_Monitoring_Evaluation.md` | `docs/operations/12-agent-testing-monitoring-evaluation.md` |
| `./AI_Agent_Evaluation_Framework_Guide.md` / `../../agentic-ui/evaluation-framework.md` | drop — both are cluster members merged into this page, not external links |
| `../../ai-usecases/EU_Banking_AI_Evaluation_Compliance_Guide.md` | `docs/assets/04-eu-bank-copilot-compliance-observability.md` (MERGE-INTO target, not a standalone page — link to the merged destination) |
| `observability.md` (agentic-ui) | `docs/agentic-systems/agentic-ui/14-observability.md` |
| `../enterprise-architecture/ai-architecture/enterprise-ai-governance-compliance.md` | `docs/architecture/51-enterprise-ai-governance-compliance.md` |
| `../enterprise-architecture/ai-architecture/agentic-ai-reliability-observability-governance.md` | `docs/architecture/43-agentic-ai-reliability-observability-governance.md` |
| `../enterprise-architecture/ai-architecture/agentic-ai-security-identity.md` | `docs/trust/05-agentic-ai-security-identity.md` |

Also convert the loser's mkdocs-material `=== "Tab Title"` tab syntax
(§8.2 judge prompt templates) to Docusaurus `<Tabs>`/`<TabItem>` components
per page-styling — it is not valid Docusaurus MDX as-is.

## Doc Type & Template

Parent page `doc_type: reference-architecture` — this is fundamentally a
blueprint of the evaluation framework (four-layer component map, pipeline
topology, drift/remediation flow) rather than a linear how-to, it requires
multiple Mermaid diagrams (satisfied by the ASCII conversions above), and a
trade-offs section fits naturally (tool/cloud-provider selection guidance
already present in survivor Ch3.5/Ch12.3). Template:
`.claude/skills/doc-standards/templates/reference-architecture.md`.

Child pages vary by content shape (see Target Structure table): most are
also `reference-architecture` (metric catalogue, cloud services,
observability/drift, benchmark/lifecycle/compliance — all blueprint-shaped
with required diagrams); the LLM-as-judge and UX/business-value pages fit
`guide` better (procedural: how to build/calibrate a judge, how to run a
UX eval); the scorecards/anti-patterns/cadence page fits `checklist`
(scoreable items, gate/review list) best. No `guide` or `checklist`
template currently exists under
`.claude/skills/doc-standards/templates/` (only `concept.md`,
`decision-adr.md`, `reference-architecture.md` are present) — flag for the
librarian/doc-standards owner that `guide` and `checklist` templates need
to be added before stage-04 migration executes this plan's child pages.
