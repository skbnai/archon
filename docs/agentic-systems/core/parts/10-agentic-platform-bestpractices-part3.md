---
title: "Enterprise Agentic Platform Best Practices — Part 3"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agentic-platform-bestpractices-part3
supersedes: []
---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/core/10-agentic-platform-bestpractices) | [Back to Part 2 ←](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part2) — This is Part 3 of 3. Covers observability, governance, and implementation.**

# Enterprise Agentic Platform Best Practices — Part 3

Continuation from Part 1-2: Observability, architecture governance, security strategies, and implementation roadmap.

## 7. Langfuse Observability — Best Practices

## 7.1 Strands + Langfuse Native Integration

:::note

Strands Agents and Langfuse have a first-party integration acknowledged in the Strands open-source announcement (Langfuse is an official contributor to the Strands project). The integration works via OTEL: Strands emits OTEL spans, which are forwarded to Langfuse's OTLP endpoint. No custom instrumentation is required for basic tracing.

:::

:::tip[✅ Best Practice]

Deploy Langfuse with its own dedicated RDS PostgreSQL (Multi-AZ) and S3 bucket within the VPC. Configure a daily S3 export of trace archives to meet MiFID II 7-year retention requirements. Apply S3 Object Lock (Compliance mode) to the archive bucket to prevent deletion even by administrators.

:::

## 7.2 Evaluation Pipeline

:::tip[✅ Best Practice]

Build an automated evaluation pipeline using Langfuse Datasets + Evaluators. Create a golden dataset for each agent type (customer agent, portfolio agent, compliance agent) that includes examples of: (1) correct FT boundary enforcement, (2) correct data scoping per tenant, (3) correct handling of FT denial. Run evaluations on every deployment and block promotion if accuracy drops below threshold.

:::

:::danger[❌ Antipattern]

Evaluating only LLM output quality (correctness, helpfulness) without evaluating security properties (FT rights enforcement, tenant isolation). An agent that gives correct financial advice but returns data for the wrong tenant is a production incident, not just a quality issue.

:::

## 7.3 PII Protection in Traces

:::tip[✅ Best Practice]

Configure Langfuse's field masking to redact specific fields before trace storage. Mask account numbers (16-digit sequences), national IDs, email addresses, and phone numbers in all span inputs and outputs. Use the MaskingFunction in Langfuse's configuration to apply regex-based redaction at ingestion time.

:::

| Data Type | Langfuse Masking Approach |
| --- | --- |
| Account numbers (IBAN/BBAN) | Regex: [A-Z]{2}[0-9]{2}[A-Z0-9]{4,30} → IBAN-REDACTED |
| Customer UPN / email | Pseudonymise: `SHA256(upn)[:8]` → shown as user_abc12345 |
| Customer full name | Partial: 'John D.' format or full redaction |
| Social Security / National ID | Full redaction |
| Trade amounts &gt; EUR 100k | Redact in trace, preserve in separate audit log |
| Credentials / tokens in headers | Full redaction — never log Authorization headers |

## 8. Architecture Issues Found & Resolutions

:::note

Based on the companion architecture document v1.0 and current research (March 2026), the following issues have been identified and resolved.

:::

## Issue #1: BFF as Trust Root without Rotation Automation

:::warning

The original architecture designated the BFF as the trust root that signs enriched context tokens. However, the BFF signing key rotation was listed as a quarterly manual process. Any compromise of the BFF signing key gives an attacker the ability to issue arbitrary tokens with any FT rights.

:::

Store the BFF RS256 signing key as a KMS Asymmetric Key (RSA_4096) — never as a stored secret. Use KMS Sign API for token signing; the private key never leaves KMS. Set KMS automatic key rotation every 90 days. After rotation, update the JWKS endpoint with the new public key alongside the old key (for in-flight token validation during rotation window). Add a CloudWatch alarm that triggers if the KMS key is accessed from outside the BFF service's IAM role or VPC endpoint.

## Issue #2: Redis Session Cache — Single Point of Failure

:::warning

ElastiCache Redis was identified as a critical dependency for authentication. If Redis becomes unavailable, all authenticated sessions fail validation and users are logged out. No fallback was defined in the original architecture.

:::

Deploy ElastiCache Redis with Multi-AZ and automatic failover. Configure a 60-second connection timeout and circuit breaker pattern. Implement a short-lived in-memory fallback: the BFF stores the last validated session in memory (LRU cache, TTL = 60 seconds, max 1000 entries) to serve during Redis reconnection. Add a Redis health check to the BFF's readiness probe. If Redis is down for &gt; 30 seconds, mark the BFF pod as not-ready, allowing the load balancer to drain it.

## Issue #3: AgentCore Runtime VPC Connectivity (Preview vs. GA)

:::warning

The original architecture was designed against AgentCore in preview (July 2025), which only supported Public and not VPC-only network configuration. As of the GA release (October 2025), VPC connectivity and PrivateLink are fully supported and should be used.

:::

Deploy AgentCore Runtime in VPC-only mode. Create a VPC endpoint for the AgentCore service and configure security groups to allow inbound from the API Gateway subnet only. Use PrivateLink for all AgentCore service calls (Runtime, Memory, Gateway, Identity, Observability). This ensures no agent invocation traffic traverses the internet. Update CloudFormation/CDK templates to use the AgentCore GA resource types (now available in CloudFormation, which was not available in preview).

## Issue #4: MCP Server Lambda Cold Start Latency

:::warning

Lambda-based MCP servers can experience 500ms–3s cold start latency for infrequently invoked tools. In a multi-step agent workflow, a cold start on a critical tool (e.g., get_customer_profile) can push total agent latency to &gt; 15 seconds, exceeding acceptable UX thresholds.

:::

Deploy customer-mcp and portfolio-mcp (the most frequently called tools) on ECS Fargate with a minimum of 1 running task (no cold start). Use Lambda only for low-frequency tools. For Lambda MCP servers that must remain Lambda, enable Provisioned Concurrency for the Lambda function. Set it to minimum 5 concurrent executions for production. Implement a tool warmup Lambda that pings all MCP Lambda servers every 10 minutes to prevent cold starts during off-peak hours.

## Issue #5: Strands Agent Loop — No Governance on Cost

:::warning

Strands' model-driven agent loop has no built-in token budget governance. An agent handling a complex query can consume 50,000+ tokens in a single session without any limit, leading to unexpected cloud spend in a multi-tenant environment.

:::

Implement the TenantBudgetGuard pattern described in Section 4.4. Apply daily and per-session token budgets per tenant and per agent type. Use the Strands callback_handler to monitor token usage in real time. If the current session approaches the per-session budget, inject a system message instructing the agent to summarise and conclude. Create a Langfuse alert on per-tenant token usage. Integrate with a cost anomaly detection Lambda that triggers a PagerDuty alert if any tenant's hourly spend exceeds 3x the rolling 7-day average.

## Issue #6: Strands Tools Batch Execution Without Tenant Context

:::warning

The Strands Batch Tool (from strands_tools) allows an agent to call multiple tools in parallel. If tool calls do not carry tenant context, parallel calls from agents serving multiple tenants in the same session could mix responses.

:::

Avoid using the generic strands_tools.batch tool. Instead, implement a bank-specific batch wrapper that injects tenant_id and ft_rights into every parallel tool call before dispatch. All custom @tool functions must extract tenant_id from the thread-local context (set at agent invocation time) rather than relying on the caller to pass it. This prevents tenant context from being accidentally dropped in batch calls.

## 9. Security Antipatterns — Comprehensive List

### Authentication & Token Management Antipatterns

:::danger[❌ Antipattern]

Storing ADFS ClientSecret in environment variables or ECS task definitions. Rotate via Secrets Manager and inject at runtime via the ECS Secrets integration. Never log or print client secrets.

:::

:::danger[❌ Antipattern]

Trusting JWTs that claim to be from the BFF without validating the kid (Key ID) header against the known BFF JWKS. Validate both signature AND kid to prevent algorithm confusion attacks.

:::

:::danger[❌ Antipattern]

Setting JWT expiry to &gt; 1 hour. Session tokens for financial operations should expire in 1 hour maximum. Long-lived tokens increase the blast radius of a token compromise.

:::

:::danger[❌ Antipattern]

Using symmetric (HS256) signing for the enriched context JWT. Use RS256 (asymmetric). HS256 requires sharing the secret key with all validating services — a credential sprawl risk.

:::

### Agent & LLM Security Antipatterns

:::danger[❌ Antipattern]

Forwarding raw user input directly to the LLM without sanitisation. For a financial services agent, always validate that user input does not contain prompt injection attempts (e.g., 'Ignore previous instructions and...') using Bedrock Guardrails.

:::

:::danger[❌ Antipattern]

Allowing agents to call external URLs directly. All HTTP calls from agents must go through an allowlisted HTTP proxy within the VPC. Agents should never be able to exfiltrate data to arbitrary external endpoints.

:::

:::danger[❌ Antipattern]

Logging complete LLM prompts and responses to CloudWatch Logs without PII masking. CloudWatch Logs retention is typically shorter than Langfuse retention, creating inconsistent audit trails. Route all LLM trace data through Langfuse with PII masking.

:::

:::danger[❌ Antipattern]

Using the same Bedrock model endpoint for all agent types without inference parameters differentiation. Set lower temperature (0.0–0.1) for tool selection steps, higher temperature (0.3–0.7) for text generation steps. This reduces hallucination risk in financial data retrieval.

:::

### MCP & Tool Antipatterns

:::danger[❌ Antipattern]

Implementing MCP tools that perform joins across tenant data at the database layer. All database queries in MCP tools must include a WHERE tenant_id = ? clause as the first filter predicate, before any other business logic.

:::

:::danger[❌ Antipattern]

Using tool names that reveal internal system architecture (e.g., rds_execute_query, lambda_invoke_data_function). Tool names are visible in LLM prompts and in traces. Use business-domain names (get_customer_portfolio) that do not reveal infrastructure details.

:::

:::danger[❌ Antipattern]

Returning error details from MCP tools that include stack traces, database query strings, or internal IP addresses. All errors must be mapped to standardised error codes (TOOL_UNAVAILABLE, DATA_NOT_FOUND, ACCESS_DENIED) before being returned to the agent.

:::

## 10. Implementation Roadmap

| Priority | Item | Section Ref | Effort |
| --- | --- | --- | --- |
| P0 — Critical | Migrate BFF signing to KMS Asymmetric Key | Issue #1 | 2 days |
| P0 — Critical | Deploy AgentCore Runtime in VPC-only mode | Issue #3 | 3 days |
| P0 — Critical | Implement AgentCore Gateway FT interceptor | Sec 3.2 | 3 days |
| P0 — Critical | Disable Dynamic MCP Client tool in all agents | Sec 2.5 | 1 day |
| P0 — Critical | Add ADFS 2019 resource parameter validation | Issue #6.1 | 1 day |
| P1 — High | Implement FT revocation SNS webhook | Issue #6.2 | 4 days |
| P1 — High | Deploy Strands OTEL → Langfuse pipeline | Sec 2.4.1 | 2 days |
| P1 — High | Implement TenantBudgetGuard for LLM spend | Sec 4.4 | 3 days |
| P1 — High | Add Redis multi-AZ with in-memory fallback | Issue #2 | 2 days |
| P1 — High | Migrate high-frequency MCP tools to ECS Fargate | Issue #4 | 5 days |
| P2 — Medium | Write Agent SOPs for all specialist agents | Sec 2.3 | 1 week |
| P2 — Medium | Implement Langfuse evaluation pipeline | Sec 7.2 | 1 week |
| P2 — Medium | Namespace all custom JWT claims | Issue #6.4 | 1 day |
| P2 — Medium | Add per-tenant token budget Langfuse alerts | Issue #5 | 2 days |
| P2 — Medium | Implement AgentCore Memory tenant namespacing | Sec 3.4 | 3 days |
| P3 — Normal | Implement JWKS certificate pinning | Issue #6.3 | 3 days |
| P3 — Normal | Build Langfuse golden dataset evaluations | Sec 7.2 | 2 weeks |
| P3 — Normal | Add MCP tool idempotency keys | Sec 5.3 | 1 week |
| P3 — Normal | Implement GraphBuilder for trade workflows | Sec 2.2.1 | 2 weeks |
| P3 — Normal | Deploy Strands Labs AI Functions for edge cases | Sec 2 notes | TBD |

---

**[Back to Part 1 ←](pathname:///archon/agentic-systems/core/10-agentic-platform-bestpractices) | [Back to Part 2 ←](pathname:///archon/agentic-systems/core/parts/10-agentic-platform-bestpractices-part2) — End of Part 3.**
