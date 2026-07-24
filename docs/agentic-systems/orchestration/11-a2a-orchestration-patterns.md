---
title: "A2A (Agent-to-Agent) Orchestration Patterns"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: a2a-orchestration-patterns
supersedes: ["../knowledge-docs/docs/workflow-orchestration/11-a2a-orchestration-patterns.md"]
doc_type: guide
tags: ["workflow-orchestration", "agents", "multi-agent", "a2a"]
---

# A2A (Agent-to-Agent) Orchestration Patterns

> **As of July 2026.** The A2A protocol is still evolving — check [google.github.io/A2A](https://google.github.io/A2A) for the latest spec.

This guide covers how agents coordinate with other agents — delegating subtasks, handing off work, negotiating priorities, and recovering from peer failures. These patterns are the architectural building blocks for multi-agent systems at enterprise scale.

---

## Why A2A Matters

A single agent can handle well-scoped tasks. Real enterprise processes require **specialization**: a loan application might involve a credit-check agent, a compliance-verification agent, an underwriting-decision agent, and a customer-communication agent. How do they share context, coordinate timing, and recover when one fails?

A2A patterns answer these questions. They are the glue between specialized agents.

**Traditional (single agent — does everything):**
```mermaid
graph LR
    A["Loan Agent<br/>- fetch credit score<br/>- check AML/KYC<br/>- underwrite decision<br/>- draft approval letter"]
```

**Multi-agent (specialized, coordinated):**
```mermaid
graph TD
    Credit["Credit Agent<br/>(credit score<br/>bureau APIs)"]
    Compliance["Compliance Agent<br/>(AML/KYC)"]
    Underwriting["Underwriting Agent<br/>(decision)"]
    Comms["Comms Agent<br/>(letter, email, SMS)"]
    
    Credit --> Underwriting
    Compliance --> Underwriting
    Underwriting --> Comms
```

---

## Pattern 1: Hierarchical Delegation

A **supervisor agent** breaks a goal into subtasks and delegates to specialized child agents. Children report results back; the supervisor aggregates and decides next steps.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class SupervisorState(TypedDict):
    goal: str
    subtasks: list[dict]
    results: dict[str, str]
    final_answer: str

def supervisor(state: SupervisorState) -> SupervisorState:
    """Decides which agent to call next."""
    if not state["subtasks"]:
        # Decompose the goal into subtasks
        subtasks = planner_llm.invoke(f"Decompose: {state['goal']}")
        return {"subtasks": subtasks}

    if all(t["id"] in state["results"] for t in state["subtasks"]):
        # All done — aggregate
        answer = aggregator_llm.invoke(f"Synthesize: {state['results']}")
        return {"final_answer": answer}

    # Delegate next pending subtask
    next_task = next(t for t in state["subtasks"] if t["id"] not in state["results"])
    return {"current_task": next_task}

def credit_agent(state: SupervisorState) -> SupervisorState:
    result = credit_service.check(state["current_task"]["applicant_id"])
    return {"results": {**state["results"], "credit": result}}

def compliance_agent(state: SupervisorState) -> SupervisorState:
    result = aml_service.check(state["current_task"]["applicant_id"])
    return {"results": {**state["results"], "compliance": result}}

# Route from supervisor to appropriate specialized agent
def route(state: SupervisorState) -> Literal["credit_agent", "compliance_agent", "end"]:
    if state.get("final_answer"):
        return "end"
    task_type = state.get("current_task", {}).get("type", "")
    return f"{task_type}_agent"
```

**When to use**: Long, complex goals with multiple independent subtasks. The supervisor maintains the goal while children focus on specialization.

**Failure handling**: If a child agent fails, the supervisor can retry the same child, use a fallback agent, or escalate to a human.

---

## Pattern 2: Sequential Handoff

Agent A completes its work, then **hands off** to Agent B with a structured context package. Agent A has no further involvement.

```python
class HandoffContext(TypedDict):
    original_request: str
    agent_a_output: dict
    handoff_reason: str
    constraints: list[str]  # what B must respect from A's work

async def research_agent(request: str) -> HandoffContext:
    """Does research, then hands off to writing agent."""
    findings = await run_research(request)

    return HandoffContext(
        original_request=request,
        agent_a_output={"findings": findings, "sources": sources},
        handoff_reason="Research complete, needs synthesis",
        constraints=["Do not modify factual claims", "Cite all sources"],
    )

async def writing_agent(ctx: HandoffContext) -> str:
    """Takes handoff from research agent."""
    system = f"""
    You are a technical writer. You received this handoff:
    Original request: {ctx['original_request']}
    Research findings: {ctx['agent_a_output']['findings']}
    Constraints you must follow: {ctx['constraints']}
    """
    return await llm.ainvoke(system + "\n\nWrite the final document.")
```

**When to use**: Sequential pipelines where each agent contributes a distinct phase. Customer support handoffs (triage → specialist), research pipelines (gather → synthesize → format).

**Key practice**: The context package must be **self-contained** — Agent B should not need to call Agent A again. Include everything B needs in the handoff.

---

## Pattern 3: Peer Collaboration

Two agents with equal authority work toward a shared goal, exchanging messages and context. Neither is the boss — they reach agreement or escalate.

```python
class CollaborationState(TypedDict):
    proposal: str
    reviews: list[dict]
    round: int
    consensus: bool

async def architect_agent(state: CollaborationState) -> CollaborationState:
    if not state["proposal"]:
        proposal = await llm.ainvoke("Design a payment gateway architecture")
        return {"proposal": proposal, "round": 1}

    # Revise based on security agent's feedback
    if state["reviews"]:
        last_review = state["reviews"][-1]
        revised = await llm.ainvoke(
            f"Revise proposal addressing: {last_review['concerns']}\n"
            f"Original: {state['proposal']}"
        )
        return {"proposal": revised, "round": state["round"] + 1}

async def security_agent(state: CollaborationState) -> CollaborationState:
    review = await llm.ainvoke(
        f"Security review of: {state['proposal']}\n"
        "List concerns and whether you approve."
    )
    approved = "APPROVED" in review.upper()
    return {
        "reviews": state["reviews"] + [{"concerns": review, "approved": approved}],
        "consensus": approved,
    }

def route_collaboration(state: CollaborationState) -> str:
    if state.get("consensus"):
        return "end"
    if state["round"] > 3:
        return "escalate_to_human"
    return "security_agent" if state["reviews"] else "architect_agent"
```

**When to use**: Tasks requiring multiple perspectives (code review, risk assessment, proposal drafting). The "round-trip" between agents catches errors neither would catch alone.

**Deadlock prevention**: Always set a maximum round limit and escalate to human when reached.

---

## Pattern 4: Fan-Out / Fan-In (Parallel Agents)

A coordinator spawns multiple agents in parallel for independent subtasks, then aggregates results.

```python
import asyncio

async def research_coordinator(question: str) -> str:
    """Fan out to specialized agents in parallel, then synthesize."""

    # Fan-out: run all agents concurrently
    results = await asyncio.gather(
        academic_agent.run(question),      # searches academic papers
        industry_agent.run(question),       # searches industry reports
        regulatory_agent.run(question),     # checks regulatory context
        competitor_agent.run(question),     # competitive landscape
        return_exceptions=True,             # don't fail if one agent errors
    )

    # Fan-in: filter errors, aggregate successes
    valid_results = {
        name: result
        for name, result in zip(["academic", "industry", "regulatory", "competitor"], results)
        if not isinstance(result, Exception)
    }

    if len(valid_results) < 2:
        raise RuntimeError("Insufficient agent results for synthesis")

    return await synthesis_agent.run(question, context=valid_results)
```

**When to use**: Research, due diligence, competitive analysis — any task where multiple independent sources improve quality. The speedup from parallelism is significant when each agent takes 5–30 seconds.

**Failure handling**: Use `return_exceptions=True` and set a minimum quorum of valid results before synthesizing.

---

## Pattern 5: Negotiation

Agent A needs something from Agent B but must negotiate terms. Agents propose, counter-propose, and either agree or escalate.

```python
class NegotiationState(TypedDict):
    resource: str
    requester: str
    offer: dict
    counter_offer: dict
    agreed: bool
    round: int

async def resource_broker_agent(state: NegotiationState) -> NegotiationState:
    """Decides whether to accept, counter, or reject."""

    if state["round"] > 5:
        return {"agreed": False}  # Negotiation failed, escalate

    analysis = await llm.ainvoke(
        f"Resource: {state['resource']}\n"
        f"Current offer: {state['offer']}\n"
        "Should we accept, counter with X, or reject? Current capacity: 70%."
    )

    if "ACCEPT" in analysis:
        return {"agreed": True}
    elif "COUNTER" in analysis:
        counter = parse_counter(analysis)
        return {"counter_offer": counter, "round": state["round"] + 1}
    else:
        return {"agreed": False}
```

**When to use**: Resource allocation, scheduling, dynamic pricing, compute resource sharing between agents.

---

## Communication Patterns

### Message Passing (Explicit)

Agents exchange typed messages with a clear envelope. Best for audit trails.

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    message_type: str  # "request" | "response" | "handoff" | "escalate"
    payload: dict
    trace_id: str      # correlate across agents
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

### Shared Memory (Implicit)

Agents read/write a shared state store. Simpler to implement, harder to debug.

```python
# Redis or in-memory shared state
shared_state = {
    "task_id": "T-123",
    "credit_result": None,    # set by credit agent
    "compliance_result": None, # set by compliance agent
    "ready_for_underwriting": False,  # set when both above are populated
}
```

**Prefer message passing** for production systems — it creates an audit trail and avoids race conditions when multiple agents write simultaneously.

---

## Deadlock Prevention

Multi-agent systems can deadlock when Agent A waits for Agent B, which waits for Agent A.

```
Deadlock scenario:
  Agent A: "Waiting for Agent B's approval"
  Agent B: "Waiting for Agent A's data"
  → Neither proceeds. System hangs.
```

**Prevention strategies**:

1. **Timeout every wait**: Every agent-to-agent call has a deadline
2. **Detect cycles**: Before assigning a dependency, check if it creates a circular wait
3. **Escalate, don't block**: If a dependency is not resolved within N seconds, escalate to supervisor or human
4. **Depth limits**: No chain of agent delegations deeper than N levels (typically 3–5)

```python
async def agent_request_with_timeout(
    target_agent: str,
    payload: dict,
    timeout_seconds: int = 30,
) -> dict:
    try:
        return await asyncio.wait_for(
            call_agent(target_agent, payload),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        # Don't block — escalate
        await notify_supervisor(f"{target_agent} timed out after {timeout_seconds}s")
        raise
```

---

## Observability for Multi-Agent Systems

Multi-agent traces need **distributed correlation** — a single trace ID spanning all agent hops.

```mermaid
graph TD
    Root["Trace ID: TRACE-abc123"]
    
    Super["Supervisor t=0ms"]
    SuperDecompose["Span: decompose_goal"]
    SuperRoute["Span: route_to_credit_agent"]
    
    Credit["Credit Agent t=120ms<br/>same trace ID, different span"]
    CreditScore["Span: fetch_credit_score"]
    CreditReturn["Span: return_to_supervisor"]
    
    Compliance["Compliance Agent t=125ms<br/>parallel with credit agent"]
    CompAml["Span: run_aml_check"]
    CompReturn["Span: return_to_supervisor"]
    
    Underwriting["Underwriting Agent t=340ms"]
    UnderwriteAgg["Span: aggregate_results"]
    UnderwriteEmit["Span: emit_decision"]
    
    Root --> Super
    Root --> Credit
    Root --> Compliance
    Root --> Underwriting
    
    Super --> SuperDecompose
    Super --> SuperRoute
    
    Credit --> CreditScore
    Credit --> CreditReturn
    
    Compliance --> CompAml
    Compliance --> CompReturn
    
    Underwriting --> UnderwriteAgg
    Underwriting --> UnderwriteEmit
```

Pass the trace ID explicitly in every `AgentMessage`. Use OpenTelemetry spans to capture each agent's work under the same root trace.

---

## Example: Loan Application Multi-Agent Flow

```mermaid
graph TD
    Start["Customer submits application"]
    Intake["Intake Agent<br/>(fast, cheap)<br/>validates format, extracts key fields"]
    
    Credit["Credit Agent"]
    Compliance["Compliance Agent"]
    Income["Income Agent"]
    
    Underwriting["Underwriting Agent<br/>(heavyweight, slow)<br/>makes decision with full context"]
    Comms["Communication Agent<br/>drafts approval letter, sends notifications"]
    
    Start --> Intake
    Intake -->|fan-out parallel| Credit
    Intake -->|fan-out parallel| Compliance
    Intake -->|fan-out parallel| Income
    
    Credit -->|fan-in all 3 must complete| Underwriting
    Compliance -->|fan-in all 3 must complete| Underwriting
    Income -->|fan-in all 3 must complete| Underwriting
    
    Underwriting -->|if approved: sequential handoff| Comms
```

The intake and underwriting agents are sequential (one depends on the other). Credit, compliance, and income agents run in parallel (independent subtasks). The handoff to communications is clean — all context flows in the handoff package.

---

## Related

[Agent Frameworks Comparison](./08-agent-frameworks-comparison.md) · [Human-in-the-Loop Architectures](./12-human-in-the-loop-architectures.md) · [Reliability Playbook](./15-reliability-playbook.md) · [Observability Framework](./16-observability-framework.md)
