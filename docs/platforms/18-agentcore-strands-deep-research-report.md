---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/aws/agentcore_strands_deep_research_report.md]
tags: [aws, agentcore, strands, research-report, runtime, gateway]
covers_version: "as of 2026-07-10"
---

Architecture, security, operations, and roadmap research report covering Amazon Bedrock AgentCore and the Strands Agents SDK, April–June 2026.

## Executive Summary

Amazon Bedrock AgentCore is AWS's managed platform for taking AI agents from prototype to production. It is deliberately **not** an agent framework — it is a set of composable, independently-adoptable services (Runtime, Gateway, Identity, Memory, Policy, Registry, Harness, Browser, Code Interpreter, Observability, Evaluations, Optimization, and the newly previewed Payments) that sit underneath any agent framework, including AWS's own open-source **Strands Agents SDK**, LangGraph, CrewAI, LlamaIndex, the OpenAI Agents SDK, and the Claude Agent SDK. The platform's thesis, repeated consistently across AWS messaging since its October 2025 preview launch, is that the hard part of agentic AI was never writing the agent loop — it is securing tool calls, isolating sessions, managing identity across trust boundaries, and observing non-deterministic behavior at scale.

Between April and June 2026, AgentCore moved through its most consequential quarter to date:

- **Policy** (Cedar-based, deterministic, gateway-enforced authorization) reached general availability on **March 3, 2026**, and by June had grown Lambda-interceptor composability, Bedrock Guardrails integration, and natural-language-to-Cedar authoring.
- **AgentCore harness**, a fully declarative "two API calls to a production agent" abstraction built on Strands, went from preview (April 22, 2026) to general availability (**June 18, 2026**, announced at the AWS New York Summit), with multi-model mid-session switching, managed memory by default, and Step Functions integration.
- **Registry**, a governance catalog for agents, tools, MCP servers, and "skills," entered public preview (~April 2026) with a four-persona (Admin/Publisher/Approver/Consumer) IAM model but no auto-indexing, no federation, and no IaC support yet.
- **Payments** entered preview (May 7, 2026), letting agents autonomously transact against x402-priced APIs and MCP servers via Coinbase and Stripe wallet connections.
- **Gateway** added GA support for fronting AgentCore Runtime agents directly as targets, expanded OAuth 3LO/OBO token-exchange patterns, and gained Lambda request/response interceptors that compose with Cedar policy evaluation.
- **Observability** deepened its native CloudWatch GenAI Observability integration (Evaluations, Optimization/failure-insights) while remaining fully OpenTelemetry-compatible with Arize Phoenix, Datadog, LangSmith, Langfuse, and Braintrust.
- Independent security research (Palo Alto Unit 42, BeyondTrust Phantom Labs, Sonrai Security) found and AWS partially remediated real isolation gaps in Code Interpreter's "Sandbox" network mode — a material finding for any threat model built on AgentCore's isolation claims.
- At the same June 17 summit, AWS previewed two **adjacent but non-AgentCore** platform services — **AWS Continuum** (autonomous vulnerability remediation with staged learn-mode/enforce-mode trust) and **AWS Context** (an identity-aware enterprise knowledge graph) — that signal where the next 12–24 months of "trustable autonomy" investment is headed.

This report reverse-engineers each AgentCore service down to its request flow and trust boundary, maps the Strands SDK's internals onto that platform, builds a threat model grounded in both AWS's stated design and independent red-team findings, and closes with evidence-scored predictions for the platform's roadmap through mid-2028. Throughout, findings are graded by source strength: **AWS-documented** (official docs/blogs/release notes), **AWS-stated-marketing** (keynotes, press claims not yet independently verified), and **independent research** (security researchers, practitioner blogs, benchmarks).

## Part I — Platform Foundations

### Why AgentCore Exists

AWS's own framing, repeated by GM Madhu Parthasarathy and VP David Richardson across 2025–2026 talks, is that most agent pilots built with open-source frameworks stalled before production because teams had to hand-roll session isolation, credential handling, tool governance, and tracing — the same undifferentiated heavy lifting AWS solved once for compute (EC2), storage (S3), and containers (Fargate/Lambda). AgentCore is explicitly framework- and model-agnostic: it will run a LangGraph agent, a Strands agent, or hand-written Python with equal support, and it will call Bedrock-hosted Claude, Nova, or externally-hosted OpenAI and Gemini models. This is a deliberate strategic choice — AWS does not need to win the framework war to win the infrastructure layer beneath it, and by remaining agnostic it captures workloads regardless of which framework wins developer mindshare.

Strands Agents SDK, AWS's own open-source (Apache 2.0) agent framework, occupies a special position: it is the framework AWS itself uses to power AgentCore harness internally, but it is not required to use AgentCore, and AgentCore is not required to use Strands. This report treats them as a paired reference implementation because that pairing is how AWS's own samples, tutorials, and the harness are built.

### The AgentCore Service Map

As of June 2026, "AgentCore" refers to the following distinct, independently billed and independently adoptable services:

| Service | Status (June 2026) | GA Date / Milestone |
|---|---|---|
| Runtime | GA | GA since ~late 2025; quota increases through June 2026 |
| Gateway | GA | GA since 2025; Runtime-as-target GA in Q2 2026 |
| Identity | GA | GA since 2025 |
| Memory | GA | GA 2025; Episodic strategy added Dec 2025 |
| Code Interpreter | GA | GA since 2025 |
| Browser | GA | GA since 2025 |
| Observability | GA | GA since 2025; CloudWatch GenAI Observability tie-in Dec 2025 |
| **Policy** | **GA** | **March 3, 2026** |
| **Evaluations** | **GA** | **March 31, 2026** |
| **Optimization** | GA | ~May–June 2026 (recommendations, failure insights) |
| **Harness** | **GA** | **June 18, 2026** (preview since April 22, 2026) |
| **Registry** | **Preview** | ~April 2026, five regions |
| **Payments** | **Preview** | **May 7, 2026**, four regions |
| MCP Server hosting (via Runtime) | GA | Part of Runtime since 2025 |

A critical architectural distinction threads through the whole platform: **Gateway is the data plane** (it proxies and enforces policy on live traffic), while **Registry is the control plane** (it catalogs and governs resources at build/publish time). Confusing the two — for example, assuming Registry auto-indexes what Gateway serves — is a common early-adopter mistake documented by multiple practitioners in the April 2026 wave of Registry-preview write-ups.

## Part II — Runtime

### Isolation Model

AgentCore Runtime's foundational design decision is **one Firecracker microVM per session**, not per request and not a shared multi-tenant container pool. Firecracker is the same open-source VMM AWS uses for Lambda and Fargate; AWS states microVMs boot in under 125ms, which is what makes per-session hardware isolation economically viable at agent scale. Each microVM gets its own isolated CPU, memory, and filesystem. When a session ends, the entire microVM is terminated and its memory is sanitized — there is no reuse of session state across users, and a compromised agent process cannot observe or interfere with another session's memory, tool state, or execution context by design.

This is a stronger isolation boundary than the shared-container model most teams reach for by default (a single Fargate service or Lambda execution environment reused across many users' conversations), and it is the architectural reason AWS positions Runtime as suitable for regulated, multi-tenant workloads without additional per-tenant infrastructure.

### Session Lifecycle and Stickiness

A session is identified by a client-supplied or Runtime-generated `runtimeSessionId`. Subsequent calls using the same ID are routed ("stuck") to the same microVM via a session header, preserving in-memory state, environment variables, running processes, and filesystem content without the agent needing to reload context. This stickiness is **best-effort, not a correctness guarantee** — the microVM will be recycled on `maxLifetime` or `idleRuntimeSessionTimeout`, and AWS documentation and re:Post guidance are explicit that MCP servers hosted on Runtime must be built **stateless between individual HTTP requests**, externalizing any state that must survive a recycle event to AgentCore Memory, DynamoDB, Redis/Valkey, or S3. Relying on process-local RAM as anything other than a latency optimization is a documented anti-pattern.

### Cold Starts and Latency Engineering

An AWS re:Post deep-dive (Angelino, Arzhanov, Gaafar, Moeller — May 2026) decomposes Runtime startup latency and recommends: container image optimization, strategic prewarming pings, multiple endpoints for blue/green traffic shaping, and self-maintained warm pools. The warm-pool pattern is economically sound specifically because of AgentCore's consumption-based pricing — memory is billed separately and more cheaply than active compute time, so holding idle warm microVMs open is materially cheaper than the business cost of cold-start latency for latency-sensitive, high-traffic agents. Teams should monitor real traffic and right-size the warm pool per time-of-day rather than over-provisioning statically.

### Protocols, Versioning, and Endpoints

Runtime supports three inbound protocols: plain HTTP (REST request/response), MCP (Streamable HTTP, JSON-RPC, both stateless and stateful modes), and A2A (Agent-to-Agent). Every configuration change (container image, protocol, network settings) creates a new **immutable version**; a **DEFAULT endpoint** auto-updates to the newest version, while named endpoints (dev, staging, prod) can be pinned and repointed independently — giving zero-downtime rollback by simply repointing an endpoint alias, the same pattern as Lambda aliases/versions.

### Networking

By default Runtime deploys in **PUBLIC** network mode. **VPC mode** provisions AWS-managed ENIs inside customer-specified subnets (via the `AWSServiceRoleForBedrockAgentCoreNetwork` service-linked role), enabling private access to RDS, internal APIs, and on-prem systems via Direct Connect/VPN, without traversing the public internet. A May 2026 AWS Networking blog documents four progressively more locked-down patterns: (1) public endpoint, public egress; (2) VPC egress via ENI, public ingress; (3) PrivateLink ingress + VPC egress, blocking public ingress via a resource-based policy condition on `aws:SourceVpce`; (4) full isolation — no IGW/NAT at all, with every AWS service call routed through VPC endpoints. Pattern 4 is the correct target state for regulated workloads handling PII, PHI, or financial data.

### Pricing Model

Runtime is consumption-based: compute is billed only while active (not during LLM inference I/O wait, though session state is held), and separate, cheaper memory-holding charges apply for idle/warm microVMs. Direct code deployment incurs standard S3 storage costs; container deployment incurs standard ECR costs. A frequently cited industry estimate (Cloudvisor, May 2026) puts AgentCore infrastructure cost at roughly 10–30% of total agent cost at scale, with model inference (billed separately through standard Bedrock pricing) dominating the bill for most workloads — a moderate-traffic support agent (10k conversations/month) was estimated at $50–200/month infrastructure plus $200–800/month inference.

## Part III — Gateway

### What Gateway Actually Is

AgentCore Gateway is a fully-managed, protocol-translating **AI gateway** — not merely an "MCP proxy." It is the single, secure entry point through which agents reach three categories of downstream target:

- **MCP targets** (Lambda functions, OpenAPI specs, Smithy models, existing MCP servers, built-in connector templates such as Salesforce/Slack/Jira/Asana/Zendesk) are **aggregated** — Gateway acts as one virtual MCP server that merges the `tools/list` of every attached target into a single unified catalog, exposed to the client as one consolidated `tools/list` response.
- **HTTP targets** (other agents, A2A services, or an AgentCore Runtime agent added directly as a target) are **proxied directly**, without aggregation or protocol translation.
- **Inference targets** route LLM traffic across multiple model providers through one unified, model-based routing endpoint.

Gateway differs from a conventional **API Gateway** in that it natively speaks and translates *agent* protocols (MCP, A2A) rather than just REST/HTTP, and it differs from a generic **service mesh** in that its core function is protocol *aggregation and translation* into a single MCP surface plus **dual-sided OAuth enforcement**, not east-west traffic shaping between microservices. It differs from a bare **MCP proxy** in that it adds Cedar policy enforcement, Lambda interceptors, semantic tool search, and unified observability — a raw MCP proxy has none of these.

### The Dual-Sided Security Architecture

Gateway enforces authentication and authorization on **both sides** of every call:

**Inbound (client → Gateway).** Gateway acts as an OAuth **resource server**, validating tokens against a configured identity provider (Cognito, Okta, Auth0, Entra ID, or a custom OIDC provider). Supported inbound modes: OAuth (JWT) for token-based authorization, IAM (AWS SigV4) for AWS-identity-based authorization, `AUTHENTICATE_ONLY` (validate the token but delegate authorization to the target — required for token-passthrough patterns), or no authorization (dev/test only).

**Outbound (Gateway → target).** Eight supported patterns: (1) no authorization — explicitly discouraged; (2) IAM-based (SigV4) — the gateway service role signs requests, with AWS able to auto-provision this role and auto-attach least-privilege permissions per target added; (3) caller IAM credentials — Gateway assumes a role on behalf of the caller via the Federated Access Service (FAS), preserving the caller's identity in the signed request; (4) OAuth 2LO (client credentials) — pure machine-to-machine, no user in the loop; (5) OAuth 3LO (authorization code grant) — user-delegated access, requiring the Gateway to have been created with MCP protocol version 2025-11-25 or later and a registered return URL; (6) token exchange grant (On-Behalf-Of / OBO) — Gateway exchanges the inbound user's access token for a new, downstream-scoped token carrying both the user's and the agent's identity, so downstream services can enforce fine-grained authorization at every hop without re-prompting for consent; (7) token passthrough — the inbound token is forwarded unmodified (requires `AUTHENTICATE_ONLY` inbound mode) and the target validates it itself; (8) API key — AgentCore-generated keys for simple target auth.

Credentials for every outbound pattern are brokered and cached through **AgentCore Identity's Token Vault** — Gateway itself never persists long-lived secrets.

### Request Lifecycle

1. Client sends an MCP `tools/call` (or `tools/list`) request to the Gateway's single endpoint, bearing an inbound credential (JWT or SigV4).
2. Gateway validates the inbound credential against the configured authorizer.
3. If a **Lambda REQUEST interceptor** is attached, it runs next — this is where request enrichment happens: injecting tenant IDs, exchanging a bearer token for tenant-scoped credentials, adding geography/role context that downstream Cedar policy will evaluate.
4. If a **Policy engine** is attached, Cedar evaluates the (possibly-enriched) request: principal, action (mapped from the specific tool name), resource (the gateway ARN), and context (arbitrary input fields, including anything the interceptor injected). Default is deny; a matching forbid always wins over a matching permit.
5. On ALLOW, Gateway translates the MCP call into the target's native protocol — a Lambda Invoke, an OpenAPI HTTP call, a Smithy-modeled call, or a passthrough to another MCP server/agent — using the resolved outbound credential.
6. The target executes and returns a result.
7. If a **Lambda RESPONSE interceptor** is attached, it can filter the tool list dynamically or redact sensitive fields in the response before it reaches the client.
8. Every hop — auth decision, policy decision, interceptor invocation, target latency — streams to AgentCore Observability / CloudWatch.

### Semantic Tool Search

As the aggregated tool catalog behind a Gateway grows into the hundreds, stuffing every tool schema into the model's context window becomes wasteful and degrades tool-selection accuracy. Gateway ships a special built-in tool, `x_amz_bedrock_agentcore_search`, callable through the standard MCP `tools/call` operation, that performs semantic retrieval over the tool catalog so an agent can discover only the handful of tools relevant to its current task rather than being handed the entire catalog on every turn.

### Ingress Networking

A dedicated PrivateLink endpoint (`agentcore.gateway`) lets resources inside a customer VPC reach Gateway without traversing the public internet. Note the documented caveat: identity-provider round-trips for OAuth (token retrieval, consent redirects) and Gateway's own outbound calls to external MCP targets still require internet egress — PrivateLink secures the *ingress* path from caller to Gateway, not every downstream hop.

## Related

- [Deep Research Report (Part 2)](parts/18-agentcore-strands-deep-research-report-part2.md) — Policy, Registry, Harness
- [Deep Research Report (Part 3)](parts/18-agentcore-strands-deep-research-report-part3.md) — Identity, Memory, Browser & Code Interpreter, MCP server hosting
- [Deep Research Report (Part 4)](parts/18-agentcore-strands-deep-research-report-part4.md) — Strands Agents SDK deep dive, Observability
- [Deep Research Report (Part 5)](parts/18-agentcore-strands-deep-research-report-part5.md) — Security threat model, production architecture, release analysis
- [Deep Research Report (Part 6)](parts/18-agentcore-strands-deep-research-report-part6.md) — Roadmap prediction, adjacent roadmap signal, best practices, anti-patterns
- [Deep Research Report (Part 7)](parts/18-agentcore-strands-deep-research-report-part7.md) — Production readiness checklist, cost optimization, security hardening, resilience (stress testing, kill switch, circuit breakers, canary rollout, feature gates)
- [Deep Research Report (Part 8)](parts/18-agentcore-strands-deep-research-report-part8.md) — Resume workflow, failover, exception handling, human-in-the-loop, sampling, synthesis
- [Deep Research Report (Part 9)](parts/18-agentcore-strands-deep-research-report-part9.md) — Sources and glossary
