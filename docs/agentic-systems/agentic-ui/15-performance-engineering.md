---
title: "Performance Engineering for Agentic Applications"
date_created: 2026-07-24
last_reviewed: 2026-07-24
date_migrated: 2026-07-24
status: current
doc_type: guide
domain: agentic-systems
topic_id: performance-engineering
supersedes:
  - docs/agentic-ui/performance-engineering.md
source: knowledge-docs
---

# Performance Engineering for Agentic Applications

A comprehensive performance reference for AI Platform Teams and Principal Architects covering metrics taxonomy, optimization techniques, and profiling methodology from browser rendering through LLM inference for agentic UIs.

:::note Related Guides
    - Reliability under load (circuit breakers, degradation): [reliability-engineering](pathname:///archon/agentic-systems/agentic-ui/16-reliability-engineering)
    - Scaling for throughput (caching, queues, autoscaling): [scalability-engineering](pathname:///archon/agentic-systems/agentic-ui/18-scalability-engineering)
    - OTel GenAI observability spans: [agentic-ai-reliability-observability-governance](../../architecture/43-agentic-ai-reliability-observability-governance.md)

---

## 1. Performance Metrics Taxonomy

Agentic applications require a new vocabulary of performance metrics. Traditional web metrics (TTFB, FCP, LCP) are necessary but insufficient — they miss the LLM-specific and agentic-specific latencies that dominate user-perceived performance.

### 1.1 Full Metrics Taxonomy

| Metric | Abbreviation | Measurement Point | What It Represents |
| -------- | ------------- | ------------------ | ------------------- |
| Time to First Byte | TTFB | Server → first HTTP byte | Server processing start; includes routing, auth |
| Time to First Token | TTFT | Server → first SSE token event | LLM begins generating; most important UX metric |
| Time to Usable UI | TTUI | Browser → first meaningful render | User sees something useful; skeleton → content |
| First Contentful Paint | FCP | Browser paint | First DOM content visible (standard web metric) |
| Tool Latency P50/P95/P99 | TL | Tool call start → result | Per tool type; critical for planning quality |
| End-to-End Task Latency | E2E | User submit → task complete | Wall-clock time for the full agent task |
| Streaming Lag | SL | Token generated → browser render | Gap between LLM output and visual display |
| Context Assembly Time | CAT | Start build → context ready | Vector retrieval + reranking + composition |
| Planning Latency | PL | Plan request → plan ready | Planner model response time |
| Memory Retrieval Latency | MRL | Query → results ranked | Vector search + reranker time |
| Render Latency | RL | DOM update → paint | React reconciliation + browser repaint |
| Token Throughput | TT | Tokens per second | Sustained generation rate |
| Inter-Token Latency | ITL | Time between consecutive tokens | Perceived streaming smoothness |
| Time to Complete Turn | TTCT | User submit → full response | Complete turn round-trip |

### 1.2 Metrics by User Interaction Type

| Interaction Type | Primary Metric | Secondary Metrics | P95 Target |
| ----------------- | --------------- | ------------------ | ----------- |
| Simple Q&A (no tools) | TTFT | E2E, Streaming Lag | TTFT &lt; 800ms, E2E &lt; 5s |
| Tool-augmented Q&A | TTFT + Tool Latency | CAT, E2E | TTFT &lt; 1s, E2E &lt; 8s |
| Multi-step agentic task | E2E | Progress events P95, PL | E2E &lt; 45s for 5-step task |
| RAG-heavy research | CAT + TTFT | MRL, E2E | CAT &lt; 500ms, E2E &lt; 15s |
| Code generation + execution | E2E | Planning Latency, Tool Latency | E2E &lt; 30s |
| Document analysis | TTFT | Context Assembly, E2E | TTFT &lt; 1.5s |
| Autonomous background task | E2E (async) | Checkpoint frequency | E2E &lt; 5min for complex task |

### 1.3 Concurrency-Adjusted Metrics

Single-user benchmarks are misleading. Always report metrics under representative concurrent load:

| Metric | Single User | 10 Concurrent | 50 Concurrent | 200 Concurrent |
| -------- | ------------ | -------------- | -------------- | ---------------- |
| TTFT P50 | 450ms | 480ms | 520ms | 750ms |
| TTFT P95 | 800ms | 950ms | 1,200ms | 2,100ms |
| E2E P50 | 4.2s | 4.5s | 5.1s | 7.8s |
| Tool Latency P95 | 1.1s | 1.3s | 1.8s | 3.5s |
| Task Completion Rate | 96% | 95% | 93% | 88% |

Degradation above 200 concurrent users (in this example) signals a scalability bottleneck — investigate with the profiling methodology in Section 11.

---

## 2. Performance Budget Framework

### 2.1 Performance Budget by Interaction Type

A performance budget allocates the total latency allowance across layers. Tracking against budgets in CI catches regressions before they reach production.

| Interaction | Total Budget | TTFT Budget | CAT Budget | Tool Budget | Render Budget |
| ------------ | ------------- | ------------ | ----------- | ------------- | -------------- |
| Simple Q&A | 5,000ms | 800ms | 200ms | 0ms | 100ms |
| RAG Q&A | 8,000ms | 1,000ms | 600ms | 400ms | 100ms |
| Tool-augmented | 10,000ms | 1,200ms | 400ms | 2,000ms | 150ms |
| Multi-step task | 30,000ms | 1,500ms | 600ms | 3,000ms (×3) | 200ms |
| Autonomous task | 300,000ms | N/A (async) | 1,000ms | 5,000ms (×5) | N/A |

### 2.2 Budget Allocation Principles

1. **Reserve 20% for overhead** — network jitter, GC pauses, scheduler delays
2. **Tool budgets are per-call** — a 3-tool task has 3× the tool budget, not shared
3. **Streaming lag compounds** — every 100ms of streaming lag degrades perceived quality
4. **Context assembly must be pre-allocated** — CAT before TTFT; it adds to total wall-clock

### 2.3 Budget Enforcement in CI/CD

```yaml
# k6 performance budget enforcement
# Fails the build if any threshold is violated
export let options = {
  thresholds: {
    // TTFT P95 must be under 1,200ms
    'http_req_duration{name:first_token}': ['p(95)<1200'],

    // End-to-end task P95 under 30s
    'http_req_duration{name:task_complete}': ['p(95)<30000'],

    // Tool call P95 under 2s
    'http_req_duration{name:tool_call}': ['p(95)<2000'],

    // Error rate under 1%
    'http_req_failed': ['rate<0.01'],

    // Task completion rate over 90%
    'task_completion_rate': ['rate>0.90'],
  },
};
```

---

## 3. First-Token Latency Optimization

TTFT is the single most important user-perceived performance metric for agentic chat. Users tolerate streaming delay once the first token arrives; they do not tolerate staring at a spinner.

### 3.1 TTFT Decomposition

User click (t=0)
- Network: browser → gateway (10–50ms, CDN helps)
- Auth + routing: (20–80ms with JWT validation)
- Context assembly: (100–600ms, RAG retrieval dominant)
  - Query embedding: 20–80ms
  - Vector search: 30–200ms
  - Reranking: 50–300ms
  - Context formatting: 10–30ms
- Prompt construction: (5–20ms, template rendering)
- LLM TTFT (provider-side): (200–1500ms, model-dependent)
  - Queue time at provider: 0–500ms (depends on load)
  - KV cache lookup: 10–50ms
  - First token generation: 100–800ms
- Network: provider → gateway → browser (10–50ms)

Total TTFT: ~400ms (best) to ~2,600ms (worst case with RAG)

### 3.2 Optimization Techniques

| Technique | Latency Reduction | Complexity | Notes |
| ----------- | ------------------ | ----------- | ------- |
| **Prompt prefix caching** | 30–60% on TTFT | Low | Provider-side; mark stable prefix with cache_control |
| **Context pre-warming** | 100–400ms | Medium | Pre-fetch likely context before user submits |
| **Parallel context assembly** | 50–70% of sequential CAT | Medium | Embedding + vector search in parallel |
| **Small planning model** | 200–600ms on planning | Medium | Fast model for plan; capable model for execution |
| **Streaming start immediately** | 0ms (perceived) | Low | Start streaming before tool calls complete |
| **Speculative decoding** | 20–40% TTFT improvement | High | Requires model-level support (vLLM) |
| **Request prioritization** | Reduces queue time | Medium | Priority queue; interactive > batch |
| **Edge inference** | 30–100ms | Very high | Deploy small model at CDN edge |

### 3.3 Provider-Side TTFT by Model Tier (2026 Reference)

| Provider + Model | TTFT P50 | TTFT P95 | Token Speed | Best For |
| ----------------- | --------- | --------- | ------------ | --------- |
| Claude claude-haiku-4-5 | 150ms | 350ms | 180 tok/s | Planning, routing, classification |
| Claude claude-sonnet-4-5 | 400ms | 900ms | 120 tok/s | Standard agentic tasks |
| Claude Opus 4 | 800ms | 1,800ms | 70 tok/s | Complex reasoning, analysis |
| GPT-4o mini | 200ms | 500ms | 160 tok/s | Fast tasks, tool calling |
| GPT-4o | 450ms | 1,100ms | 90 tok/s | General purpose |
| Gemini 2.0 Flash | 180ms | 400ms | 200 tok/s | Speed-critical paths |
| Self-hosted 7B (vLLM, A100) | 100ms | 250ms | 120 tok/s | Low-latency on-prem |
| Self-hosted 70B (vLLM, 2×H100) | 350ms | 800ms | 80 tok/s | High-capability on-prem |

:::tip Model Routing for TTFT
    Route the planning phase to claude-haiku-4-5 (TTFT ~150ms) and execution to Claude claude-sonnet-4-5. This cuts planning latency by 60% vs using Sonnet for everything, without impacting execution quality for most tasks.

---

## 4. Streaming Performance

### 4.1 SSE vs WebSocket Benchmark Comparison

| Attribute | SSE (Server-Sent Events) | WebSocket |
| ----------- | ------------------------ | ----------- |
| **Protocol** | HTTP/1.1+; native browser EventSource | Custom upgrade; binary framing |
| **Direction** | Server → client only | Bidirectional |
| **Reconnect** | Automatic with Last-Event-ID | Manual |
| **Proxy support** | Excellent (HTTP-native) | Variable (some proxies block) |
| **Load balancer support** | Good (sticky sessions needed) | Good (sticky sessions needed) |
| **Latency per event** | 1–5ms overhead | 0.5–2ms overhead |
| **Memory per connection** | 2–4 KB | 4–8 KB |
| **Throughput ceiling** | 10K–50K connections per server | 50K–100K connections per server |
| **Best for agentic UI** | Standard chat streaming | High-frequency bidirectional events (collaborative agents) |

**For most agentic UIs, SSE is the correct default.** WebSocket adds complexity for minimal gain in one-directional streaming use cases.

### 4.2 Streaming Buffer Management

```typescript
// Browser-side streaming buffer with backpressure
class StreamingBuffer {
  private buffer: string[] = [];
  private renderTimer: number | null = null;
  private readonly FLUSH_INTERVAL_MS = 16;  // ~60fps
  private readonly MAX_BUFFER_SIZE = 100;

  constructor(private readonly onFlush: (tokens: string[]) => void) {}

  push(token: string): void {
    this.buffer.push(token);

    if (this.buffer.length >= this.MAX_BUFFER_SIZE) {
      // Immediate flush if buffer is full
      this.flush();
      return;
    }

    // Schedule flush on next animation frame (batches for smooth rendering)
    if (!this.renderTimer) {
      this.renderTimer = requestAnimationFrame(() => this.flush());
    }
  }

  private flush(): void {
    if (this.buffer.length === 0) return;
    const tokens = [...this.buffer];
    this.buffer = [];
    this.renderTimer = null;
    this.onFlush(tokens);
  }
}
```

### 4.3 Progressive Rendering and Skeleton UI

```typescript
// React streaming UI with progressive enhancement
import { useState, useTransition, Suspense } from 'react';

function AgentMessageStream({ sessionId }: { sessionId: string }) {
  const [content, setContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isPending, startTransition] = useTransition();

  const startStream = async () => {
    setIsStreaming(true);
    const eventSource = new EventSource(`/stream/${sessionId}`);

    eventSource.addEventListener('token', (e) => {
      const { token } = JSON.parse(e.data);
      // Use startTransition so token updates don't block user interactions
      startTransition(() => {
        setContent(prev => prev + token);
      });
    });

    eventSource.addEventListener('done', () => {
      setIsStreaming(false);
      eventSource.close();
    });
  };

  return (
    <div className="agent-message">
      {isStreaming && content === '' && (
        // Show skeleton while waiting for TTFT
        <MessageSkeleton lines={3} />
      )}
      {content && (
        <MarkdownRenderer
          content={content}
          streaming={isStreaming}
        />
      )}
      {isStreaming && (
        <StreamingCursor />
      )}
    </div>
  );
}
```

### 4.4 Incremental DOM Updates

Full re-renders on every token are expensive and cause visual jank. Use incremental text node appending:

```typescript
// Efficient streaming text rendering — append, don't re-render
class StreamingTextRenderer {
  private container: HTMLElement;
  private currentParagraph: HTMLParagraphElement | null = null;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  appendToken(token: string): void {
    if (!this.currentParagraph) {
      this.currentParagraph = document.createElement('p');
      this.container.appendChild(this.currentParagraph);
    }

    // Append text node directly — no React reconciliation overhead
    if (this.currentParagraph.lastChild?.nodeType === Node.TEXT_NODE) {
      this.currentParagraph.lastChild.textContent! += token;
    } else {
      this.currentParagraph.appendChild(document.createTextNode(token));
    }

    // Handle paragraph breaks in streaming content
    if (token.includes('\n\n')) {
      this.currentParagraph = null;
    }
  }
}
```

---

## 5. Tool Latency Optimization

### 5.1 Parallel Tool Execution

Sequential tool execution multiplies latency. Execute independent tools in parallel wherever possible.

Sequential Tool Execution (AVOID):
- search_web → 800ms
- query_database → 400ms
- fetch_document → 600ms
- Total: 1,800ms

Parallel Tool Execution (PREFERRED):
- search_web 800ms
- query_database 400ms
- fetch_document 600ms
- All complete at 800ms (55% faster)

=== "Python"
    ```python
    import asyncio
    from typing import Any

    async def execute_tools_parallel(tool_calls: list[dict]) -> list[Any]:
        """
        Execute independent tool calls in parallel.
        Preserves order of results matching order of input.
        """
        tasks = [
            asyncio.create_task(
                execute_tool(call["name"], call["arguments"]),
                name=f"tool-{call['id']}"
            )
            for call in tool_calls
        ]
        # gather preserves order, collects all results even if some fail
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [
            {"tool_use_id": call["id"], "content": result}
            if not isinstance(result, Exception)
            else {"tool_use_id": call["id"], "error": str(result)}
            for call, result in zip(tool_calls, results)
        ]
    ```

=== "TypeScript"
    ```typescript
    async function executeToolsParallel(
      toolCalls: Array<{ id: string; name: string; input: unknown }>
    ): Promise<Array<{ toolUseId: string; content?: unknown; error?: string }>> {
      const results = await Promise.allSettled(
        toolCalls.map(call => executeTool(call.name, call.input))
      );

      return results.map((result, i) => ({
        toolUseId: toolCalls[i].id,
        ...(result.status === 'fulfilled'
          ? { content: result.value }
          : { error: result.reason?.message ?? 'Unknown error' }
        ),
      }));
    }
    ```

### 5.2 Tool Response Caching

```python
import hashlib
import json
from typing import Any, Optional
import asyncio

class ToolResponseCache:
    def __init__(self, redis, default_ttl: int = 300):
        self.redis = redis
        self.ttl_by_tool = {
            "search_web": 300,        # 5 minutes
            "query_database": 30,     # 30 seconds
            "get_user_profile": 300,  # 5 minutes
            "fetch_document": 3600,   # 1 hour
            "get_weather": 600,       # 10 minutes
            "send_email": 0,          # Never cache (side effect)
            "write_database": 0,      # Never cache (side effect)
        }
        self.default_ttl = default_ttl

    def _cache_key(self, tool_name: str, args: dict) -> Optional[str]:
        ttl = self.ttl_by_tool.get(tool_name, self.default_ttl)
        if ttl == 0:
            return None  # This tool must not be cached
        content = json.dumps({"tool": tool_name, "args": args}, sort_keys=True)
        h = hashlib.sha256(content.encode()).hexdigest()[:20]
        return f"tool:cache:{h}"

    async def get_or_execute(self, tool_name: str, args: dict, executor) -> Any:
        key = self._cache_key(tool_name, args)
        if key is None:
            return await executor(tool_name, args)  # Never cache

        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)  # Cache hit

        result = await executor(tool_name, args)
        ttl = self.ttl_by_tool.get(tool_name, self.default_ttl)
        if ttl > 0:
            await self.redis.setex(key, ttl, json.dumps(result))
        return result
```

### 5.3 Predictive Pre-Fetching

For common tool call sequences, pre-fetch likely tool results before the agent explicitly requests them:

```python
# Tool call prediction patterns (learned from conversation analytics)
PREDICTIVE_PATTERNS = {
    # When user asks about a customer, pre-fetch their profile
    "customer_inquiry": {
        "trigger": lambda msg: any(w in msg for w in ["customer", "account", "user"]),
        "prefetch": ["get_customer_profile", "get_recent_orders"]
    },
    # When user asks about a ticket, pre-fetch ticket details
    "ticket_query": {
        "trigger": lambda msg: "ticket" in msg or "issue" in msg,
        "prefetch": ["get_ticket_details", "get_ticket_history"]
    }
}

async def prefetch_likely_tools(user_message: str, session_context: dict):
    """Pre-fetch tool results in background before agent starts planning."""
    prefetch_tasks = []
    for pattern_name, pattern in PREDICTIVE_PATTERNS.items():
        if pattern["trigger"](user_message.lower()):
            for tool_name in pattern["prefetch"]:
                # Extract likely args from context
                args = extract_args_from_context(tool_name, session_context)
                prefetch_tasks.append(
                    asyncio.create_task(
                        tool_cache.get_or_execute(tool_name, args, execute_tool)
                    )
                )
    if prefetch_tasks:
        # Run in background; results will be in cache when agent asks
        asyncio.gather(*prefetch_tasks, return_exceptions=True)
```

### 5.4 Tool Selection Optimization

Each additional tool in the agent's tool set increases planning time and the probability of wrong tool selection. Optimize by:

| Strategy | Latency Impact | Quality Impact | Implementation |
| ---------- | -------------- | -------------- | ---------------- |
| Dynamic tool selection | -200ms planning | +5% accuracy | Select tools based on query category |
| Tool set tiering | -100ms planning | Neutral | Basic tier (5 tools) vs full tier (25 tools) |
| Tool description compression | -50ms TTFT | Neutral | Shorter tool descriptions = fewer tokens |
| Tool schema caching | -30ms | Neutral | Cache compiled tool schemas in memory |
| Retire unused tools | -10ms per tool | Neutral | Remove tools with &lt; 0.1% usage rate |

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/15-performance-engineering-part2) for context assembly, memory retrieval, network optimization, and frontend rendering performance.**

## Related

- [Observability for Agentic Applications](14-observability.md) — the telemetry this performance work depends on.
- [Scalability Engineering for Agentic Applications](18-scalability-engineering.md) — the closely related scaling discipline.
