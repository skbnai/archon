---
title: "AgentCore Memory Architecture Guide (Part 2)"
doc_type: guide
domain: platforms
status: current
topic_id: agentcore-memory-architecture-guide-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, agentcore, memory, session-resume, multi-agent]
covers_version: "v3.0, June 2026"
---

> Continues from [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md), completing the conversation history sidebar architecture and covering session resume, multi-agent memory patterns, memory processors, framework comparison, and token optimisation.

## The Three Layers of Session State

Any production conversation sidebar requires three distinct layers. Conflating them leads to either data loss (too little persistence) or cost and compliance problems (too much).

| Layer | Purpose | Lifespan | Storage Mechanism | AgentCore Equivalent |
|---|---|---|---|---|
| 1. Session Catalog | List conversations, titles, timestamps, metadata for sidebar display | Permanent (user-controlled) | Low-latency key-value store per user | DynamoDB: conversations table (actor_id, session_id, title, last_updated, metadata) |
| 2. Conversation Transcript | Full message history for exact resumption of context | Session TTL (days to years) | Append-only durable log | AgentCore STM: events API (ListEvents, GetEvent). Expires per event_expiry_duration config. |
| 3. Extracted Knowledge | User preferences, facts, summaries — portable across sessions | Indefinite until deleted | Vector-indexed semantic store | AgentCore LTM: memory records (RetrieveMemoryRecords). Survives STM expiry permanently. |

## Reimagining the Sidebar on AWS AgentCore

The complete AWS architecture for a Claude-style conversation history sidebar uses AgentCore Memory as the backbone. Every layer maps to a specific AWS service with clear responsibilities and data contracts:

- **Frontend Sidebar (React / React Native)** — displays the conversation list from DynamoDB: title, timestamp, last-message preview, labels. Triggers resume on click; allows rename, fork, delete, search. Connects via AppSync or REST API Gateway → Lambda → DynamoDB (session catalog).
- **Session Catalog (DynamoDB)** — stores `actor_id` (PK), `session_id` (SK), title, `created_at`, `last_updated_at`, `model_id`, `preview_text` (first 120 chars of the last message), `labels[]`, `is_pinned`, `parent_session_id` (for forks). A GSI on `actor_id` + `last_updated_at` supports sorted sidebar rendering.
- **Transcript Store (AgentCore STM)** — stores every event (user + assistant + tool calls) via `put_events`, retrieved via `ListEvents` for full context reconstruction on resume. Expires per `event_expiry_duration` (30–365 days); the event log is the canonical conversation record while it lives. Uses `batch_size=10`; `runtimeSessionId` maps to the DynamoDB `session_id`.
- **Knowledge Store (AgentCore LTM)** — extracted preferences, facts, and summaries that survive STM expiry, retrieved semantically via `RetrieveMemoryRecords` and injected as RAG context at session start; used for reconstruction when STM has expired. `STRICTLY_CONSISTENT` metadata tags `actor_id` and `session_id` onto records; extraction fires via an EventBridge post-session trigger.
- **Session Search (Kendra / OpenSearch)** — optional semantic search over conversation content, indexing transcript text as STM events are written, enabling "find my conversation about X" queries in the sidebar search bar. For EU banking, encrypt and keep in eu-central-1.
- **Cross-Session Summary (S3 + Lambda)** — after session close, a Lambda exports a compressed conversation summary to S3 (JSON). This is the permanent audit archive, surviving after both STM and LTM TTLs expire, used for compliance, SAR (GDPR Art. 15), and ultra-long-horizon reconstruction, with server-side KMS encryption and object tags for `actor_id`/`session_id`/date.

### Session Browser — Complete AWS Reference Architecture

```json
// DynamoDB Session Catalog -- Table Definition
{
  "TableName": "conversations",
  "AttributeDefinitions": [
    { "AttributeName": "actor_id", "AttributeType": "S" },
    { "AttributeName": "session_id", "AttributeType": "S" },
    { "AttributeName": "last_updated_at", "AttributeType": "N" }
  ],
  "KeySchema": [
    { "AttributeName": "actor_id", "KeyType": "HASH" },
    { "AttributeName": "session_id", "KeyType": "RANGE" }
  ],
  "GlobalSecondaryIndexes": [{
    "IndexName": "actor-time-index",
    "KeySchema": [
      { "AttributeName": "actor_id", "KeyType": "HASH" },
      { "AttributeName": "last_updated_at", "KeyType": "RANGE" }
    ]
  }]
}
```

```python
# Item structure per session
{
    'actor_id': 'cognito|user-uuid',        # from IdP -- NEVER user-provided
    'session_id': 'sess-uuid-001',          # maps to AgentCore runtimeSessionId
    'title': 'Q3 Fraud Review',             # user-editable, default = first msg
    'preview_text': 'Analyse the flagged...',  # first 120 chars of last assistant msg
    'created_at': 1748000000,               # Unix timestamp
    'last_updated_at': 1748090000,          # for sidebar sort order
    'model_id': 'claude-sonnet-4-6',
    'stm_expires_at': 1750682000,           # event_expiry_duration + created_at
    'stm_status': 'ALIVE',                  # ALIVE | EXPIRED | ARCHIVED
    'ltm_extracted': True,                  # True once consolidation ran
    'labels': ['fraud', 'q3-2026'],
    'parent_session_id': None,              # non-null for forked sessions
}
```

## Session Resume — The Full Lifecycle

The definitive guide to what happens when a user clicks an old conversation. This is the most commonly misunderstood aspect of production memory architectures. What happens depends entirely on the age of the conversation and which memory layers are still alive. There are four distinct scenarios, each requiring a different reconstruction strategy. The key insight: AgentCore Memory's two-tier architecture is specifically designed so that LTM survives STM expiry — meaning the agent can always reconstruct meaningful context, even from conversations months or years old.

### Scenario A: Resume Within Idle Timeout (Warm Start)

**Trigger:** the user left the conversation and returns within 15 minutes (before the idle timeout fires); the microVM is still in IDLE state.

1. **Invoke with the same runtimeSessionId** — AgentCore routes the request to the SAME microVM. Warm start: ~200ms latency, with full in-memory state intact (conversation history, tool results, loaded models).
2. **Agent continues without reconstruction** — no memory retrieval needed; the agent has full context from in-process memory, and the user sees a seamless continuation.
3. **ConsentCheckHook validates** — even on a warm resume, the consent check fires to validate the GDPR basis is still active.

> Warm resume is the ideal path — zero reconstruction cost, sub-200ms latency, no API calls to AgentCore Memory required. Design the session UI to show a "Live" indicator while the microVM is in IDLE state (poll the `/ping` endpoint, check the status field).

### Scenario B: Resume After Idle Timeout, STM Still Alive

**Trigger:** the user returns after more than 15 minutes but within the STM retention window (7–365 days depending on config). The microVM is TERMINATED — a cold start is required, but short-term events are still in AgentCore Memory.

1. **Cold start — new microVM provisions** — AgentCore provisions a fresh Firecracker microVM for the `runtimeSessionId`. No in-memory state; ~2.9s cold start latency (use a warm pool to reduce it).
2. **Session metadata loaded from DynamoDB** — the agent reads the session catalog record (`session_id`, `actor_id`, model, `stm_status='ALIVE'`, `created_at`) and confirms STM is within the retention window.
3. **LTM retrieval — semantic RAG injection** — the `MemoryRetrievalHook` fires: `RetrieveMemoryRecords` with `actor_id` and the current query. Top-K long-term memories are injected into the system prompt (~900 token budget), giving personality, preferences, and extracted knowledge.
4. **STM replay — full transcript load** — `ListEvents(memoryId, sessionId, actorId)` returns raw events in order; the agent reconstructs the full conversation history and injects it into the model context window as conversation turns.
5. **Context compaction if needed** — if the replayed transcript exceeds 70% of the context window, trigger ACON compaction: summarise early turns and retain recent turns verbatim. The system prompt and LTM stay; a transcript summary is injected instead.
6. **Session resumes — user sees continuation** — the agent has both full LTM personalisation and the full STM transcript. From the user's perspective, this is identical to Scenario A, just slightly slower to first token.

> **Critical implementation detail:** STM replay (step 4) can return very long event lists for long conversations. Always apply the 70% compaction threshold — do not inject the raw transcript blindly into context. The `MemoryRetrievalHook` must compute token count and trigger compaction before the model call.

### Scenario C: Resume After STM Expiry — Cold Reconstruction

**Trigger:** the user returns after the STM retention window has expired (7–365 days depending on config). This is the most common case for sidebar conversations that are weeks or months old. The microVM is TERMINATED, short-term events are GONE, and only LTM records and session metadata remain.

> **This is the critical architectural scenario.** The `session_id` still exists in DynamoDB (`stm_status='EXPIRED'`). The user sees the conversation in their sidebar and clicks it. This is where the LTM extraction investment pays dividends: the agent reconstructs meaningful context from extracted knowledge even without the raw transcript.

> **STRICTLY_CONSISTENT metadata is the key enabler here (May 2026):** tag every LTM record with `session_id` as a strictly consistent key when writing events. This guarantees that `RetrieveMemoryRecords?filter={session_id=X}` returns exactly the records from that session. Without this, the LLM might infer or miss session IDs during extraction, making session-scoped reconstruction unreliable.

Example system prompt injection for reconstruction:

```
=== PREVIOUS CONVERSATION CONTEXT ===
Session: Q3 Fraud Review (July 15, 2026)
Status: Resumed from archived conversation (original transcript no longer available)

CONVERSATION SUMMARY:
{summary_from_ltm_summarization_strategy}

KEY FACTS DISCUSSED:
{facts_from_ltm_semantic_strategy}

USER PREFERENCES RELEVANT TO THIS SESSION:
{preferences_from_ltm_user_preference_strategy}

IMPORTANT: Do not tell the user their transcript is unavailable. Reconstruct
naturally from the above context. Ask clarifying questions only if truly
necessary.
========================================
```

### Scenario D: Resume After Both STM and LTM Are Unavailable

**Trigger:** LTM extraction was never configured, the user deleted their data (GDPR Art. 17 erasure), the LTM retention policy has expired, or LTM records were manually purged. Only the DynamoDB session catalog entry remains.

| What Remains | What the Agent Can Recover | Graceful Degradation Strategy |
|---|---|---|
| DynamoDB metadata only | Session title, date, model, user labels | Acknowledge prior conversation by title/date only. Start fresh but contextualised. |
| S3 compressed archive | Summary exported post-session (if configured) | Load the S3 JSON archive, parse the conversation summary, inject as context. Best fallback. |
| GDPR erasure triggered | Nothing — complete deletion required by Art. 17 | Treat as a brand new session. Legal requirement — no workarounds. |
| LTM never configured | Nothing — STM-only deployment with no extraction | Lesson: always enable at minimum the SUMMARIZATION strategy. One-strategy cost is low. |

> **Best practice:** always configure the SUMMARIZATION strategy and export a compressed JSON session summary to S3 on session close (EventBridge → Lambda → S3 put). This creates a permanent, cost-negligible archive that acts as the final fallback for Scenario D reconstruction. A 45-minute conversation compresses to ~2-5 KB.

### Decision Tree — Which Resume Path to Use

| Condition | Path | Strategy | Expected Quality |
|---|---|---|---|
| microVM IDLE + same runtimeSessionId | A | Direct invocation — no memory calls | Perfect — full context |
| microVM TERMINATED + STM events exist | B | Cold start + LTM RAG + STM event replay + compaction | Excellent — full transcript |
| STM expired + LTM records exist | C | Cold start + LTM session-scoped retrieval + summary | Good — reconstructed context |
| STM expired + LTM exists but no session tag | C- | Cold start + actor-scoped LTM retrieval only | Partial — cross-session prefs only |
| STM expired + S3 archive exists | D-S3 | Cold start + S3 JSON archive load | Moderate — summary only |
| Nothing remains except DDB metadata | D | Acknowledge title/date, start contextualised fresh | Minimal — graceful degradation |
| GDPR erasure requested | E | Delete all data layers, treat as new user | Zero — legal requirement |

## Multi-Agent Memory Patterns — Pros & Cons

### Single Agent — Isolated Namespace

Each agent owns a dedicated Memory Resource with no sharing; `actor_id` maps to a specific user. Simplest and most secure.

**Advantages:** strongest isolation (no cross-agent contamination); simplest IAM (one role, one resource); easiest Art. 17 erasure (delete one resource); lowest operational complexity.
**Disadvantages:** knowledge siloed (Agent B cannot benefit from Agent A); duplicate storage across agents; no collaborative intelligence.

> **Recommendation:** default starting point. Use for support bots, simple chatbots, single-function agents.

### Shared Memory — Publisher / Subscriber

A dedicated writer (e.g. a KYC Collector) persists facts; downstream readers (Credit, Risk) are read-only consumers via namespace IAM.

**Advantages:** a single source of truth (KYC written once, consumed by many); read agents decoupled from write logic; fine-grained IAM namespace conditions; namespace-level audit trail.
**Disadvantages:** the writer is a single point of failure for data quality; readers may act on stale data if consolidation is delayed; namespace design requires upfront information architecture; the cross-agent trust model must be maintained in IAM.

> **Recommendation:** KYC-driven workflows. Writer = KYC/onboarding agent; readers = all downstream decision agents.

### Multi-Write Hub & Spoke

Sub-agents write to their own namespaces in parallel; an orchestrator consolidates into a final shared namespace after all complete.

**Advantages:** concurrency-safe (no race conditions); modular (each sub-agent owns its namespace); the orchestrator provides a quality gate before promotion; supports complex parallel workflows.
**Disadvantages:** higher orchestration complexity (must track all completions); consolidation latency (the shared namespace isn't updated until all finish); more IAM roles to manage; a saga pattern is needed for partial failure handling.

> **Recommendation:** complex loan origination, KYC review, compliance workflows with 3+ specialist sub-agents.

### Transaction Ledger

An append-only, immutable event ledger where every decision is timestamped and signed. Required for MiFID II, DORA, AML audit.

**Advantages:** full auditability (every decision traceable); tamper-evident (HMAC signatures); regulatory-ready for MiFID II and AML; replay capability for past sessions.
**Disadvantages:** storage grows unbounded (must tier to S3 WORM); query complexity for ledger replay; HMAC computation adds write latency; no correction (errors compensated, not overwritten).

> **Recommendation:** mandatory for EU banking agents making or influencing financial decisions. Pair with S3 Object Lock WORM.

## Memory Processors & Extractors

Pipeline order: Ingest → PII Redact → Entity Extract → Summarize → Consolidate → Vector Store → Retrieve. Non-negotiable for GDPR compliance.

| Stage | Method | Detection / Output | Latency | EU Banking Note |
|---|---|---|---|---|
| PII Redact | Regex patterns | IBAN, card, NIN, passport | ~1ms | Necessary — insufficient alone |
| PII Redact | Amazon Comprehend | Names, addresses, phones, emails, orgs | 50-200ms | Good AWS-native foundation |
| PII Redact | Presidio (OSS) | Contextual NER, multilingual EU support | 100-500ms | Excellent for German/French PII |
| PII Redact | Custom Lambda | ISIN, LEI, BIC/SWIFT, product codes | Varies | Required for financial services |
| PII Redact | Bedrock Guardrails | Output-side filter on retrieval | 10-50ms | Complementary — not write-time |
| Entity Extract | Self-managed Lambda | Domain JSON: risk appetite, products, goals | Varies | Recommended for banking agents |
| Summarize | SUMMARIZATION strategy | Condensed session highlights | Post-session | Standard — use as minimum baseline |
| Consolidate | EventBridge trigger | Dedup + merge + vector index write | Async | Never per-message. Post-session only. |

## Framework Comparison — Pros & Cons

| Framework | Architecture | Key Advantages | Key Disadvantages | Best For |
|---|---|---|---|---|
| AgentCore Memory (AWS) | Fully managed serverless. Vector store + event log behind a single API. Firecracker microVMs. | Zero infrastructure; native AWS IAM + KMS; VPC/PrivateLink; Strands SDK hooks; strictly consistent metadata (2026); session storage /mnt/workspace; GDPR-ready EU regions | AWS lock-in; limited graph memory; cross-region risk for EU; LTM extraction latency (async); less customisation vs. OSS | AWS teams; EU banking; regulated; zero infra |
| Mem0 (OSS / Managed) | Hybrid: vector DB + LLM extraction. Graph memory in Pro tier. 48K+ GitHub stars. | Largest community; framework-agnostic; self-hosted or managed; strong personalisation; LangChain/LlamaIndex native; single-pass extraction (2026) | Graph memory costs extra; 7-8s latency at scale; no native Strands hooks; GDPR burden on operator; separate infra for self-hosted | Non-AWS stacks; prototyping; personalisation agents |
| Zep / Graphiti (Graph) | Knowledge graph with ontology-aware edges. Temporal reasoning. Sub-100ms retrieval. | Sub-100ms retrieval; best temporal reasoning; SOC2/HIPAA/GDPR certified; strong for audit trails | Manual graph management; $15/M tokens (premium); smaller ecosystem; steeper learning curve | Compliance; policy-tracking; temporal fact evolution |
| LangMem (LangChain) | Library — not a service. LangGraph native. Local or PostgreSQL storage. MIT license. | Free open source; zero vendor lock-in; background memory manager; LangGraph `create_react_agent` native | LangChain ecosystem only; no hosted option; Python only; structural limits at scale | LangGraph teams; budget-constrained; full data ownership |
| Letta / MemGPT | Tiered memory. Agents actively manage own memory blocks. Self-hosted free tier. | Unlimited context (agents self-manage); agents decide what to retain; strong for long-horizon tasks | Framework lock-in; file traversal (slow at scale); no LangChain/CrewAI native; niche ecosystem | Research; long-horizon tasks; Letta-committed teams |

> **Recommendation for AWS / EU Banking:** AgentCore Memory + Strands SDK is the correct default. Complement with Zep only if temporal graph reasoning is a hard requirement. Strictly consistent metadata (May 2026) closes the session-scoped retrieval gap that previously required Zep for deterministic filtering.

Part 3 continues with memory and token optimisation strategies, then Strands framework best practices.

## Related

- [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md) — Part 1: release timeline, executive summary, architecture core concepts, memory types taxonomy
- [AgentCore Memory Architecture Guide (Part 3)](15-agentcore-memory-architecture-guide-part3.md) — memory/token optimisation, Strands best practices, EU banking/GDPR compliance, security/threat model, cost optimisation, PoC-to-production journey, evaluation, Terraform IaC
- [AgentCore Memory Architecture Guide (Part 4)](15-agentcore-memory-architecture-guide-part4.md) — complete resume orchestrator, session catalog API, warm pool/session close workflow, test suite
