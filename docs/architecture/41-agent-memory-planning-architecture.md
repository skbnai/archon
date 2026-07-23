---
doc_type: reference-architecture
domain: architecture
topic_id: agent-memory-planning-architecture
title: "Agent Memory & Planning Architecture"
date_created: 2026-07-07
last_reviewed: 2026-07-23
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

> **Current as of July 2026.** This guide covers the two subsystems that give agents continuity: **memory** (the full taxonomy, the extract-consolidate-retrieve pipeline, end-to-end lifecycle controls, and memory security) and **planning** (the plan as a versioned first-class artifact, planning modes, failure recovery, and plan governance). It is Volume 4 of the harness architecture series ([Vol 1: Harness & Orchestration](./44-ai-harness-architecture-orchestration.md); [Vol 3: MCP & A2A Deep Dive](./58-mcp-a2a-protocol-deep-dive.md)); memory-poisoning threats are covered in depth in [Security Architecture & Guardrails](pathname:///archon/trust/agentic-ai-security-guardrails).

---

## 1. Memory Taxonomy and Store Mapping

Seven distinct memory types, each with its own store, lifecycle, and risk profile. Conflating them (one vector DB for everything) is the most common memory architecture mistake.

| Memory type | Contents | Store | Lifecycle |
| ------------- | ---------- | ------- | ----------- |
| **Working memory** | Current context window: task, recent observations | Context manager (in-loop) | Per-iteration; compaction under pressure |
| **Scratchpad** | Agent's explicit notes/todo files ("context offloading") | Sandbox FS / object store per task | Task TTL; the Claude Code/Manus pattern — agents write plans & findings to files instead of holding them in-window |
| **Conversation memory** | Session transcript | Session store (KV/DB) | Session TTL; summarized on rollover |
| **Episodic** | What happened: past tasks, outcomes, decisions, feedback | Event store / document DB, embedded for recall | Long TTL; legal-hold aware |
| **Semantic** | Facts about the world/user/org ("customer X prefers Y") | Vector store + **knowledge graph** for relational facts | Curated; confidence + provenance per fact |
| **Procedural** | How-to knowledge: playbooks, learned tool sequences, **skills** (Anthropic Skills-style versioned instruction packages) | Git-backed skill/prompt registry | Versioned like code; **reviewed like code** |
| **Shared memory** | Cross-agent blackboard/workspace | Namespaced KV/graph/object store | Explicit ACLs; **the highest-risk store** |

---

## 2. The Extract–Consolidate–Retrieve Pipeline

Managed offerings (AgentCore Memory with short-term + long-term extraction strategies; Azure AI Foundry threads/memory; Mem0/Zep/Letta-class engines) all implement the same pipeline:

```
Raw turns
  → Extraction      (model distills candidate memories)
  → Consolidation   (dedupe, conflict resolution, update-vs-insert)
  → Retrieval       (hybrid vector + keyword + graph, recency/importance-weighted)
```

The engines differ in *how* each stage works, which matters for selection:

| Engine | Approach | Distinguishing property |
| -------- | ---------- | ------------------------ |
| **Mem0** | Extract-and-retrieve layer in front of any LLM call; v3 (April 2026) moved to single-pass ADD-only extraction with cross-memory entity linking | Lightest integration, broadest framework support; fastest retrieval (~80ms p50) |
| **Zep** | Temporal knowledge graph (Graphiti engine): extracts entities/facts, attaches **time validity** | Answers "what was true on date X" — bi-temporal queries; ~150ms retrieval (graph traversals) |
| **Letta** (ex-MemGPT) | Full agent runtime with memory hierarchy: memory blocks, archival memory, recall memory | Stateful agents as the unit of computation, not a bolt-on layer |
| **AgentCore Memory** | Managed short/long-term with configurable extraction strategies; namespaced retrieval injected pre-reasoning | Fully managed; harness queries configured namespaces before each reasoning pass |

Most production systems combine a dedicated memory engine with a separate storage layer (vector DB/Redis) — one tool rarely covers both extraction and retrieval at scale.

---

## 3. Memory Lifecycle Controls (End-to-End)

The end-to-end life of a memory record: **write (gated) → classify → store (encrypted, namespaced) → retrieve (entitlement-filtered) → age (TTL/decay) → archive or erase (cascaded)** — with every mutation an audit event.

```mermaid
stateDiagram-v2
    [*] --> Write: Agent/Tool<br/>writes fact
    Write --> Classify: Tag trustworthiness<br/>source, TTL, sensitivity
    Classify --> Store: Encrypt + namespace<br/>in persistent layer
    Store --> Retrieve: Query (vector, keyword,<br/>graph) + ACL filter
    Retrieve --> Age: Track access;<br/>importance-decay
    Age --> Archive: TTL expired<br/>or low-access
    Age --> Erase: Cascade delete<br/>on source removal
    Archive --> [*]
    Erase --> [*]
    
    note right of Write
        Gating: validate source,
        check poison signals
    end note
    
    note right of Retrieve
        Post-filter by caller
        entitlements (ReBAC)
    end note
```

**Memory lifecycle state machine:** Each memory record progresses through gated write, classification, encrypted storage, entitlement-filtered retrieval, and age-based disposal with cascading deletion for compliance.

### 3.1 TTL & Garbage Collection

Every record carries `{created, last_accessed, ttl, importance}`. GC = expiry + importance-decay eviction + orphan sweep (memories referencing deleted tasks/users).

:::warning GDPR erasure must cascade
    Source-document deletion must cascade to **derived memories, embeddings, caches, and summaries that quote it**. Maintain a **derivation index** (memory → sources) or you cannot comply. This is the single most commonly missed requirement in agent memory design.
:::

### 3.2 Compaction & Summarization

At ~70–80% of context budget, summarize the oldest turns into **structured digests** (decisions, open items, artifact refs — not prose vibes). Checkpoint the pre-compaction transcript to the evidence store so audit never loses raw history.

Summarization is lossy: **pin invariants** (task goal, constraints, approvals granted) so they survive every compaction. An agent that forgets an approval was denied — because the denial got summarized away — is a governance incident, not a quality bug.

### 3.3 Checkpointing & Versioning

Memory-affecting steps commit with the task checkpoint (Vol 1 §2), enabling replay and time-travel debugging. Long-term stores keep append-only versions of mutated facts (who/what/when/why) — **memory edits are audit events**.

### 3.4 Conflict Resolution & Consistency

Last-write-wins is wrong for facts. Use per-fact versions with source confidence, and surface contradictions to the consolidation model or a human queue.

Consistency promises to engineer for:

| Scope | Promise |
| ------- | --------- |
| Within a task | Read-your-writes |
| Across agents | Eventual |
| Retrieval | **Snapshot reads** — query pinned to a version timestamp so a task's evidence set is stable and reproducible |

---

## 4. Memory Security

Full threat treatments in [Security Architecture & Guardrails](pathname:///archon/trust/agentic-ai-security-guardrails) (memory poisoning, vector DB poisoning). The architectural controls:

**Namespaces & ACLs.** Namespace = `{tenant, principal, agent, purpose}`; ReBAC answers per-record access. Retrieval queries are **post-filtered by the caller's entitlements** — an agent must never retrieve what its human principal couldn't read. RAG permission-mirroring failures are a top audit finding.

**PII & encryption.** Classify at write; tokenize/redact per policy; encryption at rest with per-tenant keys (BYOK for regulated tenants); field-level encryption for sensitive attributes. **Embeddings of sensitive text are themselves sensitive** — embedding-inversion attacks are practical — so protect vector stores at the same tier as source data.

**Poisoning.** Treat memory writes from tool results/web content as untrusted (provenance tags); quarantine-and-review pipeline for low-trust writes; anomaly detection on write patterns (sudden instruction-like memories, cross-tenant similarity spikes); and the recovery primitive — **bulk invalidation by provenance** ("purge everything derived from source X between dates").

---

## 5. Planning Architecture

### 5.1 The Plan as a First-Class Artifact

Production doctrine: **the plan is a versioned data structure, not a thought.** Represent it as a goal tree / dependency DAG:

```
node = {intent, preconditions, action binding (tool/agent),
        acceptance criteria, compensation, risk class, budget}
edges = data/control dependencies
```

What this buys you:

- **Pre-execution review & approval** — governance sees the plan before actions run
- **Cost estimation** — plan-time estimates feed the cost manager's admission decision
- **Parallelization** — derived from the DAG, not guessed
- **Resumability** — plan + checkpoint = restart point
- **Diffable re-planning** — plan v2 vs. v1 shows exactly what changed and why: *auditable adaptation*

This is the same lesson Anthropic's multi-agent research system reported operationally: the lead agent saves its plan to memory before spawning subagents, because a plan held only in the context window does not survive truncation.

### 5.2 Planning Modes

**Hierarchical (HTN-style).** Supervisor decomposes goal → sub-goals → executable steps; each level owns its abstraction; matches hierarchical orchestration (Vol 1 §6).

**Adaptive / re-planning.** Plan-execute-observe with **bounded re-plan triggers**: step failure after retries, precondition invalidation, budget threshold, new information contradicting assumptions. Cap the re-plan count; escalate to human at the cap (thrash detection).

**Reflection & verification — two distinct gates:**

| Gate | Question | Who | Cost |
|------|----------|-----|------|
| **Reflection** | Was that step good? | Self (same model) | Cheap |
| **Verification** | Does output meet acceptance criteria? | Independent: deterministic checks first (tests pass, schema valid, totals reconcile), critic model second | Higher — apply at merge points |

Attach acceptance criteria **at plan time**; verification without pre-declared criteria degenerates into vibes.

**Distributed & shared plans.** In multi-agent settings the supervisor owns the master plan; workers own sub-plans and report **plan-relevant events, not transcripts**. Shared plans live in the state store with optimistic concurrency; CRDTs only for append-only progress logs. Cross-org (A2A) planning shares **task contracts, never internal plan internals** ([Vol 3 §6](./58-mcp-a2a-protocol-deep-dive.md)).

### 5.3 Failure Recovery Mapping

| Failure class | Response |
| --------------- | ---------- |
| Step-transient | Retry (idempotent) |
| Step-semantic | Local re-plan |
| Precondition collapse | Subtree re-plan |
| Pivot-step failure (non-compensatable) | **Halt + human** |
| Systemic (budget/kill-switch) | Checkpoint + suspend |

Compensation execution order = **reverse-topological over completed mutating nodes** (Saga pattern).

### 5.4 Plan Governance

- Plan versions are retained with the task record.
- High-risk plan patterns (touching pivot actions, regulated data, external egress) require approval **at plan time and again at execution of the pivot step** — plans drift between approval and execution.
- Plan-time estimation feeds the cost manager's admission decision.
- The maturity end-state: a library of **approved plan templates** (procedural memory). Agents instantiate reviewed templates and only free-plan inside declared gaps — autonomy budgeted where the process is genuinely unknown, structure everywhere else.

---

## 6. How Industry Implements

**AWS AgentCore Memory** — managed memory layer storing conversation history, extracted facts, and user preferences across sessions, backed by a vector store with a semantic retrieval API; long-term memories are retrieved from configured namespaces and injected before the agent reasons. The namespace model maps directly onto §4's `{tenant, principal, agent, purpose}` doctrine.

**Zep (Graphiti)** — the temporal-knowledge-graph approach in production: entities and facts carry time validity, enabling "what was true on date X" queries — effectively §3.4's snapshot-read consistency implemented at the engine level.

**Mem0** — the lightweight extract→consolidate→retrieve loop; v3's single-pass ADD-only extraction with cross-memory entity linking is a direct answer to the consolidation-cost problem (~80ms p50 retrieval).

**Letta** — the MemGPT lineage: memory hierarchy (blocks/archival/recall) as an agent *runtime* concern rather than an external service — closest to the "stateful agent as unit of computation" model.

**LangGraph checkpointers** — the reference implementation of §3.3: graph state saved at each superstep, organized by thread, with PostgreSQL checkpointing for step-level recovery. Known limit: checkpointers save state *between* nodes, not inside a node — pair with Temporal when node-internal durability matters (see Vol 1 §6.3).

**Claude Code / Manus scratchpad pattern** — context offloading to files as first-class memory: plans and findings written to the sandbox filesystem survive compaction, are diffable, and cost zero context until re-read. Anthropic's research system institutionalized the same move (plan saved to memory before subagent spawn).

**Market signal** — the agent-memory market in 2026 resembles the vector-DB market of 2022-23: several technically distinct approaches (extraction layers, temporal graphs, memory-native runtimes), early enterprise adoption, overlapping buyers, consolidation expected. Architect behind an abstraction: keep the memory *interface* (extract/consolidate/retrieve + namespace + provenance) yours, and treat the engine as swappable.

---

## 7. Architect's Checklist

- [ ] Each of the 7 memory types mapped to its own store and lifecycle — no single-store-for-everything
- [ ] Derivation index in place; GDPR erasure cascades to memories, embeddings, caches, summaries
- [ ] Compaction at 70–80% budget produces structured digests; invariants pinned; pre-compaction transcript checkpointed
- [ ] Per-fact versioning with confidence + provenance; contradictions surfaced, not overwritten
- [ ] Retrieval post-filtered by caller entitlements (RAG permission-mirroring verified by audit)
- [ ] Vector stores protected at the same classification tier as source data
- [ ] Provenance-tagged writes; quarantine pipeline; bulk-invalidation-by-provenance tested
- [ ] Plans represented as versioned DAGs with acceptance criteria and compensations per node
- [ ] Re-plan triggers bounded and capped; thrash escalates to human
- [ ] Pivot steps re-approved at execution time, not just plan time
- [ ] Approved plan-template library on the roadmap as the procedural-memory end-state

---

## Sources

- [AgentMarketCap — Agent Memory at Scale 2026: Letta, Zep, Mem0, LangMem Compared](https://agentmarketcap.ai/blog/2026/04/10/agent-memory-vendor-landscape-2026-letta-zep-mem0-langmem)
- [APIScout — Zep vs Mem0 vs Letta Agent Memory API (2026)](https://apiscout.dev/guides/zep-vs-mem0-vs-letta-agent-memory-api-2026)
- [Mem0 — Graph-Based Memory Solutions Compared](https://mem0.ai/blog/graph-memory-solutions-ai-agents)
- [Medium/Data Reply — Stateful Agents on Amazon Bedrock: AgentCore Runtime & Memory](https://medium.com/data-reply-it-datatech/stateful-agents-on-amazon-bedrock-how-agentcore-runtime-solves-the-memory-problem-74ba885776e7)
- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Zylos Research — Durable Execution for AI Agent Runtimes: Checkpointing, Replay, Recovery](https://zylos.ai/research/2026-04-24-durable-execution-agent-runtimes/)
- Volume 4, *Multi-Agent AI Harness Architecture (2026) — Production Reference Guide*
