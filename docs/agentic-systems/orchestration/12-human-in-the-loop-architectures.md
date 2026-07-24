---
title: "Human-in-the-Loop Architectures"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: human-in-the-loop-architectures
supersedes: ["../knowledge-docs/docs/workflow-orchestration/12-human-in-the-loop-architectures.md"]
doc_type: guide
tags: ["workflow-orchestration", "hitl", "governance", "human-oversight", "agents"]
---

# Human-in-the-Loop Architectures

> **As of July 2026.** LangGraph 1.2.8 interrupt/resume; Temporal signal patterns; patterns apply to any agent framework.

This guide covers how to design modern human-in-the-loop (HITL) architectures where humans stay in genuine control as systems become more autonomous. The goal is not simple approval gates — it is **maintaining meaningful human agency** over consequential decisions.

---

## The Evolution of HITL

```
2015-2020: Binary approval gates
  Process runs → stop → human clicks "Approve" or "Reject" → continue

2021-2023: Risk-tiered routing
  Low risk → auto-approve
  Medium risk → one approver
  High risk → multiple approvers + senior review

2024-2026: Reasoning review + in-flight guidance
  Agent explains its thinking → human reviews the reasoning → approves the plan
  OR
  Human interrupts mid-execution → redirects the agent → agent adjusts and continues
```

The shift is from reviewing **outputs** to reviewing **reasoning**. An agent that produces the right answer via wrong reasoning is a risk — the next time the situation is slightly different, it may fail.

---

## HITL Placement Patterns

### Pattern 1: Pre-Flight Approval (Plan → Approve → Execute)

The agent plans, the human approves the plan, then execution is autonomous.

```python
# LangGraph with interrupt for plan approval
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import TypedDict, Optional

class WorkflowState(TypedDict):
    goal: str
    plan: Optional[list[str]]
    plan_approved: bool
    execution_results: list[str]
    final_answer: Optional[str]

def create_plan(state: WorkflowState) -> WorkflowState:
    plan = planner_llm.invoke(f"Create a step-by-step plan for: {state['goal']}")
    return {"plan": plan, "plan_approved": False}

def execute_plan(state: WorkflowState) -> WorkflowState:
    results = []
    for step in state["plan"]:
        result = executor.run(step)
        results.append(result)
    return {"execution_results": results}

def synthesize(state: WorkflowState) -> WorkflowState:
    answer = synthesizer_llm.invoke(str(state["execution_results"]))
    return {"final_answer": answer}

def should_execute(state: WorkflowState) -> str:
    return "execute" if state["plan_approved"] else "wait_for_approval"

graph = StateGraph(WorkflowState)
graph.add_node("plan", create_plan)
graph.add_node("execute", execute_plan)
graph.add_node("synthesize", synthesize)
graph.set_entry_point("plan")
graph.add_conditional_edges("plan", should_execute)
graph.add_edge("execute", "synthesize")
graph.add_edge("synthesize", END)

checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute"],  # pause before execution, wait for human
)

# Step 1: Run until interrupt
thread_id = "workflow-001"
config = {"configurable": {"thread_id": thread_id}}
state = app.invoke({"goal": "Process refund for customer C-123"}, config)

# At this point: app is paused at "execute" node
# Human reviews state["plan"] via a UI/API
print("Plan for approval:", state["plan"])

# Step 2: Human approves (e.g., via API endpoint)
app.update_state(config, {"plan_approved": True})

# Step 3: Resume execution
final_state = app.invoke(None, config)  # None = resume from checkpoint
```

### Pattern 2: Inline Approval Gate (Execute → Gate → Continue)

The agent executes steps, pauses at a gate requiring human sign-off, then continues.

```python
# Temporal signal-based approval
from temporalio import workflow, activity
from temporalio.client import Client
import asyncio

@workflow.defn
class LoanApprovalWorkflow:
    def __init__(self):
        self._approval_received = False
        self._approved = False
        self._approver_notes = ""

    @workflow.signal
    async def receive_approval(self, approved: bool, notes: str = "") -> None:
        self._approval_received = True
        self._approved = approved
        self._approver_notes = notes

    @workflow.run
    async def run(self, application_id: str) -> dict:
        # Phase 1: automated analysis
        analysis = await workflow.execute_activity(
            analyze_loan_application,
            application_id,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # Phase 2: human approval gate
        # Notify approvers via email/Slack/Teams
        await workflow.execute_activity(
            notify_approvers,
            {"application_id": application_id, "analysis": analysis},
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Wait for human signal — timeout after 48 hours
        try:
            await workflow.wait_condition(
                lambda: self._approval_received,
                timeout=timedelta(hours=48),
            )
        except asyncio.TimeoutError:
            return {"status": "expired", "reason": "No approval within 48 hours"}

        if not self._approved:
            return {"status": "rejected", "notes": self._approver_notes}

        # Phase 3: execute approved decision
        result = await workflow.execute_activity(
            disburse_loan,
            application_id,
            start_to_close_timeout=timedelta(minutes=10),
        )
        return {"status": "approved", "disbursement": result}

# Approver sends signal from UI
client = await Client.connect("localhost:7233")
handle = client.get_workflow_handle("loan-APP-456")
await handle.signal("receive_approval", True, "Looks good — DTI within limits")
```

### Pattern 3: Reasoning Review (Show the Thinking)

The human reviews not the output but the agent's chain of reasoning before it acts.

```python
def format_reasoning_for_review(state: WorkflowState) -> dict:
    """Structure agent reasoning for human consumption."""
    return {
        "goal": state["goal"],
        "tools_used": [
            {
                "tool": call["name"],
                "input": call["input"],
                "output_summary": summarize(call["output"]),
                "why": call.get("reasoning", ""),
            }
            for call in state["tool_calls"]
        ],
        "proposed_action": state["proposed_action"],
        "confidence": state["confidence_score"],
        "risks_identified": state["identified_risks"],
        "alternatives_considered": state["alternatives"],
    }

# Human reviewer sees:
# - What the agent looked at (tools + inputs)
# - What the agent found (output summaries)
# - Why it made each call (reasoning trace)
# - What it proposes to do (action + justification)
# - What risks it identified
# - What alternatives it considered and rejected
```

**Why this matters**: An agent that proposes the right action for the wrong reason is a latent risk. Reasoning review catches this. Output review cannot.

### Pattern 4: In-Flight Guidance (Interrupt → Redirect → Resume)

A human interrupts an executing agent, provides additional context, and the agent adjusts without restarting.

```python
# LangGraph: inject human guidance mid-execution
from langgraph.types import Command, interrupt

def research_step(state: WorkflowState) -> WorkflowState:
    # Execute some research
    findings = research_tool.invoke(state["query"])

    # Interrupt: ask human for guidance before proceeding
    human_guidance = interrupt({
        "question": "The research found conflicting data. Which source should I prioritize?",
        "option_a": "Academic sources (peer-reviewed, slower)",
        "option_b": "Industry reports (more current, less rigorous)",
        "findings_so_far": findings,
    })

    # Agent incorporates guidance and continues
    if human_guidance["choice"] == "A":
        state["source_preference"] = "academic"
    else:
        state["source_preference"] = "industry"

    return {"findings": findings, "source_preference": state["source_preference"]}

# Human sends response via update_state
app.update_state(
    config,
    {"human_response": {"choice": "B", "notes": "We need current data for this report"}},
    as_node="research_step",
)
```

---

## Approval Routing and SLAs

### Risk-Based Routing Matrix

```python
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

APPROVAL_ROUTING = {
    RiskLevel.LOW: {
        "approvers": [],  # auto-approve
        "sla_hours": 0,
        "quorum": 0,
    },
    RiskLevel.MEDIUM: {
        "approvers": ["team_lead"],
        "sla_hours": 4,
        "quorum": 1,
    },
    RiskLevel.HIGH: {
        "approvers": ["team_lead", "risk_officer"],
        "sla_hours": 24,
        "quorum": 2,  # both must approve
    },
    RiskLevel.CRITICAL: {
        "approvers": ["team_lead", "risk_officer", "vp"],
        "sla_hours": 4,  # tight SLA because it's critical
        "quorum": 2,  # any
        "notify_all": True,
    },
}

def assess_risk(decision: dict) -> RiskLevel:
    amount = decision.get("amount", 0)
    is_irreversible = decision.get("irreversible", False)

    if is_irreversible and amount > 100_000:
        return RiskLevel.CRITICAL
    elif amount > 50_000 or is_irreversible:
        return RiskLevel.HIGH
    elif amount > 5_000:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
```

### SLA Escalation

```python
@workflow.defn
class ApprovalWithEscalation:
    @workflow.run
    async def run(self, request: ApprovalRequest) -> ApprovalResult:
        routing = APPROVAL_ROUTING[request.risk_level]

        # Primary approvers
        await send_approval_request(routing["approvers"])

        try:
            result = await workflow.wait_condition(
                lambda: self._approval_received,
                timeout=timedelta(hours=routing["sla_hours"]),
            )
        except asyncio.TimeoutError:
            # Escalate to next level
            await send_escalation_alert(routing["approvers"] + ["director"])

            result = await workflow.wait_condition(
                lambda: self._approval_received,
                timeout=timedelta(hours=2),  # tight escalation window
            )

        return self._approval_result
```

---

## Audit and Accountability

Every human decision in the loop must be recorded with: who, what, when, why, and with what context.

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HumanDecisionRecord:
    decision_id: str
    workflow_id: str
    approver_id: str
    approver_role: str
    decision: str  # "approved" | "rejected" | "redirected"
    notes: str
    context_shown: dict    # exactly what the human saw
    context_version: str   # hash of context — proves what was shown
    timestamp: datetime
    ip_address: str
    session_id: str

async def record_human_decision(record: HumanDecisionRecord) -> None:
    # Write to immutable audit log (append-only)
    await audit_db.insert(record)
    # Emit event for compliance reporting
    await event_bus.publish("human.decision.recorded", record)
```

**Key principle**: The audit record captures the **context shown** to the human — not just their decision. This proves that the human had the relevant information when they decided. Without this, the audit trail cannot support regulatory examination.

---

## UX Principles for HITL Interfaces

1. **Show the reasoning, not just the proposal**: Humans cannot meaningfully review what they don't understand
2. **Surface the risk explicitly**: Make the risk level, reversibility, and SLA visible before asking for a decision
3. **Provide guided redirection**: When a human wants to change direction, give them structured options — not a free-text box
4. **Log what was shown**: The decision is only meaningful if you can prove what information the human had
5. **Time-box the request**: Show the SLA countdown. "Expires in 3h 47m" creates appropriate urgency
6. **Mobile-friendly approvals**: High-stakes decisions will often need approval from a phone — design for it

---

## Training Humans to Work with Agents

A common HITL failure mode is not the technology — it is humans rubber-stamping AI decisions without genuine review. This is sometimes called "automation bias": humans trust the machine and stop applying critical judgment.

Countermeasures:

1. **Blind calibration tests**: Periodically insert known-wrong AI decisions into the approval queue. Track how often reviewers catch them. Use this to measure and improve review quality, not to punish reviewers.

2. **Reasoning-first display**: Show the agent's reasoning before showing the proposed decision. Reviewers who see the answer first are anchored to it; reviewers who see the reasoning first form independent judgment.

3. **Time-pressure awareness**: Approval queues with SLA countdowns create time pressure that degrades review quality. Design UX to surface the most impactful decisions first — not just the most urgent.

4. **Structured disagreement**: When a reviewer overrides an agent decision, require them to select a reason category (not just free text). These categories become a labeled dataset for improving the agent.

```python
class OverrideReason(Enum):
    MISSING_CONTEXT = "missing_context"       # agent didn't have info the reviewer has
    INCORRECT_POLICY = "incorrect_policy"     # agent misapplied the rule
    HALLUCINATION = "hallucination"            # agent made up a fact
    EDGE_CASE = "edge_case"                   # novel situation agent wasn't trained for
    BUSINESS_JUDGMENT = "business_judgment"   # technically correct but strategically wrong
    OTHER = "other"

async def record_override(
    decision_id: str,
    reviewer_id: str,
    override_decision: str,
    reason: OverrideReason,
    notes: str,
) -> None:
    await audit_db.record_override(decision_id, reviewer_id, override_decision, reason, notes)

    # Route to the right improvement process
    if reason in (OverrideReason.HALLUCINATION, OverrideReason.INCORRECT_POLICY):
        await flag_for_prompt_review(decision_id, reason)
    elif reason == OverrideReason.MISSING_CONTEXT:
        await flag_for_tool_addition(decision_id, notes)
```

---

## Appeals Process

Humans approved by the system can be wrong too. An appeals process allows a subsequent human reviewer to challenge an approved decision — critical for high-stakes or regulated contexts.

```python
@workflow.defn
class AppealsWorkflow:
    @workflow.run
    async def run(self, original_decision_id: str, appeal_reason: str) -> dict:
        original = await workflow.execute_activity(
            get_decision_record, original_decision_id,
            start_to_close_timeout=timedelta(seconds=10),
        )

        # Route appeals to a different (more senior) approver pool
        await workflow.execute_activity(
            notify_appeals_reviewers,
            {
                "original_decision": original,
                "appeal_reason": appeal_reason,
                "appeal_deadline": (datetime.utcnow() + timedelta(hours=48)).isoformat(),
            },
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Wait for appeals decision
        await workflow.wait_condition(
            lambda: self._appeals_decision_received,
            timeout=timedelta(hours=48),
        )

        if self._appeals_upheld:
            return {"outcome": "original_decision_upheld", "notes": self._appeals_notes}
        else:
            # Reverse the original decision and apply correction
            await workflow.execute_activity(
                reverse_decision, original_decision_id,
                start_to_close_timeout=timedelta(minutes=5),
            )
            return {"outcome": "decision_reversed", "notes": self._appeals_notes}
```

**Audit**: Every appeal and its outcome becomes part of the original decision's audit trail — regulators expect to see the full lifecycle of a contested decision.

---

## Related

[Enterprise Governance Model](./enterprise-governance-model) · [A2A Orchestration Patterns](./a2a-orchestration-patterns) · [Security Architecture](./security-architecture) · [Temporal Deep Dive](./temporal-deep-dive)
