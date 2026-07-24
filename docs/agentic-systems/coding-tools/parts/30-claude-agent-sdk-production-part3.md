---
title: "Claude Agent SDK — Production Reference (Part 3)"
domain: agentic-systems
doc_type: guide
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
topic_id: claude-agent-sdk-production-part3
supersedes: []
---

# Claude Agent SDK — Production Reference (Part 3)

Best Practices, Testing Strategies, Managed Agents, Billing, and Deployment Checklist.

**Part 3 of 3:** [← Back to Part 1](pathname:///archon/agentic-systems/coding-tools/30-claude-agent-sdk-production) | [Part 2](pathname:///archon/agentic-systems/coding-tools/parts/30-claude-agent-sdk-production-part2)

---

## 15. Best Practices

1. **Pin model versions** — use `claude-sonnet-4-6` not `claude-sonnet-latest`. Model updates can change behaviour and break evals. Update intentionally after testing.

2. **Set `max_tokens` tightly** — agents default to verbose output. Set `max_tokens` to the minimum the task requires. This both controls cost and forces conciseness.

3. **Use Haiku for sub-tasks** — the majority of subagent work (classification, extraction, short summarisation) does not require Sonnet or Opus. Default subagents to Haiku unless the task demands it.

4. **Always validate tool inputs** — the model is a probabilistic system. Tool arguments must be validated (type, range, allowlist) before execution, especially for database writes and file operations.

5. **Implement HITL for irreversible actions** — any action that cannot be undone (sending emails, charging payments, deleting records, deploying code) must have a human checkpoint or be designed to be reversible with a compensating transaction.

6. **Use durable state stores in production** — in-memory sessions die with the process. Use Postgres or Redis for all sessions that span more than one request.

7. **Separate agent roles** — a single agent with 20 tools and a 2,000-token system prompt performs worse than three specialised agents with 5 tools each. Scope each agent to one responsibility.

8. **Cap parallel subagent concurrency** — spawning 50 subagents simultaneously will hit rate limits and cause cascading failures. Use `asyncio.Semaphore` to bound concurrency to 5–10 concurrent API calls.

9. **Log tool invocations with user attribution** — every tool call must be logged with: user ID, session ID, tool name, input arguments (redact PII), timestamp, and success/failure. This is your audit trail.

10. **Test with adversarial inputs** — inject prompt injection attempts, malformed tool arguments, and extremely long inputs into your test suite. The agent should handle all of them gracefully without crashing or leaking data.

11. **Implement budget guards before dispatch** — count tokens before sending and reject or split prompts that exceed your input token budget. This prevents surprise API costs from oversized inputs.

12. **Use structured outputs for downstream processing** — when another system consumes agent output, require JSON with a validated schema rather than free text. This prevents brittle string parsing and makes failures explicit.

---

## 16. Antipatterns

1. **Running everything through Opus** — the most common cost mistake. Opus costs 5× Sonnet and should only be used for tasks that genuinely require its capabilities. Use the model selection matrix in §12.

2. **Omitting token/cost budgets** — an agent with no budget guard can run 1M tokens on a single malformed request. Always set `CostLimit` with a `max_cost_usd` hard cap.

3. **Using in-memory sessions for multi-turn interactions** — any session that spans an HTTP request or a process restart will lose context. This causes confusing user experiences and inconsistent agent behaviour.

4. **Giving agents unrestricted bash/file access** — an agent with full shell access will eventually delete something important, exfiltrate data, or be exploited via prompt injection. Always sandbox tool access.

5. **Not implementing circuit breakers** — without a circuit breaker, a degraded downstream service causes every agent request to time out for minutes, consuming thread pool capacity and accumulating cost on retries.

6. **Spawning unlimited concurrent subagents** — parallel fan-out without a concurrency limit will exhaust your API rate limit quota, triggering 429 errors that retry endlessly and amplify the problem.

7. **Not logging tool invocations** — without tool-level audit logs you cannot diagnose production incidents, demonstrate compliance, or answer "what did the agent do with user X's data?"

8. **Not validating agent output before acting on it** — agents occasionally hallucinate JSON keys, omit required fields, or produce malformed output. Validate with Pydantic before passing output to databases or APIs.

9. **Agents with no max_iterations limit** — a tool that always returns an error will cause the agent to loop indefinitely. Always set a maximum iteration count (e.g., `max_tool_calls=20`).

10. **Passing raw user input directly to the agent** — prompt injection is real. User input must be validated for length, content policy violations, and injection patterns before reaching the agent.

11. **Hardcoding API keys in source code** — even in "internal" repositories. Use environment variables, secrets managers, or CI secret injection. Rotate on a 90-day schedule.

12. **Blending multiple unrelated responsibilities in one agent** — an agent responsible for research, writing, database operations, and email sending has no meaningful tool boundaries. When something goes wrong, it is impossible to attribute or isolate the failure.

---

## 17. Testing

### Unit Testing Agents

```python
import pytest
from claude_agent_sdk.testing import MockAgent, MockToolCall

@pytest.fixture
def mock_agent():
    return MockAgent(
        model="claude-sonnet-4-6",
        responses=[
            MockToolCall(tool="query_analytics", arguments={"sql": "SELECT count(*) FROM users"}),
            "Based on the data, there are 42,317 active users.",
        ],
    )

async def test_user_count_query(mock_agent):
    result = await mock_agent.run("How many active users do we have?")

    assert "42,317" in result.text
    assert mock_agent.tool_calls[0].tool == "query_analytics"
    assert "SELECT" in mock_agent.tool_calls[0].arguments["sql"].upper()

async def test_input_too_long_raises(mock_agent):
    with pytest.raises(ValueError, match="character limit"):
        await run_with_validation("x" * 25_000)
```

### Evaluation Harness

Run a fixed set of test cases and measure pass rate, token cost, and latency. Run this in CI against every model upgrade.

```python
from dataclasses import dataclass
from claude_agent_sdk import Agent
import time

@dataclass
class EvalCase:
    prompt: str
    expected_contains: list[str]       # Strings the response must contain
    expected_tool_calls: list[str]     # Tool names that must be invoked
    max_tokens_allowed: int = 5000
    max_latency_ms: int = 30_000

EVAL_SUITE = [
    EvalCase(
        prompt="How many users signed up last week?",
        expected_contains=["users", "signed up"],
        expected_tool_calls=["query_analytics"],
        max_tokens_allowed=2000,
    ),
    EvalCase(
        prompt="Summarise the Q2 revenue trends",
        expected_contains=["Q2", "revenue"],
        expected_tool_calls=["query_analytics", "format_report"],
        max_tokens_allowed=4000,
    ),
]

async def run_eval_suite(agent: Agent) -> dict:
    passed = 0
    results = []

    for case in EVAL_SUITE:
        start = time.monotonic()
        result = await agent.run(case.prompt)
        latency_ms = (time.monotonic() - start) * 1000

        content_ok  = all(term in result.text for term in case.expected_contains)
        tools_ok    = all(t in result.tool_names_called for t in case.expected_tool_calls)
        tokens_ok   = result.usage.total_tokens <= case.max_tokens_allowed
        latency_ok  = latency_ms <= case.max_latency_ms

        passed_case = content_ok and tools_ok and tokens_ok and latency_ok
        if passed_case:
            passed += 1

        results.append({
            "prompt": case.prompt[:80],
            "passed": passed_case,
            "content_ok": content_ok,
            "tools_ok": tools_ok,
            "tokens": result.usage.total_tokens,
            "latency_ms": round(latency_ms),
            "cost_usd": result.usage.cost_usd,
        })

    return {
        "pass_rate": passed / len(EVAL_SUITE),
        "total_cases": len(EVAL_SUITE),
        "total_cost_usd": sum(r["cost_usd"] for r in results),
        "results": results,
    }
```

### Stress Testing

```python
import asyncio, statistics, time
from claude_agent_sdk import Agent

async def stress_test(agent: Agent, n_concurrent: int = 20, n_total: int = 100):
    semaphore = asyncio.Semaphore(n_concurrent)
    latencies = []
    errors = []

    async def single_run(i: int):
        async with semaphore:
            start = time.monotonic()
            try:
                result = await agent.run(f"Quick analysis task #{i}: count rows in users table")
                latencies.append((time.monotonic() - start) * 1000)
                return result
            except Exception as e:
                errors.append({"index": i, "error": str(e)})

    tasks = [single_run(i) for i in range(n_total)]
    await asyncio.gather(*tasks)

    return {
        "total_requests": n_total,
        "error_count": len(errors),
        "error_rate_pct": len(errors) / n_total * 100,
        "p50_latency_ms": statistics.median(latencies),
        "p95_latency_ms": statistics.quantiles(latencies, n=20)[18],
        "p99_latency_ms": statistics.quantiles(latencies, n=100)[98],
        "errors": errors[:10],  # First 10 errors for diagnosis
    }
```

---

## 18. Managed Agents API

### SDK vs Managed Agents: When to Switch

Managed Agents is a hosted REST product where Anthropic runs the agent sandbox. You call it via HTTP and receive results without managing any infrastructure.

**Switch from Agent SDK to Managed Agents when:**

- You need zero-infrastructure deployment for a lightweight tool
- You are building a product integration that just needs Claude to act in a sandboxed environment
- Your data is not sensitive and does not need to stay on your infrastructure
- You are prototyping and want to defer infrastructure decisions

**Stay on Agent SDK when:**

- Data residency or network isolation is required
- You need custom state stores, billing, or rate limiting
- Your agent orchestration logic is complex (multi-tenant, multi-agent DAGs)
- You need cost attribution at the per-tenant or per-user level

### Managed Agents REST API Overview

```python
import httpx

MANAGED_AGENTS_BASE = "https://api.anthropic.com/v1/agents"
HEADERS = {
    "x-api-key": os.environ["ANTHROPIC_API_KEY"],
    "anthropic-version": "2025-11-25",
    "content-type": "application/json",
}

async def run_managed_agent(task: str, tools: list[str]) -> dict:
    async with httpx.AsyncClient() as client:
        # Create an agent run
        resp = await client.post(
            f"{MANAGED_AGENTS_BASE}/runs",
            headers=HEADERS,
            json={
                "model": "claude-sonnet-4-6",
                "task": task,
                "tools": tools,           # Tool allowlist (managed sandbox)
                "max_iterations": 20,
            },
        )
        resp.raise_for_status()
        run = resp.json()

        # Poll until complete
        while run["status"] in ("queued", "running"):
            await asyncio.sleep(2)
            poll = await client.get(
                f"{MANAGED_AGENTS_BASE}/runs/{run['id']}",
                headers=HEADERS,
            )
            run = poll.json()

        return {
            "status": run["status"],
            "result": run.get("result"),
            "usage": run.get("usage"),
        }
```

For enterprise cloud deployment (AWS Bedrock, GCP Vertex AI, Azure AI Foundry), see [Claude Enterprise Deployment 2026](claude-enterprise-2026.md).

---

## 19. Agent SDK Credits Billing

From **June 15, 2026**, Agent SDK usage is included in Claude.ai subscription plans via a monthly credit allocation. Credits are consumed per SDK agent run, distinct from direct API token billing.

| Plan | Monthly Credits | Approx. Agent Runs |
| ------ | ----------------- | -------------------- |
| Pro | $20/month | approximately 100–400 typical tasks |
| Max 5× | $100/month | approximately 500–2,000 typical tasks |
| Max 20× | $200/month | approximately 1,000–4,000 typical tasks |

:::note Credits vs API billing
    Credits apply when using the Agent SDK through Claude.ai. Direct API usage (raw Messages API) is billed at standard token rates regardless of subscription plan. If you are building a SaaS product that bills your own customers for agent usage, use the API directly with your API key, not subscription credits.

**Credit consumption factors:**

- Model selected (Haiku < Sonnet < Fable < Opus)
- Total tokens per run (input + output + cache operations)
- Number of tool calls per run
- Subagent spawning (each subagent run consumes separate credits)

**Credit optimisation:**

- Use Haiku for high-volume, simple subagent tasks
- Enable prompt caching for repeated stable context blocks
- Set `max_tokens` to the minimum required for each task type
- Batch non-latency-sensitive operations using the Messages Batch API

---

## Quick Reference: Production Deployment Checklist

### Before Launch

- [ ] Pin model to specific version (e.g., `claude-sonnet-4-6`, not `claude-sonnet-latest`)
- [ ] Set `CostLimit` with `max_cost_usd` hard cap on every agent
- [ ] Configure durable state store (Postgres or Redis) — never in-memory for production
- [ ] Enable structured logging with session IDs and user attribution on every event
- [ ] Implement per-user and per-tenant rate limiting at the application layer
- [ ] Sandbox all tool access — no unrestricted shell, file system, or network
- [ ] Add HITL checkpoints for every irreversible action
- [ ] Deploy circuit breaker for all downstream service dependencies
- [ ] Set up cost alerting at 80% and 100% of monthly budget
- [ ] Complete eval harness with ≥ 20 test cases; pass rate ≥ 95% required to ship

### Monitoring

- [ ] Alert on `task_completion_rate` < 95%
- [ ] Alert on `tool_error_rate` > 5%
- [ ] Alert on `p95_latency_ms` > 30,000
- [ ] Alert on circuit breaker state changes
- [ ] Export daily usage CSV for billing reconciliation
- [ ] PagerDuty/Slack alert on circuit breaker trips

### Security and Compliance

- [ ] Never log raw prompts or responses (may contain PII)
- [ ] Audit log every tool invocation: user ID, tool name, arguments (redacted), timestamp
- [ ] Validate all tool inputs before execution
- [ ] Rotate `ANTHROPIC_API_KEY` on a 90-day schedule
- [ ] Store API keys in secrets manager — never in source code or environment files committed to git
- [ ] Review agent tool access scope quarterly; remove unused tools

---

**This is Part 3 of 3. [← Back to Part 1](pathname:///archon/agentic-systems/coding-tools/30-claude-agent-sdk-production) | [Part 2](pathname:///archon/agentic-systems/coding-tools/parts/30-claude-agent-sdk-production-part2)**
