---
title: "Claude Agent SDK — Production Reference (Part 2)"
domain: agentic-systems
doc_type: guide
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
topic_id: claude-agent-sdk-production-part2
supersedes: []
---

# Claude Agent SDK — Production Reference (Part 2)

Production Patterns, Cost Controls, Guardrails, and Observability for multi-agent systems.

**Part 2 of 3:** [← Back to Part 1](pathname:///archon/agentic-systems/coding-tools/30-claude-agent-sdk-production) | [Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/30-claude-agent-sdk-production-part3)

---

## 10. Production Patterns

### Circuit Breaker

Prevent cascade failures when a downstream service is degraded. The circuit breaker opens after N consecutive failures and allows limited recovery probes.

```python
from claude_agent_sdk import CircuitBreaker, CircuitOpenError
import structlog

log = structlog.get_logger()

breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 consecutive failures
    recovery_timeout=60,      # Probe again after 60 seconds
    half_open_max_calls=2,    # Allow 2 test calls in half-open state
    on_state_change=lambda prev, curr: log.warning(
        "circuit_breaker_state_change",
        previous=prev,
        current=curr,
    ),
)

async def safe_agent_run(prompt: str) -> str:
    try:
        async with breaker:
            result = await agent.run(prompt)
            return result.text
    except CircuitOpenError:
        log.error("circuit_open_fallback_triggered")
        return "Service temporarily unavailable. Please try again in a few minutes."
```

### Retry with Exponential Backoff

```python
from claude_agent_sdk import Agent, RetryConfig, RateLimitError, ServiceUnavailableError

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[query_analytics],
    retry_config=RetryConfig(
        max_attempts=4,
        backoff_base=2.0,          # 2s, 4s, 8s delays
        backoff_jitter=0.5,         # ±50% jitter prevents thundering herd
        retryable_errors=[RateLimitError, ServiceUnavailableError],
        on_retry=lambda attempt, error: log.warning(
            "agent_retry",
            attempt=attempt,
            error=type(error).__name__,
        ),
    ),
)
```

### Partial Result Recovery

For long-running batch jobs, checkpoint progress so the job can be resumed after a failure without reprocessing completed items.

```python
async def chunked_analysis(documents: list[dict], checkpoint_key: str) -> list[dict]:
    results = []

    # Resume from last saved checkpoint
    start_idx = await state_store.get(checkpoint_key, default=0)
    if start_idx > 0:
        log.info("resuming_from_checkpoint", index=start_idx)
        results = await state_store.get(f"{checkpoint_key}_results", default=[])

    for i, doc in enumerate(documents[start_idx:], start=start_idx):
        try:
            result = await analyst_agent.run(f"Analyse document: {doc['content']}")
            results.append({"doc_id": doc["id"], "analysis": result.text})

            # Checkpoint after every successful item
            await state_store.set(checkpoint_key, i + 1)
            await state_store.set(f"{checkpoint_key}_results", results)

        except Exception as e:
            log.error("analysis_failed", doc_id=doc["id"], index=i, error=str(e))
            results.append({"doc_id": doc["id"], "error": str(e), "analysis": None})

    # Clean up checkpoint on successful completion
    await state_store.delete(checkpoint_key)
    await state_store.delete(f"{checkpoint_key}_results")
    return results
```

### Rate Limit Handling

Anthropic enforces per-minute and per-day rate limits at the API level. Handle them gracefully.

```python
from claude_agent_sdk import RateLimiter

# Per-user limits enforced in your application layer
limiter = RateLimiter(
    backend="redis://localhost:6379",
    limits={
        "per_user_per_minute_requests": 10,
        "per_user_per_day_tokens": 500_000,
        "per_user_per_day_usd": 5.00,
    },
)

@app.post("/analyze")
async def analyze_endpoint(req: AnalyzeRequest, user: User = Depends(get_user)):
    try:
        async with limiter.check(user.id):
            result = await agent.run(req.prompt)
    except limiter.LimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": str(e),
                "retry_after_seconds": e.retry_after,
            },
        )
    return {"response": result.text, "tokens_used": result.usage.total_tokens}
```

---

## 11. Token Optimization

### Prompt Compression

Reduce system prompt size without losing fidelity. Large prompts waste tokens on every turn.

```python
# Bad — verbose, repetitive, padded with filler text
system_prompt_bad = """
You are an extremely helpful AI assistant named Claude who works for our company.
You should always be polite, respectful, and professional in all your interactions.
Your job is to help users with their questions about our products and services.
You should never say anything inappropriate or offensive...
(300 more words of filler)
"""

# Good — dense, precise, role-aware
system_prompt_good = """
Role: Senior product analyst for Acme Corp.
Capabilities: Revenue analysis, churn prediction, cohort analysis.
Constraints: Read-only database access. Do not speculate without data.
Output: Structured JSON + narrative summary. Cite specific metrics.
Tone: Direct, technical, concise.
"""
```

### Caching with `cache_control`

Use prompt caching to avoid reprocessing identical large context blocks on every API call. Cache read cost is 10% of base input cost; cache write is 25%.

```python
import anthropic

client = anthropic.Anthropic()

# Large, stable context (e.g., a policy document, schema, or codebase)
STABLE_CONTEXT = Path("company-policy.txt").read_text()

def run_with_cache(user_question: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": STABLE_CONTEXT,
                "cache_control": {"type": "ephemeral"},  # Cache this block
            },
            {
                "type": "text",
                "text": "You are a policy analyst. Answer questions based on the policy document above.",
            },
        ],
        messages=[{"role": "user", "content": user_question}],
    )
    return response.content[0].text
```

:::tip Cache savings in practice
    A 100K-token policy document costs approximately $0.30 to process per call at Sonnet pricing. With caching, the first call costs approximately $0.25 (cache write) and all subsequent calls cost approximately $0.03 (cache read). Break-even is 2 calls; after that you save approximately 90% on input tokens.

### Output Token Limits

Set `max_tokens` to the minimum needed for the task. Agents often generate verbose output by default.

```python
# Match max_tokens to the task
agents = {
    "classifier": Agent(model="claude-haiku-4-5", max_tokens=64),    # Label only
    "summariser": Agent(model="claude-haiku-4-5", max_tokens=512),   # Short summary
    "analyst":    Agent(model="claude-sonnet-4-6", max_tokens=2048), # Full analysis
    "writer":     Agent(model="claude-fable", max_tokens=8192),       # Long-form content
}
```

### Batch Processing

For non-latency-sensitive workloads, use the Messages Batch API to process many items at up to 50% lower cost.

```python
import anthropic

client = anthropic.Anthropic()

def batch_classify(texts: list[str]) -> list[str]:
    requests = [
        anthropic.types.message_create_params.MessageCreateParamsNonStreaming(
            custom_id=f"item-{i}",
            params={
                "model": "claude-haiku-4-5",
                "max_tokens": 16,
                "messages": [
                    {"role": "user", "content": f"Classify sentiment (positive/negative/neutral): {text}"}
                ],
            },
        )
        for i, text in enumerate(texts)
    ]

    batch = client.messages.batches.create(requests=requests)

    # Poll for completion (or use webhook)
    while batch.processing_status != "ended":
        import time; time.sleep(10)
        batch = client.messages.batches.retrieve(batch.id)

    results = []
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            results.append(result.result.message.content[0].text.strip())
        else:
            results.append("error")
    return results
```

---

## 12. Cost Optimization

### Model Selection Matrix

Match model to task complexity. Over-specifying the model is the single largest source of unnecessary cost in production agentic systems.

| Task Type | Recommended Model | Rationale |
| ----------- | ------------------- | ----------- |
| Classification, routing, short extraction | `claude-haiku-4-5` | Sub-100ms, minimal reasoning required |
| Summarisation (< 10K tokens) | `claude-haiku-4-5` | Fast, accurate, cost-efficient |
| Code generation (< 500 lines) | `claude-sonnet-4-6` | Strong coding, good speed |
| Multi-step reasoning, analysis | `claude-sonnet-4-6` | Best value for complex tasks |
| Creative writing, narrative | `claude-fable` | Optimised for fluency and style |
| Long-horizon coding, complex research | `claude-opus-4-6` | Maximum capability, use sparingly |

See [Claude Models 2026](../35-claude-models-2026.md) for pricing details.

### Token Counting Before Dispatch

Count tokens before sending to catch budget overruns before they incur cost.

```python
import anthropic

client = anthropic.Anthropic()

def count_tokens(model: str, messages: list[dict], system: str = "") -> int:
    response = client.messages.count_tokens(
        model=model,
        system=system,
        messages=messages,
    )
    return response.input_tokens

async def budget_guarded_run(prompt: str, max_input_tokens: int = 10_000):
    messages = [{"role": "user", "content": prompt}]
    token_count = count_tokens("claude-sonnet-4-6", messages)

    if token_count > max_input_tokens:
        raise ValueError(
            f"Input too large: {token_count} tokens exceeds budget of {max_input_tokens}. "
            f"Compress the prompt or split into smaller tasks."
        )

    return await agent.run(prompt)
```

### Budget Guards

```python
from claude_agent_sdk import Agent, CostLimit

# Hard budget per task
agent = Agent(
    model="claude-sonnet-4-6",
    cost_limit=CostLimit(
        max_tokens_per_task=50_000,
        max_cost_usd=0.75,        # Hard stop at $0.75 per task
        on_limit="raise",          # Options: "raise", "truncate", "warn"
    ),
)

# Per-tenant monthly budget (SaaS pattern)
from claude_agent_sdk.billing import TenantBudget

tenant_budgets = TenantBudget(store=postgres_store)

async def run_for_tenant(tenant_id: str, prompt: str):
    remaining = await tenant_budgets.get_remaining(tenant_id)
    if remaining.usd < 0.01:
        raise QuotaExceededError(f"Tenant {tenant_id} budget exhausted for this period")

    result = await agent.run(prompt)
    await tenant_budgets.deduct(tenant_id, result.usage.cost_usd)
    return result
```

### Dynamic Model Routing

Route simple tasks to cheaper models automatically.

```python
from claude_agent_sdk import Agent

haiku_agent  = Agent(model="claude-haiku-4-5",  max_tokens=512)
sonnet_agent = Agent(model="claude-sonnet-4-6", max_tokens=4096)
opus_agent   = Agent(model="claude-opus-4-6",   max_tokens=8192)

async def route_and_run(prompt: str, task_complexity: str = "auto") -> str:
    if task_complexity == "auto":
        # Quick complexity estimate via token count and keyword heuristics
        token_count = count_tokens("claude-haiku-4-5", [{"role": "user", "content": prompt}])
        keywords = {"analyse", "compare", "synthesise", "strategy", "architecture"}
        has_complex_keywords = any(kw in prompt.lower() for kw in keywords)

        if token_count < 500 and not has_complex_keywords:
            task_complexity = "simple"
        elif token_count < 5000:
            task_complexity = "medium"
        else:
            task_complexity = "complex"

    agent_map = {"simple": haiku_agent, "medium": sonnet_agent, "complex": opus_agent}
    selected_agent = agent_map[task_complexity]
    result = await selected_agent.run(prompt)

    log.info("model_routing", complexity=task_complexity, model=selected_agent.model,
             tokens=result.usage.total_tokens, cost_usd=result.usage.cost_usd)
    return result.text
```

---

## 13. Guardrails & Safety

### Input Validation Before Dispatch

Never pass raw user input directly to an agent. Validate length, content, and intent first.

```python
import re
from claude_agent_sdk.exceptions import InvalidInputError

MAX_PROMPT_CHARS = 20_000
BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"disregard your system prompt",
    r"you are now (?:in |)developer mode",
    r"jailbreak",
    r"DAN mode",
]

def validate_input(user_input: str) -> str:
    if not user_input or not user_input.strip():
        raise InvalidInputError("Input cannot be empty")

    if len(user_input) > MAX_PROMPT_CHARS:
        raise InvalidInputError(f"Input exceeds {MAX_PROMPT_CHARS} character limit")

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            raise InvalidInputError("Input contains a disallowed pattern")

    return user_input.strip()

@app.post("/run")
async def run_endpoint(req: RunRequest, user: User = Depends(get_user)):
    try:
        clean_input = validate_input(req.prompt)
    except InvalidInputError as e:
        log.warning("input_validation_failed", user_id=user.id, reason=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    result = await agent.run(clean_input)
    return {"response": result.text}
```

### Output Validation and Sanitisation

Validate agent output before exposing it to downstream systems or users.

```python
import json
from pydantic import BaseModel, ValidationError

class AnalysisOutput(BaseModel):
    summary: str
    key_findings: list[str]
    confidence: float  # 0.0 to 1.0
    data_sources: list[str]

async def validated_analysis(prompt: str) -> AnalysisOutput:
    result = await agent.run(
        f"{prompt}\n\nReturn your response as valid JSON matching this schema: "
        f"{AnalysisOutput.schema_json()}"
    )

    # Strip markdown code fences if present
    text = result.text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text).rstrip("` ")

    try:
        data = json.loads(text)
        return AnalysisOutput(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        log.error("output_validation_failed", error=str(e), raw=result.text[:500])
        raise ValueError(f"Agent produced invalid output: {e}")
```

### Refusal Detection and Graceful Degradation

```python
REFUSAL_INDICATORS = [
    "i'm not able to",
    "i cannot",
    "i don't have access",
    "as an ai, i",
    "i'm unable to provide",
    "i can't assist with",
]

def is_refusal(response_text: str) -> bool:
    lower = response_text.lower()
    return any(indicator in lower for indicator in REFUSAL_INDICATORS)

async def run_with_fallback(prompt: str) -> str:
    result = await primary_agent.run(prompt)

    if is_refusal(result.text):
        log.warning("agent_refusal_detected", prompt_preview=prompt[:200])
        # Try with a reframed prompt
        reframed = await reframing_agent.run(
            f"The following request was declined. Reframe it to be more acceptable "
            f"while preserving the core intent:\n\n{prompt}"
        )
        result = await primary_agent.run(reframed.text)

        if is_refusal(result.text):
            # Graceful degradation — surface to human
            return (
                "This request requires human review. "
                "A team member will follow up within 1 business day."
            )

    return result.text
```

---

## 14. Observability

### Structured Logging

```python
import structlog
from claude_agent_sdk import Agent

log = structlog.get_logger()

def make_event_handler(session_id: str, user_id: str):
    def handler(event):
        log.info(
            "agent_event",
            event_type=event.type,
            session_id=session_id,
            user_id=user_id,
            model=event.model if hasattr(event, "model") else None,
            tool_name=event.tool_name if hasattr(event, "tool_name") else None,
            input_tokens=event.usage.input_tokens if event.usage else None,
            output_tokens=event.usage.output_tokens if event.usage else None,
            cost_usd=event.usage.cost_usd if event.usage else None,
        )
    return handler

agent = Agent(
    model="claude-sonnet-4-6",
    on_event=make_event_handler(session_id="sess-001", user_id="user-42"),
)
```

### Token Usage Tracking

```python
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class UsageAccumulator:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    cost_usd: float = 0.0
    call_count: int = 0

usage_by_tenant: dict[str, UsageAccumulator] = defaultdict(UsageAccumulator)

def track_usage(tenant_id: str, usage):
    acc = usage_by_tenant[tenant_id]
    acc.input_tokens    += usage.input_tokens
    acc.output_tokens   += usage.output_tokens
    acc.cache_read_tokens  += getattr(usage, "cache_read_tokens", 0)
    acc.cache_write_tokens += getattr(usage, "cache_write_tokens", 0)
    acc.cost_usd        += usage.cost_usd
    acc.call_count      += 1

# Daily billing reconciliation
async def export_daily_usage():
    for tenant_id, acc in usage_by_tenant.items():
        await billing_db.upsert({
            "date": date.today().isoformat(),
            "tenant_id": tenant_id,
            "input_tokens": acc.input_tokens,
            "output_tokens": acc.output_tokens,
            "cost_usd": round(acc.cost_usd, 6),
            "call_count": acc.call_count,
        })
```

### Distributed Tracing (W3C Trace Context)

Propagate W3C Trace Context (`traceparent`, `tracestate`) through agent chains so spans appear correctly in your APM tool (Datadog, Jaeger, Honeycomb).

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract
from claude_agent_sdk.telemetry import OtelInstrumentation

tracer = trace.get_tracer("agent-sdk")

OtelInstrumentation.configure(
    tracer_provider=trace.get_tracer_provider(),
    capture_prompts=False,    # Avoid PII in traces
    capture_responses=False,  # Avoid sensitive output in traces
)

async def traced_agent_run(prompt: str, carrier: dict | None = None) -> str:
    """
    carrier: dict containing 'traceparent' and 'tracestate' headers
             from the upstream request (HTTP or event message).
    """
    ctx = extract(carrier or {})

    with tracer.start_as_current_span("agent.run", context=ctx) as span:
        span.set_attribute("agent.model", agent.model)
        span.set_attribute("agent.prompt_length", len(prompt))

        result = await agent.run(prompt)

        span.set_attribute("agent.input_tokens", result.usage.input_tokens)
        span.set_attribute("agent.output_tokens", result.usage.output_tokens)
        span.set_attribute("agent.cost_usd", result.usage.cost_usd)

        return result.text
```

### Key Metrics to Track

| Metric | Description | Alert Threshold |
| -------- | ------------- | ----------------- |
| `task_completion_rate` | Percentage of tasks finishing without error | < 95% |
| `avg_tokens_per_task` | Token efficiency over time | > 3× baseline |
| `tool_error_rate` | Percentage of tool calls returning errors | > 5% |
| `p95_latency_ms` | 95th percentile end-to-end latency | > 30,000 ms |
| `cost_per_task_usd` | Mean agent task cost | > budget target |
| `circuit_breaker_trips` | Circuit breaker state changes | Any in 1 hour |
| `refusal_rate` | Percentage of responses that are refusals | > 2% |
| `checkpoint_rejection_rate` | Percentage of HITL checkpoints rejected | > 10% |

---

**This is Part 2 of 3. [← Back to Part 1](pathname:///archon/agentic-systems/coding-tools/30-claude-agent-sdk-production) | [Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/30-claude-agent-sdk-production-part3) for Best Practices, Testing, Managed Agents, and Deployment Checklist.**
