---
title: Scalability Engineering for Agentic Applications (Part 2)
domain: agentic-systems
status: current
doc_type: guide
topic_id: scalability-engineering-part2
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

# Scalability Engineering for Agentic Applications (Part 2)

**[Back to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/18-scalability-engineering)**

---

## 9. Backpressure

### 9.1 Token Bucket Rate Limiting at AG-UI Gateway

```python
import asyncio
import time
from dataclasses import dataclass

@dataclass
class TokenBucketConfig:
    capacity: int         # Max tokens in bucket
    refill_rate: float    # Tokens added per second
    initial_tokens: int   # Starting token count

class TokenBucket:
    """
    Token bucket rate limiter for AG-UI gateway.
    Limits requests per user/tenant per time window.
    """
    def __init__(self, config: TokenBucketConfig):
        self.capacity = config.capacity
        self.refill_rate = config.refill_rate
        self.tokens = float(config.initial_tokens)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        """Returns True if request is allowed; False if throttled."""
        async with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now

# Per-tenant rate limiting
class RateLimiter:
    def __init__(self, redis):
        self.redis = redis

    async def check_tenant(self, tenant_id: str, tokens: int = 1) -> bool:
        # Distributed token bucket using Redis atomic operations
        pipe = self.redis.pipeline()
        key = f"ratelimit:tenant:{tenant_id}"
        # Lua script for atomic check-and-consume
        lua = """
        local tokens = tonumber(redis.call('GET', KEYS[1]) or ARGV[2])
        local refill = tonumber(ARGV[1])
        tokens = math.min(tonumber(ARGV[2]), tokens + refill)
        if tokens >= tonumber(ARGV[3]) then
            redis.call('SET', KEYS[1], tokens - tonumber(ARGV[3]), 'EX', 60)
            return 1
        else
            redis.call('SET', KEYS[1], tokens, 'EX', 60)
            return 0
        end
        """
        result = await self.redis.eval(lua, 1, key, 0.5, 100, tokens)
        return bool(result)
```

### 9.2 Backpressure in Streaming Pipelines

Streaming Backpressure Flow:

LLM Provider (tokens arrive fast, ~100 tok/s)
  ↓
Token Buffer (per-session, max 500 tokens)
  - At 80% capacity: Signal upstream to pause token read, continue draining buffer
  - At &lt;20% capacity: Resume upstream token read
  ↓
Formatter (markdown → SSE event)
  ↓
SSE Writer
  - Client consuming fast: write immediately
  - Client slow (mobile/slow connection): Buffer formatted events (max 100), apply backpressure to Formatter, never drop tokens (keepalives only)
  ↓
Client Browser

---

## 10. Autoscaling

### 10.1 KEDA-Based Autoscaling

KEDA (Kubernetes Event-Driven Autoscaling) enables scaling on business metrics (queue depth, active sessions, GPU utilization) rather than just CPU/memory.

```yaml
# KEDA ScaledObject — Agent Orchestrator
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: agent-orchestrator-scaler
spec:
  scaleTargetRef:
    name: agent-orchestrator
  pollingInterval: 15       # Check every 15 seconds
  cooldownPeriod: 300       # Wait 5 min before scale-in
  minReplicaCount: 2
  maxReplicaCount: 50
  triggers:
    # Scale on task queue depth
    - type: kafka
      metadata:
        bootstrapServers: kafka:9092
        consumerGroup: agent-workers
        topic: agent-tasks-normal
        lagThreshold: "20"   # Scale out when 20+ messages per replica

    # Scale on active session count
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: active_agent_sessions
        threshold: "8"       # Scale out when > 8 sessions per replica
        query: sum(active_agent_sessions)

    # Scale on GPU utilization (for self-hosted models)
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: gpu_utilization
        threshold: "70"      # Scale out when GPU > 70% utilized
        query: avg(nvidia_gpu_utilization)
```

### 10.2 Scale-to-Zero for Cost Optimization

```yaml
# KEDA for batch agent workers — scale to zero when no tasks
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: batch-agent-scaler
spec:
  scaleTargetRef:
    name: batch-agent-worker
  minReplicaCount: 0   # Scale to zero when idle
  maxReplicaCount: 30
  triggers:
    - type: sqs
      metadata:
        queueURL: https://sqs.us-east-1.amazonaws.com/.../agent-tasks-batch
        queueLength: "1"   # Wake up when any message arrives
        awsRegion: us-east-1
```

### 10.3 Cold Start Mitigation

Scale-to-zero introduces cold start latency (model loading, dependency initialization). Mitigation strategies:

| Strategy | Latency Reduction | Cost Overhead | Complexity |
| --------- | ------------------ | --------------- | ----------- |
| **Warm pool** (keep N idle workers) | Eliminates cold start | Cost of N idle workers | Low |
| **Pre-initialized containers** | 50–70% reduction | Container image size | Medium |
| **Lazy model loading** (load on first request) | None | None | Low |
| **Predictive scaling** (pre-scale before demand) | Eliminates cold start | Over-provisioning | High |
| **HTTP request queuing** (queue first request until warm) | Hides cold start from user | Added first-request latency | Medium |

**Recommended:** Keep min 2 replicas always running (`minReplicaCount: 2`) for interactive workloads; use true scale-to-zero only for batch/background workloads where latency is not user-facing.

---

## 11. Concurrency Management

### 11.1 Concurrency Limits at Each Layer

| Layer | Limit Type | Recommended Default | Enforcement Mechanism |
| ------- | ----------- | -------------------- | ----------------------- |
| Per-user concurrent sessions | Per-user | 3 | Application middleware |
| Per-tenant concurrent sessions | Per-tenant | 100 | Rate limiter (Redis) |
| Per-user concurrent tool calls | Per-user | 10 | Semaphore in orchestrator |
| Per-tool concurrent calls (global) | Per-tool | 50 | Tool executor semaphore |
| Per-LLM-provider concurrent requests | Per-provider | 20 | LLM proxy semaphore |
| Agent worker global concurrency | System-wide | workers × 10 | Worker pool configuration |

### 11.2 Semaphore Pattern for Tool Pools

```python
import asyncio
from typing import Dict

class ConcurrencyManager:
    """Manages per-tool and per-user concurrency limits."""

    def __init__(
        self,
        per_tool_limits: Dict[str, int],
        per_user_limit: int = 10,
        global_limit: int = 500
    ):
        self._tool_semaphores: Dict[str, asyncio.Semaphore] = {
            tool: asyncio.Semaphore(limit)
            for tool, limit in per_tool_limits.items()
        }
        self._user_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._global_semaphore = asyncio.Semaphore(global_limit)
        self._per_user_limit = per_user_limit

    def _user_semaphore(self, user_id: str) -> asyncio.Semaphore:
        if user_id not in self._user_semaphores:
            self._user_semaphores[user_id] = asyncio.Semaphore(self._per_user_limit)
        return self._user_semaphores[user_id]

    async def execute(
        self,
        tool_name: str,
        user_id: str,
        func,
        *args,
        **kwargs
    ):
        tool_sem = self._tool_semaphores.get(
            tool_name,
            asyncio.Semaphore(10)  # Default if tool not in config
        )
        user_sem = self._user_semaphore(user_id)

        async with self._global_semaphore:
            async with user_sem:
                async with tool_sem:
                    return await func(*args, **kwargs)
```

---

## 12. Multi-Region Deployment

### 12.1 Multi-Region Topology

Multi-Region Active-Active Topology:

Global Load Balancer (latency-based routing) routes to three regions:

US-EAST Region:
  - Agent Orchestrator
  - LLM Proxy
  - Tool Executor
  - Redis Cluster

EU-WEST Region:
  - Agent Orchestrator
  - LLM Proxy
  - Tool Executor
  - Redis Cluster

AP-SOUTH Region:
  - Agent Orchestrator
  - LLM Proxy
  - Tool Executor
  - Redis Cluster

All regions connect to:
  - Global State (DynamoDB Global Tables / Cosmos DB multi-region)

Replication strategy:
  - Session checkpoints: async, <5s lag
  - User preferences: sync write
  - Idempotency cache: primary-preferred
  - Conversation archive: async batch

### 12.2 Data Sovereignty Constraints

| Constraint | Impact | Design Response |
| ----------- | -------- | ---------------- |
| EU GDPR: data must stay in EU | Cannot replicate EU user data to US | EU session data never leaves EU region; global LB enforces geo-fencing |
| Healthcare (HIPAA): PHI must stay in compliant region | No session state replication to non-compliant regions | Compliant region isolated; failover within-region only |
| Financial (SOC2/PCI): audit logs must be complete | Cannot lose events in replication | Synchronous event log replication; accept higher latency |
| Government (FedRAMP): sovereign cloud | Cannot use shared multi-tenant infrastructure | Dedicated region in AWS GovCloud or Azure Government |

---

## 13. GPU Scheduling

### 13.1 GPU Allocation for Self-Hosted Models

For organizations running their own LLM inference, GPU scheduling is the primary scalability constraint.

| Model Size | VRAM Required | Suitable GPU | Concurrent Requests (naive) | With Continuous Batching |
| ----------- | -------------- | ------------- | --------------------------- | -------------------------- |
| 7B FP16 | 14 GB | A100 40GB (x1) | 1–2 | 8–12 |
| 13B FP16 | 26 GB | A100 40GB (x1) | 1 | 5–8 |
| 70B FP16 | 140 GB | H100 80GB (x2) | 1 | 3–5 |
| 70B INT4 (quantized) | 35 GB | A100 40GB (x1) | 1–2 | 6–10 |
| 405B FP8 | 200 GB | H100 80GB (x3) | 1 | 2–4 |

### 13.2 Continuous Batching for Throughput

Traditional batching waits for a full batch before processing. Continuous batching processes requests as they arrive, inserting new requests into in-progress batches when sequences complete.

```
Traditional Batching vs Continuous Batching

Traditional:
  t=0: [req1, req2, req3] -> process batch -> [resp1, resp2, resp3]
  t=1: [req4, req5]       -> wait... -> process -> [resp4, resp5]
  req4 waits the entire batch-1 duration even if it's simple

Continuous Batching (vLLM):
  t=0: [req1, req2, req3] -> start processing
  t=2: req1 finishes -> insert req4 into batch immediately
  t=3: req2 finishes -> insert req5 into batch
  -> Throughput 2–3× higher for mixed-length workloads
```

### 13.3 Multi-Model GPU Scheduling

When running multiple models on shared GPU infrastructure, use time-sharing with priority queues:

| Model | Role | Priority | Max VRAM | SLO (TTFT) |
| ------- | ------ | --------- | --------- | ----------- |
| Claude Haiku-class (small) | Planning, routing | High | 14GB | 200ms |
| Claude Sonnet-class (medium) | Standard tasks | Normal | 28GB | 800ms |
| Claude Opus-class (large) | Complex reasoning | Low | 80GB | 3,000ms |

---

## 14. Connection Pooling

### 14.1 Connection Pool Configuration

| Component | Pool Size | Max Idle | Timeout | Validation |
| ----------- | ----------- | --------- | --------- | ------------ |
| LLM Provider HTTP client | 50 | 20 | 60s connect; 120s read | TCP keepalive |
| Tool API HTTP clients | 20 per tool | 10 | 15s connect; 30s read | Health check before use |
| PostgreSQL (session storage) | 20 per worker | 10 | 5s connect; 30s query | SELECT 1 |
| Redis (state cache) | 50 | 25 | 1s connect; 3s command | PING |
| Vector DB client | 10 per worker | 5 | 3s connect; 10s query | Client-specific health |

---

## 15. Capacity Planning Framework

### 15.1 Load Model

```
Agentic Application Load Model

Peak concurrent sessions:
  = peak_daily_users × session_overlap_factor
  Example: 10,000 DAU × 0.05 overlap = 500 concurrent sessions

Tokens per session:
  = avg_turns × (avg_input_tokens + avg_output_tokens)
  Example: 8 turns × (800 input + 600 output) = 11,200 tokens/session

Total token throughput (peak):
  = concurrent_sessions × tokens_per_minute_per_session
  Example: 500 × 1,400 TPM/session = 700,000 TPM at peak

Tool calls per session:
  = avg_turns × avg_tool_calls_per_turn
  Example: 8 × 2.5 = 20 tool calls/session

Peak tool call rate:
  = concurrent_sessions × tool_calls_per_minute
  Example: 500 × (20/5 min) = 2,000 tool calls/minute
```

### 15.2 Sizing Formulas

| Component | Formula | Example |
| ----------- | --------- | --------- |
| Agent workers | `ceil(peak_sessions / sessions_per_worker)` | `ceil(500 / 10) = 50 workers` |
| LLM proxy instances | `ceil(peak_TPM / TPM_per_proxy_instance)` | `ceil(700K / 200K) = 4 instances` |
| Tool executor instances | `ceil(peak_tool_calls_per_min / calls_per_instance)` | `ceil(2000 / 500) = 4 instances` |
| Redis memory | `peak_sessions × avg_session_size_KB` | `500 × 50 KB = 25 MB` (easily fits) |
| Vector DB (memory) | `num_embeddings × embedding_dim × 4 bytes × 1.5 overhead` | `1M × 1536 × 4 × 1.5 = 9.2 GB` |

### 15.3 Cost Model

| Architecture Decision | Monthly Cost Impact | Notes |
| ---------------------- | ------------------- | ------- |
| Active-active multi-region (3 regions) | 2.5–3× single region | Full redundancy cost |
| Scale-to-zero batch workers | 40–60% reduction vs always-on | Cold start trade-off |
| Semantic caching (35% hit rate) | 25–30% LLM cost reduction | Higher for repetitive workloads |
| Prompt caching (stable system prompt) | 40–60% input token cost reduction | Anthropic/OpenAI prefix cache |
| Self-hosted 70B model vs API | Break-even at ~$30K/month API spend | Depends on GPU cluster cost |
| Vector DB managed vs self-hosted | Managed: 2–3× self-hosted at scale | But operational overhead significant |

---

## 16. Benchmark Methodology

### 16.1 Agentic Benchmark Scenarios

Unlike pure throughput benchmarks, agentic workloads require measuring quality degradation under load, not just latency and throughput.

| Scenario | Description | Duration | Success Criteria |
| ---------- | ------------- | --------- | ----------------- |
| **Ramp test** | Linearly increase load 0 → 2× peak over 10 min | 10 min | No error rate increase until 80% peak |
| **Soak test** | Sustain 80% peak load for 4 hours | 4 hours | Error rate stable; no memory leak; quality maintained |
| **Spike test** | Instant 5× load spike for 60 seconds | 60 sec spike | System recovers to baseline within 5 min post-spike |
| **Quality-under-load** | Standard load with LLM judge sampling every 5min | 1 hour | Task completion rate does not degrade > 5% vs baseline |
| **Chaos + load** | Inject tool failure at 75% peak load | 30 min | Graceful degradation; no cascading failure |
| **Cold start** | Scale-to-zero -> spike | Single event | First request served within SLO after cold start |

### 16.2 Key Benchmark Metrics

In addition to latency (P50/P95/P99) and throughput (requests/second), agentic benchmarks must measure:

| Metric | Why It Matters | Measurement Method |
| -------- | -------------- | ------------------- |
| Task completion rate under load | Quality may degrade before latency | LLM judge on sampled outputs |
| Tool success rate under load | Tool APIs may throttle under spike | Tool result outcome tracking |
| Context assembly time under load | Memory service may become bottleneck | OTel spans |
| Error budget burn rate | Rate of budget consumption during test | SLO dashboard |
| Autoscale response time | How quickly workers appear under spike | Scale event timestamps |

---

## 17. Scalability Anti-Patterns

| # | Anti-Pattern | Description | Impact | Correct Pattern |
| --- | ------------- | ------------- | -------- | ----------------- |
| 1 | **State in Worker Memory** | Session state stored only in agent worker process | Instance crash = session loss; cannot scale horizontally | Externalize state to Redis/DB |
| 2 | **Synchronous Tool Fan-Out** | Agent calls 10 tools sequentially | 10× latency vs parallel | Parallel tool execution with semaphores |
| 3 | **No Connection Pooling** | New HTTP connection per LLM call | 100ms TLS overhead per call at scale | Connection pools with keep-alive |
| 4 | **Single Queue, No Priority** | All tasks in one queue | Batch jobs block interactive chat | Priority queues: HIGH / NORMAL / BATCH |
| 5 | **No Semantic Cache** | Every query hits LLM even for repeat questions | 100% LLM costs; no deflection | Semantic cache with similarity threshold |
| 6 | **Polling Instead of Push** | Client polls /status every second | 1000 users × 1 req/s = 1000 req/s overhead | SSE push or WebSocket |
| 7 | **LLM Provider Single Point** | All traffic to one provider | Provider outage = total outage | Multi-provider routing with failover |
| 8 | **No Rate Limiting** | Unlimited requests per user | One heavy user starves others | Per-user and per-tenant rate limits |
| 9 | **Synchronous Context Assembly** | Context assembly blocks response | High P99 from slow retrievals | Async pre-warming; parallel retrieval |
| 10 | **Sticky Session Without Drain** | Rolling deploy without draining sessions | Active streams interrupted | preStop hook with session drain |
| 11 | **Uniform Token Budget** | Same context size for all tasks | Wasteful for simple tasks; insufficient for complex | Dynamic token budget by task type |
| 12 | **No Autoscale Cooldown** | Autoscaler scales in immediately after spike | Thrashing — up/down/up/down | 5-minute cooldown before scale-in |
| 13 | **Synchronous Saga Rollback** | Wait for all rollbacks before responding | User waits minutes for failure confirmation | Async rollback; immediate safe state |
| 14 | **No Queue Depth Alert** | Queue silently fills | Silent backlog builds; latency spikes surprise | Alert on queue depth > 50% of threshold |
| 15 | **Over-Provisioned Workers** | Always 50 workers even at 10% load | 5× cost at idle | KEDA scale-to-fit with min replicas |
| 16 | **Unbounded Tool Concurrency** | 500 users each fan-out 20 tools = 10,000 concurrent tool calls | Tool API rate limit hit; cascading failure | Per-tool semaphore limits |
| 17 | **No GPU KV Cache Management** | KV cache overflows silently | Context window effectively shrinks; quality degrades | Monitor and alert on KV cache utilization |
| 18 | **Exact-Match LLM Cache Only** | Cache hit rate < 5% | Cache provides no meaningful cost reduction | Semantic caching with embedding similarity |
| 19 | **No DLQ Monitoring** | DLQ silently fills | Tasks lost; sagas incomplete | DLQ depth alert; processor with runbook |
| 20 | **Homogeneous Model Routing** | Same model for all task types | Paying for Opus when Haiku would do | Task complexity routing |
| 21 | **No Data Sovereignty in Routing** | EU user data routed to US region on failover | GDPR violation | Geo-fencing rules in global load balancer |
| 22 | **Benchmark Throughput Only** | k6 tests measure req/s but not quality | System passes load test; quality degrades in production | Quality-under-load benchmarks with LLM judge |
| 23 | **Monolithic Tool Executor** | All tools in one process | One slow tool blocks all tools | Separate tool executor service with bulkheads |
| 24 | **No Session Affinity for Streaming** | Round-robin routing for SSE streams | SSE connections interrupted on each request | Sticky sessions for streaming connections |

---

## 18. Scalability Decision Matrix

| Decision | Option A | Option B | Choose A When | Choose B When |
| ---------- | --------- | --------- | -------------- | -------------- |
| **Session state** | Stateless (externalized) | Stateful (in-memory) | Sessions < 5 min; horizontal scale priority | Long-running tasks > 5 min; latency critical |
| **LLM routing** | Single provider | Multi-provider | Development/test; cost simplicity | Production; > 99.9% availability required |
| **Queue system** | Managed (SQS/Pub Sub) | Self-hosted (Kafka) | < 1M msg/day; ops simplicity | > 1M msg/day; complex routing; compliance |
| **Vector DB** | Managed (Pinecone/Weaviate Cloud) | Self-hosted (Qdrant/pgvector) | < 10M vectors; ops simplicity | > 10M vectors; cost sensitivity; data control |
| **Deployment** | Kubernetes + KEDA | Serverless (Lambda/Cloud Run) | Sustained load > 20% of day; GPU required | Bursty/irregular load; no GPU; ops minimal |
| **Caching** | Semantic cache | Exact cache | High query diversity; NLP domain | Deterministic queries; structured lookups |
| **Multi-region** | Active-active | Active-passive | < 200ms global latency required; high traffic | Cost sensitive; strong consistency required; simple failover |
| **Model hosting** | Self-hosted GPU | Provider API | > $30K/month API spend; data sovereignty | < $30K/month; no GPU team; flexibility |

---

**This is Part 2 of 3. [Continue with Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/18-scalability-engineering-part3) for implementation roadmap, decision trees, and production deployment guidance.**
