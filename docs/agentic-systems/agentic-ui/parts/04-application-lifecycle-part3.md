---
title: "Agentic Application Lifecycle — Part 3"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: application-lifecycle-part3
covers_version: "as of 2026-07-10"
supersedes: []
---

# Stages 12–17: Deployment through Retirement

This is Part 3 of 3. **[Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/04-application-lifecycle) · [Back to Part 2](pathname:///archon/agentic-systems/agentic-ui/parts/04-application-lifecycle-part2)**

## Stage 12 — Deployment

### Progressive Deployment Strategy

Shadow Mode (0%): Log only, no user impact. Canary (1–5%): Monitor closely, compare vs. baseline. Early Adopters (10%): Full UX, approved users only. General Availability (50%): Half traffic. Full Rollout (100%).

### Feature Flag Configuration for Agentic Features

| Flag Name | Type | Default | Controls |
| --- | --- | --- | --- |
| `agent_enabled` | Boolean | false | Enables agent for user segment |
| `streaming_enabled` | Boolean | true | Enables streaming vs. batch response |
| `tool_use_enabled` | Boolean | false | Enables tool calling (risky — gate separately) |
| `hitl_required` | Boolean | true | Forces HITL for all tool calls |
| `autonomous_mode` | Boolean | false | Enables HOOL mode for mature users |
| `multi_agent_enabled` | Boolean | false | Enables multi-agent topology |
| `max_tokens_per_session` | Integer | 50000 | Session token budget |

### Deployment Runbook Template

Pre-deployment: all smoke tests passing, golden dataset eval ≥ baseline, security scan complete, rollback plan tested, on-call confirmed, stakeholder notification sent.

Deployment steps: enable shadow mode (flag), validate logs, canary deploy to 5% traffic (wait 30 min), validate metrics, expand to 10% (wait 2 hours), expand to 50% (wait 24 hours), full rollout.

Rollback triggers: error rate > 2%, P95 latency > 10s for 5 min, task completion drop > 10%, any security incident.

---

## Stage 13 — Operations & Monitoring

### SLO Baseline for Agentic Applications

| SLO | Target | Alerting Threshold |
| --- | --- | --- |
| Availability (agent endpoint) | 99.5% | &lt; 99.0% triggers alert |
| P50 time to first token | &lt; 800ms | &gt; 1.5s for 10 min |
| P95 time to first token | &lt; 3s | &gt; 5s for 5 min |
| Task completion rate | ≥ target % | Drop &gt; 10% vs. 7-day baseline |
| Approval queue age (P95) | &lt; 10 min | Any approval &gt; 30 min |
| LLM API error rate | &lt; 0.5% | &gt; 1% for 5 min |
| Context window utilization | &lt; 80% | &gt; 90% P95 |
| Monthly cost | Within budget | &gt; 110% of monthly budget |

### Incident Response for Agentic Failures

- **P0 — Agent returns harmful content:** Immediate disable; security team; post-mortem
- **P0 — Agent takes unauthorized action:** Immediate disable; audit all recent sessions
- **P1 — LLM provider outage:** Failover to backup model; notify users
- **P1 — Mass approval queue stuck:** On-call engineer; unblock or cancel tasks
- **P2 — Context overflow detected:** Deploy fix; monitor
- **P2 — Tool returning wrong data:** Disable tool; fallback; investigate
- **P2 — Eval score regression > 10%:** Rollback prompt; do not promote
- **P3 — Cost spike > 2× normal:** Investigate; apply token limits; alert finance

---

## Stage 14 — Continuous Improvement

### Feedback Loop Architecture

User interaction generates structured logs → OTel collector → observability platform. Users provide explicit feedback (thumbs up/down, corrections) → feedback store → annotation queue → human labelers → eval dataset update. Session traces → eval harness run → score vs. baseline.

If pass: promote prompt to production. If fail: investigate, prompt iteration.

### A/B Testing for Prompt Improvements

1. **Hypothesis:** "Changing X will improve Y by Z%"
2. **Design:** Prompt A (control) vs. Prompt B (variant)
3. **Traffic split:** 50/50 random per session
4. **Sample size:** n = (8 × σ²) / δ² for desired effect size
5. **Duration:** Minimum 7 days to account for weekly patterns
6. **Analysis:** Student's t-test or Mann-Whitney U
7. **Decision:** Promote if p &lt; 0.05 AND effect size ≥ minimum practical significance

---

## Stage 15 — Versioning

### Version Strategy Summary

| Component | Scheme | Breaking Change Definition |
| --- | --- | --- |
| System prompt | Semantic (MAJOR.MINOR.PATCH) | MAJOR: output format or behavior change |
| Tool API | Semantic + URI version | Any parameter rename or removal |
| Agent spec | Date-stamped (YYYY-MM-DD) | Change in scope, persona, or tool set |
| Memory schema | Semantic | Any schema incompatibility |
| A2UI components | Semantic | Any component prop rename or removal |

### Backward Compatibility Commitments

- Tool API stability: 12 months after GA
- Agent behavior stability: 6 months after GA
- Output format stability: 12 months after GA
- Deprecation notice: Minimum 90 days for all breaking changes

---

## Stage 16 — Migration

### Migration Patterns

| Pattern | When to Use | Risk |
| --- | --- | --- |
| **Strangler Fig** | Gradual migration; parallel run with legacy | Low — rollback always possible |
| **Parallel Run** | High-stakes; compare old vs. new outputs | Medium — double cost during migration |
| **Big Bang** | Simple, low-traffic, full test coverage | High — no rollback window |
| **Canary Migration** | Migrate one user segment at a time | Low–Medium |

### Migration Plan Template

Document: scope (total users, data stores, features added/replaced), migration waves (users per wave, start dates, rollback windows), rollback plan (trigger, action, RTO), communication plan (30/7/0/14 days messaging).

---

## Stage 17 — Sunsetting & Retirement

### End-of-Life Criteria

| Trigger | Threshold | Action |
| --- | --- | --- |
| Active users | &lt; 5% of peak MAU for 3 months | Begin retirement |
| Replacement available | New system in GA | Communicate migration |
| Business process retired | N/A | Immediate retirement eligible |
| Technology end-of-life | LLM / platform EOL announced | Accelerated retirement |
| Security risk | Critical unmitigatable vulnerability | Emergency retirement |

### Retirement Timeline

- T-60: Announce EOL, publish migration guide
- T-45: Disable new user onboarding
- T-30: Send reminder to all users
- T-14: Second reminder, begin read-only mode
- T-7: Final reminder, data export tools available
- T-0: Service disabled, landing page redirects
- T+30: Data retention period begins
- T+[N]: Data deletion per retention schedule
- T+[N]+30: Compliance archive sealed, audit trail preserved

### Compliance Evidence Archival

- Agent audit logs: 7 years (SOX) / 5 years (GDPR) → Immutable JSON
- Approval records: 7 years → CSV + PDF
- Prompt versions: Litigation hold duration → Plain text
- Security assessments: 3 years post-retirement → PDF
- Incident reports: 5 years → PDF

---

## Lifecycle Decision Matrix

At each stage gate, this matrix guides the go / no-go / return decision.

| From Stage | Gate Fails Because | Decision | Return To |
| --- | --- | --- | --- |
| Ideation | AI score &lt; 8 | No-go | — |
| Discovery | Data unavailable | Return | Ideation (reframe problem) |
| Business Case | NPV negative | No-go or Return | Discovery (reduce scope) |
| Architecture | ARB rejects | Return | Architecture (revise) |
| UX Design | Usability &lt; 80% | Return | UX Design (iterate) |
| Context Engineering | RAG quality &lt; target | Return | Context Engineering |
| Security Review | Critical findings | Return | Architecture + Development |
| Testing | Eval regression | Return | Development + Prompt iteration |
| Deployment | Canary metrics fail | Rollback | Development |
| Operations | SLO breach sustained | Escalate | Development (hotfix) |

---

## Architecture Decision Record Template (Agentic Application)

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-[N]  
**Date:** YYYY-MM-DD  
**Deciders:** [Names and roles]  
**Review date:** YYYY-MM-DD

### Context and Problem Statement

2–4 sentences describing the situation requiring a decision. Include application stage, component being decided, and why it matters.

### Decision Drivers

1. Most important criterion (e.g., "Data residency: all processing in EU")
2. Second criterion
3. Third criterion (e.g., "Must integrate with existing Entra ID")

### Considered Options

| Option | Description | Pros | Cons |
| --- | --- | --- | --- |
| A | Brief description | Key advantages | Key disadvantages |
| B | Brief description | Key advantages | Key disadvantages |
| C | Brief description | Key advantages | Key disadvantages |

### Decision

**Chosen option: [Option X]**

Justification: 2–3 sentences referencing decision drivers.

### Consequences

**Positive:** What becomes easier

**Negative:** What becomes harder / risks accepted

**Neutral:** What changes without net impact

### Compliance Notes

Regulatory, governance, or security implications of this decision.

### Exit Strategy

How to migrate away from this choice if it fails — cost estimate and path.

### Related ADRs

ADR-[N]: Related decision and how it interacts.

---

**Storage Convention:** Store ADRs in `docs/architecture/decisions/ADR-NNNN-title.md`. Number sequentially. Never delete a superseded ADR — update its status and keep it for historical reference.

---

**This is Part 3 of 3. [Back to Part 1](pathname:///archon/agentic-systems/agentic-ui/04-application-lifecycle) · [Back to Part 2](pathname:///archon/agentic-systems/agentic-ui/parts/04-application-lifecycle-part2)**
