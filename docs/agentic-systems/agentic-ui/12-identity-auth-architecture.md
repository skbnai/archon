---
title: "Identity & Auth Architecture"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
doc_type: guide
domain: agentic-systems
topic_id: identity-auth-architecture
supersedes: ["docs/agentic-ui/identity-auth-architecture.md"]
source_type: native-md
tags: ["agentic-ui"]
covers_version: "as of 2026-07-10"
---


# Identity & Auth Architecture

Security Architects and Principal AI Architects will find here the authoritative reference for identity and authorization in agentic UI systems — covering agent identity models, OAuth 2.1 delegation chains, MCP authentication (RFC 9728 + RFC 8707), multi-tenant token isolation, and cross-agent (A2A) trust as of July 2026.

:::info Scope Boundary
    This page covers identity and auth architecture *specific to the agentic UI stack* — the AG-UI transport layer, agent runtime, MCP server connections, and A2A delegation. For the full Entra 3LO implementation guide (including OBO flow code, MSAL configuration, and Azure AD app registration), see [Entra 3LO Implementation Guide](../../protocols/index.md). For the OWASP ASI threat model and UI-level attack surfaces, see [Security Architecture](19-agentic-ui-security-architecture.md).

---

## 1. The Identity Problem in Agentic Systems

Traditional application identity is dyadic: a human user authenticates, and a service acts on behalf of that user. Agentic systems introduce a triadic or n-adic model: a human initiates a task, an orchestrator agent plans it, one or more sub-agents execute steps, and each step may call multiple tools against multiple backend systems. Each transition in this chain requires an explicit identity and authorization decision.

**Identity Chain in Agentic UI Interaction**

```mermaid
sequenceDiagram
    participant User as Human User
    participant IdP as Identity Provider
    participant Agent as Agent Orchestrator
    participant MCP_A as MCP Server A
    participant MCP_B as MCP Server B
    participant MCP_C as MCP Server C

    User->>IdP: Authenticate via OIDC
    IdP->>User: Issue user_access_token (id_token)
    User->>Agent: POST /agent/run with user_access_token
    Agent->>IdP: OBO token exchange (RFC 8693)
    IdP->>Agent: Issue scoped agent_token (user_oid + agent_id + tool_scope)
    
    Agent->>IdP: Request token for Tool A (RFC 8707 resource binding)
    IdP->>MCP_A: Issue token bound to MCP Server A only
    Agent->>MCP_A: POST /tools/call with resource-bound token
    MCP_A->>MCP_A: Validate: aud == MCP Server A
    
    Agent->>IdP: Request token for Tool B (RFC 8707 resource binding)
    IdP->>MCP_B: Issue token bound to MCP Server B only
    Agent->>MCP_B: POST /tools/call with resource-bound token
    MCP_B->>MCP_B: Validate: aud == MCP Server B
    
    Agent->>IdP: Request token for Tool C (RFC 8707 resource binding)
    IdP->>MCP_C: Issue token bound to MCP Server C only
    Agent->>MCP_C: POST /tools/call with resource-bound token
    MCP_C->>MCP_C: Validate: aud == MCP Server C
```

**Key Principle:** Each MCP server receives a token bound ONLY to itself. Token for Server A cannot be replayed against Server B. Agent cannot accumulate permissions across multiple calls.

---

## 2. Agent Identity Models

### 2.1 Four Identity Roles in Agentic UI

| Role | Description | Implementation | Principle |
| --- | --- | --- | --- |
| **Human User Identity** | The end user who initiated the interaction | OIDC id_token from IdP (Entra, Okta, Cognito) | Source of truth; never impersonated |
| **Agent Service Identity** | The agent process itself, independent of any user | Service principal / managed identity (not a human account) | Exists even for autonomous/scheduled runs |
| **Delegated Agent Identity** | Agent acting on behalf of a specific user | OBO token (scoped subset of user's access) | Used for user-initiated interactive tasks |
| **Sub-Agent Identity** | A specialized agent invoked by an orchestrator | Scoped delegation from parent, signed by A2A Agent Card | Cannot exceed parent's permission scope |

### 2.2 Agent Service Identity — The Critical Design Decision

The most common identity mistake in agentic system design is reusing an existing human user account as the agent's service identity, or cloning the running user's identity onto the agent. Both patterns produce excess privilege that is difficult to audit and impossible to scope correctly.

```text
WRONG — agent identity cloned from user
  User: alice@corp.com (Salesforce admin, has CRM full access)
  Agent identity: also alice@corp.com
  Result: agent can do anything Alice can do, including deleting CRM records

WRONG — shared service account
  All agents share: agent-service@corp.com
  Result: one compromised agent can act as any agent; no per-agent audit trail

CORRECT — dedicated service principal per agent
  Orchestrator agent:  agent-orchestrator@corp-agents.com
    Permissions: read-only access to task queue, emit AG-UI events
  CRM sub-agent:       agent-crm-reader@corp-agents.com
    Permissions: Salesforce: read opportunities, accounts (no write)
  Analytics sub-agent: agent-analytics@corp-agents.com
    Permissions: BigQuery: read sales_reporting dataset only
```

**Entra ID implementation:** Use Entra Agent ID (in preview/GA as of mid-2026) or a dedicated App Registration per agent type. Assign only the Microsoft Graph / API permissions required by that agent's published tool manifest.

**AWS AgentCore implementation:** Assign an IAM Role per agent. Use trust policy to scope which Lambda functions or containers can assume the role. Apply least-privilege IAM policies scoped to the exact S3 paths, DynamoDB tables, or Bedrock models the agent needs.

---

## 3. OAuth 2.1 Delegation Chains

### 3.1 On-Behalf-Of (OBO) Flow

The On-Behalf-Of flow (RFC 8693 Token Exchange) allows the agent to acquire a new token scoped to the user's identity but limited to the permissions the agent actually needs. This is the correct pattern for user-initiated interactive agent tasks.

```text
OBO FLOW — USER-INITIATED AGENT TASK

Step 1: User authenticates to the AG-UI frontend
        IdP returns: access_token (user's full scopes) + id_token

Step 2: Frontend sends POST /agent/run with Authorization: Bearer <user_access_token>

Step 3: AG-UI handler validates the user access_token
        Checks: iss, aud, exp, nbf, signature

Step 4: AG-UI handler calls OBO endpoint to exchange for agent token
        POST /oauth2/v2.0/token  (Entra)  OR  POST /oauth/token  (Okta)
        grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer
        assertion=<user_access_token>
        requested_token_use=on_behalf_of
        scope=<minimum required scopes for this agent task>

Step 5: IdP validates:
        - User consented to these scopes
        - Agent service principal is authorized to request OBO tokens
        - Requested scopes are a subset of user's existing grants

Step 6: IdP returns: agent_access_token
        Claims: sub=<user_oid>, azp=<agent_client_id>, scp=<requested_scopes>
        This token represents the user but with a narrower scope

Step 7: Agent uses agent_access_token for downstream MCP calls
        Each MCP server validates: iss, aud, scp, exp
        MCP server receives a token proving: "user X, via agent Y, for scope Z"

IMPORTANT: The OBO token carries the USER'S identity (sub = user_oid)
           This means audit logs show which user's data was accessed,
           not just which agent ran.
```

### 3.2 Resource Indicators — RFC 8707

Resource Indicators prevent token replay attacks where a token issued for MCP Server A is used against MCP Server B. The agent requests a separate token for each downstream resource.

```text
RFC 8707 TOKEN BINDING

Without Resource Indicators:
  Token issued for: "scope: crm:read analytics:read"
  Agent can use this token against ANY server that accepts these scopes
  RISK: if agent is compromised, token can be replayed against unintended servers

With Resource Indicators (RFC 8707):
  Token request for CRM MCP server:
    POST /oauth2/v2.0/token
    resource=https://crm-mcp.corp.com   ← Resource Indicator
    scope=crm:read
    → Token audience: aud=https://crm-mcp.corp.com  ← bound to this server only

  Token request for Analytics MCP server:
    POST /oauth2/v2.0/token
    resource=https://analytics-mcp.corp.com
    scope=analytics:read
    → Token audience: aud=https://analytics-mcp.corp.com

  CRM MCP server validates: aud == "https://crm-mcp.corp.com" → ACCEPT
  Analytics MCP server validates: aud == "https://crm-mcp.corp.com" → REJECT

RESULT: Each token is cryptographically bound to a single MCP server.
        Replay across servers is structurally impossible.
```

### 3.3 Protected Resource Metadata — RFC 9728

RFC 9728 allows MCP servers to publish their authorization requirements in a discoverable metadata document. Agents can automatically discover what scopes and resource indicators are required before requesting tokens.

```text
RFC 9728 DISCOVERY FLOW

Step 1: Agent queries MCP server metadata endpoint
        GET https://crm-mcp.corp.com/.well-known/oauth-protected-resource

Step 2: MCP server returns:
        {
          "resource": "https://crm-mcp.corp.com",
          "authorization_servers": ["https://login.microsoftonline.com/{tenant}"],
          "scopes_supported": ["crm:read", "crm:write", "crm:admin"],
          "bearer_methods_supported": ["header"]
        }

Step 3: Agent uses this metadata to construct the correct token request:
        - Knows which authorization server to use
        - Knows which scope to request
        - Knows the resource indicator value
        → No hardcoded auth configuration in agent code

ENTERPRISE BENEFIT: New MCP servers added to the cluster are automatically
                    discoverable without updating agent configuration.
```

---

## 4. MCP Authentication Architecture

### 4.1 Per-Server Auth Boundary

Each MCP server must enforce its own authentication boundary, independent of whether the calling agent or gateway has already validated something. This is defense-in-depth: the MCP server does not trust that the agent stack "already checked."

**MCP Server Auth Boundary**

```mermaid
flowchart TD
    A["Agent POST /tools/call<br/>Authorization: Bearer &lt;token&gt;"] --> B["1. Validate Bearer Token<br/>Check: iss, aud, exp, nbf, scp"]
    B --> C{Token<br/>Valid?}
    C -->|No| D["Return 401 Unauthorized"]
    C -->|Yes| E["2. Extract user identity<br/>sub = user_oid"]
    E --> F["3. Look up user permissions<br/>user_oid → Salesforce user → roles"]
    F --> G{Authorized<br/>for tool?}
    G -->|No| H["Return 403 Forbidden"]
    G -->|Yes| I["4. Execute tool call"]
    I --> J["5. Return result<br/>+ audit log entry"]
    D --> K["MCP SERVER RESPONSE"]
    H --> K
    J --> K
    
    style B fill:#e1f5ff
    style F fill:#e1f5ff
    style I fill:#c8e6c9
```

**What the MCP Server Does NOT Trust:**
- `X-Agent-Authorized: true` header
- Claims that the gateway already validated the token
- Agent assertions about user permissions
- Any input from the agent's context (prompt content, tool args) for authorization decisions — only the signed JWT is authoritative

### 4.2 MCP Auth Stack Summary

| Standard | Role | Status (July 2026) |
| --- | --- | --- |
| OAuth 2.1 | Authorization framework (replaces OAuth 2.0) | Required per MCP spec |
| OIDC | User identity and ID token issuance | Required for user-delegated flows |
| RFC 8693 | Token exchange (OBO flow) | Required for delegation chains |
| RFC 8707 | Resource Indicators (token binding) | Required per MCP spec |
| RFC 9728 | Protected Resource Metadata (discovery) | Required per MCP spec |
| PKCE | Code flow security for public clients | Required per OAuth 2.1 |
| mTLS | Transport-level client authentication | Recommended for service-to-service MCP calls |

---

## 5. Multi-Tenant Token Isolation

In enterprise deployments with multiple tenants sharing the same agent infrastructure, token isolation is critical. A tenant A user must never receive data from tenant B, even if both tenants use the same agent orchestrator.

```text
MULTI-TENANT ISOLATION PATTERN

Tenant A User                    Tenant B User
                                     
     OIDC token (tid=tenant-a)        OIDC token (tid=tenant-b)
    ▼                                 ▼

  AG-UI Handler                                
  Extracts: tid claim from incoming token     
  Routes to: tenant-a-specific agent context  
  No cross-tenant state, memory, or context   

                  OBO token exchange (includes tid claim)
                 ▼

  MCP Server                                   
  Validates: tid = tenant-a-id in token       
  Applies: tenant-a row-level security filter 
  Returns: only tenant-a data                 


CONTROLS
  - Tenant ID (tid) claim is cryptographically signed in the token
  - Agent context is scoped to a session; sessions are tenant-scoped
  - Memory store keys are prefixed with tenant_id
  - State store partitioned by tenant_id
  - No cross-tenant agent memory (episodic or semantic)
  - Audit log includes tenant_id on every entry
```

---

## 6. Cross-Agent Identity (A2A)

When an orchestrator agent delegates a task to a sub-agent (A2A protocol), the sub-agent must be able to verify the orchestrator's identity and the delegation is bounded.

### 6.1 Agent Cards and Signed Delegation

```text
A2A DELEGATION CHAIN

Orchestrator Agent
  Agent Card: {
    id: "urn:agent:orchestrator:v1",
    capabilities: ["task_planning", "sub_agent_delegation"],
    public_key: "ed25519:...",
    endpoint: "https://orchestrator.agents.corp.com"
  }
  Signed with orchestrator private key

    POST /tasks/send to CRM Sub-Agent
    Task payload signed with orchestrator private key
    Includes: user_identity_hint, delegated_scopes, task_id
   ▼

CRM Sub-Agent
  Verifies: task payload signature against orchestrator's public key (from Agent Card)
  Verifies: orchestrator is listed in its trusted-callers policy
  Validates: delegated_scopes ⊆ sub-agent's own permission set
  (Sub-agent cannot accept scopes it doesn't hold)
  Acquires: its own scoped token for MCP calls (using its own service identity)
```

### 6.2 Preventing Privilege Escalation in A2A

The most critical constraint: a sub-agent must never hold more permission than the orchestrator grants, and the orchestrator cannot grant more than the user delegated to it.

```text
PERMISSION HIERARCHY (must be monotone non-increasing)

User permissions (source of truth)
   Can read: CRM opportunities, Analytics dashboards
   Cannot: delete CRM records, modify user accounts

OBO token granted to Orchestrator Agent
   Scope: crm:read analytics:read  (subset of user permissions)
   CANNOT grant sub-agents more than this

Delegation to CRM Sub-Agent
   Scope: crm:read  (subset of orchestrator's scope)
   BLOCKED: if orchestrator tries to grant crm:write (it doesn't hold it)

Delegation to Analytics Sub-Agent
   Scope: analytics:read  (subset of orchestrator's scope)

ENFORCEMENT: The IdP rejects OBO/token-exchange requests for scopes
             the requesting token does not already contain.
             The MCP server validates scopes in the token (signed, not
             asserted by the agent) — agent cannot self-grant scopes.
```

---

## 7. Service Identity for Autonomous Agents

Not all agent runs are user-initiated. Scheduled agents, event-triggered agents, and monitoring agents run without a human user's session. These use a service identity (not OBO).

```text
AUTONOMOUS AGENT IDENTITY PATTERN

Event trigger (cron/webhook/queue)
         
         ▼

  Agent Orchestrator                             
  Identity: managed identity / service principal
  Credentials: injected by platform at runtime  
    (not stored in code, env vars, or config)   
                                                 
  Token acquisition: client_credentials flow    
  POST /oauth2/v2.0/token                       
  grant_type=client_credentials                 
  scope=<agent service scope>                   
  client_assertion=<workload identity JWT>      


WHAT NOT TO DO
  ✗ Store client_secret in application config
  ✗ Use long-lived API keys in environment variables
  ✗ Share service identity across agents

WHAT TO DO
  ✓ Use Workload Identity Federation (no secrets stored anywhere)
  ✓ Kubernetes: ServiceAccount → Workload Identity → Entra App
  ✓ AWS: EC2/Lambda IAM Role → no stored credentials
  ✓ Token lifetime: 1 hour max, refreshed at runtime
  ✓ Separate service principal per agent type with least-privilege role
```

---

## 8. Secrets Management

Tools and MCP servers often need credentials to call backend APIs (database passwords, API keys, OAuth client secrets). These must never pass through the agent's context window.

```text
CREDENTIAL INJECTION PATTERN (correct)

Agent Context Window:
  "Call the CRM API to get opportunities for customer {{customer_id}}"
  Tool definition: { name: "crm.get_opportunities", params: {customer_id} }
  ← NO credentials in context window

Tool Dispatcher / API Gateway:
  Receives tool call: crm.get_opportunities({customer_id: "acct-123"})
  Looks up CRM credentials from secrets store (Azure Key Vault / AWS Secrets Manager)
  Injects Authorization header before forwarding to CRM API
  ← Credentials never touch the agent or the LLM

CRM API:
  Receives: GET /opportunities?customer_id=acct-123
  Header: Authorization: Bearer <crm_api_token>
  ← Token was injected by the gateway, never seen by the model

WRONG PATTERNS
  ✗ System prompt: "Use API key sk-1234 to call the CRM"
  ✗ Tool argument: {customer_id: "...", api_key: "sk-1234"}
  ✗ Memory store contains plaintext credentials
  ✗ Skill instructions reference credentials by name
```

| Secrets Store | Use Case | TTL Recommendation |
| --- | --- | --- |
| Azure Key Vault | Entra-native workloads, certificate rotation | 90 days max for secrets; use managed identity where possible |
| AWS Secrets Manager | AWS-native workloads, RDS password rotation | Auto-rotation enabled; 30-day rotation for API keys |
| HashiCorp Vault | Multi-cloud, dynamic secrets | Dynamic secrets (generated per-request, expire after use) |
| Kubernetes Secrets (encrypted etcd) | MCP server pod credentials | Use External Secrets Operator to sync from Key Vault/SM |

---

## 9. AG-UI Transport Authentication

The AG-UI SSE stream itself must be authenticated. The client initiates the stream with a valid user token; the server validates it before beginning the stream.

```text
AG-UI TRANSPORT AUTH FLOW

Client:
  POST /agent/run
  Headers:
    Authorization: Bearer <user_oidc_access_token>
    Content-Type: application/json
  Body: {messages, state, context}

Server (AG-UI Handler):
  1. Extract Bearer token from Authorization header
  2. Validate token:
     - iss = expected OIDC issuer
     - aud = AG-UI server client_id
     - exp > now
     - nbf ≤ now
     - signature valid (JWKS endpoint)
  3. Extract user claims: sub, email, groups/roles
  4. Check session rate limits (per sub)
  5. Begin OBO token exchange for downstream services
  6. Open SSE stream: Content-Type: text/event-stream
  7. Correlate all AG-UI events with run_id + user sub

Client SSE reconnection:
  If stream drops, client reconnects with same Bearer token
  Server validates token again (may have refreshed in client)
  Server resumes from last known state (Redis-backed session)

WEBSOCKET VARIANT:
  Initial HTTP Upgrade includes Authorization header
  After upgrade, connection is authenticated for its lifetime
  Token refresh requires closing and re-opening connection
  (or use a heartbeat mechanism to refresh tokens in-band)
```

---

## 10. Identity Anti-Patterns

| Anti-Pattern | Risk | Correct Pattern |
| --- | --- | --- |
| Cloning human user identity onto agent | Agent can do anything the human can (excess privilege) | Dedicated service principal with least-privilege |
| Shared service account across all agents | No per-agent audit; one compromise affects all | One identity per agent type |
| Long-lived static API keys in env vars | Key rotation is manual; leaked key persists | Workload Identity Federation + dynamic secrets |
| Credentials in agent system prompt or instructions | LLM output may leak the credential | Gateway-side credential injection |
| No Resource Indicators (RFC 8707) | Token for MCP Server A replayable against Server B | Bind each token to its target resource |
| OBO token with full user scopes | Agent can do everything the user can (violates least-privilege) | OBO with minimum required scopes only |
| Trusting agent claims about user permissions | Agent can assert false claims (prompt injection) | Only trust signed JWT claims |
| Single token for all MCP servers | Token compromise exposes all backends | Per-server token with RFC 8707 binding |

---

## Related Pages

- [Security Architecture](19-agentic-ui-security-architecture.md) — Trust boundaries, OWASP ASI mapping, attack surfaces
- [Enterprise Reference Architecture](08-enterprise-reference-architecture.md) — Layer 6 (Identity Service), TB3–TB5
- [Entra 3LO Implementation Guide](../../protocols/index.md) — Full OBO implementation with code
- [Entra 3LO Security Review](../../protocols/index.md) — Security audit patterns
- [Agent Identity: Entra vs AgentCore](../../protocols/index.md) — Platform comparison
