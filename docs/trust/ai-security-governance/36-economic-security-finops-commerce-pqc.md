---
title: "Economic Security: Agent FinOps & Autonomous Commerce"
doc_type: guide
domain: trust
status: current
topic_id: economic-security-finops-commerce-pqc
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/05-Economic-Security-FinOps-Commerce-PQC.md]
tags: [ai-security, finops, ap2, autonomous-commerce]
covers_version: "as of 2026"
---

Budget and cost as an attack surface, the Agent FinOps platform design specification, and the AP2 trust model for autonomous commerce with delegated payment authority.

## Economic Risk Does Not Fit Neatly Into Existing Controls

An autonomous agent's ability to consume budget, and increasingly to spend real money, moves at a velocity no human approval workflow was designed for. A misconfigured agent in an infinite tool-call loop is not just a reliability incident — it is a financial incident, potentially a large one, measured in minutes rather than the days or weeks a traditional procurement-fraud control was built to catch. As the industry's payment infrastructure for agents — principally Google's Agent Payments Protocol (AP2), now contributed to the FIDO Alliance for standards-track governance — moves from pilot to production, agents are beginning to hold delegated authority to actually move money, not just request that a human move it.

## Agent FinOps & Economic Security

**Threat landscape: budget and cost as an attack surface.** Budget exhaustion attacks have an attacker (external or an internal compromised agent) deliberately drive an agent or agent fleet to consume its allocated compute/API budget, either to deny service to legitimate use or as a denial-of-wallet attack against the enterprise directly. The A2A protocol's historical default of unauthenticated endpoints is a direct enabler here: an unauthenticated A2A endpoint can be assigned unlimited resource-heavy tasks by any caller, draining budget with no transaction ever reaching a human approval gate. Cost amplification attacks exploit a multi-agent delegation chain so a single low-cost triggering action fans out into many expensive downstream calls — a single poisoned input causing a cascading failure (ASI08) that is also, simultaneously, a cost-amplification event. Autonomous spending risks expand the threat model as agents gain delegated payment authority via AP2 and similar protocols, from "the agent wasted compute budget" to "the agent authorized an unauthorized real-world financial transaction" — a materially different risk category requiring materially different controls. Agent cost governance gaps are common: most organizations deploying agents have observability into token and API cost but lack the governance layer that ties cost anomalies to the same kill-switch and policy-enforcement infrastructure used for security incidents, meaning a runaway-cost event and a security incident are detected by different teams, on different dashboards, with different response playbooks, even though the underlying control (stop this agent now) is identical.

**Agent FinOps platform — design specification.** Cost governance should be a first-class policy dimension enforced at the same control point as security policy, not a separate, downstream reporting function reconciled at month-end:

| Component | Function | Integration Point |
|---|---|---|
| Per-agent budget envelope | Hard ceiling on spend (compute, API, and where applicable real-money) assigned at agent provisioning, tied to autonomy level | Enforced at the policy engine (Cedar/OPA) alongside security authorization, not in a separate billing system |
| Real-time spend tracking | Continuous, sub-minute-latency tracking of consumption against budget envelope per agent, per task, per session | Fed from the same trace/telemetry stream used by the AI SOC |
| Anomaly detection on spend velocity | Statistical and rule-based detection of spend-rate anomalies (a 10x normal burn rate in five minutes is a signal regardless of whether any individual action looks malicious) | Correlated with AI SOC detection logic — a spend anomaly should trigger the same investigation workflow as a security anomaly |
| Automatic circuit breakers | Budget envelope breach triggers automatic task suspension, not just an alert; tied to the kill-switch framework | Same revocation mechanism as a security-triggered kill switch (credential/SVID revocation), not a soft "please stop" signal |
| Cost-per-outcome reporting | Cost normalized against the ARE reliability metric "cost-per-successful-task," not raw spend alone | Feeds both FinOps reporting and the reliability error-budget calculation, connecting cost directly to whether the spend produced value |

**Design principle: one circuit breaker, two trigger sources.** Build a single kill-switch and circuit-breaker mechanism that can be triggered either by security policy violation or by budget-envelope breach, rather than building two separate emergency-stop systems owned by two different teams. The two trigger sources are correlated more often than not — runaway cost is frequently the first observable symptom of a cascading failure or a compromised agent, well before a security-specific signal fires.

## Autonomous Commerce Security

Autonomous commerce — agents that can browse, select, negotiate, and complete purchases or payments on a human's or organization's behalf — moved from demonstration to standards-track infrastructure with the release of Google's Agent Payments Protocol (AP2) in September 2025 and its subsequent contribution to the FIDO Alliance for industry-wide standards governance. This is the clearest signal yet that autonomous commerce is being treated by the industry as production infrastructure requiring the same rigor as existing payment rails, not as an experimental feature.

**AP2 architecture and trust model.** AP2 addresses a structural problem traditional payment APIs were never designed for: they assume an explicit, real-time human authorization at the moment of transaction, which does not hold when an agent is acting on delegated authority, potentially asynchronously, on a task a human approved in general terms some time earlier. AP2's answer is to make consent and intent cryptographically verifiable and explicit at each stage of the transaction, rather than inferred from the fact that an authenticated session initiated the request.

| AP2 Concept | Function | Security Property It Provides |
|---|---|---|
| Mandates (Intent / Cart) | Cryptographically signed documents capturing what the user authorized — an Intent Mandate for general authorization ("book me a flight under $500") and a Cart Mandate for the specific transaction the agent assembled before execution | Verifiable, non-repudiable proof of what was actually authorized, closing the gap between general delegation and specific action |
| Role separation | Distinct roles (the user's Shopping Agent, the merchant's Credential Provider, the payment processor) such that no single role sees more than it needs — the Shopping Agent never sees raw payment credentials, for example | Limits blast radius of any single role's compromise; directly analogous to the tool-broker credential-custody pattern in the secure agent OS |
| Verifiable settlement receipts | Deterministic, auditable proof that a transaction settled as authorized | Supports dispute resolution and regulatory audit without relying on trust in any single party's transaction log |
| Per-task spend caps | Hard limits scoped to the specific delegated task, independent of the agent's broader FinOps budget envelope | A second, transaction-specific control layer on top of the general budget-governance layer — defense in depth for spending authority specifically |

Independent security analysis of AP2 reports a meaningful fraud-rate improvement over API-centric agent payment integrations — base fraud rates around 2.1% for conventional API-based agent payment flows versus approximately 1.15% under AP2's verifiable-intent model, with the largest improvement specifically in tampering-related fraud, attributed to the mandate-signing mechanism making transaction tampering cryptographically detectable rather than merely procedurally discouraged.

**Demonstrated attack surface: prompt injection against payment agents.** Published red-team research targeting AP2 specifically via prompt injection confirms what cognitive-security research would predict: a payment protocol's cryptographic guarantees protect the integrity of a mandate once it is signed, but do nothing to prevent an agent from being manipulated, via prompt injection in content it processes, into forming and signing a mandate it should never have formed in the first place. The cryptography is sound; the upstream goal-hijack risk (ASI01) is unchanged by it. This is the single most important architectural lesson in this domain: a verifiable-payment protocol secures the transaction, not the decision to transact, and cognitive-security and Least Agency controls remain fully necessary even after a strong payment protocol like AP2 is adopted.

**Enterprise autonomous commerce security architecture.** Delegated spending authority is scoped identically to the agent's autonomy-level taxonomy — a low-autonomy agent requires per-transaction human approval regardless of AP2 mandate signing; only high-autonomy agents should hold standing delegated payment authority, and even then bounded by per-task spend caps. Wallet-based transactions and stored payment credentials are never held directly by the purchasing agent — consistent with the tool-broker credential-custody architecture, the agent requests a scoped, single-use payment token from a credential broker rather than holding reusable payment credentials in its own context or memory. Procurement agents operating against external vendor or marketplace A2A endpoints require the same Agent Card signature verification and trust-broker evaluation specified for any external A2A counterparty before any mandate is formed, not just before settlement. Every formed Cart Mandate is logged to the immutable audit trail with full provenance of the inputs (which documents, search results, or tool outputs influenced the purchasing decision), specifically to support post-incident forensic reconstruction of how a malicious mandate was formed if cognitive-security controls fail. Spend caps under the FinOps envelope and AP2's per-task mandate caps are treated as independent, redundant controls — a misconfiguration in one should not silently remove the protection of the other.

## Related

- [Economic Security: Quantum-Ready Agent Security (Part 2)](parts/36-economic-security-finops-commerce-pqc-part2.md) — NIST post-quantum standards, practical migration constraints, and the post-quantum agent fabric design
- [AI Control Architecture](08-ai-control-architecture.md)
- [Identity/MCP/A2A Security Blueprint](34-identity-mcp-a2a-security-blueprint.md)
