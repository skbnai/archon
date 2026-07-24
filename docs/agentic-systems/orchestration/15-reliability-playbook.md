---
title: "Reliability Playbook for Agentic Systems"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: reliability-playbook
supersedes: ["../knowledge-docs/docs/workflow-orchestration/15-reliability-playbook.md"]
doc_type: guide
tags: ["workflow-orchestration", "reliability", "sre", "failure-modes", "agents"]
---

# Reliability Playbook for Agentic Systems

> **As of July 2026.** LangGraph 1.2.8; Temporal 1.x; Claude claude-sonnet-4-6 API.

This playbook documents how agentic systems fail, how to detect failures, how to recover, and how to prevent them. It is written for SREs and platform engineers who own production agentic systems.

---

## Why Agentic Reliability is Different

Traditional services fail in predictable ways: timeout, crash, bad data. Agentic systems fail in new ways that most monitoring does not catch:

| Traditional Failure | Agentic Failure |
| --- | --- |
| Service returns 500 | Agent returns confident wrong answer |
| Timeout | Agent loops for 20 minutes then times out |
| Crash | Agent completes but with hallucinated tool name |
| Bad data | Agent ignores good data, makes up its own |
| Cascade failure | Agent A asks Agent B, B asks Agent C, C asks A → deadlock |

The hardest failures are **silent correctness failures** — the system completes successfully but the answer is wrong, and nothing in your monitoring catches it.

---

## Failure Mode Catalog

### FM-01: Tool Hallucination

**What**: Agent invokes a tool that does not exist or with arguments outside the defined schema.

```
Agent: "I'll call the get_credit_history tool to check the applicant's history."
System: Tool "get_credit_history" not found.
Agent: "I'll try get_credit_report instead."  (exists — but wrong data)
```

**Detection**:

```python
class ToolCallValidator:
    def validate(self, tool_name: str, args: dict, registered_tools: dict) -> None:
        if tool_name not in registered_tools:
            raise ToolHallucinationError(
                f"Agent called non-existent tool: {tool_name}. "
                f"Available: {list(registered_tools.keys())}"
            )
        schema = registered_tools[tool_name]["input_schema"]
        jsonschema.validate(args, schema)  # raises if args don't match schema
```

**Prevention**: Use strict tool schemas with JSON Schema validation. Never give agents tool names that sound similar to each other — similarity causes hallucination.

---

### FM-02: Infinite Reasoning Loop

**What**: Agent gets stuck in a loop — calls a tool, gets unsatisfying result, calls the same tool again with slightly different args, infinitely.

```
[loop starts]
  Action: search_policy(query="refund eligibility")
  Result: "Refunds allowed within 30 days"
  Thought: "I need more specific guidance"
  Action: search_policy(query="refund eligibility specific cases")
  Result: "Refunds allowed within 30 days"
  Thought: "Still not specific enough"
  [→ continues until token limit or timeout]
```

**Detection and Prevention**:

```python
from collections import Counter

class LoopDetector:
    def __init__(self, window: int = 5, threshold: int = 3):
        self.window = window
        self.threshold = threshold
        self.call_history: list[str] = []

    def record_call(self, tool_name: str, args_hash: str) -> None:
        call_key = f"{tool_name}:{args_hash}"
        self.call_history.append(call_key)

        if len(self.call_history) > self.window:
            self.call_history.pop(0)

        counts = Counter(self.call_history)
        if counts[call_key] >= self.threshold:
            raise AgentLoopError(
                f"Agent called {tool_name} with similar args {self.threshold}+ times in {self.window} steps. "
                "Breaking loop — escalating to human."
            )
```

---

### FM-03: Context Window Exhaustion

**What**: Conversation history grows too long, causing the LLM to either refuse (context limit) or lose coherence (attention degradation near the limit).

```python
import tiktoken

def count_tokens(messages: list[dict], model: str = "claude-sonnet-4-6") -> int:
    """Estimate token count for a conversation."""
    # Claude uses ~4 chars per token as rough estimate
    total_chars = sum(len(str(m)) for m in messages)
    return total_chars // 4

def trim_context(messages: list[dict], max_tokens: int = 180_000) -> list[dict]:
    """Trim middle messages to stay within limit, keeping system + recent messages."""
    if count_tokens(messages) <= max_tokens:
        return messages

    system_messages = [m for m in messages if m["role"] == "system"]
    recent_messages = messages[-10:]  # Always keep last 10 turns

    # Summarize the middle
    middle = messages[len(system_messages):-10]
    if middle:
        summary = summarize_messages(middle)
        summary_message = {"role": "user", "content": f"[Earlier context summary: {summary}]"}
        return system_messages + [summary_message] + recent_messages

    return system_messages + recent_messages
```

---

### FM-04: Stale Memory

**What**: Agent makes decisions based on long-term memory that is no longer true.

```
Memory: "Customer prefers email communication"
Reality: Customer opted out of email 6 months ago
Agent: Sends email → customer complaints
```

**Prevention**:

```python
@dataclass
class MemoryEntry:
    content: str
    confidence: float         # degrades over time
    created_at: datetime
    last_validated_at: Optional[datetime]
    valid_until: Optional[datetime]  # hard expiry for time-sensitive facts

    def is_stale(self, max_age_days: int = 90) -> bool:
        age = (datetime.utcnow() - self.created_at).days
        if self.valid_until and datetime.utcnow() > self.valid_until:
            return True
        return age > max_age_days

def retrieve_memories_with_freshness(entity_id: str, query: str) -> list[str]:
    memories = memory_store.retrieve(entity_id, query)

    fresh = [m for m in memories if not m.is_stale()]
    stale = [m for m in memories if m.is_stale()]

    if stale:
        logger.warning(f"Skipping {len(stale)} stale memories for entity {entity_id}")

    return [m.content for m in fresh]
```

---

### FM-05: Multi-Agent Deadlock

**What**: Agent A waits for Agent B; Agent B waits for Agent A. Neither proceeds.

**Detection**:

```python
class DependencyTracker:
    def __init__(self):
        self.waiting_for: dict[str, str] = {}  # agent_id → blocking_agent_id

    def agent_waiting_for(self, agent_id: str, blocking_agent: str) -> None:
        self.waiting_for[agent_id] = blocking_agent

        if self._has_cycle():
            cycle = self._find_cycle()
            raise DeadlockError(f"Deadlock detected: {' → '.join(cycle)}")

    def _has_cycle(self) -> bool:
        visited = set()
        for start in self.waiting_for:
            path = set()
            node = start
            while node in self.waiting_for:
                if node in path:
                    return True
                if node in visited:
                    break
                path.add(node)
                node = self.waiting_for[node]
            visited |= path
        return False
```

---

### FM-06: Partial Execution (Some Steps Done, Some Not)

**What**: Agent completes steps 1-3, crashes at step 4, and on retry re-executes steps 1-3 with side effects.

**Prevention**: Use Temporal for any multi-step execution with side effects. Temporal's activity result caching prevents re-execution of completed steps.

```python
# Inside Temporal workflow — completed activities are NEVER re-executed on replay
@workflow.run
async def run(self, data: dict) -> dict:
    # If step_1 completed before crash, Temporal uses cached result
    result_1 = await workflow.execute_activity(step_1, data)
    # step_2 runs only if step_1 truly hasn't run yet (replay uses cache)
    result_2 = await workflow.execute_activity(step_2, result_1)
    return result_2
```

For agents outside Temporal, use idempotency keys:

```python
import hashlib

def idempotency_key(operation: str, **params) -> str:
    content = f"{operation}:{sorted(params.items())}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]

async def issue_refund_idempotent(account_id: str, amount: float, reason: str) -> dict:
    key = idempotency_key("refund", account_id=account_id, amount=amount)

    # Check if already processed
    existing = await refund_store.get(key)
    if existing:
        return existing  # Return cached result, don't double-refund

    result = await payment_gateway.refund(account_id, amount, reason)
    await refund_store.set(key, result, ttl_hours=24)
    return result
```

---

## Detection Strategies

### Metric Baseline for Agentic Systems

```python
# Metrics to track (expose via OpenTelemetry)
from opentelemetry import metrics

meter = metrics.get_meter("agent_reliability")

# Core agent health
agent_iterations = meter.create_histogram("agent.iterations", description="Iterations per agent run")
agent_duration = meter.create_histogram("agent.duration_ms", description="Agent run duration")
agent_token_usage = meter.create_histogram("agent.tokens_used", description="Tokens per run")
agent_tool_calls = meter.create_histogram("agent.tool_calls", description="Tool calls per run")

# Failure counters
agent_loops_detected = meter.create_counter("agent.loop_detected", description="Reasoning loops caught")
agent_hallucinations = meter.create_counter("agent.tool_hallucination", description="Hallucinated tool calls")
agent_context_trims = meter.create_counter("agent.context_trimmed", description="Context window trims")
agent_escalations = meter.create_counter("agent.escalated_to_human", description="Escalations to human")

# Business outcome metrics (most important)
agent_decision_distribution = meter.create_histogram("agent.decision_type", description="Distribution of decisions")
agent_override_rate = meter.create_gauge("agent.human_override_rate", description="% of agent decisions overridden by humans")
```

### Alerting Thresholds

```yaml
# alert_rules.yaml
alerts:
  - name: AgentHighIterations
    condition: agent.iterations > 12  # near max_iterations limit
    severity: warning
    action: "Check for reasoning loop — review trace"

  - name: AgentHighOverrideRate
    condition: agent.human_override_rate > 0.15  # 15%
    severity: critical
    action: "Agent decision quality degraded — review prompt version and model"

  - name: AgentTokenSurge
    condition: agent.tokens_used > 150000  # near 200k context limit
    severity: warning
    action: "Context growing — review context trimming strategy"

  - name: AgentHallucinationSpike
    condition: agent.tool_hallucination increase > 5 in 10m
    severity: critical
    action: "Prompt may have drifted — rollback to previous version"
```

---

## Recovery Playbooks

### Playbook: Agent Loop Detected

1. **Immediate**: The loop detector raises `AgentLoopError` — catch it, log the full message history
2. **Escalate**: Route to human with the conversation context and the point where it looped
3. **Diagnose**: Which tool was being called? Was the tool returning useful data? Was the prompt under-specified?
4. **Fix**: Usually either (a) add a loop detection prompt instruction, (b) improve the tool's output format, or (c) add a more specific tool

### Playbook: Hallucinated Tool Name

1. **Immediate**: Catch `ToolHallucinationError`, log the hallucinated name
2. **Abort the run**: Do not let the agent continue with a broken tool call
3. **Diagnose**: Was the tool name close to a real tool? Do you have two tools with similar names?
4. **Fix**: Rename tools to be maximally distinct. Improve tool descriptions to disambiguate.

### Playbook: High Human Override Rate

1. **Flag**: Alert fires when override rate exceeds 15%
2. **Identify**: Which workflow type / which decision type is being overridden?
3. **Sample**: Review 10 recent agent decisions + human overrides — what did the agent miss?
4. **Root cause**: Stale prompt? Model regression? New edge cases not in training data?
5. **Fix**: Update prompt, add examples, or add a new tool if agent lacks data to decide correctly

---

## SLA Design for Agent Workflows

Recommended SLAs (starting points — calibrate to your context):

| Workflow Type | p50 | p95 | p99 | Timeout |
|---|---|---|---|---|
| Simple agent run | 3s | 8s | 15s | 30s |
| Complex agent run | 15s | 45s | 90s | 3m |
| Multi-agent fan-out | 20s | 60s | 120s | 5m |
| HITL approval gate | — | — | — | 24h (business) |
| Human reasoning review | — | — | — | 4h (business) |

Set Temporal `start_to_close_timeout` to your p99 + 20% margin. Build alerting on p95. Design graceful degradation for p99 breaches.

---

## Related

[Observability Framework](./observability-framework) · [Human-in-the-Loop Architectures](./human-in-the-loop-architectures) · [Anti-Patterns Catalog](./anti-patterns-catalog) · [Enterprise Governance Model](./enterprise-governance-model)
