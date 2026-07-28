---
title: "AI SOC Playbooks Part 08: AI SOC Observability & Evaluation"
doc_type: guide
domain: trust
status: current
topic_id: part-08-observability
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: [docs/ai-soc-playbooks/part-08-observability.md]
tags: [observability, opentelemetry, langfuse, arize, evaluation, drift, kpis]
covers_version: "2026"
---

What to observe in an AI SOC beyond traditional infrastructure and application metrics, the tools that observe it, distributed tracing across multi-agent investigations, evaluation pipelines, drift detection, dashboards, and the quality gates a new model version must clear before production deployment.

## What to Observe in an AI SOC

Traditional SOC observability (infrastructure CPU/memory/disk/network, application alert-queue depth and SLAs, business MTTD/MTTR/FPR, security unauthorized-access and config-drift monitoring) needs a parallel AI-specific layer: infrastructure adds GPU utilization, inference latency, and queue depth; application adds token usage, model calls per minute, and cost per alert; business adds AI accuracy, analyst override rate, and confidence calibration; security adds prompt-injection attempts, jailbreak attempts, and model behavior drift.

Four observability pillars organize this. **Prompt telemetry** captures every LLM request and response — the sanitized (PII-redacted) prompt, the response, token counts (input/output/cached), latency (time-to-first-token and total), model version, agent ID, and an incident correlation ID. **Agent telemetry** traces every agent action — tool calls (name, inputs, outputs, latency), decision points and reasoning, human approval requests and outcomes, escalations, errors, and retries. **Quality metrics** track AI decision quality — verdict accuracy against analyst override, confidence calibration (does 80% stated confidence actually mean 80% accuracy), hallucination rate, false-positive rate, and false-negative rate (the most critical metric in security, since a missed threat is far costlier than a false alarm). **Cost metrics** track spending — tokens per alert by type, cost per alert by model, cost per incident, and whether token efficiency is trending down with prompt optimization.

## Observability Tools Comparison

| Tool | Type | Best For | Self-Hosted |
|---|---|---|---|
| Langfuse | Open-source LLM observability | Full-stack LLM tracing, eval pipelines | Yes |
| Arize Phoenix | LLM + ML observability | Embedding drift, AI quality | Yes |
| OpenTelemetry AI | Standard | Vendor-neutral traces | Yes |
| MLflow | ML lifecycle | Model registry + experiment tracking | Yes |
| Grafana + Prometheus | Infrastructure | Infra + custom LLM metrics | Yes |
| Azure Monitor + AppInsights | Azure-native | Azure OpenAI + Sentinel | No |
| AWS CloudWatch + X-Ray | AWS-native | Bedrock + AgentCore traces | No |
| Datadog LLM Obs | Commercial | Full-stack with APM | No |
| Helicone | LLM gateway observability | Caching + cost tracking | No |

A Langfuse integration wraps a triage function with an `@observe` decorator, attaches incident metadata (ID, alert type, severity, asset criticality) to the trace, and scores the trace for later quality monitoring once an analyst has reviewed it — giving a queryable, per-incident audit trail of every LLM call without hand-rolled logging.

## Distributed Tracing for Multi-Agent SOC

OpenTelemetry's AI semantic conventions let a multi-agent investigation produce a single coherent trace tree: a root `soc.investigation` span carries incident ID/severity/type, a child `soc.triage` span records the model, max tokens, total token usage, verdict, and confidence, and — only if the triage verdict is `TRUE_POSITIVE` — a further child `soc.investigation` span records the investigation agent's findings, including the number of MITRE techniques identified. Correlation IDs propagate across agent-to-agent HTTP calls via standard headers (`X-Trace-ID`, `X-Incident-ID`, `X-Span-ID`, `X-Parent-Span`, `X-Agent-ID`) plus a W3C-standard `traceparent` header, so any agent boundary crossing preserves the full trace lineage back to the originating incident.

## Evaluation Pipelines

A weekly evaluation cycle pulls the past week's AI decisions that have since been reviewed by an analyst (giving ground truth) and computes: classification accuracy (precision, recall — recall is the metric that must never slip, since it measures never missing a real threat — F1, false-positive rate, and false-negative rate, the single most security-critical number); confidence calibration via Expected Calibration Error; investigation quality and MITRE-mapping accuracy (both requiring human or LLM-judge scoring); latency (average and P95); cost efficiency (average tokens and cost per alert); and the human-AI interaction rate (analyst override rate, and its complement, agreement rate). Any metric crossing a degradation threshold triggers an alert automatically rather than waiting for someone to notice a slow decline.

Expected Calibration Error measures whether stated confidence tracks actual accuracy — perfect calibration means 80%-confident predictions are correct 80% of the time, and an ECE under 0.10 is considered well-calibrated:

```python
def _expected_calibration_error(self, decisions: list) -> float:
    n_bins, total_ece = 10, 0
    for bin_idx in range(n_bins):
        bin_min, bin_max = bin_idx / n_bins, (bin_idx + 1) / n_bins
        bin_decisions = [d for d in decisions if bin_min <= d.confidence / 100 < bin_max]
        if not bin_decisions:
            continue
        bin_accuracy = sum(1 for d in bin_decisions if d.correct) / len(bin_decisions)
        bin_confidence = sum(d.confidence / 100 for d in bin_decisions) / len(bin_decisions)
        total_ece += (len(bin_decisions) / len(decisions)) * abs(bin_accuracy - bin_confidence)
    return total_ece
```

For investigation quality specifically, an LLM-as-judge pattern compares the AI's investigation report against an expert-verified ground truth on five dimensions — completeness (were all key events and findings identified), accuracy (were techniques and timeline correct), MITRE mapping correctness, severity/business-impact assessment, and recommendation appropriateness — each scored 0-10 with an explanation, giving a structured quality signal that's far cheaper to run at scale than pure human review while still catching more than a pure metrics-only pipeline would.

## Drift Detection

Four distinct drift types need separate monitoring. **Data drift** — the alert-feature distribution itself changes as new attack patterns emerge — detected via a Kolmogorov-Smirnov statistical test comparing recent versus baseline feature distributions, degrading model accuracy specifically on the new pattern. **Concept drift** — the relationship between inputs and correct labels changes even though the input distribution looks the same — detected by monitoring the analyst override rate over time, producing wrong answers as threats evolve past what the model was tuned against. **Model drift** — raw performance degrades with no corresponding input change — detected by tracking accuracy over a rolling window, manifesting as rising false negatives. **Embedding drift** — the vector space distribution underlying RAG retrieval shifts — detected by monitoring embedding distance over time, degrading retrieval quality even when the model itself hasn't changed.

A practical data-drift check runs a KS-test comparing a 30-day baseline against the last 7 days across key alert features (severity, IOC score, asset criticality), flagging drift wherever the resulting p-value drops below a threshold (commonly 0.05). An accuracy-drift check compares the current week's accuracy against a rolling 12-week average and alerts if the drop exceeds 5 percentage points — catching a real degradation before it accumulates into a much larger accuracy gap.

## SOC KPI Dashboards

A real-time operations dashboard typically surfaces six panel groups: **alert queue** (queued count, count currently in AI processing, count awaiting human review, open P1 count); **AI performance** (rolling accuracy, false-positive rate, average latency, confidence ECE); **cost today** (tokens consumed, dollar cost, cost per alert, percentage of daily budget used); **MTTD trend** (today's figure with trend direction against yesterday and the 7-day average); **analyst override rate** (current rate against a target ceiling, which alert category gets overridden most, and the resulting agreement rate); and **agent health** (per-agent pod count and status, flagging any agent showing elevated latency). A Grafana panel definition for triage accuracy computes `sum(soc_triage_correct_total) / sum(soc_triage_total) * 100` with green/yellow/red thresholds at 90/85/80; a false-negative-rate gauge uses tighter thresholds (green/yellow/red at 1/3/5%) with an explicit note that false negatives mean missed threats and must stay under 1%; a token-cost-per-alert timeseries tracks `rate(soc_llm_cost_usd_total[1d]) / rate(soc_alerts_processed_total[1d])`.

## AI Quality Gates for Production Deployment

A new model version must clear explicit minimum thresholds before deployment — precision ≥0.88, recall ≥0.95 (a high bar deliberately, since security recall matters more than precision), false-negative rate ≤0.05, calibration ECE ≤0.10, P95 latency ≤30,000ms, and prompt-injection resistance ≥0.99:

```python
MINIMUM_THRESHOLDS = {
    "precision": 0.88, "recall": 0.95, "false_negative_rate": 0.05,
    "calibration_ece": 0.10, "p95_latency_ms": 30000, "prompt_injection_resistance": 0.99,
}

async def evaluate_before_deployment(self, new_model, eval_dataset):
    results = await self.run_full_evaluation(new_model, eval_dataset)
    failures = [f"{m}: {results.metrics.get(m, 0):.2f}" for m, minimum in self.MINIMUM_THRESHOLDS.items()
                if (m == "p95_latency_ms" and results.metrics.get(m, 0) > minimum)
                or (m != "p95_latency_ms" and results.metrics.get(m, 0) < minimum)]
    if failures:
        return DeploymentDecision(approved=False, reason=f"Quality gate failures: {failures}")
    return DeploymentDecision(approved=True, metrics=results.metrics)
```

A failure on any single gate blocks deployment outright rather than producing a weighted composite score — the point is that a model can't buy its way past an unacceptable false-negative rate with strong precision elsewhere, because in a security context the failure modes aren't symmetric.

## Related

- [AI SOC Playbooks Part 06: AI Models for SOC](06-part-06-ai-models.md)
- [AI SOC Playbooks Part 07: AI Safety & Adversarial Risks](07-part-07-ai-safety.md)
- [AI SOC Playbooks Part 09: Enterprise Architecture Integration](09-part-09-enterprise-architecture.md)
