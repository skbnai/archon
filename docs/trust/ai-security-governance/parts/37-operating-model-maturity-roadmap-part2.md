---
title: "Enterprise Agent Operating Model: Checklists, Interview Guide & Roadmap (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: operating-model-maturity-roadmap-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/06-Operating-Model-Maturity-Roadmap.md]
tags: [ai-security, checklists, interview-guide, roadmap]
covers_version: "as of 2026"
---

Production readiness gate checklists, a principal architect interview guide, a 24-month learning and implementation roadmap, and the certifications and standards bodies worth tracking.

## Security Review Checklists

These are intentionally condensed to the highest-leverage items — gate checklists for the two moments that matter most: approving a new agent for production, and approving a new MCP server or A2A counterparty for connection. Treat each as the pass/fail gate, not the complete control set.

**New agent production readiness checklist:**

- [ ] **Identity** — Agent has a SPIFFE SVID or equivalent workload identity; no static, long-lived credentials present.
- [ ] **Registry** — Agent Registry entry complete: purpose, sponsor, autonomy level, scoped tools.
- [ ] **Least Agency** — Autonomy level matches a documented risk classification; no standing access beyond what the level requires.
- [ ] **Threat model** — MAESTRO-based threat model completed and reviewed for this agent's architecture pattern.
- [ ] **Runtime isolation** — Sandboxing tier assigned matches the agent's trust-boundary exposure.
- [ ] **Tool scope** — Every tool/MCP connection passes gateway validation; no direct, unmediated credentials held by the agent.
- [ ] **Memory governance** — Memory writes are classified and provenance-tagged at write time; retention policy assigned.
- [ ] **Human oversight** — Approval gates defined for any irreversible or high-consequence action regardless of trust score.
- [ ] **Observability** — Agent is instrumented to the OpenTelemetry/OpenLLMetry standard and visible to the AI SOC.
- [ ] **Reliability** — SLIs/SLOs defined with an error-budget-triggered autonomy downgrade path.
- [ ] **FinOps** — Budget envelope and spend-velocity anomaly detection configured.
- [ ] **Kill switch** — Tested, identity-layer kill-switch capability confirmed before go-live.
- [ ] **Compliance crosswalk** — Agent's risk tier mapped against applicable regulation (EU AI Act Annex III high-risk status, DORA, PCI DSS, GDPR memory implications).

**New MCP server / A2A counterparty connection checklist:**

- [ ] **Provenance** — Server/agent publisher identity verified; for A2A, Agent Card signature cryptographically verified against the claimed domain.
- [ ] **Scanning** — Tool definitions and descriptions scanned for hidden-instruction/poisoning patterns prior to registration.
- [ ] **Schema validation** — Discovery-time and invocation-time schema validation both configured at the gateway, not discovery-time only.
- [ ] **Transport** — mTLS enforced; unauthenticated transport rejected by default policy.
- [ ] **Tool signing** — Tool signatures verified where supported; re-verification triggers configured to catch "rug pull" post-install modification.
- [ ] **Tenant isolation** — Multi-tenant servers confirmed to enforce session and credential isolation between tenants.
- [ ] **Trust broker** — External A2A counterparty has an assigned trust score and recorded trust relationship before any production task delegation.
- [ ] **Spend caps** — Per-task spend caps configured for any counterparty connection capable of initiating cost or financial transactions.
- [ ] **Audit logging** — Tamper-evident logging confirmed operational for the new connection before production traffic flows.
- [ ] **Supply chain** — Component recorded in the AI BOM with applicable provenance documentation (Model Card / Agent Card).

## Principal Architect Interview Guide

These questions distinguish candidates who have absorbed current best practice from those who can reason architecturally about a fast-moving, still-converging field — the latter matters more, because much of the specific tooling and even some of the standards will have moved by the time a hire is six months into the role.

**Architecture & threat modeling:** Walk through how you would threat-model a multi-agent system using MAESTRO, and specifically describe a cross-layer threat a single-layer review would miss. An agent has a clean identity, a clean trust score, and has behaved correctly for six months — describe a realistic attack path that still succeeds against it, and what control would have caught it. When would you choose Firecracker over gVisor over WASM for sandboxing an agent's tool execution, and what's the wrong reason to choose one over another?

**Identity & trust:** Explain the difference between authenticating a workload and authorizing an action, and describe a real architecture where conflating the two created a vulnerability. How would you design compound identity for an agent acting on behalf of a suspended user account, and what should happen? What is the structural limitation of SPIFFE for agent security, and what has to be layered on top of it?

**MCP / A2A:** Describe tool poisoning in your own words, and explain why discovery-time schema validation alone is insufficient to prevent it. A vendor pitches an MCP server with no gateway in front of it, claiming their server is "secure by design" — what is your response, and what would you require before connecting it? What changed in A2A v1.0 that materially improved enterprise trust in the protocol, and what gap still remains even with that change?

**Governance & judgment:** A business unit wants to deploy a full-autonomy agent against a use case you believe should be more supervised — walk through how you'd handle that conversation. How do you decide which emerging framework (a new OWASP sub-project, a new IETF draft, a new vendor "standard") is worth building architecture around versus tracking and waiting? Describe an incident where a reliability problem and a security problem were actually the same underlying issue, and how your operating model would surface that connection rather than splitting it across two teams.

## 24-Month Learning & Implementation Roadmap

This roadmap is sequenced for an enterprise architect or security architect building both their own expertise and the organization's capability simultaneously — the realistic situation most readers are in, rather than joining an already-mature function.

**Months 1-3 — Foundation.** Complete the foundational architecture work and produce an Agent Security Architecture Repository for at least one business unit as a pilot. Stand up an Agent Registry, even a minimal one, and run a discovery exercise to find every agent currently running in the enterprise — the inventory gap is almost always larger than expected. Begin or accelerate ISO 42001 gap analysis, particularly if any system may fall under EU AI Act Annex III high-risk classification given the enforcement milestone timeline.

**Months 4-9 — Identity & Protocol Security.** Deploy or extend a SPIFFE/SPIRE trust domain to cover agent workloads. Stand up an MCP gateway with the five-stage validation pipeline for at least the highest-risk tool integrations. Establish the AI Governance Board and produce the first version of the framework crosswalk. Define the five-level autonomy taxonomy and retroactively classify every registered agent.

**Months 10-15 — Operations & Resilience.** Stand up the AI SOC's cross-surface correlation capability, even in an early form, on top of an existing observability platform. Run the first red team exercise mapped explicitly against the OWASP ASI Top 10, and close the loop with the first purple-team detection patterns. Define and begin tracking the first Agent Reliability Engineering SLIs/SLOs. Build and test the unified kill-switch/circuit-breaker mechanism spanning both security and FinOps triggers.

**Months 16-24 — Scale & Future-Proofing.** Extend the A2A gateway and trust-broker infrastructure to cover external counterparties, if the enterprise's use cases require cross-organization agent collaboration. Pilot delegated agent spending under AP2 or an equivalent payment-mandate protocol for a bounded, low-risk use case, with full FinOps and cognitive-security controls in place first. Begin architecting crypto-agility into every new identity, MCP, A2A, and payment-mandate component — not a full PQC migration, but ensuring nothing built in this window becomes a forklift-upgrade liability later. Conduct a full maturity-model self-assessment and set the explicit, board-approved target maturity level for the following 24 months.

## Certifications, Standards, and Communities to Track

**Certifications:**

| Certification | Focus | Best Fit |
|---|---|---|
| CAISP (Certified AI Security Professional) | Full-stack AI security: prompt injection, NIST AI RMF alignment, AI red teaming, OWASP LLM Top 10 and agentic attack patterns | Security professionals and architects wanting balanced offense/defense/governance coverage; widely cited as the broadest single AI security credential |
| COASP (Certified Offensive AI Security Professional) | Pure offensive specialization: AI attack-surface mapping, adversarial ML, agentic exploitation, AI incident response | Experienced red teamers adding AI-specific offensive skills |
| OSAI (OffSec) | Offensive AI techniques with an extended, exam-style endurance assessment | Practitioners who already hold OffSec credentials and want AI-specific depth |
| AIGP (AI Governance Professional, IAPP) | Policy, compliance, and risk management rather than technical security | GRC professionals, privacy officers, and AI Governance Board members rather than hands-on architects |

AI security roles are commanding meaningfully elevated compensation, reported in the roughly $150,000-$290,000 range depending on seniority and specialization, reflecting both the acute skills shortage and the speed at which the field is professionalizing.

**Standards bodies and initiatives to track directly:** the OWASP GenAI Security Project is the primary source for the ASI Top 10, the emerging MCP Top 10, the Agentic Skills Top 10, and the AIBOM Generator initiative; the Cloud Security Alliance maintains the MAESTRO framework and ongoing research on agent identity and NHI; NIST's AI Agent Standards Initiative and the NCCoE agent identity concept paper are worth tracking for the eventual interoperability profile; the IETF WIMSE working group covers workload-identity-to-workload-identity authentication standards underpinning the AIMS draft architecture; the Linux Foundation's Agent2Agent Protocol Project is the neutral governance body for A2A since Google's 2025 donation; the FIDO Alliance Payments Technical Working Group now governs AP2's standards-track evolution, including its post-quantum profile; and MITRE ATLAS is the continuously updated adversary-tactics knowledge base for AI-specific techniques.

**Open-source tooling worth evaluating:** SPIFFE/SPIRE (CNCF) is the reference workload-identity implementation; OWASP MCP-Scan and equivalent scanners (Cisco mcp-scanner, Snyk agent-scan) provide pre-deployment MCP tool scanning; OpenLLMetry/Traceloop provides vendor-neutral OpenTelemetry instrumentation for agent and LLM traces; MAESTRO threat-modeling tooling from the Cloud Security Alliance provides AI-assisted, layer-by-layer threat identification; Promptfoo and DeepTeam are open-source red-teaming frameworks with test suites mapped directly to the OWASP ASI Top 10; and Open Policy Agent (OPA) and Cedar remain the two leading policy-engine choices for the centralized authorization layer specified throughout this series.

## Closing Note: How to Use This Guidance

A large reference architecture, a stack of checklists, and a multi-year roadmap are only useful if they change what gets built and funded. The single most consequential decision an enterprise can make is to fund the identity substrate first. Almost everything else — MCP gateway policy, A2A trust brokering, agent registry enforcement, FinOps circuit breakers, even post-quantum migration — becomes simpler, cheaper, and more defensible once every agent, tool, and peer in the ecosystem carries a verifiable, ephemeral, centrally governed identity. Build that first, build the governance fabric around it second, and treat the remaining domains as the detailed specification for what to do once that foundation is in place, not as a checklist to attack in parallel from a standing start.

This guidance reflects the state of a genuinely fast-moving field as of mid-2026. Treat the architectural patterns — identity-first design, centralized gateways, layered threat modeling, autonomy earned rather than granted by default — as durable. Treat the specific vendor names, protocol version numbers, and standards-body timelines as a snapshot to be re-verified against current sources before any major investment decision.

## Related

- [Enterprise Agent Operating Model & Maturity Model (Part 1)](../37-operating-model-maturity-roadmap.md)
- [Enterprise Governance](../18-enterprise-governance.md)
- [AI Control Series Overview](../01-ai-control-series-overview.md)
