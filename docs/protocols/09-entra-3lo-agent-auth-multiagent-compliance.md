---
title: "EntraID 3LO: AC Gateway + AC Identity — Volume 3"
doc_type: reference-architecture
domain: protocols
topic_id: entra-3lo-agent-auth-multiagent-compliance
status: current
date_created: 2026-07-09
last_reviewed: 2026-07-10
supersedes:
  - docs/ai-protocols/auth/entra-3lo-agent-auth-multiagent-compliance.md
  - docs/ai-protocols/auth/EntraID_3LO_Agent_Auth_Volume3.pdf
source_type: native-md
tags: [ai-protocols, auth, reference-architecture]
---

# EntraID 3LO: AC Gateway + AC Identity — Volume 3

Multi-Agent Chains, Regulatory Compliance (DORA/NIS2), Protocol Landscape &amp; Maturity Model

*GENAI Agent Foundry · June 2026*

Builds on: Volume 1 (Standards, Architecture, Industry) + Volume 2 (Code, Vault, Runbook, OWASP)

This volume covers: Multi-agent auth chains, MCP+A2A protocol stack, DORA/NIS2/EU AI Act compliance, three-lines-of-defence governance, forward-looking protocol horizon, maturity model.

---

## Multi-Agent Delegation Flow

```mermaid
graph TD
    subgraph "User Context"
        User["End User<br/>Full Consent Scope"]
    end
    
    subgraph "Hop 1: Orchestrator"
        Orch["Orchestrator Agent<br/>Request subset of scopes"]
    end
    
    subgraph "Hop 2: Sub-Agent"
        SubA["Sub-Agent (Jira)<br/>Request only needed scope"]
    end
    
    subgraph "Hop 3: Tool/API"
        Tool["Resource Server<br/>Enforce user permissions"]
    end
    
    User -->|Tc: full scope| Orch
    Orch -->|T_orch: read:jira-work| SubA
    SubA -->|T_sub: narrowed scope| Tool
    
    User -.->|audit trail| Log["Correlation Chain<br/>hop depth, act claim<br/>agent_id, user_oid"]
```

---

## 19. Multi-Agent Delegation Chains — The Hardest Problem

Single-agent 3LO is a solved problem. The harder frontier is **multi-hop delegation**: when an orchestrator agent spawns sub-agents, each of which may call tools or other agents. At each hop, three questions must be answered: (1) whose authority is this acting under? (2) how has scope been constrained at each hop? (3) is there an auditable chain?

### 19.1 The Delegation Chain Problem

OAuth's RFC 8693 was designed for pairwise exchange, not multi-hop agent chains. Three structural limitations emerge in production:

| Limitation | Description | Risk in GENAI Context |
| --- | --- | --- |
| No cross-domain trust | Each trust domain needs its own auth server. No mechanism for cross-domain token verification without pre-established federation. | Agents calling Atlassian + Graph + GHE in sequence each need separate token exchange — no shared trust fabric. |
| Opaque delegation history | Token exchange produces a new token with no cryptographic record of the original delegation chain. | Audit log cannot prove "Sub-Agent B acted because Orchestrator A was delegated by User X". Chain is asserted, not proven. |
| No holder-side attenuation | Only the auth server can narrow scopes. An intermediary agent cannot further constrain what it delegates. | If Orchestrator receives `write:jira-work`, it can delegate the full scope to Sub-Agent — even if Sub-Agent only needs `read`. |

### 19.2 The `act` Claim — What RFC 8693 Gives You Today

RFC 8693 token exchange supports the `act` claim in the resulting JWT, which carries actor identity. This is the minimum viable audit chain available today:

```json
{
  "sub": "user@org.example",           // The user on whose behalf we act
  "oid": "a3b4c5d6-...",               // User object ID
  "act": {                              // RFC 8693 actor claim
    "sub": "agent-identity-sp-id",     // Which Agent Identity is acting
    "act": {                            // Nested: who delegated to this agent
      "sub": "orchestrator-agent-id"
    }
  },
  "scp": "read:jira-work",             // Scope — MUST be intersection, never union
  "aud": "api.atlassian.com",          // RFC 8707: bound to specific resource
  "exp": 1750000000,
  "iat": 1749996400
}
// The act chain: token is for user, via orchestrator, via agent-identity
// Each hop MUST exchange for a narrower or equal scope — never broader
// Log the full JWT payload (minus sensitive fields) for audit
```

:::warning RFC 8693 Attack Vector
    A compromised intermediary can present a valid `subject_token` and a valid `actor_token` from **different** delegation contexts. The auth server cannot detect this without cryptographic binding. Mitigation: short token TTL + audience binding (RFC 8707) + `correlation_id` logged at every hop.

### 19.3 Practical Multi-Agent Pattern — Scope Attenuation Ladder

Until the IETF OAuth WG formalises cryptographic chain binding, the pragmatic production pattern is the **scope attenuation ladder**:

| Hop | Actor | Token Received | Exchange To | Scope Rule |
| --- | --- | --- | --- | --- |
| 0 — User | Human user signs in | User token Tc (full delegated scope) | Passes Tc to Orchestrator | User's full consent scope |
| 1 — Orchestrator | Orchestrator Agent Identity | Receives Tc; exchanges via OBO to T_orch | Passes T_orch to Sub-Agent or Tool | Request ONLY what current task needs — not full Tc scope |
| 2 — Sub-Agent | Sub-Agent Agent Identity | Receives T_orch; exchanges via OBO to T_sub | Passes T_sub to Tool/API | Further narrow: only scope for this specific tool call |
| 3 — Tool/API | Resource server (Jira, Graph) | Receives T_sub; validates audience + scope | Executes API call | User permissions always constrain regardless of scope on token |

:::warning Mandatory Rule
    Scope attenuation is a MUST at each hop. Never pass an orchestrator's full scope to a sub-agent. Each exchange should request only what is needed for the immediate task. This is the primary defence against excessive agency in multi-agent pipelines.

### 19.4 Correlation &amp; Audit Across Agent Hops

```python
# Every agent call must carry and propagate correlation metadata
# In HTTP headers (add to all inter-agent calls):
X-Correlation-ID: {uuid4}             # Generated at user request entry; propagated unchanged
X-Agent-Chain: orchestrator-v2,sub-agent-jira-v1   # Append each agent name
X-Delegation-Depth: 2                  # Hop count (enforce max depth = 3 in gateway policy)
X-User-OID: a3b4c5d6-...              # Original user OID — never allow agent to override

# Audit log entry at each hop (structured JSON):
{
  "correlation_id": "cf3a...",
  "agent_id": "sub-agent-jira-v1",
  "user_oid": "a3b4c5d6-...",
  "delegated_by": "orchestrator-v2",
  "action": "PATCH",
  "resource": "jira/DEMO-123/status",
  "scope_used": "write:jira-work",
  "hop_depth": 2,
  "token_exp": 1749999600,
  "timestamp": "2026-06-28T10:15:00Z",
  "result": 200
}
# This enables the CISO query: 'Show everything agent-chain X did on behalf of user Y'
# Also required for DORA ICT incident reporting
```

### 19.5 Maximum Delegation Depth Policy

| Policy | Recommended Value | Rationale |
| --- | --- | --- |
| Max delegation depth | 3 hops (user → orchestrator → sub-agent → tool) | Beyond 3, audit chain is practically unverifiable; attack surface grows exponentially |
| Min scope at each hop | Only the scope required for the immediate tool call | Principle of least privilege; prevents sub-agents inheriting orchestrator's full authority |
| Token TTL reduction | Each hop halves the remaining TTL | Limits blast radius if a mid-chain token is compromised; ensures chain expires |
| Max concurrent chains | Policy-defined per agent blueprint | Prevent agent spawning unbounded sub-agent trees; enforce in AC Gateway |
| Correlation ID required | Mandatory — reject calls without it | Without it, audit reconstruction across hops is impossible |

---

## 20. The 2026 Agent Protocol Stack: MCP + A2A + Streamable HTTP

The ecosystem has converged on a three-layer protocol stack for production agent systems:

| Layer | Protocol | Governs | Auth Mechanism | Status (June 2026) |
| --- | --- | --- | --- | --- |
| Tool access | MCP (Model Context Protocol) | How agent calls tools, reads data, invokes prompts | OAuth 2.1 + PKCE mandatory for remote HTTP servers; Dynamic Client Registration | Production; 2025-11-05 spec; mandated by ChatGPT (Sept 2025), Claude, Copilot |
| Agent coordination | A2A (Agent-to-Agent) | How agents delegate tasks to other agents; capability discovery via Agent Cards | RFC 8693 token exchange; OAuth 2.0 M2M per agent identity | v1.0 released April 2026; 150+ orgs including AWS, Microsoft, Salesforce, SAP |
| Transport | Streamable HTTP (MCP 2025-03-26 spec) | Bidirectional streaming between agent and tool server | Bearer token in Authorization header; token bound to session via RFC 8707 | Replaced SSE as primary MCP transport; production in all major frameworks |
| Identity layer | IETF drafts: AIMS, WIMSE, Agentic JWT, SCIM for agents | Cryptographic agent identity, cross-domain trust, agent lifecycle | Emerging: AIP proposes Invocation-Bound Capability Tokens | Draft stage; no single standard adopted yet |

### 20.1 How MCP Auth Works (2025-11-05 Spec)

The MCP specification mandates OAuth 2.1 for all remote (HTTP) MCP servers:

| Step | Actor | Action |
| --- | --- | --- |
| 1 | MCP Client (Agent) | Contacts MCP server without auth |
| 2 | MCP Server | Returns 401 + Protected Resource Metadata (RFC 9728) pointing to authorisation server |
| 3 | MCP Client | Fetches auth server metadata; performs Dynamic Client Registration if needed |
| 4 | MCP Client | Runs OAuth 2.1 Auth Code + PKCE (for user-delegated) or Client Credentials (for M2M) |
| 5 | Auth Server (Entra ID) | Issues access token bound to MCP server audience (RFC 8707 resource indicator) |
| 6 | MCP Client | Includes Bearer token in all subsequent calls to MCP server |
| 7 | MCP Server | Validates token: signature, expiry, audience == this server's URI |

:::note MCP 2025-11-05 Additions
    Mandatory PKCE for all clients, Client ID Metadata Documents (CIMD) as preferred registration method, step-up authorisation for incremental scope consent. All compatible with the 3LO pattern in this document.

### 20.2 How A2A Auth Works (v1.0)

A2A uses Agent Cards (JSON-LD documents) for capability discovery and OAuth M2M tokens for per-agent authentication:

```json
// Agent Card (published by Sub-Agent at /.well-known/agent.json)
{
  "name": "JiraSubAgent",
  "version": "1.2",
  "url": "https://jira-agent.genai.org.internal/a2a",
  "capabilities": ["jira:read", "jira:write"],
  "authentication": {
    "type": "oauth2",
    "tokenEndpoint": "https://login.microsoftonline.com/{tid}/oauth2/v2.0/token",
    "scopes": ["api://jira-sub-agent/.default"]
  },
  "identity": {
    "entraAgentIdentityId": "sub-agent-sp-object-id"
  }
}
```

```http
// Orchestrator calls Sub-Agent via A2A
POST https://jira-agent.genai.org.internal/a2a/tasks
Authorization: Bearer {T_sub_from_RFC8693_exchange}
X-Correlation-ID: {parent_correlation_id}
X-Delegation-Depth: 2

{
  "taskId": "task-uuid",
  "input": {"action": "update_status", "issue": "DEMO-123", "status": "Done"},
  "context": {"user_oid": "a3b4c5d6", "delegated_by": "orchestrator-v2"}
}
```

### 20.3 Protocol Choice Matrix for GENAI Agent Foundry

| Scenario | Protocol | Auth Pattern | AC Gateway Role |
| --- | --- | --- | --- |
| Agent calls Jira/Confluence REST API | Direct HTTPS (no MCP/A2A) | 3LO: per-user `refresh_token` in vault → `access_token` injected at gateway | Credential vault lookup + injection + audit log |
| Agent calls internal MCP tool server (e.g., Jira MCP) | MCP (Streamable HTTP) | OAuth 2.1 Bearer token; gateway proxies and re-signs with agent identity | Token validation inbound + outbound MCP auth header injection |
| Orchestrator delegates to Jira sub-agent | A2A v1.0 | RFC 8693 OBO exchange; scope attenuated at each hop; `act` chain in JWT | Enforce max delegation depth; validate `act` chain; propagate `correlation_id` |
| Agent acts autonomously (no user context, org-level task) | Direct HTTPS or MCP | 2LO: Client Credentials via Blueprint → Agent Identity `fmi_path` chain | App credential vault; no per-user token needed; audit with `agent_id` only |
| Agent triggers high-risk action across any protocol | CIBA (overlaid on any transport) | Suspend action; send backchannel approval request to user; resume on approve | CIBA decision endpoint; approval state machine; timeout/rejection handling |

---

## 21. Regulatory Compliance: DORA, NIS2 &amp; EU AI Act

AI agents that access ICT systems are within scope of DORA and NIS2. The 3LO + AC Gateway architecture directly satisfies several mandatory obligations.

### 21.1 DORA — Digital Operational Resilience Act (Reg. EU 2022/2554)

DORA became fully applicable 17 January 2025. In 2026, regulators have moved from reviewing paperwork to demanding real-time proof of control.

| DORA Pillar | Specific Requirement | How This Architecture Addresses It |
| --- | --- | --- |
| 1. ICT Risk Management | Art. 6-10: Identify, protect, detect, respond, recover. Log all ICT operations. | Every agent API call logged with `agent_id`, `user_oid`, scope, resource, result, timestamp. Entra Identity Protection detects anomalous token usage. |
| 2. ICT Incident Reporting | Art. 17-19: Classify, report to NCA within 24h (early warning), 72h (full report). | P0 incident playbook (Vol. 2 §15) maps to DORA classification. Correlation IDs allow reconstructing full impact scope for regulators. |
| 3. Digital Operational Resilience Testing | Art. 24-27: Annual TLPT for significant institutions. | Token vault, AC Gateway, and Entra Agent ID are in-scope ICT systems for TLPT. Include 3LO token theft scenarios, delegation chain splicing, and prompt injection in test plans. |
| 4. ICT Third-Party Risk | Art. 28-44: Register all ICT third-party providers. Assess concentration risk. | Entra ID (Microsoft), GitHub Enterprise, Atlassian, AWS are all ICT third parties. Must be in the Register of Information. Microsoft is a designated CTPP under DORA — EU oversight applies directly. |
| 5. Information Sharing | Art. 45: Voluntary sharing of cyber threat intelligence. | Agent token abuse patterns (unusual scope requests, unexpected countries, after-hours activity) are shareable threat indicators. |

### 21.2 NIS2 — Network and Information Security Directive

Banks are 'essential entities' under NIS2 Annex I Sector 4. DORA is lex specialis for ICT risk management, but NIS2 still applies for CSIRT reporting and supply chain security.

| NIS2 Article | Requirement | Architectural Control |
| --- | --- | --- |
| Art. 21 — Security measures | Access control, least privilege, MFA, encryption, audit logging | 3LO per-user scoped tokens (not shared accounts). FIC+MSI (no passwords). AES-256-GCM vault encryption. Full audit log. Conditional Access enforced at blueprint level. |
| Art. 21 — Supply chain security | Assess security of ICT suppliers and their practices | Atlassian, GitHub, Microsoft are ICT suppliers for agent-accessed data. Their 3LO implementations must be assessed: PKCE enforced? Refresh token rotation? Scope granularity? |
| Art. 22 — Incident reporting | Early warning within 24h of significant incident to national CSIRT | P0 playbook (§15.2) includes CSIRT notification step. Significant incident = agent accessing data it was not authorised to access, or credential vault breach. |
| Art. 21 — Continuity | Business continuity plans covering ICT systems | Token vault fallback: if vault unavailable, agents must gracefully degrade (not silently fail open). Circuit breaker: if Entra unavailable, agent queues tasks rather than proceeding without auth. |

### 21.3 EU AI Act — High-Risk System Considerations

The EU AI Act (applicable December 2027 for Annex III high-risk systems, deferred from August 2026 by the Digital Omnibus) intersects with DORA via Article 9(10). Agents that access user data and make decisions affecting customers may be classified as high-risk.

| EU AI Act Obligation | Applicability | Control Mapping |
| --- | --- | --- |
| Human oversight (Art. 14) | High-risk: agent makes decisions affecting users (credit, fraud, customer service actions) | CIBA gate for irreversible actions. Access Reviews for agent permissions. Human escalation path in agent workflow design. |
| Technical documentation (Art. 11) | High-risk: full lifecycle documentation required | Volume 1-4 document series. Architecture Decision Records. |
| Logging &amp; audit (Art. 12) | High-risk: logs must enable post-hoc reconstruction of AI decisions | Full delegation chain log (§19.4). User OID + `agent_id` + scope + resource + timestamp on every call. |
| Data governance (Art. 10) | Training data and input data quality | Scoped tokens limit what data agent can read. `read:jira-work` scope prevents agent from accessing financial core systems via the same identity. |
| Conformity assessment (Art. 43) | Third-party assessment for high-risk systems | Entra Agent ID, AC Gateway, and credential vault are in-scope for conformity assessment if agent system is classified high-risk. |

:::warning Practical Advice
    If agents are used for customer-facing decisions (fraud flagging, service actions), classify as high-risk early and design to EU AI Act Art. 14 (human oversight) from the start. Retrofitting human oversight into a production agent is significantly harder than designing it in.

---

## 22. Agent Identity Governance Model — Three Lines of Defence

DORA explicitly requires three independent lines of defence for ICT risk:

| Line | Role | Responsibilities for Agent Identity | Tools |
| --- | --- | --- | --- |
| Line 1 — Agent Owner / Builder | Business unit / team that builds and operates the agent | Define minimal scope set. Register OAuth apps with least-privilege scopes. Implement sidecar pattern. Configure CIBA gates for high-risk tools. Ensure `offline_access` only requested when background operation is needed. | Entra Agent ID portal, AC Gateway config, Atlassian/GHE dev console |
| Line 2 — Security / Identity Team | Independent risk function | Review all new agent identity registrations. Define consent flow standards. Set Conditional Access policies on blueprints. Monitor Entra Identity Protection alerts for agent identities. Perform quarterly access reviews. | Entra admin centre, Identity Protection, Access Reviews, Security SIEM |
| Line 3 — Internal Audit | Independent assurance | Annual audit: verify Line 1 controls work. Verify Line 2 independence. Sample audit log entries: confirm `agent_id` + `user_oid` + scope present on all entries. DORA TLPT coordination: confirm agents are in-scope for penetration testing. | Audit sampling tools, log analytics, TLPT coordination |

### 22.1 Agent Registry — Mandatory for Governance at Scale

Every deployed agent identity must be registered with the following mandatory fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `agent_id` | UUID (Entra Agent Identity SP object ID) | Primary key; used in all audit logs |
| `blueprint_id` | UUID (Entra Blueprint app registration ID) | Links instance to its policy template |
| `agent_name` | String | Human-readable; appears in consent screens and audit UIs |
| `owning_team` | Team/org identifier | Line 1 accountability; notified on Access Review |
| `security_sponsor` | Entra user UPN | Line 2 accountability; approves scope changes; DORA: designated responsible person |
| `provider_connections` | Enum[] | Which providers this agent can access: `atlassian`, `graph`, `ghe`, ... |
| `scopes_granted` | String[] | Explicit list of all delegated scopes; reviewed quarterly |
| `consent_model` | Enum | `admin_pre_consent` \| `user_3lo` \| `ciba_required` |
| `risk_tier` | Enum | `read_only` \| `standard` \| `high_risk` \| `critical` (triggers CIBA requirement) |
| `registered_at` | Timestamp | Creation date; dormant agents flagged after 90 days without use |
| `last_active` | Timestamp | Updated by vault on every credential access; drives dormancy detection |
| `dora_in_scope` | Boolean | Whether this agent is in scope for DORA incident reporting and TLPT |

### 22.2 Access Review Schedule

| Review Type | Frequency | Who Performs | Output |
| --- | --- | --- | --- |
| Quarterly scope review | Every 90 days | Security sponsor + owning team | Confirm each scope still needed; remove unused scopes; escalate if dormant |
| Annual full review | Yearly | Security team + Internal Audit | Full agent identity inventory; decommission unused; DORA evidence |
| Event-triggered review | On incident / personnel change | Security team | Immediate review of all agent identities owned by departing person; transfer or revoke |
| Pre-deployment review | Before every new agent goes live | Security team (Line 2 sign-off) | Scope approval; consent model approval; risk tier assignment; DORA scoping decision |

---

## 23. Forward-Looking: The 2027 Protocol Horizon

### 23.1 Emerging IETF Standards (2026 Drafts)

| Draft | What It Defines | Relevance | Likely Timeline |
| --- | --- | --- | --- |
| `draft-oauth-ai-agents-on-behalf-of-user` (-02, Aug 2025) | Extends Auth Code flow: `requested_actor` param names the agent on consent screen; `actor_token` authenticates agent at token endpoint | Directly relevant: users will see agent name on Atlassian/Graph consent screens. | Expected OAuth WG adoption 2026-2027 |
| `draft-mw-spice-actor-chain` | Cryptographically verifiable actor chains for OAuth 2.0 Token Exchange | Solves delegation chain splicing (§19.2). When ratified, replace `correlation_id` approach with cryptographic binding. | Draft stage; experimental implementations 2026 |
| `draft-ietf-oauth-identity-chaining` | OAuth identity and authorisation chaining across trust domains | Solves cross-domain agent calls. Relevant if GENAI agents need to federate across partner organisations. | Active WG discussion; 2027 target |
| WIMSE (Workload Identity in Multi-Service Environments) | Cross-service workload identity standard; agent as a workload identity type | Standardises how agent identity is asserted across cloud boundaries without cloud-provider-specific FIC mechanisms. | Draft 2026; production 2027 |
| SCIM for AI Agents (IETF 2026) | Agent lifecycle management: provisioning, deprovisioning, attribute management via SCIM | Will standardise the Agent Registry schema and automate agent deprovisioning via standard SCIM DELETE calls to Entra. | Early draft; watch for adoption |
| AIP: Agent Identity Protocol (arxiv 2603.24775) | Invocation-Bound Capability Tokens (IBCTs) — offline attenuable delegation with cryptographic provenance | Academic proposal addressing all 7 agent identity requirements that OAuth alone cannot satisfy. Not yet an IETF draft. | Research 2026; potential standardisation 2027+ |

### 23.2 Platform Roadmap Watch

| Platform | Expected Development | Impact on This Architecture |
| --- | --- | --- |
| Microsoft Entra Agent ID | Agent 365 admin centre (M365 admin view for all agents). GA of beta Graph APIs (`agentIdentities`). SCIM provisioning for agent identities. | Simplifies agent registry — Agent 365 may replace bespoke registry. GA APIs remove beta risk. |
| Atlassian | Admin-level revocation for 3LO grants (currently only per-user or app uninstall). Richer MCP server for Jira/Confluence. | Solves OQ-3 (admin cannot revoke per-user grant). MCP server removes need for direct REST token management. |
| GitHub Enterprise | Fine-grained PATs reaching enterprise admin controls. GitHub App improvements for org-level agent access. | Reduces reliance on OAuth App long-lived tokens. Fine-grained PATs solve the GHE refresh token gap. |
| MCP + A2A joint spec (Q3 2026 target) | AAIF-governed joint specification bridging MCP tool calls and A2A agent coordination at auth layer | Will likely define a unified token format for tool-call + agent-delegation. |

---

## 24. Agent Auth Maturity Model — Where Are You Now?

| Level | Name | Characteristics | Target for GENAI Foundry |
| --- | --- | --- | --- |
| 0 — Unsafe | Credential in agent | Static API keys or service account tokens embedded in agent code or env vars. No per-user isolation. No audit trail. Global blast radius. | NOT acceptable. Zero tolerance policy. |
| 1 — Authenticated | Agent has identity | Agent has its own Entra service principal. Uses client credentials (2LO). Tokens not in code — in Key Vault or env. Centralised logging. | Minimum for autonomous (non-user-data) agents |
| 2 — Delegated | User-delegated access (3LO) | 3LO consent flow implemented. Per-user `refresh_tokens` in encrypted vault. Proactive refresh. Rotating tokens. User can revoke. Scope minimised. | **Target for MD-1, MD-2, MD-3 (Minimal Delivery)** |
| 3 — Governed | Auditable + policy-enforced | FIC+MSI credential (no secrets). AC Gateway as PEP. OPA policy on every tool call. CIBA for high-risk actions. Full `act` chain in audit log. Access Reviews quarterly. Agent Registry. Three lines of defence operating. | **Target for Phase 2-3 production readiness** |
| 4 — Resilient | DORA/NIS2 compliant + tested | All Level 3 controls + DORA TLPT in scope for agents. CTPP concentration risk assessed. Automated incident reporting pipeline. EU AI Act conformity assessed. Chaos engineering: token vault outage → graceful degradation, not fail-open. | Target for Phase 3 + regulatory audit readiness |
| 5 — Adaptive | Cryptographically provable + federated | Invocation-Bound Capability Tokens (or equivalent). Cryptographic `act` chain. Cross-domain trust without pre-established federation. Automated SCIM lifecycle. Real-time risk-adaptive token issuance. | 2027+ horizon; watch IETF drafts |

---

## 25. Master Delivery Roadmap — All Volumes Synthesised

| Phase | Timeline | Maturity Target | Key Deliverables | Blockers / Dependencies |
| --- | --- | --- | --- | --- |
| Phase 0 — Unblocked now | Q3 2026 | Level 1 → 2 design | 1. This research (Volumes 1-3) published. 2. Security/Identity alignment session (MD-2). 3. Atlassian + GHE OAuth app registrations (dev tenant). 4. Entra Agent Identity Blueprint registered (dev tenant). 5. Agent Registry schema designed and approved. 6. Credential vault schema + encryption design approved. | None — all can proceed immediately |
| Phase 1 — After gateway whitelist | Q3-Q4 2026 | Level 2 — Delegated | 1. AC Gateway live with 3-plane architecture. 2. Credential vault deployed (encrypted, KMS-backed). 3. 3LO consent flow live (Atlassian + GHE). 4. OBO flow live (Graph API via sidecar). 5. Proactive refresh with distributed locking. 6. Full audit log: `agent_id` + `user_oid` + scope + resource + ts. 7. Reference implementation merged (MD-3). | AC Gateway whitelist; AC Identity whitelist; FT/Entra self-service Security approval |
| Phase 2 — Production hardening | Q4 2026 – Q1 2027 | Level 3 — Governed | 1. FIC+MSI credential on all blueprints (no client secrets). 2. OPA policy engine on AC Gateway (RBAC + ABAC). 3. CIBA gate live for high-risk tool actions. 4. Agent Registry live + integrated with Entra lifecycle. 5. Quarterly Access Reviews scheduled and running. 6. Multi-agent scope attenuation ladder implemented. 7. `correlation_id` propagated across all agent hops. 8. OWASP Agentic Top 10 review completed. | Phase 1 complete; OPA/policy engine decision; CIBA provider selection |
| Phase 3 — DORA readiness | Q1-Q2 2027 | Level 4 — Resilient | 1. Agents added to DORA Register of Information. 2. CTPP concentration risk documented. 3. TLPT scope includes agent identity + AC Gateway + token vault. 4. EU AI Act conformity assessment completed (if high-risk agents). 5. Automated incident reporting pipeline (P0/P1 → DORA notification). 6. Chaos tests: vault outage → graceful degradation (not fail-open). 7. MCP OAuth 2.1 adopted for all tool server connections. 8. A2A v1.0 adopted for orchestrator → sub-agent delegation. | Phase 2 complete; regulatory engagement timeline; MCP/A2A joint spec maturity |
| Phase 4 — 2027 horizon | Q3 2027+ | Level 5 — Adaptive | 1. IETF `draft-oauth-ai-agents-on-behalf-of-user` adopted → agent named on consent screen. 2. Cryptographic `act` chain (`draft-mw-spice-actor-chain`) deployed. 3. SCIM for agents → automated lifecycle provisioning. 4. Cross-domain A2A federation with external partners. 5. Risk-adaptive token issuance (shorter TTL on elevated risk score). | IETF drafts reaching RFC status; platform support (Entra, Atlassian, GHE); MCP+A2A joint spec release |

---

## Series Executive Summary — Volumes 1, 2 &amp; 3

The problem is real and urgent. AI agents acting on behalf of users across M365, Atlassian, and GHE need user-delegated auth that is auditable, least-privilege, and compliant with DORA. 93% of production agent projects use unscoped API keys. 79% of organisations have deployed agents; only 14% have full security approval. The gap is the opportunity this spec addresses.

The solution is standardised and production-proven. The EntraID 3LO pattern — Blueprint → FIC/MSI → Agent Identity → OBO token exchange → per-user scoped access — is in production at Microsoft, AWS, Auth0, TrueFoundry, and Atlassian. No new primitives are needed. What is needed is disciplined implementation.

**The three non-negotiables remain:**

1. **No client secrets** — FIC+MSI
2. **Per-user token isolation** with encrypted vault and proactive refresh
3. **Full audit trail**: `agent_id` + `user_oid` + scope + resource + timestamp on every call

Everything else — CIBA, multi-agent chains, MCP/A2A, DORA compliance — builds on these three.
