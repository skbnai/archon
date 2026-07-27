---
title: "AI Authorization Architecture"
doc_type: guide
domain: trust
status: current
topic_id: ai-authorization
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part07_AI_Authorization.md]
tags: [ai-security, authorization, deepmind, cedar, opa]
covers_version: "as of 2026"
---

RBAC vs. ABAC vs. PBAC vs. ReBAC for autonomous agents, Cedar and OPA/Rego policy patterns, OpenFGA relationship-based authorization, and risk-adaptive access control.

## Authorization Challenges for Autonomous Agents

Authorization for autonomous AI agents is fundamentally different from authorization for human users or traditional software services. Human authorization is relatively static — a user's role changes infrequently and their access needs are well-characterized. Agent authorization is dynamic — the same agent type may need entirely different permissions depending on the specific task, the user it is acting for, the current risk context, and the phase of a multi-step workflow.

**Authorization principle for agents:** Authorization decisions must be goal-aware, context-sensitive, risk-adaptive, and reversibility-conscious. A permission granted for reading data should not automatically extend to writing data, even if both are within a traditional role's scope. Each action requires independent evaluation against current context.

## Authorization Model Comparison

| Model | Decision Based On | AI Agent Fit | Key Limitation |
|---|---|---|---|
| RBAC | User role membership | Poor | Roles too coarse; cannot express task-specific permissions |
| ABAC | Attributes of subject, resource, environment | Moderate | Does not capture agent goal state or action intent |
| PBAC (Policy-Based) | Explicit policy rules over context | Good | Policy authoring complexity; performance at scale |
| ReBAC (Relationship-Based) | Entity relationship graph (Zanzibar) | Moderate | Relationships don't capture temporal or goal context |
| Capability-Based | Possession of unforgeable capability token | Good | Token management complexity; revocation challenges |
| Risk-Adaptive | Real-time risk score drives access level | Excellent | Risk model quality determines security efficacy |
| Goal-Aware (emerging) | Agent goal + context + risk | Excellent | No production frameworks exist yet (2026) |

## Cedar: Policy Language for AI Agent Authorization

AWS Cedar, open-sourced in 2023, is the most suitable general-purpose policy language for AI agent authorization. Cedar is designed for: fast evaluation (policies evaluate in sub-millisecond time), strong typing (prevents policy authoring errors), formal verification (policy correctness can be proven), and human readability. Cedar is used by Amazon Verified Permissions and Amazon Bedrock AgentCore.

**Cedar policy examples for AI agents:**

```cedar
// Allow finance analyst agent to read financial reports for tasks delegated by finance team
permit(
  principal in AgentType::"finance-analyst",
  action == Action::"read",
  resource in DataScope::"financial-reports"
) when {
  principal.task_delegated_by in Group::"finance-team" &&
  principal.risk_score < 50 &&
  resource.classification <= "CONFIDENTIAL" &&
  context.time_of_day.hour >= 6 &&
  context.time_of_day.hour <= 20
};

// Forbid any agent from deleting records with external effects
forbid(
  principal is AgentInstance,
  action in [Action::"delete", Action::"purge"],
  resource
) unless {
  principal.human_approval_received == true &&
  principal.approval_for_resource == resource.id &&
  context.approval_timestamp > now() - duration("15m")
};
```

## OPA/Rego for Complex AI Agent Policies

Open Policy Agent (OPA) with the Rego policy language provides more expressive power than Cedar for complex, context-rich authorization decisions. OPA is particularly suitable for behavioral policy evaluation where the authorization decision depends on patterns across the agent's action history.

**OPA integration architecture:**

- **Sidecar Pattern:** OPA runs as a sidecar container in the agent pod; policy decisions made via local HTTP call (&lt;5ms).
- **Bundle Distribution:** policy bundles distributed via the OPA Bundle API; agents always run the latest approved policies.
- **External Data:** OPA integrates with the agent context store (action history, risk scores) via the External Data API.
- **Decision Logging:** all OPA decisions logged to a central decision log with full input/output; enables policy auditing.
- **Partial Evaluation:** pre-compile policies for known agent types to reduce per-request evaluation overhead.

## OpenFGA / Zanzibar for Relationship-Based Authorization

OpenFGA (Open Fine-Grained Authorization), based on Google's Zanzibar system, provides relationship-based access control (ReBAC) with highly scalable, low-latency authorization. For AI agents, OpenFGA is particularly valuable for authorization decisions that depend on organizational relationships: "can this agent access resources owned by the user who delegated this task?"

**ReBAC for agent delegation — example OpenFGA tuples:**

```
# Alice owns the finance report
user:alice | owner | document:finance-report-q2

# Alice delegates to finance-analyst agent
agent:finance-analyst-sess-a7f2b1 | delegate_of | user:alice

# ReBAC check: can agent read document alice owns?
# Resolution: agent -> delegate_of -> alice -> owner -> document -> can read
check(agent:finance-analyst-sess-a7f2b1, reader, document:finance-report-q2) = true
```

## Risk-Adaptive Authorization

Risk-adaptive authorization (RAA) adjusts the authorization threshold dynamically based on real-time risk signals. For AI agents, risk signals include: current behavioral anomaly score, cumulative session risk, environmental threat indicators, time-of-day factors, and sensitivity of the requested resource.

| Risk Level | Score Range | Access Controls | Human Oversight |
|---|---|---|---|
| Very Low (Routine) | 0-20 | Automatic approval; minimal logging | Random sampling audit |
| Low (Normal) | 21-40 | Automatic approval; standard logging | Exception-based review |
| Medium (Elevated) | 41-60 | Automatic approval; enhanced logging; behavioral alert | Alert to SOC; no blocking |
| High (Concerning) | 61-80 | Require additional attestation; gate on sensitive actions | Human review required for flagged actions |
| Very High (Suspicious) | 81-95 | Block all non-read actions; human must authorize each write | Active monitoring; SOC escalation |
| Critical (Quarantine) | 96-100 | Block all actions; agent quarantined | Immediate incident response |

## Related

- [Identity for AI Agents](10-identity-for-ai-agents.md)
- [Memory Governance](12-memory-governance.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
