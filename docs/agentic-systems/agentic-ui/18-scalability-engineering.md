---
title: Scalability Engineering for Agentic Applications
domain: agentic-systems
status: current
doc_type: guide
topic_id: scalability-engineering
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - ../knowledge-docs/docs/agentic-ui/scalability-engineering.md
related_docs:
  - reliability-engineering
  - ../cloud-platforms/ai-gateway/kong-ai-gateway-guide
  - ../enterprise-architecture/ai-architecture/agent-memory-planning-architecture
---

# Scalability Engineering for Agentic Applications

A comprehensive scalability reference for AI Platform Teams and Principal Architects covering stateless design, horizontal scaling patterns, queue architectures, autoscaling, GPU scheduling, and capacity planning for agentic systems from frontend through LLM inference.

**Build on the foundation:** Circuit breakers and degradation under load are covered in [reliability-engineering](16-reliability-engineering.md). AI Gateway load balancing and rate limiting are in [Kong AI Gateway Guide](../../platforms/index.md). Agent memory and state scaling details are in [Agent Memory Planning Architecture](../../architecture/41-agent-memory-planning-architecture.md).

---

## 1. Scalability Dimensions Unique to Agentic Applications

Agentic applications impose fundamentally different scalability constraints than stateless REST APIs. Understanding these differences is prerequisite to selecting the right scaling strategies.

### 1.1 The Four Hard Problems

| Scalability Problem | Traditional App | Agentic App | Engineering Impact |
| -------------------- | ---------------- | ------------- | ------------------- |
| **Stateful conversations** | Each request independent | Session state must follow user or be accessible from any instance | Session affinity OR expensive state externalization |
| **Long-running tasks** | < 1s per request | 30s – 30min per task | Persistent connections; heartbeats; worker lifecycle management |
| **Token throughput bottleneck** | CPU/memory bound | LLM token generation is the primary ceiling | Cannot scale past provider TPM (tokens-per-minute) limits |
| **Tool call fan-out** | Linear request processing | One user message triggers 5–20 parallel tool calls | Concurrency spikes; downstream API rate limit cascade |

### 1.2 The Agentic Scalability Stack

```
Agentic Application Scalability Layers

Layer 6: Frontend (React)
  - Virtualized conversation history
  - SSE backpressure signalling
  - Service Worker for offline/caching

Layer 5: AG-UI Gateway (Edge/CDN)
  - SSE termination and fan-in
  - Rate limiting per user/tenant
  - Token bucket throttling

Layer 4: Agent Orchestrator
  - Horizontal worker pool scaling
  - Session affinity or state externalization
  - Task queue management

Layer 3: LLM Proxy / AI Gateway
  - Multi-provider load balancing
  - Semantic caching
  - Retry and fallback logic

Layer 2: Tool Executor Service
  - Per-tool connection pools
  - Parallel fan-out with concurrency limits
  - Result caching by tool type and TTL

Layer 1: Memory and Storage
  - Vector DB horizontal scaling (shard by collection)
  - Redis cluster for hot state
  - Tiered storage: hot to warm to cold
```

### 1.3 Token Throughput: The Primary Ceiling

LLM token generation is the hard scalability ceiling for most agentic deployments. Unlike CPU or memory, which can be scaled horizontally with cost, token throughput is governed by provider limits.

| Constraint Type | Source | Typical Limit | Scale-Out Option |
| ---------------- | -------- | --------------- | ----------------- |
| RPM (requests per minute) | Provider tier | 500 – 10,000 RPM | Multi-provider routing; multiple API keys |
| TPM (tokens per minute) | Provider tier | 40K – 4M TPM | Distribute across provider tiers |
| TPD (tokens per day) | Provider tier | Hard daily cap | Batch workloads in off-peak windows |
| Concurrent requests | Provider | 10 – 500 | Queue management + circuit breaking |
| Context window | Model | 8K – 2M tokens | Context compression to extend effective throughput |

---

## 2. Stateless Architecture Patterns

### 2.1 Session State Externalization

Moving session state out of the agent worker process enables any instance to serve any request, enabling true horizontal scaling.

| Storage Option | Latency | Consistency | Cost | Best For |
| --------------- | --------- | ------------- | ------ | --------- |
| **Redis Cluster** | &lt; 1ms | Strong (single shard) | Medium | Hot session data; streaming position |
| **DynamoDB / Cosmos DB** | 5–15ms | Strong (provisioned) | Medium-high | Session metadata; turn history |
| **PostgreSQL** | 5–20ms | ACID | Low-medium | Structured conversation history |
| **Object Storage (S3/GCS)** | 50–200ms | Eventual | Very low | Long-term archive; context snapshots |
| **Memcached** | &lt; 1ms | None (no persistence) | Low | Ephemeral context fragments only |

```python
# Session state externalization pattern
from redis.asyncio import Redis
import json
from typing import Optional
from dataclasses import dataclass, asdict

@dataclass
class SessionState:
    session_id: str
    user_id: str
    conversation_history: list
    current_plan: dict
    tool_results_cache: dict
    last_event_id: str
    degradation_level: int = 1

class ExternalizedSessionStore:
    def __init__(self, redis: Redis, ttl_seconds: int = 3600):
        self.redis = redis
        self.ttl = ttl_seconds

    async def load(self, session_id: str) -> Optional[SessionState]:
        data = await self.redis.get(f"session:{session_id}")
        if data is None:
            return None
        return SessionState(**json.loads(data))

    async def save(self, state: SessionState) -> None:
        await self.redis.setex(
            f"session:{state.session_id}",
            self.ttl,
            json.dumps(asdict(state))
        )

    async def update_field(self, session_id: str, field: str, value) -> None:
        """Partial update without loading full state."""
        # Use Redis hash for granular field updates
        await self.redis.hset(f"session:h:{session_id}", field, json.dumps(value))
        await self.redis.expire(f"session:h:{session_id}", self.ttl)
```

### 2.2 Event-Sourced Conversation State

Event sourcing stores the append-only log of conversation events rather than a mutable state snapshot. Any worker can reconstruct the current state by replaying the event log.

```
Event-Sourced Conversation

Event Log (append-only):
  evt-001: UserMessage  { content: "Book a flight to NYC" }
  evt-002: PlanCreated  { steps: ["search_flights", "check_price", "book"] }
  evt-003: ToolCall     { tool: "search_flights", args: {...} }
  evt-004: ToolResult   { tool: "search_flights", result: {...} }
  evt-005: AgentThought { content: "Best option is AA101 at $450" }
  evt-006: ToolCall     { tool: "book_flight", args: {...} }
  evt-007: ToolResult   { tool: "book_flight", result: { confirmation: "XYZ" }}
  evt-008: AgentMessage { content: "Your flight is booked. Confirmation: XYZ" }

Benefits:
  - Any worker can reconstruct state from evt-001..N
  - Built-in audit trail
  - Natural replay for debugging
  - Streaming resync via Last-Event-ID

Trade-offs:
  - State reconstruction cost grows with event count
  - Requires periodic snapshots for long sessions
  - Event schema must be versioned carefully
```

### 2.3 Stateless vs Stateful Worker Trade-Offs

| Aspect | Stateless Workers | Stateful Workers |
| -------- | ------------------- | ----------------- |
| Scaling | Simple horizontal — add instances | Complex — must migrate or drain sessions |
| Memory efficiency | Load state on each request (cache miss cost) | Keep hot state in memory (fast) |
| Fault tolerance | Any worker can take over on crash | Session lost unless migrated first |
| Deployment | Rolling deploy with zero-downtime | Requires session drain before instance replacement |
| Cost | Higher Redis/DB read cost per request | Higher per-instance memory cost |
| Recommended use | Interactive chat (short sessions &lt; 5min) | Long-running tasks (&gt; 5min); autonomous agents |

---

## 3. Sticky Sessions and Session Affinity

### 3.1 When Sticky Sessions Are Required

Sticky sessions route a user's requests to the same backend instance. They are required when:

1. **Active streaming connection** — an SSE/WebSocket connection is live; it cannot be moved to another instance without interruption
2. **In-memory tool execution state** — a running agent task has partial results in RAM
3. **GPU-based inference** — the model's KV cache for the session lives on a specific GPU
4. **Tool connection pools** — the worker has an open, authenticated connection to a tool API that cannot be transferred

Sticky sessions are NOT required when:

- State is fully externalized (Redis)
- Request is idempotent (retrieval, read-only)
- Task is queued and not yet started

### 3.2 Consistent Hashing for Agent Assignment

```
Consistent Hashing Ring — Agent Worker Assignment

        Worker-A
           |
    W-D ---+--- W-B
           |
        Worker-C

Session routing:
  hash(session_id) mod ring_size -> nearest worker clockwise

  Example:
    session-001 -> hash: 0x3F -> nearest clockwise: Worker-B
    session-002 -> hash: 0x7A -> nearest clockwise: Worker-C
    session-003 -> hash: 0xC1 -> nearest clockwise: Worker-A

  When Worker-B is removed (rolling deploy):
    Only Worker-B's sessions are rehashed
    Worker-A, Worker-C sessions unchanged
    -> Minimizes session disruption during deploys
```

### 3.3 Session Draining for Rolling Deployments

```yaml
# Kubernetes deployment with session draining
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-orchestrator
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0   # Never reduce capacity
  template:
    spec:
      terminationGracePeriodSeconds: 300  # 5min for active sessions to complete
      containers:
        - name: agent-orchestrator
          lifecycle:
            preStop:
              exec:
                command:
                  - /bin/sh
                  - -c
                  - |
                    # Signal: stop accepting new sessions
                    curl -X POST http://localhost:8080/admin/drain
                    # Wait for active sessions to complete (max 4min)
                    timeout 240 /bin/sh -c 'while [ $(curl -s http://localhost:8080/admin/active-sessions) -gt 0 ]; do sleep 5; done'
```

---

## 4. Horizontal Scaling Patterns

### 4.1 Agent Worker Pool Scaling

```
Agent Worker Pool Architecture

Task Queue (Kafka/SQS)
        |
        v
Agent Worker Pool (KEDA-scaled)

  Worker-1   Worker-2   Worker-N
  Sessions   Sessions   Sessions
  max: 10    max: 10    max: 10

  Scale trigger: queue_depth / max_sessions_per_worker
  Min replicas: 2   Max replicas: 50
  Scale-out: queue_depth > 20 for 30s
  Scale-in: queue_depth < 5 for 5min
```

### 4.2 LLM Proxy/Gateway Layer Scaling

The LLM proxy is a critical scaling layer. It should be stateless and scaled independently from agent workers.

| Concern | Pattern | Config Example |
| --------- | --------- | --------------- |
| Multi-provider routing | Weighted round-robin | Claude 60%, GPT-4o 30%, Gemini 10% |
| Rate limit distribution | Token bucket per provider | 400K TPM per provider instance |
| Semantic caching | Embedding similarity > 0.95 → return cache | TTL: 5min for deterministic; 0 for creative |
| Failover | Circuit breaker per provider | Open after 5 failures in 10s |
| Authentication | API key rotation and secret management | Rotate every 30 days; multiple keys per provider |

### 4.3 Tool Executor Scaling

Tool calls are often the highest-fan-out component. Each user message may trigger 5–20 tool calls, some in parallel.

```python
import asyncio
from typing import List, Any
from dataclasses import dataclass

@dataclass
class ToolCallSpec:
    tool_name: str
    args: dict
    timeout_seconds: float = 15.0
    max_concurrent: int = 5  # Per-tool concurrency limit

class ToolExecutor:
    def __init__(self):
        # Per-tool semaphores prevent any single tool from overwhelming its API
        self._semaphores: dict = {}

    def _get_semaphore(self, tool_name: str, max_concurrent: int) -> asyncio.Semaphore:
        if tool_name not in self._semaphores:
            self._semaphores[tool_name] = asyncio.Semaphore(max_concurrent)
        return self._semaphores[tool_name]

    async def execute_parallel(
        self,
        tool_calls: List[ToolCallSpec],
        global_timeout: float = 30.0
    ) -> List[Any]:
        """
        Execute tool calls in parallel, respecting per-tool concurrency limits.
        Returns results in the same order as input, with errors inlined.
        """
        async def execute_one(spec: ToolCallSpec) -> Any:
            sem = self._get_semaphore(spec.tool_name, spec.max_concurrent)
            async with sem:
                try:
                    return await asyncio.wait_for(
                        self._call_tool(spec.tool_name, spec.args),
                        timeout=spec.timeout_seconds
                    )
                except asyncio.TimeoutError:
                    return {"error": "timeout", "tool": spec.tool_name}
                except Exception as e:
                    return {"error": str(e), "tool": spec.tool_name}

        return await asyncio.gather(
            *[execute_one(spec) for spec in tool_calls],
            return_exceptions=False
        )

    async def _call_tool(self, tool_name: str, args: dict) -> Any:
        # Tool dispatch logic
        pass
```

---

## 5. Caching Strategy

### 5.1 Semantic Caching

Semantic caching returns cached responses when a new query is semantically equivalent to a prior query, even without an exact string match.

Semantic Cache Lookup Flow:

New query: "What is the capital of France?"
  Step 1: Embed query → vector [0.21, 0.88, ...]
  Step 2: ANN search in cache index (cosine similarity)
  Step 3a (Hit): Nearest match "What's France's capital city?" (similarity: 0.97)
    - 0.97 > threshold (0.92) → CACHE HIT
    - Return cached response: "The capital of France is Paris."
  Step 3b (Miss): No match above threshold → CACHE MISS
    - Call LLM → store embedding + response in cache

Semantic cache configuration decisions:

| Parameter | Conservative | Balanced | Aggressive |
| ----------- | ------------- | --------- | ----------- |
| Similarity threshold | 0.97 | 0.92 | 0.85 |
| Cache TTL | 1 hour | 6 hours | 24 hours |
| Max cache size | 10K entries | 100K entries | 1M entries |
| Hit rate expectation | 5–15% | 20–35% | 40–60% |
| Staleness risk | Very low | Low | Medium |
| Best for | Medical / legal (high accuracy req.) | General enterprise | FAQ-heavy, stable domain |

### 5.2 Tool Response Caching

| Tool Type | Cacheable? | TTL | Cache Key | Invalidation |
| ----------- | ----------- | ----- | ----------- | ------------- |
| Web search | Yes (soft) | 5 min | query + date | Time-based |
| Database read | Yes | 30 sec | SQL hash + params | Write invalidation |
| File read | Yes | 60 sec | path + etag | etag change |
| Calendar lookup | Yes | 2 min | user + date range | Calendar update event |
| Weather | Yes | 10 min | location + time | Time-based |
| Code execution | No | — | — | Too variable |
| Email send | No | — | — | Side effect; never cache |
| Database write | No | — | — | Side effect; use idempotency |
| Real-time stock | No | — | — | Too volatile |
| User profile | Yes | 5 min | user_id | Profile update event |

### 5.3 LLM Prompt Caching

LLM providers (Anthropic, OpenAI) offer prefix caching: if the same prompt prefix is sent repeatedly, the provider caches the KV state for that prefix and charges less for cache hits.

```python
# Anthropic prompt caching — mark stable prefix with cache_control
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": STABLE_SYSTEM_PROMPT,  # Same across all requests
            "cache_control": {"type": "ephemeral"}  # Cache this prefix
        }
    ],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": LARGE_DOCUMENT,  # Same document, cache it
                    "cache_control": {"type": "ephemeral"}
                },
                {
                    "type": "text",
                    "text": user_question  # Dynamic per-request; not cached
                }
            ]
        }
    ]
)
# usage.cache_read_input_tokens -> tokens served from cache (90% cost reduction)
# usage.cache_creation_input_tokens -> tokens written to cache (25% cost premium)
```

**Cache cost analysis:**

| Scenario | Without Cache | With Cache (steady state) | Cost Reduction |
| ---------- | ------------- | -------------------------- | ---------------- |
| 10K token system prompt, 1000 users/day | $30/day | $4/day | 87% |
| 50K token document analysis, 500 users/day | $150/day | $20/day | 87% |
| 1K token system prompt (small) | $3/day | $2.4/day | 20% (break-even at ~50 uses) |

### 5.4 Context Fragment Caching

For RAG-heavy agents, cache retrieved context fragments by embedding so the same retrieval query doesn't hit the vector DB repeatedly.

```python
from hashlib import sha256
import json
from typing import Optional, List

class ContextFragmentCache:
    def __init__(self, redis, ttl_seconds: int = 300):
        self.redis = redis
        self.ttl = ttl_seconds

    def _cache_key(self, query_embedding: List[float], top_k: int) -> str:
        # Round embedding to 3 decimal places for cache key stability
        rounded = [round(x, 3) for x in query_embedding]
        h = sha256(json.dumps({"emb": rounded, "k": top_k}).encode()).hexdigest()[:16]
        return f"ctx:frag:{h}"

    async def get(self, embedding: List[float], top_k: int) -> Optional[list]:
        key = self._cache_key(embedding, top_k)
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set(self, embedding: List[float], top_k: int, fragments: list) -> None:
        key = self._cache_key(embedding, top_k)
        await self.redis.setex(key, self.ttl, json.dumps(fragments))
```

---

## 6. Edge Rendering and CDN

### 6.1 Edge Architecture for Agentic UIs

Edge + Origin Architecture:

Users (global) → CDN Edge (Cloudflare Workers / Fastly / CloudFront)

CDN Edge Routes:
  - /static/* → Serve from edge cache (UI assets, fonts, icons)
  - /api/chat (POST) → Pass through to origin
  - /stream/session/* → Edge SSE termination
    • Edge maintains SSE connection to client
    • Edge polls or subscribes to origin for events
    • Edge buffers and replays for reconnects
  - /api/tools/* → Origin (cannot cache; side effects)

Origin (Regional) contains:
  - Agent Orchestrator (k8s)
  - LLM Proxy
  - Tool Executor

### 6.2 Edge SSE Termination

Terminating SSE at the edge (rather than origin) reduces the number of long-lived connections that origin servers must maintain.

| Metric | Without Edge SSE | With Edge SSE |
| -------- | ----------------- | -------------- |
| Long-lived connections at origin | = concurrent users | = CDN PoP count |
| Origin server thread/connection cost | High (per-user) | Low (per PoP) |
| User latency | Origin latency | Edge latency (&lt; 20ms) |
| Reconnect behaviour | Client → origin | Client → edge → origin buffers |
| Complexity | Low | High (edge-origin event bus required) |

---

## 7. Load Balancing

### 7.1 Layer 7 Load Balancing for Streaming

Standard round-robin load balancing breaks streaming connections. Streaming requires:

1. **Connection persistence** — once a streaming connection is established, all packets must go to the same origin
2. **Drain support** — before removing an instance, drain all active streams gracefully
3. **Health checks that understand streaming** — health check must verify SSE endpoint, not just HTTP 200

```nginx
# Nginx config for sticky streaming with AG-UI
upstream agent_workers {
    least_conn;  # Route new connections to least-loaded worker

    server worker-1:8080;
    server worker-2:8080;
    server worker-3:8080;

    keepalive 128;  # Keep upstream connections open
}

server {
    location /stream/ {
        proxy_pass http://agent_workers;

        # Streaming-specific settings
        proxy_buffering off;          # Disable response buffering for SSE
        proxy_cache off;
        proxy_read_timeout 3600s;     # Keep connection alive for 1 hour
        proxy_send_timeout 3600s;

        # Session affinity by session_id cookie
        proxy_set_header X-Session-ID $cookie_session_id;

        # SSE headers
        proxy_set_header Accept-Encoding "";
        add_header Cache-Control no-cache;
        add_header Content-Type "text/event-stream";
        add_header X-Accel-Buffering no;
    }
}
```

### 7.2 LLM Provider Load Balancing

| Strategy | Best For | Configuration |
| ---------- | --------- | --------------- |
| **Round-robin** | Homogeneous providers | Distribute evenly across identical providers |
| **Weighted round-robin** | Primary + secondary split | Claude 70% (primary) + GPT-4o 30% (secondary) |
| **Least connections** | Minimizing latency variance | Route to provider with fewest active requests |
| **Priority failover** | Cost optimization | Always use primary; failover only on circuit open |
| **Cost-based routing** | Cost optimization at scale | Route to cheapest provider meeting latency SLO |
| **Task-based routing** | Capability optimization | Complex tasks → Claude Opus; simple → Claude Haiku |

---

## 8. Queue Architecture

### 8.1 Task Queue for Long-Running Agent Jobs

Queue Architecture — Long-Running Agent Tasks:

Producer Side:
  - API Gateway receives POST /agent/tasks (returns task_id immediately)
  - Enqueues to Task Queue (Kafka / SQS)

Task Queue with Priority Queues:
  - HIGH: HITL tasks, real-time
  - NORMAL: standard chat tasks
  - BATCH: background pipelines (off-peak)
  - Dead Letter Queue: failed tasks after 3 failures (routed to ops team)

Consumer Side:
  - Agent Workers poll HIGH, NORMAL, and BATCH queues
  - Process tasks and update status

Client Interface:
  - Polls `GET /agent/tasks/{task_id}/status` for status updates
  - OR receives push via SSE stream

### 8.2 Queue Configuration Reference

**Kafka (self-hosted):**

```yaml
# Kafka topic configuration for agent tasks
topics:
  agent-tasks-high:
    partitions: 12        # Match number of high-priority workers
    replication-factor: 3
    config:
      retention.ms: 3600000    # 1 hour (tasks expire)
      max.message.bytes: 1048576  # 1MB max task payload

  agent-tasks-normal:
    partitions: 30
    replication-factor: 3
    config:
      retention.ms: 86400000   # 24 hours

  agent-tasks-dlq:
    partitions: 6
    replication-factor: 3
    config:
      retention.ms: 604800000  # 7 days for investigation
```

**AWS SQS:**

```python
import boto3

sqs = boto3.client('sqs')

# Create main queue with DLQ
dlq_response = sqs.create_queue(
    QueueName='agent-tasks-dlq',
    Attributes={
        'MessageRetentionPeriod': '604800',  # 7 days
    }
)
dlq_arn = sqs.get_queue_attributes(
    QueueUrl=dlq_response['QueueUrl'],
    AttributeNames=['QueueArn']
)['Attributes']['QueueArn']

main_queue = sqs.create_queue(
    QueueName='agent-tasks-normal.fifo',
    Attributes={
        'FifoQueue': 'true',
        'ContentBasedDeduplication': 'false',
        'VisibilityTimeout': '300',     # 5 min processing window
        'MessageRetentionPeriod': '86400',  # 24 hours
        'RedrivePolicy': f'{{"deadLetterTargetArn":"{dlq_arn}","maxReceiveCount":"3"}}',
    }
)
```

### 8.3 Queue Depth Monitoring and Autoscaling Triggers

| Queue | Scale-Out Trigger | Scale-In Trigger | Max Workers | Min Workers |
| ------- | ------------------ | ----------------- | ------------- | ------------- |
| agent-tasks-high | depth > 5 for 30s | depth = 0 for 5min | 20 | 2 |
| agent-tasks-normal | depth > 20 for 60s | depth < 3 for 5min | 50 | 2 |
| agent-tasks-batch | depth > 100 for 5min | depth < 10 for 15min | 30 | 0 (scale-to-zero) |
| tool-executor | depth > 50 for 30s | depth < 10 for 5min | 100 | 3 |

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/18-scalability-engineering-part2) for backpressure, autoscaling, concurrency management, multi-region deployment, GPU scheduling, connection pooling, and capacity planning.**
