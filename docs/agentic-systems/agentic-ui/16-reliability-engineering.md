---
title: "Reliability Engineering for Agentic Applications"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: reliability-engineering
covers_version: "as of 2026-07-10"
supersedes:
  - docs/agentic-ui/reliability-engineering.md
---

# Reliability Engineering for Agentic Applications

A comprehensive engineering reference for Enterprise Architects and AI Platform Teams designing production-grade reliability for agentic UIs and agent runtimes — covering SLO frameworks, fault tolerance patterns, saga orchestration, streaming recovery, and chaos engineering.

:::note Related Guides
    - Observability instrumentation (OTel GenAI spans): Agentic AI Reliability & Observability
    - HITL gates and escalation: Enterprise AI Architecture Patterns
    - AI Gateway circuit breaker: Kong AI Gateway Guide

---

## 1. Why Agentic Reliability Is Fundamentally Different

Traditional web application reliability operates on independent, stateless HTTP request-response pairs. Agentic applications break all these assumptions: inputs produce different outputs each call (non-determinism); conversations maintain state across turns; tasks run seconds to minutes (long exposure window); dependency graphs have 5–15 hops (compound failure); LLM returns 200 OK with wrong answers (semantic failures invisible to infrastructure).

### 1.1 The Five Dimensions of Agentic Unreliability

| Dimension | Traditional App | Agentic App | Impact |
| --- | --- | --- | --- |
| **Determinism** | Same input → same output | Same input → different output | Cannot rely on retry |
| **State** | Stateless per-request | Stateful conversation, multi-turn | Failure mid-conversation corrupts state |
| **Duration** | Milliseconds to seconds | Seconds to minutes per task | More exposure window |
| **Dependency graph** | 2–3 hops | 5–15 hops | Compound failure |
| **Failure semantics** | Error codes definitive | 200 OK with wrong answer | Invisible to monitors |

### 1.2 The Compound Failure Probability Problem

With eight dependencies each at 99.9%, system availability drops to 99.2% — two hours downtime/month. Agentic applications chain 8–15 components. At 99.9% per component, a 12-hop chain has 98.8% theoretical availability.

### 1.3 Four Failure Classes Requiring Different Machinery

| Failure Class | Trigger | Correct Response | Dangerous Response |
| --- | --- | --- | --- |
| **Transport** | Network timeout, HTTP 429, DNS failure | Retry with backoff + jitter | Blind retry (thundering herd) |
| **Semantic** | Bad reasoning, hallucinated tool args | Re-plan with different strategy | Retry (same wrong output) |
| **Systemic** | Provider outage, quota exhaustion | Failover to alternate provider | Retry hoping outage resolves |
| **Safety/Policy** | Guardrail trip, policy violation | Halt; escalate to HITL | **Never retry-around** |

**Critical:** Retrying around guardrail trip converts contained event to incident. Safety blocks must halt and escalate, never retry.

### 1.4 Observability Is Prerequisite

Cannot build error budgets or tune SLOs without visibility. Confirm OpenTelemetry GenAI semantic conventions instrumented across every component before implementing patterns.

---

## 2. SLA/SLO/SLI Definitions for Agentic Applications

### 2.1 Terminology

| Term | Definition | Agentic Note |
| --- | --- | --- |
| **SLI** | Measurable signal | Must include semantic quality, not just transport |
| **SLO** | Target threshold | Set by product × reliability jointly |
| **SLA** | Contractual commitment | Typically SLO minus 10–20% safety margin |
| **Error Budget** | SLO headroom | 100% − SLO; budget for experimentation |
| **Burn Rate** | Consumption speed | 2× burn = fast alert; 5× = slow alert |

### 2.2 Availability SLOs by Workload Class

| Workload Class | Recommended SLO | Rationale |
| --- | --- | --- |
| Interactive chat (best-effort) | 99.5% | Latency tolerance high |
| Interactive chat (business-critical) | 99.9% | Revenue-impacting |
| Autonomous workflows (batch) | 99.5% | Async; workflow-level retry OK |
| Autonomous workflows (real-time) | 99.9% | Blocks downstream |
| HITL-assisted | 99.95% | Human waiting; time-sensitive |
| Embedded in SaaS | 99.95% | Customer-facing; affects NPS |
| Regulated financial/healthcare | 99.99% | Regulatory and contractual |

### 2.3 Latency SLIs

| SLI Name | Measurement Point | P50 | P95 | Alert |
| --- | --- | --- | --- | --- |
| **TTFT** | First SSE event | 600ms | 1,200ms | > 2s for 5m |
| **Streaming Lag** | Token generation to render | &lt; 50ms | &lt; 150ms | > 500ms for 2m |
| **Tool Completion** | Tool call start → result | 300ms | 1,500ms | Tool-specific |
| **End-to-End Task** | User submit → complete | 3s | 15s | > 30s for 5m |
| **Context Assembly** | Build → ready | 100ms | 400ms | > 600ms for 5m |
| **Memory Retrieval** | Query → ranked | 80ms | 250ms | > 500ms for 5m |
| **Guardrail Latency** | Input → decision | 50ms | 200ms | > 400ms for 5m |
| **Planning Latency** | Request → plan | 800ms | 2,500ms | > 4s for 5m |

### 2.4 Quality SLIs

| Quality SLI | Definition | Target |
| --- | --- | --- |
| **Task Completion** | % reaching successful state | ≥ 92% |
| **Tool Success** | % returning valid results | ≥ 97% |
| **Hallucination Rate** | % factually incorrect | &lt; 3% |
| **Context Faithfulness** | % grounded in context | ≥ 90% |
| **Plan Success Rate** | % without replanning | ≥ 85% |
| **HITL Escalation** | % escalated | 2–8% baseline |
| **User Satisfaction** | CSAT score | ≥ 4.0/5.0 |

### 2.5 Error Budget Calculation

For 99.9% SLO over 30 days: error budget = 43.2 minutes. Track consumed vs. remaining. Alert at 50%, 75%, 100% consumed.

### 2.6 Burn Rate Alert Configuration

- **Fast Burn Critical:** > 14.4× (2% in 1hr) → P1, immediate page
- **Fast Burn Warning:** > 6× (5% in 6hr) → P2, notify lead
- **Slow Burn Warning:** > 3× (10% in 3d) → P3, standup
- **Budget at 50–75%:** P3, freeze non-essential
- **Budget at 75%:** P2, halt features
- **Exhausted:** P1, feature freeze

---

## 3. Fault Tolerance Patterns

### 3.1 Circuit Breaker for LLM Providers

Prevents cascade when LLM provider degraded. States: CLOSED (normal), OPEN (fast-fail), HALF_OPEN (testing).

Configuration: failure_threshold (5 → OPEN), success_threshold (3 in HALF_OPEN → CLOSED), timeout (30s OPEN → HALF_OPEN), probe_limit (5% traffic), fallback provider.

### 3.2 Bulkhead Pattern

Isolates LLM calls, tool calls, UI rendering into separate pools. Stuck tool cannot block LLM streaming.

- LLM Pool: max 20, queue 100, timeout 60s
- Tool Pool: max 50, queue 200, timeout 30s
- UI Pool: max 100, queue unlimited, timeout 5s

### 3.3 Timeout Hierarchy

Timeouts must nest: inner shorter than outer.

| Timeout | Default | Scope | On Expiry |
| --- | --- | --- | --- |
| UI Response | 120s | Connection alive | Heartbeat |
| Agent Task | 300s | Complete task | Mark TIMEOUT |
| LLM Call | 60s | HTTP request | Circuit breaker |
| Tool Call | 15–30s | Individual tool | `timeout_error` |
| Memory | 3s | Vector DB | Exact-match |
| Guardrail | 2s | Check | Fail open |
| Planning | 30s | Planner | Partial plan |

**Danger:** Equal inner/outer timeouts expire simultaneously, making failure source unclear.

---

## 4. Graceful Degradation Ladder

Degradation ladder defines behavior at each impairment level. Goal: always return some value rather than error.

| Level | Name | Conditions | Capabilities | UX |
| --- | --- | --- | --- | --- |
| **L1** | Full Agentic | All nominal | All tools, memory, planning | Full interactive |
| **L2** | Reduced Tools | 1–2 non-critical unavailable | Core tools only | "Cannot do X" |
| **L3** | Read-Only | Write unavailable | Read-only tools | "Read-only mode" |
| **L4** | Static/Cached | LLM degraded | Cached responses; FAQ | Non-streaming; "cached" |
| **L5** | Human Handoff | All AI unavailable | Zero capability | "Connecting to human" |

### 4.1 Degradation Decision Criteria

Flowchart: LLM open? → fallback? → L2 or L4. Tools > 50% unavailable? → L3. Memory unavailable? → L2 degraded. Guardrail unavailable? → L5 if required. All clear? → L1.

### 4.2 Automatic Recovery

Poll at 15s, 30s, 60s, 120s, 5min intervals. On recovery, promote one level (not to L1). Soak 2+ minutes before further promotion. Log all transitions.

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/16-reliability-engineering-part2) for Retry, Checkpoint, and Saga patterns.**
