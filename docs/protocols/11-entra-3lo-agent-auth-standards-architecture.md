---
title: "EntraID 3LO: AC Gateway + AC Identity — Volume 1"
doc_type: reference-architecture
domain: protocols
topic_id: entra-3lo-agent-auth-standards-architecture
status: current
date_created: 2026-07-09
last_reviewed: 2026-07-10
supersedes:
  - docs/ai-protocols/auth/entra-3lo-agent-auth-standards-architecture.md
  - docs/ai-protocols/auth/EntraID_3LO_Agent_Auth_Research.pdf
source_type: native-md
tags: [ai-protocols, auth, reference-architecture]
---

# EntraID 3LO: AC Gateway + AC Identity — Volume 1

User-Delegated Auth for AI Agents · Standards, Architecture &amp; Industry Analysis

*GENAI Agent Foundry · June 2026*

| | |
| --- | --- |
| **Scope** | 3-Legged OAuth enabling agents to act on behalf of users |
| **Consumers** | M365 (Graph API), GitHub Enterprise (GHE), Atlassian (Jira/Confluence) |
| **Compiled** | June 2026 |

---

## Architecture Diagram

```mermaid
graph LR
    subgraph "Client & Auth"
        UA["User Agent<br/>or App"]
        AuthSvr["Authorization<br/>Server<br/>Entra ID"]
    end
    
    subgraph "Agent Identity Layer"
        Blueprint["Blueprint<br/>FIC + MSI"]
        AgentID["Agent Identity<br/>SP Instance"]
    end
    
    subgraph "Gateway & Vault"
        Gateway["AC Gateway<br/>PDP + PEP"]
        Vault["Token Vault<br/>AES-256-GCM"]
    end
    
    subgraph "Resources"
        Graph["Graph API<br/>M365"]
        Jira["Atlassian<br/>Jira/Confluence"]
        GHE["GitHub<br/>Enterprise"]
    end
    
    UA -->|Auth Code + PKCE| AuthSvr
    AuthSvr -->|access_token<br/>refresh_token| Blueprint
    Blueprint -->|FIC/MSI| Blueprint
    Blueprint -->|OBO Exchange| AgentID
    AgentID -->|Delegated Token| Gateway
    Gateway -->|Lookup & Refresh| Vault
    Gateway -->|Bearer Token| Graph
    Gateway -->|Bearer Token| Jira
    Gateway -->|Bearer Token| GHE
```

---

## 1. Background &amp; Problem Statement

### 1.1 Why User-Delegated Auth Matters for AI Agents

Traditional OAuth assumes an interactive human session: a redirect, a consent screen, and a short-lived browser session. AI agents invert this model — they must act autonomously, after the user session ends, on behalf of users who explicitly consented. This creates a fundamentally different lifecycle requirement.

A simple "redirect and store the token" approach works in demos but fails under four production conditions:

1. Tokens expire while the agent is mid-task
2. Background refresh races cause 401 cascades
3. Multi-user/multi-tenant systems cannot share tokens
4. Enterprise security reviews reject service accounts with broad static credentials

### 1.2 The Three Identity Questions Agents Must Answer

| Question | Traditional Answer | Agent-Specific Answer |
| --- | --- | --- |
| Who is acting? | The authenticated user | The agent acting FOR the user (dual identity) |
| What can they do? | User's role/permission set | Intersection of user permissions AND agent-granted scopes |
| For how long? | Browser session lifetime | Until task complete or token revoked — even days later |

---

## 2. Standards &amp; Theoretical Foundation

### 2.1 Core RFCs

| RFC / Spec | What It Defines | Agent Relevance |
| --- | --- | --- |
| RFC 6749 | OAuth 2.0 — Auth Code Grant (3LO), Client Credentials (2LO) | Foundation for all agent auth flows |
| RFC 7636 PKCE | Proof Key for Code Exchange — binds code to verifier | Mandatory for public clients; prevents code injection |
| RFC 8693 | Token Exchange — OBO flow: swap user token for agent-scoped token | Core mechanism for agent acting on behalf of user |
| RFC 8707 | Resource Indicators — bind token to specific resource server | Prevents token audience confusion in multi-API environments |
| OAuth 2.1 | Consolidates 2.0 + BCP; mandates PKCE; removes implicit/password grant | MCP spec mandates OAuth 2.1 for all HTTP transports |
| IETF Draft OBO-AI | Extends Auth Code flow: `requested_actor` + `actor_token` params | Emerging standard; agent named on consent screen |
| MCP 2025-11-05 | Model Context Protocol mandates OAuth 2.1 + PKCE for remote servers | All MCP-based tool calls require compliant auth |

### 2.2 The 3LO Authorization Code Flow — Step by Step

The 3-Legged OAuth flow involves three parties: the Client (the AI agent/app), the Authorization Server (Entra ID / Atlassian auth), and the Resource Owner (the user). Unlike 2LO (machine-to-machine), 3LO requires explicit user consent before any token is issued.

| Step | Actor | Action / Token |
| --- | --- | --- |
| 1 | Agent/App | Redirect user to `/authorize?client_id=…&scope=…&code_challenge=PKCE_HASH&state=CSRF_TOKEN` |
| 2 | Auth Server | Display consent screen showing what the agent will access on user's behalf |
| 3 | User | Grant (or deny) access; Auth Server issues short-lived `authorization_code` |
| 4 | Agent/App | POST to `/token`: exchange code + `code_verifier` for `access_token` + `refresh_token` |
| 5 | Agent | Call resource API (Graph, Jira, GHE) with Bearer `access_token` |
| 6 | Agent (background) | Proactively refresh at 80% TTL; rotate `refresh_token`; store securely |
| 7 | On revoke/task end | Invalidate `refresh_token`; remove from credential vault |

### 2.3 On-Behalf-Of (OBO) — Token Exchange for Agent Chains

RFC 8693 Token Exchange is the mechanism where an agent receives a user token (Tc) from the calling client application, then exchanges it for a resource-scoped token at the target API. This creates a clear delegation chain without embedding user credentials in the agent.

```http
POST /oauth2/v2.0/token
grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
assertion={user_access_token_Tc}
client_assertion={agent_identity_token_T1}   # FIC/MSI preferred
requested_token_use=on_behalf_of
scope=https://graph.microsoft.com/Mail.Read
```

:::warning Key Constraint
    The output token is bounded by the intersection of (user permissions) AND (agent-granted scopes). The agent **cannot escalate** beyond what the user already has.

---

## 3. Microsoft Entra Agent ID — Architecture

### 3.1 The Three-Tier Agent Identity Model

Microsoft Entra Agent ID introduces a purpose-built identity model that separates identity definition from identity instances:

| Tier | Object | Purpose |
| --- | --- | --- |
| 1 — Blueprint | Agent Identity Blueprint (App Registration) | Template defining agent type, permissions, credential type. Admin sets Conditional Access here. One blueprint → many instances. |
| 2 — Identity | Agent Identity (Service Principal child) | Per-deployment instance. Holds scoped permissions. Can impersonate Agent User. Token exchange uses FIC → MSI chain. |
| 3 — User | Agent User Account (optional) | Synthetic user principal for agents that need a mailbox, calendar, or full user-scoped Graph access. |

### 3.2 Token Chain for Interactive (OBO) Agent Flow

The token chain follows a strict three-step sequence:

```
Step 1: Blueprint acquires T1
  POST /oauth2/v2.0/token
    client_id=AgentBlueprint
    grant_type=client_credentials
    client_assertion=TUAMI   # Managed Identity token
    scope=api://AzureADTokenExchange/.default

Step 2: Agent Identity performs OBO exchange using T1 + Tc
  POST /oauth2/v2.0/token
    client_id=AgentIdentity
    grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
    assertion={Tc}              # User token received from client app
    client_assertion={T1}       # Blueprint token
    requested_token_use=on_behalf_of
    scope=https://graph.microsoft.com/Mail.Read

Step 3: Agent calls resource API with resulting delegated token
```

:::warning Production Credential Rule
    Client secrets **MUST NOT** be used in production. Use Federated Identity Credentials (FIC) with Managed Identity (MSI) as the credential for Agent Identity Blueprints.

### 3.3 Supported Grant Types for Agent Entities

| Grant Type | Supported By | Use Case |
| --- | --- | --- |
| `client_credentials` | Blueprint + Identity | Bootstrap token for FIC chain; autonomous app-only operations |
| `jwt-bearer` (OBO) | Blueprint + Identity | User-delegated access; agent acts on behalf of signed-in user |
| `refresh_token` | Agent Identity | Background long-running tasks; maintain user context across sessions |
| `user_fic` | Agent Identity | Agent's user account impersonation (mailbox, calendar scenarios) |

:::warning No Interactive Flows for Agents
    Interactive `/authorize` flows are **EXPLICITLY BLOCKED** for agent entities. Redirect URIs are not supported. All auth occurs programmatically via token exchange.

### 3.4 Microsoft Entra Agent ID — Governance Capabilities

| Capability | Mechanism | Benefit |
| --- | --- | --- |
| Conditional Access | Apply CA policies to Blueprint → all instances inherit | Enforce MFA, location, risk-based controls on agents |
| Access Packages | Entitlement Management API assigns scoped permissions | Governed, time-bound access; auto-expiry with sponsor notification |
| Access Reviews | Periodic review of agent identity permissions | Compliance: verify agent still needs its access |
| Lifecycle Workflows | Automate sponsor handoff, expiry notifications | Human accountability chain for every agent |
| Identity Protection | Risk scoring, anomaly detection on agent tokens | Detect token abuse or compromised agent instances |
| Audit Logs | Full audit trail: agent ID + user OID + scope + timestamp | Forensics, regulatory compliance |

---

## 4. AC Gateway — Three-Plane Architecture

### 4.1 Why a Gateway Is Not Just a Proxy

Traditional API gateways sit in front of APIs, controlling inbound traffic. Agentic architectures are different — the agent itself mediates between user and infrastructure. The AC Gateway must therefore operate as a **policy enforcement point** at the execution layer. It owns three distinct planes:

| Plane | Responsibility | Key Mechanism |
| --- | --- | --- |
| Inbound Auth | Validate who is calling the agent | Verify Entra bearer token; extract user OID + agent identity |
| Access Control | What can this agent do for this user? | OPA/PDP policy: RBAC + ABAC + approval thresholds |
| Outbound Auth | Credential to call downstream API | Per-user credential vault; 3LO refresh token → access token; agent never sees raw credentials |

### 4.2 Token Lifecycle at the Gateway

| Event | Gateway Action |
| --- | --- |
| User first consent | Store `{access_token, expires_at, refresh_token, scopes, provider_metadata}` encrypted, keyed by `(user_id, provider)` |
| Agent makes tool call | Lookup credential vault; if `access_token` valid → inject; if expiring → refresh first |
| Token near expiry (80%) | Background proactive refresh; acquire per-(user,provider) distributed lock to avoid race conditions |
| Refresh + rotate atomically | New `access_token` + new `refresh_token` written; old `refresh_token` invalidated immediately |
| User revokes access | Delete vault entry; agent blocked from further calls for that user+provider |
| Agent task completes | Optionally revoke `refresh_token`; agent should not retain delegation between unrelated tasks |

### 4.3 2LO vs 3LO Decision Framework

| Condition | Use 2LO (Client Credentials) | Use 3LO (Auth Code) |
| --- | --- | --- |
| Data ownership | Org-level / shared data (no user owner) | User's personal data (email, calendar, issues assigned to them) |
| Consent | Admin pre-consents once for all agents | Each user must explicitly consent (GDPR requirement) |
| Token subject | Application identity (agent) | User identity (delegated; user + agent named) |
| Examples | Internal analytics API, batch processors | Graph Mail, Jira issues, GHE repo access |
| AC Gateway config | Store app credential (FIC/cert) | Store per-user `refresh_token`; run consent redirect flow |

### 4.4 Production Runtime Flow (End-to-End)

| # | Stage | Detail |
| --- | --- | --- |
| 1 | User prompt | User: "Close ticket DEMO-123 in Jira" |
| 2 | Agent plan | LLM determines: call Jira API → update issue status |
| 3 | Gateway inbound | Validate user Entra bearer token; extract `user_oid` |
| 4 | PDP check | RBAC: does agent have `Jira:write` scope for this user? ABAC: within policy? Approval needed? |
| 5 | Vault lookup | Retrieve Jira `refresh_token` for `user_oid`; check if `access_token` valid |
| 6 | Token refresh | (If needed) POST to `auth.atlassian.com/oauth/token` with `refresh_token`; store rotated pair |
| 7 | Tool execution | Gateway (not agent) executes PATCH `api.atlassian.com/ex/jira/{cloudId}/rest/api/3/issue/DEMO-123` |
| 8 | Audit log | Record: `agent_id`, `user_oid`, `scope=write:jira-work`, `resource=DEMO-123`, result, timestamp |
| 9 | Response | Return result to agent; agent formats response to user |

---

## 5. Target Resource Integrations

### 5.1 Microsoft 365 — Graph API (Delegated Permissions)

Graph API is the primary target for M365 user-delegated access. The agent must use the OBO flow (Section 3.2) to exchange the user's Entra token for a Graph-scoped delegated token.

| Scope | Access Granted | Notes |
| --- | --- | --- |
| `Mail.Read` | Read user's email | Delegated; requires user consent |
| `Mail.Send` | Send email as user | High risk; consider CIBA approval gate |
| `Calendars.ReadWrite` | Read/write user calendar | Delegated |
| `Files.ReadWrite` | Read/write OneDrive files | Delegated |
| `User.Read` | Read signed-in user profile | Always needed; low risk |
| `.default` | All pre-consented admin scopes | **AVOID for 3LO** — use minimal explicit scopes |

:::note Best Practice
    Request only the scope needed for the current task. Use incremental consent to add scopes as needed.

### 5.2 GitHub Enterprise (GHE) — OAuth App / GitHub App

GHE supports both OAuth Apps (user-delegated 3LO) and GitHub Apps (installation-scoped 2LO). For agent access to user-owned repositories, OAuth App with 3LO is required.

| Aspect | Detail |
| --- | --- |
| Authorization URL | `https://{ghe-host}/login/oauth/authorize?client_id=…&scope=repo read:user` |
| Token URL | `https://{ghe-host}/login/oauth/access_token` |
| Scopes | `repo` (full repo access), `read:org`, `read:user`, `workflow` — use minimal set |
| Token type | GitHub does **not** issue refresh tokens for OAuth Apps; access tokens are long-lived (use with caution) |
| GitHub App alternative | Installation tokens (2LO) expire after 1hr; fine-grained permissions; recommended for server-to-server |
| Gateway config | Whitelist AgentCore/AC Gateway callback URL in GHE OAuth App settings |

### 5.3 Atlassian (Jira / Confluence) — 3LO Details

Atlassian's 3LO uses Auth Code Grant with rotating refresh tokens. All API calls must go through `api.atlassian.com` and include the `cloudId`.

```
Authorization URL:
  https://auth.atlassian.com/authorize
    ?client_id=YOUR_CLIENT_ID
    &scope=read:jira-work write:jira-work read:jira-user offline_access
    &redirect_uri=https://ac-gateway.org.internal/callback/atlassian
    &state={CSRF_TOKEN}
    &response_type=code
    &prompt=consent

Token Exchange:
  POST https://auth.atlassian.com/oauth/token
  { grant_type: authorization_code, client_id, client_secret, code, redirect_uri }

API Call:
  GET https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3/issue/DEMO-123
  Authorization: Bearer {access_token}
```

| Key Scope | Permission Granted |
| --- | --- |
| `read:jira-work` | Read issues, projects, workflows |
| `write:jira-work` | Create/update issues, transitions |
| `read:jira-user` | Read user profiles |
| `read:confluence-content.all` | Read Confluence pages and spaces |
| `write:confluence-content` | Create/update Confluence content |
| `offline_access` | **REQUIRED** to receive `refresh_token` for background agent operation |
| `manage:jira-configuration` | Admin config — **AVOID** unless explicitly needed |

:::note Atlassian Scope Behaviour
    User permissions always constrain the app. If a user lacks "Administer Jira", the agent cannot administer Jira even if the scope is granted. Least privilege is automatic.

    Rotating refresh tokens: each use issues a new `refresh_token`. The gateway must store the latest one atomically.

---

## 6. Industry: Who Has Productionised 3LO for AI Agents

| Organisation | Product / Pattern | Key Production Details | Status |
| --- | --- | --- | --- |
| AWS / Amazon Bedrock | AgentCore Identity | Full 3LO + 2LO. Secure token vault with KMS encryption. Per user+agent credential isolation. `@requires_access_token` decorator handles entire consent + refresh flow. Pre-built integrations: GitHub, Slack, Salesforce, Google Drive. | GA (Sept 2025) |
| Microsoft | Entra Agent ID + Microsoft.Identity.Web | Blueprint→Identity→OBO chain. FIC+MSI as preferred credential (no secrets). `services.AddAgentIdentities()` in .NET SDK. Conditional Access, Identity Protection, Access Reviews all extended to agents. | GA 2026 |
| Atlassian | 3LO for Forge/Connect apps | Rotating refresh tokens. `offline_access` scope for background agents. `cloudId`-based API routing. Account-level consent (per-user, per-site). | Production (long-standing) |
| TrueFoundry | MCP Gateway + Token Vault | Three-plane architecture (inbound/access/outbound). Per-(user,provider) distributed lock for refresh. Proactive refresh at 80% TTL. Atomic rotation of access+refresh tokens. | Production (May 2026) |
| WorkOS | Auth platform for AI agents | OAuth On-Behalf-Of flow (IETF draft). Front-channel consent with named agent on screen. `act` claim in resulting token names user + client + agent. | Production 2025–2026 |
| Aembit / SecureW2 | Workload Identity Federation | Eliminate static secrets entirely. Agent proves identity via SPIFFE/SPIRE workload identity. Conditional Access at network layer. Zero standing privileges. | Production (enterprise) |
| Auth0 / Okta | AI Agent auth with CIBA | CIBA for high-risk agent actions. Push notification to user device for explicit real-time consent before critical operations (e.g., transfer funds, send company-wide email). FGA for fine-grained tool authorisation. | Production 2025 |

**Key production patterns observed across all providers:**

- No client secrets in production — universally replaced by FIC + Managed Identity or certificates
- Sidecar/auth-proxy pattern — agent never handles credentials
- Proactive refresh at 80% TTL with distributed locking
- Atomic token rotation — new access+refresh written in single transaction
- Per-user credential isolation — tokens stored with `(user_id, provider)` key
- Revoke on task completion
- Full audit trail on every API call

---

## 7. Security, Zero Trust &amp; Threat Model

### 7.1 PKCE &amp; CSRF Binding (Mandatory for all 3LO flows)

PKCE (RFC 7636) prevents authorisation code injection by binding the auth request to a verifier that only the original client can produce. The `state` parameter prevents CSRF. Both are mandatory in OAuth 2.1.

```
# Client generates:
code_verifier = crypto.random(32)                        # 32-byte random
code_challenge = BASE64URL(SHA256(code_verifier))

# In /authorize request:
&code_challenge={code_challenge}&code_challenge_method=S256&state={session_bound_nonce}

# In /token request:
&code_verifier={code_verifier}
# Auth server verifies SHA256(verifier)==challenge
```

### 7.2 Threat Model &amp; Mitigations

| Threat | Attack Vector | Mitigation |
| --- | --- | --- |
| Token theft | Stolen `access_token` used by attacker | Short TTL (minutes). mTLS binding. Monitor for concurrent use from different IPs. |
| Refresh token theft | Stolen `refresh_token` used to mint new access tokens | Refresh token rotation: stolen token triggers detection (legitimate client fails next refresh). |
| Prompt injection → token misuse | Malicious input tricks agent into using tokens for unintended actions | PDP policy check at gateway; action is independent of LLM output. Zero trust: LLM not trusted for auth decisions. |
| Service account abuse | Agent holds global static credential; any injection = full access | 3LO with per-user scoped tokens. Never use service accounts for user-data agents. |
| Token audience confusion | Token for gateway reused against backend APIs | RFC 8707 Resource Indicators: bind token to specific resource URI. MCP spec requires this. |
| Excessive scope creep | Agent accumulates more access than needed over time | Access Reviews (Entra). Time-bound Access Packages. Request only scope needed for current task. |
| Dynamic Client Reg abuse | Malicious agent self-registers with broad scopes | Validate client metadata and redirect URIs strictly. Require pre-approval for new agent registrations. |
| Compromised agent instance | One agent instance with valid token attacks others | FIC + MSI credential bound to specific agent identity. No shared secrets between instances. mTLS/SPIFFE. |

### 7.3 CIBA — Human-in-the-Loop for High-Risk Actions

Client-Initiated Backchannel Authentication (CIBA) is an OAuth 2.0 extension for decoupled, asynchronous user approval for irreversible or high-risk actions.

| Step | Action |
| --- | --- |
| 1 | Agent identifies high-risk action (e.g., "send email to all-company list", "delete Jira project") |
| 2 | Agent sends CIBA authorisation request to Auth Server |
| 3 | Auth Server sends push notification to user's mobile device |
| 4 | User approves or denies on device |
| 5 | Agent polls token endpoint; receives approval token or rejection |
| 6 | Agent proceeds (or aborts) based on user decision |

:::warning CIBA Requirement
    Actions like sending bulk emails, deleting resources, or financial transfers should **ALWAYS** route through CIBA. Design the agent's tool catalog with explicit risk tiers.

---

## 8. Dependencies, Blockers &amp; Delivery Plan

### 8.1 Phased Delivery Roadmap

| Phase | Milestone | Key Activities |
| --- | --- | --- |
| **Phase 0** (Unblocked now) | Alignment &amp; Design | 1. Document 3LO pattern. 2. Security/Identity meeting: agree consent flow model. 3. Register OAuth apps in Atlassian &amp; GHE dev consoles. 4. Define agent identity blueprint in Entra dev tenant. |
| **Phase 1** (After gateway whitelist) | AC Gateway + AC Identity online | 1. AC Gateway live with 3-plane architecture. 2. AC Identity whitelisted. 3. Implement credential vault (per-user, per-provider, AES-256 encrypted). 4. Implement proactive refresh with distributed locking. |
| **Phase 2** (Reference impl) | End-to-End Working Flow | 1. Reference impl: agent calls Jira/GHE/Graph via OBO chain. 2. Consent flow: user redirect → approval → `refresh_token` stored in vault. 3. Audit logging: `agent_id` + `user_oid` + scope + resource + timestamp. |
| **Phase 3** (Hardening) | Production Readiness | 1. No client secrets anywhere: FIC + MSI for all blueprints. 2. Conditional Access policies on all agent blueprints. 3. CIBA gate for high-risk tool actions. 4. OWASP Agentic Top 10 review. |

### 8.2 Minimal Delivery Checklist

| # | Deliverable | Acceptance Criteria |
| --- | --- | --- |
| MD-1 | EntraID 3LO pattern documented for ≥1 scope | Living document covering flow, token chain, scope selection, and gateway config for at least one of: M365 / GHE / Atlassian. |
| MD-2 | Security/Identity team alignment on consent flow | Agreed consent UX pattern; defined which agent types require user consent vs admin pre-consent; CIBA policy for high-risk actions. |
| MD-3 | Reference implementation for user-delegated token flows | Working code (e.g., using `Microsoft.Identity.Web` + `AddAgentIdentities()`) demonstrating OBO chain: Blueprint → Identity → Resource API with FIC/MSI credentials. |

---

## 9. Open Questions &amp; Industry Gaps

| # | Open Question / Gap | Current State | Recommended Action |
| --- | --- | --- | --- |
| OQ-1 | IETF `draft-oauth-ai-agents-on-behalf-of`: timing for adoption? | Draft -02 (Aug 2025). Not yet adopted by OAuth WG. | Track IETF OAuth WG. Design consent screen to show agent name now (can retrofit draft params later). |
| OQ-2 | GitHub Enterprise: no refresh token for OAuth Apps — how to handle long-running agent tasks? | GHE OAuth App access tokens are long-lived (no expiry by default) — security risk. | Prefer GitHub App (installation token, 1hr TTL, fine-grained) for server-side agents. |
| OQ-3 | Atlassian consent: user must repeat per-site. How to handle multi-site agents? | Current Atlassian 3LO is per-site. Admin cannot revoke individual user grants; must uninstall app. | Document limitation. Design agent to request per-site consent lazily (just-in-time). |
| OQ-4 | CIBA: which tools in the agent catalog are "high risk"? | Not yet defined. | Security/Product alignment session. Define risk tiers: read / write / destructive / financial. |
| OQ-5 | Multi-agent pipelines: how does trust chain propagate across agent hops? | RFC 8693 reduces authority at each hop (never amplifies). But audit chain across agents is not standardised. | Implement `correlation_id` + `delegation_chain` claim in internal tokens. Log each hop. |
| OQ-6 | FT/Entra self-service: what is the approval process for registering new agent OAuth apps? | Currently manual, requires Security engagement. | Define and publish SLA: Security reviews new app registration within N days. |

---

## Executive Summary

The EntraID 3LO pattern for AI agents is well-understood, standardised, and production-proven by AWS Bedrock AgentCore, Microsoft Entra Agent ID, Atlassian, and multiple enterprise platform teams. The core pattern is:

**Agent Identity Blueprint → FIC/MSI credential → OBO token exchange → per-user scoped access token → resource API call → audit log**

**The three non-negotiable production requirements:**

1. **No client secrets** — use FIC+MSI
2. **Per-user token isolation** — never share tokens across users
3. **Full audit trail** — every agent API call must be traceable to a specific agent, user, scope, and timestamp
