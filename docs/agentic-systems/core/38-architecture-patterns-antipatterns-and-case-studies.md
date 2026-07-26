---
title: "Architecture Patterns, Anti-Patterns & Case Studies"
domain: agentic-systems
doc_type: guide
topic_id: architecture-patterns-antipatterns-and-case-studies
status: current
supersedes:
  - "docs/agentic-systems/skill/enterprise/11-architecture-patterns-antipatterns-and-case-studies.md"
date_created: 2026-07-24
last_reviewed: 2026-07-24
---

# Part 14 — Architecture Patterns · Part 15 — Anti-Patterns · Part 16 — Vendor Case Studies (+ Deliverable 10)

## PART A: Production Architecture Patterns

### 11.1 Central vs. Domain vs. Federated Skill Registry

| Pattern | Description | Best for |
| --- | --- | --- |
| **Central Registry** | One registry, one team, one schema, org-wide | Small-to-mid enterprises, or early-stage programs establishing discipline before scaling |
| **Domain Registry** | Each business domain (finance, HR, supply chain) runs its own registry with domain-appropriate ownership | Large enterprises where domains have genuinely independent compliance regimes (e.g., financial-close skills vs. HR skills have almost no overlap and different regulators) |
| **Federated Registry** | Domain registries remain independently operated but publish a common metadata schema (file `02`) into a shared discovery/search layer | The realistic end-state for most large enterprises running multiple vendor platforms (Azure Foundry *and* SAP Joule *and* Salesforce Agentforce simultaneously) — avoids forcing one vendor's native format on every team while still preventing cross-platform duplication (file `06`) |

### 11.2 Marketplace / Capability Catalog

A business-facing layer on top of the technical registries (file `06`, §6.2) — lets non-engineering stakeholders answer "what can our agents already do" without needing to read SKILL.md files. AWS's newly launched Agent Registry and Azure's Entra Agent Registry both explicitly serve this dual technical/business-discovery role.

### 11.3 Skill Gateway / Policy Enforcement Point

The deterministic chokepoint described in file `09` — every tool invocation passes through it regardless of which skill or agent initiated the call. Implemented as AWS AgentCore Gateway + Cedar policy, Azure API Management as AI Gateway, or a custom OPA-fronted proxy. Non-negotiable in any architecture above pilot scale.

### 11.4 Evaluation Pipeline (recap, detail in file `08`)

CI-integrated: every skill/tool version change triggers golden-dataset regression before it can be promoted, with canary/A-B rollout as the final gate before full production traffic.

### 11.5 Observability Pipeline (recap, detail in file `08`)

OTel Collector as the neutral aggregation point, fanning out to whichever backend(s) the enterprise standardizes on, so no single vendor's tracing format becomes a lock-in dependency — the same architectural argument that made OTel the default choice for traditional microservices observability applies here.

### 11.6 Version Management, Approval, and Deployment Pipelines (recap, detail in file `10`)

The full chain: draft → automated gate → security/compliance review → regression suite → canary → production, with instant-rollback via default-version pointer.

---

## PART B: Common Anti-Patterns

| Anti-pattern | Why it fails | Correct pattern |
| --- | --- | --- |
| **Creating a Skill for every API** | Reintroduces the 1:1 tool-per-integration sprawl Skills were meant to abstract away; skills become thin, low-value wrappers | Only create a Skill where genuine judgment/sequencing exists; a bare API call is a Tool (file `01`, `04`) |
| **Embedding business logic in prompts** | Invisible to auditors, easy to silently violate, drifts from the real policy source of truth | Extract compliance-critical logic to a deterministic workflow/tool; skill references it (file `07`) |
| **Massive skill instructions** | Degrades instruction-following; buries important rules | Progressive disclosure — split into `references/*.md` (file `02`) |
| **Duplicate Skills / duplicate MCP wrappers** | Wastes effort, creates inconsistent behavior across "the same" capability, confuses discovery | Similarity-gated registry admission (file `06`) |
| **One tool doing multiple unrelated tasks** | Model can't reliably predict its behavior; hard to scope permissions narrowly | Single-purpose tools (file `05`) |
| **Poor tool descriptions** | Directly causes wrong-tool-selection incidents (Salesforce's own guidance is explicit on this causal link) | Full template in file `05` |
| **Missing ownership** | No one to fix it when it breaks or drifts; blocks certification | Mandatory `owner` field, enforced at registry admission (file `02`, `10`) |
| **No registry** | Duplication, no discovery, no governance surface at all | Minimum viable: even a spreadsheet-backed catalog with the metadata schema (file `02`) beats no registry |
| **No evaluation** | Regressions ship silently; no way to know if a prompt tweak helped or hurt | Golden dataset + online sampling, mandatory pre-certification (file `08`, `10`) |
| **No observability** | Incidents are undebuggable; no data to drive the improvement loop | OTel GenAI conventions end-to-end (file `08`) |
| **No versioning** | Can't roll back; can't reason about what changed between two production incidents | Semver + default-version pointer (file `10`) |
| **No lifecycle** | Deprecated capabilities silently linger and get reused by mistake | Explicit lifecycle states, discovery-visible deprecation (file `10`) |
| **Prompt duplication** | Same boilerplate copy-pasted across many skills; a policy change requires N edits instead of 1 | Shared/reusable sub-skills (file `07`) |
| **Conflicting Skills** | Two skills give contradictory guidance for overlapping scope; model behavior becomes unpredictable | Registry-level scope-overlap + contradiction linting; single owner per policy domain |
| **Hidden side effects** | A skill that appears read-only actually triggers a write (e.g., a "check status" skill that also sends a notification) | Postconditions must be explicit in the tool definition (file `05`) and reflected in the permission manifest |
| **Unbounded autonomy** | Agent takes high-impact, irreversible action without a checkpoint | `human_approval` triggers, least-agency principle, PEP enforcement (file `09`) |
| **No policy enforcement (or enforcement only in the prompt)** | Bypassable by prompt injection; not a real security boundary | Deterministic PEP outside the model (file `09`) |
| **No deprecation strategy** | Old capabilities never get retired; registry rots; agents keep finding and using stale/insecure versions | Lifecycle with communicated deadlines (file `10`) |

---

## PART C: Vendor / Platform Case Studies

*Reflects publicly documented capability as of mid-2026; verify current state before procurement, given the pace of releases in this space.*

### AWS Bedrock AgentCore

- **Skill packaging**: AWS-curated skills catalog (toggle-enabled), plus prebuilt coding-assistant skills (Kiro, Claude Code, Codex, Cursor) for platform-specific guidance.
- **Tool/MCP integration**: AgentCore Gateway converts APIs/Lambda functions into MCP-exposed tools automatically; native Web Search tool exposed as an MCP gateway target.
- **Observability**: OTel-based AgentCore Observability; trace-tree bundling of repeated spans; unified across runtime, Lambda, EKS, and non-AWS environments.
- **Governance/Registry**: AWS Agent Registry (Preview) — private, governed catalog for agents, tools, skills, MCP servers.
- **Security**: Natural-language policy → Cedar compilation; Bedrock Guardrails integrated at the policy layer for prompt-injection and sensitive-data-exposure checks on gateway targets.
- **Evaluation**: 13 built-in evaluators, batch evaluation against defined datasets, A/B testing on live traffic, recommendation engine grounded in production trace analysis.
- **Notable differentiator**: harness is explicitly decoupled from the model (switch models mid-session), and exportable from managed config to full Strands-based code when custom orchestration is needed.

### Microsoft Foundry (Azure AI Foundry Agent Service)

- **Skill packaging**: Skills explicitly implement the open Agent Skills specification — `SKILL.md` with YAML front matter, versioned via a dedicated Skills API (`/skills/{name}/versions`), independent of the Toolbox (tool) catalog.
- **Tool/MCP integration**: Toolboxes provide a single managed MCP-compatible endpoint per curated tool set; Tool Search selects a relevant subset per task rather than exposing everything; 1,400+ MCP-enabled tool connections cited.
- **Observability**: End-to-end OTel tracing with built-in evaluators (coherence, relevance, groundedness, safety) in the Foundry Control Plane.
- **Governance/Registry**: Skills are versioned, project-scoped, and MCP-resource-discoverable; Entra Agent Registry for org-wide agent discovery.
- **Security**: Entra Agent ID for agent identity; BYO-VNet with no public egress; integrated guardrails including cross-prompt injection (XPIA) mitigation.
- **Notable differentiator**: the clearest direct adoption of Anthropic's open Skills spec among the hyperscalers, making cross-platform skill portability most concrete here.

### Google ADK / Vertex AI Agent Platform

- **Skill packaging**: Agent Skill objects following the Agent Skills specification; skills can bundle scripts/assets/references, loaded incrementally.
- **Tool/MCP integration**: Rich tool ecosystem including MCP tools and cross-framework adapters (LangChain, CrewAI).
- **Registry**: Google Cloud Skill Registry — explicit collision-prevention against locally loaded skill names, semantic/keyword `search_skills` query, session-level caching of dynamically loaded skills.
- **Observability**: Built-in evaluation, Cloud Trace integration when deployed to Agent Runtime.
- **Notable differentiator**: A2A was originated by Google and remains most natively integrated here; ADK is explicitly framework-agnostic on the model side.

### Salesforce Agentforce

- **Skill equivalent**: Topics (scope/persona/instructions) + Actions (Apex, Flow, Prompt Template, or external API) — functionally a Skill/Tool split under different vocabulary; the Atlas Reasoning Engine performs skill-selection-equivalent (topic/action selection) and a grounding check before final response.
- **Determinism control**: Agentforce Script blends natural-language instruction with rule-based, deterministic control flow in one governed artifact — a direct, productized answer to the "hidden business logic in prompts" anti-pattern.
- **Interoperability**: Exposes agents as A2A endpoints; consumes MCP tools; every custom agent is discoverable/delegatable to partner agents via Flow.
- **Security**: Einstein Trust Layer masks PII before any prompt leaves the platform; explicit architectural guidance against cloning the running human user's profile onto the agent's service identity.
- **Observability**: Command Center for agent observability; Conversation Preview panel showing exact topic/action selection and inputs/outputs for debugging.
- **Notable differentiator**: tightest native binding between agent capability and the underlying CRM's own permission model (field-level security, sharing rules) — the governance model is inherited from the platform rather than bolted on.

### SAP Joule / SAP Business AI Platform

- **Skill packaging**: ~2,400 "Joule Skills" across 40+ specialized agents (Q1 2026 figures), built via low-code Joule Studio or pro-code SAP Cloud SDK for AI with LangGraph/AutoGen/CrewAI/Google ADK framework adapters.
- **Grounding**: SAP Knowledge Graph provides the semantic layer connecting business entities, workflows, and operational systems that skills reason over.
- **Interoperability**: A2A for cross-vendor multi-agent collaboration (agents expose A2A-compliant server endpoints); MCP for internally exposing SAP business capabilities with semantically enriched access.
- **Governance**: SAP Agent Hub maintains governance and audit trail for every invocation, including externally-built agents orchestrating SAP Joule agents as sub-agents.
- **Notable differentiator**: strongest "audit-ready by construction" positioning for transactional financial/HR/procurement domains — every agent action is logged with what it did, why, and what data it used, marketed explicitly as "traceability by design."

### ServiceNow AI Platform

- **Skill equivalent**: Generative AI "skills" as one category of tool an AI Agent uses (alongside scripts and flows) within an Agentic Workflow; AI Agent Studio for building/customizing agents.
- **Orchestration/governance**: AI Agent Orchestrator coordinates multi-agent teams toward a shared outcome with modular responsibilities and centralized governance; AI Control Tower provides cross-agent, cross-model, cross-source governance and monitoring — explicitly positioned as an "AI control tower" layer above individual agent frameworks, competing on governance rather than raw agent-building.
- **Notable differentiator**: the most governance-first framing among the platforms studied — ServiceNow explicitly critiques standalone agent frameworks as "capability without control" and positions itself as the control/audit layer that sits above them.

### Comparison summary table

| Dimension | AWS AgentCore | Azure Foundry | Google ADK | Salesforce Agentforce | SAP Joule | ServiceNow |
| --- | --- | --- | --- | --- | --- | --- |
| Skill = spec-conformant SKILL.md? | Curated catalog, coding-focused | ✅ explicit | ✅ explicit | ❌ (Topics/Actions, native model) | ❌ (Joule Skills, native model) | ❌ (native model) |
| Dedicated Skill Registry separate from Tool registry | ✅ (catalog vs. Gateway) | ✅ (Skills API vs. Toolbox) | ✅ (Skill Registry vs. tool ecosystem) | Implicit (Topic vs. Action) | Implicit (Joule Skills vs. Agent Hub) | Implicit |
| Native A2A support | Via Runtime | Preview | Native (Google-originated) | ✅ (endpoints for every custom agent) | ✅ | Partnered (Google Cloud) |
| Deterministic policy engine | Cedar (auto-generated from NL) | Entra + network isolation | Vertex AI policy | Trust Layer + platform sharing model | Agent Hub audit/governance | AI Control Tower |
| Built-in evaluators | 13 evaluators | ASSERT/Rubric/Agent Optimizer | Built-in eval framework | Command Center + Conversation Preview | — (governance-focused) | AI Control Tower monitoring |
| Standout strength | Framework/model neutrality, harness decoupling | Deepest Skills-spec conformance | A2A nativity, collision-safe registry | CRM-native permission inheritance | Financial/HR audit-readiness | Cross-agent governance/control tower |

---

## Deliverable 10 — Consolidated pattern/anti-pattern/vendor catalog

This file **is** Deliverable 10: the pattern catalog (Part A), anti-pattern catalog (Part B), and vendor-neutral comparison with platform references (Part C) above, together with the cross-references to files `01`–`10` for full best-practice detail on each row.

**Top five recommendations for any enterprise starting or maturing an Agent Skills program**, synthesized across every source reviewed:

1. **Separate the Skill registry from the Tool/MCP registry architecturally**, even if one platform's UI blurs them — this single distinction prevents the majority of the anti-patterns cataloged above.
2. **Make the deterministic Policy Enforcement Point non-negotiable** before scaling past pilot — every platform studied independently arrived at "model-side guardrails are not sufficient" as a first-order design constraint.
3. **Treat skill supply-chain security as a first-class governance gate**, not an afterthought — the ecosystem's own poisoning incidents in Q1 2026 make this the fastest-moving risk category in this entire research area.
4. **Instrument for OpenTelemetry GenAI conventions now, even while the spec is experimental** — the migration cost of retrofitting observability later is far higher than adopting an evolving-but-directionally-correct standard early.
5. **Build the enterprise metadata schema (file `02`) as the source of truth, and treat every vendor's native format as an export target**, not the other way around — this is what makes a federated, multi-platform registry (file `06`) actually achievable instead of aspirational.

## Related

- [Governance & Lifecycle](37-governance-and-lifecycle.md) — the previous section in this series.
