---
title: "AI Planning vs. Workflow Engines"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: ai-planning-vs-workflow-engines
supersedes: ["../knowledge-docs/docs/workflow-orchestration/14-ai-planning-vs-workflow-engines.md"]
doc_type: guide
tags: ["workflow-orchestration", "ai-planning", "workflow-engines", "agents", "htn"]
---

# AI Planning vs. Workflow Engines

> **As of July 2026.** Classical AI planning concepts are timeless; LangGraph 1.2.8 used for planning-adjacent patterns.

This guide compares classical AI planners with workflow/orchestration engines and explains when each is the right tool. For most enterprise architects, this is unfamiliar territory — classical AI planning (planning as search over a state space) is rarely encountered outside research, yet it is increasingly relevant as agents become more autonomous.

---

## What is Classical AI Planning?

Classical AI planning frames execution as a **search problem**:

- **Initial state**: What is true now?
- **Goal state**: What do we want to be true?
- **Actions**: What can we do to change state? Each action has preconditions and effects.
- **Plan**: A sequence of actions that takes us from initial state to goal state.

```
Example: Loan approval planning problem

Initial state:
  application_received = true
  credit_checked = false
  documents_verified = false
  loan_approved = false

Goal:
  loan_approved = true

Available actions:
  check_credit:
    precondition: application_received = true
    effect: credit_checked = true

  verify_documents:
    precondition: application_received = true
    effect: documents_verified = true

  underwrite:
    precondition: credit_checked = true AND documents_verified = true
    effect: loan_approved = true OR loan_rejected = true

Planner generates:
  [check_credit, verify_documents, underwrite]
  OR
  [verify_documents, check_credit, underwrite]  (both are valid orderings)
```

The planner does not execute the plan — it finds the plan. A separate execution engine runs it.

---

## Planning Approaches

### STRIPS Planning (State Transition)

The classical model: actions have preconditions and add/delete effects on propositions.

```python
# Simple STRIPS-style planner
from dataclasses import dataclass
from typing import Optional

@dataclass
class Action:
    name: str
    preconditions: set[str]    # propositions that must be true
    add_effects: set[str]      # propositions this action makes true
    delete_effects: set[str]   # propositions this action makes false

def find_plan(
    initial_state: set[str],
    goal: set[str],
    actions: list[Action],
    max_depth: int = 20,
) -> Optional[list[str]]:
    """BFS search for a plan."""
    from collections import deque

    queue = deque([(initial_state, [])])
    visited = set()

    while queue:
        state, plan = queue.popleft()
        state_key = frozenset(state)

        if goal.issubset(state):
            return plan

        if state_key in visited or len(plan) >= max_depth:
            continue

        visited.add(state_key)

        for action in actions:
            if action.preconditions.issubset(state):
                new_state = (state | action.add_effects) - action.delete_effects
                queue.append((new_state, plan + [action.name]))

    return None  # No plan found

# Define loan approval actions
actions = [
    Action("check_credit", {"application_received"}, {"credit_checked"}, set()),
    Action("verify_documents", {"application_received"}, {"documents_verified"}, set()),
    Action("underwrite", {"credit_checked", "documents_verified"}, {"decision_made"}, set()),
]

plan = find_plan({"application_received"}, {"decision_made"}, actions)
# → ["check_credit", "verify_documents", "underwrite"]  (or verify first)
```

### Hierarchical Task Network (HTN) Planning

HTN decomposes high-level tasks into subtasks recursively — closer to how humans think about processes.

```python
@dataclass
class TaskDecomposition:
    task: str
    method: str
    subtasks: list[str]
    preconditions: set[str]

HTN_METHODS = {
    "process_loan": [
        TaskDecomposition(
            task="process_loan",
            method="standard_approval",
            subtasks=["verify_eligibility", "assess_risk", "make_decision", "disburse"],
            preconditions={"application_received"},
        ),
        TaskDecomposition(
            task="process_loan",
            method="expedited_approval",  # alternative method for small loans
            subtasks=["quick_credit_check", "auto_approve_if_eligible"],
            preconditions={"application_received", "amount_under_threshold"},
        ),
    ],
    "verify_eligibility": [
        TaskDecomposition(
            task="verify_eligibility",
            method="full_verification",
            subtasks=["check_credit", "verify_documents", "check_sanctions"],
            preconditions=set(),
        ),
    ],
}
```

HTN planning is well-suited to enterprise processes because the decomposition hierarchy mirrors how organizations structure their processes — and allows the planner to choose between methods based on context.

---

## Workflow Engines (Review)

Workflow engines (Temporal, Camunda) execute **predefined plans** — the developer specifies the sequence of steps, branching logic, and error handling.

```python
# Temporal workflow: the plan IS the code
@workflow.defn
class LoanWorkflow:
    @workflow.run
    async def run(self, application_id: str) -> str:
        # Developer-defined plan: always these steps in this order
        credit = await workflow.execute_activity(check_credit, application_id)
        docs = await workflow.execute_activity(verify_documents, application_id)
        decision = await workflow.execute_activity(underwrite, credit, docs)

        if decision.approved:
            await workflow.execute_activity(disburse_loan, application_id)

        return decision.status
```

The plan is **fixed at development time**. The workflow engine handles reliability (retries, durability), not planning.

---

## Head-to-Head Comparison

| Dimension | AI Planner | Workflow Engine |
| --- | --- | --- |
| **Plan origin** | Generated at runtime from goal | Written by developer |
| **Adaptability** | High — finds new paths for new goals | Low — only handles coded paths |
| **Predictability** | Low — plan varies by context | High — same code = same steps |
| **Computational cost** | High — search over state space | Low — direct execution |
| **Explainability** | Medium — can show step sequence | High — code is the documentation |
| **Failure handling** | Replanning (find alternative path) | Retry + compensation (coded) |
| **Auditability** | Medium — log the generated plan | High — event log = exact steps |
| **Team expertise** | Specialist (AI planning background) | Mainstream (any senior dev) |
| **Tooling maturity** | Low-Medium | High |

---

## LLM-Based Planning: The New Middle Ground

Modern LLM agents blur the line between planning and execution. An LLM can generate a plan, then execute it step by step — combining both approaches.

```python
from anthropic import Anthropic

client = Anthropic()

def llm_planner(goal: str, available_tools: list[dict], current_state: dict) -> list[dict]:
    """Use LLM to generate a plan given a goal and available tools."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""You are a process planner. Given a goal and available tools,
        generate a step-by-step plan as a JSON list of steps.
        Each step has: {"step": int, "action": str, "tool": str, "rationale": str}
        Only use tools from the provided list. Ensure preconditions are met.""",
        messages=[{
            "role": "user",
            "content": f"""
            Goal: {goal}
            Current state: {current_state}
            Available tools: {available_tools}

            Generate a minimal plan to achieve the goal.
            """,
        }],
    )
    import json
    return json.loads(response.content[0].text)

def execute_plan(plan: list[dict], tools: dict) -> list[dict]:
    """Execute a generated plan step by step."""
    results = []
    for step in plan:
        tool = tools.get(step["tool"])
        if tool is None:
            results.append({"step": step["step"], "error": f"Tool {step['tool']} not found"})
            continue
        result = tool.invoke(step)
        results.append({"step": step["step"], "result": result})
    return results

# LLM generates the plan; deterministic executor runs it
plan = llm_planner(
    goal="Process refund for customer C-123's duplicate charge",
    available_tools=[get_account_tool, check_charges_tool, issue_refund_tool],
    current_state={"customer_identified": True},
)
results = execute_plan(plan, tool_registry)
```

This approach combines the adaptability of planning with the reliability of deterministic execution: the LLM plans, a coded executor runs each step with proper retry logic.

---

## When to Use Each

### Use Classical AI Planning When

- The **space of possible processes is too large** to enumerate in code (manufacturing scheduling, logistics optimization, robotics)
- **Goals change frequently** at runtime (different customer goals = different processes)
- **Optimal ordering matters** and depends on context (minimize steps, parallelize where possible)
- You have **AI/planning expertise** on the team and the complexity justifies it

### Use Workflow Engines When

- The process is **well-understood and stable** — steps are known in advance
- **Regulatory compliance** requires exact, auditable steps
- **Team expertise** in AI planning is not available or justified
- **Failure handling** is complex (saga patterns, compensation)

### Use LLM-Based Planning When

- You need **adaptive planning** but don't need formal completeness guarantees
- The goal is **expressed in natural language** and varies per user
- You want **explainable planning** (the LLM can justify each step)
- You are building on an **agentic stack** already (LangGraph, CrewAI)

### The Practical Decision Tree

```
Is the process fixed and well-known?
  YES → Temporal / Camunda
  NO  ↓

Do you need optimal planning (minimize cost/steps)?
  YES → Classical planner (STRIPS, HTN)
  NO  ↓

Is the goal expressed in natural language?
  YES → LLM-based planning (agent + tool calling)
  NO  ↓

Is formal completeness required?
  YES → Classical planner
  NO  → LLM-based planning
```

---

## Hybrid: Plan-and-Execute Pattern

The most powerful pattern for complex enterprise processes:

```
Phase 1: LLM generates a plan
  → "To process this refund, I need to: (1) verify the duplicate, (2) check policy, (3) issue refund"

Phase 2: Plan submitted for human review (if high-stakes)
  → Human approves: "Yes, execute this plan"

Phase 3: Temporal executes the approved plan durably
  → Each step runs as a Temporal activity with full retry/audit guarantees

Phase 4: If a step fails, agent replans for that step only
  → "Step 2 failed — let me find an alternative"
```

This separates the **intelligence** (planning) from the **reliability** (execution) — each layer does what it is best at.

---

## Explainability: Presenting Plans to Humans

One underrated advantage of explicit planning (over purely agentic execution) is that plans can be presented to and approved by humans before execution. A plan is inherently more legible than a reasoning trace.

```python
def format_plan_for_human_review(plan: list[dict]) -> str:
    """Format a generated plan for human approval before execution."""
    lines = ["Proposed execution plan:", ""]
    for step in plan:
        lines.append(
            f"  Step {step['step']}: {step['action']}\n"
            f"    Tool: {step['tool']}\n"
            f"    Rationale: {step['rationale']}\n"
            f"    Estimated duration: {step.get('est_seconds', '?')}s\n"
            f"    Reversible: {'Yes' if step.get('reversible', True) else 'No — requires approval'}"
        )
    lines += [
        "",
        f"Total estimated duration: {sum(s.get('est_seconds', 0) for s in plan)}s",
        f"Irreversible steps: {sum(1 for s in plan if not s.get('reversible', True))}",
    ]
    return "\n".join(lines)

# Output example:
# Proposed execution plan:
#
#   Step 1: Retrieve customer account data
#     Tool: get_account_info
#     Rationale: Need current balance and status before processing refund
#     Estimated duration: 1s
#     Reversible: Yes
#
#   Step 2: Issue $50 refund
#     Tool: issue_refund
#     Rationale: Duplicate charge confirmed — policy allows full refund
#     Estimated duration: 3s
#     Reversible: No — requires approval
```

This "show the plan, get approval, then execute" pattern is the bridge between AI planning and human-in-the-loop governance. See [Human-in-the-Loop Architectures](./12-human-in-the-loop-architectures.md) for implementation.

---

## Related

[Durable Execution vs Cognitive Execution](./06-durable-vs-cognitive-execution.md) · [Tool Calling Orchestration](./09-tool-calling-orchestration.md) · [Human-in-the-Loop Architectures](./12-human-in-the-loop-architectures.md) · [Agent Frameworks Comparison](./08-agent-frameworks-comparison.md)
