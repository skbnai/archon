---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report (Part 9)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report-part9
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, sources, glossary]
covers_version: "as of 2026-07-10"
---

> Continues from [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md) and [Part 8](18-agentcore-strands-deep-research-report-part8.md), closing out Part XXIII (Keeping the Agent Live) with Sampling and the full-stack Synthesis, then the report's Sources and Glossary appendices.

## Part XXIII — Keeping the Agent Live (concluded)

### Sampling

"Sampling" means two unrelated things in this stack, and both matter operationally:

**MCP protocol sampling (`sampling/createMessage`)** is a first-class MCP capability, distinct from tools/resources/prompts, that lets an **MCP server** request an LLM completion **from the client** — reversing the normal request direction. A code-review MCP server, for instance, can ask the client's LLM to summarize a diff mid-tool-call without the server holding its own model credentials; the client retains full control over model selection and access, and the protocol's human-in-the-loop design gives the user two explicit checkpoints — approve/edit the outbound prompt before it reaches the LLM, and approve/edit the completion before it's returned to the server. A draft protocol revision under discussion as of mid-2026 (referenced in spec-tracking commentary as version-dated "2026-07-28") proposes an `InputRequiredResult` mechanism that would let a `tools/call` pause mid-flight for either an elicitation or a sampling request and resume later by re-issuing the call with the gathered answers plus an opaque, client-echoed `requestState` — explicitly designed so a stateless server instance can resume the interaction without holding a connection open, which is directly relevant to the Runtime statelessness discipline covered in Part 3. Treat this as an emerging capability to watch, not a currently-guaranteed one.

**Observability trace sampling** is the unrelated, cost-control meaning: capturing telemetry for only a subset of requests to bound instrumentation overhead and CloudWatch/X-Ray ingestion cost at scale. Documented guidance converges on an environment-dependent default: **100% trace sampling in development** (full visibility while iterating), stepping down to **adaptive sampling in production** — CloudWatch Application Signals' adaptive sampling, or a fixed ratio such as 1-in-10 with 100%-on-error as a common independently-recommended pattern, so that every *failed* request is still fully captured even when most successful ones are not. Two AWS-specific mechanics worth noting: **X-Ray Trace Indexing only indexes 1% of spans as searchable trace summaries by default** even when full spans are ingested (a distinct dial from raw ingestion sampling, and one teams commonly discover only after failing to find a specific trace in the console), and **CloudWatch Transaction Search must be explicitly enabled once per account per Region** before AgentCore spans appear in the GenAI Observability dashboard at all — an easy-to-miss one-time setup step, not an ongoing sampling decision.

### Synthesis: The Full "Keep It Live" Stack

Read top-to-bottom, these mechanisms form a layered resilience stack, each layer catching what the one above it misses:

1. **Governance (pre-execution):** Cedar Policy in ENFORCE mode — blocks disallowed actions before they ever reach a tool.
2. **Circuit breaking (mid-execution, automated):** Lambda-interceptor-fed counters + Cedar budget rules, or a third-party overlay — trips on threshold breach without waiting for a human.
3. **Kill switch (mid-execution, manual/emergency):** `StopRuntimeSession` for a single session; a pre-staged IAM emergency-deny for a stuck session; your own session registry for fleet-wide visibility AgentCore does not natively provide.
4. **Human-in-the-loop (mid-execution, judgment-requiring):** hook, tool-context, Step Functions, or MCP elicitation — matched to latency and ownership requirements (Part 8).
5. **Exception discipline (per-call):** the five-way taxonomy in Part 8, so retry logic, credential refresh, and business-rule denials never get routed through the same generic handler.
6. **Progressive rollout (change management):** configuration-bundle or target-based A/B testing with statistical-significance gating before every promotion (Part 7).
7. **Load/regression testing (pre-change validation):** batch Evaluations in CI/CD, plus concurrency-focused load testing against known quota ceilings, before a change ever reaches the A/B stage (Part 7).
8. **Observability (continuous, underlying everything above):** OTEL traces feeding both CloudWatch and a secondary platform, sampled appropriately for environment and cost, with failure-insights continuously mining for the silent failures no exception handler will ever catch.

No single AgentCore service in isolation delivers "keep the agent live" — it is the composition of Policy, Gateway interceptors, Runtime's session/ping/async-task primitives, Optimization's A/B testing, Step Functions' callback pattern, and a small amount of platform-team-owned glue (a session registry, a pre-staged emergency-deny policy, a circuit-breaker Lambda) that AgentCore does not yet provide natively. Architects should budget for that glue explicitly rather than assuming it ships with the platform.

## Appendix A — Sources

This report is grounded in the following categories of publicly available evidence gathered via web search in July 2026: AWS official documentation (docs.aws.amazon.com/bedrock-agentcore), AWS Machine Learning, Security, Networking, and AWS News blogs, AWS re:Invent 2025 and AWS Summit New York (June 17, 2026) announcements, the strands-agents GitHub organization and its published SDK documentation (strandsagents.com), independent security research from Palo Alto Networks Unit 42, BeyondTrust Phantom Labs, and Sonrai Security, and practitioner/analyst write-ups from AWS Heroes, AWS Builder Center, Arize AI, Weights & Biases, DeepWiki (awslabs/amazon-bedrock-agentcore-samples), and multiple independent cloud-architecture blogs (hidekazu-konishi.com, clawaws.com, Cloudvisor, Xebia, dev.to contributors) current as of late June–early July 2026. Facts drawn from AWS marketing/keynote claims not yet independently verified are flagged explicitly in-text as such (notably in Part 6 and the roadmap-adjacent sections); all other claims are drawn from official documentation, release notes, or independently reproduced/verified research.

## Appendix B — Glossary

**2LO / 3LO** — Two-legged / three-legged OAuth: machine-to-machine client-credentials grant vs. user-delegated authorization-code grant.

**A2A** — Agent-to-Agent protocol, for direct agent-to-agent communication and discovery.

**Cedar** — AWS's open-source, CNCF-hosted authorization policy language, used by both Amazon Verified Permissions and AgentCore Policy.

**Firecracker** — The open-source microVM virtual machine monitor underlying Runtime, Browser, Code Interpreter, Lambda, and Fargate isolation.

**MCP** — Model Context Protocol, the open standard for connecting agents to external tools and data sources.

**OBO** — On-Behalf-Of token exchange; Gateway exchanges an inbound user token for a downstream-scoped token carrying both user and agent identity.

**OTEL / ADOT** — OpenTelemetry / AWS Distro for OpenTelemetry, the instrumentation standard underlying AgentCore Observability.

**Workload Identity** — An agent/Runtime's own first-class security identity, distinct from, and combined with, but never substituting for, the end user's identity.

## Related

- [Deep Research Report](../18-agentcore-strands-deep-research-report.md) — executive summary, platform foundations, Runtime, Gateway
- [Deep Research Report (Part 2)](18-agentcore-strands-deep-research-report-part2.md) — Policy, Registry, Harness
- [Deep Research Report (Part 3)](18-agentcore-strands-deep-research-report-part3.md) — Identity, Memory, Browser & Code Interpreter, MCP server hosting
- [Deep Research Report (Part 4)](18-agentcore-strands-deep-research-report-part4.md) — Strands Agents SDK deep dive, Observability
- [Deep Research Report (Part 5)](18-agentcore-strands-deep-research-report-part5.md) — Security threat model, production architecture, release analysis
- [Deep Research Report (Part 6)](18-agentcore-strands-deep-research-report-part6.md) — Roadmap prediction, adjacent roadmap signal, best practices, anti-patterns
- [Deep Research Report (Part 7)](18-agentcore-strands-deep-research-report-part7.md) — Production readiness checklist, cost optimization, security hardening, stress testing, kill switch, circuit breakers, canary rollout
- [Deep Research Report (Part 8)](18-agentcore-strands-deep-research-report-part8.md) — Feature gates, resume workflow, failover, exception handling, human-in-the-loop
