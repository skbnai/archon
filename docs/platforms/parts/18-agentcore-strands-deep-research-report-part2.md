---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, policy, registry, harness]
covers_version: "as of 2026-07-10"
---

> Continues from [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md), covering Policy, Registry, and Harness.

## Part IV — Policy

### Why Policy Exists

AWS's own security-blog framing (May 2026) is direct about the problem: an LLM's plan cannot be trusted to enforce its own constraints. System prompts and training-time alignment are bypassable via prompt injection or hallucination; hard-coded checks scattered through tool code are unauditable at scale. Policy's answer is to move authorization **entirely outside the agent and outside the LLM's context**, into the Gateway boundary, so that a compromised or manipulated agent cannot reason its way around a rule it cannot see or influence. Policy is enforced regardless of *how* the agent was prompted, jailbroken, or buggy — the enforcement point is structurally separate from the reasoning loop.

### Cedar: Why This Language

Policy is built on **Cedar**, AWS's open-source (and, as of early 2026, CNCF-hosted) authorization policy language — the same language behind Amazon Verified Permissions. Cedar was chosen for three properties: it is human-readable, it is machine-analyzable via automated/formal reasoning, and policies are schema-validated at authoring time. AgentCore auto-generates the Cedar schema from each Gateway's actual tool definitions, which is the key differentiator from generic Verified Permissions (where the developer must hand-author the schema and call authorization APIs themselves). Policy in AgentCore is purpose-built for exactly one enforcement point — the Gateway's MCP request path — with agent-specific features (partial-evaluation tool filtering, natural-language authoring) built in.

### Evaluation Semantics

- **Default deny.** If no policy matches a request, the result is DENY.
- **Forbid overrides permit.** If any forbid policy matches, the result is DENY even if a permit also matches.
- **At least one permit required.** ALLOW requires at least one matching permit and zero matching forbid policies.
- Evaluation happens **per tool call** (`tools/call`), distinct from `tools/list` — a caller can be permitted to *see* a tool exists without being permitted to *invoke* it, and vice versa in some designs.

A minimal example (paraphrased from AWS's getting-started guide) permits a caller tagged with a specific username to invoke a refund tool only when the requested amount is below a threshold — the amount check happens against `context.input.amount`, a field the Gateway injects automatically from the tool call's actual arguments at evaluation time.

### Neuro-Symbolic Policy Authoring

Administrators can write Cedar directly, or describe a rule in plain English (e.g., "allow callers with manager scope to use `markdown_to_email`") and have it formalized automatically. AWS's security blog describes this as a **neuro-symbolic feedback loop**: an LLM proposes candidate Cedar from the natural-language description, and **Cedar Analysis** — a symbolic, mathematical reasoning engine — validates the candidate against the gateway's schema and checks the *entire policy set* holistically for conflicts, redundancy, overly-permissive grants, and overly-restrictive grants, failing the operation with a description of the problem if issues are found. This control-plane analysis runs every time a policy is attached, not just at natural-language authoring time.

Practitioner guidance (multiple independent write-ups, May 2026) converges on treating natural-language generation as a **draft**, not a final artifact: always inspect the generated Cedar against the real Gateway schema before enforcing, and prefer specific, concrete natural-language requirements ("allow refund:write callers to process refunds when amount is less than 500") over vague ones ("make refunds safe"), since vague requirements produce vague — and often over-broad — Cedar.

### Rollout Discipline: LOG_ONLY → ENFORCE

Every policy engine attaches to a Gateway in one of two modes:

- **LOG_ONLY** — every request is evaluated and the decision is logged to CloudWatch, but nothing is blocked. This is the recommended starting mode: it lets a team validate that real production traffic maps to the policy set the way they expect before any enforcement risk is taken.
- **ENFORCE** — decisions are actually applied; unpermitted calls are rejected (commonly surfaced as an MCP-level error / HTTP 403), and every decision is still logged for audit.

The consistent practitioner rollout pattern: start LOG_ONLY, inspect what *would* have been denied, fix tool-name/claim-mapping/schema mismatches, then flip to ENFORCE only once the denied-case set is fully understood and expected.

### Policy + Lambda Interceptors: Composability, Not Competition

An important architectural nuance from AWS's June 2026 blog on combining the two mechanisms: **REQUEST interceptors always run before Cedar policy evaluation.** This ordering is intentional — interceptors are the right tool for anything *dynamic* (external lookups, token exchange, injecting per-tenant context that isn't in the raw request), while Cedar is the right tool for anything expressible as a *static logical rule* over the resulting enriched context. AWS documents three composable design patterns:

1. **Policy-only** — role-based tool restriction via straightforward permit/forbid rules. Best when authorization is a pure function of identity claims already present in the token.
2. **Interceptor-only** — dynamic credential exchange (e.g., swapping a JWT for tenant-scoped IAM credentials, an "act-on-behalf" pattern) with no static rule needed.
3. **Combined** — an interceptor enriches the request with attributes an external system must supply (e.g., the caller's data-residency region from a lookup service), and Cedar enforces the resulting rule (e.g., "EU-tagged callers may not invoke US-only tools"). RESPONSE interceptors additionally can filter which tools appear in `tools/list` per-caller and redact sensitive fields from tool results — dynamic response shaping that Cedar's request-time evaluation cannot do.

The design guidance AWS gives: use interceptors for everything inherently dynamic and Cedar for everything expressible as a logical condition; treat them as a pipeline, not overlapping controls.

### Relationship to IAM

IAM and Policy are complementary layers answering different questions. IAM answers "is this AWS principal (the Gateway's execution role) allowed to invoke this Lambda function at all?" Policy answers "is this specific end-user, acting through this agent, allowed to call `process_refund` with `amount=2000` right now?" Removing IAM scoping under the assumption that "Policy handles authorization now" removes an entire independent layer of defense-in-depth — the two must both be correctly configured, not treated as substitutes.

### GA Timeline and Guardrails Integration

Policy reached GA on **March 3, 2026**. By the April–June wave, AWS integrated **Bedrock Guardrails directly into the Policy/Gateway layer**: Guardrails now evaluates outputs from *already-authorized* agent actions and inputs to gateway targets for prompt-injection attempts, harmful content, and sensitive-data exposure — critically, this evaluation runs at the Gateway layer, **outside the agent's own context window**, so the agent cannot reason around a check it never sees. Because every tool and every context source is required to route through the Gateway, AWS's framing is that *every new agent capability is automatically governed by the same security layer* without additional integration work per tool. AWS has also signaled (as "coming soon" in the same announcement) that third-party detection signals — Check Point, Zscaler, Rubrik, Netskope, and SentinelOne were named — will be pluggable into the same policy evaluation pipeline.

## Part V — Registry

### Purpose and Positioning

AgentCore Registry is a fully managed, serverless **catalog and governance layer** — the control-plane counterpart to Gateway's data-plane role. It provides centralized discovery, versioning, approval workflows, and search across four resource categories: **Agents**, **MCP Tools**, **Skills**, and **Custom Resources** (arbitrary JSON for anything that doesn't fit the other three). It entered public preview around April 2026 in five regions (us-east-1, us-west-2, ap-southeast-2, ap-northeast-1, eu-west-1), free during preview, with usage-based "Net Records" pricing planned at GA.

### The Four-Persona IAM Model

Registry is architecturally unusual within AgentCore for explicitly separating four distinct personas into distinct IAM policies:

- **Administrator** — owns registry infrastructure: creates/configures registries, sets authentication mode (IAM or JWT), wires EventBridge for approval automation, and decides whether auto-approval is enabled (documented as *always off* by default in production-oriented guidance).
- **Publisher** — submits new records for approval.
- **Approver** — reviews and approves/rejects submissions (a distinct persona from Administrator, enabling segregation of duties).
- **Consumer** — discovers and consumes registry records (search, retrieve) with no write/mutate permissions; practitioner guidance recommends running Consumer-side MCP proxies with a `--read-only` flag to structurally prevent accidental writes.

### What Registry Deliberately Does Not Do (Preview Limitations)

Multiple independent practitioner write-ups (April 2026) converge on the same gap list, worth treating as a due-diligence checklist before depending on Registry in a production governance program:

- **No auto-indexing.** Deploying an agent to Runtime does not automatically publish it to Registry — registration is a manual, explicit act.
- **No cross-account/cross-team federation.** Each AWS account has its own independent registries; there is no native mechanism to expose a platform-team's registry to squad-level accounts.
- **No SemVer-aware version diffing.** Registry supports a `recordVersion` field but does not compute or enforce semantic-version compatibility between versions.
- **No Terraform or CloudFormation support as of April 2026** — provisioning is Console/CLI/boto3/API only, which several teams noted as a blocker for full infrastructure-as-code workflows.
- The **Registry ID** is not surfaced as a labeled, copyable field in the console — it must be extracted from the resource ARN, a minor but repeatedly-noted UX friction point.

### Registry vs. Gateway — the Control-Plane / Data-Plane Split

The clearest mental model documented across multiple AWS-partner blogs: Gateway is the **traffic layer** — it proxies and enforces policy on live invocations. Registry is the **build-time layer** — it catalogs what exists, who owns it, and whether it has been vetted, but it does not sit in the request path at runtime. A common integration pattern emerging in mid-2026 write-ups is using Registry purely as a **metadata catalog for "skills"** (name, description, instructions, allowed-tools list) that an agent loads dynamically per-session — keeping the actual tool implementations in-process for latency, while decoupling skill *content* (editable without a redeploy) from the agent *runtime* (which only needs to change when the loading mechanism itself changes). One documented migration (a 16-skill AWS governance agent) reported moving from hardcoded, always-loaded skill descriptions in the system prompt to Registry-backed dynamic loading, cutting prompt bloat and enabling live skill edits without a container rebuild — completed end-to-end, per that team's account, in about an hour using AI-assisted planning.

## Part VI — Harness

### What Harness Is, and Isn't

AgentCore harness is a **fully managed agent orchestration abstraction built on top of Runtime**, internally powered by the Strands Agents framework. Where Runtime asks a developer to write the agent loop and ship a container, Harness asks only for **configuration**: a model, a system prompt, and a set of tools, via two API calls — `CreateHarness` (define) and `InvokeHarness` (run). AWS's own framing at GA: "two API calls to a production-grade agent." No orchestration code, no Dockerfile, no ECR push is required, though an execution role, Bedrock model access, and (for cross-model use) IAM permissions on the harness/runtime action families are still needed.

Harness entered **public preview on April 22, 2026** and reached **GA on June 18, 2026** at the AWS New York Summit.

### What GA Auto-Provisions

At GA, omitting a memory ARN on `CreateHarness` auto-provisions a managed AgentCore Memory resource with sensible defaults: **SEMANTIC + SUMMARIZATION** strategies, 30-day short-term event expiry, AWS-owned encryption, and multi-tenant namespace isolation keyed on `actorId` by default. GA also added: the AWS-curated skills catalog behind a one-toggle setup; built-in evaluations and A/B testing with statistical-significance reporting; unified observability auto-traced to CloudWatch; immutable versioning with named endpoints and instant rollback (the same version/endpoint model as Runtime); and **export to Strands code** when configuration alone is no longer sufficient and full control is needed (export to the Claude Agent SDK was announced as "coming soon" at GA).

### Multi-Model, Mid-Session Provider Switching

A default model is set at `CreateHarness` time; any individual `InvokeHarness` call can override it to one of four provider families — `bedrock` (any Bedrock-hosted model: Claude, Nova, Llama, DeepSeek, Qwen, Kimi, MiniMax, Cohere, Mistral, and GPT-5.5/GPT-5.4 via Bedrock Mantle), `openAi` (direct OpenAI API), `gemini` (direct Google Gemini), or `liteLlm` (any LiteLLM-supported provider). The documented and independently-verified behavior that distinguishes this from a naive "swap the model ID" implementation: **conversation history and message context carry across the swap**. A session can plan its approach with one model, execute a step with a second, and summarize with a third, without losing continuity — independent verification (a June 2026 hands-on write-up) confirmed this by swapping Claude Sonnet 4.6 for gpt-oss-120b mid-conversation and observing that context (including a specific detail seeded earlier in the session) survived the swap.

### Built-In Tools and the Inline-Function Escape Hatch

Every Harness session ships two always-available built-in tools — `shell` and `file_operations` — running inside an isolated environment with its own filesystem, giving the agent a working directory it can read from and write to safely. Beyond that, Harness supports five configurable tool types. The most architecturally significant is the **inline function**: it lets Harness pause execution mid-turn (streaming a `stopReason: "tool_use"` event back to the caller), hand control to the caller's own application code, and resume once the caller returns a tool result. Because the inline function's code runs in the **caller's** environment — not inside Harness's managed compute — this is the sanctioned pattern for giving an agent access to resources behind a corporate firewall (internal databases, on-prem APIs) without exposing them to AgentCore's compute layer at all.

### Positioning Against Runtime and Third-Party "Managed Agent" Offerings

A widely-cited comparison ("Latent Thoughts," April 2026) frames the choice as: pick **Harness** when the fastest path to a working agent matters more than custom control (Harness *inverts* the deployment model — you deploy configuration, not code); pick **Runtime** directly when you need full control over the orchestration loop, custom middleware, or a framework Harness doesn't wrap; and treat "Bedrock Managed Agents, powered by OpenAI" (a separate, OpenAI-specific offering combining OpenAI's own harness with AWS infrastructure) as a narrower alternative scoped to teams committed to OpenAI's frontier models specifically. One functional gap noted as of the April 2026 preview period: unlike Runtime, Harness was at that time reachable only via the AWS API/SDK/CLI (`InvokeHarness`) — it did not yet expose an HTTP, MCP, or A2A endpoint the way Runtime does; whether this expands is an open roadmap question addressed in Part XVI.

### Pipeline and CI/CD Integration

Harness integrates directly into **AWS Step Functions** via an `InvokeHarness` state, letting a harness-defined agent participate as a step inside a larger orchestrated pipeline without custom Lambda glue code.

## Related

- [Deep Research Report](../18-agentcore-strands-deep-research-report.md) — executive summary, platform foundations, Runtime, Gateway
- [Deep Research Report (Part 3)](18-agentcore-strands-deep-research-report-part3.md) — Identity, Memory, Browser & Code Interpreter, MCP server hosting
