---
title: "Multi-Agent Topology Patterns"
date_created: 2026-07-14
last_reviewed: 2026-07-14
status: current
source_type: native-md
source_file: ""
tags: ["architecture", "patterns", "multi-agent"]
doc_type: reference-architecture
covers_version: "as of 2026-07-14"
domain: architecture
topic_id: multi-agent-topology-patterns
supersedes:
  - docs/enterprise-architecture/ai-architecture/multi-agent-topology-patterns.md
---

# Multi-Agent Topology Patterns

**Audience:** AI architects, platform engineers, and senior engineers designing multi-agent systems.

**Purpose:** Canonical taxonomy of 16 multi-agent topology patterns. For each pattern: what problem it solves, architecture diagram, lifecycle, state management, communication model, governance requirements, failure modes, enterprise suitability score, and anti-patterns to avoid.

---

## Pattern Catalog

| # | Pattern | Core Idea | Enterprise Suitability |
|---|---------|-----------|----------------------|
| 1 | Supervisor-Worker | Single supervisor delegates to specialist workers | ★★★★★ |
| 2 | Router | Classifier routes tasks to specialized agents | ★★★★★ |
| 3 | Planner-Executor | Planner decomposes goals; executors run steps | ★★★★☆ |
| 4 | Manager-Worker Pool | Manager allocates work units to dynamic worker pool | ★★★★☆ |
| 5 | Blackboard | Shared state board; agents post and consume knowledge | ★★★☆☆ |
| 6 | Pipeline / Chain | Linear sequence; each agent transforms and passes | ★★★★★ |
| 7 | Parallel Fan-Out | Coordinator fans tasks out; aggregates results | ★★★★★ |
| 8 | Mesh | Agents discover and call each other as peers | ★★★☆☆ |
| 9 | Swarm | Emergent behaviour from many simple agents, no central coordinator | ★★☆☆☆ |
| 10 | Committee / Ensemble | Multiple agents produce outputs; aggregator decides | ★★★★☆ |
| 11 | Debate / Adversarial | Agents argue opposing positions; arbiter decides | ★★★☆☆ |
| 12 | Voting / Consensus | Multiple agents vote; majority or quorum wins | ★★★☆☆ |
| 13 | Recursive / Self-Spawning | Agent spawns sub-agents for sub-problems | ★★★☆☆ |
| 14 | Reflection | Agent critiques its own output in a self-correction loop | ★★★★☆ |
| 15 | Judge / Critic | Separate judge agent scores another agent's output | ★★★★★ |
| 16 | Human-in-the-Loop (HITL) Hybrid | Human approval gate embedded in agent workflow | ★★★★★ |

---

## 1. Supervisor-Worker

### Problem

A complex task has multiple parallel or sequential sub-tasks requiring specialist agents. No single agent can handle the full breadth. A coordinating intelligence must delegate, monitor, and synthesise.

### Architecture

```
        User Task
            │
            ▼
    ┌─────────────────────────┐
    │     SUPERVISOR          │
    │ • Decomposes task       │
    │ • Assigns to workers    │
    │ • Monitors completion   │
    │ • Synthesises results   │
    └──┬──────┬──────┬────────┘
       │      │      │
   ┌───▼──┬──▼──┬───▼────┐
   │Wrk A │Wrk B │ Wrk C  │
   │(spec)│(spec)│(spec)  │
   └──┬───┴──┬───┴──┬─────┘
      │      │      │
      └──┬───┘      │
         ▼          ▼
      Results → Supervisor Synthesises
```

### Lifecycle

1. Supervisor receives goal; invokes planning model to decompose into sub-tasks
2. Each sub-task dispatched to matching worker (via tool call or A2A task)
3. Supervisor tracks completion state per worker (success / fail / timeout)
4. On all-complete: supervisor synthesises; on partial failure: retry / escalate / degrade
5. Final response returned to user

### State Management

Supervisor owns task-plan state (sub-task list, assignment map, completion status). Workers are typically stateless. Use durable workflow engine (Temporal, Step Functions) for plans exceeding a single context window.

### Governance

Supervisor inherits the user's authorization context; re-attests before each worker call. Worker tokens scoped to their specialisation. Supervisor logs every delegation, assignment, and result for audit trail. Policy Engine evaluated at supervisor layer before any delegated action.

### Failure Modes

| Failure | Behaviour | Resolution |
|---------|-----------|------------|
| Worker timeout | Supervisor marks sub-task failed; retries up to budget | If budget exhausted: graceful degradation or HITL |
| Supervisor crash | Plan state lost if not durable | Checkpoint plan state after each assignment |
| Worker hallucination cascades | Supervisor accepts bad sub-output as fact | Verification gate: supervisor validates worker output schema/grounding |
| Worker exceeds scope | Worker calls tools outside its charter | Scoped tool registry per worker role |
| Supervisor context overflow | Plan state + all worker results overflow context | Summarise completed sub-tasks; store verbatim in memory service |

### Enterprise Suitability ★★★★★

Best pattern for most enterprise use cases. Clear governance hierarchy, predictable delegation, auditability. Used by: financial research agents (researcher/analyst/compliance workers), customer-service orchestration (triage/billing/technical workers), code review agents (security/style/test workers).

---

## 2. Router

### Problem

A single entry point receives diverse task types. Routing to the correct specialist agent improves quality and reduces cost versus sending all queries to a general-purpose agent.

### Architecture

```
  User Query
      │
      ▼
 ┌──────────┐
 │  ROUTER  │────────► Billing Agent
 │ (classify│
 │  intent) │────────► Technical Agent
 │          │
 │          │────────► Escalation Agent
 └──────────┘
```

### Lifecycle

1. Router receives query; classifies intent (via model, embeddings, or rule engine)
2. Confidence score computed; low-confidence triggers fallback to general agent or HITL
3. Selected agent receives full context and produces response
4. Response returned; router optionally validates response type matches route

### Governance

Router is the first policy enforcement point: can deny routing to sensitive agents based on user tier/role. Route selection logged with classification confidence for explainability. Routing rules versioned and change-managed (routing drift is a critical failure mode).

### Enterprise Suitability ★★★★★

Ideal for: customer service (triage), multi-domain chatbots, API gateways in front of agent pools. The simplest multi-agent topology to govern and audit.

---

## 3. Planner-Executor

### Problem

A complex goal requires dynamic decomposition into a plan, where each step's execution informs subsequent steps. The plan itself may evolve as new information arrives.

### Architecture

```
  Goal
   │
   ▼
┌──────────────────────────────────────┐
│              PLANNER                 │
│  1. Decompose goal into step DAG      │
│  2. Prioritize and sequence steps    │
│  3. Re-plan on execution feedback    │
└───────────────┬──────────────────────┘
                │  Plan + context
                ▼
┌──────────────────────────────────────┐
│             EXECUTOR                 │
│  For each step:                      │
│    - Select tool / agent             │
│    - Execute                         │
│    - Report result back to planner   │
│    - On failure: signal for re-plan  │
└──────────────────────────────────────┘
```

### State Management

Plan state (DAG) is the critical shared state; must survive planner restarts. Executor maintains step-execution state (current step, results, failures). Use durable execution (Temporal workflows, LangGraph with checkpointer).

### Governance

Plan approval gate for high-risk plans (HITL before first executor step). Planner decisions logged: "chose to decompose into X steps because Y" (explainability). Executor cannot proceed to next step without planner acknowledgement (step-gate option). Budget limits on plan depth (max steps) and plan changes (max re-plans).

### Enterprise Suitability ★★★★☆

Excellent for: autonomous research assistants, document-processing workflows, software development agents. Requires durable execution infrastructure.

---

## 4. Manager-Worker Pool

### Problem

Large volumes of uniform tasks need processing at scale. A manager allocates work units from a queue to a pool of interchangeable workers, handling backpressure and worker failure.

### Key Differences from Supervisor-Worker

Workers are **fungible** (any worker can handle any work unit); supervisors have specialist workers. Scale is the primary concern (10s–1000s of concurrent workers). Work units are pre-enumerated in a queue.

### State Management

Work queue is the authoritative state (SQS, Kafka, Pub/Sub, Temporal task queue). Manager tracks in-flight assignments; heartbeat-based timeouts detect dead workers. Workers are stateless; no cross-worker state sharing.

### Enterprise Suitability ★★★★☆

Best for: document ingestion pipelines, batch evaluation runs, large-scale data extraction. Requires queue infrastructure.

---

## 5. Blackboard

### Problem

Multiple specialist agents contribute partial knowledge towards a solution that no single agent can compute alone. Agents read and write to a shared knowledge structure asynchronously.

### State Management

Blackboard is the critical shared state (typically a vector store + structured DB hybrid). Optimistic concurrency or versioned writes handle simultaneous KS writes. Control component monitors blackboard state and decides which KS to activate next.

### Governance

Write permissions scoped per knowledge source (KS-A cannot overwrite KS-B contributions). Blackboard change log for audit trail. Quorum requirement before hypothesis is "accepted" (at least N KS must agree).

### Enterprise Suitability ★★★☆☆

Specialized use cases (scientific research, intelligence analysis, medical). Operationally complex; avoid for standard enterprise use cases.

---

## 6. Pipeline / Chain

### Problem

A task requires sequential transformation stages, where each stage's output becomes the next stage's input. Stage dependencies are linear and well-defined.

### Architecture

```
  Input
    │
    ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Stage 1 │─→│ Stage 2 │─→│ Stage 3 │─→│ Stage 4 │
│ Extract │  │Classify │  │ Enrich  │  │ Format  │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
                                            │
                                            ▼
                                         Output
```

### State Management

Each stage receives the previous stage's output as its full context. Pipeline controller tracks which stage is in progress. Idempotency: each stage must be safe to retry without side effects.

### Governance

Policy checks at stage boundaries (each stage is a policy enforcement point). Output schema validation between stages. Pipeline configuration versioned.

### Enterprise Suitability ★★★★★

Excellent fit for: document processing, ETL with AI enrichment, content moderation (extract → classify → flag → route), structured data generation. Easiest topology to test, debug, and govern.

---

## 7. Parallel Fan-Out

### Problem

A task can be decomposed into independent sub-tasks that can execute concurrently. Sequential execution is too slow; parallel execution dramatically reduces end-to-end latency.

### Key Controls

**Retry budget coordination:** each sub-agent has independent retry budget, but coordinator enforces global retry cap. **Partial failure handling:** decide upfront — fail-all, best-effort, or minimum-N-of-M. **Result deduplication:** parallel agents may retrieve the same content.

### Enterprise Suitability ★★★★★

Excellent for: multi-source research, parallel document comparison, multi-region query, A/B evaluation. Must be paired with retry-budget coordination.

---

## 8. Mesh

### Problem

Agents have peer-to-peer relationships and may discover and call each other directly without a central coordinator. Flexibility is the primary goal.

### Governance Challenges

No single policy enforcement point: every agent-to-agent edge is a trust boundary. Authorization evaluated at every call (SPIFFE workload identity + OPA/Cedar). Audit trail requires distributed tracing (W3C trace context mandatory). Cycles are possible: loop detection required at each agent.

### Enterprise Suitability ★★★☆☆

High operational complexity; avoid for most enterprise use cases. Appropriate only when coordination graph cannot be known at design time (dynamic agent discovery) and agents are well-governed microservices with strong identity.

---

## 9. Swarm

### Problem

A large number of simple agents collectively solve a problem through local interactions and emergent behavior. No central coordinator; behavior emerges from the aggregate.

### Enterprise Suitability ★★☆☆☆

Currently a research topology. Difficult to govern, audit, or explain. Not recommended for production enterprise systems in 2026.

---

## 10. Committee / Ensemble

### Problem

A single agent's output may be unreliable for high-stakes decisions. Multiple independent agents produce outputs; an aggregator picks or synthesises the best.

### Aggregation Strategies

**Majority vote:** for classification tasks. **Best-of-N:** judge model scores each output. **Synthesis:** aggregator LLM combines insights. **Minimum-N agreement:** output accepted if N of M agents agree (quorum).

### Enterprise Suitability ★★★★☆

Strong for: high-stakes decisions (medical, legal, financial underwriting), output quality improvement, hallucination reduction. Higher cost (N× model calls).

---

## 11. Debate / Adversarial

### Problem

Complex decisions benefit from opposing viewpoints. Agents argue opposing positions; an arbiter decides based on the debate.

### Enterprise Suitability ★★★☆☆

Useful for: policy analysis, risk assessment, regulatory decisions requiring documented reasoning. Requires careful design to avoid debate loops.

---

## 12. Voting / Consensus

### Problem

Multiple agents vote on an outcome; decision emerges from majority or quorum.

### Enterprise Suitability ★★★☆☆

Appropriate for: distributed decision-making, fairness-critical scenarios. Sensitive to consensus threshold design.

---

## 13. Recursive / Self-Spawning

### Problem

Agent spawns sub-agents for sub-problems to enable unlimited task decomposition depth.

### Enterprise Suitability ★★★☆☆

Powerful for complex hierarchical problems but requires strict depth/cost limits to prevent runaway recursion.

---

## 14. Reflection

### Problem

Agent critiques its own output in a self-correction loop to improve quality.

### Enterprise Suitability ★★★★☆

Excellent for: quality improvement, error detection, iterative refinement. Adds latency and cost; best for non-time-critical tasks.

---

## 15. Judge / Critic

### Problem

Separate judge agent scores another agent's output, enabling quality control and feedback loops.

### Enterprise Suitability ★★★★★

Powerful pattern for: quality gates, hallucination detection, compliance verification, human-in-the-loop workflows.

---

## 16. Human-in-the-Loop (HITL) Hybrid

### Problem

Embedding human approval gates at critical decision points ensures human oversight and accountability.

### Governance

Human decision gates required for: high-risk actions, novel situations, disputed outputs. Human overrides logged with identity, timestamp, and rationale.

### Enterprise Suitability ★★★★★

Essential for: regulated industries, high-stakes decisions, compliance-critical workflows. Requires clear HITL UX and approval SLA management.

---

## Selecting Patterns

**Simple task, clear specialization** → Supervisor-Worker or Router  
**Sequential transformation** → Pipeline  
**Parallel independent work** → Fan-Out  
**Quality-critical decision** → Committee/Ensemble or Judge  
**Adaptive planning** → Planner-Executor  
**Scale with uniform tasks** → Manager-Worker Pool  
**High-stakes/regulated** → Supervisor-Worker + HITL Hybrid  
**Enterprise default** → Supervisor-Worker + Router + Pipeline combination
