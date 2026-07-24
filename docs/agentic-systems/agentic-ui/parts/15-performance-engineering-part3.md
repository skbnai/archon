---
title: "Performance Engineering for Agentic Applications — Part 3"
date_created: 2026-07-24
last_reviewed: 2026-07-24
date_migrated: 2026-07-24
status: current
doc_type: guide
domain: agentic-systems
topic_id: performance-engineering-part3
supersedes:
  - docs/agentic-ui/performance-engineering.md
source: knowledge-docs
---

# Performance Engineering for Agentic Applications — Part 3

This is Part 3 of 3. [Return to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/15-performance-engineering) for metrics taxonomy, budget framework, TTFT, streaming, and tool latency. [Part 2 ←](pathname:///archon/agentic-systems/agentic-ui/parts/15-performance-engineering-part2) covers context assembly, memory retrieval, network optimization, and frontend rendering.

---

## 10. LLM Inference Optimization

### 10.1 Quantization Trade-Offs

| Quantization | VRAM Usage | Quality Loss | Throughput Gain | Use Case |
| ------------- | ----------- | ------------- | ---------------- | --------- |
| **FP32** (full precision) | 4× FP16 | None (baseline) | 0.5× FP16 | Training only |
| **FP16** (half precision) | Baseline | Negligible | Baseline | Standard production |
| **BF16** | Same as FP16 | Negligible | Same as FP16 | Preferred on H100/A100 |
| **INT8** | 0.5× FP16 | &lt; 1% on most benchmarks | 1.5–2× FP16 | Good quality/cost balance |
| **INT4** (GPTQ/AWQ) | 0.25× FP16 | 1–5% on benchmarks | 2–3× FP16 | Cost-optimized serving |
| **INT4 + INT8 mixed** | 0.3× FP16 | &lt; 2% | 2–2.5× FP16 | Recommended self-hosted default |

### 10.2 Inference Server Comparison

| Server | Continuous Batching | Multi-Model | Quantization | Best For |
| -------- | ------------------- | ------------ | ------------- | --------- |
| **vLLM** | Yes (PagedAttention) | Yes | GPTQ, AWQ, INT8 | General purpose; high throughput |
| **TGI** (HuggingFace) | Yes | Yes | INT8, INT4 | HuggingFace models; easy setup |
| **SGLang** | Yes (RadixAttention) | Yes | INT8 | Complex multi-call workloads |
| **Triton Inference Server** | Configurable | Yes | TensorRT-LLM | Enterprise; NVIDIA stack |
| **Ollama** | No | Yes | GGUF (Q4–Q8) | Development; laptop inference |
| **LM Studio** | No | No | GGUF | Development only |

**Choose vLLM** for production self-hosted inference. Its PagedAttention mechanism provides the best throughput for concurrent requests through efficient KV cache memory management.

### 10.3 KV Cache Management

KV Cache: The Hidden Performance Variable

Without KV cache management:
- Session 1: 10,000 tokens (fills 40% of GPU KV cache)
- Session 2: 8,000 tokens (fills 32%)
- Session 3: 15,000 tokens (fills 60%) → EVICTS session 1 + 2!
- New request for session 1 → must recompute from scratch

With PagedAttention (vLLM):
- KV cache stored in pages (blocks), not contiguous memory
- Pages allocated and freed like virtual memory
- No fragmentation → higher utilization → less eviction
- → 10–15× more concurrent sessions per GPU

### 10.4 Request Batching Strategies

| Strategy | Throughput | Latency | Implementation |
| ---------- | ----------- | -------- | ---------------- |
| **Static batching** | Medium | High (waits for batch) | Batch size N; wait until full |
| **Dynamic batching** | High | Medium | Batch with timeout; send partial batch if timeout reached |
| **Continuous batching** | Highest | Low | Insert new requests as old ones finish tokens |
| **Speculative batching** | Highest | Lowest | Draft model generates candidates; verify in batch |

---

## 11. Profiling Methodology

### 11.1 AG-UI Event Timeline Profiling

AG-UI Performance Profiling — Event Timeline

Timeline spans (OpenTelemetry):

t=0ms [user.submit_message]
t=10ms [auth.validate_token] ← 10ms
t=12ms [session.load_state] ← 2ms (Redis hit)
t=15ms [context.assemble starts] (duration: 385ms)
  - t=15ms [query.embed] ← 45ms
  - t=60ms [vector.search] ← 90ms
  - t=150ms [reranker.score] ← 200ms
  - t=350ms [context.format] ← 50ms
t=400ms [context.assemble ends]
t=400ms [llm.request_start]
t=410ms [llm.provider_queue] ← 10ms (no queue)
t=410ms [llm.first_token] ← 390ms
t=800ms [TTFT reached] (Total: 800ms from start)
t=800ms [stream.first_token_sent]
... streaming continues ...
t=4,200ms [stream.done]
... tool calls execute ...
t=4,200ms [tool.search_web.start]
t=5,100ms [tool.search_web.end] ← 900ms
t=4,200ms [tool.query_db.start] (parallel)
t=4,700ms [tool.query_db.end] ← 500ms
t=5,100ms [llm.second_request] (after tools)
t=5,500ms [llm.first_token] (second call)
t=8,300ms [stream.final_done]
t=8,300ms [E2E TASK LATENCY = 8,300ms total]

### 11.2 Server-Side Trace with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer("agent-orchestrator")

async def handle_user_message(session_id: str, message: str):
    with tracer.start_as_current_span(
        "agent.handle_message",
        kind=SpanKind.SERVER,
        attributes={
            "session.id": session_id,
            "message.length": len(message),
        }
    ) as root_span:

        # Context assembly
        with tracer.start_as_current_span("context.assemble") as ctx_span:
            context = await assemble_context(session_id, message)
            ctx_span.set_attribute("context.token_count", context.token_count)
            ctx_span.set_attribute("context.retrieval_count", len(context.fragments))

        # LLM call
        with tracer.start_as_current_span(
            "gen_ai.completion",
            attributes={
                "gen_ai.system": "anthropic",
                "gen_ai.request.model": "claude-sonnet-4-5",
                "gen_ai.request.max_tokens": 2048,
            }
        ) as llm_span:
            response = await call_llm(context)
            llm_span.set_attribute("gen_ai.usage.input_tokens", response.usage.input_tokens)
            llm_span.set_attribute("gen_ai.usage.output_tokens", response.usage.output_tokens)
            llm_span.set_attribute("gen_ai.response.ttft_ms", response.ttft_ms)
```

### 11.3 Browser Performance Timeline

```javascript
// Browser-side performance marking for agentic UI
class AgentPerfTracker {
  private marks: Record<string, number> = {};

  mark(name: string): void {
    this.marks[name] = performance.now();
    performance.mark(`agent:${name}`);
  }

  measure(name: string, start: string, end: string): number {
    performance.measure(`agent:${name}`, `agent:${start}`, `agent:${end}`);
    return this.marks[end] - this.marks[start];
  }

  reportToAnalytics(sessionId: string): void {
    const metrics = {
      session_id: sessionId,
      ttft_ms: this.measure('ttft', 'submit', 'first_token'),
      first_render_ms: this.measure('first_render', 'first_token', 'first_paint'),
      e2e_ms: this.measure('e2e', 'submit', 'task_complete'),
      streaming_lag_avg_ms: this.calculateAvgStreamingLag(),
    };

    // Send to analytics / RUM service
    navigator.sendBeacon('/analytics/performance', JSON.stringify(metrics));
  }
}

// Usage
const tracker = new AgentPerfTracker();
submitButton.addEventListener('click', () => tracker.mark('submit'));
eventSource.addEventListener('token', () => {
  if (isFirstToken) tracker.mark('first_token');
});
eventSource.addEventListener('done', () => {
  tracker.mark('task_complete');
  tracker.reportToAnalytics(sessionId);
});
```

### 11.4 Identifying Bottlenecks: Decision Tree

Performance Investigation Decision Tree

Symptom: High TTFT (&gt; 1.5s P95)
- Is CAT &gt; 600ms? YES → Bottleneck in context assembly
  - Is vector search &gt; 200ms? → Index tuning or Redis cache
  - Is reranker &gt; 300ms? → Switch to bi-encoder or reduce top-k
  - Is embedding &gt; 100ms? → Batch embedding or faster model
- Is provider queue time &gt; 200ms? YES → LLM provider throughput limit
  - Add more API keys (distribute RPM limit)
  - Route to faster model tier for this task
  - Enable request batching / queuing
- Is auth/routing &gt; 100ms? YES → Auth service bottleneck
  - JWT validation in middleware (no network hop)
  - Auth service scaling

Symptom: High Tool Latency (&gt; 3s P95)
- Are tools called sequentially? YES → Implement parallel tool execution
- Is tool API rate limited? YES → Tool response caching; multiple API keys
- Is single tool slow? YES → Per-tool investigation (check tool API status)

Symptom: High Streaming Lag (&gt; 300ms)
- Is token buffer filling up? YES → Increase buffer flush rate; check client consumption speed
- Is React re-rendering on every token? YES → Use startTransition; append text node directly
- Is network between server and client slow? YES → CDN edge; HTTP/2 multiplexing; compression for non-SSE

---

## 12. Performance Testing

### 12.1 Load Testing Agentic Workloads

```javascript
// k6 load test for agentic chat (ES module format)
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Trend } from 'k6/metrics';

const ttftTrend = new Trend('ttft_ms');
const taskCompleteTrend = new Trend('task_complete_ms');
const taskCompletionRate = new Counter('task_completed');

export let options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 50 },   // Sustain
    { duration: '2m', target: 100 },  // Spike
    { duration: '5m', target: 50 },   // Recovery
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    'ttft_ms': ['p(95)<1200'],
    'task_complete_ms': ['p(95)<30000'],
    'http_req_failed': ['rate<0.01'],
  },
};

export default function () {
  const sessionId = `test-session-${__VU}-${__ITER}`;

  // Initiate agent task
  const startTime = Date.now();
  const res = http.post(
    '/api/chat',
    JSON.stringify({
      session_id: sessionId,
      message: 'What are the top 3 issues in my support queue this week?',
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(res, { 'task started': (r) => r.status === 200 });
  const taskId = res.json('task_id');

  // Poll for first token (TTFT simulation)
  let ttftRecorded = false;
  let attempts = 0;
  while (attempts < 30) {
    const statusRes = http.get(`/api/tasks/${taskId}/events`);
    if (statusRes.json('has_first_token') && !ttftRecorded) {
      ttftTrend.add(Date.now() - startTime);
      ttftRecorded = true;
    }
    if (statusRes.json('status') === 'complete') {
      taskCompleteTrend.add(Date.now() - startTime);
      taskCompletionRate.add(1);
      break;
    }
    sleep(1);
    attempts++;
  }
}
```

### 12.2 Latency Regression Testing in CI

```yaml
# GitHub Actions step for performance regression testing
- name: Performance regression test
  run: |
    k6 run --out json=perf-results.json tests/perf/agent-load-test.js

- name: Compare with baseline
  run: |
    python scripts/compare_perf.py \
      --current perf-results.json \
      --baseline perf-baseline.json \
      --max-regression-pct 10 \
      --fail-on-regression

- name: Upload results
  uses: actions/upload-artifact@v3
  with:
    name: perf-results
    path: perf-results.json
```

### 12.3 Real-User Monitoring (RUM)

```typescript
// RUM SDK integration for agentic UI
import { datadogRum } from '@datadog/browser-rum';

// Track agent-specific custom actions
function trackAgentMetrics(event: AgentUIEvent): void {
  if (event.type === 'first_token') {
    datadogRum.addAction('agent.first_token', {
      session_id: event.sessionId,
      ttft_ms: event.ttft,
      model: event.model,
      has_tools: event.hasTools,
      context_tokens: event.contextTokens,
    });
  }

  if (event.type === 'task_complete') {
    datadogRum.addAction('agent.task_complete', {
      session_id: event.sessionId,
      e2e_ms: event.totalDuration,
      tool_count: event.toolsUsed,
      completion_status: event.status,
    });
  }
}

// Custom RUM views for conversation sessions
datadogRum.startView({
  name: 'agent_conversation',
  service: 'agent-ui',
});
```

---

## 13. Performance Reference Benchmarks

### 13.1 TTFT Ranges by Model Tier (2026, API-hosted)

| Model Tier | P50 | P95 | P99 | Notes |
| ----------- | ----- | ----- | ----- | ------- |
| Ultra-fast (Haiku/Flash) | 150–300ms | 400–700ms | 700–1,200ms | Best for classification, routing |
| Standard (Sonnet/GPT-4o) | 350–600ms | 800–1,400ms | 1,400–2,500ms | Best for general tasks |
| Advanced (Opus/GPT-4o-Preview) | 700–1,200ms | 1,500–3,000ms | 3,000–5,000ms | Best for complex reasoning |
| With RAG (+ vector retrieval) | Add 100–500ms | Add 200–800ms | Add 500–1,500ms | Varies by retrieval complexity |
| With semantic cache (35% hit) | −60ms avg | −100ms avg | −200ms avg | Cache hits skip retrieval |

### 13.2 Tool Latency Ranges by Type

| Tool Category | P50 | P95 | P99 | Notes |
| -------------- | ----- | ----- | ----- | ------- |
| In-memory lookup | 1–5ms | 5–15ms | 15–50ms | Redis, local state |
| Database read (indexed) | 5–30ms | 30–80ms | 80–200ms | Postgres, DynamoDB |
| Vector DB search | 10–50ms | 50–150ms | 150–400ms | Depends on index size |
| Internal API call | 20–100ms | 100–300ms | 300–800ms | Depends on service |
| External SaaS API | 100–500ms | 500–1,500ms | 1,500–5,000ms | Network-dependent |
| Web search | 300–800ms | 800–2,000ms | 2,000–5,000ms | Provider-dependent |
| Code execution (sandbox) | 500–2,000ms | 2,000–8,000ms | 8,000–30,000ms | Startup + execution |
| File/document processing | 200–1,000ms | 1,000–5,000ms | 5,000–20,000ms | File size–dependent |

### 13.3 Vector Retrieval Latency by DB and Index Size

| Vector DB | 100K vectors | 1M vectors | 10M vectors | 100M vectors |
| ----------- | ------------- | ----------- | ------------ | ------------- |
| Pinecone (s1) | 5–15ms | 10–30ms | 20–60ms | 40–120ms |
| Qdrant (HNSW) | 3–10ms | 5–20ms | 10–40ms | 20–80ms |
| Milvus (IVF_FLAT) | 5–20ms | 15–50ms | 30–100ms | 60–200ms |
| pgvector (ivfflat) | 10–40ms | 30–100ms | 80–300ms | Not recommended |
| Redis Vector | 2–5ms | 5–15ms | 15–50ms | Not recommended |

---

## 14. Performance Anti-Patterns

| # | Anti-Pattern | Description | Impact | Correct Pattern |
| --- | ------------- | ------------- | -------- | ----------------- |
| 1 | **Sequential Tool Calls** | Tools called one-at-a-time even when independent | N × tool latency instead of max(tool latency) | Parallel execution with `asyncio.gather` / `Promise.allSettled` |
| 2 | **No Prompt Cache** | System prompt rebuilt and billed in full every call | 100% input token cost for stable prefix | Mark stable prefix with `cache_control` |
| 3 | **Full Re-render per Token** | React state update on every token | Browser jank; main thread blocking | `startTransition` + text node append |
| 4 | **Synchronous Context Assembly** | Embed → search → rerank → history (sequential) | Each step waits for previous; 400–800ms wasted | Parallel assembly with independent sub-queries |
| 5 | **No Semantic Cache** | Same question asked 1000× hits LLM every time | 100× LLM cost for cached workloads | Semantic cache with cosine similarity threshold |
| 6 | **Same Model for All Tasks** | Using Opus for "summarize in 1 sentence" | 5–10× slower and more expensive than needed | Route to Haiku/Flash for simple tasks |
| 7 | **Unvirtualized Message List** | All 500 messages in DOM simultaneously | 500× render cost; scroll lag | Virtualized list (react-window) |
| 8 | **Synchronous Markdown Parsing** | Parse markdown on main thread per streaming token | UI jank during streaming | Web Worker for markdown + syntax highlighting |
| 9 | **No Tool Response Cache** | Weather/DB queries re-executed every turn | Redundant latency; unnecessary API cost | TTL cache by tool type |
| 10 | **Context Assembly After Queue** | Context assembled after LLM queue position reserved | Wasted time; LLM waits for context | Assemble context in parallel with queue wait |
| 11 | **No Streaming Buffer** | Each SSE token triggers individual DOM update | 100 tok/s = 100 DOM updates/s | Buffer tokens; flush at 60fps |
| 12 | **Blocking Auth on LLM Path** | Auth service called synchronously in hot path | 20–100ms added to every request | JWT validation in middleware (no network hop) |
| 13 | **Large Tool Schemas Every Call** | Full 50-tool JSON schema sent every request | 2,000–5,000 extra tokens per call | Dynamic tool selection; schema caching |
| 14 | **No Connection Pooling** | New TLS connection per LLM API call | 100ms+ overhead per call | HTTP connection pool with keep-alive |
| 15 | **SSE Buffering at Proxy** | Nginx/proxy buffers SSE before sending | Chunks accumulate; streaming appears batch | `X-Accel-Buffering: no`; `proxy_buffering off` |
| 16 | **No Compression for REST** | Large JSON payloads sent uncompressed | 3–10× payload overhead | gzip/brotli for REST (not SSE) |
| 17 | **Polling Instead of SSE** | Client polls `/status` every second for task completion | 1000 users = 1000 req/s overhead | SSE push notifications |
| 18 | **Missing Warmup** | Cold vector DB; cold LLM proxy; cold worker on first request | 2–10× latency on first requests after deploy | Readiness probe with warmup queries |
| 19 | **Full Context Reload on Tool Error** | Rebuilds entire context on tool retry | Double context assembly cost | Cache context; pass to retry |
| 20 | **No Inter-Token Latency Monitoring** | Only measuring TTFT, not streaming smoothness | Jittery streaming invisible in P95 | Monitor ITL (inter-token latency) variance |
| 21 | **Synchronous Reranker** | Reranker blocks context assembly | 200–500ms added to every RAG query | Async reranking; consider bi-encoder for P95 |
| 22 | **LLM as Classifier** | Using full LLM to classify/route simple queries | 300–800ms TTFT for a task that needs 10ms | Fine-tuned classifier or keyword router for simple cases |
| 23 | **No Budget Enforcement in CI** | Performance budgets defined but not enforced | Regressions ship unnoticed | k6 thresholds in CI pipeline |
| 24 | **Single-Threaded Tool Executor** | Tool executor processes calls sequentially | Fan-out blocked; multiplies tool latency | Async executor with concurrency controls |
