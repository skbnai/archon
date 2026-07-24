---
title: Enterprise Governance Model
domain: agentic-systems
doc_type: guide
topic_id: enterprise-governance-model
status: current
supersedes:
  - ../knowledge-docs/docs/workflow-orchestration/18-enterprise-governance-model.md
date_created: 2026-07-24
last_reviewed: 2026-07-24
source_type: native-md
covers_version: "as of July 2026 — applies to Temporal 1.x, Camunda 8, LangGraph 1.2.8, Claude claude-sonnet-4-6"
tags:
  - workflow-orchestration
  - governance
  - compliance
  - versioning
  - enterprise
---

# Enterprise Governance Model

> **As of July 2026.** Framework applies to Temporal 1.x, Camunda 8.x, LangGraph 1.2.8, Claude claude-sonnet-4-6 and equivalent.

This guide designs a governance framework for orchestrating with Temporal, Camunda, LangGraph, and Claude together in an enterprise context. It covers versioning, approval workflows, audit architecture, compliance evidence, rollback procedures, and access control.

---

## Why Governance Is Harder for Agentic Systems

Traditional workflow governance was straightforward: version the BPMN file, get sign-off, deploy. Rollback meant deploying the previous file.

Agentic systems introduce three new governance challenges:

1. **Probabilistic decisions**: The same workflow with a different prompt version may produce different outcomes — even on identical inputs
2. **Multiple artifact types**: You now version workflows, prompts, models, tools, and business rules — each with its own change velocity
3. **Cascading impact**: A prompt change might affect hundreds of downstream decisions before anyone notices

**Governance Scope in Agentic Systems**

| Artifact | Change Velocity | Owner |
|----------|-----------------|-------|
| Temporal workflows / Camunda BPMN | Slow | Platform team |
| LangGraph agent graphs | Medium | AI engineers |
| **Prompt templates** | **Fast** | **Prompt engineers** |
| Claude model versions | Controlled by Anthropic | External |
| MCP tool definitions | Medium | Platform team |
| DMN decision tables | Slow | Business analysts |
| Business rule policies | Slow | Compliance team |

Each has a different owner, change velocity, and risk profile. The governance model must handle all of them.

---

## Versioning Strategy

### Semantic Versioning for All Artifacts

```
Format: MAJOR.MINOR.PATCH

MAJOR: Breaking change — existing workflows using this version will behave differently
       Examples: model upgrade (Claude 3 → Claude claude-sonnet-4-6), prompt intent change,
                 tool API breaking change

MINOR: New capability — backwards compatible, no behavior change for existing invocations
       Examples: new tool added, new prompt path for an edge case, new DMN rule for new country

PATCH: Bug fix or clarification — no semantic change
       Examples: prompt typo fix, logging improvement, error message clarification
```

### Prompt Versioning

Prompts are first-class versioned artifacts — not strings in config files.

```python
# prompt_registry.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PromptVersion:
    prompt_id: str
    version: str           # "2.1.3"
    content: str
    model_constraint: str  # "claude-sonnet-4-6" — which model this was tested with
    author: str
    approved_by: str
    approved_at: datetime
    test_coverage: float   # % of test cases passing
    rollout_percentage: int  # % of traffic using this version

class PromptRegistry:
    def get_active(self, prompt_id: str, context: dict) -> PromptVersion:
        """Returns the active prompt version, respecting rollout percentages."""
        versions = self.db.get_active_versions(prompt_id)

        # Sort by rollout: newer version gets its percentage, rest on stable
        for version in versions:
            if self._should_use(version, context):
                return version

        return self.db.get_stable(prompt_id)

    def _should_use(self, version: PromptVersion, context: dict) -> bool:
        """Canary rollout: percentage of requests use the new version."""
        import hashlib
        hash_val = int(hashlib.md5(context.get("run_id", "").encode()).hexdigest(), 16)
        return (hash_val % 100) < version.rollout_percentage

prompt_registry = PromptRegistry()

# Usage in agent — always fetch from registry, never hardcode
@activity.defn
async def run_underwriting_agent(application_id: str) -> dict:
    prompt = prompt_registry.get_active("underwriting-decision", {"run_id": application_id})
    agent = build_agent(system_prompt=prompt.content)
    return await agent.run(application_id)
```

### Model Version Pinning

```python
# model_config.py — centrally managed, change requires approval
MODEL_ASSIGNMENTS = {
    "underwriting": {
        "model": "claude-sonnet-4-6",
        "pinned": True,  # Do not auto-upgrade
        "approved_by": "Risk Committee",
        "approved_at": "2026-06-15",
        "review_date": "2026-12-15",  # When to re-evaluate
    },
    "customer-support": {
        "model": "claude-haiku-4-5-20251001",  # Cost-optimized
        "pinned": False,  # Can take minor model updates automatically
        "max_model_version": "claude-haiku-4-5-*",  # Wildcard for patch updates only
    },
}
```

---

## Approval Workflows by Change Type

Different changes carry different risk — route them accordingly.

| Change Type | Required Approval | SLA | Deployment Gate |
| --- | --- | --- | --- |
| PATCH: prompt typo fix | Tech lead | 4h | Staging test pass |
| MINOR: new tool added | Tech lead + product | 24h | Integration test pass + 1h canary |
| MAJOR: prompt intent change | Tech lead + product + risk | 48h | A/B test + risk sign-off |
| Model upgrade | CTO + Risk Committee | 1 week | Full eval suite + 24h canary |
| New workflow deployment | EA board | 5 days | Security review + full staging |
| Emergency change | Senior tech lead | 2h | Post-deployment audit required |

### Change Request Process

```python
@dataclass
class ChangeRequest:
    change_id: str
    artifact_type: str     # "prompt" | "model" | "workflow" | "tool" | "policy"
    artifact_id: str
    current_version: str
    proposed_version: str
    change_type: str       # "major" | "minor" | "patch"
    description: str
    justification: str
    risk_assessment: str
    test_results: dict
    requester: str
    approvers_required: list[str]
    approvals_received: list[dict]
    status: str            # "pending" | "approved" | "rejected" | "deployed" | "rolled_back"

async def submit_change_request(cr: ChangeRequest) -> str:
    cr.change_id = generate_id("CR")
    await cr_db.insert(cr)
    await notify_approvers(cr)
    await audit_log.record("change_request.submitted", cr)
    return cr.change_id

async def approve_change(change_id: str, approver: str, notes: str) -> None:
    cr = await cr_db.get(change_id)

    if approver not in cr.approvers_required:
        raise ValueError(f"{approver} not in required approvers for this change")

    cr.approvals_received.append({
        "approver": approver,
        "notes": notes,
        "approved_at": datetime.utcnow().isoformat(),
    })

    if len(cr.approvals_received) >= required_quorum(cr.change_type):
        cr.status = "approved"
        await deploy_change(cr)

    await cr_db.update(cr)
    await audit_log.record("change_request.approved", {"change_id": change_id, "approver": approver})
```

---

## Audit Architecture

Every consequential decision in the system needs a full audit trail: what happened, who approved it, what information was available, and what the outcome was.

### Decision Audit Record

```python
@dataclass
class DecisionAuditRecord:
    # Identity
    decision_id: str
    workflow_id: str
    workflow_version: str

    # What version of each artifact was active
    prompt_id: str
    prompt_version: str
    model_id: str
    tool_versions: dict[str, str]

    # What the agent saw
    input_data: dict
    retrieved_context: dict  # what memory/RAG retrieved

    # What the agent did
    tool_calls: list[dict]
    reasoning_trace: str  # agent's chain of thought
    proposed_decision: str

    # Human review (if applicable)
    human_reviewer: Optional[str]
    human_decision: Optional[str]
    human_notes: Optional[str]
    human_reviewed_at: Optional[datetime]

    # Final outcome
    final_decision: str
    outcome_applied_at: datetime

    # Compliance
    regulatory_flags: list[str]
    audit_trail_hash: str  # hash of this entire record for tamper detection

async def record_decision(record: DecisionAuditRecord) -> None:
    record.audit_trail_hash = compute_hash(record)
    await audit_db.insert_immutable(record)

    # Emit to compliance reporting pipeline
    await compliance_stream.publish(record)
```

### Querying the Audit Trail

```python
async def get_decision_audit(workflow_id: str) -> dict:
    """Full audit trail for a single workflow execution."""
    return {
        "workflow": await workflow_db.get(workflow_id),
        "decisions": await audit_db.get_by_workflow(workflow_id),
        "human_approvals": await approval_db.get_by_workflow(workflow_id),
        "change_requests": await cr_db.get_active_at(workflow_id),  # what versions were live
        "timeline": build_timeline(workflow_id),
    }

async def compliance_report(date_from: date, date_to: date, artifact_id: str) -> dict:
    """For regulatory examination: all decisions made using a specific prompt/model version."""
    decisions = await audit_db.query(
        artifact_id=artifact_id,
        date_from=date_from,
        date_to=date_to,
    )
    return {
        "artifact_id": artifact_id,
        "period": f"{date_from} to {date_to}",
        "total_decisions": len(decisions),
        "decisions_by_outcome": group_by(decisions, "final_decision"),
        "human_override_rate": compute_override_rate(decisions),
        "decisions": decisions,
    }
```

---

## Rollback Procedures

### Workflow Rollback (Temporal)

Running workflow instances continue with their original version. New instances start on the previous version.

```python
from temporalio.client import Client, WorkflowHandle

async def rollback_workflow_version(workflow_type: str, target_version: str) -> None:
    """Point new workflow instances at a previous version."""

    # Update the version registry — new instances will pick up the previous version
    await version_registry.set_active(workflow_type, target_version)

    # Optional: drain in-flight workflows
    client = await Client.connect("localhost:7233")
    active = await client.list_workflows(f"WorkflowType='{workflow_type}' AND Status='Running'")

    print(f"Rolling back {workflow_type} to {target_version}")
    print(f"  New instances: will use {target_version} immediately")
    print(f"  In-flight ({len(active)} workflows): will complete with their original version")

    await audit_log.record("rollback.initiated", {
        "workflow_type": workflow_type,
        "rolled_back_to": target_version,
        "in_flight_count": len(active),
    })
```

### Prompt Rollback (Immediate)

```python
async def rollback_prompt(prompt_id: str, target_version: str, reason: str) -> None:
    """Roll back a prompt to a previous version — effective on next invocation."""

    current = await prompt_registry.get_active_version(prompt_id)

    # Set previous version as active (rollout=100%)
    await prompt_registry.set_active(prompt_id, target_version, rollout_percentage=100)

    # Invalidate any caches
    await cache.invalidate_pattern(f"prompt:{prompt_id}:*")

    await audit_log.record("prompt.rollback", {
        "prompt_id": prompt_id,
        "from_version": current.version,
        "to_version": target_version,
        "reason": reason,
    })

    print(f"Prompt {prompt_id} rolled back from {current.version} → {target_version}")
    print("Effective immediately — no redeploy required")
```

---

## Access Control Model

| Role | Read | Propose | Approve | Deploy | Emergency |
|------|------|---------|---------|--------|-----------|
| Engineer | ✓ | ✓ | | | |
| Senior Engineer | ✓ | ✓ | PATCH | | |
| Tech Lead | ✓ | ✓ | MINOR | PATCH | |
| Product Owner | ✓ | ✓ | MINOR | | |
| Risk Officer | ✓ | | MAJOR | | |
| Enterprise Architect | ✓ | ✓ | All | MINOR | |
| CTO | ✓ | ✓ | All | MAJOR | ✓ |

```python
from enum import Enum

class Role(Enum):
    ENGINEER = "engineer"
    SENIOR_ENGINEER = "senior_engineer"
    TECH_LEAD = "tech_lead"
    PRODUCT_OWNER = "product_owner"
    RISK_OFFICER = "risk_officer"
    ENTERPRISE_ARCHITECT = "enterprise_architect"
    CTO = "cto"

CHANGE_APPROVERS = {
    "patch": [Role.TECH_LEAD, Role.ENTERPRISE_ARCHITECT, Role.CTO],
    "minor": [Role.ENTERPRISE_ARCHITECT, Role.CTO],
    "major": [Role.RISK_OFFICER, Role.CTO],
    "emergency": [Role.CTO],
}

def can_approve(role: Role, change_type: str) -> bool:
    return role in CHANGE_APPROVERS.get(change_type, [])
```

---

## Governance Checklist (Per Deployment)

Before any MAJOR change ships to production:

- [ ] Change request submitted and approved by required quorum
- [ ] All artifact versions documented (prompt, model, tools, workflow)
- [ ] Test suite run against new version — coverage ≥ 85%
- [ ] Canary deployed at 5% traffic for minimum 1 hour
- [ ] Canary metrics reviewed (error rate, decision distribution, latency)
- [ ] Rollback procedure tested in staging
- [ ] Audit trail verified end-to-end in staging
- [ ] Compliance team notified (if regulatory scope)
- [ ] On-call engineer briefed on rollback procedure
- [ ] Post-deployment monitoring dashboard confirmed live

---

## Related

[Human-in-the-Loop Architectures](./12-human-in-the-loop-architectures.md) · [Security Architecture](./17-workflow-orchestration-security-architecture.md) · [Observability Framework](./16-observability-framework.md) · [Capability Maturity Model](./23-capability-maturity-model.md)
