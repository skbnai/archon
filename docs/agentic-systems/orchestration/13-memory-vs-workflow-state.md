---
title: "Memory vs. Workflow State"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: memory-vs-workflow-state
supersedes: ["../knowledge-docs/docs/workflow-orchestration/13-memory-vs-workflow-state.md"]
doc_type: guide
tags: ["workflow-orchestration", "memory", "state", "agents", "langgraph", "temporal"]
---

# Memory vs. Workflow State

> **As of July 2026.** Temporal 1.x event sourcing; LangGraph 1.2.8 checkpointing; pgvector 0.7 for long-term memory.

This guide clarifies the boundary between workflow state (deterministic, recoverable) and agent memory (contextual, learned). Both are essential in hybrid systems — and the architectures for managing them are fundamentally different.

---

## The Four Layers

Hybrid agentic systems have four distinct state/memory layers. Conflating them causes the most common reliability failures.

```mermaid
graph TD
    A["LAYER 4: External Context<br/>(databases, APIs, real-time data — not owned by either)"]
    B["LAYER 3: Agent Long-Term Memory<br/>(learned patterns, past experiences — survives runs)"]
    C["LAYER 2: Agent Working Memory<br/>(current reasoning context — discarded after run)"]
    D["LAYER 1: Workflow State<br/>(deterministic, recoverable — owned by Temporal)"]
    
    A --> B
    B --> C
    C --> D
```

---

## Layer 1: Workflow State (Temporal)

Workflow state is the **ground truth of process execution**. It lives in Temporal's event log and is fully recoverable from it.

**What belongs here**:

- Current step in the process
- Accumulated data from completed activities (IDs, timestamps, decisions)
- Signals received (approvals, cancellations, external events)
- Timers and deadlines

**What does NOT belong here**:

- Agent reasoning traces (these are memory, not state)
- Large binary blobs (embeddings, documents)
- Ephemeral context that doesn't affect process branching

```python
# Everything that affects workflow routing lives in state
@dataclass
class LoanWorkflowState:
    application_id: str

    # Process state — drives branching
    credit_check_result: Optional[CreditCheckResult] = None
    compliance_cleared: Optional[bool] = None
    underwriting_decision: Optional[str] = None  # "approved" | "rejected" | "pending_docs"

    # Timestamps — for SLA tracking
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    credit_check_completed_at: Optional[datetime] = None

    # Human signals received
    manual_override: Optional[str] = None
    override_by: Optional[str] = None

    # IDs of completed activities — for audit
    charge_id: Optional[str] = None
    notification_sent: bool = False
```

**Key constraint**: Workflow state must be **serializable** (JSON). No lambdas, database connections, or live objects. Temporal serializes state to the event log on every change.

### Recovery Semantics

```
Temporal replay on crash:
  1. Read event log from start
  2. Re-execute workflow code (does NOT re-execute activities)
  3. Activity results come from event log (cached)
  4. Workflow returns to exact state before crash

Result: deterministic, guaranteed recovery
```

---

## Layer 2: Agent Working Memory

Working memory is the **context window of a single agent run**. It includes the conversation history, tool call results, and reasoning trace for the current execution.

**What belongs here**:

- The conversation/message history for this run
- Tool call inputs and outputs from this run
- Intermediate reasoning steps
- Constraints passed in at the start of this run

**Lifetime**: Starts when the agent runs; discarded when it returns a result.

```python
# LangGraph agent state = working memory for one run
from typing import TypedDict, Annotated
import operator

class AgentWorkingMemory(TypedDict):
    # Conversation history — accumulates during the run
    messages: Annotated[list, operator.add]

    # Intermediate findings — ephemeral
    tools_called: Annotated[list, operator.add]
    facts_found: dict

    # Run-level constraints
    max_amount: float
    allowed_tools: list[str]

    # Output to return to Temporal
    decision: Optional[str]
    decision_rationale: Optional[str]
```

**Recovery semantics**: Working memory does NOT survive a crash by default. If the agent activity crashes, Temporal retries the entire activity — the agent starts fresh with an empty working memory.

To enable mid-run recovery, use LangGraph's checkpointer:

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    app = graph.compile(checkpointer=checkpointer)

    # The graph can pause mid-run and resume from last checkpoint
    config = {"configurable": {"thread_id": "run-abc123"}}
    result = await app.ainvoke({"messages": [...]}, config)
```

---

## Layer 3: Agent Long-Term Memory

Long-term memory **persists across agent runs**. It captures patterns, preferences, and knowledge the agent should remember for future interactions with the same entity.

### Use Cases

- "This customer always prefers email over SMS"
- "This account has a history of fraudulent disputes — flag for extra review"
- "This supplier typically requires 3 documents for a compliance check"

### Implementation with pgvector

```python
# pip install pgvector==0.3.0 psycopg2-binary
from pgvector.psycopg2 import register_vector
import psycopg2
import numpy as np
from anthropic import Anthropic

client = Anthropic()

def embed(text: str) -> list[float]:
    """Generate embedding for semantic search."""
    response = client.embeddings.create(
        model="voyage-3",
        input=text,
    )
    return response.data[0].embedding

def store_memory(conn, entity_id: str, content: str, memory_type: str) -> None:
    """Store a memory with embedding for future retrieval."""
    embedding = embed(content)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO agent_memories (entity_id, content, memory_type, embedding, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (entity_id, content_hash) DO UPDATE
            SET last_reinforced = NOW(), frequency = agent_memories.frequency + 1
            """,
            (entity_id, content, memory_type, np.array(embedding))
        )
    conn.commit()

def retrieve_relevant_memories(conn, entity_id: str, query: str, top_k: int = 5) -> list[str]:
    """Retrieve memories most relevant to the current query."""
    query_embedding = embed(query)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT content, 1 - (embedding <=> %s) AS similarity
            FROM agent_memories
            WHERE entity_id = %s
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (np.array(query_embedding), entity_id, np.array(query_embedding), top_k)
        )
        return [row[0] for row in cur.fetchall()]

# Usage: inject relevant memories into agent context
def build_agent_context(customer_id: str, current_query: str) -> str:
    with get_db_connection() as conn:
        memories = retrieve_relevant_memories(conn, customer_id, current_query)

    if not memories:
        return ""

    return "Relevant context from past interactions:\n" + "\n".join(f"- {m}" for m in memories)
```

### Garbage Collection

Long-term memory must be pruned to stay relevant:

```python
async def prune_stale_memories(entity_id: str, max_age_days: int = 365) -> int:
    """Remove memories not accessed in max_age_days."""
    async with db_pool.acquire() as conn:
        result = await conn.execute(
            """
            DELETE FROM agent_memories
            WHERE entity_id = $1
              AND last_accessed < NOW() - INTERVAL '%s days'
              AND frequency < 3  -- keep frequently-accessed even if old
            RETURNING id
            """,
            entity_id, max_age_days
        )
        return len(result)
```

---

## Layer 4: External Context

External context is data that exists in systems **not owned by the workflow or agent** — databases, APIs, third-party services.

**What belongs here**: Customer profiles, product catalogs, regulatory rules, real-time pricing, financial balances.

**Key difference from memory**: External context is not stored by the agent system. It is fetched on demand and may change between fetches.

```python
@activity.defn
async def fetch_customer_context(customer_id: str) -> dict:
    """Fetch current external context — NOT stored in workflow state."""
    # Always fetch fresh — external systems own this data
    profile = await crm_client.get_customer(customer_id)
    risk_score = await risk_service.get_score(customer_id)
    account_balance = await banking_api.get_balance(customer_id)

    return {
        "profile": profile,
        "risk_score": risk_score,
        "account_balance": account_balance,
        "fetched_at": datetime.utcnow().isoformat(),  # timestamp for audit
    }
```

**Important**: If a workflow needs external context for routing decisions, fetch it in an activity and store the result in workflow state. Do not fetch it directly in workflow code (that would break Temporal's determinism guarantees).

---

## Interaction Between Layers

```mermaid
graph TD
    Start["Temporal Workflow starts"]
    A["Activity: fetch_external_context()<br/>stores result in workflow state Layer 1"]
    B["Activity: run_agent()<br/>injects: workflow state + long-term memory Layer 3<br/>agent builds: working memory Layer 2 during execution<br/>agent queries: external context via tools Layer 4<br/>agent returns: decision + rationale"]
    C["Workflow stores decision in state Layer 1"]
    D["Activity: store_agent_learnings()<br/>distills key facts from working memory<br/>persists as long-term memory Layer 3"]
    E["Workflow continues to next step"]
    
    Start --> A
    A --> B
    B --> C
    C --> D
    D --> E
```

---

## Recovery Matrix

| Layer | Survives crash? | Recovery method | Guaranteed? |
| --- | --- | --- | --- |
| Workflow state | Yes | Temporal event log replay | Yes — deterministic |
| Agent working memory | No (by default) | LangGraph checkpointer (opt-in) | Yes if checkpointer configured |
| Long-term memory | Yes | Stored in external DB | Yes (DB durability) |
| External context | N/A — not stored | Refetch on next activity call | No — may change |

---

## Common Mistakes

**Mistake 1: Storing agent reasoning in workflow state**  
The reasoning trace is working memory, not workflow state. Don't serialize entire message histories into Temporal's event log — they can be megabytes per run.

**Mistake 2: Using workflow state for caching**  
Workflow state is for process control data. Don't store frequently-changing external data (prices, inventory) in it — it won't be fresh when replayed.

**Mistake 3: No long-term memory cleanup**  
Agent long-term memory grows forever if not pruned. Stale memories degrade agent quality and inflate storage costs.

**Mistake 4: Fetching external context in workflow code (not in activities)**  
External API calls in workflow code break Temporal's determinism. All side effects must live in activities.

---

## Versioning Memory After Model Upgrades

When you upgrade an LLM model version (e.g., Claude 3.5 → claude-sonnet-4-6), long-term memories created under the old model may be interpreted differently by the new model. This is a subtle but important migration risk.

```python
@dataclass
class MemoryEntry:
    content: str
    created_at: datetime
    model_version: str         # which model was active when memory was created
    last_accessed_model: str   # which model last used this memory
    confidence: float

async def migrate_memories_for_model_upgrade(
    entity_id: str,
    old_model: str,
    new_model: str,
) -> dict:
    """
    After a model upgrade, re-validate and optionally re-embed memories.
    High-confidence memories created under the old model should be reviewed
    if they contain model-specific interpretations.
    """
    memories = await memory_store.get_all(entity_id)
    old_model_memories = [m for m in memories if m.model_version == old_model]

    results = {"reviewed": 0, "flagged": 0, "archived": 0}

    for memory in old_model_memories:
        # Re-validate: ask new model if memory still makes sense
        validation = await new_model_client.messages.create(
            model=new_model,
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": f"Is this statement still accurate and well-formed? Answer YES or NO only: '{memory.content}'"
            }],
        )

        if "NO" in validation.content[0].text.upper():
            await memory_store.archive(memory)
            results["archived"] += 1
        else:
            await memory_store.update_model_tag(memory, new_model)
            results["reviewed"] += 1

    return results
```

**Practice**: Run memory migration as part of model upgrade testing — before the new model goes to production — so you know how many memories need review.

---

## Related

[Durable Execution vs Cognitive Execution](./durable-vs-cognitive-execution) · [Reliability Playbook](./reliability-playbook) · [Agent Frameworks Comparison](./agent-frameworks-comparison) · [Temporal Deep Dive](./temporal-deep-dive)
