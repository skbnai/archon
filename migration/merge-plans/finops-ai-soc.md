# Merge Plan: finops-ai-soc

## Cluster

| old_path | words | last_reviewed | source_type | status_field | disposition |
| --- | --- | --- | --- | --- | --- |
| `docs/ai-soc-playbooks/part-12-finops.md` | 2227 | 2026-07-16 | pdf-converted | current | MIGRATE (survivor) |
| `docs/databricks-agentic-ai/part-12-finops.md` | 9 | 2026-07-16 | native-md | current | MERGE-INTO (loser) |

- **target_topic_id:** `finops-ai-soc`
- **target canonical path:** `docs/operations/02-finops-ai-soc.md`
- **domain:** operations
- **wave:** 8
- Registry check: `governance/CANONICAL_REGISTRY.yaml` (~line 3462) already registers this
  `topic_id` with `canonical: docs/operations/02-finops-ai-soc.md` and
  `supersedes: [docs/databricks-agentic-ai/part-12-finops.md]`. No registry change is
  needed for this plan.

**Deliberate cross-domain split, not an inconsistency:** every other part of the
`ai-soc-playbooks` series (parts 01–11, 13, 14) lands in `docs/trust/ai-soc-playbooks/`
per `mapping.csv` — this is the only member of that 14-part series that moves to
`docs/operations/`. That is intentional per doctrine ("FinOps unifies under
docs/operations per doctrine, even though the rest of this series stays in trust") and
is consistent with the wider wave-8 pattern: every other FinOps-titled old file across
the corpus (databricks part-12, the enterprise-architecture FinOps sub-topics, etc.)
also lands under `docs/operations/`. This plan does not attempt to pull the page back
into `docs/trust/ai-soc-playbooks/` for series consistency — that would contradict the
registry and the cross-cutting-topic doctrine.

## Survivor

**Survivor = `docs/ai-soc-playbooks/part-12-finops.md`** (2227 words,
`source_type: pdf-converted`, `last_reviewed: 2026-07-16`, `status: current`).

Having read both files in full, this is not a close call:

- The survivor is a complete, structured FinOps chapter: 7 numbered sections covering
  token cost anatomy, prompt-caching economics, full cost-at-scale modeling (8,000
  alerts/day), a model-routing strategy with Python reference code, an ROI framework
  (traditional-SOC-vs-AI-SOC comparison plus a `SOCROICalculator` class), a
  cost-optimization playbook (batch processing, prompt-template lean-out, response
  caching), and a cost-governance/budgeting section with a monthly budget table and a
  live FinOps dashboard mock. It ends with a `Related`/`Next` link footer.
- The loser (`docs/databricks-agentic-ai/part-12-finops.md`) is, verified by reading
  the actual file, **9 words total**: front matter (`title`, `date`, `date_created`,
  `last_reviewed`, `status: current`, `source_type: native-md`, `source_file`, `tags`)
  plus a single H1 line (`# Part 12 — AI SOC FinOps & ROI`). There is no body at all —
  no sections, no prose, no code, nothing past the heading.

Recency ties (both `last_reviewed: 2026-07-16`) so the decision rests entirely on
completeness, and the loser has none. Survivor confirmed:
`docs/ai-soc-playbooks/part-12-finops.md`.

## Unique-Content Map

Read the loser file in full (all 11 lines, both files quoted above). As expected for a
9-word file, there is **no unique content — safe to drop.**

- No body content exists past the H1 to compare against the survivor.
- The only thing the loser contributes that the survivor's front matter doesn't
  already cover is a slightly different tag set (`tags: ["finops", "roi", "soc",
  "cost-optimization", "tco", "kpis"]` vs. the survivor's `["finops",
  "cost-optimization", "token-budget", "roi", "model-routing"]`) and the alternate
  title `"AI SOC FinOps & ROI"` vs. the survivor's `"Part 12 — AI SOC FinOps & Cost
  Management"`. Both are already captured: the registry's `aliases` for `finops-ai-soc`
  records the survivor's title as the alias, and the loser's distinct tags (`tco`,
  `kpis`) are reasonable additions to the new page's `tags` field (see Transform Notes)
  even though there's no prose to carry forward.
- **Conclusion: drop the loser entirely.** Nothing beyond a tag/alias nudge survives
  from it.

## Target Structure

Survivor structure checked for converted-pdf damage: no stray `\f` form-feed
characters, no literal "Page N of N" footer/header artifacts, and no
broken/merged table cells were found in the numbered-list or budget-table sections.
However, `ascii_art_suspected: True` is confirmed on inspection — the file contains
five large fenced "plain code block" diagrams built from box-drawing-style ASCII
(`════`, `─────`, `TOKEN COST ANATOMY`, `AI SOC FINOPS DASHBOARD`, the SOC
cost-comparison block, the monthly budget table, and the FinOps dashboard mock) that
render as monospace text art rather than semantic tables/diagrams. These need
`diagram-standards` conversion (see Transform Notes) rather than verbatim carry-over.

Proposed H2/H3 outline for `docs/operations/02-finops-ai-soc.md` (mirrors the
survivor's existing 7-section structure, which is sound and doesn't need
reorganizing — only artifact cleanup and front-matter/link conversion):

```
# AI SOC FinOps & Cost Management

(1-paragraph "why this matters" intro — replaces the bare audience/related line under the H1)

## AI SOC Cost Model
### Token Cost Breakdown (per-alert cost anatomy — convert ASCII block to a real table)
### Anthropic Ephemeral Cache: Input Cost Reduction

## Full Cost Model at Scale
### Daily Cost at Enterprise Alert Volume (convert ASCII scenario block to a table)

## Model Routing Strategy
### Intelligent Model Selection (SOCModelRouter reference code)

## ROI Calculation Framework
### Traditional SOC vs. AI SOC Cost Comparison (convert ASCII comparison block to a table)
### ROI Calculator Reference Code (SOCROICalculator)

## Cost Optimization Playbook
### Batch Processing for Non-Urgent Alerts
### Token Reduction via Structured Templates
### Response Caching for Identical Alerts

## Cost Governance and Budgeting
### Monthly Budget Structure (convert ASCII budget table to a real Markdown table)
### Automated Cost Alerting (CostGovernanceAgent reference code)

## FinOps Dashboard (convert ASCII dashboard mock to a real table + callouts)

## Related
## Sources
```

**Word count / split decision:** 2227 words is ~11% over the ~2000-word soft limit —
a mild overage, not a multi-topic sprawl. Recommendation is **trim, not split**:

- This is one coherent topic (AI SOC cost model, routing, ROI, optimization,
  governance are all facets of the same FinOps discipline for one system), and the
  registry has already fixed a single canonical path/topic_id — splitting would
  require new `topic_id`s that don't exist, which is out of scope for planning.
- A meaningful share of the word count is in the five ASCII-art blocks themselves
  (raw arithmetic walked out line-by-line, e.g. the per-alert and daily-cost
  calculations). Converting those to compact Markdown tables per Transform Notes
  will recover a large fraction of the ~230-word overage as a side effect of the
  mandatory artifact cleanup, likely bringing the page close to or under 2000 words
  without deliberately cutting substantive content.
- If word count is still over budget after table conversion, the next trim
  candidate is condensing the two full Python reference-code blocks
  (`SOCModelRouter`, `SOCROICalculator`) to their signatures plus a short
  prose summary of behavior, since both are illustrative rather than
  copy-paste-ready production code. Not proposing a structural split for this wave.

## Transform Notes

- **Converted-PDF / ASCII-art artifacts to strip or convert:** the five fenced
  ASCII-art blocks (token cost anatomy, daily-cost-at-scale scenario, the
  traditional-vs-AI-SOC comparison, the monthly budget framework, and the FinOps
  dashboard mock) all use `════`/`─────` box-drawing characters and column-aligned
  plain text standing in for tables and a dashboard visual. Flag for
  `diagram-standards` conversion: the budget framework and dashboard mock convert
  cleanly to Markdown tables (they're already tabular data dressed as ASCII); the
  cost-anatomy and cost-comparison blocks are sequential arithmetic walk-throughs and
  are better served as a Markdown table (inputs/outputs/cost columns) plus a short
  worked-example callout rather than a diagram. None of the five are actual
  topology/sequence/architecture diagrams, so no Mermaid diagram is mandated by
  doc-standards for this page — the fix here is de-ASCII-ing tabular data, not adding
  a C4 diagram.
- **Front matter conversion:** old fields `date`, `date_created`, and `source_file`
  do not exist in the new schema and should be dropped. `supersedes` in the new front
  matter should list both old paths: `docs/ai-soc-playbooks/part-12-finops.md` and
  `docs/databricks-agentic-ai/part-12-finops.md`. `tags` should carry forward the
  survivor's tags (`finops`, `cost-optimization`, `token-budget`, `roi`,
  `model-routing`) and may fold in the loser's non-duplicate tags (`tco`, `kpis`) if
  they exist in the controlled tag vocabulary — verify against doc-standards' allowed
  tag list before adding.
- **Links needing rewrite (in-domain):** the survivor's `**Related:**` line links to
  `part-06-ai-models.md` and `part-08-observability.md` as sibling files. Per the
  registry these are now **cross-domain** targets:
  `docs/trust/ai-soc-playbooks/06-part-06-ai-models.md` (topic_id
  `part-06-ai-models`) and `docs/trust/ai-soc-playbooks/08-part-08-observability.md`
  (topic_id `part-08-observability`) — both now live in the `trust` domain while this
  page lives in `operations`. These must be rewritten as cross-domain relative links
  (e.g. `../trust/ai-soc-playbooks/06-part-06-ai-models.md`), not left as same-folder
  relative links, since they no longer share a folder with this page.
- **Links needing rewrite (in-domain, same-domain):** this page should also link to
  `docs/operations/01-agent-evaluation-framework.md` (topic_id
  `agent-evaluation-framework`) in its `## Related` section — the AI SOC cost model
  depends on evaluation/automation-rate assumptions (e.g. the "78.3% automation rate"
  and cost-per-alert figures in the dashboard section) that tie directly to that
  page's evaluation framework. This is a same-domain link, ordinary relative path.
- **Cross-domain hub link — call out explicitly:** this page should also link back to
  the trust-domain AI-SOC hub context, since 13 of the 14 `ai-soc-playbooks` parts
  live under `docs/trust/` and readers arriving at the FinOps page will expect a way
  back to the rest of the series. There is no dedicated `ai-soc-playbooks` hub page in
  the registry (the old `docs/ai-soc-playbooks/index.md` was folded into
  `hub-trust`, i.e. `docs/trust/index.md`), so the correct target is
  `docs/trust/index.md` (topic_id `hub-trust`), not a nonexistent
  `docs/trust/ai-soc-playbooks/index.md`. **This is a deliberate cross-domain
  link (operations → trust) and should be flagged as such in a code comment or
  admonition when the page is built** (e.g. "This page is part of the AI SOC
  Playbooks series; the rest of the series lives in the Trust domain — see
  Trust Hub"), so a future corpus-consistency pass doesn't mistake it for a
  broken/misplaced link.
- **Numeric/pricing content flag:** the page contains extensive per-1k-token model
  pricing (`claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-8` at specific
  $/1k rates) and dated dashboard figures ("JULY 2026" MTD spend). This is exactly
  the kind of versioned/pricing claim `research-grounding` is meant to catch — flag
  for a grounding pass at build time so stale pricing isn't carried forward silently;
  not resolved by this planning-only pass.

## Doc Type & Template

Old front matter used no `doc_type` field at all (`source_type: pdf-converted` is not
a doc type). Between the two candidates suggested by the content:

- **`runbook`** doesn't fit well: a runbook is procedural/operational
  ("do these steps when X happens"), and while the Cost Governance section has one
  operational procedure (`CostGovernanceAgent`'s budget-threshold response), that's a
  small fraction of the page. The bulk of the content — cost modeling, ROI
  frameworks, optimization strategy — is explanatory/decision-support, not a
  step-by-step incident procedure.
- **`guide` fits better**: the page's dominant purpose is "how to model, calculate,
  and optimize AI SOC costs" — a practitioner how-to with worked examples and
  reference code, matching `guide`'s definition more closely than `runbook`'s
  narrower procedural scope. This is consistent with the "Playbooks" series framing
  (playbooks-as-guides) and with cost-management content elsewhere in this wave
  (e.g. `finops-cost-management-overview` is also framed as a guide-style umbrella
  doc).

**Recommended `doc_type: guide`.**

Flag: `.claude/skills/doc-standards/templates/` currently contains only
`concept.md`, `decision-adr.md`, and `reference-architecture.md` — **no `guide.md`
template exists yet**, despite `guide` being a valid type in `DOC_TYPES.md`. This is
the same gap already flagged by the `auth-standards-reference` merge plan in this
wave; it is outside this merge plan's scope (I own only this one file) but the
stage-04 migrator/doc-standards owner will need a `guide.md` template added (or an
explicit fallback decision) before this page — and others slated as `guide` — can be
produced.
