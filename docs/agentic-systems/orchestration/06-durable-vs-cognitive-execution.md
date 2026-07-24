---
title: "Durable Execution vs. Cognitive Execution"
doc_type: guide
domain: agentic-systems
status: current
topic_id: durable-vs-cognitive-execution
supersedes:
  - docs/workflow-orchestration/06-durable-vs-cognitive-execution.md
date: 2026-07-24
last_reviewed: 2026-07-24
---

# Durable Execution vs. Cognitive Execution

## The Core Distinction

Two fundamentally different execution models coexist in enterprise systems—and conflating them is one of the most expensive architectural mistakes teams make.

**Durable execution** (Temporal, Azure Durable Functions, AWS Step Functions) guarantees that a defined sequence of steps will eventually complete, exactly as programmed, surviving any infrastructure failure. The system is deterministic: given the same inputs and the same event history, it always produces the same outputs.

**Cognitive execution** (LangGraph, CrewAI, Claude agents) uses an LLM to reason about what to do next. The agent observes context, generates thoughts, invokes tools, and iterates until it reaches a goal—or decides it can't. The system is probabilistic: the same input may produce different outputs depending on model temperature, context window state, and which tools happen to respond first.

They are not competitors. They solve different problems. The challenge is knowing which one owns which layer of your system.

---

## Durable Execution: The Deterministic Contract

### What It Is

Durable execution is built on **event sourcing**: every state transition in a workflow is written to an append-only log before it is acted on. If the process crashes, it replays the log to reconstruct exactly where it was—and continues from there without re-executing completed steps.

**Event Log (Temporal History)**:
1. `WorkflowStarted {orderId: "ORD-123"}`
2. `ActivityScheduled {name: "ValidatePayment"}`
3. `ActivityCompleted {result: {valid: true}}`
4. `ActivityScheduled {name: "ChargeCard"}`
5. **CRASH HERE**
6. Worker restarts, replays events 1-4, picks up at 4
7. `ActivityCompleted {result: {charged: true}}`
8. `WorkflowCompleted`

Replay is **deterministic** because every activity result is cached in the log. The replayed code reaches the same decision branches using cached results, never re-executing side effects.

### Key Properties

| Property | Behavior |
| --- | --- |
| **State model** | Event log is source of truth; workflow state is derived |
| **Recovery** | Replay from last completed event; no re-execution of completed steps |
| **Retry semantics** | Retry the *same* activity with *same* input until success or max retries |
| **Failure handling** | Explicit: compensation logic, saga patterns |
| **Observability** | Exact: "Activity 3 of 7 completed at 14:23:01" |
| **Determinism** | Guaranteed: same inputs → same outputs |
| **Side effects** | Controlled: only inside activities (never in workflow code) |
| **Long running** | Native: workflows survive restarts, run for days or years |

### Example: Payment Processing

```python
@workflow.defn
class PaymentWorkflow:
    @workflow.run
    async def run(self, payment: Payment) -> Result:
        validation = await workflow.execute_activity(
            validate_payment,
            payment,
            retry_policy=RetryPolicy(max_attempts=3)
        )

        if not validation.valid:
            return Result(success=False, reason=validation.error)

        # If this crashes after charge but before notify,
        # replay skips the charge (result cached) and retries notify only
        charge = await workflow.execute_activity(
            charge_card,
            payment,
            retry_policy=RetryPolicy(max_attempts=1)
        )

        await workflow.execute_activity(
            notify_customer,
            charge,
            retry_policy=RetryPolicy(max_attempts=5)
        )

        return Result(success=True, charge_id=charge.id)
```

Compliance teams can read the event log and answer "exactly what happened" to the dollar—at any point in time, months later.

---

## Cognitive Execution: The Probabilistic Contract

### What It Is

Cognitive execution uses an LLM as the **reasoning engine** that determines what to do next. Rather than following a predefined script, the agent:

1. Receives a goal and available tools
2. Generates a thought about what action to take
3. Invokes a tool
4. Observes the result
5. Reasons about what to do next
6. Repeats until done

**Agent Execution Loop (ReAct pattern)**:

Goal: "Help customer resolve billing dispute for account A-123"

Step 1:
- Thought: "I need to look up the account first"
- Action: lookup_account(id="A-123")
- Observation: `{balance: -$50, last_charge: "Jul 1 SAAS"}`

Step 2:
- Thought: "The $50 charge looks suspicious. Check it."
- Action: get_charge_details(id="CHG-789")
- Observation: `{amount: 50, desc: "Annual plan renewal"}`

Step 3:
- Thought: "Customer may not have noticed auto-renew. Offer partial refund per policy."
- Action: check_refund_policy(reason="auto-renew")
- Observation: `{eligible: true, max_refund: 25}`

Step 4:
- Action: draft_response(offer_refund=25, explain=true)
- Result: [Response drafted, awaiting human review]

### Key Properties

| Property | Behavior |
| --- | --- |
| **State model** | Conversation history + working memory |
| **Recovery** | Restart from scratch or from last checkpoint |
| **Retry semantics** | Retry with *different reasoning* (not the same action) |
| **Failure handling** | Emergent: agent may try another approach |
| **Observability** | Opaque: "Why did agent choose this tool?" requires tracing |
| **Determinism** | Probabilistic: same input may yield different action sequence |
| **Side effects** | Uncontrolled: agent calls tools in any order it decides |
| **Long running** | Native to short-medium tasks; long runs need memory management |

### The Non-Determinism Challenge

In a Temporal workflow, you can guarantee:

- "Activity A always runs before Activity B"
- "If Activity A fails, we retry it exactly 3 times"
- "The compensation saga always runs if step 5 fails"

In a cognitive system, you cannot guarantee:

- "The agent will always check balance before applying refund"
- "The agent will always ask for approval before making changes"
- "The agent will not invent a tool that does not exist"

This is not a defect—it is a feature. The agent adapts to unexpected situations. But it means the **contract is different**: you are agreeing to a best-effort, probabilistic outcome, not a guaranteed deterministic one.

---

## Head-to-Head Comparison

| Dimension | Durable Execution | Cognitive Execution |
| --- | --- | --- |
| **Control flow** | Code-defined graph | LLM-determined at runtime |
| **Predictability** | High (same path each time) | Low-Medium (varies by context) |
| **Adaptability** | Low (must handle all cases in code) | High (adapts to novel situations) |
| **Debuggability** | High (event log = full trace) | Medium (requires reasoning trace) |
| **Auditability** | Excellent (exact replay) | Challenging (probabilistic) |
| **Cost per step** | Low (direct function calls) | Higher (LLM tokens per reasoning step) |
| **Speed** | Fast (no LLM latency per step) | Slower (LLM reasoning per step) |
| **Error handling** | Explicit (you define compensation) | Emergent (agent decides) |
| **Compliance** | Strong (deterministic audit trail) | Weaker (probabilistic decisions) |
| **Novel situations** | Poor (crashes or takes wrong path) | Strong (adapts via reasoning) |

---

## Retry Semantics: A Critical Difference

This is where teams get into trouble most often.

### Durable Execution Retry

In Temporal, a retry means: **re-execute the same activity with the same inputs**.

```python
retry_policy = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
)
```

This works because activities must be **idempotent**: calling `send_email(...)` three times has the same effect as calling it once. The event log ensures the result is cached after the first success.

### Cognitive Execution Retry

In an LLM agent, a "retry" means: **reason about why it failed and try a different approach**.

```
First attempt:
  Action: send_invoice(customer_id=123)
  Error:  "Customer email not set"

Agent reasoning:
  "The customer has no email. Let me find their phone instead."
  Action: get_customer_phone(customer_id=123) → "+1-555-0100"
  Action: send_sms_invoice(phone="+1-555-0100") → Success
```

The agent adapted—it did not retry the same failed action. This is powerful but unverifiable: you cannot guarantee the agent will always find this workaround, or that it will not take a worse path.

---

## Hybrid Architectures: Using Both Together

The most powerful pattern uses both—each owning what it does best.

### The Outer/Inner Pattern

```mermaid
flowchart TD
    T["Temporal Workflow outer shell durable"]
    A1["Activity 1: Fetch Customer Data"]
    A2["Activity 2: Run LangGraph Agent cognitive"]
    Agent["Agent: Analyze dispute<br/>Tool: lookup_policy<br/>Tool: check_eligibility<br/>Tool: draft_resolution"]
    A3["Activity 3: Apply Resolution to CRM"]
    
    T --> A1 --> A2 --> Agent --> A3 --> T
    
    style T fill:#e3f2fd
    style A1 fill:#c8e6c9
    style A2 fill:#fff9c4
    style Agent fill:#ffccbc
    style A3 fill:#c8e6c9
```

**Temporal owns**: High-level flow, guaranteed execution, compensation logic, and audit trail.  
**The agent owns**: Reasoning, policy interpretation, and adaptive decision-making within a bounded step.

If the agent fails, Temporal can retry the entire activity (re-running the agent from scratch) or escalate to a human. The outer workflow remains auditable. The inner reasoning is traceable but probabilistic.

### When to Use Hybrid

| Scenario | Pattern |
| --- | --- |
| Complex, variable decision within a structured process | Agent as Temporal activity |
| Structured steps before/after free-form reasoning | Temporal wrapping agent |
| Compliance-required audit trail + adaptive logic | Temporal outer + LangGraph inner |
| Dynamic tool selection with guaranteed completion | Agent tools → Temporal activities |

---

## When to Choose Each

### Choose Durable Execution When

- **Compliance matters**: You need an exact, auditable record of every step
- **Idempotency is achievable**: Actions can be retried without unintended side effects
- **The process is well-defined**: You know all the steps in advance
- **Long-running is required**: The process might take hours, days, or weeks
- **Cost control**: LLM calls add up at scale; structured steps are an order of magnitude cheaper
- **Failure modes are known**: You can write explicit compensation logic

**Examples**: Payment processing, regulatory filings, order fulfillment, onboarding workflows

### Choose Cognitive Execution When

- **The problem is open-ended**: You cannot enumerate all paths in advance
- **Context varies dramatically**: Each situation requires different judgment
- **Reasoning is required**: Interpreting policy, evaluating exceptions, making judgment calls
- **Tools evolve frequently**: Adding capabilities without rewriting flows
- **Speed-to-market matters**: Building flows by prompt is faster than coding decision trees

**Examples**: Customer support, content moderation, research assistance, document analysis, exception handling

### The Decision Heuristic

> If you can draw it as a flowchart, use durable execution.  
> If it requires reading the situation and deciding, use cognitive execution.  
> If it requires both, wrap the cognitive layer inside durable execution.

---

## The Practical Reality in 2026

Enterprise systems increasingly layer both models:

1. **Process orchestration** (Temporal/Camunda): Governs the high-level lifecycle
2. **Decision intelligence** (LangGraph/Claude): Governs the reasoning within bounded steps
3. **Human oversight** (approval gates): Governs high-stakes decisions either model makes

The key architectural principle: **push determinism as high as you can, push cognition as deep as it needs to go**.

Do not use an LLM where a simple rule works. Do not use a rigid workflow where judgment is required. The boundary between them is your most important architectural decision.

---

## Summary

| What You Need | Use |
| --- | --- |
| "Process runs exactly as defined" | Durable execution |
| "Process adapts based on context" | Cognitive execution |
| "Exact audit trail required" | Durable execution |
| "Handle novel situations" | Cognitive execution |
| "Cost-efficient at scale" | Durable execution |
| "Natural language goals" | Cognitive execution |
| "Guaranteed completion" | Durable execution |
| "Best-effort with reasoning" | Cognitive execution |
| "Both required" | Temporal (outer) + LangGraph (inner) |

The future is not one or the other. It is building the judgment to know which layer owns which responsibility—and designing systems where both can coexist without one undermining the other's guarantees.

---

**Related sections**: [Workflow vs Agent Architecture](./03-workflow-vs-agent-architecture.md) · [Temporal Deep Dive](./04-temporal-deep-dive.md) · [Memory vs Workflow State](./13-memory-vs-workflow-state.md) · [Reliability Playbook](./15-reliability-playbook.md)
