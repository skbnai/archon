---
title: "Identity & Non-Human Identity for Agentic AI"
doc_type: guide
domain: trust
status: current
topic_id: identity-mcp-a2a-security-blueprint
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/02-Identity-MCP-A2A-Security-Blueprint.md]
tags: [ai-security, identity, spiffe, non-human-identity, agentic-ai]
covers_version: "as of 2026"
---

Human identity foundations for agent platforms, the SPIFFE/SPIRE non-human identity substrate, the compound-identity problem, and the emerging decentralized-trust layer for cross-organization agents.

## Identity Is the Unsolved Foundation

If this entire body of agentic security research were reduced to one finding, it would be this: identity is the unsolved foundation underneath every other agentic security control, and the industry knows it. Organizations have largely solved authentication ("who is this agent") through static API keys and shared service accounts — functional but insecure — while authorization ("what is this agent allowed to do, and for how long") remains almost entirely unaddressed at most enterprises. Agents routinely hold standing access to resources they need for a single task, and that access persists indefinitely after the task completes.

Identity, MCP security, and A2A security are a single connected problem, because they are. MCP is how an agent identifies itself to a tool; A2A is how an agent identifies itself to a peer agent; both ultimately rest on the same workload-identity substrate. An enterprise that solves agent identity once, well, and centrally gets MCP and A2A authentication largely for free. An enterprise that solves them separately ends up with three incompatible trust models and the operational fragility that comes with reconciling them.

**Where the standards landscape actually stands.** NIST's AI Agent Standards Initiative launched February 2026 and remains in its listening-session phase; there is no ratified federal standard for agent identity yet. The IETF draft AIMS (Agent Identity Management System), published March 2026 by engineers from AWS, Zscaler, Ping Identity, and Defakto, does not invent new protocols — it maps SPIFFE (workload identity), WIMSE (workload-to-workload authentication, an active IETF working group), and OAuth 2.0 (delegated authorization) onto a layered stack purpose-built for agents. This is the most credible converging architecture in the market. Treat anything claiming to be a finished, ratified "agent identity standard" with skepticism — the field is converging, not converged.

## Human Identity Foundations

Human identity for agentic platforms does not require new protocols, but it does require extending existing ones to a new use case: the human-in-the-loop approval step. OAuth 2.0 and OIDC remain the backbone for human authentication into agent platforms and consoles; SAML persists in regulated and legacy enterprise environments for federation; passkeys, FIDO2, and WebAuthn are increasingly the required second factor for high-risk human approval actions (approving an agent's irreversible action, elevating an agent's autonomy level, onboarding a new agent identity) because phishable credentials are an unacceptable weak link at the one point in the system where a human is supposed to be the final check.

The major identity platforms — Microsoft Entra ID, Okta, Ping Identity, and ForgeRock — have all published agent-specific extensions to their human IAM product lines rather than treating agent identity as a separate product line, which is the architecturally correct direction: it keeps human and non-human identity in one governable system rather than creating a second, unmanaged identity plane.

| Platform | Agent Identity Positioning |
|---|---|
| Microsoft Entra ID | Entra Agent ID extends the existing Entra ID tenant model to agents, issuing first-class identities with conditional access, PIM-style just-in-time elevation, and lifecycle management inside Entra; tightly coupled to Copilot Studio and the Agent 365 control plane |
| Okta | Okta for AI Agents extends Okta's workforce identity platform with agent-specific provisioning (including a SCIM extension for provisioning agent identities alongside human ones) and delegated-access flows |
| Ping Identity | Positioned around PingOne for Workforce, extended with verifiable-credential and decentralized-identity capabilities aimed at agent-to-agent and agent-to-service trust |
| ForgeRock (part of Ping) | Consolidated under the Ping Identity portfolio post-acquisition; legacy ForgeRock deployments are being migrated toward the unified Ping agent identity roadmap |

## Non-Human Identity: The SPIFFE/SPIRE Substrate

SPIFFE (Secure Production Identity Framework For Everyone) has become the de facto standard for non-human workload identity, and its adoption curve for AI agents specifically is the steepest part of that trend. The reason is structural: agents share every difficult property of the workload types SPIFFE was designed for — they are ephemeral (many exist for the duration of a single task), non-deterministic (the same input can produce different actions across runs), high blast-radius (a single agent may touch internal APIs, databases, and external services in one session), and they proliferate faster than any manual identity-provisioning process can track (a single employee may "own" dozens of agents acting on their behalf).

SPIRE, the CNCF reference implementation of the SPIFFE specification, issues short-lived X.509 SVIDs (SPIFFE Verifiable Identity Documents) or JWT-SVIDs to workloads after performing attestation — verifying properties of the requesting process (its Kubernetes service account, its container image digest, its cloud instance metadata, its Unix UID) against registered selectors before issuing credentials. Two SPIFFE-identified peers then establish mutual TLS directly, without a shared secret or human-mediated enrollment. This is precisely the property agents need: an agent spun up by an orchestrator a moment ago can prove who it is without anyone having manually registered it in advance.

**Critical limitation to architect around:** SPIFFE authenticates the workload, not its intent. An SVID proves "this is the legitimate agent process running this container image" — it provides no guarantee whatsoever about what that process will do next. SPIFFE is necessary infrastructure, not a complete authorization solution; it must be paired with the policy and behavioral layers described in the rest of this series.

Production validation of this pattern exists at real scale: Block (formerly Square) runs a full SPIFFE plus WIMSE plus OAuth stack in production and is the most frequently cited real-world reference for the architecture this guide recommends. HashiCorp Vault Enterprise added native SPIFFE authentication specifically to handle non-human identities including AI agents, allowing an agent holding an SVID to exchange it directly for a Vault-managed secret without a separate enrollment step. Uber's SPIFFE deployment processes billions of attestations daily, demonstrating the pattern scales to hyperscale agent populations.

| NHI Mechanism | What It Establishes | Typical Use in Agent Architectures |
|---|---|---|
| SPIFFE / SPIRE | Cryptographic workload identity ("what process is this") | Base identity layer for every agent runtime, MCP server, and A2A endpoint |
| Workload Identity Federation (cloud-native) | Federation of cloud IAM identity to workloads without static credentials | Agent-to-cloud-API authentication (replacing long-lived service account keys) |
| Managed Identity (Azure) | Azure-native equivalent of workload identity for resources running in Azure | Agents hosted on Azure compute calling Azure-native services |
| AWS IAM Roles + STS | Temporary, scoped credentials issued via role assumption | Agents hosted on AWS compute requiring temporary AWS API access |
| Kubernetes Workload Identity (Service Account Token Projection) | Kubernetes-native identity for pods, often federated outward via SPIFFE or cloud workload identity | Agent runtimes deployed as Kubernetes workloads |

## Agent Identity: The Compound Identity Problem

The hardest open problem in this domain is not workload identity — SPIFFE solves that reasonably well — it is compound identity: most consequential agent actions are taken on behalf of a human or another system, and the authorization decision needs to account for both the agent's own identity and the principal it is acting for. An agent with a valid SPIFFE SVID that is, in this moment, acting on behalf of a suspended user account should not be able to complete the action — but a workload-identity check alone cannot know that.

| Mechanism | What It Solves | Where It Falls Short for Agents |
|---|---|---|
| Service Accounts | Simple, broadly supported non-human authentication | Static, long-lived, ambient authority; no delegation chain — the pattern current research explicitly flags as the insecure-but-functional status quo |
| Delegated Identity / OAuth On-Behalf-Of | Carries forward a human principal's authorization through a chain of services | Designed for relatively shallow, predictable delegation chains; multi-hop agent-to-agent delegation strains the model |
| RFC 8693 Token Exchange | Standardized mechanism to exchange one token for another, including for delegation and impersonation | Increasingly the recommended mechanism for agent-acts-for-user flows, but adoption in agent platforms is still early |
| Federated Identity | Cross-domain trust without shared credential stores | Federation trust agreements were designed for human SSO cadence, not for agents dynamically discovering and trusting new counterparties at runtime |
| Impersonation | Simple model where an agent simply assumes a user's full identity | Eliminates the audit distinction between "the user did this" and "the agent did this on the user's behalf" — actively harmful for accountability and should be avoided as an architectural pattern |

**Enterprise agent identity blueprint.** The architecture that combines these mechanisms into a coherent compound-identity model rather than choosing one runs in four layers: cryptographic workload identity (a SPIFFE SVID) establishes "this is the legitimate agent process," issued at agent instantiation and re-attested continuously, not just once at startup; user-plus-agent compound identity is carried as a structured claim (an `actor` claim in a JWT, following the RFC 8693 `act` pattern) so every downstream system can see both "which agent" and "on whose authority" in a single, non-repudiable token; ephemeral credentials are issued just-in-time for the specific task, scoped to the minimum required resources, and expire automatically — never a standing credential held in agent memory or configuration; and policy-driven authorization evaluates the compound identity (agent plus acting-for principal plus requested action plus resource sensitivity) against centrally managed policy at the moment of each tool call, not once at session start.

**Microsoft's framing of the shift.** Public commentary on agentic identity standards describes the change as fundamentally a mental-model shift: historically, non-human entities (OAuth clients, SPIFFE workloads, token-exchange actors) were kept in separate taxonomies precisely so the security properties of human-present and non-human transactions could be reasoned about separately. Agents collapse that separation — the same agent identity may need to act both autonomously and on a human's explicit behalf, sometimes within the same session — and the standards landscape (OAuth CIMD, the IETF WIMSE working group) is actively being extended to accommodate that collapse rather than maintaining the old separation.

## Future Identity: Decentralized Trust

Looking past 2026-2027, the identity layer is expected to extend toward verifiable, portable trust that does not depend on a single enterprise's identity provider — relevant once agents routinely interact with counterparty agents outside the enterprise boundary (supplier agents, payment-network agents, regulator-facing agents). Decentralized Identity (DID) provides self-sovereign identifiers not bound to a single registry or identity provider, allowing an agent's identity to be verified independent of which organization issued it. Verifiable Credentials are cryptographically signed claims about an agent (its capabilities, its compliance posture, its operator) that can be verified by any relying party without contacting the issuer in real time. Agent Credentials and Agent Cards are the A2A protocol's mechanism for an agent to advertise its capabilities and authentication requirements in a verifiable, signed format. Agent Trust Networks and Agent PKI are public-key infrastructure purpose-built for issuing and revoking agent certificates at the scale and velocity agent populations require — materially different from traditional enterprise PKI, designed for infrastructure that changes on the order of months, not minutes. And Agent Reputation Systems are behavioral trust scores, distinct from cryptographic identity, that quantify how reliably an agent has performed historically and feed into dynamic authorization decisions.

## Related

- [Identity/MCP/A2A Security Blueprint: MCP Security (Part 2)](parts/34-identity-mcp-a2a-security-blueprint-part2.md) — protocol internals, the MCP threat landscape, and the enterprise MCP gateway blueprint
- [Foundations & Reference Architecture](33-foundations-reference-architecture.md)
- [Identity for AI Agents](10-identity-for-ai-agents.md)
