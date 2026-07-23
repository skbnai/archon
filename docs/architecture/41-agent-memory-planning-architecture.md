---
doc_type: reference-architecture
domain: architecture
topic_id: agent-memory-planning-architecture
title: "Agent Memory & Planning Architecture"
date_created: 2026-07-07
last_reviewed: 2026-07-10
status: current
covers_version: "as of 2026-07-10"
aliases:
  - agent memory planning
  - memory architecture planning architecture
supersedes:
  - docs/enterprise-architecture/ai-architecture/agent-memory-planning-architecture.md
tags:
  - enterprise-ai-architect
  - agentic-systems
  - memory-architecture
  - planning
  - state-management
---

# Agent Memory & Planning Architecture

Volume 4 of the harness architecture series. Covers the two subsystems that give agents continuity: **memory** (full taxonomy, extract-consolidate-retrieve pipeline, end-to-end lifecycle controls, security) and **planning** (plan as versioned first-class artifact, planning modes, failure recovery, governance).

Related volumes: [Vol 1: Harness & Orchestration](./44-ai-harness-architecture-orchestration.md); [Vol 3: MCP & A2A Deep Dive](./pathname:///archon/architecture/mcp-a2a-protocol-deep-dive); [Security Architecture & Guardrails](./pathname:///archon/architecture/agentic-ai-security-guardrails).

---

## Memory Taxonomy and Store Mapping

Seven distinct memory types, each with its own store, lifecycle, and risk profile. Conflating them (one vector DB for everything) is the most common memory architecture mistake.

| Memory Type | Contents | Store | Lifecycle |
|---|---|---|---|
| **Working memory** | Current context: task, recent observations | Context manager (in-loop) | Per-iteration; compaction under pressure |
| **Scratchpad** | Agent's explicit notes/todo (context offloading) | Sandbox FS / object store per task | Task TTL; Claude Code/Manus pattern—agents write plans to files |
| **Conversation memory** | Session transcript | Session store (KV/DB) | Session TTL; summarized on rollover |
| **Episodic** | What happened: past tasks, outcomes, decisions, feedback | Event store / document DB; embedded for recall | Long TTL; legal-hold aware |
| **Semantic** | Facts about world/user/org ("customer X prefers Y") | Vector store + knowledge graph for relational facts | Curated; confidence + provenance per fact |
| **Procedural** | How-to knowledge: playbooks, learned tool sequences, skills | Git-backed skill/prompt registry | Versioned like code; reviewed like code |
| **Shared memory** | Cross-agent blackboard/workspace | Namespaced KV/graph/object store | Explicit ACLs; highest-risk store |

---

## The Extract–Consolidate–Retrieve Pipeline

Managed offerings all implement the same pipeline:

```
Raw turns
  → Extraction (model distills candidate memories)
  → Consolidation (dedupe, conflict resolution, update-vs-insert)
  → Retrieval (hybrid vector + keyword + graph, recency/importance-weighted)
```

| Engine | Approach | Distinguishing Property |
|---|---|---|
| **Mem0** | Extract-and-retrieve layer in front of any LLM; single-pass ADD-only extraction with cross-memory entity linking | Lightest integration; broadest framework support; fast retrieval (~80ms p50) |
| **Zep** | Temporal knowledge graph (Graphiti): extracts entities/facts with time validity | Answers "what was true on date X"; bi-temporal queries; ~150ms retrieval |
| **Letta** | Full agent runtime with memory hierarchy: memory blocks, archival, recall memory | Stateful agents as unit of computation, not bolt-on layer |
| **AgentCore Memory** | Managed short/long-term with configurable extraction strategies | Fully managed; namespaced retrieval injected pre-reasoning |

Most production systems combine a dedicated memory engine with separate storage layer—one tool rarely covers both extraction and retrieval at scale.

---

## Memory Lifecycle Controls (End-to-End)

**Write (gated) → classify → store (encrypted, namespaced) → retrieve (entitlement-filtered) → age (TTL/decay) → archive or erase** — every mutation is an audit event.

### TTL & Garbage Collection

Every record carries `{created, last_accessed, ttl, importance}`. GC = expiry + importance-decay + orphan sweep (memories referencing deleted tasks/users).

**GDPR erasure must cascade**: Source-document deletion must cascade to derived memories, embeddings, caches, and summaries. Maintain a derivation index (memory → sources) or you cannot comply.

### Compaction & Summarization

At ~70–80% of context budget, summarize oldest turns into structured digests (decisions, open items, artifact refs—not prose). Checkpoint pre-compaction transcript to evidence store.

Summarization is lossy: pin invariants (task goal, constraints, approvals granted) so they survive every compaction. An agent that forgets an approval was denied is a governance incident, not a quality bug.

### Checkpointing & Versioning

Memory-affecting steps commit with task checkpoint, enabling replay and time-travel debugging. Long-term stores keep append-only versions of mutated facts (who/what/when/why)—memory edits are audit events.

### Conflict Resolution & Consistency

Last-write-wins is wrong for facts. Use per-fact versions with source confidence; surface contradictions to consolidation model or human queue.

| Scope | Promise |
|---|---|
| Within a task | Read-your-writes |
| Across agents | Eventual |
| Retrieval | **Snapshot reads** — query pinned to version timestamp; task's evidence set is stable, reproducible |

---

## Memory Security

**Namespaces & ACLs**: Namespace = `{tenant, principal, agent, purpose}`; ReBAC answers per-record access. Retrieval queries post-filtered by caller's entitlements—an agent must never retrieve what its human principal couldn't read.

**PII & encryption**: Classify at write; tokenize/redact per policy; encryption at rest with per-tenant keys (BYOK for regulated); field-level encryption for sensitive. Embeddings of sensitive text are themselves sensitive—protect vector stores at same tier as source data.

**Poisoning**: Treat memory writes from tool results/web as untrusted (provenance tags); quarantine-and-review pipeline for low-trust writes; anomaly detection on write patterns; recovery primitive = bulk invalidation by provenance.

---

## Planning Architecture

### The Plan as a First-Class Artifact

**Production doctrine**: the plan is a versioned data structure, not a thought. Represent as goal tree/dependency DAG:

```
node = {intent, preconditions, action binding (tool/agent),
        acceptance criteria, compensation, risk class, budget}
edges = data/control dependencies
```

Benefits:
- Pre-execution review & approval
- Cost estimation
- Parallelization
- Resumability
- Diffable re-planning (auditable adaptation)

### Planning Modes

**Hierarchical (HTN-style)**: Supervisor decomposes goal → sub-goals → executable steps; each level owns abstraction; matches hierarchical orchestration.

**Adaptive / re-planning**: Plan-execute-observe with bounded re-plan triggers (step failure, precondition invalidation, budget threshold, new contradicting information). Cap re-plan count; escalate at cap (thrash detection).

**Reflection & verification—two distinct gates**:

| Gate | Question | Who | Cost |
|---|---|---|---|
| **Reflection** | Was that step good? | Self (same model) | Cheap |
| **Verification** | Does output meet acceptance criteria? | Independent: deterministic checks first, critic model second | Higher—apply at merge points |

Attach acceptance criteria at plan time; verification without pre-declared criteria degenerates into vibes.

**Distributed & shared plans**: Supervisor owns master plan; workers own sub-plans and report plan-relevant events, not transcripts. Shared plans in state store with optimistic concurrency; CRDTs only for append-only progress logs.

### Failure Recovery Mapping

| Failure Class | Response |
|---|---|
| Step-transient | Retry (idempotent) |
| Step-semantic | Local re-plan |
| Precondition collapse | Subtree re-plan |
| Pivot-step failure (non-compensatable) | **Halt + human** |
| Systemic (budget/kill-switch) | Checkpoint + suspend |

Compensation execution order = reverse-topological over completed mutating nodes (Saga pattern).

### Plan Governance

- Plan versions retained with task record
- High-risk patterns (pivot actions, regulated data, external egress) require approval at plan time AND execution of pivot step—plans drift
- Plan-time estimation feeds cost manager's admission decision
- Maturity end-state: library of approved plan templates (procedural memory); agents instantiate reviewed templates; only free-plan inside declared gaps

---

## Architect's Checklist

- [ ] Seven memory types mapped to own store and lifecycle
- [ ] Derivation index in place; GDPR erasure cascades
- [ ] Compaction at 70–80% produces structured digests; invariants pinned
- [ ] Per-fact versioning with confidence + provenance; contradictions surfaced
- [ ] Retrieval post-filtered by caller entitlements
- [ ] Vector stores protected at source data classification tier
- [ ] Provenance-tagged writes; quarantine pipeline; bulk-invalidation-by-provenance tested
- [ ] Plans represented as versioned DAGs with acceptance criteria and compensations per node
- [ ] Re-plan triggers bounded and capped; thrash escalates to human
- [ ] Pivot steps re-approved at execution time, not just plan time
- [ ] Approved plan-template library on roadmap as procedural-memory end-state

---

## Sources

- AgentMarketCap — Agent Memory at Scale 2026: Letta, Zep, Mem0, LangMem Compared
- Anthropic — How we built our multi-agent research system
- Zylos Research — Durable Execution for AI Agent Runtimes
