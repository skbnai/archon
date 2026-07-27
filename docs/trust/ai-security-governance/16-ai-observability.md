---
title: "AI Observability"
doc_type: guide
domain: trust
status: current
topic_id: ai-observability
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part12_AI_Observability.md]
tags: [ai-security, observability, deepmind, opentelemetry]
covers_version: "as of 2026"
---

Reasoning telemetry, decision audit trails, OpenTelemetry semantic conventions for AI, an observability platform comparison, and behavioral analytics for AI security.

## Beyond Traditional Observability: The AI Observability Stack

Traditional observability (logs, metrics, traces) captures what software systems did in sufficient detail for operations and debugging. For AI agents, this is necessary but insufficient: logs tell you what API calls were made; AI observability additionally captures why those calls were made, what the agent was thinking, and whether the reasoning process was sound. This semantic dimension of observability is unique to AI systems and requires new instrumentation primitives.

**AI observability dimensions:**

- **Execution Observability:** tool calls, API requests, outputs. Standard distributed tracing handles this layer. Implementation: OpenTelemetry traces.
- **Context Observability:** what information was in the agent's context when each decision was made. Essential for debugging and audit. Implementation: context snapshots in trace spans.
- **Reasoning Observability:** why the agent made each decision. Includes chain-of-thought, goal state, planning traces. Implementation: LLM-specific span attributes.
- **Memory Observability:** what memories were retrieved and written; how memory influenced decisions. Implementation: memory read/write events in trace.
- **Goal Observability:** how the agent's goal state evolved throughout the task; goal drift detection. Implementation: goal state events timeline.
- **Trust Observability:** real-time trust scores; policy decisions; authorization events. Implementation: policy decision events.
- **Behavioral Observability:** statistical behavioral patterns; drift from baseline; anomaly detection. Implementation: behavioral analytics platform.

## OpenTelemetry for AI Agents

**OpenInference semantic conventions.** OpenInference (Arize AI's contribution to OpenTelemetry for AI) defines semantic conventions for LLM and agent observability. These conventions standardize how AI systems instrument their traces, enabling consistent analysis across different frameworks and vendors.

| OTel Attribute | Content | Security Use |
|---|---|---|
| `gen_ai.prompt` | Input prompt to LLM call | Injection detection; prompt audit |
| `gen_ai.completion` | LLM output text | Output safety scanning; PII detection |
| `gen_ai.tool.name` | Name of tool invoked | Tool usage audit; policy verification |
| `gen_ai.tool.input` | Tool invocation parameters | Parameter validation; DLP |
| `gen_ai.tool.output` | Tool result returned to model | Result injection detection; content scanning |
| `llm.token.count.total` | Token usage for the LLM call | Cost control; DoS detection |
| `gen_ai.agent.id` | Unique agent instance identifier | Agent identity correlation |
| `gen_ai.agent.goal` | Current agent goal state | Goal drift detection; intent verification |
| `gen_ai.retrieval.query` | Query sent to vector database | Retrieval monitoring; data access audit |
| `gen_ai.retrieval.results` | Documents retrieved | Knowledge base access audit |

## AI Observability Platform Comparison

| Platform | Strengths | Weaknesses | Best For |
|---|---|---|---|
| Arize Phoenix | LLM eval framework; strong prompt/response analysis; open source; OTel integration | Limited multi-agent support; no enterprise RBAC in OSS version | LLM quality monitoring; prompt optimization |
| Langfuse | Excellent trace visualization; cost tracking; datasets and evals; strong OSS community | Newer platform; multi-agent tracing improving | Developer debugging; evaluation pipelines |
| Weights & Biases (Weave) | Strong experiment tracking; model versioning; good LLM support | ML engineering focus; less security-oriented | Model development and evaluation |
| Helicone | Low-latency proxy; cost monitoring; request logging | Limited semantic analysis; more operational than analytical | Cost management; request logging |
| Custom OpenTelemetry | Full control; integrate with existing Grafana/Datadog; compliance-ready | Significant engineering effort; no AI-specific dashboards out of the box | Enterprises with existing OTel investment |
| Datadog LLM Observability | Integrated with existing enterprise Datadog; good security team adoption | Limited LLM-specific depth vs. dedicated platforms; cost | Enterprises already using Datadog |

## Reasoning Telemetry Architecture

**Capturing agent reasoning traces.** Reasoning telemetry captures the agent's chain-of-thought, planning steps, and decision rationale in a structured, queryable format. This data is essential for security audit, compliance, debugging, and behavioral analytics. However, reasoning traces may contain sensitive business information and must be protected with the same care as the outputs.

**Reasoning trace data structure — example schema (JSON):**

```json
{
  "trace_id": "tr-8f3a2c...",
  "agent_id": "finance-analyst-sess-a7f2b1",
  "task_id": "task-8c3d9e",
  "step_number": 3,
  "goal_state": "Analyze Q2 revenue by region",
  "reasoning": "<stored encrypted>",
  "reasoning_summary": "Decided to retrieve revenue data from data warehouse",
  "planned_action": {
    "tool": "query_data_warehouse",
    "parameters": { "query_id": "rev_by_region_q2" }
  },
  "risk_score": 15,
  "policy_decision": "APPROVE",
  "timestamp": "2026-06-25T14:23:01Z"
}
```

**Reasoning trace privacy:**

- **Encryption at Rest:** reasoning traces encrypted with agent-instance-specific keys; key rotation on session end.
- **Access Control:** reasoning traces accessible only to the deploying team, SOC with audit justification, and compliance under court order.
- **Redaction Pipeline:** automated PII detection and redaction in reasoning summaries before they enter analytics pipelines.
- **Selective Disclosure:** regulatory reporting receives summaries, not full traces; full traces available only through a privileged access process.

## Behavioral Analytics for AI Security

Behavioral analytics applies statistical and ML methods to agent telemetry to detect anomalies, drift, and potential security incidents that rule-based systems cannot catch. The key insight is that even individually authorized actions can be anomalous in aggregate — detecting this requires statistical modeling of normal behavior.

| Analytic | Method | Signal | Alert Threshold |
|---|---|---|---|
| Action frequency analysis | Z-score vs. baseline distribution | Sudden burst of specific action type | &gt;3 sigma from hourly baseline |
| Data access pattern | Graph-based access pattern comparison | Novel resource access or graph traversal | New node accessed in access graph |
| API endpoint diversity | Shannon entropy of API calls | Systematic API enumeration (low entropy) | &lt;2.0 bits entropy over 100 calls |
| External call correlation | Cross-agent external call analysis | Multiple agents calling same unusual endpoint | &gt;3 agents calling same new endpoint |
| Session risk trajectory | Time-series analysis of cumulative risk score | Accelerating risk accumulation | Risk score growth &gt;5 points/minute |
| Goal drift | Semantic similarity of actions to stated goal over time | Actions diverging from stated goal | Semantic similarity &lt;0.6 |
| Credential access timing | Time-of-day and sequence analysis | Unusual credential access patterns | Access outside normal operational hours |

## Related

- [Multi-Agent Security](15-multi-agent-security.md)
- [AI Security Operations Center](17-ai-soc.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
