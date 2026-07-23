---
title: "Enterprise Agent Reference Architectures, Platform Engineering & Checklists"
date_created: 2026-07-07
last_reviewed: 2026-07-10
status: current
source_type: native-md
source_file: ""
tags: ["architecture", "platform-engineering", "enterprise-agents"]
doc_type: reference-architecture
covers_version: "as of 2026-07-10"
domain: architecture
topic_id: enterprise-agent-reference-architectures
supersedes:
  - docs/enterprise-architecture/ai-architecture/enterprise-agent-reference-architectures.md
---

# Enterprise Agent Reference Architectures, Platform Engineering & Checklists

**Current as of July 2026.** Domain-by-domain reference architecture deltas (banking, healthcare, insurance, retail, manufacturing, public sector, telco, software engineering, digital employees, customer support), the platform-engineering operating model, the July 2026 framework/runtime comparative analysis, architecture artifacts, best-practice canon, review checklists, and a 4-quarter migration roadmap.

---

## 1. Reference Architectures by Domain

All domains share the Vol 1 harness; this table captures the **deltas** — what each domain must add or tighten.

| Domain | Dominant constraints | Architecture deltas |
| -------- | --------------------- | --------------------- |
| **Banking** | Model risk management (SR 11-7 lineage), DORA, PCI, AML/KYC auditability | Agents classed as models → MRM validation before prod; dual-control on any funds-adjacent pivot; deterministic calculation engines (agents *orchestrate* pricing/risk engines, never compute them); full decision replay; on-soil model routing; A2A internal directories already live at scale (trade recon, KYC, reg reporting) |
| **Healthcare** | HIPAA/PHI, clinical safety, FDA boundary (decision support vs. device) | PHI tokenization before model egress; BAAs constrain provider list; clinician-in-the-loop on anything care-adjacent; provenance-cited outputs mandatory; strict separation of admin agents (scheduling, coding) from clinical-context agents |
| **Insurance** | Fairness/discrimination law on underwriting & claims, state regulators | Bias evals per release as gate; adverse-decision explanations (plan+evidence rendered human-readable); actuarial models stay deterministic behind tools; claims agents = classic Saga territory (reserve→adjust→pay with compensations) |
| **Retail / e-commerce** | Scale, margin, brand safety; agentic commerce | Heavy caching + small-model routing; price/promo actions bounded by deterministic guard tables; AP2/agent-payment rails with cryptographic consent mandates for buy-side agents; catalog MCP servers as the core tool estate |
| **Manufacturing** | OT/IT separation, safety-critical actuation | Agents advisory-only across the OT boundary (recommend; humans/PLC-level interlocks actuate); edge inference for latency; digital-twin tools for consequence-free simulation before any real action |
| **Public sector** | Sovereignty, FOIA/records, procurement, fairness | Sovereign/on-prem model hosting; every interaction a public record (retention by statute); explainability of citizen-affecting decisions; often air-gapped MCP topology with private registry mirrors |
| **Telecommunications** | Network-critical ops, massive event volume | Event-driven agent fleet on the incident bus; closed-loop remediation graduated (observe → recommend → auto-remediate low-risk classes with kill switches); config changes through existing change-management tools as MCP servers |
| **Software engineering** | IP protection, code provenance, CI safety | Git-workspace coordination pattern; agents get branch-scoped tokens (never main); CI as the verification gate; secret-scanning on every agent commit; sandbox = ephemeral dev container; SBOM/AI-BOM on agent-generated dependencies |
| **Digital employee** | Cross-system identity, HR-like lifecycle | Agent gets an *employee-like* identity in the IdP (joiner-mover-leaver process!), entitlement reviews, manager-of-record; calendar/email/ERP via MCP; the governance registry doubles as the "org chart" |
| **Customer support** | CX latency, deflection economics, compliance scripts | Swarm/handoff triage → specialist agents; confidence-based escalation to humans with full context transfer; response templates as deterministic rails for regulated statements; QA sampling pipeline scoring agent conversations |

---

## 2. Platform Engineering

The agent platform is a **product, run by a platform team, with golden paths.** Gartner projects 80% of large software-engineering organizations will have platform teams by 2026 (up from 45% in 2022).

**CI/CD** — Eval suites are merge gates (prompt/policy/agent changes blocked on regression); artifacts (containers, policy bundles, prompt packs, MCP manifests) signed (Sigstore) and immutable.

**GitOps** — Argo CD or Flux reconciling desired state including agent definitions, registry entries, and policy bundles from Git; Terraform for the cloud substrate; drift detection doubles as tamper detection.

**Runtime** — Kubernetes (or ECS) for control-plane services; sandbox fleet on Firecracker/gVisor node pools or managed runtimes (AgentCore Runtime, Azure Container Apps dynamic sessions); service mesh (Istio/Linkerd) for mTLS + SPIFFE identity + traffic policy; secrets via Vault/cloud KMS with dynamic short-lived credentials only.

**Progressive delivery** — Argo Rollouts/Flagger driving shadow → canary → GA with eval metrics as canary analysis inputs; feature flags (OpenFeature) on capabilities and guardrails; one-command rollback restoring code + prompt + policy + model-pin as an atomic set.

**Developer experience** — Backstage portal exposing golden-path templates ("create agent" scaffolds: harness SDK, eval harness, registry entry, dashboards pre-wired), self-service MCP-server onboarding with automated security tiering, local dev harness with recorded-replay of model calls for deterministic tests, and platform APIs.

**Platform KPI**: Score the platform on **time-to-first-agent-in-prod** and **% of agents on the golden path**.

---

## 3. Comparative Analysis (July 2026)

Scores: ● strong ◐ partial ○ weak/N-A. "Enterprise readiness" = managed isolation + identity + audit + support posture.

| Capability | AWS AgentCore | OpenAI Agents SDK | Google ADK | LangGraph | Semantic Kernel | CrewAI | AutoGen* | OpenHands | Claude Code | Copilot (agent) | Cursor |
| ------------ | --------------- | ------------------- | ------------ | ----------- | ----------------- | -------- | ---------- | ----------- | ------------- | ----------------- | -------- |
| **Category** | Managed runtime + services | Framework (+ managed tools) | Framework + managed platform | Framework + platform | Framework (.NET/Py) | Framework (+cloud) | Framework | Coding agent (OSS) | Coding agent (product) | Coding agent (product) | AI IDE/agent |
| **Security posture** | ● (session microVM isolation, IAM/Identity svc) | ◐ (guardrail hooks; infra yours) | ● (Model Armor, IAM, zero-trust guidance) | ◐ (platform adds auth; DIY otherwise) | ◐ (Azure integration strong) | ◐ | ◐ | ◐ (sandbox strong; enterprise DIY) | ● (permissioned tools, sandbox modes, enterprise policies) | ● (GitHub org policy surface) | ◐ |
| **Governance/registry** | ● (Gateway tool mgmt, policy hooks) | ◐ | ● (platform registry, Agentspace lineage) | ◐ (platform assistants registry) | ◐ | ○ | ○ | ○ | ◐ (enterprise mgmt, hooks) | ● (org controls, audit) | ◐ |
| **Memory** | ● managed (ST/LT strategies) | ◐ sessions | ● (platform memory bank) | ● (checkpointers, stores) | ◐ | ◐ | ◐ | ◐ (workspace-as-memory) | ● (files/skills pattern, auto-memory) | ◐ | ◐ |
| **Scalability** | ● serverless sessions | ◐ (yours) | ● (GCP) | ● (platform) / ◐ (DIY) | ● on Azure | ◐ | ◐ | ◐ | ◐ (per-seat/CI) | ● | ◐ |
| **Extensibility/protocols** | ● MCP+A2A native | ● MCP; handoffs | ● MCP+A2A native | ● MCP; anything Python | ● MCP; connectors | ◐ | ◐ | ● (OSS, MCP) | ● (MCP client+server, SDK) | ◐ (MCP arriving through GH ecosystem) | ● (MCP) |

**Selection Heuristics**

- **Cloud-committed + want managed isolation** → AgentCore / AI Foundry / Gemini Enterprise, per your cloud
- **Want portable, inspectable control flow you own** → LangGraph (+ Temporal spine)
- **.NET estate** → Semantic Kernel / Microsoft Agent Framework
- **Multi-language + A2A-first** → Google ADK
- **Fastest prototype** → OpenAI Agents SDK or CrewAI, then re-platform
- **Software-engineering agents** → Claude Code / Copilot as products; OpenHands where OSS control is required

**Realistic composition**: In practice enterprises run a managed runtime + one framework + Temporal + your own gateway/registry — no vendor covers the full harness alone.

---

## 4. Architecture Artifacts

Deliverables your architecture repo should contain:

**C4 set** — Context (users, agent platform, model providers, MCP/A2A counterparties, enterprise systems, regulators-as-stakeholder); Container (the harness planes as containers); Component (the component table is the inventory); plus a Deployment diagram and a Trust-boundary diagram.

**Sequence diagrams (minimum set)** — task happy path; approval-gated pivot action; injection-detected containment; checkpoint resume after crash; cross-org A2A delegation; saga compensation.

**Runtime interaction diagram** — the harness loop annotated with PEPs and telemetry emission points.

**Threat model & failure tree** — mapped to boundaries; a failure tree rooting "unacceptable outcome" down through guard layers.

**Risk register** — `{risk, owner, tier, controls, residual, test evidence, review date}`.

**Decision matrix & ADRs** — at minimum: orchestration pattern, workflow engine, policy language (Cedar vs OPA), identity fabric (SPIFFE vs cloud-native), memory engine, gateway build-vs-buy, framework choice.

**Technology radar (mid-2026):**

| Ring | Items |
| ------ | ------- |
| **Adopt** | MCP, A2A, OTel GenAI conventions, Temporal-style durable execution, Cedar/OPA, SPIFFE, microVM sandboxes, eval-gated CI |
| **Trial** | MCP Tasks/Apps (post-2026-07-28), AP2, guard-model ensembles, semantic caching, agent identity extensions to OAuth |
| **Assess** | Computer-use agents in prod, cross-org agent marketplaces, CRDT shared plans |
| **Hold** | Unmediated mesh topologies, chat-as-API integration, long-lived agent credentials, prompt-only guardrails |

**Capability map & maturity model**:

| Level | State |
| ------- | ------- |
| **L1** | Pilots — single agent, manual review |
| **L2** | Productionized — gateway, registry, evals |
| **L3** | Governed scale — policy-as-code, HITL tiers, cost mgmt |
| **L4** | Federated — A2A cross-domain, marketplaces, autonomous low-risk classes |
| **L5** | Optimizing — closed-loop eval→improvement, portfolio-level ROI management |

Most enterprises are **L2** in mid-2026; regulated leaders at **L3**.

---

## 5. Best-Practice Canon

1. Invariants in the harness, judgment in the model.
2. Single mediated path to models (AI gateway) and to actions (tool gateway).
3. Short-lived attested identity everywhere; delegation only narrows.
4. Idempotency keys + sagas make retries and failures safe.
5. Plan as reviewable artifact; verification against pre-declared criteria.
6. Provenance-tag all context; assume injection is survivable, not detectable.
7. Registries-of-record gate everything invokable.
8. Evals as merge gates; shadow before canary before GA.
9. Checkpoint at step boundaries; durable-execution spine.
10. Kill switches at four scopes, drilled quarterly.

### Anti-Patterns / Common Failure Modes

Direct model credentials in apps; unbounded loops without budget ceilings; retrying semantic failures; transcript-passing between agents (context flooding); approval UIs showing agent summaries instead of raw actions; memory writes without provenance; unpinned tool manifests (rug-pulls); unevaluated fallback models; shared caches across tenants; mesh topologies without mediation; treating guardrail classifiers as invariant controls; rollbacks that revert code but not prompts/policies/model-pins.

---

## 6. Review Checklists

### Architecture Review

- [ ] Every component has an owner
- [ ] All planes crossed only via mediation
- [ ] Trust boundaries documented
- [ ] Orchestration pattern justified by ADR
- [ ] Degradation ladder defined per use case
- [ ] Data-residency routing proven

### Security Review

- [ ] Lethal-trifecta separation verified per agent
- [ ] Tool manifests hash-pinned
- [ ] Tokens audience-bound, sender-constrained, ≤15 min
- [ ] Sandbox egress allowlisted
- [ ] Injection test suite in CI + red-team date on record
- [ ] Memory write-gating + bulk-invalidation path
- [ ] Approval UI shows raw actions, not summaries
- [ ] MCP 2026-07-28 posture: stateless handles user-bound/expiring, header/body integrity, Apps templates reviewed

### Operations

- [ ] SLOs + error budgets defined
- [ ] Kill switches tested (with date)
- [ ] DLQ triage runbook
- [ ] Checkpoint-resume game-day passed
- [ ] Cost budgets enforced pre-flight
- [ ] On-call playbooks for: injection, contamination, runaway-spend, approval-flood

### Governance

- [ ] All agents registered with risk tier + owner
- [ ] Eval gates wired in CI
- [ ] Audit lake immutable + retention/legal-hold implemented
- [ ] Model/agent cards published
- [ ] EU AI Act classification recorded per use case
- [ ] Entitlement (joiner-mover-leaver) reviews include agent identities

### Testing Strategy

Unit (tools, policies — policies get tests!) → recorded-replay agent tests (deterministic) → eval suites per capability (golden sets + LLM-judge with human calibration) → adversarial (injection/jailbreak corpora) → chaos (provider faults) → shadow production → sampled human QA in prod.

Non-determinism is managed by testing distributions against thresholds, not exact outputs.

---

## 7. Migration Roadmap (Typical 4 Quarters)

| Quarter | Theme | Deliverables |
| --------- | ------- | -------------- |
| **Q1 — Foundations** | Mediation + visibility | AI gateway in front of all model traffic; registries stood up; OTel + audit lake; identity fabric (SPIFFE/STS) for agent workloads; first agent moved behind the harness in shadow mode |
| **Q2 — Governed production** | Policy + durability | Policy-as-code PDP/PEPs; approval engine; eval-gated CI; checkpointing on Temporal/workflow spine; 2–3 use cases GA at risk tier ≤T2 |
| **Q3 — Scale** | Registry + memory + cost | MCP private registry + tiered onboarding; memory services with ACL/provenance; cost management with pre-flight budgets; canary/shadow automation; first T3 use case with dense HITL |
| **Q4 — Federation** | Cross-domain | Internal A2A directory; cross-domain supervisor patterns; DR/game days; maturity L3 audit; evaluate cross-org A2A with one partner under contract |

Throughout: migrate MCP servers toward the 2026-07-28 stateless model during its 12-month deprecation window.

---

## 8. Trends to Architect For (2027+)

- Standardized delegated authority for agents in OAuth
- MCP extensions ecosystem maturing
- A2A richer semantics
- Agent marketplaces with signed capability attestation
- Verification-first stacks
- Consolidation of harness services into cloud primitives
- Regulatory hardening (EU AI Act high-risk enforcement, sector-specific guidance)

The platforms described in this series are the compliance substrate — build once.
