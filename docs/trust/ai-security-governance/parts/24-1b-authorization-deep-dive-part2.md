---
title: "Authorization Deep Dive: Engines, Interceptor Patterns & XACML (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: 1b-authorization-deep-dive-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol1b_Authorization_Deep_Dive.md]
tags: [authorization, ai-security, policy, stride, performance]
covers_version: "as of 2026"
---

Event-driven authorization for asynchronous multi-agent workflows, a complete STRIDE threat model for the authorization stack, and production authorization performance benchmarks.

## Event-Driven Authorization Architecture

Multi-agent workflows often operate asynchronously via EventBridge or SQS. Authorization in event-driven systems requires a different pattern — the PEP cannot block in the traditional synchronous sense, but must validate events before they reach consumers.

**Event authorization pipeline:**

1. **Event Producer** (agent) publishes an event to EventBridge including principal claims, action, resource, and context.
2. **EventBridge Rule** routes the event to an Authorization Lambda before it reaches any consumer: the Lambda extracts principal claims from the event, calls Cedar AVP `IsAuthorized`, and on deny routes the event to a Dead Letter Queue while publishing an `AUTHORIZATION_DENIED` event for the SIEM; on allow it forwards the event to the target consumer.
3. **Consumer** (specialist agent or service) re-validates on receipt as defense in depth — a compromised EventBridge rule cannot bypass consumer-side authorization.
4. **Business Logic Execution** proceeds only after both checks pass.

The Authorization Lambda requires every event to carry an `authorizationContext`; an event missing this context is denied outright (`MISSING_AUTH_CONTEXT`). For events that do carry context, the Lambda maps the event's `detail-type` to a Cedar action and its `resources` field to a Cedar resource, evaluates the request against Amazon Verified Permissions, and on `ALLOW` publishes an audit event while letting the event proceed; on deny it writes the event and denial reason to the dead-letter queue and publishes an `AUTHORIZATION_DENIED` event to the enterprise audit bus for SIEM correlation.

## Complete STRIDE Threat Model for Enterprise Agentic AI

The following is a comprehensive STRIDE threat model for the entire authorization stack. Each threat includes its attack scenario, affected components, and specific mitigations implemented in this architecture.

**Spoofing threats:**

| Threat | Attack Scenario | Affected Components | Mitigation |
|---|---|---|---|
| Agent Identity Spoofing | Malicious code claims to be a trusted agent (e.g., "payments-agent") by forging its entity ID in a Cedar request | Cedar PDP, MCP Gateway | Agent identity must be derived from an mTLS certificate or signed IAM role credential — never from a self-reported header |
| User Impersonation by Agent | Agent uses a stored user token to act beyond its delegation scope | Token Exchange Service | RFC 8693 delegation tokens are scope-constrained and carry an `act` claim; Cedar verifies `act.sub` matches the delegated scope |
| JWT Replay Attack | Attacker replays a captured user JWT to gain unauthorized access | Lambda Authorizer | JWT `jti` (JWT ID) is tracked in ElastiCache for the token lifetime; a duplicate `jti` triggers deny + alert |
| Tenant Claim Forgery | Attacker modifies the JWT `tenant_id` claim to access another tenant's data | Claims Normalization | Tenant ID is cryptographically bound in the JWT signature; only the IdP can set it, and normalization re-validates against the IdP |
| JWKS Poisoning | Attacker substitutes a malicious JWKS endpoint to validate forged tokens | Lambda Authorizer | JWKS endpoint URL is hardcoded in authorizer config (not token-derived); certificate pinning in production |

**Tampering threats:**

| Threat | Attack Scenario | Affected Components | Mitigation |
|---|---|---|---|
| Context Manipulation | Agent modifies `risk_score` or `businessHours` in the context object before Cedar evaluation | Claims Normalization, PDP | Context is constructed server-side from signed claims and server clock; client-supplied context values are rejected and the context hash is audited |
| Policy Store Tampering | Attacker modifies Cedar policies directly in the AVP console, bypassing CI/CD | AVP Policy Store, PAP | AVP policy changes trigger CloudTrail alerts; a config rule detects drift; all changes require PRs and MFA for AVP console access |
| Audit Log Tampering | Attacker modifies or deletes CloudTrail logs to hide unauthorized actions | CloudTrail, S3 | S3 Object Lock (WORM) on the audit bucket; CloudTrail log file validation via SHA-256 chain; log delivery to a separate security account |
| Memory Injection | Agent writes malicious content to a shared memory store that influences other agents | Memory Store, DynamoDB | Memory write authorization via Cedar policy; content classification before write; shared memory requires explicit project membership |

**Repudiation threats:**

| Threat | Attack Scenario | Mitigation |
|---|---|---|
| Tool Invocation Denial | Agent or user denies having invoked a destructive tool | CloudTrail records every AVP `IsAuthorized` call with principal, action, resource, decision, and policy matched; KMS-signed records are non-repudiable |
| Policy Change Denial | Administrator denies having changed a Cedar policy | AVP policy changes are logged to CloudTrail with the IAM principal who made the change; signed Git commit history provides additional non-repudiation |
| Data Access Denial | Agent denies having accessed a classified document via RAG | Post-retrieval Cedar evaluation logs every document-access decision; document chunk IDs and content hashes are in the audit record |

**Information disclosure threats:**

| Threat | Attack Scenario | Mitigation |
|---|---|---|
| Cross-Tenant Data Leakage | Agent retrieves documents belonging to another tenant via RAG | Mandatory Cedar forbid on tenant mismatch; pre-retrieval vector filter by `tenant_id`; storage partition isolation as defense-in-depth |
| Over-Privileged LLM Context | Retrieved documents exceed the user's clearance level and are injected into LLM context | Post-retrieval Cedar per-chunk authorization removes over-classified chunks before context injection |
| Authorization Decision Leakage | Error messages reveal policy structure (e.g., naming the specific group a user lacks) | All denial responses return a generic 403; detailed denial reasons are logged to CloudTrail only, never in API responses |
| Memory Cross-User Leakage | Agent reads another user's episodic memory by manipulating session context | Memory records are keyed by `userId#tenantId` in DynamoDB; Cedar forbids when `memory.ownerId != principal.userId` |
| PII in Agent Output | LLM generates a response containing PII extracted from retrieved documents | Bedrock Guardrails + Amazon Macie scan agent outputs; Cedar output-classification policy blocks and flags DLP-failed outputs |

**Denial of service threats:**

| Threat | Attack Scenario | Mitigation |
|---|---|---|
| PDP Exhaustion | Attacker floods AVP with `IsAuthorized` calls to exhaust capacity and cause deny-all | AVP is managed and auto-scales; Lambda Authorizer caches decisions (300s TTL); rate limiting at WAF and API Gateway; circuit breaker defaults to deny (not open) if AVP is unavailable |
| Cache Poisoning DoS | Attacker triggers massive cache invalidation via repeated policy changes | Policy changes require a multi-step, multi-approver CI/CD pipeline; emergency cache flush requires a separate IAM permission; rate limiting on policy-change events |
| Tool Invocation Storms | Runaway agent invokes tools in a tight loop, exhausting downstream API quotas | Per-agent, per-tool rate limiting enforced at the MCP PEP Gateway; Step Functions workflow max concurrency; a dead man's switch on agent execution time |

**Elevation of privilege threats:**

| Threat | Attack Scenario | Mitigation |
|---|---|---|
| Confused Deputy Attack | Orchestrator agent accumulates permissions from multiple workflow steps, gaining more access than any single step should allow | Cedar evaluates the delegated scope at every step independently; no permission accumulation between steps; delegation tokens are scoped and time-limited |
| Prompt Injection Privilege Escalation | Adversarial content in retrieved documents instructs the agent to invoke tools it is not authorized for | Bedrock Guardrails detect injection patterns; Cedar tool authorization is independent of LLM reasoning — a prompt cannot grant Cedar permissions |
| Agent-to-Agent Privilege Escalation | Sub-agent claims broader scope than the orchestrator delegated | Cedar verifies the sub-agent's delegated scope is a subset of the orchestrator's scope; the token exchange service enforces scope intersection at delegation time |
| Expired Session Privilege Retention | Agent continues executing after the user's session expires, using cached authorization decisions | JWT expiry is enforced at normalization; cached decisions have a TTL no greater than the JWT expiry; re-authorization is required for sessions over 60 minutes |

## Authorization Performance Benchmarks

The following benchmarks are based on production measurements from AWS documentation, OPA/Styra benchmarks, and published enterprise implementations. All figures assume a warm cache unless stated otherwise.

**Latency benchmarks by component:**

| Component | P50 | P95 | P99 | P99.9 | Notes |
|---|---|---|---|---|---|
| AWS AVP `IsAuthorized` (managed) | 2ms | 5ms | 8ms | 15ms | Measured from Lambda in the same region |
| OPA sidecar (in-memory bundle) | 0.3ms | 0.8ms | 1.5ms | 3ms | Rego evaluation, no network I/O |
| OPA central server (network) | 1.5ms | 3ms | 5ms | 12ms | Same-AZ, HTTP/2 |
| Claims normalization (Redis hit) | 0.5ms | 1ms | 2ms | 4ms | ElastiCache same-AZ |
| Claims normalization (cold — LDAP) | 15ms | 25ms | 40ms | 80ms | Group GUID resolution from Entra |
| JWT signature validation (cached JWKS) | 0.3ms | 0.5ms | 1ms | 2ms | RSA-256 in Lambda memory |
| Lambda Authorizer total (cache hit) | 1ms | 2ms | 4ms | 8ms | API GW serves from IAM cache |
| Lambda Authorizer total (cache miss) | 25ms | 40ms | 60ms | 100ms | Cold path including the AVP call |
| RAG pre-filter construction | 0.2ms | 0.5ms | 1ms | 2ms | Derived from cached claims |
| Cedar chunk post-auth (per chunk) | 1ms | 2ms | 4ms | 8ms | Batch mode for multiple chunks |

**Cache hit rate targets:**

| Cache Layer | Target Hit Rate | If Miss | Impact of Miss |
|---|---|---|---|
| API GW IAM Policy Cache (300s) | &gt;70% | Lambda Authorizer executes | +40ms avg |
| Claims Normalization (Redis, 3600s TTL) | &gt;95% | Full LDAP + mapping pipeline | +30ms avg |
| PIP Attribute Cache (Redis, 300s TTL) | &gt;85% | DynamoDB attribute lookup | +5ms avg |
| OPA Bundle (in-memory, 30s refresh) | 100% | N/A (async refresh) | No impact on request path |
| Cedar AVP (no client-side cache) | N/A (managed) | Always calls AVP API | AVP manages internally |

**Performance engineering principle:** the critical path for 95% of requests must add less than 5ms of latency — achievable with warm caches. The 5% cold-path cost (25-60ms) is acceptable because it occurs only on the first request in a new session. Never sacrifice security for performance; instead, optimize the cache warm path.

**Throughput and scaling characteristics:**

| Component | Single Instance TPS | Horizontal Scaling | AWS Managed? |
|---|---|---|---|
| AVP `IsAuthorized` | ~5,000 TPS per region | AWS manages — effectively unlimited | Yes — fully managed |
| Lambda Authorizer | 1,000 concurrent (default) | Auto-scale — request an AWS limit increase | Yes — serverless |
| OPA Sidecar (ECS) | ~10,000 TPS per core | Scale with service instances (1:1) | No — self-managed |
| ElastiCache Redis (claims) | 100,000+ ops/sec per node | Cluster mode — horizontal sharding | Yes — managed |
| Claims Normalization (ECS) | 500 TPS per Fargate task (2 vCPU) | Auto-scaling on CPU/request metrics | Yes — Fargate managed |

## Related

- [Authorization Deep Dive (Part 1)](../24-1b-authorization-deep-dive.md)
- [Identity, Claims & Policy Design](../25-identity-claims-policy.md)
- [Executive Architecture & Authorization Fundamentals](../23-executive-architecture.md)
