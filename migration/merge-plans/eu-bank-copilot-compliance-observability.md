# Merge Plan: eu-bank-copilot-compliance-observability

## Cluster

| | old_path | words | last_reviewed | source_type |
|---|---|---|---|---|
| Survivor | `docs/ai-usecases/eu-bank-ai-copilot-part4-compliance-infra-observability.md` | 2874 | 2026-07-17 | converted-pdf |
| Loser | `docs/ai-usecases/EU_Banking_AI_Agent_Evaluation_Framework.md` | 3670 | 2026-07-13 | converted-pdf |
| Loser | `docs/ai-usecases/EU_Banking_AI_Evaluation_Compliance_Guide.md` | 7840 | 2026-07-14 | converted-pdf |

- target canonical path: `docs/assets/04-eu-bank-copilot-compliance-observability.md`
- domain: `assets`
- wave: `8`

**Series context:** this cluster is Part 4 of the 4-part `eu-bank-copilot`
worked example (`series_name: "EU Bank AI Copilot Platform"`, `series_part: 4`,
`series_total: 4` in the survivor's frontmatter — it `Continues from` Part 3
per its own intro line). Full picture from `grep -n "eu-bank" migration/mapping.csv`:

- Part 1 — architecture & design decisions → `eu-bank-copilot-architecture` (not part of this cluster).
- Part 2 — sequence diagrams & code → `eu-bank-copilot-sequence-diagrams` (not part of this cluster).
- Part 3 — agent runtime, MCP & security → `eu-bank-copilot-runtime-security` (not part of this cluster; referenced only via the "Continues from" link).
- **Part 4 — compliance, infra & observability → `eu-bank-copilot-compliance-observability` (this plan).**
- The monolith `eu-bank-ai-copilot-complete.md` is `DROP` (superseded by the 4-part split) — its old `series_index` frontmatter field is now dangling, see Transform Notes.

**Cross-reference to the separate eval-framework cluster:** `grep -n "EU_Banking_AI_Agent_Evaluation_Framework\|agent-evaluation-framework" migration/mapping.csv`
confirms both loser files here are tagged `known-dup:eu-bank-copilot` (and, for
the first loser, *also* `known-dup:eval-framework`), and that the **general**
evaluation-framework cluster is a wholly separate mapping.csv cluster:

- `docs/agentic-ui/evaluation-framework.md` → MERGE-INTO `agent-evaluation-framework`
- `docs/ai-development/testing/AI_Agent_Evaluation_Framework_Complete.md` → **MIGRATE**, survivor of `known-dup:eval-framework`, target `docs/operations/01-agent-evaluation-framework.md`
- `docs/ai-development/testing/AI_Agent_Evaluation_Framework_Guide.md` → MERGE-INTO same survivor

That cluster is handled by another agent under its own merge plan. **This plan
does not redo that decision** — it only confirms (below) that the two losers
assigned to *this* cluster are correctly split between "general eval
methodology" (out of scope, belongs on the operations page) and "EU-Bank
compliance/infra/observability specifics" (in scope, belongs here), and it
adds one explicit cross-link from this page to that survivor for readers who
want the general framework.

## Survivor

Survivor per `migration/mapping.csv` is
`docs/ai-usecases/eu-bank-ai-copilot-part4-compliance-infra-observability.md`
(2874 words, converted-pdf, reviewed 2026-07-17 — the most recent of the
three by four and one day respectively).

Confirmed after reading all three files in full: both losers are much
longer (3670 and 7840 words — combined over 4x the survivor), and mapping.csv's
stated rationale holds cleanly:

- **Loser 1** (`EU_Banking_AI_Agent_Evaluation_Framework.md`) is, almost in its
  entirety, the *generic* Strands-Evals/AgentCore evaluation framework: seven
  evaluation dimensions (D1–D7), the full evaluator-class taxonomy, per-metric
  targets, a composite-scoring formula, a 5-gate CI/CD eval pipeline, and an
  instrumentation map. None of this is EU-Bank-copilot infrastructure or
  observability detail — it is the same evaluation methodology that the
  `known-dup:eval-framework` cluster's survivor
  (`AI_Agent_Evaluation_Framework_Complete.md` → `operations/01-agent-evaluation-framework.md`)
  already generalizes. Only the regulatory *labels* attached to each metric
  (EU AI Act article, GDPR article, DORA article) are EU-Bank-flavored; the
  mechanics are generic. This confirms the mapping.csv rationale for loser 1.
- **Loser 2** (`EU_Banking_AI_Evaluation_Compliance_Guide.md`) is a much
  broader Responsible-AI/regulatory-compliance guide (regulatory landscape,
  high-risk classification, RAI 7-pillars, fairness/XAI methodology, DPIA
  template, penalty tables, BCBS alignment). Most of this is also *general*
  EU-banking-AI compliance methodology, not specific to this platform's actual
  infrastructure — but a genuine minority of it **is** EU-Bank-copilot
  infra/observability-specific (the 3-layer PII detection architecture, the
  approved-region/regulator table, the compliance gate pipeline, the Art. 12
  audit-log schema, and the agentic/RAG-specific risk list — see Unique-Content
  Map). This is new information not in the survivor and not eval-framework
  boilerplate — it belongs here, not in `operations/01-agent-evaluation-framework.md`.

**Conclusion: recency-over-length holds, and the mapping.csv exclusion
rationale is correct** — the bulk of both losers' extra word count is either
(a) general eval-framework methodology correctly excluded to the operations
survivor, or (b) general regulatory/RAI reference material that belongs to
neither page in this pair (see "out of scope" note in Unique-Content Map). No
disagreement is flagged. A small, genuinely unique set of compliance/infra
facts from loser 2 (and one flag from loser 1) should still be folded in —
see Target Structure.

## Unique-Content Map

### `EU_Banking_AI_Agent_Evaluation_Framework.md` (3670 words)

Almost entirely out of scope (general eval-framework methodology — D1–D7
dimensions, evaluator taxonomy, composite-scoring formula, 5-gate CI/CD eval
pipeline, instrumentation map, AgentCore eval quotas — all belong to
`operations/01-agent-evaluation-framework.md`, not here). One item is
genuinely compliance/infra-relevant and should be carried forward:

1. Open verification flag: **"VERIFY Bedrock Guardrails EU PII entity
   coverage — IBAN, EU National ID, EU VAT Number, BIC/SWIFT Code"** (with
   Amazon Comprehend custom-entity / regex fallback noted). This is a direct,
   unresolved gap against the survivor's own §2.3 Bedrock Guardrails Terraform,
   which only implements `CREDIT_DEBIT_CARD_NUMBER`, `BANK_ACCOUNT_NUMBER`,
   and `PHONE` — no IBAN/VAT/National-ID/BIC entities. Worth a "Known Gap"
   callout in the merged page, not silent omission.

Everything else in this file (regulatory-overlay-to-dimension mapping,
D3/D4 config split, decision register D-001–D-005, Phoenix/EKS deployment
choice for the *evaluation* stack) is either eval-framework-generic or
describes the eval subsystem's own infra (Phoenix), not the copilot
platform's compliance/infra/observability — correctly out of scope here.

### `EU_Banking_AI_Evaluation_Compliance_Guide.md` (7840 words)

Most sections (regulatory landscape/timeline/penalties, high-risk
classification taxonomy, RAI 7-pillars framework, fairness/bias metric
formulas + counterfactual test code, XAI stakeholder levels, RAI/AML/credit
metrics catalogues, 3-level human-oversight framework, DPIA template,
regulatory reporting checklists, penalty/risk matrix, BCBS alignment) are
general EU-banking-AI compliance/RAI methodology, not specific to this
platform's infra — out of scope for this page. Genuinely unique
compliance/infra/observability facts, not in the survivor and not
eval-framework boilerplate:

1. **3-layer PII detection architecture** — AWS Comprehend + Microsoft
   Presidio (EU entities: IBAN, VAT, NHI, BSN, passport) + AgentCore Cedar
   policy for session-scoped access denial. Survivor's own PII handling
   (§4.4) is only 4 regex patterns — this is a materially more complete,
   platform-specific control stack.
2. **Approved-region / national-regulator table** — `eu-central-1` (BaFin/ECB),
   `eu-west-1`, `eu-west-3` (ACPR), `eu-north-1` (Finansinspektionen),
   `eu-south-1` (Banca d'Italia) — survivor only names two regions with no
   regulator rationale.
3. **6-gate automated compliance pipeline** (prohibited-practices → PII →
   fairness/bias → explainability → audit-trail → DORA-resilience), distinct
   from survivor's §2.2 security-focused CI/CD gate (SAST/SCA/secrets/IaC/
   container/SBOM) — a separate, compliance-purpose gate not present anywhere
   in the survivor.
4. **Art. 12 compliance audit-log JSON schema** (decision/evaluation_scores/
   human_review/compliance blocks; 10-year WORM retention) — distinct purpose
   from survivor's §4.4 operational telemetry log; complements rather than
   duplicates it.
5. **DORA Third-Party concentration-risk detail** — hard cap "no single LLM
   provider >70% of critical workload," with Anthropic and Arize Phoenix
   named as third parties requiring the same DORA Art. 28 assessment as AWS —
   adds detail survivor's DORA table (Art. 26 row) doesn't have.
6. **Agentic/RAG-specific risk list** — cross-customer RAG retrieval leakage,
   embeddings-as-personal-data (GDPR Art. 4(1)), action irreversibility,
   prompt-injection-via-tool-output, cascading hallucination, scope creep,
   cross-session memory persistence — ties directly to this platform's
   Strands/MCP/RAG design and complements Part 3's OWASP/threat-model
   content and this page's own observability section.
7. **Technical File (Art. 11 + Annex IV) documentation obligation** — 8-section
   structure, 10-year retention — a compliance documentation requirement not
   mentioned anywhere in the survivor.

## Target Structure

Combined raw word count is ~14,384, but per the Unique-Content Map above,
the large majority of both losers is out of scope (general eval-framework
methodology → operations survivor; general RAI/compliance reference material
→ neither page in this pair). The genuinely in-scope net-new content
(7 items from loser 2, 1 flag from loser 1) is estimated at **~500–800 words**
once compressed into tables/subsections rather than reproduced in full.
Estimated merged length: **~3,400–3,700 words** (survivor's 2874 + net-new).

This exceeds the general `doc-standards` ≤~2,000-word guideline, but that
guideline is explicitly advisory for a case-study that is already Part 4 of
an established 4-part series split (the same overage pattern accepted for
Part 1, at ~2300–2500 words per its own merge plan). **Recommendation: keep
as one page, do not split further.** Splitting a already-final part of a
fixed 4-part series (mapping.csv commits to a single `target_path` for this
cluster) would fragment the series structure for a ~500–800 word delta; the
new subsections below are additive, not a second topic.

Proposed H2/H3 outline for `docs/assets/04-eu-bank-copilot-compliance-observability.md`:

```
# EU Bank AI Copilot Platform — Part 4: Compliance, Infrastructure & Observability
(intro: "Continues from Part 3" link + new admonition: "For the general,
 cross-industry agent evaluation methodology this platform's eval stack
 builds on — dimensions, evaluators, CI/CD eval gates, composite scoring —
 see docs/operations/01-agent-evaluation-framework.md")

## 1. EU Regulatory Compliance
### 1.1 GDPR Controls                              (survivor, unchanged)
### 1.2 DORA Controls                              (survivor table + NEW: concentration-risk cap / Anthropic+Phoenix third-party row, from loser 2 item 5)
### 1.3 EU AI Act Readiness                        (survivor, + pointer to new §1.5 Technical File obligation)
### 1.4 PII Detection Architecture (NEW)           (3-layer: Comprehend + Presidio + Cedar — loser 2 item 1; supersedes/extends survivor §4.4's regex-only view)
### 1.5 Technical File & Documentation Obligations (NEW) (Art. 11/Annex IV 8-section structure — loser 2 item 7)

## 2. Infrastructure & Deployment
### 2.1 IAM Least Privilege Matrix                 (survivor, unchanged)
### 2.2 CI/CD Security Gate Pipeline                (survivor, unchanged — security-focused)
### 2.3 Automated Compliance Gate Pipeline (NEW)    (6 regulatory gates — loser 2 item 3; distinct from 2.2, cross-reference it)
### 2.4 Bedrock Guardrails (Terraform)              (survivor + Known Gap callout — loser 1 item 1: IBAN/VAT/National-ID/BIC coverage unverified)
### 2.5 Data Residency — Approved Regions (NEW)     (region/regulator table — loser 2 item 2)
### 2.6 Summary: End-to-End Call Flow               (survivor, unchanged, renumbered)

## 3. Operational Runbook                          (survivor §3.1–3.4, unchanged)

## 4. Observability & Monitoring
### 4.1–4.2 OpenTelemetry Instrumentation           (survivor, unchanged)
### 4.3 Key Dashboards & Alerts                     (survivor, unchanged)
### 4.4 Operational Telemetry Log Schema            (survivor's existing log schema, retitled for clarity against 4.5)
### 4.5 Compliance Audit-Trail Log Schema (NEW)     (Art. 12 schema — loser 2 item 4; cross-reference 4.4, note distinct purpose/retention)
### 4.6 Agentic & RAG-Specific Risk Considerations (NEW) (loser 2 item 6; cross-link to Part 3's OWASP/threat-model section)

## 5. Glossary                                      (survivor, unchanged)

## Related
    Part 1 (architecture), Part 2 (sequence diagrams), Part 3 (runtime & security),
    docs/operations/01-agent-evaluation-framework.md (general eval methodology — explicit cross-ref)
## Sources
```

## Transform Notes

- **Converted-PDF artifacts to strip (all 3 files are `converted-pdf`):**
  - Survivor: verify none of its 6 tables were column-shifted/row-wrapped by
    conversion; none observed on read, but re-check post-merge once new rows
    are spliced in.
  - Loser 1: plain-text ASCII architecture tree (`eu-central-1 (primary) / ...`
    block, lines 81–96) — `ascii_art_suspected: True` confirmed; this
    describes the *eval* stack's own infra (Phoenix/EKS/RDS) and is out of
    scope, so it does not need conversion, just confirm it is **not** copied
    in by accident.
  - Loser 2: multiple ASCII diagrams that **would** need `diagram-standards`
    conversion to Mermaid if any surrounding content is carried over — the
    regulatory-timeline bar chart (`2024 ████...`), the HITL workflow
    ASCII flowchart (§9.2), and the 6-gate compliance-pipeline ASCII boxes
    (§12.1, source for new §2.3 above). The gate-pipeline diagram specifically
    **is** being carried into the merged page (as new §2.3) — convert it to a
    proper Mermaid flowchart, do not paste the ASCII boxes.
  - Loser 2 also has raw LaTeX (`$$...$$`) fairness-metric formulas — not
    carried over (out of scope), but flag for whoever eventually homes the
    general fairness/XAI content that MDX/Docusaurus math rendering should be
    checked if reused elsewhere.
  - Escaped-brace artifacts from PDF conversion appear in the survivor too
    (e.g. `DELETE /users/\{id\}/data`, `tool_calls_total\{status="error"\}`) —
    unescape `\{`/`\}` to `{`/`}` throughout during migration.
- **Links needing rewrite:**
  - Survivor's "Continues from Part 3" link
    (`./eu-bank-ai-copilot-part3-agent-mcp-security.md`) → rewrite to
    canonical `docs/assets/03-eu-bank-copilot-runtime-security.md`.
  - Survivor's closing "see the series index" link
    (`./eu-bank-ai-copilot-complete.md`) → dangling, since that monolith is
    `DROP`'d; replace with a link to a Part 1–4 hub/index if one exists in
    the target IA (e.g. `hub-assets.md`'s target), else drop the sentence.
  - Frontmatter `series_index: "ai-usecases/eu-bank-ai-copilot-complete"` →
    same monolith problem; update or drop the field.
  - **New required link:** add the explicit cross-reference admonition (see
    Target Structure intro) pointing to
    `docs/operations/01-agent-evaluation-framework.md` for readers who want
    the general evaluation-dimension/evaluator/CI-CD-eval-gate methodology
    that this page deliberately does not repeat.
- **Diagram-standards flag:** yes — new §2.3 (compliance gate pipeline) should
  be authored as a Mermaid flowchart per `diagram-standards`, not ported as
  ASCII boxes from loser 2 §12.1. No other new Mermaid is strictly required;
  survivor's `mermaid_count: 0` sections are all tables, which is acceptable
  for this doc_type.

## Doc Type & Template

- `doc_type: case-study` (survivor's current frontmatter says
  `multi-part-series`, which is not in the `governance/DOC_TYPES.md`
  taxonomy — `case-study` is correct: "Applied example", 365d freshness SLA).
- **FLAG: no case-study template exists.** `.claude/skills/doc-standards/templates/`
  contains only `concept.md`, `decision-adr.md`, and `reference-architecture.md`
  — no `case-study.md`. This is the same gap already flagged on the Part 1
  merge plan (`migration/merge-plans/eu-bank-copilot-architecture.md`); it
  applies to all 4 parts of this series and is not re-raised as a new issue
  here, just confirmed still open. The migrator should follow generic page
  anatomy (frontmatter → context paragraph → body → Related → Sources) until
  a `case-study.md` template is added upstream.
