---
title: Scalability Engineering for Agentic Applications (Part 3)
domain: agentic-systems
status: current
doc_type: guide
topic_id: scalability-engineering-part3
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

# Scalability Engineering for Agentic Applications (Part 3)

**[Back to Part 2 ←](pathname:///archon/agentic-systems/agentic-ui/parts/18-scalability-engineering-part2)**

---

## 19. Putting It All Together: Implementation Roadmap

Scalability engineering for agentic applications is not a single technology choice but a systematic approach across six critical layers. This section provides a practical roadmap for implementing the patterns and technologies covered in Parts 1 and 2.

### 19.1 The Scalability Implementation Sequence

**Phase 1: Foundation (Weeks 1–4)**

Start with core stateless patterns before scaling to avoid rewriting architecture:

1. **Externalize session state to Redis** — This single decision enables all downstream scaling patterns. Implement the ExternalizedSessionStore pattern from Part 1 Section 2.
2. **Set up task queuing** — Deploy a simple priority queue (SQS or Kafka) to decouple producer from consumer. This isolates load spikes and enables per-queue autoscaling.
3. **Implement connection pooling** — Configure pools for LLM provider, tool APIs, and databases using the specifications in Part 2 Section 14. Connection reuse reduces TLS overhead by 80–90%.
4. **Add basic monitoring** — Instrument queue depth, active sessions, and LLM TPM consumption. Without these signals, autoscaling decisions are blind.

**Phase 2: Scaling Boundaries (Weeks 5–12)**

Once foundation is solid, add rate limiting and concurrency controls:

1. **Deploy token bucket rate limiting** — Implement per-user and per-tenant limits using the TokenBucket pattern from Part 2 Section 9. This prevents any single user from starving others.
2. **Establish concurrency limits** — Apply semaphore patterns at tool, user, and global levels per Part 2 Section 11. Start conservative (per-user = 3, per-tool = 5) and relax based on load test data.
3. **Add semantic caching** — Begin with conservative settings (0.97 threshold, 1-hour TTL, 10K entries) from Part 2 Section 5. Semantic caching deflects 15–25% of requests at low operational cost.
4. **Implement backpressure signaling** — Add flow control in streaming pipelines per Part 2 Section 9. Backpressure prevents buffer overflows and cascading failures.

**Phase 3: Autoscaling (Weeks 13–20)**

With monitoring and boundaries in place, autoscaling becomes safe:

1. **Implement KEDA autoscaling** — Configure ScaledObjects for agent workers (queue depth + session count triggers), LLM proxy (TPM), and tool executors per Part 2 Section 10. Use the recommended trigger thresholds.
2. **Enable scale-to-zero for batch jobs** — Only after observing cold start latency in load tests. Keep min replicas ≥2 for interactive workloads to maintain SLA.
3. **Add pre-warmed pool for interactive** — If cold start exceeds 2 seconds, maintain a small pool of always-on workers rather than scaling to zero.
4. **Run continuous soak tests** — Deploy the benchmark scenarios from Part 2 Section 16 (ramp, soak, spike, quality-under-load). Verify no quality degradation under peak load.

**Phase 4: Multi-Region and Advanced (Weeks 21–32)**

Only deploy multi-region and GPU scheduling after single-region proves stable:

1. **Deploy active-active multi-region** — Start with active-passive (primary + cold standby) per Part 2 Section 12 to manage complexity. Upgrade to active-active only if serving global low-latency SLA.
2. **Implement GPU scheduling** — If self-hosting LLMs, configure continuous batching and multi-model scheduling per Part 2 Section 13. This multiplies GPU throughput by 2–3×.
3. **Establish data sovereignty guardrails** — Apply geo-fencing at the global load balancer level for GDPR/HIPAA/SOC2 compliance per Part 2 Section 12.2.
4. **Optimize cost model** — Using capacity planning formulas from Part 2 Section 15, evaluate trade-offs: semantic cache vs. API spend, self-hosted vs. provider, scale-to-zero vs. always-on.

### 19.2 Scaling Decision Tree

Use this decision tree when facing specific scalability bottlenecks:

**Bottleneck: LLM token throughput (P99 latency > 5s)**

- **Check:** Is queue depth > 50% of target?
  - Yes → Configure KEDA autoscaling on TPM metric; add more LLM proxy instances.
  - No → Check LLM provider rate limits (API dashboard). If approaching limit: (a) add multi-provider routing, (b) add semantic cache to deflect repeats, (c) implement prompt caching for large docs.

**Bottleneck: Tool API rate limits are breached**

- **Check:** Are tool calls exceeding fan-out limits?
  - Yes → Apply semaphore limits per Part 2 Section 11. Start with max_concurrent=5 per tool, increase gradually.
  - No → Check if tool calls are retry-storming (retries for transient failures). Implement exponential backoff and circuit breakers per reliability-engineering topic.

**Bottleneck: Session affinity pressure (load balancer sticky session overhead)**

- **Check:** Are sessions long-running (> 5 min)?
  - Yes → Accept sticky session cost; prioritize session draining for low-downtime deployments per Part 1 Section 3.3.
  - No → Externalize all state to Redis and remove sticky sessions. Reduces load balancer complexity and enables true round-robin.

**Bottleneck: Memory usage per agent worker (> 500MB per session)**

- **Check:** Is memory growing with session age?
  - Yes → Implement periodic state snapshots and cleanup per Part 1 Section 2.2 (event sourcing with snapshots).
  - No → Add memory profiling to identify leaks. If acceptable, scale worker pool instead (easier than per-session memory optimization).

**Bottleneck: Vector DB query latency**

- **Check:** Is query latency > 50ms at p95?
  - Yes → Implement context fragment caching per Part 1 Section 5.4. Cache hit rate reduces round-trips by 40–60%.
  - No → Profile vector DB load. If CPU saturated, shard collections across DB instances.

### 19.3 Common Pitfalls and How to Avoid Them

Part 2 Section 17 catalogued 24 anti-patterns. Here are the three most costly:

**Anti-Pattern #1: Synchronous Tool Fan-Out**

Tools are called sequentially instead of in parallel. This multiplies latency by the number of tools (e.g., 5 tools × 500ms each = 2.5s vs. 500ms parallel).

*Prevention:* Use the ToolExecutor.execute_parallel() pattern from Part 1 Section 4.3 by default. Measure and profile before optimizing further.

**Anti-Pattern #5: No Semantic Cache**

Every query hits the LLM even for repeat questions. At 10K users with 20% repeat rate, this wastes 30% of LLM spend.

*Prevention:* Enable semantic caching by week 5 of Phase 2, starting with conservative settings (Part 2 Section 5.1). Measure hit rate and adjust threshold based on domain.

**Anti-Pattern #21: No Data Sovereignty in Routing**

A GDPR-compliant EU user's data is routed to US region on failover, causing compliance violations and regulatory risk.

*Prevention:* Hard-code geo-fencing rules in the global load balancer before multi-region deployment (Part 2 Section 12.2). Test failover paths for compliance.

### 19.4 Capacity Planning Quick Reference

Before scaling to production load, use these formulas to size your infrastructure:

**Peak concurrent sessions:** `peak_daily_users × session_overlap_factor`  
*Example:* 10,000 DAU × 0.05 overlap = 500 concurrent sessions

**LLM proxy instances:** `ceil(peak_TPM / TPM_per_proxy_instance)`  
*Example:* ceil(700K TPM / 200K TPM) = 4 instances

**Agent worker instances:** `ceil(peak_sessions / sessions_per_worker)`  
*Example:* ceil(500 sessions / 10 sessions) = 50 workers

**Redis memory:** `peak_sessions × avg_session_size_KB`  
*Example:* 500 sessions × 50 KB = 25 MB (fits in a single small instance)

**Benchmark before committing:** Run the soak test (Part 2 Section 16.1) at 80% of your expected peak load for 4 hours. If any metric exceeds SLA thresholds, scale components until test passes.

### 19.5 Metrics and Alerting

Scalability is invisible until something breaks. Monitor these key metrics:

| Metric | Target SLO | Alert Threshold | Action |
| ------- | ----------- | -------- | --------- |
| Queue depth (per priority level) | < 3 | > 50 | Scale workers |
| LLM TPM utilization | < 80% | > 90% | Enable caching; add provider |
| Concurrent sessions per worker | < 20 | > 25 | Scale workers |
| Token bucket refill lag (user-facing) | < 100ms | > 500ms | Increase bucket capacity |
| P95 session load latency (Redis) | < 10ms | > 20ms | Add Redis cluster shard |
| Tool API error rate (transient) | < 1% | > 3% | Check downstream API health |
| Autoscaler response time (scale-out) | < 1 min | > 2 min | Investigate KEDA triggers |
| Memory per worker instance | < 1GB | > 1.5GB | Profile for leaks; increase sessions_per_worker |

### 19.6 Testing Your Scalability

Before production, verify scalability assumptions with these tests:

1. **Load test to 2× peak:** Use k6 or Locust to generate concurrent user sessions. Measure P99 latency and error rate. Should stay within SLA.
2. **Chaos + load test:** Inject tool failures (random 500 errors) at 75% peak load. System should degrade gracefully (reduced throughput, not cascading failure).
3. **Cold start timing:** Scale workers to zero, then trigger a spike. Measure time from spike start to first successful response. If > SLA, configure warm pool.
4. **Quality-under-load:** Run LLM judge on sampled task outputs at peak load vs. baseline. Quality should not degrade > 5%.

Run these tests in a staging environment identical to production (same region, cluster size, data volumes). Production scalability issues almost always traced back to skipped or inadequate staging tests.

---

## Conclusion

Scalability for agentic applications requires coordinated decisions across six layers: frontend backpressure signaling, edge SSE termination, agent orchestration with externalized state, LLM routing and caching, tool execution with concurrency limits, and infrastructure autoscaling. No single technology solves scalability; rather, the framework depends on:

- **Stateless architecture** to enable horizontal scaling
- **Queue-based async** to decouple producer from consumer
- **Concurrency and rate limiting** to prevent runaway load
- **Semantic caching** to deflect requests before they reach bottlenecks
- **Autoscaling rules** that trigger on business metrics (queue depth, active sessions, token throughput), not infrastructure metrics (CPU, memory)
- **Benchmarking methodology** that measures quality degradation under load, not just latency

The scalability decision matrix in Part 2 Section 18 provides criteria for choosing between alternatives (stateless vs. stateful, single provider vs. multi-provider, managed vs. self-hosted). Start with the simplest option that meets your SLA, then optimize based on observed bottlenecks, not premature assumptions.

**Related Documentation:**
- [Reliability Engineering](../16-reliability-engineering.md) — Circuit breakers and graceful degradation under load
- [Agent Memory Planning Architecture](../../../architecture/41-agent-memory-planning-architecture.md) — Scaling session state and conversation history
- [Kong AI Gateway Guide](../../../platforms/08-kong-ai-gateway-guide.md) — Rate limiting and load balancing at the gateway layer
