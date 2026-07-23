---
doc_type: reference-architecture
domain: architecture
topic_id: ai-harness-architecture-orchestration
title: "AI Harness Architecture & Multi-Agent Orchestration"
date_created: 2026-07-07
last_reviewed: 2026-07-23
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

:::info State of the world (July 2026)
MCP finalized spec is 2025-11-25; the 2026-07-28 release (stateless core, Extensions framework, Tasks, MCP Apps) finalizes this month. A2A is at v1.x under the Linux Foundation's Agentic AI Foundation with 150+ organizations in production. AWS Bedrock AgentCore, Azure AI Foundry Agent Service, and Google's Gemini Enterprise Agent Platform (ex-Vertex AI) are GA managed agent runtimes, all supporting MCP and A2A. Design against these baselines.

---

## 1. The AI Harness Doctrine

The **AI harness** is the deterministic software shell that surrounds a non-deterministic model and turns it into an accountable system component. The model produces tokens; the harness produces **governed actions**. Formally: the harness owns the agent loop (context assembly → inference → action selection → tool execution → observation → state commit) and every ingress/egress path around that loop—identity, policy, safety, telemetry, cost, and lifecycle.

Two architectural stances define production practice:

**Stance 1 — The model is an untrusted, replaceable inference dependency; all invariants live in the harness.** This position is consistent across Anthropic's agent engineering guidance, OpenAI's Agents SDK design, and AWS AgentCore's service decomposition. Anything that must be true 100% of the time (authorization, spend limits, audit, data residency) must be enforced deterministically *outside* the model. Anything that only needs to be true most of the time (tone, plan quality, relevance) can be delegated to the model or probabilistic checks.

**Stance 2 — The harness is where product quality lives.** Production experience from Claude Code, Devin, Manus, and OpenHands shows teams running the *same frontier model* with different harnesses see order-of-magnitude differences in task completion. Context management, tool ergonomics, and recovery behavior dominate model choice. Anthropic's multi-agent research system work reached the same conclusion from the prompt side: agent-tool interfaces are as critical as human-computer interfaces, and fixing a flawed tool description cut task completion times by ~40%.

| Guarantee class | Enforcement point | Examples |
| --- | --- | --- |
| **Invariant (100%)** | Harness, deterministic | AuthZ decisions, budget ceilings, audit trail, data residency, iteration caps |
| **Quality (most of the time)** | Model + probabilistic checks | Tone, plan quality, relevance, summarization fidelity |

---

## 2. Runtime Component Catalog

The canonical decomposition below is the reference component model. In small deployments several components collapse into one process; at enterprise scale each becomes an independently scaled, independently governed service.

| Component | Responsibility | Production notes / failure characteristics |
| --- | --- | --- |
| **Agent Runtime** | Sandboxed execution environment hosting the loop: process/microVM per session (AgentCore uses per-session microVM isolation; OpenHands/Claude Code use containers or local sandboxes) | Must be disposable and reproducible. Session-scoped compute isolation is the primary tenant boundary. Runtime crash must never lose committed state—state lives outside |
| **Execution Loop** | The perceive→plan→act→observe cycle; enforces max-iterations, budgets, stop conditions | Loop-runaway (agent oscillation) is a top-3 production incident class; require hard iteration/token/wall-clock ceilings enforced outside model reasoning |
| **Planner** | Decomposes goals into steps/DAGs; may be the same model, a distinct model, or a workflow engine | Separate plan *representation* from plan *execution* so plans are inspectable, diffable, approvable, and resumable (see [Memory & Planning](./41-agent-memory-planning-architecture.md)) |
| **Reflection** | Post-step self-evaluation; updates plan/memory based on outcomes | Bound reflection depth; unbounded self-critique loops burn budget with diminishing returns |
| **Critic** | Independent evaluator (usually a second model or rules) scoring outputs before commit | Keep critic context isolated from the actor to reduce shared-delusion; critics with the same context tend to rubber-stamp |
| **Tool Execution** | Mediated invocation of tools/MCP servers: schema validation, timeout, sandboxing, result normalization | Never let the model's emitted arguments reach a backend without deterministic schema + policy validation. Structured, actionable tool error messages are the largest cheap win in agent reliability |
| **Memory** | Working/episodic/semantic/procedural stores | Memory writes are privileged operations: gate through policy, tag provenance, encrypt, TTL ([full guide](./41-agent-memory-planning-architecture.md)) |
| **Context Manager** | Assembles the prompt: system policy, task, retrieved memory, tool schemas, history; compaction/summarization near window limits | **The #1 quality lever.** Enforce a strict context budget with priority tiers (invariants &gt; task &gt; fresh observations &gt; history). Compaction must be checkpointed and auditable |
| **State Manager** | Durable task/session state: plan, step results, variables; enables pause/resume/replay | Model on event-sourced or workflow-engine semantics (Temporal-style deterministic replay is the strongest pattern) |
| **Policy Engine** | Deterministic authorization of every action (Cedar/OPA/Verified Permissions). PDP separate from PEPs embedded in gateway/tool layer | Policy evaluation must be O(ms) and fail-closed. Version policies; log every decision with policy version ID |
| **Safety Engine** | Probabilistic + deterministic content/behavior screening: prompt-injection classifiers, PII detection, harmfulness filters (Bedrock Guardrails, Azure Content Safety, Model Armor, Llama Guard-class models) | Layered before *and* after inference and around tool results (indirect injection). Track false-positive budget as an SLO |
| **AI Gateway** | Single choke point for all model traffic: authN/Z, routing, quota, caching, redaction, audit | Should be the *only* path to model APIs; direct model credentials in app code is an anti-pattern |
| **Approval Engine** | Human-in-the-loop: pause task, route to approver with full action preview, resume/deny. Backed by durable state (Temporal signals, AgentCore/LangGraph interrupts) | Approvals must show the *exact* pending action (rendered tool call + diff), not the agent's summary of it. Timebox approvals; expired = deny |
| **Scheduler** | Triggers agents: cron, events, human requests; admission control against capacity/budget | Apply queue-depth-based admission control; agents amplify load (1 request → N model calls → M tool calls) |
| **Queue** | Decouples submission from execution (SQS/Kafka/Redis Streams) | Per-tenant queues or fair-share partitioning to prevent noisy-neighbor starvation. DLQ mandatory |
| **Retry Manager** | Classified retry: transient (retry w/ jitter), semantic (re-plan), fatal (fail + escalate) | Never blind-retry non-idempotent tool calls; require idempotency keys (Stripe pattern) on all mutating tools |
| **Event Bus** | Emits domain events (task.started, step.completed, approval.requested, budget.exceeded) for observers, triggers, audit | The integration spine; downstream consumers (billing, SIEM, eval pipelines) subscribe rather than polling agent state |
| **Registry** | Source of truth for agents, tools, MCP servers, prompts, policies: versions, owners, risk class, entitlements | Registry-of-record is the governance keystone. Nothing deploys or gets invoked unless registered |
| **Discovery** | Runtime resolution: which agent/tool/MCP server serves this capability for this tenant/region (A2A Agent Cards + MCP registry + internal catalog) | Discovery answers must be policy-filtered per caller—never return capabilities the caller can't invoke |
| **Telemetry** | OTel traces/metrics/logs with GenAI semantic conventions; token &amp; cost meters | Trace context must propagate across model calls, MCP calls (standardized via `_meta` traceparent in MCP 2026-07-28), and A2A hops |
| **Trace Manager** | Correlates the full causal chain: user → agent → sub-agents → tools → data, producing decision graphs | Store full prompt/response payloads in a separate, access-controlled evidence store (privacy) linked by trace ID |
| **Cost Manager** | Real-time metering, budgets, attribution (tenant/agent/task), enforcement (throttle/downgrade/halt) | Enforce *pre-flight* budget checks, not just post-hoc reporting; runaway loops can burn 5–6 figures in hours |
| **Session Manager** | User/agent session lifecycle, sticky context, TTL, isolation | With MCP going stateless at protocol level, session semantics move fully into your harness—own them explicitly with signed, expiring session/state handles |
| **Checkpoint Manager** | Snapshots of loop state at step boundaries; enables resume after crash, human edit-and-resume, time-travel debugging | Checkpoint = (context digest, plan version, memory refs, pending actions). LangGraph checkpointers and AgentCore session persistence are reference implementations |

---

## 3. Logical Architecture: The 8-Plane Model

Layered view (top to bottom):

1. **Experience layer** — chat UIs, IDEs, APIs, ambient/background triggers
2. **Governance plane** — registries (agent/tool/prompt/policy/MCP), approval workflows, risk classification, audit lake. Consumes events; authorizes deployments.
3. **Orchestration plane** — supervisors, workflow engine, scheduler, queues, event bus
4. **Agent plane** — agent runtimes (loop + planner + reflection + critic), session &amp; checkpoint managers, memory services
5. **Mediation plane** — AI gateway (model side) and tool gateway/MCP gateway (action side), policy engine PDP, safety engine, approval engine
6. **Capability plane** — models (multi-provider), MCP servers, tools, external A2A agents
7. **Data plane** — vector stores, knowledge graphs, document stores, object storage, transactional systems
8. **Cross-cutting** — identity fabric (SPIFFE/OIDC/STS), telemetry, cost, secrets

:::tip Design rule: arrows only cross planes through mediation
Agents never call models or tools directly; supervisors never touch data stores except through registered tools. Every plane crossing is an identity + policy + telemetry checkpoint. If a proposed integration bypasses the mediation plane, it is an architecture defect, not a shortcut.

---

## 4. End-to-End Task Lifecycle

The canonical per-task runtime sequence—this is the end-to-end lifecycle every governed agent task follows:

```
Trigger → Scheduler (admission + budget) → Queue → Runtime spawn
    (microVM/container, workload identity issued via SPIRE/STS, scoped tokens minted)
→ Loop iteration:
      Context Manager assembles prompt (policy header + task + memory + tool schemas)
      → Safety Engine (input pass) → AI Gateway → Model
      → Parsed action → Policy Engine (allow/deny/approve) → [Approval Engine if required]
      → Tool Executor (sandbox, timeout, idempotency key) → MCP server / API
      → Result → Safety Engine (tool-result pass: injection scan) → State commit + Checkpoint
      → Reflection/Critic (optional) → next iteration or terminate
→ Outputs → Safety Engine (output pass) → Event Bus (task.completed) → Runtime teardown
```

```mermaid
sequenceDiagram
    participant User
    participant Scheduler
    participant AI Gateway
    participant Policy Engine
    participant Tool Executor
    participant State Manager
    User->>Scheduler: Task submission
    Scheduler->>Scheduler: Admission check (budget + capacity)
    Scheduler->>AI Gateway: Spawn runtime
    loop Agent Loop
        AI Gateway->>AI Gateway: Assemble context + input safety screen
        AI Gateway->>AI Gateway: Call model
        AI Gateway->>Policy Engine: Evaluate parsed action
        Policy Engine->>Tool Executor: Authorized action
        Tool Executor->>Tool Executor: Schema validation + sandbox
        Tool Executor->>State Manager: Checkpoint step
    end
    State Manager->>User: Task complete + event emitted
```

Lifecycle guarantees to enforce at each stage:

| Stage | Guarantee | Failure handling |
| --- | --- | --- |
| **Trigger → Admission** | Pre-flight budget + capacity check passes before any compute is spent | Reject/queue with backpressure signal |
| **Runtime spawn** | Fresh sandbox, short-lived workload identity, no standing credentials | Spawn failure = retry from queue; nothing to clean up |
| **Context assembly** | Invariants (policy header, task goal, approvals) survive every compaction | Compaction checkpointed; raw transcript in evidence store |
| **Inference** | All model traffic through the AI gateway; input safety screen applied | Gateway failover/routing; safety block = structured refusal |
| **Action authorization** | Every parsed action hits the policy engine; fail-closed | Deny logged with policy version; approval path for gated actions |
| **Tool execution** | Schema-validated args, sandboxed, timed out, idempotency-keyed | Classified retry: transient/semantic/fatal |
| **State commit** | Checkpoint at step boundary; committed state survives runtime crash | Resume from checkpoint, never from scratch |
| **Teardown** | Sandbox destroyed, tokens expire, task.completed event emitted | Orphan reaper for zombie runtimes |

Every arrow emits an OTel span; every policy decision and tool call lands in the audit log with the actor chain (human → agent → sub-agent) and policy version.

---

## 5. Trust Boundaries TB1–TB8

Enumerate and defend these boundaries explicitly—they feed the threat model in [Security Architecture &amp; Guardrails](./pathname:///archon/architecture/agentic-ai-security-guardrails):

| # | Boundary | Crossing controls |
| --- | --- | --- |
| **TB1** | Human ↔ Agent | AuthN (OIDC), intent capture, input safety screen, session binding |
| **TB2** | Agent ↔ Model | AI gateway only; prompt provenance tags; response filtering |
| **TB3** | Agent ↔ Tool/MCP | Tool gateway; per-call authZ; schema validation; sandbox; result injection-scan (data crossing *into* context is untrusted) |
| **TB4** | Agent ↔ Memory | Namespace ACLs; write provenance; poisoning detection |
| **TB5** | Agent ↔ Agent (internal) | A2A/message bus with workload identity; no ambient shared credentials |
| **TB6** | Agent ↔ External org agents | Signed Agent Cards, contract-level allowlists, DLP on egress |
| **TB7** | Tenant ↔ Tenant | Session-scoped compute, per-tenant keys/namespaces, no shared caches without cache-scope keys |
| **TB8** | Runtime ↔ Infrastructure | No instance-profile ambient creds inside sandboxes; egress proxy; syscall filtering |

:::danger Key doctrine
Any content that entered the context window from outside the trust boundary (web pages, retrieved docs, tool results, other agents' messages) is **data, never instructions**—but the model cannot reliably enforce that distinction, so the harness must constrain what a possibly-hijacked agent can do. **Least privilege beats detection.**

---

## 6. Multi-Agent Orchestration

### 6.1 Why Multi-Agent At All

Multi-agent buys you: context isolation (each agent gets a clean, focused window), heterogeneous models per role (cheap models for routing, frontier for synthesis), parallelism, blast-radius containment, and organizational alignment (agent per domain team).

It costs you: coordination overhead, compounded error rates across hops, harder debugging, and token multiplication. Anthropic's multi-agent research system reported **~15× token usage vs. single-agent chat** (agents alone run ~4× chat)—the architecture outperformed single-agent Claude Opus 4 by 90.2% on their internal research eval, but is only economically viable when the task's value covers the multiplier and the work parallelizes.

Default guidance across Anthropic and OpenAI engineering material: **start single-agent with good tools; split only when context, skill, or parallelism demands it.**

### 6.2 Pattern Comparison

| Pattern | Mechanics | Advantages | Disadvantages | Latency | Scalability | Governance | Failure modes | Recovery | Enterprise fit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Supervisor** | One orchestrator model routes/delegates to workers; owns final answer | Simple mental model; single audit/decision point; easy HITL insertion | Supervisor is bottleneck &amp; single point of misjudgment; context bloat at hub | +1 hop per delegation | Moderate (fan-out limited by supervisor context) | Strong—central choke point | Supervisor loop/misroute; worker result mis-integration | Restart from supervisor checkpoint | **Default enterprise pattern** |
| **Manager–Worker** | Supervisor variant with homogeneous worker pool + queue | Elastic parallelism; simple retries per work item | Task must shard cleanly; result merge logic | Low per item | High (queue-driven) | Strong | Skew/straggler workers; merge conflicts | Re-queue failed shards | Batch/ETL-like agent workloads |
| **Hierarchical** | Multi-level supervisors (org-chart of agents) | Scales scope; domain encapsulation; per-level policy | Latency &amp; error compounding per level; blame diffusion | High (depth × hop) | High in scope | Good if each level logs | Mis-delegation cascades | Sub-tree restart via checkpoints | Large multi-domain platforms |
| **Mesh / P2P** | Any agent may message any agent (A2A) | Flexible; no bottleneck; org-boundary friendly | Emergent behavior hard to audit; N² channels | Variable | Very high | Weak unless every edge mediated | Message storms; circular delegation; contamination spread | Hard—need per-edge idempotency + global kill | Cross-org federation only, with contracts |
| **Blackboard** | Agents read/write shared workspace; act opportunistically | Loose coupling; great for incremental knowledge fusion | Write conflicts; poisoning surface; ordering | Medium | High | Medium (audit the board) | Stale/poisoned entries drive all agents wrong | Board versioning + rollback | Investigation/analysis pipelines |
| **Market / Contract Net** | Task announced; agents bid; award to best bidder | Dynamic load/skill matching; decentralized | Bid honesty/calibration; auction overhead; gaming | High (auction round) | High | Medium (log auctions) | No bidders; winner's-curse failures | Re-auction | Rare in-enterprise; niche resource allocation |
| **Swarm (handoff-style)** | Lightweight agents transfer control + context laterally (OpenAI Swarm → Agents SDK handoffs) | Minimal orchestration code; natural for routing/triage | Control flow implicit in prompts; audit trail = conversation | Low | Moderate | Medium | Ping-pong handoffs; lost context on transfer | Conversation checkpoint | Customer-support triage tiers |
| **Actor model** | Each agent = actor w/ mailbox, private state, supervision trees (Akka/Orleans/Cloudflare Durable Objects semantics) | Proven concurrency discipline; supervision = recovery built-in; location transparency | Requires actor-runtime expertise; message-ordering design | Low | Very high | Good (mailbox = audit) | Mailbox overflow; actor starvation | Supervisor restart strategies (one-for-one etc.) | Strong substrate for platform builders |
| **Event-driven** | Agents subscribe to domain events; emit new events | Extreme decoupling; replayable history; org-scale integration | Causality hard to follow; eventual consistency | Async | Very high | Good if event schema governed | Event storms; poison events; dupe processing | DLQ + replay from offset | Background/ambient agents |
| **DAG execution** | Predefined dependency graph; agents fill nodes | Deterministic structure; parallel where DAG allows; easy cost estimates | Rigid; poor for exploratory tasks | Optimal for known work | High | Strongest—structure is reviewable pre-run | Node failure blocks descendants | Re-run node, resume DAG | Regulated, repeatable processes |
| **Workflow engine (Temporal, Camunda)** | Durable-execution engine owns control flow; agents are activities | Exactly-once-ish orchestration, replay, signals (HITL), timers, versioning for free | Determinism constraints on workflow code; two-tier debugging (workflow vs. agent) | Low overhead | Very high | Strong (history is the audit) | Non-deterministic workflow code breaks replay; activity timeouts | Automatic replay/retry; continue-as-new | **Recommended backbone** for long-running agent processes |
| **LangGraph-style state machine** | Explicit graph of nodes+edges over shared typed state; checkpointed | Inspectable control flow; interrupts for HITL; time-travel | You own the graph design; framework coupling | Low | High (platform-dependent) | Strong | Bad state-merge reducers; graph deadlock | Resume from checkpoint | **Default for in-house agent apps** |
| **Decision tree / rules** | Deterministic router precedes model work | Cheap, predictable, testable | No generalization | Minimal | High | Strongest | Rule gaps | Edit rules | Front-line routing before LLM spend |
| **Hybrid** | Workflow/DAG skeleton with supervised model-driven sub-loops inside nodes | Combines auditability with flexibility | Design discipline required; boundary confusion (who owns retries) | Balanced | High | Strong | Layered checkpoints | **The realistic end-state** for most enterprises |

### 6.3 Selection Doctrine

1. **Structure over intelligence where possible.** If the process is knowable in advance, encode it as a DAG/workflow and confine model autonomy to node internals. Autonomy is a cost you pay for unknown structure.
2. **Durable execution as the spine.** Temporal (or Camunda/Step Functions for BPMN/state-machine cultures) should own long-running control flow; LangGraph-class graphs own the cognitive loop within a workflow activity. This split cleanly separates *process reliability* (engine's job) from *reasoning quality* (harness's job).
3. **One mediation edge per pattern.** Whatever topology you pick, every inter-agent edge must traverse identity + policy + telemetry. If a pattern makes that impractical (unmediated mesh), it is disqualified for regulated workloads.
4. **Compounding error math.** A 5-step chain of 95%-reliable steps is ~77% reliable; a 3-level hierarchy of those chains is far worse. Add critics/verification at merge points, not everywhere.
5. **Kill-switch reachability.** Every pattern must support: pause-all (drain queues), cancel-task (propagated via A2A/MCP cancellation), and revoke-identity (STS/SPIFFE short-lived creds make this fast). Patterns where cancellation can't propagate (fire-and-forget events without correlation IDs) need compensating design before production.

### 6.4 Anti-Patterns Observed in Production

| Anti-pattern | Shape | Fix |
| --- | --- | --- |
| **The Committee** | N agents "discussing" with shared context—token burn with convergence to the loudest prompt | Actor pattern + independent critic |
| **Supervisor-as-God** | Supervisor accumulates every worker transcript until context collapse | Pass summaries/artifacts, not transcripts (artifact-passing via shared object store is the Claude Code / Manus pattern) |
| **Recursive delegation without depth caps** | Agent spawns sub-agent spawns sub-agent | Enforce max spawn depth and global task budget in the harness, not prompts |
| **Chat as API** | Agents parsing each other's prose | A2A structured Tasks/Artifacts or typed messages |
| **Retry-on-semantic-failure** | Re-running identical prompts on judgment errors | Retries are for transport faults; *re-planning* is for reasoning faults |

---

## 7. Deployment Architecture

Reference deployment (cloud-agnostic; concrete mappings in parentheses):

- **Control cluster** (Kubernetes / ECS): gateway, policy engine, registries, schedulers, workflow engine (Temporal or managed), event bus (Kafka/EventBridge).
- **Execution fleet**: ephemeral sandboxes—Firecracker microVMs / gVisor / Kata containers per session (AgentCore Runtime model), autoscaled, no standing credentials, egress via proxy allowlist.
- **Model access**: managed endpoints (Bedrock, Anthropic API, Azure OpenAI, Vertex) fronted exclusively by the AI gateway; optional self-hosted fallback pool.
- **State tier**: workflow DB (Temporal/Postgres), checkpoint store (S3/object), memory stores (vector DB, graph DB), audit lake (immutable, WORM where regulated).
- **Multi-region**: active/active control plane; execution pinned by data-residency policy; model routing table per region (EU AI Act / data-sovereignty constraints).

---

## 8. How Industry Implements

### AWS — Bedrock AgentCore

AgentCore decomposes the harness into managed services that map almost one-to-one onto the component catalog above: **Runtime** (per-session microVM isolation with dedicated compute, memory, and filesystem; up to 8-hour sessions; the microVM is destroyed and memory sanitized at session end—TB7 enforced at the infrastructure layer), **Memory** (managed short/long-term memory with extraction strategies), and **Gateway** (MCP-compatible tool gateway handling auth, rate limiting, and retries). The multi-tenant guidance is explicit: session-scoped compute isolation is the tenant boundary.

### Microsoft — Azure AI Foundry Agent Service

Foundry Agent Service is the managed runtime for custom agent architectures on Azure: managed sandbox with persistent filesystem, **Entra identity per agent** (workload identity as a first-class harness feature), scale-to-zero pricing, and support for agents built with LangGraph, Microsoft Agent Framework, Claude Agent SDK, and OpenAI Agents SDK. A2A v1 support ships in Microsoft Agent Framework, and Copilot Studio's A2A support went GA in April 2026—the mediation-plane pattern applied to cross-platform agent communication.

### Google — Gemini Enterprise Agent Platform

The evolution of Vertex AI into a full agent platform: agent-to-agent orchestration with generative *and* deterministic orchestration patterns (the hybrid pattern above productized), sub-second cold starts in the revamped Agent Runtime, and multi-day long-running agent workflows—durable execution semantics as a managed service.

### Anthropic — Multi-Agent Research System &amp; Claude Code

Anthropic's published engineering on its research system is the canonical supervisor-pattern case study: an orchestrator-worker design where the lead agent saves its plan to memory before spawning subagents (plan survives context truncation), decomposes queries into explicitly-scoped subtasks (objective, output format, tool guidance, task boundaries), and passes artifacts rather than transcripts. Key published numbers: 90.2% improvement over single-agent on internal research evals; ~15× token usage vs. chat; tool-description fixes cutting task time ~40%. Claude Code itself demonstrates the scratchpad/artifact pattern: agents write plans and findings to files instead of holding them in-window.

### Temporal — Durable Execution as the Spine

Temporal's trajectory validates selection doctrine #2: $300M raised at a $5B valuation (Feb 2026), 9.1 trillion lifetime action executions with 1.86 trillion from AI-native companies. The consensus production stack layers Temporal as the outer durability/orchestration layer with LangGraph StateGraphs as the inner cognitive loop inside activities—LangGraph 1.0 with PostgreSQL checkpointing for step-level recovery, Temporal for workflows past the "restart is acceptable" threshold. LangGraph, Pydantic AI, and the OpenAI Agents SDK have all adopted durable execution as a first-class feature; it is baseline infrastructure now, not an option.

### Production Results Across Industries

- **JPMorgan** runs 450+ AI use cases in production daily, including agentic investment-banking presentation generation and trade-settlement automation.
- **Walmart's** supply-chain agent makes autonomous replenishment decisions across 4,700 stores—a complete decision owned by an agent, with architecture matched to risk level.
- **General Mills'** shipment-optimization agents assess 5,000+ daily shipments, $20M+ saved since FY2024.
- The pattern across the highest-ROI deployments: the agent owned a complete decision, ran in production (not a pilot), and the architecture matched the risk level of the task.

---

## 9. Architect's Checklist

- [ ] Every invariant (authZ, budget, audit, residency) enforced deterministically in the harness—none delegated to prompts
- [ ] Hard iteration/token/wall-clock ceilings on every loop, enforced outside model reasoning
- [ ] All model traffic through one AI gateway; no model credentials in app code
- [ ] Every tool call: schema validation → policy decision → sandbox → idempotency key → result injection-scan
- [ ] Checkpoint at every step boundary; runtime crash never loses committed state
- [ ] TB1–TB8 enumerated in the threat model with explicit crossing controls
- [ ] Orchestration pattern chosen from the comparison table with governance column weighted for your regulatory context
- [ ] Kill-switch: pause-all, cancel-task, revoke-identity all reachable and tested
- [ ] Pre-flight cost checks; per-tenant fair-share queues; DLQ on everything

---

## Sources

- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [AWS — Building multi-tenant agents with Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/machine-learning/building-multi-tenant-agents-with-amazon-bedrock-agentcore/)
- [AWS Docs — AgentCore isolated sessions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html)
- [Microsoft Learn — Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)
- [Microsoft — A2A v1 in Microsoft Agent Framework](https://devblogs.microsoft.com/agent-framework/a2a-v1-is-here-cross-platform-agent-communication-in-microsoft-agent-framework-for-net/)
- [Google Cloud — Introducing Gemini Enterprise Agent Platform](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform)
- [AgentMarketCap — Durable Agent Execution in Production 2026](https://agentmarketcap.ai/blog/2026/04/10/durable-agent-execution-production-temporal-modal-event-sourced)
- [Zylos Research — Durable Execution for AI Agent Runtimes](https://zylos.ai/research/2026-04-24-durable-execution-agent-runtimes/)
- [AI Monk — 12 Agentic AI Examples With Measurable ROI](https://aimonk.com/agentic-ai-examples-enterprise-roi-case-studies/)
- Volume 1, *Multi-Agent AI Harness Architecture (2026) — Production Reference Guide*
