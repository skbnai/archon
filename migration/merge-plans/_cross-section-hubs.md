# Cross-Section Overlap Themes — Hub/Spoke Designations

Stage-03 requirement: for themes that recur as separately-registered `topic_id`s across
multiple domains in `governance/CANONICAL_REGISTRY.yaml`, name ONE canonical hub/entry-point
per theme and demote the rest to spokes. **This is a navigation decision only** — no page
listed below is merged, deleted, or re-registered. Every topic_id stays exactly as it is in
the registry, with its own canonical path. The only follow-up action implied by this document
is: spoke pages should carry an "up" link to their theme's designated hub, and the hub page
should link down to its spokes.

This file is read-only input for humans/librarian; it does not modify
`governance/CANONICAL_REGISTRY.yaml`, `migration/mapping.csv`, or `migration/inventory.csv`.

Method: `grep`-derived from `governance/CANONICAL_REGISTRY.yaml` (616 topics, 11 domains) —
matches are on `id`/`aliases` fields only (canonical-path substrings were excluded from
matching to avoid false positives from shared directory names, e.g. every chapter filed under
`docs/trust/ai-security-governance/` would otherwise match "security" regardless of content).

15 themes covered: security, FinOps, memory, evaluation, observability, MCP, anti-patterns,
glossary, interview, identity & authentication, RAG, orchestration, compliance,
responsible AI / safety & guardrails, A2A (agent-to-agent protocol).

---

## 1. Security

Spans 6 domains: strategy, agentic-systems, protocols, platforms, trust, assets.

| id | domain | canonical |
|---|---|---|
| part-13-security-model | strategy | docs/strategy/23-part-13-security-model.md |
| governance-responsible-ai-and-security | strategy | docs/strategy/39-governance-responsible-ai-and-security.md |
| agentic-ui-security-architecture | agentic-systems | docs/agentic-systems/agentic-ui/19-agentic-ui-security-architecture.md |
| cicd-secrets-security | agentic-systems | docs/agentic-systems/coding-tools/01-cicd-secrets-security.md |
| security-governance | agentic-systems | docs/agentic-systems/coding-tools/02-security-governance.md |
| harness-security-supplychain-observability | agentic-systems | docs/agentic-systems/core/06-harness-security-supplychain-observability.md |
| governance-and-security | agentic-systems | docs/agentic-systems/core/26-governance-and-security.md |
| agent-skills-security-architecture | agentic-systems | docs/agentic-systems/core/36-agent-skills-security-architecture.md |
| part-07-security-threats | agentic-systems | docs/agentic-systems/multimodal/07-part-07-security-threats.md |
| workflow-orchestration-security-architecture | agentic-systems | docs/agentic-systems/orchestration/17-workflow-orchestration-security-architecture.md |
| entra-3lo-agent-auth-security-review | protocols | docs/protocols/10-entra-3lo-agent-auth-security-review.md |
| mcp-enterprise-security-governance-operations-2026 | protocols | docs/protocols/14-mcp-enterprise-security-governance-operations-2026.md |
| k8s-handbook-part8-security | platforms | docs/platforms/41-k8s-handbook-part8-security.md |
| part-07-security-architecture | platforms | docs/platforms/47-part-07-security-architecture.md |
| a2a-security-governance | trust | docs/trust/02-a2a-security-governance.md |
| agentic-ai-security-guardrails | trust | docs/trust/04-agentic-ai-security-guardrails.md |
| agentic-ai-security-identity | trust | docs/trust/05-agentic-ai-security-identity.md |
| evolution-enterprise-ai-security | trust | docs/trust/ai-security-governance/06-evolution-enterprise-ai-security.md |
| runtime-ai-security | trust | docs/trust/ai-security-governance/09-runtime-ai-security.md |
| multi-agent-security | trust | docs/trust/ai-security-governance/15-multi-agent-security.md |
| identity-mcp-a2a-security-blueprint | trust | docs/trust/ai-security-governance/34-identity-mcp-a2a-security-blueprint.md |
| economic-security-finops-commerce-pqc | trust | docs/trust/ai-security-governance/36-economic-security-finops-commerce-pqc.md |
| aispm-ai-security-posture-management | trust | docs/trust/ai-security-governance/45-aispm-ai-security-posture-management.md |
| runtime-security-governance | trust | docs/trust/ai-security-governance/47-runtime-security-governance.md |
| enterprise-security-architecture | trust | docs/trust/cybersec-architect/02-enterprise-security-architecture.md |
| security-domains | trust | docs/trust/cybersec-architect/03-security-domains.md |
| ai-security | trust | docs/trust/cybersec-architect/04-ai-security.md |
| agentic-ai-security | trust | docs/trust/cybersec-architect/05-agentic-ai-security.md |
| cloud-security | trust | docs/trust/cybersec-architect/07-cloud-security.md |
| security-operations | trust | docs/trust/cybersec-architect/09-security-operations.md |
| security-patterns | trust | docs/trust/cybersec-architect/13-security-patterns.md |
| eu-bank-copilot-runtime-security | assets | docs/assets/03-eu-bank-copilot-runtime-security.md |

**Recommended hub:** `hub-trust` (`docs/trust/index.md`) — this is a hub-type page already,
and the trust domain is functionally "the security/governance domain" of the wiki (it already
absorbed the old `ai-security-governance/index.md` and `security/index.md` overview pages per
its `supersedes` list). It is the natural reader entry point for "security" as a theme.

**Spokes:** all 31 other rows above. Each keeps its own scope (strategy-level security model,
CI/CD secrets, agent-skill security, K8s security, EU bank case study, etc.) and should link
up to `hub-trust`.

**Duplicate-suspicion flags:**
- `agent-skills-security-architecture` and `agentic-ui-security-architecture` share the
  identical alias **"security architecture"** verbatim (no further scoping text in either
  alias) and sit in the same domain (agentic-systems), one chapter apart in numbering scheme.
  **POSSIBLE MISSED DUPLICATE, not just cross-section overlap** — worth a human diff to confirm
  agent-skills security architecture and agentic-UI security architecture are actually distinct
  content and not two passes over the same material.
- `governance-and-security` (agentic-systems/core/26, alias "governance & security") vs.
  `security-governance` (agentic-systems/coding-tools/02, alias "security architecture &
  enterprise ai governance") — same domain, near-identical generic titles. Scope looks
  differentiable (core-fundamentals chapter vs. coding-tools-series chapter) but titles are
  close enough to warrant a quick human check. Flagged as a **soft** possible-duplicate, lower
  confidence than the one above.

---

## 2. FinOps

Spans 6 domains: strategy, agentic-systems, platforms, trust, operations, assets.

| id | domain | canonical |
|---|---|---|
| ai-cost-implementation-guide-2026 | strategy | docs/strategy/04-ai-cost-implementation-guide-2026.md |
| part-12-observability-finops | agentic-systems | docs/agentic-systems/multimodal/12-part-12-observability-finops.md |
| part-08-observability-finops-integration | platforms | docs/platforms/48-part-08-observability-finops-integration.md |
| economic-security-finops-commerce-pqc | trust | docs/trust/ai-security-governance/36-economic-security-finops-commerce-pqc.md |
| finops-ai-soc | operations | docs/operations/02-finops-ai-soc.md |
| finops-cost-management-overview | operations | docs/operations/03-finops-cost-management-overview.md |
| finops-budget-governance | operations | docs/operations/04-finops-budget-governance.md |
| finops-capacity-forecasting | operations | docs/operations/05-finops-capacity-forecasting.md |
| finops-chargeback-attribution | operations | docs/operations/06-finops-chargeback-attribution.md |
| finops-infrastructure-optimization | operations | docs/operations/07-finops-infrastructure-optimization.md |
| finops-maturity-model | operations | docs/operations/08-finops-maturity-model.md |
| finops-multiagent-cost-propagation | operations | docs/operations/09-finops-multiagent-cost-propagation.md |
| finops-rag-mcp-a2a-economics | operations | docs/operations/10-finops-rag-mcp-a2a-economics.md |
| finops-unit-economics-kpis | operations | docs/operations/11-finops-unit-economics-kpis.md |
| case-12-meritage-dynamic-pricing-agent | assets | docs/assets/45-case-12-meritage-dynamic-pricing-agent.md |

**Recommended hub:** `finops-cost-management-overview` (`docs/operations/03-finops-cost-management-overview.md`)
— explicitly the "overview" chapter of the operations-domain FinOps series; the operations
domain has no dedicated finops hub-type page (only the generic `hub-operations`), so the
overview chapter is the most foundational stand-in.

**Spokes:** all others, including the strategy-level cost-implementation guide, the two
observability+finops integration chapters, the trust-domain economic-security chapter, and the
Meritage pricing-agent case study.

**Duplicate-suspicion flags:** none — each entry has a clearly distinct sub-scope (budget
governance vs. capacity forecasting vs. chargeback vs. multi-agent cost propagation, etc.).

---

## 3. Memory

Spans 4 domains: architecture, agentic-systems, platforms, trust.

| id | domain | canonical |
|---|---|---|
| agentic-ai-landing-zone-memory-architecture | architecture | docs/architecture/27-agentic-ai-landing-zone-memory-architecture.md |
| agent-memory-planning-architecture | architecture | docs/architecture/41-agent-memory-planning-architecture.md |
| ai-memory-agent-innovations-research-report | agentic-systems | docs/agentic-systems/core/07-ai-memory-agent-innovations-research-report.md |
| mcp-integration-and-memory | agentic-systems | docs/agentic-systems/core/24-mcp-integration-and-memory.md |
| memory-vs-workflow-state | agentic-systems | docs/agentic-systems/orchestration/13-memory-vs-workflow-state.md |
| agentcore-memory-architecture-guide | platforms | docs/platforms/15-agentcore-memory-architecture-guide.md |
| agentcore-memory-gaps-extensions-2026 | platforms | docs/platforms/16-agentcore-memory-gaps-extensions-2026.md |
| agentcore-memory-operations-deepdive | platforms | docs/platforms/17-agentcore-memory-operations-deepdive.md |
| memory-governance | trust | docs/trust/ai-security-governance/12-memory-governance.md |
| rag-memory-data-authorization | trust | docs/trust/ai-security-governance/29-rag-memory-data-authorization.md |
| ai-soc-observability-redteam-memory | trust | docs/trust/ai-security-governance/35-ai-soc-observability-redteam-memory.md |

**Recommended hub:** `agentic-ai-landing-zone-memory-architecture` (`docs/architecture/27-agentic-ai-landing-zone-memory-architecture.md`)
— framed as an enterprise "landing zone" pattern, the most foundational/architecture-level
overview of memory. (Note: the old `docs/agentic-systems/memory/index.md` hub page was already
folded into `hub-agentic-systems`'s `supersedes` list in stage-02, so there is no
memory-specific hub-type page left to designate.)

**Spokes:** all others, including the AWS AgentCore-specific trio (platforms domain), the
governance/authorization-flavored trust-domain entries, and `agent-memory-planning-architecture`
(close second choice for hub — link it directly under the designated hub as the next read).

**Duplicate-suspicion flags:** none — vendor-specific (AgentCore), governance-specific, and
architecture-pattern framings are genuinely distinct.

---

## 4. Evaluation

Spans 4 domains: architecture, agentic-systems, data-knowledge, operations.

| id | domain | canonical |
|---|---|---|
| agentic-ai-landing-zone-evaluation | architecture | docs/architecture/26-agentic-ai-landing-zone-evaluation.md |
| prompts-evaluation-spark-infrastructure | agentic-systems | docs/agentic-systems/coding-tools/54-prompts-evaluation-spark-infrastructure.md |
| evaluation-reusability-deduplication | agentic-systems | docs/agentic-systems/core/27-evaluation-reusability-deduplication.md |
| observability-and-evaluation | agentic-systems | docs/agentic-systems/core/35-observability-and-evaluation.md |
| part-10-evaluation-benchmarks | agentic-systems | docs/agentic-systems/multimodal/10-part-10-evaluation-benchmarks.md |
| part-11-evaluation-harnesses-cicd | agentic-systems | docs/agentic-systems/multimodal/11-part-11-evaluation-harnesses-cicd.md |
| evaluation | data-knowledge | docs/data-knowledge/08-evaluation.md |
| agent-evaluation-framework | operations | docs/operations/01-agent-evaluation-framework.md |
| agent-testing-monitoring-evaluation | operations | docs/operations/12-agent-testing-monitoring-evaluation.md |

**Recommended hub:** `evaluation` (`docs/data-knowledge/08-evaluation.md`) — the bare topic id
("evaluation & quality gates") is the most generic/foundational framing among the matches.

**Spokes:** all others, notably `agent-evaluation-framework` (operations domain — close second
choice, since it opens the operations FinOps/eval chapter set) and the multimodal-specific,
prompt-specific, and CI/CD-harness-specific chapters.

**Duplicate-suspicion flags:** none on their own, but note overlap with the Observability theme
below via `observability-and-evaluation` and `agent-testing-monitoring-evaluation`, which are
legitimately cross-listed under both themes (single pages, not duplicates).

---

## 5. Observability

Spans 7 domains: strategy, architecture, agentic-systems, platforms, trust, operations, assets.

| id | domain | canonical |
|---|---|---|
| part-14-observability | strategy | docs/strategy/24-part-14-observability.md |
| agentic-ai-reliability-observability-governance | architecture | docs/architecture/43-agentic-ai-reliability-observability-governance.md |
| observability | agentic-systems | docs/agentic-systems/agentic-ui/14-observability.md |
| cicd-observability-scaling | agentic-systems | docs/agentic-systems/coding-tools/03-cicd-observability-scaling.md |
| harness-security-supplychain-observability | agentic-systems | docs/agentic-systems/core/06-harness-security-supplychain-observability.md |
| multi-agent-and-observability | agentic-systems | docs/agentic-systems/core/25-multi-agent-and-observability.md |
| observability-and-evaluation | agentic-systems | docs/agentic-systems/core/35-observability-and-evaluation.md |
| part-12-observability-finops | agentic-systems | docs/agentic-systems/multimodal/12-part-12-observability-finops.md |
| observability-framework | agentic-systems | docs/agentic-systems/orchestration/16-observability-framework.md |
| k8s-handbook-part10-observability | platforms | docs/platforms/27-k8s-handbook-part10-observability.md |
| part-08-observability-finops-integration | platforms | docs/platforms/48-part-08-observability-finops-integration.md |
| ai-observability | trust | docs/trust/ai-security-governance/16-ai-observability.md |
| ai-soc-observability-redteam-memory | trust | docs/trust/ai-security-governance/35-ai-soc-observability-redteam-memory.md |
| part-08-observability | trust | docs/trust/ai-soc-playbooks/08-part-08-observability.md |
| agent-testing-monitoring-evaluation | operations | docs/operations/12-agent-testing-monitoring-evaluation.md |
| eu-bank-copilot-compliance-observability | assets | docs/assets/04-eu-bank-copilot-compliance-observability.md |

**Recommended hub:** `observability` (`docs/agentic-systems/agentic-ui/14-observability.md`) —
bare id, generic "observability for agentic applications" framing, the most overview-level page
among the matches. Close second: `observability-framework` (orchestration-specific).

**Spokes:** all others — K8s-specific, SOC-specific, EU-bank-case-specific, and
FinOps-integration-specific observability chapters all stay separate and link up.

**Duplicate-suspicion flags:** none beyond the cross-theme overlaps already noted under FinOps
and Evaluation (same pages, not duplicates).

---

## 6. MCP (Model Context Protocol)

Spans 5 domains: architecture, agentic-systems, protocols, trust, operations.

| id | domain | canonical |
|---|---|---|
| mcp-a2a-protocol-deep-dive | architecture | docs/architecture/58-mcp-a2a-protocol-deep-dive.md |
| copilotkit-mcp-apps-vs-tools | agentic-systems | docs/agentic-systems/coding-tools/08-copilotkit-mcp-apps-vs-tools.md |
| cheatsheet-11-mcp-pipeline-errors | agentic-systems | docs/agentic-systems/coding-tools/14-cheatsheet-11-mcp-pipeline-errors.md |
| cheatsheet-3-mcp | agentic-systems | docs/agentic-systems/coding-tools/17-cheatsheet-3-mcp.md |
| module-4-mcp | agentic-systems | docs/agentic-systems/coding-tools/26-module-4-mcp.md |
| mcp-deep-guide | agentic-systems | docs/agentic-systems/coding-tools/39-mcp-deep-guide.md |
| skills-tools-mcp-relationship | agentic-systems | docs/agentic-systems/core/20-skills-tools-mcp-relationship.md |
| mcp-integration-and-memory | agentic-systems | docs/agentic-systems/core/24-mcp-integration-and-memory.md |
| skills-tools-mcp-a2a-relationship | agentic-systems | docs/agentic-systems/core/31-skills-tools-mcp-a2a-relationship.md |
| mcp-impact | agentic-systems | docs/agentic-systems/orchestration/10-mcp-impact.md |
| mcp-deep-research-2026 | protocols | docs/protocols/13-mcp-deep-research-2026.md |
| mcp-enterprise-security-governance-operations-2026 | protocols | docs/protocols/14-mcp-enterprise-security-governance-operations-2026.md |
| mcp-harness-aidlc | protocols | docs/protocols/15-mcp-harness-aidlc.md |
| agent-tool-mcp-authorization | trust | docs/trust/ai-security-governance/27-agent-tool-mcp-authorization.md |
| identity-mcp-a2a-security-blueprint | trust | docs/trust/ai-security-governance/34-identity-mcp-a2a-security-blueprint.md |
| finops-rag-mcp-a2a-economics | operations | docs/operations/10-finops-rag-mcp-a2a-economics.md |

**Recommended hub:** `hub-protocols` (`docs/protocols/index.md`) — hub-type page; MCP is
fundamentally a protocol and the protocols domain is small and protocol-focused, making its
domain hub the natural entry point. `mcp-deep-guide` (agentic-systems) is the best
"comprehensive deep-dive" spoke to link prominently from the hub.

**Spokes:** all others — cheatsheets, module/training content, CopilotKit-specific,
authorization-specific, and economics-specific MCP pages.

**Duplicate-suspicion flags:** `cheatsheet-3-mcp` and `cheatsheet-11-mcp-pipeline-errors` are
both short-form MCP cheatsheets in the same coding-tools series; scope (general MCP cheatsheet
vs. pipeline-errors-specific) looks distinct enough from the ids alone, but low-confidence —
worth a quick skim if not already checked in stage-02. Not escalating to a full flag.

---

## 7. Anti-patterns

Spans 2 domains: agentic-systems, trust (weaker cross-domain spread, but named explicitly in
the stage-03 requirement, so included regardless).

| id | domain | canonical |
|---|---|---|
| anti-patterns | agentic-systems | docs/agentic-systems/agentic-ui/03-anti-patterns.md |
| harness-bestpractices-antipatterns-roadmap | agentic-systems | docs/agentic-systems/core/03-harness-bestpractices-antipatterns-roadmap.md |
| architecture-patterns-antipatterns-and-case-studies | agentic-systems | docs/agentic-systems/core/38-architecture-patterns-antipatterns-and-case-studies.md |
| anti-patterns-catalog | agentic-systems | docs/agentic-systems/orchestration/22-anti-patterns-catalog.md |
| best-practices-anti-patterns | trust | docs/trust/ai-security-governance/21-best-practices-anti-patterns.md |

**Recommended hub:** `anti-patterns` (`docs/agentic-systems/agentic-ui/03-anti-patterns.md`) —
bare id, earliest-numbered chapter, most general catalog framing.

**Spokes:** all others — orchestration-specific catalog, harness-roadmap-specific, EA
case-study-specific, and trust/security-specific anti-pattern chapters.

**Duplicate-suspicion flags:** `anti-patterns` and `anti-patterns-catalog` are close in name
(general catalog vs. "orchestration and agentic systems" catalog per its alias) — the alias
text does scope the second one to orchestration specifically, so this reads as legitimate
scope difference, not a duplicate. Not flagging.

---

## 8. Glossary

Spans 2 domains: strategy, architecture (weaker spread; named explicitly in the requirement).

| id | domain | canonical |
|---|---|---|
| vol10-relationship-maps-glossary | strategy | docs/strategy/44-vol10-relationship-maps-glossary.md |
| vol5-ai-strategy-transformation-glossary | strategy | docs/strategy/48-vol5-ai-strategy-transformation-glossary.md |
| ea-glossary-cheatsheet | architecture | docs/architecture/69-ea-glossary-cheatsheet.md |

**Recommended hub:** `ea-glossary-cheatsheet` (`docs/architecture/69-ea-glossary-cheatsheet.md`)
— general-purpose "enterprise architecture glossary & cheat sheet," not scoped to one
book/volume, unlike the other two which are volume-specific glossaries (relationship-maps vol10,
strategy-transformation vol5).

**Spokes:** the two volume-specific glossaries — these remain the terminology reference for
their specific book series and should link up to the general glossary as the reader's landing
point.

**Duplicate-suspicion flags:** none — each glossary is scoped to a specific source volume, so
term lists differ by design (this is the pattern the stage-03 brief itself describes as
same-theme-different-scope, not literal duplication).

---

## 9. Interview

Single domain (career) — 21 matches, all in career. Included per the explicit requirement.

| id | domain | canonical |
|---|---|---|
| ea-interview-handbook | career | docs/career/05-ea-interview-handbook.md |
| interview-ai-agent-systems | career | docs/career/06-interview-ai-agent-systems.md |
| interview-ai-engineer-question-bank | career | docs/career/07-interview-ai-engineer-question-bank.md |
| interview-agentic-ai-platforms-questionnaire | career | docs/career/08-interview-agentic-ai-platforms-questionnaire.md |
| interview-ea-hitl-hotl-hool | career | docs/career/09-interview-ea-hitl-hotl-hool.md |
| interview-ea-quality-resilience-testing | career | docs/career/10-interview-ea-quality-resilience-testing.md |
| interview-ea-senior | career | docs/career/11-interview-ea-senior.md |
| interview-ea-soft-skills-and-behaviors | career | docs/career/12-interview-ea-soft-skills-and-behaviors.md |
| interview-ey-ai-architect | career | docs/career/13-interview-ey-ai-architect.md |
| interview-enterprise-architect-age-of-ai | career | docs/career/14-interview-enterprise-architect-age-of-ai.md |
| interview-enterprise-genai-architect | career | docs/career/15-interview-enterprise-genai-architect.md |
| interview-hard-scenarios | career | docs/career/16-interview-hard-scenarios.md |
| interview-ml-ai-mastery-guide | career | docs/career/17-interview-ml-ai-mastery-guide.md |
| interview-multimodal-ai-ea-scenarios | career | docs/career/18-interview-multimodal-ai-ea-scenarios.md |
| interview-ea-master-guide | career | docs/career/19-interview-ea-master-guide.md |
| interview-ea-vol3-cto-ai | career | docs/career/20-interview-ea-vol3-cto-ai.md |
| interview-ea-artifacts-and-metrics | career | docs/career/21-interview-ea-artifacts-and-metrics.md |
| interview-fde-architect-context | career | docs/career/22-interview-fde-architect-context.md |
| interview-fde-role-skills-map | career | docs/career/23-interview-fde-role-skills-map.md |
| interview-harness-question-bank | career | docs/career/30-interview-harness-question-bank.md |
| ea-soft-skills-interview-master-guide | career | docs/career/44-ea-soft-skills-interview-master-guide.md |

**Recommended hub:** `ea-interview-handbook` (`docs/career/05-ea-interview-handbook.md`) —
earliest-numbered, general "handbook" framing among 21 role/scenario/question-bank-specific
pages. (`hub-career`, the domain hub, is the alternative if a broader "career hub" framing is
preferred, but since every match here is already career-domain, the interview-specific handbook
is the more precise entry point per the task's guidance.)

**Spokes:** all other 20 — role-specific (EY, FDE, senior EA), scenario-specific (hard
scenarios, multimodal), and skill-specific (soft skills, quality/resilience testing) question
banks.

**Duplicate-suspicion flags:** `interview-ea-soft-skills-and-behaviors` (career/12) and
`ea-soft-skills-interview-master-guide` (career/44) both cover EA soft-skills interview prep.
**POSSIBLE MISSED DUPLICATE, not just cross-section overlap** — names and likely content
overlap closely enough (both "soft skills" + "interview" for the EA role) that this looks like
two source docs that should have been merged in stage-02 rather than two genuinely distinct
scopes. Recommend a human diff.

---

## 10. Identity & Authentication

*(Additional theme — discovered via `identity`/`auth` id matches spanning 4 domains:
agentic-systems, protocols, trust, plus assets-adjacent via aliases.)*

| id | domain | canonical |
|---|---|---|
| identity-auth-architecture | agentic-systems | docs/agentic-systems/agentic-ui/12-identity-auth-architecture.md |
| auth-standards-reference | protocols | docs/protocols/01-auth-standards-reference.md |
| enterprise-ai-platform-auth-survey | protocols | docs/protocols/02-enterprise-ai-platform-auth-survey.md |
| marketplace-connector-auth-patterns | protocols | docs/protocols/03-marketplace-connector-auth-patterns.md |
| agentidentity-research-2026 | protocols | docs/protocols/04-agentidentity-research-2026.md |
| identity-obo-sessions | protocols | docs/protocols/05-identity-obo-sessions.md |
| agent-identity-entra-vs-awsagentcore | protocols | docs/protocols/06-agent-identity-entra-vs-awsagentcore.md |
| auth-identity-flows | protocols | docs/protocols/07-auth-identity-flows.md |
| entra-3lo-agent-auth-implementation | protocols | docs/protocols/08-entra-3lo-agent-auth-implementation.md |
| entra-3lo-agent-auth-multiagent-compliance | protocols | docs/protocols/09-entra-3lo-agent-auth-multiagent-compliance.md |
| entra-3lo-agent-auth-security-review | protocols | docs/protocols/10-entra-3lo-agent-auth-security-review.md |
| entra-3lo-agent-auth-standards-architecture | protocols | docs/protocols/11-entra-3lo-agent-auth-standards-architecture.md |
| tool-authentication-connectors | protocols | docs/protocols/12-tool-authentication-connectors.md |
| agent-communication-identity-gateway | trust | docs/trust/03-agent-communication-identity-gateway.md |
| agentic-ai-security-identity | trust | docs/trust/05-agentic-ai-security-identity.md |
| policy-authorization-series-overview | trust | docs/trust/ai-security-governance/02-policy-authorization-series-overview.md |
| identity-for-ai-agents | trust | docs/trust/ai-security-governance/10-identity-for-ai-agents.md |
| ai-authorization | trust | docs/trust/ai-security-governance/11-ai-authorization.md |
| 1b-authorization-deep-dive | trust | docs/trust/ai-security-governance/24-1b-authorization-deep-dive.md |
| identity-claims-policy | trust | docs/trust/ai-security-governance/25-identity-claims-policy.md |
| agent-tool-mcp-authorization | trust | docs/trust/ai-security-governance/27-agent-tool-mcp-authorization.md |
| 3b-agent-authorization-deep-dive | trust | docs/trust/ai-security-governance/28-3b-agent-authorization-deep-dive.md |
| rag-memory-data-authorization | trust | docs/trust/ai-security-governance/29-rag-memory-data-authorization.md |
| identity-mcp-a2a-security-blueprint | trust | docs/trust/ai-security-governance/34-identity-mcp-a2a-security-blueprint.md |
| identity-architecture | trust | docs/trust/cybersec-architect/06-identity-architecture.md |

**Recommended hub:** `identity-architecture` (`docs/trust/cybersec-architect/06-identity-architecture.md`)
— the most general-purpose "identity architecture" chapter (no protocol/vendor/authz-flow
qualifier in scope), positioned in the trust domain's cybersecurity-architect series.
(`hub-trust` is already the designated hub for the Security theme above; using the more
specific `identity-architecture` page here avoids overloading one hub for two related but
distinct themes.)

**Spokes:** all other 23 — the large Entra 3LO sub-series (protocols domain, 6 chapters),
the authorization-deep-dive sub-series (trust domain), vendor-comparison pages, and the
identity-auth-architecture UI-specific page.

**Duplicate-suspicion flags:** `identity-architecture` (trust/cybersec-architect/06, "Part 6 —
identity architecture") vs. `identity-auth-architecture` (agentic-systems/agentic-ui/12,
"identity & auth architecture") — near-identical titles across domains. Scope looks
differentiable (enterprise cybersecurity-architect book chapter vs. agentic-UI-specific
application chapter), so this is a **lower-confidence, soft flag** rather than a hard one — a
human should confirm the UI chapter isn't just restating the cybersec-architect chapter's
identity-architecture content in an agentic-UI wrapper.

---

## 11. RAG (Retrieval-Augmented Generation)

Spans 4 domains: agentic-systems, data-knowledge, trust, operations.

| id | domain | canonical |
|---|---|---|
| rag-agents-models-platform | agentic-systems | docs/agentic-systems/coding-tools/51-rag-agents-models-platform.md |
| part-05-multimodal-rag | agentic-systems | docs/agentic-systems/multimodal/05-part-05-multimodal-rag.md |
| complex-rag-deep-dive | data-knowledge | docs/data-knowledge/13-complex-rag-deep-dive.md |
| rag-memory-data-authorization | trust | docs/trust/ai-security-governance/29-rag-memory-data-authorization.md |
| finops-rag-mcp-a2a-economics | operations | docs/operations/10-finops-rag-mcp-a2a-economics.md |

**Recommended hub:** `complex-rag-deep-dive` (`docs/data-knowledge/13-complex-rag-deep-dive.md`)
— data-knowledge is RAG's natural home domain, and this is the most substantial/general RAG
technical guide among the matches (no hub-type page exists specifically for RAG; the domain
hub `hub-data-knowledge` covers the whole data-knowledge domain, not RAG specifically).

**Spokes:** the agent/platform-comparison RAG page, the multimodal-RAG chapter, the
authorization-specific trust chapter, and the FinOps-economics chapter (already a spoke of
FinOps and MCP themes too — single crosscutting page).

**Duplicate-suspicion flags:** none — each entry has a distinct angle (deep technical guide,
platform/agent comparison, multimodal-specific, authorization-specific, economics-specific).

---

## 12. Orchestration

Spans 3 domains: architecture, agentic-systems, assets.

| id | domain | canonical |
|---|---|---|
| agent-interoperability-orchestration | architecture | docs/architecture/40-agent-interoperability-orchestration.md |
| ai-harness-architecture-orchestration | architecture | docs/architecture/44-ai-harness-architecture-orchestration.md |
| ai-coding-orchestrators | agentic-systems | docs/agentic-systems/orchestration/07-ai-coding-orchestrators.md |
| tool-calling-orchestration | agentic-systems | docs/agentic-systems/orchestration/09-tool-calling-orchestration.md |
| a2a-orchestration-patterns | agentic-systems | docs/agentic-systems/orchestration/11-a2a-orchestration-patterns.md |
| workflow-orchestration-security-architecture | agentic-systems | docs/agentic-systems/orchestration/17-workflow-orchestration-security-architecture.md |
| case-03-ironclad-maintenance-orchestration-agent | assets | docs/assets/36-case-03-ironclad-maintenance-orchestration-agent.md |

**Recommended hub:** `ai-harness-architecture-orchestration` (`docs/architecture/44-ai-harness-architecture-orchestration.md`)
— "AI harness architecture & multi-agent orchestration" is the most foundational/architecture-
level overview, versus the more narrowly scoped orchestration-subfolder chapters (tool-calling,
A2A-specific, security-specific) and the Ironclad case study.

**Spokes:** all others, including `agent-interoperability-orchestration` (close second choice —
also architecture-domain and foundational) and the four `agentic-systems/orchestration/`
sub-chapters, plus the case study.

**Duplicate-suspicion flags:** none — `agent-interoperability-orchestration` and
`ai-harness-architecture-orchestration` are adjacent in numbering (40, 44) and both
architecture-level, but aliases indicate distinct focus (interoperability/standards vs.
harness/multi-agent orchestration specifically). Not flagging, but noting the closeness for
awareness.

---

## 13. Compliance

Spans 5 domains: architecture, agentic-systems, protocols, trust, assets.

| id | domain | canonical |
|---|---|---|
| enterprise-ai-governance-compliance | architecture | docs/architecture/51-enterprise-ai-governance-compliance.md |
| part-09-compliance-responsible-ai | agentic-systems | docs/agentic-systems/multimodal/09-part-09-compliance-responsible-ai.md |
| entra-3lo-agent-auth-multiagent-compliance | protocols | docs/protocols/09-entra-3lo-agent-auth-multiagent-compliance.md |
| 5b-compliance-governance-decision-framework | trust | docs/trust/ai-security-governance/32-5b-compliance-governance-decision-framework.md |
| part-10-standards-compliance | trust | docs/trust/ai-soc-playbooks/10-part-10-standards-compliance.md |
| eu-bank-copilot-compliance-observability | assets | docs/assets/04-eu-bank-copilot-compliance-observability.md |

**Recommended hub:** `enterprise-ai-governance-compliance` (`docs/architecture/51-enterprise-ai-governance-compliance.md`)
— the most general/enterprise-wide framing among the matches; the others are each scoped to a
specific sub-context (multimodal, multiagent-auth, decision-framework-within-a-47-chapter book,
SOC-standards-mapping, one bank case study).

**Spokes:** all others.

**Duplicate-suspicion flags:** none — sub-scopes are clearly distinct.

---

## 14. Responsible AI / Safety & Guardrails

*(Additional theme — combines guardrails, red-teaming, safety, and "responsible AI" id/alias
matches, which individually spanned only 2–3 domains but together recur across 4: strategy,
agentic-systems, data-knowledge, trust.)*

| id | domain | canonical |
|---|---|---|
| part-12-responsible-ai | strategy | docs/strategy/22-part-12-responsible-ai.md |
| governance-responsible-ai-and-security | strategy | docs/strategy/39-governance-responsible-ai-and-security.md |
| responsible-ai | agentic-systems | docs/agentic-systems/agentic-ui/17-responsible-ai.md |
| module-7-safety-enterprise-exam | agentic-systems | docs/agentic-systems/coding-tools/29-module-7-safety-enterprise-exam.md |
| constitutional-ai-safety-2026 | agentic-systems | docs/agentic-systems/coding-tools/38-constitutional-ai-safety-2026.md |
| part-08-guardrails-sanitization | agentic-systems | docs/agentic-systems/multimodal/08-part-08-guardrails-sanitization.md |
| part-09-compliance-responsible-ai | agentic-systems | docs/agentic-systems/multimodal/09-part-09-compliance-responsible-ai.md |
| governance-rai | data-knowledge | docs/data-knowledge/09-governance-rai.md |
| agentic-ai-security-guardrails | trust | docs/trust/04-agentic-ai-security-guardrails.md |
| ai-soc-observability-redteam-memory | trust | docs/trust/ai-security-governance/35-ai-soc-observability-redteam-memory.md |
| ai-red-teaming-guide | trust | docs/trust/ai-security-governance/42-ai-red-teaming-guide.md |
| part-07-ai-safety | trust | docs/trust/ai-soc-playbooks/07-part-07-ai-safety.md |
| part-01-nist-ai-100-2-adversarial-ml | trust | docs/trust/nist-ai-standards/01-part-01-nist-ai-100-2-adversarial-ml.md |
| ai-safety-framework | trust | docs/trust/sovereign-constitutional-ai/05-ai-safety-framework.md |
| rai-operating-model | trust | docs/trust/sovereign-constitutional-ai/10-rai-operating-model.md |

**Recommended hub:** `part-12-responsible-ai` (`docs/strategy/22-part-12-responsible-ai.md`) —
strategy is the highest-altitude domain in this wiki, and this chapter is the most
executive/overview-level treatment of the theme, versus the many deep, sub-scoped trust-domain
chapters (NIST adversarial-ML standard, red-teaming guide, constitutional-AI safety framework,
RAI operating model).

**Spokes:** all others.

**Duplicate-suspicion flags:** `part-12-responsible-ai` (strategy), `responsible-ai`
(agentic-systems/agentic-ui), `part-09-compliance-responsible-ai` (agentic-systems/multimodal),
`governance-rai` (data-knowledge), and `rai-operating-model` (trust) are five differently-scoped
"responsible AI" pages — strategy-level, agentic-application-level, multimodal-specific,
data-governance-specific, and operating-model-specific respectively. Aliases support distinct
scope for each, so **not flagging as duplicates**, just noting this theme has the widest
legitimate fan-out of any theme in this document.

---

## 15. A2A (Agent-to-Agent Protocol)

*(Additional theme — the A2A protocol recurs distinctly from the general MCP theme above,
spanning 5 domains: architecture, agentic-systems, protocols, trust, operations.)*

| id | domain | canonical |
|---|---|---|
| mcp-a2a-protocol-deep-dive | architecture | docs/architecture/58-mcp-a2a-protocol-deep-dive.md |
| a2a-deep-research | agentic-systems | docs/agentic-systems/core/17-a2a-deep-research.md |
| skills-tools-mcp-a2a-relationship | agentic-systems | docs/agentic-systems/core/31-skills-tools-mcp-a2a-relationship.md |
| a2a-orchestration-patterns | agentic-systems | docs/agentic-systems/orchestration/11-a2a-orchestration-patterns.md |
| emerging-protocols-overview | protocols | docs/protocols/21-emerging-protocols-overview.md |
| a2a-security-governance | trust | docs/trust/02-a2a-security-governance.md |
| identity-mcp-a2a-security-blueprint | trust | docs/trust/ai-security-governance/34-identity-mcp-a2a-security-blueprint.md |
| finops-rag-mcp-a2a-economics | operations | docs/operations/10-finops-rag-mcp-a2a-economics.md |

**Recommended hub:** `mcp-a2a-protocol-deep-dive` (`docs/architecture/58-mcp-a2a-protocol-deep-dive.md`)
— architecture-domain comparative deep-dive covering both MCP and A2A, the most overview-level
treatment of A2A specifically (vs. `a2a-deep-research`, which is framed as critical
research/analysis rather than an entry-point overview).

**Spokes:** all others, including `a2a-deep-research` (agentic-systems — close second choice,
good "go deeper" link from the hub), the orchestration-patterns and security-governance
A2A-specific chapters, and the crosscutting FinOps/identity/MCP pages.

**Duplicate-suspicion flags:** none — `mcp-a2a-protocol-deep-dive` (comparative overview) and
`a2a-deep-research` (critical analysis/research) read as complementary rather than duplicative,
per their aliases.

---

## Summary of duplicate-suspicion flags raised

1. **agent-skills-security-architecture** vs. **agentic-ui-security-architecture** (Security
   theme) — identical alias text "security architecture", same domain. Highest-confidence flag.
2. **interview-ea-soft-skills-and-behaviors** vs. **ea-soft-skills-interview-master-guide**
   (Interview theme) — both EA soft-skills interview prep. High-confidence flag.
3. **governance-and-security** vs. **security-governance** (Security theme) — same domain,
   near-identical generic titles. Soft/lower-confidence flag.
4. **identity-architecture** vs. **identity-auth-architecture** (Identity & Authentication
   theme) — near-identical titles across domains. Soft/lower-confidence flag.

All four are navigation-adjacent findings surfaced while building this hub/spoke map, not new
merge-plan work — they are called out here for human follow-up (a content diff), separate from
the normal hub/spoke designations, per the stage-03 instruction to flag genuine duplicate
suspicion separately from ordinary same-theme/different-scope overlap.
