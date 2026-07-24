---
title: Observability Framework for Orchestrated AI Systems
domain: agentic-systems
doc_type: guide
topic_id: observability-framework
status: current
supersedes:
  - docs/workflow-orchestration/16-observability-framework.md
date_created: 2026-07-24
last_reviewed: 2026-07-24
source_type: native-md
covers_version: "as of July 2026 — OpenTelemetry 1.x, LangSmith latest, Temporal Web UI 2.x"
tags:
  - workflow-orchestration
  - observability
  - tracing
  - monitoring
  - opentelemetry
---

# Observability Framework for Orchestrated AI Systems

> **As of July 2026.** OpenTelemetry 1.x; LangSmith; Temporal Web UI 2.x; Grafana for dashboards.

This guide designs unified observability for systems running Temporal, Camunda, and LangGraph together. The challenge is stitching traces across three fundamentally different execution models into a single coherent picture of what happened and why.

---

## The Observability Challenge

Three tools. Three trace formats. Three dashboards. A single business process — loan approval — might touch all three:

```mermaid
graph TD
    A["Customer request"] --> B["Temporal Workflow<br/>process orchestration"]
    B --> C["Activity: run_agent"]
    C --> D["LangGraph Agent<br/>reasoning"]
    D --> E["Tool: get_credit_score"]
    D --> F["Tool: check_compliance"]
    D --> G["Tool: draft_decision"]
    D --> H["Camunda Process<br/>DMN decision routing"]
    H --> I["Gateway: route_by_risk_level"]
    I --> J["Temporal Workflow continues<br/>Activity: notify_applicant"]
    J --> K["Response to applicant"]
```

To answer "why did application APP-123 get rejected?" you need to correlate events across all three systems using a single trace ID.

---

## Three Observability Domains

### Domain 1: Workflow Observability (Process Layer)

**What to capture**: Step sequence, duration per step, retries, failures, signals received.

**Tools**: Temporal Web UI (built-in); OpenTelemetry spans for custom export.

```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer("workflow.orchestration")

@activity.defn
async def check_credit_activity(applicant_id: str) -> CreditResult:
    with tracer.start_as_current_span(
        "activity.check_credit",
        kind=SpanKind.INTERNAL,
        attributes={
            "applicant.id": applicant_id,
            "workflow.type": "loan_approval",
            "activity.attempt": activity.info().attempt,
        },
    ) as span:
        try:
            result = await credit_bureau.check(applicant_id)
            span.set_attribute("credit.score", result.score)
            span.set_attribute("credit.decision", result.decision)
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR, str(e))
            raise
```

**Key metrics to expose**:

```python
from opentelemetry import metrics

meter = metrics.get_meter("workflow.process")

workflow_duration = meter.create_histogram(
    "workflow.duration_ms",
    description="End-to-end workflow duration",
)
activity_success_rate = meter.create_gauge(
    "workflow.activity.success_rate",
    description="Success rate per activity type",
)
workflow_sla_breach = meter.create_counter(
    "workflow.sla_breach",
    description="Workflows that exceeded SLA",
)
```

---

### Domain 2: Agent Observability (Reasoning Layer)

**What to capture**: Reasoning steps, tool calls with inputs/outputs, token usage, decision rationale, iteration count.

**Tools**: LangSmith for LangGraph; custom OpenTelemetry spans; structured logging.

```python
from langsmith import traceable
from opentelemetry import trace

tracer = trace.get_tracer("agent.reasoning")

@traceable(name="underwriting_agent_run")  # LangSmith tracing
async def run_underwriting_agent(application_id: str, context: dict) -> dict:
    with tracer.start_as_current_span(
        "agent.run",
        attributes={
            "agent.type": "underwriting",
            "application.id": application_id,
            "trace.id": get_parent_trace_id(),  # correlate to workflow trace
        },
    ) as span:

        graph = build_underwriting_graph()
        result = await graph.ainvoke(
            {"application_id": application_id, "context": context},
            config={"configurable": {"thread_id": application_id}},
        )

        # Record agent-level metrics in the span
        span.set_attribute("agent.iterations", result["iteration_count"])
        span.set_attribute("agent.tokens_used", result["total_tokens"])
        span.set_attribute("agent.tool_calls", len(result["tool_calls"]))
        span.set_attribute("agent.decision", result["decision"])

        return result
```

**Structured reasoning log** — append to every tool call for post-hoc analysis:

```python
import structlog

log = structlog.get_logger()

def log_tool_call(
    run_id: str,
    tool_name: str,
    tool_input: dict,
    tool_output: str,
    reasoning: str,
    iteration: int,
) -> None:
    log.info(
        "agent.tool_call",
        run_id=run_id,
        iteration=iteration,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_output_length=len(tool_output),
        tool_output_preview=tool_output[:200],
        agent_reasoning=reasoning,
    )
```

---

### Domain 3: Business Observability (Outcome Layer)

**What to capture**: Business outcomes by workflow version, model version, and prompt version. This is the layer that answers "did our AI actually help?"

```python
from opentelemetry import metrics
from datetime import datetime

meter = metrics.get_meter("business.outcomes")

# Decision distribution — the most important signal
decision_distribution = meter.create_histogram(
    "business.decision",
    description="Distribution of business decisions by type",
)

# Override rate — are humans correcting the AI?
human_override = meter.create_counter(
    "business.human_override",
    description="Number of agent decisions overridden by humans",
)

# Business value metrics
loans_approved_amount = meter.create_histogram(
    "business.loan.approved_amount",
    description="Dollar value of loans approved",
)

async def record_business_outcome(
    workflow_id: str,
    decision: str,
    overridden: bool,
    amount: float,
    prompt_version: str,
    model_id: str,
) -> None:
    attributes = {
        "decision": decision,
        "prompt_version": prompt_version,
        "model_id": model_id,
    }

    decision_distribution.record(1, attributes)

    if overridden:
        human_override.add(1, attributes)

    if decision == "approved":
        loans_approved_amount.record(amount, attributes)
```

---

## Distributed Trace Correlation

The key to unified observability is propagating a single trace ID from the Temporal workflow through to the agent and back.

```python
from opentelemetry.propagate import extract, inject
from opentelemetry import context, trace

# In Temporal workflow: create root span, extract trace context
@workflow.defn
class LoanWorkflow:
    @workflow.run
    async def run(self, application_id: str) -> dict:
        tracer = trace.get_tracer("workflow")

        with tracer.start_as_current_span(f"workflow.loan_approval.{application_id}") as root_span:
            # Extract trace context for injection into activity
            carrier = {}
            inject(carrier)  # puts traceparent + tracestate into carrier dict

            # Pass carrier to agent activity so it continues the same trace
            result = await workflow.execute_activity(
                run_agent_activity,
                {"application_id": application_id, "trace_carrier": carrier},
                start_to_close_timeout=timedelta(minutes=5),
            )
            return result

# In agent activity: restore trace context from workflow
@activity.defn
async def run_agent_activity(input_data: dict) -> dict:
    # Restore the trace context from the workflow
    ctx = extract(input_data["trace_carrier"])
    token = context.attach(ctx)

    try:
        tracer = trace.get_tracer("agent")
        with tracer.start_as_current_span("activity.agent_run") as span:
            # This span is now a CHILD of the workflow's root span
            result = await run_underwriting_agent(input_data["application_id"])
            return result
    finally:
        context.detach(token)
```

With trace propagation, a single Jaeger/Grafana Tempo query shows the full distributed trace hierarchy:

**Trace: TRACE-abc123 (3.2s total)**
  - **workflow.loan_approval.APP-123** (3.2s)
    - activity.check_credit (0.4s)
    - activity.agent_run (2.1s)
      - agent.tool_call: get_credit_profile (0.3s)
      - agent.tool_call: check_compliance (0.8s)
      - agent.tool_call: lookup_policy (0.2s)
      - agent.reason_and_decide (0.8s — LLM time)
    - activity.notify_applicant (0.3s)

---

## Dashboards

### Operations Dashboard (SRE view)

**Workflow Orchestration — Operations Dashboard**

| Metric | Value |
|--------|-------|
| **Throughput** | 1,240 runs/hr |
| **Latency (p95)** | 4.2s |
| **Error Rate** | 0.3% |

**Agent Metrics**
- Average iterations: 4.1
- Average tokens: 8,200
- Loop detections: 0

**Active Workflows by Status**
- Running: 42
- Waiting approval: 7
- Failed: 2

### Business Dashboard (Product view)

**Loan Approval — Business Intelligence Dashboard**

**Today's Decisions**
- Processed: 156
- Total approved: $2.4M

**Decision Breakdown**
- Approved: 68%
- Rejected: 24%
- Pending documentation: 8%

**Quality Metrics**
- Human Override Rate: 4.2% (target: &lt;10%)
- Prompt version: underwriting-v3.1.2
- Model: claude-sonnet-4-6

---

## Alerting Strategy

```yaml
# grafana_alerts.yaml
groups:
  - name: workflow_orchestration
    rules:
      - alert: WorkflowErrorRateHigh
        expr: rate(workflow.errors[5m]) > 0.02
        for: 2m
        annotations:
          summary: "Workflow error rate above 2% — check Temporal for failed workflows"

      - alert: AgentIterationsHigh
        expr: histogram_quantile(0.95, agent.iterations) > 10
        for: 5m
        annotations:
          summary: "Agent p95 iterations above 10 — possible reasoning loops forming"

      - alert: BusinessOverrideRateHigh
        expr: business.human_override_rate > 0.15
        for: 10m
        annotations:
          summary: "Human override rate above 15% — agent decision quality degraded"
          runbook: "https://wiki.internal/runbooks/agent-override-rate-high"

      - alert: PromptVersionDrift
        expr: count(distinct(business.decision{prompt_version=~".+"})) > 2
        for: 0m
        annotations:
          summary: "More than 2 prompt versions active — possible rollout issue"
```

---

## Debugging Agent Decisions Post-Hoc

When a stakeholder questions a specific agent decision weeks after it happened, you need to reconstruct exactly what the agent saw and why it decided what it did.

```python
async def reconstruct_decision(decision_id: str) -> dict:
    """Full reconstruction of an agent decision for audit or debugging."""

    # Retrieve the audit record (immutable — stored at decision time)
    record = await audit_db.get_decision(decision_id)

    # Retrieve the prompt version active at that time
    prompt = await prompt_registry.get_version(
        record.prompt_id, record.prompt_version
    )

    # Retrieve the tool call log
    tool_calls = await trace_store.get_tool_calls(record.run_id)

    # Reconstruct the full conversation the LLM saw
    reconstructed_messages = rebuild_conversation(
        system_prompt=prompt.content,
        tool_calls=tool_calls,
        tool_results=record.tool_results,
    )

    return {
        "decision_id": decision_id,
        "made_at": record.timestamp.isoformat(),
        "model": record.model_id,
        "prompt_version": record.prompt_version,
        "reconstructed_conversation": reconstructed_messages,
        "final_decision": record.final_decision,
        "human_reviewer": record.human_reviewer,
        "human_override": record.human_decision if record.human_reviewer else None,
    }
```

This reconstruction capability is a regulatory requirement in many jurisdictions — the firm must be able to explain any AI-assisted decision to an examiner, months or years later.

---

## Tool Choices

| Use Case | Tool | Why |
| --- | --- | --- |
| Workflow traces | Temporal Web UI | Built-in, zero setup, full event log |
| Agent reasoning traces | LangSmith | First-class LangGraph support, trace diffing |
| Distributed tracing | Grafana Tempo + OpenTelemetry | Correlate across all systems |
| Metrics dashboards | Grafana | Standard, works with all metric backends |
| Log aggregation | Loki (or Datadog/Splunk) | Structured log queries |
| Alerting | Grafana Alertmanager | Unified alert routing |

---

## Incident Response with Observability

When something breaks in production, observability determines how fast you recover. The following workflow applies to both workflow failures and agent quality degradation.

### Incident Triage Playbook

```
Step 1: Identify the failure domain
  Is the error rate up?        → Check workflow traces (Temporal Web UI)
  Is the latency up?           → Check activity duration breakdown
  Is override rate up?         → Check agent decision distribution dashboard
  Is a specific step failing?  → Filter traces by activity type + error

Step 2: Isolate the change
  What deployed in the last hour?
    - Check prompt_version in recent audit records
    - Check model_id in recent decision records
    - Check git log for workflow/activity changes

Step 3: Scope the blast radius
  How many workflow runs are affected?
  → SELECT COUNT(*) FROM audit_records WHERE prompt_version = 'v3.2.0' AND failed = true

Step 4: Mitigate
  Prompt issue → rollback prompt to previous version (see Enterprise Governance Model)
  Activity failure → Temporal retries may handle it automatically
  Agent quality drop → escalate all decisions to human until root cause found

Step 5: Root cause and follow-up
  Write incident report with: timeline, metrics before/after, root cause, fix applied
```

### Trace Query Examples

```python
# Find all agent runs that took > 60 seconds (Jaeger/Tempo HTTP API)
import requests

def find_slow_agent_runs(min_duration_ms: int = 60_000) -> list[dict]:
    response = requests.get(
        "http://tempo.internal:3100/api/search",
        params={
            "service.name": "agent.reasoning",
            "min_duration": f"{min_duration_ms}ms",
            "limit": 50,
        },
    )
    return response.json()["traces"]

# Find all runs that escalated to human (structured log query)
def find_escalated_runs(hours: int = 24) -> list[dict]:
    return log_client.query(
        filter='event="agent.escalated_to_human"',
        time_range_hours=hours,
        fields=["run_id", "workflow_id", "reason", "timestamp"],
    )
```

---

## Related

[Reliability Playbook](./15-reliability-playbook.md) · [Security Architecture](./17-workflow-orchestration-security-architecture.md) · [Enterprise Governance Model](./18-enterprise-governance-model.md) · [Human-in-the-Loop Architectures](./12-human-in-the-loop-architectures.md)
