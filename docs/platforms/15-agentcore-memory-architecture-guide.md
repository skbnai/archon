---
title: "AgentCore Memory Architecture Guide"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-memory-architecture-guide
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/aws/AgentCore_Memory_Architecture_Guide.md]
tags: [aws, agentcore, memory, strands, session-management]
covers_version: "v3.0, June 2026"
---

Amazon Bedrock AgentCore Memory (GA October 2025, latest update June 2026) is the fully managed memory layer for AWS AI agents. It eliminates the need to manually orchestrate DynamoDB, OpenSearch, Redis, and custom retrieval logic. Built on Firecracker microVMs for session isolation and a purpose-built two-tier memory architecture (short-term events + long-term vector store), it enables agents to maintain context within a session, resume across sessions, and recover gracefully when memory has expired. This guide covers the complete session resume lifecycle — the most commonly misunderstood aspect of production memory architectures — with a focus on the Strands framework, EU banking compliance, and session resume patterns.

## What's New — Release Timeline (2025–2026)

AgentCore has moved extremely fast since its announcement. This timeline captures every significant release, validated against official AWS documentation and trusted community sources as of June 2026.

| Date | Milestone | Details |
|---|---|---|
| Jul 2025 | AWS Summit NY Announcement | AgentCore Memory announced. Short-term + long-term memory, Strands SDK integration revealed. |
| Aug 2025 | AWS Blog Published | Official deep-dive: memory resource, events, strategies, retrieval API documented publicly. |
| Oct 2025 | General Availability (GA) | All AgentCore services GA. VPC, PrivateLink, CloudFormation, resource tagging added. A2A protocol support in Runtime. Self-managed memory strategy added. 9 AWS regions including eu-central-1 and eu-west-1. |
| Dec 2025 | AgentCore Policy Preview | Natural language → Cedar policy enforcement. AgentCore Evaluations (13 evaluators + custom). Episodic memory strategy GA. |
| Feb 2026 | Stateful Runtime Environment | Firecracker microVM per session. Persistent session storage (`/mnt/workspace`, S3-backed). 15-min idle timeout (configurable to 28800s). 8-hour max microVM lifetime. Warm-pool pre-warming capability. |
| Mar 2026 | Performance Benchmarks | Pre-warmed sessions 90% faster: latency from ~2.9s to ~250ms average. AgentCore CLI ships (CDK-based IaC, Terraform coming). |
| Apr 2026 | AgentCore CLI GA | CLI deploys agents as IaC with audit history. Harness pattern: define model + tools + system prompt, no orchestration code. Model-agnostic: switch models mid-session. AI coding assistant skills (Claude Code, Codex, Kiro) included. |
| May 2026 | Strictly Consistent Metadata | New `STRICTLY_CONSISTENT` extraction type on LTM metadata. Up to 3 keys per strategy. Ensures metadata passes through LLM extraction unchanged. Supports semantic, preference, and episodic strategies. |
| Jun 2026 | AWS Lambda MicroVMs | New compute primitive: dedicated Firecracker VMs per session, snapshot-based startup, suspend/resume state, up to 16 vCPU / 32 GB RAM / 32 GB disk. Complements AgentCore Runtime. Available us-east-1, eu-west-1, ap-northeast-1. |

> **Strictly Consistent Metadata (May 2026) — key impact:** previously, all metadata on long-term memory records was inferred by the LLM during extraction, meaning values could drift or be misclassified. Now, setting `extraction_type=STRICTLY_CONSISTENT` guarantees the exact value you supply arrives on the record — critical for tenant isolation, session scoping, and multi-agent routing in banking contexts.

## Executive Summary

| Dimension | Current State (June 2026) |
|---|---|
| Memory Service GA | October 2025 — 9 AWS regions (eu-central-1, eu-west-1 for EU banking) |
| Runtime Architecture | Firecracker microVM per session (Feb 2026). 15-min idle timeout, 8-hour max lifetime. |
| Memory Tiers | Short-term: raw events, 7-365d retention. Long-term: extracted vector records, indefinite. |
| Session Storage | Persistent `/mnt/workspace` S3-backed filesystem. Survives microVM termination. 14-day idle retention. |
| New in 2026 | Stateful runtime, strictly consistent metadata, Lambda MicroVMs, AgentCore CLI, A2A protocol |
| Strands SDK | `AgentCoreMemorySessionManager`: STM + LTM with hooks. Prompt caching `CacheConfig(strategy='auto')`. |
| Resume When STM Expires | Long-term memory retrieval + session metadata (DynamoDB) reconstructs conversation context |
| EU Banking | CMK mandatory, VPC/PrivateLink, eu-central-1 primary, GDPR Art. 17 erasure workflow required |
| Token Optimisation | 65% of enterprise AI failures stem from context drift (not exhaustion). 70% compaction threshold. |

## AgentCore Architecture — Core Concepts

### Memory Resource, Events & Namespaces

A **Memory Resource** is the top-level logical container. It holds raw **Events** (short-term) and extracted **Memory Records** (long-term). Organisation is via a hierarchical namespace: `/strategy/{strategyId}/actor/{actorId}/session/{sessionId}/`. IAM conditions on namespace paths enforce multi-tenant isolation. The trailing slash is mandatory to prevent prefix collisions in multi-tenant applications.

| Component | Type | Stored As | Retention | Retrieval API |
|---|---|---|---|---|
| Memory Resource | Container | Logical (no storage cost) | Persistent | N/A — defines policies |
| Events | Short-term | Append-only event log | 7–365 days (per config) | ListEvents, GetEvent |
| Memory Records | Long-term | Vector-indexed records | Indefinite until delete | RetrieveMemoryRecords |
| Session Namespace | Scope | IAM condition key | Persistent | namespacePath filter |
| Metadata (LTM) | Annotation | String key-value pairs | Same as record | Metadata filter on retrieval |

### Five Design Principles

- **Abstracted Storage** — no DynamoDB, OpenSearch, or Redis to manage. Single API surface; the vector store is managed internally.
- **Security by Default** — encrypted at rest and in transit, AWS-managed or CMK. Per-session microVM isolation gives complete memory sanitisation on termination.
- **Continuity** — events stored chronologically; session branching for parallel tasks; the filesystem persists across microVM restarts.
- **Hierarchical Namespaces** — an `actor_id/namespace/memory_id` hierarchy, with IAM condition keys (`bedrock-agentcore:namespace`, `bedrock-agentcore:namespacePath`) for RBAC.
- **Scalable Retrieval** — internally managed vector embeddings and semantic similarity search, plus strictly consistent metadata (May 2026) for deterministic filtering.

### MicroVM Session Lifecycle (February 2026)

Each `runtimeSessionId` is bound to a dedicated Firecracker microVM. The microVM transitions through three states; understanding this lifecycle is essential for designing the session resume architecture (below).

- **ACTIVE** — the microVM is processing a sync request or executing background tasks (the agent reports `HealthyBusy` in `/ping`). All in-memory state and filesystem are available; model invocations are billed at the active rate.
- **IDLE** — no requests are being processed, but the microVM is still provisioned and billed at the idle (memory-only) rate. It responds instantly to the next invocation (a warm start, ~200ms p50 vs. ~2.9s cold), and survives up to `idleRuntimeSessionTimeout` (default 900s / 15 min).
- **TERMINATED** — the microVM is destroyed and memory sanitised after (a) the idle timeout expires, (b) the 8-hour max lifetime is reached, (c) an explicit `StopRuntimeSession` call, or (d) a health check failure. The next invocation triggers a cold start (~2.9s). Session storage (`/mnt/workspace`) survives microVM termination for 14 days.

| Lifecycle Parameter | Default | Min | Max | Notes |
|---|---|---|---|---|
| idleRuntimeSessionTimeout | 900s (15m) | 1s | 28800s | Time idle before microVM terminates. Must be &lt;= maxLifetime. |
| maxLifetime | 28800s (8h) | 1s | 28800s | Hard ceiling on microVM lifetime. New session required after this. |
| Session storage idle | 14 days | N/A | N/A | Filesystem (/mnt/workspace) retained 14 days after last activity. |
| LTM extraction latency | Async | N/A | N/A | Gap between writing events and LTM records being searchable. |

> **Pre-warming:** a benchmark (April 2026) shows pre-warmed sessions serve requests 90% faster than cold starts (2.9s → 250ms avg). Implement a heartbeat loop that pings idle sessions with `HealthyBusy` status every 10 minutes to keep them alive past the idle timeout threshold.

### Memory Lifecycle Flow

1. **Write short-term event** — a `put_events` call buffers the message to the AgentCore Memory event log (`batch_size` controls flush frequency).
2. **Async extraction fires** — after the session ends (an EventBridge trigger), the LLM-based extraction pipeline reads events and produces structured long-term memory records.
3. **Consolidation stores LTM** — extracted records are stored in the vector index under `/strategy/{id}/actor/{actorId}/namespace`, with strictly consistent metadata preserved exactly.
4. **Next session opens** — the `MemoryRetrievalHook` fires: semantic search over LTM records injects the top-K results into the system prompt before the model call.
5. **STM replay (if alive)** — if the session's short-term events are still within the retention window, the `ListEvents` API replays the raw conversation for full context reconstruction.

## Memory Types — Complete Taxonomy

### Short-Term Memory (Working Memory)

Short-term memory stores raw conversation events as an ordered, append-only log. It is the foundation of all other memory types. The key insight: short-term memory is not just for in-session context — it is the input data source for the LTM extraction pipeline. Without events, no long-term memories can be extracted.

| Property | Value | Notes |
|---|---|---|
| Retention | 7 to 365 days (per Memory Resource) | Set at resource creation — cannot change without recreation |
| Scope | Single or cross-session | Cross-session: same actor_id links sessions across time |
| batch_size | 1 to N messages | Use 10+ — reduces API calls 90%. Flush on session close. |
| Retrieval | ListEvents, GetEvent | Returns raw events in chronological order. Used for STM replay. |
| Branching | Supported | Parallel tasks within same actor context |
| Encryption | AWS-managed default or CMK | CMK mandatory for EU banking / regulated workloads |
| Session isolation | Complete per session_id | Enforced at service level — cannot be overridden |
| Expiry on LTM | Async extraction runs post-session | LTM records available after consolidation delay (not instant) |

### Long-Term Memory Strategies

| Strategy | What It Extracts | Best For | Strictly Consistent Metadata? | GDPR Basis |
|---|---|---|---|---|
| SUMMARIZATION | Condensed session highlights | Advisory sessions, troubleshooting | Supported (3 keys max) | Legitimate interest |
| USER_PREFERENCE | Likes, dislikes, behaviour patterns | Personalisation, wealth banking | Supported | Consent required |
| SEMANTIC | Domain facts, entities, relationships | KYC, product knowledge, org data | Supported | Legitimate interest |
| EPISODIC | Episodes with context and outcomes | Pattern learning, adaptation | Supported | Legit interest + audit |
| SELF-MANAGED | Anything via custom Lambda pipeline | Full control, domain-specific | N/A — operator controls fully | Operator owns fully |

> **Strictly Consistent Metadata (NEW May 2026):** set `extraction_type='STRICTLY_CONSISTENT'` on a metadata key to guarantee it passes through LLM extraction unchanged. Critical for tenant_id isolation (never let the LLM infer it), session_id scoping, conversation_thread linking, and compliance-grade record tagging. Up to 3 keys per strategy.

### Episodic Memory

A reflection agent analyses structured episodes to extract reusable patterns. When similar tasks arise, the main agent retrieves the learnings. AWS demonstrated at re:Invent an agent that learned from a solo trip booking, then automatically adjusted for a family trip three months later. This requires a quarterly EBA fairness audit for EU banking use.

> **EU Banking Warning:** episodic memory influencing credit or fraud decisions must provide a human review pathway (GDPR Art. 22). Reflection reasoning must be logged (MiFID II). EBA ML Guidelines §5.1 requires a quarterly demographic fairness audit.

### Persistent Session Storage (`/mnt/workspace`) — NEW Feb 2026

A durable, S3-backed POSIX filesystem mounted at `/mnt/workspace` inside the microVM. Unlike short-term memory (conversation events), session storage holds files, code, build artifacts, and working state. It survives microVM termination and is re-mounted when a new microVM picks up the same `runtimeSessionId`. It is retained for 14 days of inactivity.

| Capability | Short-Term Memory | Session Storage (/mnt/workspace) |
|---|---|---|
| What it stores | Conversation events (text messages) | Files, code, models, database files, build artifacts |
| Survives microVM stop? | YES (in AgentCore Memory service) | YES (S3-backed — persists for 14 days after last activity) |
| Survives session end? | YES (until retention TTL expires) | YES (until 14-day idle expiry or explicit cleanup) |
| Retrieval method | ListEvents API — chronological | POSIX filesystem (ls, cat, git, npm — standard tools) |
| Indexing | None — raw event log | None — file system traversal |
| Primary use | LTM extraction input + STM replay | Coding agents, data pipelines, long-horizon work sessions |
| Best practice | batch_size=10, flush on close | Write to /mnt/workspace; session auto-syncs to S3 |

### Retention Period Decision Matrix

| Use Case | Memory Type | Retention | GDPR Lawful Basis | Regulatory Driver |
|---|---|---|---|---|
| Customer support chat | Short-term | 7 to 30 days | Legitimate interest | CX best practice |
| Loan application | STM + Checkpoint | 90 days | Contract performance | Dispute resolution |
| Wealth management prefs | LTM (Preference) | 2 years | Consent | MiFID II suitability |
| Fraud investigation | LTM (Semantic) | 7 years | Legal obligation | 5AMLD / Art. 6(c) |
| Trading preferences | LTM (Preference) | 1 year | Consent + Legal | MiFID II Art. 25 |
| KYC entities | LTM (Semantic) | 5 years | Legal obligation | 4AMLD / 5AMLD |
| Episodic patterns | Episodic | 1yr + review | Legitimate interest | EBA ML Guidelines |
| Session workspace files | Session Storage | 14 days idle | Contract performance | Functional continuity |

## Conversation History Sidebar — Architecture

How Claude and ChatGPT build their sidebars, and how to re-imagine this on AWS AgentCore.

### How Claude / ChatGPT Build Their Sidebars

The conversation history sidebar is one of the most used features in consumer AI products. Understanding how it is built reveals the three fundamental data requirements every production agent application must satisfy — and maps directly to what AgentCore provides.

| Component | What It Stores | How It's Used | Claude Implementation |
|---|---|---|---|
| Conversation Index | Session ID, title, timestamp, last message preview | Browse sidebar, search past conversations | JSONL transcript index per project directory |
| Conversation Transcript | Full message history (user + assistant turns) | Resume: full context re-injected into model window | `*.jsonl` per session_id in `~/.claude/projects/` |
| Session Metadata | Branch/fork graph, labels, project, model used | Resume from fork, filter by project, show metadata | `sessions-index.json` |
| Cross-Session Memory | User preferences extracted from past chats | Injects personalisation into new conversations via RAG | `settings.json` + memory feature (RAG over history) |
| Search Index | Embeddings or keyword index over past messages | Find specific past conversation by content | RAG tool call visible in conversation |

Key architectural insight from Claude Code's implementation: session state is written to disk on every event, not on exit — so a crash loses nothing. Sessions are stored as JSONL files (one event per line) with unique session IDs. The sidebar is built entirely from file reads; no running agent is required. This is the pattern to replicate on AWS.

> **Claude's memory feature (2025):** chat search uses RAG over conversation history — past conversations are indexed, and the agent performs a tool call to retrieve relevant context from prior sessions. Memory is updated within 24 hours of conversation changes. Users can view, edit, import, and export memories from Settings > Capabilities.

Part 2 continues with the three layers of session state, the full AWS reference architecture for reimagining this sidebar on AgentCore, and the session catalog schema.

## Related

- [AgentCore Memory Architecture Guide (Part 2)](parts/15-agentcore-memory-architecture-guide-part2.md) — session resume lifecycle, multi-agent memory patterns, memory processors, framework comparison, token optimisation
- [AgentCore Memory Architecture Guide (Part 3)](parts/15-agentcore-memory-architecture-guide-part3.md) — Strands best practices, EU banking/GDPR compliance, security/threat model, cost optimisation, PoC-to-production journey, evaluation, Terraform IaC
- [AgentCore Memory Architecture Guide (Part 4)](parts/15-agentcore-memory-architecture-guide-part4.md) — complete resume orchestrator, session catalog API, warm pool/session close workflow, test suite
