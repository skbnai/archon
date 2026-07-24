---
title: Orchestration Capability Maturity Model (CMM)
domain: agentic-systems
doc_type: guide
topic_id: capability-maturity-model
status: current
supersedes:
  - ../knowledge-docs/docs/workflow-orchestration/23-capability-maturity-model.md
date_created: 2026-07-24
last_reviewed: 2026-07-24
source_type: native-md
covers_version: "as of July 2026 — applies to enterprises using Temporal, Camunda, LangGraph, and agentic AI"
tags:
  - workflow-orchestration
  - maturity-model
  - cmm
  - transformation
  - enterprise
---

# Orchestration Capability Maturity Model (CMM)

> **As of July 2026.** Maturity model for enterprises progressing from manual processes to autonomous orchestrated AI systems.

This guide defines a five-level Capability Maturity Model (CMM) for workflow and AI orchestration. It tells you where you are today, what the next level looks like, what investment is required to get there, and where the risks are at each stage.

---

## Model Overview

**Capability Maturity Levels (Orchestration)**

- **Level 5: Autonomous** — Self-optimizing, multi-agent, learns from outcomes
- **Level 4: AI-Enabled** — Agents making decisions, governed AI, monitored quality
- **Level 3: Governed** — Standards, versioning, governance, compliance evidence
- **Level 2: Orchestrated** — Temporal or Camunda running defined workflows reliably
- **Level 1: Ad Hoc** — Manual processes, point-to-point integrations, no orchestration

Most enterprises in 2026 are at **Level 2–3**. Early movers are at **Level 4**. Level 5 is the emerging frontier.

---

## Level 1: Ad Hoc

### What You Have

- Manual processes managed via email, spreadsheets, and tribal knowledge
- Point-to-point integrations written per-project (REST calls, cron jobs, scripts)
- No observability — something broke? Check Slack first
- Recovery strategy: "Someone fixes it"
- No standard for how processes are defined, versioned, or communicated

### Symptoms of Level 1

| Symptom | Example |
| --- | --- |
| No workflow definition | "We process refunds manually — John knows the steps" |
| No durability | Cron job fails at 2am, nobody knows until morning |
| No versioning | "What changed last week?" "Not sure" |
| No observability | "How long does onboarding take?" "It varies" |
| High toil | Engineers spend 30%+ of time on operational fire-fighting |

### Investment to Reach Level 2

- Effort: 3–6 months
- Team: 2–4 engineers + a process analyst
- Technology: Choose Temporal or Camunda (see [Decision Matrix](./20-decision-matrix.md))
- Risk: Change management — teams accustomed to manual control resist orchestration

---

## Level 2: Orchestrated

### What You Have

- Workflows defined in code (Temporal) or BPMN (Camunda) for 50%+ of critical processes
- Durable execution: workflows survive crashes, retry on failure
- Basic monitoring: success/failure rates, duration
- Deployment: workflows deployed via CI/CD
- Team capability: engineers can write and deploy workflows independently

### Example Architecture (Level 2)

```mermaid
graph TD
    A["Customer Request"]
    B["Temporal Workflow<br/>- Validate input<br/>- Charge payment<br/>- Send confirmation<br/>- Retry on failure"]
    C["Monitoring Dashboard<br/>Success/failure rate<br/>Latency metrics"]
    
    A --> B
    B --> C
    
    style A fill:#e3f2
    style B fill:#fff
    style C fill:#f3e5
```

### Key Capabilities at Level 2

- [ ] Durable execution for critical workflows
- [ ] Automated retry with configurable policies
- [ ] Basic audit trail (which workflows ran, succeeded/failed)
- [ ] CI/CD for workflow deployments
- [ ] On-call playbook for workflow failures

### Investment to Reach Level 3

- Effort: 3–6 months
- Team: Add governance/platform role
- Technology: Version control for all workflow artifacts, governance tooling
- Risk: Governance introduces friction — teams may bypass it under pressure

---

## Level 3: Governed

### What You Have

- Versioning for all workflow artifacts (code, BPMN, DMN tables, configuration)
- Formal approval process for workflow changes (change management)
- Compliance evidence available on demand (audit trail, decision history)
- Standards documented and enforced (naming conventions, retry policies, error handling)
- Rollback procedures tested and documented

### Governance Maturity Indicators

```python
# You know you're at Level 3 when you can answer all of these:
LEVEL_3_AUDIT_QUESTIONS = [
    "Which version of the refund workflow was running at 2pm on March 15?",
    "Who approved the last change to the underwriting decision table?",
    "How many times has this workflow been retried in the last 30 days?",
    "What is the SLA breach rate for the payment workflow?",
    "Show me the rollback procedure for a broken workflow deployment.",
]
```

### Example Architecture (Level 3)

```mermaid
graph TD
    A["Change Management<br/>CR-456: Update refund policy<br/>Approved by: Tech Lead, Risk Officer<br/>Deployed: 2026-07-10 14:00"]
    B["Temporal Workflows<br/>Versioned & Governed<br/>workflow: refund-approval-v2.3.1<br/>dmn: refund-policy-v1.8.0"]
    C["Compliance Evidence Store<br/>- Decision audit trail<br/>- Change request history<br/>- SLA compliance reports"]
    
    A --> B
    B --> C
    
    style A fill:#e3f2
    style B fill:#fff
    style C fill:#f3e5
```

### Investment to Reach Level 4

- Effort: 6–12 months
- Team: AI engineers, ML/LLM expertise, prompt engineering
- Technology: LangGraph or equivalent, LLM API integration, vector store for memory
- Risk: AI quality — agents may perform worse than deterministic rules on well-understood tasks

---

## Level 4: AI-Enabled

### What You Have

- LLM agents making decisions for ambiguous, complex, or novel cases
- AI quality measurement (human override rate, decision accuracy, drift detection)
- Governed AI: prompt versioning, model version pinning, A/B testing
- Human-in-the-loop for high-stakes decisions
- Multi-system orchestration: Temporal + LangGraph working together

### Decision Quality Metrics (Level 4)

```python
LEVEL_4_QUALITY_METRICS = {
    "human_override_rate": {
        "target": "<0.10",  # < 10% of agent decisions overridden by humans
        "alert_threshold": 0.15,
        "meaning": "If > 15%, agent quality has degraded",
    },
    "decision_consistency": {
        "target": ">0.92",  # same case → same decision ≥ 92% of time
        "measurement": "Send identical test cases weekly",
        "meaning": "Prompt drift or model change causes inconsistency",
    },
    "false_rejection_rate": {
        "target": "<0.05",  # < 5% of truly eligible applications rejected
        "measurement": "Sample rejected decisions, human-review a random subset",
        "meaning": "Core business quality metric",
    },
}
```

### Example Architecture (Level 4)

```mermaid
graph TD
    A["Customer Loan Application"]
    B["Temporal Workflow<br/>Process Governor"]
    C["Activity 1: Validate format"]
    D["Activity 2: Compliance Agent"]
    E["Activity 3: Underwriting Agent"]
    F["Activity 4: HITL gate"]
    G["Activity 5: Disburse or Reject"]
    H["LangGraph Agent<br/>Compliance"]
    I["LangGraph Agent<br/>Underwriting"]
    J["Human Approval<br/>if risk > medium"]
    K["AI Quality Dashboard<br/>Override rate: 4.2%<br/>Consistency: 95%<br/>Prompt: v3.1.2<br/>Model: claude-sonnet-4-6"]
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    D --> H
    E --> I
    F --> J
    B --> K
    
    style A fill:#e3f2
    style B fill:#fff
    style D fill:#fff
    style E fill:#fff
    style F fill:#fff
    style K fill:#f3e5
```

### Investment to Reach Level 5

- Effort: 12–24 months
- Team: Specialized multi-agent systems engineers, AI safety expertise
- Technology: A2A protocols, autonomous agent frameworks, reinforcement learning
- Risk: Autonomy introduces new failure modes that are harder to detect and correct

---

## Level 5: Autonomous

### What You Have

- Agents that proactively identify work, not just respond to requests
- Multi-agent systems that coordinate autonomously to achieve business goals
- Self-optimization: system learns from outcomes and adjusts prompts/tools/routing
- Self-healing: agents detect degradation and adapt without human intervention
- Continuous improvement loop: A/B testing of agent strategies runs perpetually

### Characteristics of Level 5

```
Level 5 behaviors:
  ✓ "Agent monitors loan portfolio and proactively flags concentration risk"
  ✓ "Agent A detects it needs information only Agent B has → calls Agent B"
  ✓ "System detects its override rate rising → triggers prompt review automatically"
  ✓ "Agent adjusts its tool-calling strategy based on last week's failure patterns"
```

### Level 5 Risk Factors

Level 5 is powerful and dangerous:

- **Autonomy amplifies errors**: A self-optimizing agent that drifts in the wrong direction can make thousands of wrong decisions before detection
- **Explainability degrades**: Self-modified agents may be harder to audit
- **Governance must be continuous**: Manual governance review cycles are insufficient at Level 5 — automated governance required

---

## Self-Assessment Tool

Rate your organization on each capability (0 = not present, 1 = partial, 2 = fully implemented):

```python
MATURITY_ASSESSMENT = {
    # Level 2 capabilities (min score: 8/10 to advance)
    "critical_workflows_orchestrated": 0,   # Are critical processes in Temporal/Camunda?
    "durable_execution": 0,                  # Do workflows survive restarts?
    "basic_monitoring": 0,                   # Success/failure/duration tracked?
    "cicd_for_workflows": 0,                 # Deployed via pipeline?
    "on_call_playbook": 0,                   # Recovery procedure documented?

    # Level 3 capabilities (min score: 10/12 to advance)
    "artifact_versioning": 0,               # All workflow artifacts versioned?
    "change_management": 0,                  # Formal approval process?
    "audit_trail": 0,                        # Compliance evidence available?
    "standards_documented": 0,              # Standards enforced?
    "rollback_procedures": 0,               # Tested rollback documented?
    "sla_measurement": 0,                   # SLA tracked and reported?

    # Level 4 capabilities (min score: 10/12 to advance)
    "llm_integration": 0,                   # Agents making decisions?
    "prompt_versioning": 0,                  # Prompts in registry with history?
    "ai_quality_metrics": 0,               # Override rate, consistency tracked?
    "hitl_for_high_risk": 0,               # Human gate for high-stakes decisions?
    "model_version_pinning": 0,            # Models pinned, upgrade process?
    "multi_system_orchestration": 0,       # Temporal + LangGraph coordinated?

    # Level 5 capabilities
    "proactive_agents": 0,                  # Agents initiate work without prompting?
    "multi_agent_coordination": 0,          # A2A patterns implemented?
    "self_optimization": 0,                  # System improves from outcomes?
    "automated_governance": 0,             # Governance checks automated?
}

def assess_level(scores: dict) -> int:
    l2_score = sum(scores[k] for k in list(scores.keys())[:5])
    l3_score = sum(scores[k] for k in list(scores.keys())[5:11])
    l4_score = sum(scores[k] for k in list(scores.keys())[11:17])
    l5_score = sum(scores[k] for k in list(scores.keys())[17:])

    if l2_score < 8:
        return 1
    if l3_score < 10:
        return 2
    if l4_score < 10:
        return 3
    if l5_score < 6:
        return 4
    return 5
```

---

## Investment Summary

| Level | Timeline | Team Size | Primary Technology | Key Risk |
| --- | --- | --- | --- | --- |
| 1 → 2 | 3–6 months | 2–4 engineers | Temporal or Camunda | Change management |
| 2 → 3 | 3–6 months | +1 platform/governance | Governance tooling, audit store | Governance friction |
| 3 → 4 | 6–12 months | +2 AI engineers | LangGraph, LLM APIs, vector store | AI quality degradation |
| 4 → 5 | 12–24 months | +3 specialists | A2A, autonomous frameworks | Amplified failures |

---

## Typical Enterprise Journey: Financial Services

```
2023 (Level 1):
  Manual loan processing. 14 days average cycle time.
  No workflow system. Processing tracked in spreadsheets.

2024 (Level 2):
  Deployed Temporal for loan application processing.
  Cycle time: 6 days. Retries/failures automated.
  Manual compliance and underwriting decisions.

2025 (Level 3):
  Full governance: DMN rules versioned, change management implemented.
  Audit trail satisfies regulatory examination.
  Prompt registry created (anticipating Level 4).

2026 H1 (Level 4):
  LangGraph agents handle ambiguous cases (35% of applications).
  HITL gate for amounts > $100K.
  AI quality dashboard live. Override rate: 6%.
  Cycle time: 2 days.

2027 target (Level 4+):
  Multi-agent: credit, compliance, underwriting agents coordinated.
  Proactive portfolio monitoring agent.
  Exploring Level 5 self-optimization.
```

---

## Related

[Enterprise Governance Model](./18-enterprise-governance-model.md) · [Reference Architectures](./19-reference-architectures.md) · [Decision Matrix](./20-decision-matrix.md) · [Human-in-the-Loop Architectures](./human-in-the-loop-architectures)
