---
doc_type: reference-architecture
domain: architecture
topic_id: ai-harness-architecture-orchestration
title: "AI Harness Architecture & Multi-Agent Orchestration"
date_created: 2026-07-07
last_reviewed: 2026-07-10
status: current
covers_version: "as of 2026-07-10"
aliases:
  - ai harness architecture multi-agent orchestration
  - harness architecture
supersedes:
  - docs/enterprise-architecture/ai-architecture/ai-harness-architecture-orchestration.md
tags:
  - enterprise-ai-architect
  - agentic-systems
  - harness-architecture
  - orchestration
  - multi-agent
---

# AI Harness Architecture & Multi-Agent Orchestration

Volume 1 of the harness architecture series, covering the AI harness—the deterministic software shell that turns non-deterministic models into accountable system components—its full runtime component catalog, end-to-end task lifecycle, trust boundaries, and complete orchestration pattern comparison. Companion guides: [Memory & Planning Architecture](./41-agent-memory-planning-architecture.md); [Security Architecture & Guardrails](./pathname:///archon/architecture/agentic-ai-security-guardrails); [Reliability, Observability & Governance](./pathname:///archon/architecture/agentic-ai-reliability-observability-governance).

---

## The AI Harness Doctrine

The **AI harness** is the deterministic software shell that surrounds a non-deterministic model and turns it into an accountable system component. The model produces tokens; the harness produces **governed actions**. Formally: the harness owns the agent loop (context assembly → inference → action selection → tool execution → observation → state commit) and every ingress/egress path—identity, policy, safety, telemetry, cost, lifecycle.

### Two Architectural Stances

**Stance 1 — The model is untrusted, replaceable**. All invariants live in the harness. Consistent across Anthropic's agent engineering guidance, OpenAI's Agents SDK, and AWS AgentCore's service decomposition. Anything that must be true 100% of the time (authorization, spend limits, audit, data residency) enforced deterministically *outside* the model. Anything needing to be true most of the time (tone, plan quality, relevance) delegated to the model or probabilistic checks.

**Stance 2 — The harness is where product quality lives**. Production experience from Claude Code, Devin, Manus, and OpenHands shows teams running the same frontier model with different harnesses see order-of-magnitude differences in task completion. Context management, tool ergonomics, and recovery behavior dominate model choice.

| Guarantee Class | Enforcement Point | Examples |
|---|---|---|
| **Invariant (100%)** | Harness, deterministic | AuthZ, budget ceilings, audit trail, data residency, iteration caps |
| **Quality (most of the time)** | Model + probabilistic checks | Tone, plan quality, relevance, summarization fidelity |

---

## Runtime Component Catalog

The canonical decomposition below is the reference component model. In small deployments several components collapse into one process; at enterprise scale each becomes an independently scaled, independently governed service.

| Component | Responsibility | Production Notes |
|---|---|---|
| **Agent Runtime** | Sandboxed execution hosting the loop | Must be disposable, reproducible; session-scoped isolation is primary tenant boundary |
| **Execution Loop** | Perceive→plan→act→observe cycle; enforces max-iterations, budgets, stop conditions | Loop-runaway is top-3 production incident class; hard ceilings required |
| **Planner** | Decomposes goals into steps/DAGs | Separate plan representation from execution for inspectability, diffability, approval, resumability |
| **Reflection** | Post-step self-evaluation; updates plan/memory | Bound reflection depth; unbounded loops burn budget with diminishing returns |
| **Critic** | Independent evaluator (model or rules) scoring outputs before commit | Keep isolated from actor to reduce shared-delusion |
| **Tool Execution** | Mediated invocation of tools/MCP servers | Never let model-emitted arguments reach backend without schema + policy validation |
| **Memory** | Working/episodic/semantic/procedural stores | Memory writes are privileged; gate through policy, tag provenance, encrypt, TTL |
| **Context Manager** | Assembles prompt: policy, task, memory, tool schemas, history | #1 quality lever; enforce strict budget with priority tiers |
| **State Manager** | Durable task/session state: plan, step results; enables pause/resume | Event-sourced or Temporal-style deterministic replay |
| **Policy Engine** | Deterministic authorization of every action (Cedar/OPA/Verified Permissions) | Must be O(ms), fail-closed; version policies; log every decision with policy version ID |
| **Safety Engine** | Probabilistic + deterministic content/behavior screening | Layered before AND after inference; around tool results (indirect injection) |
| **AI Gateway** | Single choke point for all model traffic | Should be *only* path to model APIs; direct credentials in app code is anti-pattern |
| **Approval Engine** | Human-in-the-loop; pause task, route to approver with exact action preview | Timebox approvals; expired = deny |
| **Scheduler** | Triggers agents: cron, events, human requests | Admission control against capacity/budget |
| **Queue** | Decouples submission from execution | Per-tenant queues or fair-share partitioning |
| **Retry Manager** | Classified retry: transient, semantic, fatal | Never blind-retry non-idempotent calls; require idempotency keys |
| **Event Bus** | Emits domain events (task.started, step.completed, approval.requested, budget.exceeded) | Integration spine; downstream consumers subscribe |
| **Registry** | Source of truth: agents, tools, MCP servers, prompts, policies | Governance keystone; nothing deploys unless registered |
| **Discovery** | Runtime resolution: which agent/tool/MCP server for this tenant/region | Answers policy-filtered per caller |
| **Telemetry** | OTel traces/metrics/logs with GenAI semantic conventions | Trace context propagates across model, MCP, A2A calls |
| **Trace Manager** | Correlates full causal chain: user → agent → sub-agents → tools → data | Store full payloads in access-controlled evidence store |
| **Cost Manager** | Real-time metering, budgets, attribution, enforcement | Pre-flight budget checks, not post-hoc reporting |
| **Session Manager** | User/agent session lifecycle, sticky context, TTL, isolation | With MCP stateless, session semantics move fully to harness |
| **Checkpoint Manager** | Snapshots of loop state at step boundaries | Enables resume after crash, human edit-and-resume, time-travel debugging |

---

## Logical Architecture: The 8-Plane Model

Layered view (top to bottom):

1. **Experience layer** — chat UIs, IDEs, APIs, ambient/background triggers
2. **Governance plane** — registries (agent/tool/prompt/policy/MCP), approval workflows, risk classification, audit lake
3. **Orchestration plane** — supervisors, workflow engine, scheduler, queues, event bus
4. **Agent plane** — runtimes (loop + planner + reflection + critic), session & checkpoint managers, memory services
5. **Mediation plane** — AI gateway (model side) and tool gateway/MCP gateway (action side), policy engine PDP, safety engine, approval engine
6. **Capability plane** — models (multi-provider), MCP servers, tools, external A2A agents
7. **Data plane** — vector stores, knowledge graphs, document stores, object storage, transactional systems
8. **Cross-cutting** — identity fabric (SPIFFE/OIDC/STS), telemetry, cost, secrets

**Design rule: arrows only cross planes through mediation**. Agents never call models or tools directly; supervisors never touch data stores except through registered tools. Every plane crossing is an identity + policy + telemetry checkpoint.

---

## End-to-End Task Lifecycle

The canonical per-task runtime sequence:

```
Trigger → Scheduler (admission + budget) → Queue → Runtime spawn
    (microVM/container, workload identity via SPIRE/STS, scoped tokens)
→ Loop iteration:
      Context Manager assembles prompt
      → Safety Engine (input pass) → AI Gateway → Model
      → Parsed action → Policy Engine (allow/deny/approve) → [Approval Engine]
      → Tool Executor (sandbox, timeout, idempotency key) → MCP server / API
      → Result → Safety Engine (injection scan) → State commit + Checkpoint
      → Reflection/Critic (optional) → next iteration or terminate
→ Outputs → Safety Engine (output pass) → Event Bus (task.completed) → Runtime teardown
```

| Stage | Guarantee | Failure Handling |
|---|---|---|
| **Trigger → Admission** | Pre-flight budget + capacity check passes before compute spent | Reject/queue with backpressure |
| **Runtime spawn** | Fresh sandbox, short-lived workload identity, no standing credentials | Spawn failure = retry from queue |
| **Context assembly** | Invariants survive every compaction | Compaction checkpointed; raw in evidence store |
| **Inference** | All model traffic through AI gateway; input safety screen applied | Gateway failover; safety block = structured refusal |
| **Action authorization** | Every parsed action hits policy engine; fail-closed | Deny logged with version; approval path for gated |
| **Tool execution** | Schema-validated args, sandboxed, timed out, idempotent-keyed | Classified retry: transient/semantic/fatal |
| **State commit** | Checkpoint at step boundary; survives runtime crash | Resume from checkpoint, never scratch |
| **Teardown** | Sandbox destroyed, tokens expire, task.completed event emitted | Orphan reaper for zombie runtimes |

Every arrow emits an OTel span; every policy decision and tool call lands in audit log with actor chain and policy version.

---

## Trust Boundaries TB1–TB8

| # | Boundary | Crossing Controls |
|---|---|---|
| **TB1** | Human ↔ Agent | AuthN (OIDC), intent capture, input safety screen, session binding |
| **TB2** | Agent ↔ Model | AI gateway only; prompt provenance tags; response filtering |
| **TB3** | Agent ↔ Tool/MCP | Tool gateway; per-call authZ; schema validation; sandbox; result injection-scan |
| **TB4** | Agent ↔ Memory | Namespace ACLs; write provenance; poisoning detection |
| **TB5** | Agent ↔ Agent (internal) | A2A/message bus with workload identity; no ambient shared credentials |
| **TB6** | Agent ↔ External org agents | Signed Agent Cards, contract-level allowlists, DLP on egress |
| **TB7** | Tenant ↔ Tenant | Session-scoped compute, per-tenant keys/namespaces, no shared caches |
| **TB8** | Runtime ↔ Infrastructure | No instance-profile creds inside sandboxes; egress proxy; syscall filtering |

**Key doctrine**: Any content that entered the context from outside the trust boundary (web pages, retrieved docs, tool results, other agents' messages) is **data, never instructions**—but the model cannot reliably enforce that distinction, so the harness must constrain what a possibly-hijacked agent can do. **Least privilege beats detection.**

---

## Multi-Agent Orchestration

### Why Multi-Agent

Multi-agent buys you: context isolation (each agent gets clean, focused window), heterogeneous models per role (cheap models for routing, frontier for synthesis), parallelism, blast-radius containment, organizational alignment (agent per domain team).

---

## Architect's Checklist

- [ ] Agent loop owns all invariants (authZ, budget ceilings, audit trail, data residency)
- [ ] AI gateway is single path to all model APIs; no direct model credentials in app code
- [ ] Policy engine evaluates every action; O(ms) latency; fail-closed; versioned policies logged
- [ ] Tool execution: schema validation + sandbox + idempotency key on all calls
- [ ] Context manager enforces strict budget with priority tiers (invariants > task > observations > history)
- [ ] State management: event-sourced or deterministic replay (Temporal pattern)
- [ ] Safety layer: input screening, tool-result injection scanning, output gating per risk tier
- [ ] Trust boundaries TB1–TB8 explicitly defined and controls verified by audit
- [ ] Orchestration abstraction prevents framework lock-in (LangGraph/AutoGen/CrewAI interchangeable)
- [ ] OTel spans on every arrow; audit log on every policy decision and tool call
