---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report (Part 3)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, identity, memory, code-interpreter, mcp]
covers_version: "as of 2026-07-10"
---

> Continues from [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md), covering Identity, Memory, Browser & Code Interpreter, and MCP server hosting on Runtime.

## Part VII — Identity

### Core Model: Delegation, Not Impersonation

AgentCore Identity's foundational design principle is that an **agent authenticates as itself while carrying verifiable user context** — it does not impersonate the end user. This is what AWS's identity-chaining documentation calls separating *identity* from *delegation* and then combining them only within defined boundaries. The chain, end to end:

1. A human user authenticates through an existing IdP (Cognito, Okta, Entra ID, Auth0) and the client application receives a user JWT.
2. The client invokes the agent, passing the user JWT as inbound auth.
3. AgentCore Runtime/Gateway validates the JWT and extracts user identity context.
4. AgentCore Identity issues a **Workload Access Token** — an internally AWS-signed token representing *both* the agent's own workload identity and the user context, without simply forwarding the raw user token.
5. When the agent needs a downstream, non-AWS resource (Google Drive, Slack, GitHub, Salesforce), it presents the Workload Access Token to the **Token Vault**, which either returns a cached, previously-consented provider token or orchestrates a fresh OAuth consent flow (3LO), then caches the result bound to the specific agent+user pair.
6. The agent uses the vaulted, scoped provider credential to call the external resource — never the user's raw session credential, and never a shared system-wide credential.

Every hop preserves both identities and produces an audit trail; if the user later revokes consent, the Token Vault blocks further use of that provider credential immediately.

### Components

- **Agent Identity Directory** — a unified directory of agent/workload identities, each with an ARN, metadata (name, OAuth return URLs, timestamps), managed centrally. Agents are first-class security principals, not applications masquerading as users.
- **Agent Authorizer** — validates whether a caller (user or service) may invoke a given agent at all (the inbound check).
- **Resource Credential Provider** — stores the configuration needed to obtain credentials for a specific downstream resource server.
- **Resource Token Vault** — encrypted at rest and in transit, stores OAuth access/refresh tokens, client credentials, and API keys; the single source of truth an agent queries at invocation time rather than embedding secrets in code.

### Inbound vs. Outbound Auth

**Inbound Auth** governs who may invoke a Runtime, Gateway, or tool — configured as IAM (SigV4) or JWT (OAuth/OIDC). A single Runtime supports *either* SigV4 *or* JWT inbound auth, not both simultaneously; teams needing both must create separate Runtime versions/endpoints. **Outbound Auth** governs how the agent/Gateway reaches downstream, non-AWS resources — via an API key or an OAuth client (2LO or 3LO), referenced by ARN in agent/tool code.

### Workload Identity as a Trust Boundary (Confused-Deputy Prevention)

Each deployed Runtime automatically provisions a corresponding workload identity directory keyed on the Runtime's own ARN. This directory enforces a **callback-URL whitelist** for OAuth redirects — only URLs explicitly registered against that specific workload can complete an authorization-code flow on its behalf, preventing a malicious or misconfigured client from hijacking the redirect to exfiltrate an authorization code. Separately, AWS's guidance is explicit and repeated across multiple official and community sources: execution-role trust policies **must** include `aws:SourceArn`/`aws:SourceAccount` conditions scoped to the specific Gateway or Runtime ARN. Without this condition, *any* AgentCore Runtime in *any* AWS account could in principle assume the role via the shared `bedrock-agentcore.amazonaws.com` service principal — a textbook confused-deputy vulnerability that AWS's own samples explicitly guard against.

### Federation

Identity natively integrates with Cognito, Okta, and Microsoft Entra ID as inbound identity providers, avoiding a re-platforming of existing enterprise identity. A practical May 2026 guide (Arpan Das) documents the "configure once, enforce everywhere" pattern: a single Entra App Registration and a single AgentCore OAuth Client entry govern both MCP-server (tool) invocations and full Agent Runtime invocations, differentiated only by which OAuth 2.0 grant type applies to a given caller pattern (a human via an MCP client, a pipeline invoking an autonomous agent, or a chained multi-agent scenario needing identity propagation).

**Cross-cloud limitation, independently documented (Descope, June 2026):** AgentCore Identity, like its Azure and GCP counterparts, is tightly coupled to its own cloud. A non-AWS agent can register against AgentCore, but still ultimately needs AWS credentials to participate — and there is no AWS-native mechanism to unify agent identity across AWS, Azure AI Foundry, and Vertex AI simultaneously. Third-party "agentic identity hub" vendors (Descope is cited as one example) are positioning specifically to fill this cross-cloud identity-federation gap, which is a legitimate architectural gap for genuinely multi-cloud agent estates rather than a vendor-created problem.

### Identity Propagation Across Multi-Agent Chains

When a supervisor agent delegates to a specialist agent, the user's identity claims travel with the delegated request. Combined with Gateway-enforced Cedar policy, this means a monitoring/specialist agent several hops downstream can still only access the original user's data — the cryptographic binding between workload identity and user identity holds regardless of how many agents sit in the chain, which is the property that makes multi-agent architectures auditable rather than an identity-laundering risk.

## Part VIII — Memory

### Two-Tier Model

AgentCore Memory splits into **short-term memory** (the raw, turn-by-turn conversation buffer for a single session — every message, unprocessed) and **long-term memory** (persistent, cross-session, semantically searchable knowledge, produced asynchronously by one or more configurable **strategies**). This distinction carries an important timing contract that is easy to get wrong: long-term memory is populated by an *asynchronous* extraction pipeline that runs after short-term events are recorded, not synchronously mid-session — a strategy is not available to influence the *current* turn the way short-term context is.

### Built-In Long-Term Strategies

AgentCore ships four built-in strategies, each with a distinct retrieval contract:

- **Semantic** — extracts discrete facts and knowledge; retrieval is pure relevance-ranked semantic search over embeddings. Best for "what does the agent know about X."
- **User Preference** — captures stable behavioral signals ("prefers window seats," "budget-conscious"). Only processes USER/ASSISTANT-role messages.
- **Summary** — produces XML-structured, `<topic>`-tagged condensed narratives of a session; unlike Semantic and User Preference, Summary processes *all* message roles, capturing tool-call context too.
- **Episodic** (added Q4 2025, expanded through 2026) — captures not just facts but *how the agent arrived at them*: goal, reasoning steps, actions taken, outcome, and a reflection. This is the strategy AWS's VP of AgentCore, David Richardson, described publicly as designed to answer questions like a returning traveler's preferred seat or price range without needing custom instructions — the agent recalls relevant episodes automatically when retrieval conditions are met, rather than requiring the developer to hand-code "remember this."

Teams can further customize any built-in strategy's extraction/consolidation system prompt or swap its underlying model while keeping the output schema fixed, or build a fully **self-managed strategy** with custom extraction, consolidation, and ingestion logic (billed differently from built-in strategies).

### Extraction Pipeline

When new short-term events are recorded, an asynchronous pipeline invokes an LLM to identify meaningful information matching the configured strategy or strategies, producing structured memory records in a predefined schema. Strategies run in **parallel** — multiple memory types process independently and do not block one another, which keeps the pipeline's latency profile flat as more strategies are added. Retrieval (`RetrieveMemoryRecords`) performs semantic search via embeddings automatically; unlike some competing memory frameworks that expose explicit recency/importance/relevance weighting knobs, AgentCore's approach treats relevance as embedding-driven and handles recency/importance implicitly inside consolidation.

### Governance, TTL, and Multi-Tenant Isolation

Short-term event expiry is configurable per Memory resource (a 7-day default is common in samples; Harness's GA-provisioned default is 30 days). Namespace templates key long-term memory to an `actorId`, giving each user/tenant a structurally isolated memory space — Alice's preferences are never retrievable in Bob's session, even across entirely different session IDs, because retrieval is scoped by namespace, not merely filtered post-hoc.

## Part IX — Browser and Code Interpreter

### Browser Tool

AgentCore Browser is a serverless, cloud-hosted browser automation service purpose-built for agent-driven web interaction (form filling, data extraction, QA testing, CAPTCHA-heavy flows). Architecturally it shares Runtime's session model: each browser session is isolated (VM-level sandboxing), auto-scales without infrastructure management, and supports VPC connectivity for reaching internal web applications privately. Observability is first-class — AWS documents live session viewing, CloudTrail logging, and full session replay for compliance review and troubleshooting, positioning Browser as auditable by design rather than a black box a human must trust blindly.

### Code Interpreter: Design Intent

Code Interpreter gives an agent a secure, isolated sandbox for executing agent-generated code — critical because arbitrary code execution driven by an LLM is one of the highest-consequence capabilities an agent can be granted. AWS's architecture: each session runs in its own isolated sandbox (backed, like Runtime, by ephemeral hardened microVMs), with pre-built multi-language runtimes, large-file support (up to 100MB inline, 5GB via S3), and CloudTrail logging. Default execution time is 15 minutes, extendable to 8 hours for long-running data-processing workloads. Sandboxes support session-level customization (compute resources, available libraries) and two network modes: **Sandbox** (advertised as complete isolation, no external access) and **Public** (internet-connected).

### Independent Security Findings — A Material Correction to the Isolation Claim

This is one of the most consequential findings in this report, because it directly bears on any threat model that assumes Code Interpreter's "Sandbox" mode provides *complete* network isolation.

- **Palo Alto Networks Unit 42 (April 30, 2026)** demonstrated that Sandbox mode, originally documented by AWS as providing "complete isolation with no external access," in fact permitted DNS resolution — an operative gap, since DNS queries are themselves a viable, low-bandwidth data-exfiltration channel (DNS tunneling). AWS updated its documentation to clarify that Sandbox mode allows DNS resolution by design, rather than treating it purely as a bug.
- **BeyondTrust Phantom Labs (originally published March 16, 2026, updated April 22, 2026)** independently disclosed the same underlying gap — Sandbox mode's DNS resolution enabling DNS-based command-and-control/exfiltration — and reported that, following public disclosure, **AWS did subsequently remediate the DNS-exfiltration vector specifically** (the update notes DNS-based exfiltration is "no longer possible" as of the April 22 update). BeyondTrust's practical guidance for teams that had assumed Sandbox mode meant complete isolation: inventory all Code Interpreter instances and their network modes; scan for prompt-injection vectors that could manipulate code sent to the interpreter; apply Guardrails on inputs as a second layer; and — the clearest structural fix — **migrate genuinely sensitive workloads to VPC-only mode**, which AWS states is the only mode providing complete network isolation and full control over DNS resolution.
- **Sonrai Security (March 25, 2026)** took the finding a step further: even in Sandbox mode, the interpreter's IAM role credentials remained reachable and abusable via access to a subset of AWS services (notably S3) that did not require external network access to reach — meaning "no external network access" did not, in Sonrai's testing, equate to "no ability to abuse the role's AWS permissions." Sonrai's conclusion: network-mode isolation and IAM-permission scoping are two independent controls, and a team that hardens one while assuming it also hardens the other has a false sense of security.

**Threat-model implication:** "Sandbox mode" should not, by itself, be treated as a sufficient boundary for code execution against untrusted or adversarially-influenced input (e.g., code whose content or targets were partly shaped by a prompt-injected instruction). The two concrete architectural mitigations independent researchers converge on are (1) **VPC-only network mode** for any Code Interpreter session handling sensitive workloads, and (2) **least-privilege, tightly-scoped IAM execution roles** for the interpreter specifically — never reuse a broadly-privileged role across the interpreter and other AgentCore primitives.

## Part X — MCP Server Hosting

### Hosting MCP Servers on AgentCore Runtime

AgentCore Runtime can host a developer's own MCP server as a managed, scaling endpoint — distinct from Gateway, which *aggregates and translates* existing APIs/Lambdas into MCP tools. When a Runtime is configured for the MCP protocol, the platform expects the container to expose `0.0.0.0:8000/mcp`, matching the default path most official MCP SDKs use out of the box. Runtime supports both **stateless** (`stateless_http=True`, the recommended default for basic tool servers) and **stateful** (`stateless_http=False`, required for elicitation, LLM-generated sampling, or progress notifications) streamable-HTTP modes; in either mode, Runtime auto-injects an `Mcp-Session-Id` header on any request lacking one, so clients can maintain continuity to the same session.

**The critical operational caveat, independently confirmed by multiple practitioners and AWS's own re:Post guidance:** AgentCore does **not** guarantee sticky routing of every individual HTTP request to one specific container instance under horizontal scale-out — session affinity via `runtimeSessionId` is a best-effort optimization, not a correctness mechanism. Any MCP server design that depends on in-process RAM for protocol-level session state will break unpredictably once traffic triggers scaling or a microVM recycle. The only correct architecture externalizes state — AgentCore Memory, DynamoDB, Redis/Valkey, or S3 are the documented options — and treats the `Mcp-Session-Id`/`runtimeSessionId` purely as a routing hint, never as a durability guarantee.

Both IAM (SigV4) and OAuth/Cognito authentication work out of the box for Runtime-hosted MCP servers, and the same Gateway-fronting pattern available for HTTP agents (adding a Runtime as a Gateway HTTP target) applies to MCP-protocol Runtimes as well — letting a team put Cedar policy, Guardrails, and unified observability in front of a hand-written MCP server without changing the server's own code.

## Related

- [Deep Research Report](../18-agentcore-strands-deep-research-report.md) — executive summary, platform foundations, Runtime, Gateway
- [Deep Research Report (Part 2)](18-agentcore-strands-deep-research-report-part2.md) — Policy, Registry, Harness
- [Deep Research Report (Part 4)](18-agentcore-strands-deep-research-report-part4.md) — Strands Agents SDK deep dive, Observability
