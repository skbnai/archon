---
title: "Performance Engineering for Agentic Applications — Part 2"
date_created: 2026-07-24
last_reviewed: 2026-07-24
date_migrated: 2026-07-24
status: current
doc_type: guide
domain: agentic-systems
topic_id: performance-engineering-part2
supersedes:
  - docs/agentic-ui/performance-engineering.md
source: knowledge-docs
---

# Performance Engineering for Agentic Applications — Part 2

This is Part 2 of 3. [Return to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/15-performance-engineering) for metrics taxonomy, budget framework, TTFT, streaming, and tool latency.

---

## 6. Context Assembly Performance

### 6.1 Parallel Context Assembly Pipeline

Sequential (SLOW):
- Embed query → 50ms
- Vector search → 150ms
- Rerank → 200ms
- Load conv. history → 30ms
- Load user prefs → 20ms
- Merge + format → 20ms
- Total: 480ms

Parallel (FAST):
- Embed query → 50ms (start)
- Check cache → 10ms (parallel)
- Load conv. history → 30ms (parallel)
- Load user prefs → 20ms (parallel)
- Vector search → 150ms (wait for embed)
- Rerank → 200ms (parallel w/ history)
- Merge + format → 20ms
- Total: ~420ms (vs 480ms sequential)
- Savings: ~12% + eliminates idle waits

### 6.2 Context Compression Algorithms

When the retrieved context exceeds the token budget, compression is necessary. The choice of algorithm affects both latency and quality.

| Algorithm | Latency | Compression Ratio | Quality Loss | Use Case |
| ----------- | --------- | ------------------- | ------------- | --------- |
| **Truncation** (tail) | 0ms | Up to 90% | High (loses context) | Never recommended |
| **Truncation** (smart: preserve system prompt + recent) | 1ms | Up to 70% | Medium | Last resort |
| **Extractive summarization** | 50–150ms | 60–80% | Low | Conversation history |
| **LLMLingua** (token-level) | 100–500ms | 50–75% | Low-medium | Long documents |
| **RECOMP** (extract-compress) | 200–800ms | 60–80% | Low | RAG passages |
| **LLM summarization** (small model) | 500–2000ms | 70–90% | Very low | Critical context |
| **Hierarchical summarization** | 1000–5000ms | 80–95% | Low | Very long sessions |

**Recommendation:** Use extractive summarization for conversation history (fast, good quality), and LLMLingua for retrieved document passages (better compression with acceptable latency).

### 6.3 Chunking Strategy Impact on Retrieval Speed

The document chunking strategy used at indexing time directly affects retrieval latency at query time.

| Chunking Strategy | Chunk Size | Retrieval Recall | Retrieval Latency | Notes |
| ------------------ | ----------- | ----------------- | ------------------ | ------- |
| Fixed-size (512 tokens) | Fixed | Medium | Fast | Simple; misses cross-chunk context |
| Sentence-aware | Variable (50–200 tokens) | High | Fast | Better boundaries; more chunks |
| Paragraph-aware | Variable (100–500 tokens) | High | Medium | Good default |
| Semantic (embedding-based) | Variable | Highest | Slow (indexing) | Best quality; expensive to index |
| Hierarchical (parent+child) | Multi-level | High | Medium | Returns parent for context; child for precision |
| Sliding window (overlap 20%) | Fixed + overlap | High | Medium | Good for dense docs; more storage |

---

## 7. Memory Retrieval Performance

### 7.1 Vector DB Performance Comparison

| Vector DB | Latency P50 (1M vectors) | Latency P95 (1M vectors) | QPS (single node) | Best For |
| ----------- | ------------------------ | ------------------------ | ------------------ | --------- |
| **Pinecone** (managed) | 10–30ms | 50–80ms | 500–2,000 | Production; managed; fast setup |
| **Weaviate** (managed) | 15–40ms | 60–100ms | 400–1,500 | Hybrid search; multi-tenancy |
| **Qdrant** (self-hosted) | 5–20ms | 20–50ms | 1,000–5,000 | High performance; self-hosted |
| **Chroma** (self-hosted) | 20–60ms | 80–200ms | 100–500 | Development; small scale |
| **pgvector** (PostgreSQL) | 30–100ms | 100–500ms | 100–400 | Existing Postgres; < 1M vectors |
| **Milvus** (self-hosted) | 5–15ms | 20–40ms | 2,000–10,000 | Large scale; high QPS |
| **Redis Vector** | 2–8ms | 10–25ms | 5,000–20,000 | Ultra-low latency; small corpus |

**Choose when:**

- Pinecone / Weaviate: managed cloud, production use, moderate scale
- Qdrant / Milvus: self-hosted, > 10M vectors, high QPS requirement
- pgvector: already using PostgreSQL, < 500K vectors, operational simplicity
- Redis Vector: < 100K vectors, latency SLO < 10ms

### 7.2 Tiered Memory Architecture

HOT TIER (Redis, < 5ms):
- Current conversation context (last 20 turns)
- User session preferences
- Frequently retrieved facts (LRU cache)
- Tool results cache
- TTL: 1–24 hours

WARM TIER (Vector DB, 10–80ms):
- Long-term user memory (last 90 days)
- Organizational knowledge base
- Document chunks + embeddings
- Conversation summaries
- TTL: 90 days – 1 year

COLD TIER (Object Storage, 100–500ms):
- Full conversation archive
- Raw documents
- Context snapshots for replay
- Compliance audit logs
- TTL: Retention policy (often 7 years for compliance)

Access pattern:
1. Check hot tier (&lt; 5ms)
2. On miss: query warm tier (10–80ms); populate hot tier
3. On miss: retrieve from cold tier (100–500ms); populate warm tier

### 7.3 Index Warm-Up Strategies

Cold vector DB instances have high P99 latency on first queries. Warm up before serving traffic:

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

async def warmup_vector_index(
    vector_client,
    collection_name: str,
    warmup_queries: list[list[float]],
    top_k: int = 5
) -> None:
    """
    Warm up vector DB index by executing dummy queries
    before the service starts accepting user traffic.
    """
    logger.info(f"Warming up vector index: {collection_name}")
    tasks = [
        vector_client.query(
            collection=collection_name,
            vector=query,
            limit=top_k
        )
        for query in warmup_queries
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    errors = sum(1 for r in results if isinstance(r, Exception))
    logger.info(
        f"Index warmup complete: {len(warmup_queries) - errors}/{len(warmup_queries)} successful"
    )

# Call in Kubernetes readiness probe after startup
async def readiness_check() -> bool:
    await warmup_vector_index(
        vector_client=vector_db,
        collection_name="knowledge_base",
        warmup_queries=WARMUP_QUERY_EMBEDDINGS,  # 50 representative queries
    )
    return True
```

---

## 8. Network Optimization

### 8.1 HTTP/2 and HTTP/3 for Streaming

| Protocol | Multiplexing | Header Compression | Connection Setup | SSE Support |
| --------- | ------------- | ------------------ | ----------------- | ------------- |
| HTTP/1.1 | No (one stream per connection) | None | 1 RTT (TLS: 2 RTT) | Yes (one stream) |
| HTTP/2 | Yes (multiple streams per connection) | HPACK | 1 RTT (TLS: 1 RTT with 0-RTT) | Yes (per-stream) |
| HTTP/3 (QUIC) | Yes (without head-of-line blocking) | QPACK | 0 RTT (0-RTT handshake) | Yes |

**Recommendation:** Enable HTTP/2 for all agentic API endpoints. HTTP/3 for global users with variable network conditions.

### 8.2 Compression for AG-UI Events

```python
# gzip/brotli compression middleware for AG-UI event stream
from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# Enable gzip compression for all responses except SSE
# (SSE should NOT be gzip-compressed — it disables streaming)
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses > 1KB
    compresslevel=6,    # Balance between CPU and compression ratio
)

@app.get("/stream/{session_id}")
async def stream_response(session_id: str):
    # SSE endpoint — DO NOT compress
    return StreamingResponse(
        generate_sse_events(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Content-Encoding": "identity",  # Explicitly no compression
        }
    )
```

---

## 9. Frontend Rendering Performance

### 9.1 React Streaming Best Practices

| Practice | Latency Improvement | Implementation |
| --------- | ------------------- | ---------------- |
| `startTransition` for token updates | Prevents blocking urgent updates | Wrap token appends in `startTransition` |
| `useDeferredValue` for heavy renders | Defers re-render until browser is idle | Apply to conversation history list |
| Virtualized conversation list | Eliminates off-screen render cost | `react-window` or `react-virtual` for > 50 messages |
| `React.memo` for message components | Prevents re-render of completed messages | Memoize each completed message by content hash |
| `Suspense` for tool result loading | Progressive disclosure without blocking | Wrap tool result components in Suspense |
| CSS containment | Limits browser layout scope per message | `contain: layout style` on message containers |

### 9.2 Virtualized Conversation List

```typescript
import { VariableSizeList } from 'react-window';
import { useRef, useCallback } from 'react';

function ConversationHistory({ messages }: { messages: Message[] }) {
  const listRef = useRef<VariableSizeList>(null);
  const sizeMap = useRef<Record<number, number>>({});

  const getItemSize = useCallback(
    (index: number) => sizeMap.current[index] ?? 80,
    []
  );

  const setItemSize = useCallback((index: number, size: number) => {
    if (sizeMap.current[index] !== size) {
      sizeMap.current[index] = size;
      listRef.current?.resetAfterIndex(index);
    }
  }, []);

  return (
    <VariableSizeList
      ref={listRef}
      height={600}
      itemCount={messages.length}
      itemSize={getItemSize}
      width="100%"
      overscanCount={5}  // Render 5 extra items outside viewport
    >
      {({ index, style }) => (
        <MessageItem
          message={messages[index]}
          style={style}
          onHeightChange={(h) => setItemSize(index, h)}
        />
      )}
    </VariableSizeList>
  );
}
```

### 9.3 Web Worker for Heavy Rendering

Offload markdown parsing, syntax highlighting, and math rendering to a Web Worker to avoid blocking the main thread during streaming:

```typescript
// worker.ts — runs in background thread
self.addEventListener('message', async (event) => {
  const { type, content, id } = event.data;

  if (type === 'parse_markdown') {
    const parsed = await parseMarkdown(content);
    const highlighted = await applySyntaxHighlighting(parsed);
    self.postMessage({ type: 'parsed', id, html: highlighted });
  }
});

// main thread
const renderWorker = new Worker(new URL('./worker.ts', import.meta.url));

function renderMessage(content: string, id: string): Promise<string> {
  return new Promise((resolve) => {
    const handler = (e: MessageEvent) => {
      if (e.data.id === id) {
        renderWorker.removeEventListener('message', handler);
        resolve(e.data.html);
      }
    };
    renderWorker.addEventListener('message', handler);
    renderWorker.postMessage({ type: 'parse_markdown', content, id });
  });
}
```

---

**This is Part 2 of 3. [Continue with Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/15-performance-engineering-part3) for LLM inference optimization, profiling methodology, performance testing, benchmarks, and anti-patterns.**
