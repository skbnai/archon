---
title: "Agent Reliability Engineering (ARE)"
doc_type: reference-architecture
domain: architecture
status: current
canonical: true
topic_id: agent-reliability-engineering
maturity: expert
personas: [sre, platform-engineer, architect, engineering-lead]
last_reviewed: 2026-07-19
covers_version: "as of July 2026"
supersedes:
  - docs/enterprise-architecture/ai-architecture/agent-reliability-engineering.md
tags:
  - reliability
  - sre
  - agents
  - slo
  - error-budgets
  - observability
sources: []
---

# Agent Reliability Engineering (ARE)

**Audience:** SREs, Platform Engineers, AI Architects, and Engineering Leads responsible for operating AI agent systems in production.

**Purpose:** ARE applies Site Reliability Engineering (SRE) principles — SLOs, error budgets, toil, PRR, chaos engineering, on-call discipline — to the specific failure modes, operational characteristics, and governance requirements of AI agent systems.

**Scope:** ARE is a discipline, not a tool. This guide covers the practices, metrics, processes, and team model. For agent reliability patterns (retry, circuit breakers, graceful degradation, checkpointing), see the companion guide → [Agentic AI Reliability, Observability & Governance](43-agentic-ai-reliability-observability-governance.md).

**Related:** [AIOps Guide](pathname:///archon/engineering/aiops-guide) | [Agentic AI Security & Guardrails](pathname:///archon/architecture/agentic-ai-security-guardrails) | [Enterprise AI Architecture Patterns](49-enterprise-ai-architecture-patterns.md)

---

## 1. What is Agent Reliability Engineering?

### 1.1 SRE Applied to AI Agent Systems

Traditional SRE was designed for deterministic software systems: the same input produces the same output; failures are binary (up or down); root cause is traceable through code.

AI agent systems break every SRE assumption:

- Non-deterministic: the same input may produce different outputs across runs
- Multi-dimensional failure: agents can be "up" (responding) while producing wrong or harmful outputs
- Emergent failure: agent behaviour in production differs from evaluation (the 37% lab-to-production gap)
- Self-amplifying failure: one bad agent decision can trigger cascading bad decisions in downstream agents

ARE extends SRE to handle these characteristics.

### 1.2 ARE vs SRE vs AIOps

| Discipline | Focus | Primary Output |
| --- | --- | --- |
| **SRE** | Infrastructure and service reliability (availability, latency) | Runbooks, SLOs, incident response for traditional software |
| **ARE** | AI agent reliability (task completion, quality, safety) | Agent SLOs, production readiness standards, agent failure response |
| **AIOps** | AI applied to IT operations (noise reduction, RCA automation) | AI-augmented operations for any IT system |

ARE teams own: agent SLO design, production readiness reviews, agent chaos testing, on-call for agent production issues, agent toil measurement, and feedback loops from production back to model/product teams.

### 1.3 The ARE Promise

When ARE is applied:

- Agent failures are detected and classified within 60 seconds
- Critical safety failures (guardrail trips) are never retried
- Quality regressions are caught by evaluation harness before they reach production
- On-call load from agent systems is &lt; 3 pages/week per engineer
- Every production agent incident has a postmortem within 24 hours

---

## 2. Agent SLOs — Measuring What Matters

### 2.1 Why Infrastructure SLOs Are Insufficient for Agents

A traditional SLO measures: "Is the service responding within acceptable latency?" This misses the key agent failure modes:

| SLO Question | Traditional SRE | ARE Extension Needed |
| --- | --- | --- |
| Is it up? | Uptime / availability | Task completion rate |
| Is it fast? | Latency P99 | Time to task completion (not TTFT) |
| Is it correct? | Not measured | Quality score; faithfulness; format compliance |
| Is it safe? | Not relevant | Guardrail trip rate; harmful output rate |
| Is it cost-efficient? | Not measured | Cost per successful task |
| Is it improving? | Not measured | Model update regression rate |

### 2.2 Agent SLO Dimensions

Define SLOs across five dimensions:

**Dimension 1: Task Completion Rate (TCR)**

```
TCR = (Tasks completed successfully) / (Tasks attempted) × 100

Success = agent produced an output meeting all of:
  - Completed within deadline
  - Met format requirements
  - Passed quality threshold
  - Did not trip a safety guardrail

Target: 97–99.5% depending on task criticality
Alert threshold: burn rate > 3× over 1-hour window
```

**Dimension 2: Semantic Quality Rate (SQR)**

```
SQR = (Tasks rated acceptable by judge) / (Tasks evaluated) × 100

Measured by: LLM-as-judge on sampled production outputs
Sampling rate: 5–10% of production; 100% of flagged outputs
Target: > 90% for production agents
Alert threshold: SQR drops > 10% vs. 7-day baseline
```

**Dimension 3: Safety Compliance Rate (SCR)**

```
SCR = 1 - (Guardrail trips / Tasks attempted)

Target: > 99.9% (< 1 guardrail trip per 1,000 tasks)
Alert threshold: Any increase in guardrail trip rate
Note: A guardrail trip is not a system failure — the guardrail worked.
      What matters is the false-positive rate (valid tasks tripped).
```

**Dimension 4: Latency SLO**

```
For interactive agents:
  P50 time-to-complete: < 10 seconds
  P95 time-to-complete: < 30 seconds
  P99 time-to-complete: < 120 seconds

For batch agents:
  Mean completion: per-task baseline + 20% tolerance
  Note: extended thinking tasks have very different latency profiles
```

**Dimension 5: Cost per Task (CPT)**

```
CPT = Total inference cost / Tasks completed

Target: Defined per use case; alert on > 30% drift from baseline
Driver: Model version updates, context bloat, retry volume

CPT spike is often a leading indicator of quality problems
(agents retry more when model performance degrades)
```

### 2.3 Error Budgets for Agent Systems

Error budget = allowable failure from the SLO:

```
EXAMPLE: Research Agent
  TCR SLO: 98%
  Error budget: 2% of tasks
  Monthly task volume: 50,000
  Monthly budget: 1,000 task failures

If October used:
  500 failures = 50% budget consumed → continue without restriction
  900 failures = 90% → freeze new features; fix reliability first
  1,000 failures = 100% → all new development stops; reliability sprint required
```

The error budget policy creates the right incentive structure:

- Product teams move fast only while reliability is good
- When reliability degrades, the error budget stops feature development until fixed

### 2.4 Agent SLO Example Registry

```yaml
# Agent SLO Registry Entry
agent:
  id: "research-agent-v2"
  type: "batch-research"
  owner: "platform-team"
  criticality: "high"

slos:
  task_completion_rate:
    target: 0.98
    window: "30d"
    evaluation: "automated"

  semantic_quality_rate:
    target: 0.91
    window: "7d"
    evaluation: "llm-as-judge"
    judge_model: "claude-sonnet-5"
    sample_rate: 0.08

  safety_compliance:
    target: 0.999
    window: "30d"
    evaluation: "guardrail-logs"
    false_positive_budget: 0.005

  latency_p95:
    target_seconds: 180
    window: "1h"

  cost_per_task:
    baseline_usd: 0.042
    alert_drift_pct: 30
    window: "24h"

error_budget:
  monthly_task_volume: 50000
  tcr_budget_tasks: 1000
  policy:
    - threshold: 0.50  # 50% budget consumed
      action: "notify team"
    - threshold: 0.90  # 90% budget consumed
      action: "feature freeze; reliability sprint"
    - threshold: 1.00  # budget exhausted
      action: "halt new deployments; incident declared"
```

---

## 3. Toil in Agent Operations

### 3.1 Agent-Specific Toil

SRE defines toil as manual, repetitive, automatable work that grows with scale and produces no lasting value. Agent systems generate a distinctive toil profile:

| Toil Category | Example | Elimination Strategy |
| --- | --- | --- |
| **Manual output review** | Reviewing flagged agent outputs one-by-one | LLM-as-judge automation; sampling-based review |
| **Model version testing** | Manually testing each agent use case when model updates | Automated evaluation harness in CI/CD |
| **Context bloat management** | Manually trimming context when agents hit token limits | Automatic context compression; budget enforcer |
| **Guardrail tuning** | Manually adjusting guardrail thresholds after false positives | Feedback loop from production to guardrail calibration system |
| **Runbook updates** | Manually updating agent runbooks after model capability changes | AI-assisted runbook maintenance; version-controlled |
| **Agent retry investigation** | Manually diagnosing why specific tasks repeatedly fail | Automated semantic failure classifier; structured retry reports |
| **SLO report generation** | Manually pulling SLO metrics and writing weekly reports | Automated SLO dashboard + weekly digest agent |
| **Embedding index refresh** | Manually triggering re-indexing of knowledge base for RAG agents | Event-driven automatic re-indexing on knowledge source changes |

### 3.2 Toil Budget

ARE teams should target: **&lt; 50% of engineering time on toil**. If toil exceeds 50%, reliability work is being crowded out by maintenance.

Track toil by logging time spent on each toil category weekly. Use the data to prioritise automation investments.

---

## 4. Production Readiness Review (PRR) for AI Agents

### 4.1 Why Agents Need a PRR

AI agents can be technically deployed (Kubernetes pods running, APIs responding) while being operationally not ready:

- No SLOs defined
- No evaluation harness
- No guardrails configured
- No graceful degradation plan
- No on-call runbook
- No cost monitoring

The PRR gate ensures agents meet operational standards before reaching production users.

### 4.2 ARE Production Readiness Checklist

**SLO Readiness**

- [ ] Task Completion Rate SLO defined and baselined
- [ ] Semantic Quality Rate SLO defined with LLM-as-judge configured
- [ ] Safety Compliance Rate SLO defined with guardrail logging
- [ ] Latency SLO defined per interaction tier (interactive / batch)
- [ ] Cost per task baseline established
- [ ] Error budget policy documented and enforcement configured

**Evaluation Coverage**

- [ ] Golden evaluation dataset exists (minimum 100 representative examples)
- [ ] Evaluation harness runs in CI/CD on every model update
- [ ] Quality regression threshold configured (deploy blocked if quality drops > 5%)
- [ ] Adversarial test set exists (prompt injection, jailbreak, edge cases)
- [ ] Performance benchmark established at 2× expected production load

**Reliability Architecture**

- [ ] Retry policy configured: exponential backoff with jitter, 3-strike limit
- [ ] Circuit breaker configured for each provider and each tool
- [ ] Graceful degradation ladder defined (all 5 rungs)
- [ ] Fallback model evaluated and approved for each use case
- [ ] Timeout configured: per-step AND end-to-end task deadline
- [ ] Step-boundary checkpointing implemented for long-running tasks
- [ ] Rollback mechanism tested for model version changes

**Observability**

- [ ] OpenTelemetry GenAI spans emitted for all model calls
- [ ] Structured trace per task (task-level, not just call-level)
- [ ] Cost attribution tags on every model call
- [ ] SLO dashboards live in Grafana / Datadog
- [ ] SLO burn rate alerts configured in PagerDuty

**Safety and Governance**

- [ ] Guardrails configured and tested (input and output)
- [ ] HITL gates defined for all Level 3+ actions
- [ ] Audit trail writing to append-only store
- [ ] PII scrubbing verified in log pipeline
- [ ] Data classification validated (agent not accessing T0 data above its clearance)
- [ ] Security review completed (prompt injection tested)

**Operational Readiness**

- [ ] On-call runbook documented and reviewed by on-call team
- [ ] Incident classification guide for agent-specific failure types
- [ ] Cost budget and alerting configured
- [ ] On-call rotation designated (who is paged for agent incidents)
- [ ] Escalation path documented
- [ ] Postmortem process defined for agent incidents

**Business Readiness**

- [ ] User-facing error messages designed (not raw AI error traces)
- [ ] Graceful degradation experience designed (what users see at each rung)
- [ ] Feature flag configured (allows kill-switch without deployment)
- [ ] Business owner sign-off on SLO targets

### 4.3 PRR Process

```
AGENT FEATURE DEVELOPMENT COMPLETE
           │
           ▼
   STAGING VALIDATION (1–2 weeks)
   - Golden set evaluation
   - Load test at 2× expected volume
   - Adversarial test set
           │
           ▼
   PRR SUBMISSION
   - PRR checklist completed by dev team
   - Submitted to ARE team
           │
           ▼
   ARE REVIEW (3–5 business days)
   - Review each checklist item with evidence
   - Run spot checks on evaluation results
   - Review SLO design for achievability
           │
      ┌────┴────┐
     PASS      FAIL
      │         │
      ▼         ▼
   APPROVED  CONDITIONAL APPROVAL
   for prod  (specific gaps must be
              closed within 2 weeks)
```

---

## 5. Chaos Engineering for Agent Systems

### 5.1 Why Agents Need Chaos Testing

Traditional chaos testing (kill a pod, inject latency) doesn't cover agent-specific failure modes. ARE extends chaos engineering to test:

- **Model provider outages:** What happens when Anthropic API is down?
- **Model quality degradation:** What happens when the model consistently produces low-quality outputs?
- **Tool failures:** What happens when a specific tool returns errors?
- **Context overflow:** What happens when the context window fills up mid-task?
- **Guardrail false positives:** What happens when the guardrail trips on valid inputs?
- **Budget exhaustion:** What happens when the agent runs out of retry budget?
- **Safety failure:** Does the safety circuit breaker correctly halt and escalate?

### 5.2 Agent Chaos Experiments

**Experiment 1: Provider outage**

```
Fault injection: Return HTTP 503 from model provider (100% error rate)
Expected behaviour:
  - Circuit breaker opens after 3 failures
  - Agent routes to fallback model
  - Fallback model evaluated equivalent for this task class
  - No task silently lost; all in-flight tasks gracefully degraded or queued

Validation:
  - Task Completion Rate: > 85% (some degradation expected)
  - No unhandled exceptions in agent runtime logs
  - Circuit breaker state change logged and alerted
  - Fallback model outputs meet minimum quality threshold
```

**Experiment 2: Model quality degradation**

```
Fault injection: Replace model with a model known to produce poor outputs for this task
Expected behaviour:
  - LLM-as-judge quality scores drop
  - Quality SLO burn rate increases
  - Alert fires within 5 minutes
  - Agent auto-escalates to higher-capability model (if cascade configured)

Validation:
  - Quality alert fires within SLA
  - Escalation to human if quality remains below threshold for > 15 minutes
  - Audit log shows quality degradation event
```

**Experiment 3: Tool failure cascade**

```
Fault injection: Return random errors from web-search tool (50% error rate)
Expected behaviour:
  - Agent retries with backoff (≤3 retries per tool call)
  - After retry budget exhausted, agent uses alternative search tool
  - If no alternative, gracefully degrades to response without real-time data
  - Tool-level circuit breaker activates for web-search after threshold

Validation:
  - Task Completion Rate: > 80% (degraded but acceptable)
  - No infinite retry loops
  - Alternative tool activated within tool circuit breaker timeout
```

**Experiment 4: Context overflow**

```
Fault injection: Provide a task with documents that fill 95% of context window before task instructions
Expected behaviour:
  - Agent detects context budget pressure at planning stage
  - Agent either: compresses earlier context OR requests task decomposition
  - Agent does NOT silently drop system prompt instructions
  - Does NOT hallucinate about document content that was truncated

Validation:
  - No system prompt instructions lost in output
  - Context management action logged
  - Quality maintained above SLO threshold
```

**Experiment 5: Safety failure handling**

```
Fault injection: Submit input designed to trigger guardrail
Expected behaviour:
  - Guardrail trips correctly (True Positive)
  - Agent HALTS immediately; does NOT retry
  - Incident raised in ITSM (or alert sent to security)
  - User receives appropriate safe decline message

Validation:
  - No retry-around-guardrail behaviour observed
  - Audit log shows guardrail trip with full context
  - Alert sent within 30 seconds of guardrail trip
  - Task not retried with modified prompt
```

### 5.3 Chaos Schedule

| Experiment | Frequency | Environment |
| --- | --- | --- |
| Provider outage | Monthly | Staging |
| Model quality degradation | Quarterly | Staging |
| Tool failure cascade | Monthly | Staging |
| Context overflow | Quarterly | Staging |
| Safety failure | Monthly | Staging (synthetic inputs only) |
| Full multi-fault chaos | Quarterly | Staging |
| Provider failover test | Monthly | Production canary (5% traffic) |

---

## 6. Agent On-Call

### 6.1 Agent-Specific Incident Classification

Standard SRE incident severity doesn't map cleanly to agent failures. Use this agent-specific classification:

| Severity | Agent Condition | Response |
| --- | --- | --- |
| **P0 — Critical Safety** | Guardrail bypassed; harmful output reached user; agent took destructive action | Immediate shutdown; security team notified; human review before re-enable |
| **P1 — Service Down** | TCR &lt; 50%; all tasks failing; agent runtime crash | Page on-call immediately; agent killed switch if needed |
| **P2 — Quality Degraded** | SQR drops > 15%; users receiving poor outputs | Page on-call within 15 minutes; quality investigation |
| **P3 — Partial Impairment** | TCR 85–97%; one tool failing; latency SLO miss | Slack alert; business-hours investigation |
| **P4 — Cost Anomaly** | CPT > 2× baseline; budget burn accelerating | JIRA ticket; team investigates next business day |
| **P5 — Informational** | SLO burn rate approaching threshold; minor drift | Dashboard only; no alert |

### 6.2 Agent Incident Runbook Template

```markdown
# Agent Incident Runbook: [Incident Type]

## Summary
What this runbook addresses: [Incident pattern]
Agent affected: [Agent ID]
Severity classification: [P0–P5]

## Detection
How this incident is detected: [Alert name / guardrail / SLO burn]
Alert link: [dashboard link]

## Immediate triage (0–5 minutes)

1. Check agent runtime status:
   `kubectl get pods -n agents -l agent=[agent-id]`

2. Check TCR over last 15 minutes:
   [Grafana dashboard link]

3. Check for recent deployments:
   [Deployment history link or command]

4. Check provider status:
   - Anthropic: https://status.anthropic.com
   - [Other providers used by this agent]

## Containment

For P0/P1: Enable kill switch:
  [kill switch command or feature flag URL]

For P2/P3: Enable fallback model:
  `kubectl set env deployment/[agent-id] FALLBACK_MODE=true`

## Root Cause Investigation

5. Read last 100 task traces:
   [Jaeger / trace query command]

6. Check for quality degradation pattern:
   [LLM-as-judge scores dashboard link]

7. Check for tool failure cascade:
   [Tool error rate dashboard link]

## Resolution

Based on root cause:
- Provider outage → Fallback model; wait for provider recovery
- Model quality regression → Roll back to previous model version
- Tool failure → Disable failing tool; use alternative
- Guardrail false positives → Tune guardrail threshold (requires security review)
- Code bug → Roll back deployment; fix in next release

## Post-incident

- Update SLO burn dashboard to show resolved
- Draft postmortem (use AI-generated draft from incident data)
- Create follow-up tickets for root cause fix
- Add test case to chaos engineering suite if novel failure mode
```

### 6.3 On-Call Load Targets

ARE teams should target on-call loads that are sustainable:

| Metric | Target | Alert Threshold |
| --- | --- | --- |
| Pages per engineer per week | &lt; 3 during business hours; &lt; 1 at night | > 5/week |
| Mean time from page to resolution (P1) | &lt; 30 minutes | > 60 minutes |
| % incidents handled by automation | > 60% | &lt; 40% |
| Postmortem completion rate | > 95% | &lt; 80% |

If on-call load exceeds targets, activate error budget enforcement: freeze feature development and focus on reliability until load normalises.

---

## 7. Agent Capacity Planning

### 7.1 Capacity Dimensions for Agent Systems

Agent capacity planning differs from traditional capacity planning because agents consume multiple resource types simultaneously:

| Resource | Planning Horizon | Scaling Approach |
| --- | --- | --- |
| **Model tokens per second** | 30-day rolling forecast | Provider rate limit increase; model routing; caching |
| **Agent runtime (CPU/RAM)** | 7-day rolling | Kubernetes HPA; KEDA on queue depth |
| **Vector store capacity** | 90-day forecast | Index sharding; tiered storage |
| **Tool call rate** | 30-day rolling | Tool server scaling; rate limit planning |
| **LLM-as-judge capacity** | 30-day rolling | Separate quota for evaluation; sampling rate adjustment |
| **Trace storage** | 90-day forecast | Sampling rate; hot/cold tiering |
| **GPU capacity** (self-hosted) | 6-month forecast | H100/A100 reservation; neocloud contracts |

### 7.2 Model Token Forecast

The dominant capacity constraint for most agent systems is model token throughput:

```
MONTHLY TOKEN FORECAST MODEL

Base: current month avg daily tokens used × 30
Growth: apply CAGR from last 3 months
Seasonality: adjust for known high-load events (quarter-end, Black Friday)

Alert: Forecast exceeds 70% of provider rate limit → request limit increase
Alert: Forecast exceeds 90% of limit → emergency routing to secondary provider

Example:
  Current: 500M tokens/month
  Growth rate: 15%/month
  3-month forecast: 500M × (1.15)^3 = 760M tokens/month
  Provider rate limit: 800M tokens/month
  Action: Request increase to 1.2B by month 2
```

### 7.3 Agent Pool Sizing

For agents deployed as Kubernetes Deployments:

```
AGENT POOL SIZING FORMULA

concurrent_tasks = task_rate × avg_task_duration
agent_replicas = ceil(concurrent_tasks / tasks_per_agent_replica) × 1.3 (buffer)

Example:
  task_rate = 100 tasks/minute
  avg_task_duration = 45 seconds
  concurrent_tasks = 100/60 × 45 = 75
  tasks_per_replica = 5 (based on CPU profiling)
  replicas_needed = ceil(75/5) × 1.3 = 20 replicas

KEDA scaler: scale on queue depth (0 replicas when idle; scale up linearly with queue)
Max replicas: set to provider rate limit / tokens_per_task
```

---

## 8. Agent Model Version Management

### 8.1 The Model Update Problem

When a model provider releases a new version, it may:

- Improve performance on most tasks
- Regress on your specific task due to RLHF changes
- Change structured output format slightly
- Behave differently on edge cases

Without ARE governance, model updates silently break production agents.

### 8.2 Model Update Protocol

```
PROVIDER ANNOUNCES NEW MODEL VERSION
           │
           ▼
   EVALUATION HARNESS RUNS (automated, within 4 hours)
   - Full golden set evaluation on new model version
   - Compare against current production model scores
   - Flag any dimension where new model scores < current - 2%
           │
      ┌────┴────┐
   PASS        FAIL (regression detected)
   (scores     │
    equal or   ▼
    better)  BLOCK auto-upgrade
      │       Create Jira ticket with regression detail
      ▼       Notify model team + product owner
   PROMOTE    Investigate: prompt tuning? | version pinned? | model rejected?
   to staging │
      │       Options:
      ▼       1. Tune prompt to recover performance → re-evaluate
   SHADOW     2. Pin to previous version (notify team of vendor timeline)
   TEST       3. Accept regression if tradeoff acceptable (documented decision)
   (5%, 24h)
      │
      ▼
   PROMOTE to production (with 1-hour monitoring period)
```

### 8.3 Model Version Pinning Policy

| Situation | Action | Maximum Pin Duration |
| --- | --- | --- |
| Quality regression detected | Pin to previous version | 90 days (vendor may deprecate) |
| Breaking change in tool calling schema | Pin; submit issue to vendor | 60 days |
| Active incident investigation | Pin for stability | 14 days |
| Feature development in progress | Pin for stability | 30 days |

When approaching pin expiration: re-evaluate on updated version or escalate to vendor for resolution.

---

## 9. ARE Maturity Model

| Level | Name | Characteristics | Target Metrics |
| --- | --- | --- | --- |
| **L0** | No ARE | No SLOs; incidents discovered by user complaints | MTTR > 2 hours; no quality metrics |
| **L1** | Basic monitoring | Availability monitoring; basic alerting; manual postmortems | MTTR &lt; 60 min; no quality SLOs |
| **L2** | ARE Foundations | SLOs defined; evaluation harness; structured incident response | TCR > 95%; SQR measured; PRR process exists |
| **L3** | Proactive ARE | Chaos testing; error budget enforcement; automated quality monitoring | TCR > 98%; on-call &lt; 5 pages/week |
| **L4** | Advanced ARE | Full chaos suite; model update automation; capacity forecasting | TCR > 99%; on-call &lt; 2 pages/week; toil &lt; 30% |
| **L5** | ARE-Driven Development | Error budgets gate feature development; ARE metrics drive product decisions | SLOs stable; continuous improvement without incidents |

### 9.1 ARE Adoption Roadmap

**Month 1–2 (L0 → L1):**

- Define TCR and latency SLOs for each agent in production
- Deploy OTel GenAI spans for all model calls
- Establish on-call rotation for agent incidents
- First agent PRR completed for highest-traffic agent

**Month 3–4 (L1 → L2):**

- Evaluation harness running in CI/CD for all agents
- SQR monitoring with LLM-as-judge live for top 3 agents
- Error budget policy defined and communicated
- Agent on-call runbooks for top 10 incident types

**Month 5–8 (L2 → L3):**

- Chaos engineering started: provider outage and tool failure experiments
- Error budget enforcement gates in place
- Model update protocol automated
- CPT monitoring live for all agents

**Month 9–18 (L3 → L4):**

- Full chaos suite running quarterly
- Capacity forecasting automated
- Toil tracking and elimination programme active
- ARE dashboard: all SLO dimensions visible in one view

---

## 10. ARE Reference Glossary

| Term | Definition |
| --- | --- |
| **ARE** | Agent Reliability Engineering — applying SRE discipline to AI agent production systems |
| **TCR** | Task Completion Rate — % of attempted tasks that complete successfully |
| **SQR** | Semantic Quality Rate — % of tasks producing acceptable quality outputs |
| **SCR** | Safety Compliance Rate — % of tasks that complete without triggering safety guardrails |
| **CPT** | Cost Per Task — total inference cost divided by successful tasks |
| **Error budget** | Allowed failure volume within an SLO period; when exhausted, feature development stops |
| **PRR** | Production Readiness Review — checklist-gated review before agent goes to production |
| **Chaos engineering (ARE)** | Injecting agent-specific faults (provider outage, quality degradation) to test failure handling |
| **Toil** | Manual, repetitive, automatable work that grows with scale |
| **Model version pinning** | Locking an agent to a specific model version to prevent unplanned updates |
| **Golden evaluation set** | Curated dataset of representative inputs with known acceptable outputs used to test agent quality |
| **LLM-as-judge** | Using a language model to evaluate another model's output quality |
| **Guardrail false positive** | Safety guardrail blocking a valid, safe input — part of SCR measurement |
| **Degradation ladder** | Ordered set of capability modes from full capability to graceful shutdown |
| **HITL gate** | Human-in-the-Loop gate — requiring human approval before an agent takes an action |

---

## Further Reading

**Internal Cross-References**

- [Agentic AI Reliability, Observability & Governance](43-agentic-ai-reliability-observability-governance.md) — Reliability patterns: retry, circuit breakers, checkpointing, graceful degradation
- [Enterprise AIOps Guide](pathname:///archon/engineering/aiops-guide) — AI applied to IT operations; AIOps platform design
- [Agentic AI Security & Guardrails](pathname:///archon/architecture/agentic-ai-security-guardrails) — Guardrail architecture; safety controls
- [Enterprise AI Architecture Patterns](49-enterprise-ai-architecture-patterns.md) — Pattern 7: LLM-as-judge evaluation | Pattern 13: Evaluation harness
- [Enterprise AI Governance & Compliance](51-enterprise-ai-governance-compliance.md) — Governance framework; compliance controls

**External References**

- [Google SRE Books](https://sre.google) — SRE foundations: SLOs, error budgets, toil, on-call
- [Chaos Engineering Principles](https://principlesofchaos.org) — Chaos engineering methodology
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — Telemetry standards for AI systems
- [NIST AI RMF](https://www.nist.gov/system/files/documents/2023/01/26/AI%20RMF%201.0.pdf) — AI risk management framework
