---
title: "Identity/MCP/A2A Security Blueprint: A2A Security (Part 3)"
doc_type: guide
domain: trust
status: current
topic_id: identity-mcp-a2a-security-blueprint-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/02-Identity-MCP-A2A-Security-Blueprint.md]
tags: [ai-security, a2a, agent-cards, gateway, zero-trust]
covers_version: "as of 2026"
---

Agent-to-Agent (A2A) protocol mechanics, the documented A2A threat landscape, the enterprise A2A gateway architecture, and the unified identity-to-trust chain spanning identity, MCP, and A2A.

## Agent-to-Agent (A2A) Security

Where MCP governs how an agent talks to tools, A2A — Google's Agent2Agent protocol, donated to the Linux Foundation in June 2025 and now governed under neutral, multi-vendor stewardship as the Agent2Agent Protocol Project — governs how agents talk to each other as peers across organizational and vendor boundaries. A2A reached v1.0 in early 2026 and v1.2 by late March 2026, with more than 150 organizations in production and launch partners spanning Accenture, Atlassian, Salesforce, SAP, ServiceNow, PayPal, and Deloitte — meaning this is no longer an experimental protocol for most large enterprises' partner ecosystems; it is rapidly becoming load-bearing infrastructure.

**A2A protocol mechanics.** Agent Cards are the protocol's discovery mechanism: a structured document an agent publishes describing its capabilities, supported authentication schemes, and endpoint; other agents retrieve and incorporate Agent Cards into their own planning context to decide whether and how to delegate a task. Discovery is the process by which a host agent locates and evaluates candidate remote agents for a given task, typically by retrieving and comparing Agent Cards. Federation is the explicit design goal of cross-organization, cross-framework interoperability that lets agents built on LangGraph, CrewAI, or any other framework expose themselves as A2A peers and collaborate regardless of underlying implementation. Trust Establishment, as of A2A v1.0, works through Signed Agent Cards — a cryptographic signature tied to the publishing domain, allowing a receiving agent to verify a card actually originated from the domain it claims to; this was the single change the protocol's stewards identify as having unblocked enterprise procurement, because it answers "can we trust this Agent Card came from where it claims to?" Delegation is the mechanism by which a host agent assigns a task to a remote agent, carrying forward (or explicitly not carrying forward) authorization context.

## A2A Threat Landscape

The protocol's own stewardship has been explicit that authentication, prior to v1.0, was effectively optional in the specification — implementers were left to build their own credential management, and unauthenticated default deployments were common. This created, and continues to create where v1.0 protections are not yet adopted, a specific and well-documented set of risks.

**Agent Card Poisoning / Metadata Injection** embeds malicious instructions in Agent Card metadata fields that a host agent's LLM-driven reasoning engine incorporates into its planning context — demonstrated in published research using a simulated hotel-booking delegation scenario where poisoned card metadata caused unintended transmission of PII and payment data to an attacker-controlled endpoint. **Agent Card Spoofing / Forgery** occurs when an attacker stands up a fake Agent Card at a domain they control, redirecting other agents to a malicious endpoint; this is mitigated by Signed Agent Cards in A2A v1.0+, but the spec supports rather than enforces signing, so unsigned deployments remain vulnerable, including via DNS or CDN compromise. **Agent Card Shadowing** is the unauthorized cloning or mirroring of a legitimate agent's advertised skills to impersonate it within a collaborative workflow, closely related to and often co-occurring with direct impersonation attacks. **Agent-in-the-Middle** attacks have an intermediary agent intercept and manipulate A2A traffic between two legitimate peers, demonstrated in 2025 security research. **Rogue / Compromised Trusted Agents** — an agent legitimately onboarded and trusted that is later compromised, with its established trust exploited to covertly extract credentials and data while evading detection — is the most operationally dangerous pattern, precisely because the agent's prior trusted status lowers the probability of detection. **Task Poisoning / Unauthenticated Resource Exhaustion** happens when default unauthenticated endpoints accept unlimited task assignments from any caller, allowing a compromised internal system or external actor to drain an organization's API/compute budget with infinite resource-heavy tasks — identified as the most direct production risk of deploying A2A endpoints with default (unauthenticated) configuration. **Privilege Escalation via Delegation Chains** occurs when a task delegated through multiple agent hops accumulates or loses authorization context in ways that grant the final executing agent more privilege than any single hop was meant to confer — a structural risk of any multi-hop delegation protocol without explicit, end-to-end authorization-chain validation.

**The sensitive-payload gap.** Despite its strengths in cross-provider interoperability, A2A currently lacks specialized safeguards for particularly sensitive payloads — payment credentials, identity documents — beyond generic token expiry. The complementary AP2 (Agent Payments Protocol) extension, with more than 60 payments and financial-services launch partners, is the protocol stewards' answer for the payments case specifically, adding verifiable mandates, deterministic settlement receipts, and per-task spend caps. For non-payment sensitive data, enterprises should not assume A2A's base protections are sufficient and should apply additional field-level encryption and data-minimization controls on top of the protocol's default transport security.

## Enterprise A2A Gateway — Secure Architecture

As with MCP, the architecturally sound response to a protocol that delegates security decisions to implementers is to centralize those decisions in a gateway rather than trusting every individual agent deployment to implement them correctly and consistently.

| Gateway Function | Implementation Pattern |
|---|---|
| Discovery Validation | Every inbound Agent Card is cryptographically verified against its signature before being trusted; unsigned cards from external domains are rejected by default policy, with signed-card verification mandatory for any cross-organization A2A relationship |
| Claims Mapping | Authorization claims carried in A2A delegation requests are mapped to the enterprise's internal compound-identity model so an external agent's claimed authority is translated into, and bounded by, internal policy — never trusted at face value |
| Trust Broker | A centralized component maintains the trust relationships and current trust scores for every known external agent counterparty, replacing ad hoc point-to-point trust decisions made by individual internal agents |
| Policy Evaluation | Every delegated task is evaluated against policy (budget limits, data-sensitivity boundaries, allowed task types) before being accepted from, or sent to, an external A2A peer |
| Audit Logging | Full request/response capture for every A2A interaction, tied to the compound identity of both the internal and external agent, supporting incident-response and regulatory audit requirements |

Published A2A security research applying the MAESTRO threat-modeling framework specifically to A2A recommends a concrete control bundle worth adopting directly: Agent Card digital-signature verification combined with input sanitization; mutual TLS paired with OAuth 2.0/OIDC and JWT-based per-request authentication; nonce-and-MAC-based replay prevention for tasks; strict schema validation; TLS 1.3 with certificate pinning and DNSSEC; cryptographic artifact-integrity hashing; tamper-evident audit logging; and software-supply-chain security via SBOM and dependency scanning for the A2A client/server implementations themselves. This control set is scoped to protocol-level communication security — it does not address model-level cognitive vulnerabilities (goal hijacking once a task is accepted), which remain the responsibility of separate cognitive-security controls.

## Synthesis: The Unified Identity-to-Trust Chain

Read end to end, identity, MCP security, and A2A security describe one continuous trust chain rather than three separate domains. A workload identity (SPIFFE SVID) establishes which process is running. A compound identity claim establishes who that process is acting for. An MCP gateway uses that identity to authorize what tools the process may call and with what parameters. An A2A gateway uses the same identity substrate to establish whether this agent can be trusted by — and can trust — a peer agent outside the organizational boundary. Every layer re-validates rather than inheriting trust from the layer below, which is the practical meaning of Zero Trust applied to agents.

**The single highest-leverage architectural investment.** If an enterprise can only fund one piece of this blueprint in year one, fund the identity substrate: a SPIFFE/SPIRE trust domain extended to cover every agent, MCP server, and A2A endpoint, paired with a centrally managed policy engine (Cedar or OPA) that every gateway calls into. MCP gateway controls and A2A gateway controls both become dramatically simpler to build and operate once they can assume a trustworthy, centrally issued identity is already present on every request — and conversely, no amount of gateway sophistication compensates for an identity layer built on static API keys and shared service accounts.

## Related

- [Identity & Non-Human Identity for Agentic AI (Part 1)](../34-identity-mcp-a2a-security-blueprint.md)
- [Identity/MCP/A2A Security Blueprint: MCP Security (Part 2)](34-identity-mcp-a2a-security-blueprint-part2.md)
- [Multi-Agent Security](../15-multi-agent-security.md)
