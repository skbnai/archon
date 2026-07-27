---
title: "Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report (Part 7)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-strands-deep-research-report-part7
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, production-readiness, cost-optimization, resilience]
covers_version: "as of 2026-07-10"
---

> Continues from [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md), covering the production readiness checklist, cost optimization guide, security hardening summary, and the first half of operational resilience (stress testing, kill switch, circuit breakers, canary rollout).

## Part XX — Production Readiness Checklist

- [ ] Every Gateway has an explicit inbound authorization mode configured (never "no authorization" outside dev/test)
- [ ] Every outbound target uses a scoped credential pattern (2LO/3LO/OBO/IAM), never "no authorization"
- [ ] Every execution-role trust policy includes `aws:SourceArn`/`aws:SourceAccount` conditions
- [ ] Policy engine has completed a LOG_ONLY validation window against real traffic before ENFORCE cutover
- [ ] Cedar policy set has passed Cedar Analysis with no unresolved conflicts/redundancies
- [ ] Bedrock Guardrails attached at the Gateway layer for prompt-injection and sensitive-data-exposure screening
- [ ] Code Interpreter sessions handling sensitive data run in VPC-only network mode with a dedicated, least-privilege execution role
- [ ] MCP servers hosted on Runtime externalize all protocol-level session state (no reliance on in-process RAM)
- [ ] Strands hot-reload is disabled/absent in the deployed container
- [ ] Memory short-term event expiry and long-term strategy selection are deliberate choices, documented per use case
- [ ] Multi-region deployments have an explicit, tested Memory and Registry state-replication or resynchronization plan
- [ ] OTEL export is configured to both CloudWatch and at least one secondary trace-debugging platform for engineering-facing visibility
- [ ] Failure-insights/continuous-monitoring is enabled to catch silent (no-error-signal) behavioral regressions
- [ ] A documented incident-response playbook exists specifically for prompt-injection and tool/MCP-poisoning scenarios (see Part XXII)
- [ ] Registry entries for all production agents/tools have gone through the Approver persona's review, with auto-approval left off

## Part XXI — Cost Optimization Guide

- **Warm pools over blanket pre-provisioning.** AgentCore's memory-vs-compute pricing split makes maintaining a right-sized warm pool of idle (memory-billed-only) microVMs cheaper than either accepting cold-start latency or provisioning full active compute capacity ahead of demand — monitor actual traffic and adjust pool size by time-of-day.
- **Match memory strategy cost to actual retrieval need.** Self-managed memory strategies are billed differently (and generally at a premium) versus built-in strategies — reach for a built-in strategy first and only build custom extraction/consolidation logic when a built-in strategy's output schema is genuinely insufficient.
- **Use Optimization's recommendation engine before hand-tuning.** It mines production traces to suggest concrete, grounded prompt and tool-description fixes rather than requiring manual trial-and-error — a lower-cost path to quality improvement than iterative human-driven prompt engineering alone.
- **Right-size Code Interpreter session duration.** The default 15-minute execution window is appropriate for most tasks; only extend toward the 8-hour maximum for workloads that genuinely require it, since longer-running sandboxes hold billed resources for longer.
- **Treat model inference, not AgentCore infrastructure, as the primary cost lever.** Industry estimates place AgentCore's own infrastructure cost at roughly 10–30% of total agent spend at scale — cost-optimization effort is generally better spent on model selection/routing (Harness's per-invocation model override enables cheap-model-for-simple-steps, expensive-model-for-hard-steps routing within a single session) than on infrastructure tuning alone.

## Part XXII — Security Hardening Guide (Summary)

1. Layer defenses in series: adaptive-retry-aware error handling → input Guardrails with seeded jailbreak/injection patterns → Cedar policy at the Gateway → least-privilege IAM on every execution role → VPC-only network mode for sensitive compute → full audit logging (CloudTrail, Observability traces) as the backstop that makes every other layer reviewable after the fact.
2. Apply a WAF at the actual internet-facing front door (CloudFront/API Gateway/ALB) — AgentCore Runtime itself does not host a WAF, so this layer must be added explicitly by the deploying team if public ingress is retained.
3. Never assume a single security control is sufficient; the recurring theme across every independent finding in this report (Code Interpreter Sandbox mode, confused-deputy trust-policy gaps, Registry auto-approval) is that AWS ships a *documented* safe default, but the *effective* security posture depends on the deploying team correctly configuring — and periodically re-validating — every layer, not just enabling the platform feature and assuming it is sufficient on its own.
4. Build an incident-response playbook specifically for agent-native failure modes: a prompt-injection incident should have a defined process for (a) identifying which Gateway-mediated tool calls occurred during the affected session via Observability traces, (b) determining whether Guardrails or Policy caught/blocked the injected action, (c) revoking any Token Vault credentials the affected session held, and (d) reviewing whether the injected content entered via a Registry-catalogued (vetted) or unvetted tool/MCP source, since that materially changes the remediation (patch a specific tool vs. re-review the entire unvetted-source policy).

## Part XXIII — Keeping the Agent Live: Resilience, Rollout, and Control Operability

This part addresses the operational control surface a platform team needs to run agents continuously in production: how to load-test them, how to stop them when they misbehave, and how to roll out changes safely (continued in [Part 8](18-agentcore-strands-deep-research-report-part8.md), which covers feature gates, resume workflows, failover, exception handling, human-in-the-loop, sampling, and the closing synthesis). Every mechanism below is either an AWS-documented AgentCore capability or an independently-documented gap/workaround — both are marked explicitly, because the gaps matter as much as the capabilities for an architect making a build-vs-buy call on the control plane.

### Stress Testing and Load Testing

Agent load testing is qualitatively different from conventional API load testing, and the difference matters for capacity planning: a 2× increase in concurrent sessions does not produce a proportional latency increase, because token-generation cost, tool-call fan-out, and context-window growth all compound non-linearly. Independent load-testing analysis (LoadView, GetVocal) converges on measuring **latency elasticity** — how response time bends as concurrency rises — rather than flat requests-per-second, and on tracking **cognitive-load failure modes** distinct from infrastructure failure: hallucination rate, tool-call failure rate, and task-completion rate all typically degrade *before* raw latency or error-rate thresholds are breached, meaning an agent under load can look "green" on infrastructure dashboards while quietly answering worse.

**AgentCore-specific load-testing surface:**

- **Quota-aware test design.** As of the June 2026 quota increases, `InvokeAgentRuntime` supports up to 200 TPS per agent per account (25 TPS previously), active sessions up to 5,000 per account in us-east-1/us-west-2 (2,500 elsewhere), and container-deployment session creation up to 400 TPM per endpoint. A load test plan should explicitly target these ceilings — both to validate real headroom and to confirm `ServiceQuotaExceededException` handling degrades gracefully rather than cascading.
- **AgentCore Evaluations, batch mode**, is the AWS-native mechanism for regression-style load/quality testing: run the agent against a curated dataset in batch, score aggregate results against a baseline, and — per AWS's own guidance — wire this into CI/CD so no configuration change reaches production without passing known-good cases first. This is complementary to, not a replacement for, raw throughput load testing.
- **A documented idle-timeout footgun directly relevant to load-test design:** if a custom `/ping` handler sets `time_of_last_update` to the current time on every ping (rather than only when status genuinely changes), the platform's idle-timeout calculation never fires, sessions accumulate past their intended idle window, and a sustained test run can silently exhaust the account's session quota via `maxVms`/`ServiceQuotaExceededException` — a bug in test harness code, not the platform, but one specifically triggered by the ping-based health model AgentCore uses.
- **Third-party tooling** (k6, Locust, Gatling, or agent-specific harnesses like Botium) remains necessary for raw concurrency/throughput testing; AgentCore does not ship a load-generation tool itself, only the evaluation/observability surface to interpret results against.

### Kill Switch

**What AgentCore provides natively:** `StopRuntimeSession` — a documented API (boto3 `stop_runtime_session` or the equivalent HTTP endpoint) that immediately terminates a specific active session by `agentRuntimeArn` + `runtimeSessionId`, halting any in-flight streaming response and releasing the microVM. This is the sanctioned, single-session kill switch, and AWS's own re:Post guidance recommends calling it explicitly as part of timeout/error-handling logic, not only as a manual emergency action.

**A documented, material gap (independent finding, GitHub issue #498 against `aws/bedrock-agentcore-starter-toolkit`, April 2026):** there is **no API to list or bulk-terminate all active sessions** — an operator facing a fleet-wide runaway cannot enumerate and kill every session in one call; `list-sessions` only lists *Memory* sessions, not Runtime/microVM sessions, which is a specific, easy-to-make confusion under incident pressure. The same report documents a worse edge case: a genuinely looping agent that continuously writes to its persistent workspace volume can prevent `StopRuntimeSession`'s own shutdown sequence from completing, because AgentCore attempts to back up the volume before killing the container, and a continuously-written volume never finishes backing up — the stop request effectively stalls. The only workaround the reporting team found effective was an **out-of-band IAM emergency-deny policy** attached directly to the runtime's execution role, denying `bedrock:InvokeModel`/`InvokeModelWithResponseStream`/`CallWithBearerToken`, which starves the agent's next model call with a 403 and breaks the loop from outside the agent entirely — consistent with this report's recurring theme that effective containment lives outside the agent process, never inside it.

**Practical kill-switch architecture, synthesizing AWS's primitive and the independent gap-fill patterns:**

1. **Per-session:** `StopRuntimeSession`, called proactively on timeout/ping-failure/error conditions in your own orchestration code — do not wait for a human to notice.
2. **Fleet-wide / emergency:** maintain your own session registry (log every `runtimeSessionId` you create, e.g., to DynamoDB, at invocation time) specifically *because* AgentCore does not expose a native list-and-kill-all API; treat this as a required piece of your own control plane, not an optional nicety.
3. **Last-resort, when a session is unresponsive to `StopRuntimeSession`:** a pre-staged, single-purpose IAM emergency-deny policy scoped to the specific runtime's execution role (per the confused-deputy guidance in Part VII, this role should already be scoped to exactly one runtime, which is also what makes an emergency-deny safe to apply without collateral impact on other workloads). Know the role name and have the deny-policy JSON ready *before* an incident, not during one.
4. **Governance-layer kill switch (pre-execution, not post-hoc):** a Cedar forbid policy attached in ENFORCE mode is itself a kill switch for a specific tool, principal, or action class — flipping a single policy from permit to forbid (or adding a global forbid) blocks the dangerous action at the Gateway before it ever reaches the tool, which is faster and safer than terminating a session already mid-execution.

### Circuit Breakers

A circuit breaker differs from a kill switch in scope and trigger: a kill switch is a manual or session-scoped stop; a circuit breaker is an **automated, threshold-driven** trip — iteration count, dollar/token budget, consecutive failure count, or a semantic policy violation — that halts *before* a human notices, and (ideally) recovers automatically once the underlying condition clears. The independent tooling landscape here (Waxell Runtime, and several open-source Show-HN-era projects — AgentFuse, AgentCircuit, FailWatch, Runtime Fence) exists specifically because, as of mid-2026, **no cloud agent platform, AgentCore included, ships a first-class, configurable circuit-breaker primitive as a single toggle** — this is a genuine gap independent analysis converges on, not an AgentCore-specific shortcoming.

What AgentCore *does* give you to assemble an equivalent, distributed across the layers already documented in this report:

- **Cedar forbid rules with context conditions** can encode budget-style logic directly — e.g., deny a tool call when `context.input.amount` or a running total exceeds a threshold — evaluated deterministically at the Gateway, outside agent reasoning, which is exactly the "enforcement lives outside the agent" property a circuit breaker needs.
- **Lambda REQUEST interceptors** can maintain per-session or per-principal counters (iteration count, cumulative spend) in an external store (Redis/DynamoDB) and inject a context attribute Cedar then evaluates — this is the composable pattern from Part IV applied specifically to circuit-breaking rather than access control.
- **`add_async_task`/`complete_async_task` plus the `/ping` `HealthyBusy` contract** give you a natural hook point to enforce a hard wall-clock or iteration ceiling on long-running work: a custom ping handler can inspect elapsed time or task count and simply stop reporting `HealthyBusy`, which surfaces the stall through normal Runtime health-checking.
- The explicit architectural conclusion independent analysis reaches, and this report concurs with: **circuit-breaking should be a first-class infrastructure primitive, not bespoke per-team code** — until AgentCore ships one natively, budget this as platform-team-owned shared infrastructure (a small Lambda interceptor + Cedar policy pair, reused across every Gateway) rather than letting each agent team reinvent it.

### Canary Release and Progressive Rollout

AgentCore does **not** offer Lambda-style weighted-alias traffic splitting directly on Runtime endpoint versions (there is no routing-config equivalent for AgentCore Runtime endpoints the way there is for a Lambda alias). Progressive rollout on AgentCore is instead achieved through two AWS-documented, Gateway-mediated mechanisms:

**1. Gateway HTTP passthrough targets with session-sticky weighted routing.** Gateway now supports HTTP passthrough targets that front any HTTP endpoint — including another AgentCore Runtime version, an external agent, or an A2A service — with configurable **session stickiness so weighted routing rules keep a given session on the same target** once assigned. This is the closest AgentCore analog to a canary weight, applied at the Gateway rather than the Runtime layer.

**2. AgentCore Optimization's A/B testing (GA-adjacent, part of the Optimization/agent-performance-loop capability).** This is the fully-documented, purpose-built mechanism, and it is worth treating as *the* canary/progressive-rollout primitive for AgentCore rather than reaching for hand-rolled weighted routing:

- An A/B test defines **control** and **treatment** variants two ways: **target-based routing** (different named Runtime endpoints, registered as separate Gateway targets — use this when the change involves code, a framework upgrade, or an entirely different implementation) or **configuration-bundle-based routing** (same Runtime, different immutable configuration-bundle version — use this when the change is purely a system prompt, model ID, or tool-description edit, requiring no redeployment at all).
- Gateway assigns each **session** (not each request) to a variant based on the `X-Amzn-Bedrock-AgentCore-Runtime-Session-Id` header and the configured traffic weights; **assignment is sticky** — once a session lands on a variant, every subsequent request in that session stays on it, giving within-session consistency while still distributing new sessions per the configured split.
- **Online evaluation scores every session automatically** against configured evaluators, and the results object — polled via `GetABTest` — reports, per evaluator, mean score, absolute and percent change, **p-value, confidence interval, and an `isSignificant` boolean** (AWS's stated threshold: p < 0.05). Results can be polled at any time without affecting statistical validity.
- **Promotion and rollback are explicit, first-class operations**: `agentcore promote ab-test` stops the test, repoints the control endpoint to the treatment version (or updates the winning gateway target), and removes the losing variant, after which `agentcore deploy` applies the change — a clean, auditable promotion step rather than a manual traffic-weight edit. Pausing an in-flight test simply reverts all traffic to the existing (control) configuration, which is itself a rollback mechanism with no additional steps.
- Config-bundle-based A/B tests are notably cheap to run: a documented example ran a 50/50 split entirely through configuration versioning, "with no container rebuild," which is a materially faster iteration loop than infrastructure-level canarying.

**Practical guidance:** default to configuration-bundle A/B testing for prompt/model/tool-description changes (fast, cheap, no redeploy), and reserve target-based (Gateway-routed, separate-Runtime) A/B testing for genuine code or framework changes. In both cases, do not promote until the target evaluator reports `isSignificant: true` with a positive percent-change — the practitioner write-ups reviewed for this report show real cases (a +18% directional lift at p=0.059) that *look* like wins but fail the significance bar at low sample sizes, and promoting on a directional-but-not-significant result is a documented practitioner mistake worth guarding against explicitly.

## Related

- [Deep Research Report](../18-agentcore-strands-deep-research-report.md) — executive summary, platform foundations, Runtime, Gateway
- [Deep Research Report (Part 6)](18-agentcore-strands-deep-research-report-part6.md) — Roadmap prediction, adjacent roadmap signal, best practices, anti-patterns
- [Deep Research Report (Part 8)](18-agentcore-strands-deep-research-report-part8.md) — Feature gates, resume workflow, failover, exception handling, human-in-the-loop, sampling, synthesis
