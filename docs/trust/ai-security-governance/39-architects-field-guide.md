---
title: "Architect's Field Guide: Inherited Mess & Identity Rebuild"
doc_type: case-study
domain: trust
status: current
topic_id: architects-field-guide
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/08-Architects-Field-Guide.md]
tags: [ai-security, case-study, identity, architecture]
covers_version: "as of 2026"
---

A fictionalized six-month case study — one architect, one bank, greenfield build through live incident — following Meridian Trust Bank's inherited agent sprawl and identity rebuild. Companion narrative to the [Foundations & Reference Architecture](33-foundations-reference-architecture.md) series and the [Zero-to-Mastery Curriculum](38-zero-to-mastery-curriculum.md).

**Fictionalization note:** Meridian Trust Bank, its personnel, and this engagement are fictional, composited from realistic patterns observed across organizations this program is written for. Every technical mechanism, control, and tradeoff described is grounded in the same 2026 material underlying the rest of this program.

## How This Guide Works

The reference architecture and the ten-stage curriculum teach by domain — identity, then MCP, then A2A, then governance — each treated as its own complete topic. That's right for reference material and systematic skill-building. It is not how work actually arrives in a real job, where an architect inherits a partial mess, sequences decisions under competing pressure, and discovers which decisions were right only months later, sometimes at 2 a.m.

This guide does the opposite: it follows one fictional organization, Meridian Trust Bank, through one architect's first six months — the inherited mess, the identity rebuild, an MCP/A2A rollout under deadline pressure, a compliance crunch, standing up real operations, a live security incident, and the postmortem. The technical substance is identical to the rest of the program; what differs is the order decisions arrive in, under real pressure, rather than a reference manual's tidy domain-by-domain order.

Recurring elements: **The Architect's Reasoning** — the thinking behind a decision, including what was weighed and discarded. **Decision Point** — a genuine fork in the road, with the real options considered, tradeoffs, and which was chosen and why. **Exhibit** — an actual artifact (a policy file, a token structure, a config snippet) illustrating what a decision produced in concrete form. **Field Note** — a lesson that generalizes beyond Meridian, flagged explicitly.

**Meridian Trust Bank — quick reference.** Profile: ~$40B in assets, regional retail and commercial bank, EU client nexus creating partial EU AI Act exposure. Starting position: 47 agents in production or near-production, discovered (not officially inventoried) across six business units, no central governance, eighteen months of organic, ungoverned AI adoption. Role: first Enterprise Agentic AI Security Architect, reporting to the CTO, with a CISO-adjacent mandate until a dedicated AI CISO is hired. The arc: Chapter 1 (discovery) → Chapter 2 (identity) → Chapter 3 (MCP/A2A under deadline) → Chapter 4 (governance/compliance crunch) → Chapter 5 (operations stand-up) → Chapter 6 (the incident) → Chapter 7 (the fix and what it teaches).

## Chapter 1: The Inherited Mess

*Week 1 on the job.*

Meridian is a fictional but realistic mid-size regional bank with an eighteen-month-old internal AI initiative that has, in the CTO's words, "gotten ahead of itself." This is your first Monday as the bank's first Enterprise Agentic AI Security Architect. The technical content that follows is identical in substance to the reference program and the curriculum; what's different is the order you encounter it in — the order a real engagement forces on you.

Your first two days are meetings and log access requests, not design work. By Wednesday you have a real picture: **47 distinct agents** in production or near-production use across six business units — your own count, not the 31 the existing "AI inventory" spreadsheet shows. **Identity:** 41 of 47 agents authenticate using a shared service-account pattern — three Azure service principals, each with broad Graph API and internal API scopes, reused across many unrelated agents. **MCP:** a platform team stood up an internal gateway eight months ago for one team; eleven other teams have since connected without review, and four teams run unmanaged MCP servers entirely outside it. **A2A:** none in production yet, but commercial lending is six weeks from launching an agent negotiating document exchange with a loan-origination SaaS vendor's agent — discovered by accident in a Slack channel, not through governance. **Governance:** no AI Governance Board exists; the bank's existing model-risk-management function, built for traditional statistical/ML credit models under SR 11-7-style governance, has never reviewed an agentic system. **Regulatory exposure:** flagged but unconfirmed EU AI Act Annex III high-risk triggers for a subset of services, ahead of the Act's enforcement date (December 2027 for Annex III, after the Digital Omnibus deferral). **Prior incident:** a near-miss four months earlier, when a marketing-content agent with an overly broad CRM scope drafted and nearly auto-sent a customer email containing another customer's account details — caught only because a human reviewer noticed; the agent's scope was never revisited.

**The Architect's Reasoning.** Every finding maps to something specific from the reference program, and recognizing the mapping immediately is what "mastery" cashes out to in a real engagement. The shared service-account pattern is the static-credential anti-pattern. The unmanaged MCP servers are a live ASI04 supply-chain exposure. The A2A launch discovered in a Slack channel is exactly the scenario the gateway pattern exists to prevent. The near-miss is autonomy granted without an autonomy-level framework. The instinct under this much pressure is to fix the loudest fire first — usually the A2A launch, because it has a date and a sponsor. Resist it. The first job isn't fixing anything; it's establishing a single source of truth for what exists, because every fix made on incomplete information will need to be redone once the full picture emerges — and redone identity work has a way of leaving orphaned grants nobody remembers to clean up.

**Decision Point: where do you spend your first three weeks?** The CTO wants a plan by Friday; lending wants their A2A launch unblocked; Legal wants an EU AI Act answer. Three options: stop the A2A launch and fix it first (addresses the most visible, time-boxed risk, but builds A2A trust controls on the same shared-service-account problem — solving the wrong layer first); do a full regulatory gap analysis first (satisfies Legal's urgency, but produces a compliance document describing controls that don't exist yet — close to worthless as an audit artifact); or **agent discovery and identity foundation first** (slower to produce a week-one deliverable, but correctly sequences the rest of the work).

**Rationale:** this is the same conclusion the reference program reaches by a different route — fund the identity substrate first, because almost everything else gets simpler once it exists. Week one closes the inventory gap (47 vs. 31); weeks two and three stand up SPIFFE/SPIRE and a compound-identity pattern, even though neither produces anything visibly exciting for Friday. What you show the CTO instead is the inventory gap itself: a clear, numbers-based argument that the bank cannot make a credible A2A decision or regulatory claim while it doesn't know what it's running. That argument usually buys the three weeks.

**Field Note.** In a real engagement, the hardest part of identity-first sequencing is rarely the technical argument — it's the political one. The inventory gap (47 vs. 31) wins every time, because it's concrete, numeric, and not abstract architecture talk — "we don't actually know what we're running" lands with any executive regardless of technical background.

## Chapter 2: The Identity Rebuild

*Weeks 2-6.*

Three Azure service principals carry the authentication load for 41 of 47 agents. Two have Graph `User.Read.All` and `Mail.Send` scopes far broader than any individual agent needs, because at some point an engineer needed `Mail.Send` for one agent, had no narrower role available, and reused an over-scoped credential rather than requesting a new one through what was, at the time, a multi-week process. This isn't a story about careless engineers — it's a story about a credential-provisioning process so slow that reusing a broad credential was the path of least resistance.

**The Architect's Reasoning.** It's tempting to treat that paragraph as background color and skip to the SPIFFE deployment plan. Don't. The over-broad credentials exist because of a process failure, not a technology failure — if the new identity architecture doesn't also fix provisioning speed, engineers will route around it again within a quarter, just as they did the first time. Every identity decision in this chapter is evaluated against one extra criterion beyond the usual security properties: can a developer get a correctly-scoped credential for a new agent in roughly the same time it used to take to grab a broad one. If not, the architecture fails in practice regardless of how sound it is on paper.

**Building the SPIFFE/SPIRE trust domain.** The design follows the standard identity-substrate pattern directly: a SPIRE server stood up with trust domain `spiffe://meridian-agents.internal`, SPIRE agents on every Kubernetes cluster and VM scale set hosting agent workloads. Attestation selectors are registered per workload — Kubernetes-hosted agents use namespace, service account, and a signed container-image digest; VM-hosted legacy agents use cloud instance metadata and a host-level attestation agent.

**Exhibit — SPIRE registration entry (customer support agent, Kubernetes-hosted):**

```
spire-server entry create \
  -spiffeID spiffe://meridian-agents.internal/agent/support/ticket-responder \
  -parentID spiffe://meridian-agents.internal/spire/agent/k8s-psat/prod-cluster \
  -selector k8s:ns:agents-support \
  -selector k8s:sa:ticket-responder-sa \
  -selector k8s:container-image-digest:sha256:8f2a1c...e94b \
  -ttl 3600
```

The one-hour SVID TTL was a deliberate, debated choice — short enough to make a stolen SVID close to worthless quickly, long enough to avoid excessive re-attestation load across roughly 50 agents and growing. SPIRE handles rotation transparently, so the number can be tightened later once the rotation infrastructure proved itself under real load for a month.

**Solving compound identity — the actual hard part.** SPIFFE alone answers "which agent process is this." Meridian's harder problem was compound identity: the customer support agent acts on behalf of specific support staff, sometimes triggered by an inbound ticket with no human directly in the loop, and every action needs to be traceable to a specific accountable human or an explicit, documented exception for fully autonomous action.

**Decision Point: how does the agent carry "who it's acting for"?** Three options: the agent impersonates the support staff member directly (simplest against existing Entra ID, but destroys the human/agent audit distinction — flagged by compliance as a non-starter for SOC 2 and internal audit); build a separate, parallel agent-identity claims system (maximum flexibility, but creates exactly the "two incompatible identity systems" fragmentation the reference architecture warns against, and the existing identity team would reasonably resist owning a system they didn't build); or **RFC 8693 token exchange with an actor claim, integrated into the existing Entra ID tenant** (more upfront integration work, but keeps one identity system of record and gives the existing team a clear ownership boundary). The third was chosen.

The agent's SVID authenticates the workload to an internal token-exchange service, which mints a short-lived JWT carrying both the agent's own identity and an actor claim identifying the human or business process the action is performed for. For ticket-triggered autonomous actions with no specific human in the loop, the actor claim names a registered "autonomous action" service identity rather than a real person — a detail that mattered enormously during the Chapter 6 incident, because it let the audit trail immediately distinguish a genuinely autonomous action from one falsely claiming human sponsorship.

**Exhibit — compound identity token (decoded, illustrative):**

```json
{
  "iss": "https://identity.meridian.internal",
  "sub": "spiffe://meridian-agents.internal/agent/support/ticket-responder",
  "act": {
    "sub": "svc:autonomous-ticket-triage",
    "acting_for": "support-team:tier1",
    "authorization_basis": "policy:AUTO-TICKET-REPLY-V2"
  },
  "scope": "crm:read ticket:read email:draft",
  "exp": 1719014400
}
```

**Field Note.** The `authorization_basis` field isn't in any textbook diagram of an actor-claim token — it was added when the bank's internal auditor asked, reasonably, "when I see this token in a log six months from now, how do I know what policy authorized this action without finding the engineer who built it." Build a habit of asking what a token needs to say to a future, less-informed reader, not just to the system validating it right now.

**The migration — not a cutover.** 47 agents don't migrate from shared service accounts to SPIFFE identity in one weekend; trying to would itself be a high-risk, low-visibility change. The migration ran in three waves over five weeks: **Wave 1 (week 3)** — 6 lowest-risk, read-only agents (documentation search, meeting-notes summarizers), validating the SPIRE deployment and token-exchange service under real but low-consequence load. **Wave 2 (weeks 4-5)** — 28 agents with limited write access (ticket systems, internal wikis, non-financial CRM fields), the bulk of the fleet, surfacing most integration friction while consequences of a mistake stayed contained. **Wave 3 (week 6)** — 13 highest-risk agents, including the customer support agent and anything touching financial or PII-sensitive systems, migrated last and individually reviewed.

Each wave ran both identity systems in parallel for 48 hours — the agent authorized under the old shared account while simultaneously shadow-validated against the new SPIFFE-based policy, mismatches logged but not enforced — before cutting over. This shadow-mode pattern caught eleven scope mismatches across the three waves that would otherwise have caused either an outage or a silent over-grant.

**The Architect's Reasoning.** Eleven scope mismatches out of 47 agents is worth sitting with — roughly a quarter of the fleet where nobody, not the original developer, not the platform team, not you, actually knew what access the agent needed until shadow-mode made the gap visible. This is the strongest empirical argument for the migration approach, worth keeping as a story for the next stakeholder who suggests a faster cutover: a "fast" migration that skips shadow-mode validation isn't actually faster, it's deferring the discovery of these mismatches to the first production incident they cause.

## Related

- [Architect's Field Guide: MCP/A2A Under Pressure & Governance Crunch (Part 2)](parts/39-architects-field-guide-part2.md)
- [Identity/MCP/A2A Security Blueprint](34-identity-mcp-a2a-security-blueprint.md)
- [Zero-to-Mastery Curriculum: Program & Foundations](38-zero-to-mastery-curriculum.md)
