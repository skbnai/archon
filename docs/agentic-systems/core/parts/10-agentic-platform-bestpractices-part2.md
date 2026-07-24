---
title: "Enterprise Agentic Platform Best Practices — Part 2"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agentic-platform-bestpractices-part2
supersedes: []
---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/core/10-agentic-platform-bestpractices) — This is Part 2 of 3. Covers multitenancy, MCP security, and ADFS. [Continue with Part 3 →](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part3) for observability, governance, and implementation.**

# Enterprise Agentic Platform Best Practices — Part 2

Continuation from Part 1: Integration patterns, multitenancy design, security antipatterns, compliance requirements, and implementation roadmap.

## 4. Multitenancy Design

:::note

In the bank context, multitenancy has two meanings: (a) multiple business divisions sharing the platform (internal multitenancy — e.g., Retail Banking vs. Wealth Management), and (b) potentially serving external clients via APIs (external multitenancy). The isolation requirements and threat model differ.

:::

## 4.1 Multitenancy Isolation Model

| Layer | Internal Multitenancy | External Multitenancy |
| --- | --- | --- |
| AgentCore Runtime | Shared runtime; session isolation per microVM | Separate runtime per tenant; no shared infrastructure |
| AgentCore Memory | Namespace-scoped: tenant:{div}:user:{sub} | Separate memory store per external tenant |
| MCP Servers | Shared; FT rights restrict data access | Separate MCP instances or strict tenant_id row filtering |
| Langfuse Traces | Tenant_id tag on all traces; project-level access control | Separate Langfuse projects per external tenant |
| DynamoDB (context) | Partition key includes tenant_id | Separate table or separate AWS account |
| LLM Model Access | Shared Bedrock model endpoint | Shared Bedrock model endpoint (model is stateless) |
| Agent SOPs | Shared SOPs parameterised by tenant policy | Tenant-specific SOPs with tenant-specific rules |
| IAM / Roles | Single IAM role per agent type | Separate IAM role per external tenant (IAM boundary) |

## 4.2 Tenant Context Propagation

:::tip[✅ Best Practice]

Add a tenant_id claim to the enriched context JWT at the BFF layer. The tenant_id should be derived from the user's AD OU (organizational unit) or a separate tenant registry. Pass tenant_id in all downstream calls as a header (X-Tenant-ID) and include it in all DynamoDB partition keys, memory namespaces, Langfuse trace metadata, and MCP tool invocations.

:::

:::danger[❌ Antipattern]

Inferring tenant from the user's email domain or UPN suffix. Email domains can be shared across tenants or spoofed. Always derive tenant_id from a trusted, verified attribute in the ADFS token (e.g., the AD OU or a custom ADFS claim attribute) and validate it at the BFF layer.

:::

## 4.3 Cross-Tenant Data Leakage Prevention

:::warning

The most critical multitenancy risk for a bank is cross-tenant data leakage via the LLM context. If a supervisor agent's context window contains data from Tenant A (e.g., a customer name from a previous tool call), and the session is improperly reused for Tenant B, the model may surface Tenant A's data in Tenant B's response. The AgentCore microVM isolation per session is the primary mitigation, but the application tier must also enforce tenant scoping.

:::

:::tip[✅ Best Practice]

Implement a TenantContextMiddleware that: (1) extracts tenant_id from the enriched JWT, (2) injects tenant_id into every tool call parameter at the agent layer, (3) validates that tool results belong to the expected tenant before returning them to the agent, and (4) logs any cross-tenant data access attempt as a CRITICAL security event.

:::

:::danger[❌ Antipattern]

Relying solely on MCP server-side row-level filtering for tenant isolation. If the MCP server has a bug in its filtering logic, the agent may receive cross-tenant data. Defence in depth requires tenant validation at both the agent input (tool parameter injection) and the agent output (result validation) layers.

:::

## 4.4 Tenant-Specific Rate Limiting and Cost Governance

:::tip[✅ Best Practice]

Implement per-tenant token budgets using a Redis-backed counter. Each tenant should have a configurable daily LLM token budget. When a tenant approaches their budget, degrade gracefully (disable complex multi-step agents, switch to lighter models) rather than hard-blocking, which creates a poor user experience.

:::

```python
# ✅  CORRECT: Per-tenant token budget enforcement
import redis

class TenantBudgetGuard:
    def __init__(self, redis_client, budgets: dict):
        self.redis = redis_client
        self.budgets = budgets  # {tenant_id: daily_token_limit}

    async def check_and_deduct(self, tenant_id: str, estimated_tokens: int) -> str:
        key = f'token_budget:{tenant_id}:{date.today().isoformat()}'
        current = int(self.redis.get(key) or 0)
        budget = self.budgets.get(tenant_id, 100000)
        usage_pct = current / budget
        if usage_pct > 1.0:
            return 'BLOCKED'
        elif usage_pct > 0.85:
            return 'DEGRADED'  # switch to lighter model
        self.redis.incrby(key, estimated_tokens)
        self.redis.expire(key, 86400)  # 24h TTL
        return 'ALLOWED'
```

## 5. MCP Security — Best Practices & Antipatterns

## 5.1 MCP Server Design

:::tip[✅ Best Practice]

Design MCP tools with the principle of least privilege: each tool schema should expose only the minimum parameters needed. Avoid free-text fields in tool parameters that could be exploited for prompt injection (e.g., instead of query: string, use predefined enum values where possible). Validate all input parameters server-side against a whitelist.

:::

:::danger[❌ Antipattern]

Implementing MCP tools that accept and execute raw SQL or shell commands constructed from user input. Even if the agent is trusted, the LLM can be manipulated via prompt injection in tool results to construct malicious queries. Always use parameterised queries and never pass LLM-generated strings directly to SQL or shell commands.

:::

## 5.2 MCP Server Versioning and Compatibility

:::tip[✅ Best Practice]

Version all MCP server tool schemas using semantic versioning (e.g., customer-mcp/v2.1). Use the AgentCore Gateway's tool selection feature to route specific agent versions to compatible MCP server versions. Maintain backward-compatible schema changes (additive only) and deprecate, not remove, old tool signatures.

:::

:::danger[❌ Antipattern]

Breaking MCP tool schema changes in place (renaming fields, changing types, removing parameters). When an agent is mid-execution and a tool schema changes, the agent's planned tool call will fail, creating difficult-to-debug errors. MCP tools must be treated as public API contracts with proper versioning discipline.

:::

## 5.3 MCP Tool Call Idempotency

:::tip[✅ Best Practice]

All state-mutating MCP tools (e.g., submit_trade_order, update_customer_record) must be idempotent via a client-provided idempotency key. The agent should include a call_id (derived from the session_id + tool_name + timestamp) in every mutating tool call. The MCP server must return the same result for duplicate calls within a 24-hour window.

:::

:::danger[❌ Antipattern]

Allowing agents to retry failed mutating tool calls without idempotency keys. If a trade submission tool call times out and the agent retries, without idempotency enforcement the trade may be submitted twice. This is a critical financial risk — all write operations must be idempotent.

:::

## 5.4 Tool Result Validation

:::tip[✅ Best Practice]

Validate MCP tool results before returning them to the agent. Check that the returned data belongs to the requesting tenant (tenant_id match), that numeric fields are within plausible ranges, and that PII fields are appropriately masked. Log any validation failures as security events.

:::

:::danger[❌ Antipattern]

Passing raw database query results directly to the agent context without sanitisation. Database results may contain fields the LLM should not see (internal flags, system fields, cross-tenant data due to missing WHERE clause). Always apply a response schema filter that extracts only the declared output fields.

:::

## 6. ADFS / FT Rights — Known Issues & Solutions

## 6.1 Known Issue: ADFS 2019 Resource Parameter

:::warning

ADFS 2019 (sts.danskebank.com) requires the 'resource' parameter in the token request to return AD group claims. If the resource parameter is omitted, a token is issued but group claims are absent. This is a commonly reported issue causing silent authorisation failures where users appear authenticated but have no AD groups.

:::

:::tip[✅ Best Practice]

Always include the resource parameter in all ADFS 2019 token requests. The resource value must exactly match the Service Application name registered in Cloud2 / AD. Validate group claim presence in the BFF token enrichment step and fail fast with a descriptive error if groups are empty.

:::

## 6.2 Known Issue: FT Rights Staleness (Mid-Session Revocation)

:::warning

FT rights are resolved at login time and embedded in the session token. If a bank administrator revokes a user's FT rights mid-session (e.g., after detecting suspicious activity), the user retains access until session expiry (up to 1 hour). This is a regulatory risk.

:::

:::tip[✅ Best Practice]

Implement a real-time FT revocation webhook. When the FT Service revokes rights, it publishes to an SNS topic. The BFF subscribes and immediately invalidates the affected session in Redis (delete the session key). The next agent call will fail JWT validation and redirect to re-authentication.

:::

## 6.3 Known Issue: JWKS Cache Poisoning

:::warning

If an attacker can manipulate the JWKS refresh endpoint (via DNS poisoning or BGP hijacking of the ADFS endpoint), they could inject a fake public key, allowing forged tokens to be validated. This is a low-probability but high-impact attack.

:::

:::tip[✅ Best Practice]

Implement JWKS certificate pinning for the ADFS endpoint. Cache the expected certificate thumbprints in Secrets Manager and validate them on every JWKS refresh. Additionally, use DNSSEC-validated resolution for the ADFS hostname and route JWKS refresh traffic through AWS PrivateLink where possible (ADFS 2019 internal endpoint).

:::

## 6.4 Known Issue: JWT Claim Namespace Collisions

:::warning

When the BFF adds custom claims (ft_rights, enriched_at, tenant_id) to the JWT, there is a risk of collision with standard OIDC claims if the claim names are not namespaced. Future OIDC specs or ADFS updates could introduce claims with the same names, causing validation errors.

:::

:::tip[✅ Best Practice]

Namespace all custom BFF-injected claims with a bank-specific prefix. Use a URI-style namespace for production: https://bank.eu/claims/ft_rights instead of ft_rights. Validate the namespace in all downstream claim extraction code.

:::

---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/core/10-agentic-platform-bestpractices) — End of Part 2. [Continue with Part 3 →](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part3) for observability, governance, and implementation.**
