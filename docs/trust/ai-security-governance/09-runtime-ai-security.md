---
title: "Runtime AI Security"
doc_type: guide
domain: trust
status: current
topic_id: runtime-ai-security
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part05_Runtime_AI_Security.md]
tags: [ai-security, runtime-security, deepmind, circuit-breakers]
covers_version: "as of 2026"
---

Execution interception, behavioral monitoring, approval gates, circuit breakers, and checkpoint/rollback architecture for live AI agent sessions — with a direct mapping to Kubernetes admission-control patterns.

## Runtime Security Paradigm for AI Agents

Runtime security for AI agents addresses the class of threats that emerge during live execution and cannot be prevented through static analysis, pre-deployment testing, or policy configuration alone. Runtime threats include: behavioral drift from baseline, adversarial manipulation of in-progress sessions, cascading failures in multi-agent workflows, and emergent harmful patterns from combinations of individually safe actions.

**Runtime security principle:** No pre-deployment control is sufficient. The threat surface expands during execution as the agent accumulates context, interacts with external systems, and makes decisions with compounding consequences. Runtime controls are not a backup — they are an essential primary defense layer.

## Execution Interception Architecture

**The action interception pipeline.** Every agent action must pass through an interception pipeline before execution. The pipeline evaluates actions synchronously (for low-latency blocking decisions) and asynchronously (for complex behavioral analysis). The architecture mirrors Kubernetes admission controllers but operates on semantic agent actions rather than API server requests.

| Stage | Operation | Blocking? | Max Latency | Action on Reject |
|---|---|---|---|---|
| Schema Validation | Validate action format and parameter types | Yes | &lt;1ms | Return error to agent |
| Authorization Check | Verify action is within capability scope | Yes | &lt;5ms | Return DENY; log |
| Hard Constraint Check | Check against absolute prohibitions | Yes | &lt;5ms | Block + alert SOC |
| Semantic Risk Score | Score action intent and impact | Conditional | 50ms | Queue for human review if high-risk |
| Behavioral Pattern Check | Compare to expected action distribution | Conditional | 200ms | Alert + optional block |
| Rate Limit Check | Enforce per-action-type rate limits | Yes | &lt;1ms | Throttle; alert if sustained |
| Reversibility Assessment | Score irreversibility of action | Conditional | 10ms | Require human approval if irreversible |
| Async Audit Log | Record action and all evaluation results | No | Async | N/A |

## Behavioral Monitoring

**Baseline and drift detection.** Behavioral monitoring requires establishing a baseline of expected agent behaviour for each agent type, task category, and operational context. Drift detection then continuously compares live behaviour against the baseline using statistical methods. Significant drift triggers alerts and may trigger automatic containment.

**Behavioral metrics:**

- **Action Type Distribution:** frequency distribution of tool calls by type (read vs. write vs. external call).
- **API Endpoint Distribution:** distribution of API endpoints accessed by the agent.
- **Data Volume:** volume of data read and written per session; anomalous spikes indicate potential exfiltration.
- **External Call Rate:** rate and diversity of calls to external services.
- **Error Rate:** frequency of authorization denials, tool errors, and exception conditions.
- **Action Sequence Entropy:** statistical entropy of action sequences; low entropy may indicate a scripted/automated attack.
- **Goal Consistency Score:** semantic similarity between agent actions and the stated task goal.
- **Resource Acquisition Rate:** rate at which the agent requests new permissions or capabilities.

## Approval Gates and Human-in-the-Loop Controls

**Approval gate design.** Approval gates pause agent execution at defined decision points and require human authorization before proceeding. Effective approval gate design balances safety (comprehensive coverage) against operational efficiency (low reviewer burden). Gates must be designed so that the reviewer has sufficient context to make a meaningful decision — not just a rubber stamp.

| Gate Type | Trigger Condition | Information Presented to Reviewer | SLA |
|---|---|---|---|
| Pre-action Gate | Action risk score > threshold | Action params, agent goal, prior actions, risk rationale | 5 minutes |
| Impact Gate | Potential impact > defined threshold (e.g., &gt;$10k, &gt;1000 records) | Impact estimate, action details, data affected | 15 minutes |
| Irreversibility Gate | Action reversibility score < threshold | Action details, consequences if not reversed, reversal procedure | 30 minutes |
| Novel Action Gate | Action type not in training baseline | Action details, similar historical actions, risk assessment | 15 minutes |
| Accumulated Risk Gate | Session cumulative risk score > threshold | Session summary, all prior actions, risk accumulation | Immediate |
| Policy Exception Gate | Action requires policy exception | Exception details, policy rationale, risk and alternatives | 1 hour |

**Reviewer experience:** Human approvers need purpose-built decision support tools, not raw log dumps. The approval UI must present: a clear statement of what the agent wants to do, why it believes this is necessary, what alternatives exist, what the consequences are, and a one-click approve/deny/modify workflow.

## Circuit Breakers and Kill Switches

**Circuit breaker patterns.** Circuit breakers automatically halt agent execution when detected conditions indicate potential misalignment, compromise, or impending harm. Unlike approval gates (which pause execution for human review), circuit breakers immediately terminate or quarantine the agent without human intervention.

| Circuit Breaker | Trigger | Action | Recovery |
|---|---|---|---|
| Hard Limit Breaker | Absolute policy violation detected | Immediate task termination | Manual human review required |
| Anomaly Breaker | Behavioral anomaly score exceeds critical threshold | Session pause; human notification | Human review and re-authorization |
| Cascade Breaker | Agent causing cascading failures in downstream systems | Agent isolation; downstream systems notified | Root cause analysis before re-enable |
| Rate Breaker | Request rate exceeds sustained abnormal threshold | Throttle to safe rate; alert | Automatic reset after observation period |
| Resource Breaker | Resource consumption exceeds quota | Pause execution; release resources | Automatic reset with quota increase approval |
| External Signal Breaker | Kill signal received from authorized principal | Immediate shutdown; state checkpoint | Manual authorization to restart |

## Checkpoint and Rollback Architecture

For long-running agent tasks, checkpoint and rollback capabilities enable recovery from detected issues without losing all prior work. Checkpointing captures: agent goal state, action history, memory state, acquired capabilities, and conversation context. Rollback restores a prior checkpoint and allows the agent to proceed with corrected instructions or modified constraints.

**Checkpoint triggers:**

- Time-based: checkpoint every N minutes for long-running tasks.
- Milestone-based: checkpoint at each defined task milestone or phase boundary.
- Risk-based: checkpoint before any action classified as high-risk or irreversible.
- Human-intervention: checkpoint immediately when human approval is requested.
- Anomaly-based: checkpoint when a behavioral anomaly is detected (enables forensic analysis).

**Comparison with Kubernetes admission controllers:**

| Concept | Kubernetes | AI Agent Equivalent |
|---|---|---|
| Admission Controller | Intercepts API server requests pre-admission | Action Interceptor intercepts agent actions pre-execution |
| Validating Webhook | Validates requests against policy; approve/reject | Policy Engine validates action semantics; approve/reject/queue |
| Mutating Webhook | Modifies requests to enforce policy (e.g., add labels) | Action Modifier adjusts action parameters to meet policy (e.g., reduce scope) |
| OPA Gatekeeper | Policy-as-code for K8s resources | OPA/Cedar policy engine for agent actions |
| Pod Security Policy | Restricts container capabilities | Execution Sandbox restricts agent OS capabilities |
| ResourceQuota | Limits resource consumption by namespace | Resource Quotas limit agent CPU, memory, API calls |
| NetworkPolicy | Controls pod network connectivity | Agent Network Policy controls egress to external endpoints |

## Related

- [AI Control Architecture](08-ai-control-architecture.md)
- [Identity for AI Agents](10-identity-for-ai-agents.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
