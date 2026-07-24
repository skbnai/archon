---
title: Anti-Patterns Catalog - Orchestration and Agentic Systems
domain: agentic-systems
doc_type: guide
topic_id: anti-patterns-catalog
status: current
supersedes:
  - ../knowledge-docs/docs/workflow-orchestration/22-anti-patterns-catalog.md
date_created: 2026-07-24
last_reviewed: 2026-07-24
source_type: native-md
covers_version: "as of July 2026 — patterns apply across Temporal, Camunda, LangGraph, CrewAI"
tags:
  - workflow-orchestration
  - anti-patterns
  - lessons-learned
  - agents
  - design
---

# Anti-Patterns Catalog: Orchestration and Agentic Systems

> **As of July 2026.** Patterns documented here apply across Temporal, Camunda, LangGraph, CrewAI, and similar systems.

This catalog documents what **not** to do — common architectural mistakes, attractive but broken patterns, and production failures. Each anti-pattern includes why it happens, why it fails, and the correct approach.

---

## AP-01: Treat Agents Like Deterministic Activities

**The pattern**: Teams familiar with Temporal activities treat LLM agent invocations exactly like regular activities — expect them to produce the same output for the same input, retry them identically on failure, and audit their results as if they were deterministic.

**Why it seems right**: In Temporal, activities are deterministic. Retry = same action, same result. The mental model works for everything else.

**Why it fails**:

```
Temporal retry of a deterministic activity:
  Attempt 1: charge_card(amount=50) → FAIL (network error)
  Attempt 2: charge_card(amount=50) → SUCCESS ✓

Temporal retry of an LLM agent activity:
  Attempt 1: run_agent("Analyze application APP-123") → "Rejected — insufficient income"
  Attempt 2: run_agent("Analyze application APP-123") → "Approved — income acceptable"
  # Same inputs, different outputs. Which result do you record?
```

Retrying an agent doesn't guarantee the same decision. This breaks audit trails, creates inconsistent records, and can result in contradictory decisions being applied.

**The correct pattern**: Treat agent activities as **best-effort with a single attempt**. If the agent fails, escalate to human — do not retry and trust that the second answer is the same.

```python
# DO NOT: retry agent decisions like regular activities
await workflow.execute_activity(
    run_agent, application_id,
    retry_policy=RetryPolicy(max_attempts=3),  # ← Wrong for agents
)

# DO: single attempt, escalate on failure
try:
    result = await workflow.execute_activity(
        run_agent, application_id,
        retry_policy=RetryPolicy(max_attempts=1),
        start_to_close_timeout=timedelta(minutes=5),
    )
except ActivityError:
    await workflow.execute_activity(escalate_to_human, application_id)
```

---

## AP-02: All Business Logic in Prompts

**The pattern**: Using the prompt as the primary location for business rules. "If the customer has a premium account AND the charge is over $500 AND it's within 30 days..." — all in the system prompt.

**Why it seems right**: Prompts are easy to update. No code deployment needed. The LLM can "understand" complex rules in natural language.

**Why it fails**:

1. **Auditability**: You cannot prove which version of a rule was active at decision time
2. **Testing**: You cannot unit-test rules in a prompt — only E2E test the whole agent
3. **Consistency**: The LLM interprets rules probabilistically — edge cases produce inconsistent results
4. **Performance**: Running the entire rule set through an LLM is 100x more expensive than a DMN table

**The correct pattern**: Keep business rules in **structured, testable systems** (DMN tables, rule engines, policy-as-code). Use the LLM only for what structured systems cannot handle — interpretation, judgment, and novel situations.

```python
# DO NOT: embed business rules in prompt
system_prompt = """
You are a refund agent. Rules:
- Refund if within 30 days AND premium customer AND amount < $500
- Refund if purchase was a gift AND customer complained within 7 days
- Do not refund if account has >3 refunds in last 90 days
... (50 more rules)
"""

# DO: check rules in code, use LLM for exceptions only
async def process_refund(request: RefundRequest) -> RefundDecision:
    # Deterministic rules first (fast, cheap, auditable)
    rule_result = await dmn_engine.evaluate("refund-policy", request)

    if rule_result.decision in ("approve", "reject"):
        return RefundDecision(decision=rule_result.decision, basis="policy_rule")

    # LLM only for genuine ambiguity
    if rule_result.decision == "escalate":
        agent_decision = await run_refund_agent(request, context=rule_result.context)
        return RefundDecision(decision=agent_decision, basis="agent_judgment")
```

---

## AP-03: No Versioning for Prompts

**The pattern**: Storing prompts as strings in environment variables, config files, or directly in code — with no version history, no change tracking, and no ability to know which prompt was active at a given time.

**Why it seems right**: "It's just a text file" — seems like overkill to version it like software.

**Why it fails**:

- A production incident occurred. You changed the prompt two hours ago. You have no way to prove what changed.
- You need to roll back. You don't have the previous version.
- A regulator asks "what instruction did the AI receive when it rejected this loan application in March?" You have no answer.

**The correct pattern**: Treat prompts as versioned, approved artifacts. Store in a registry with full history. See [Enterprise Governance Model](./18-enterprise-governance-model.md).

---

## AP-04: Ignore Non-Determinism in Audit Trails

**The pattern**: Logging only the agent's final answer — not the reasoning, not the tool calls, not which prompt version was active.

**Why it seems right**: "We just need to know what the AI decided."

**Why it fails**: You have the verdict but not the reasoning. When a decision is challenged — by a customer, regulator, or incident review — you cannot explain HOW the decision was reached. This is a compliance failure in regulated industries and a trust failure everywhere else.

**The correct pattern**: Log the full decision provenance:

```python
@dataclass
class AgentDecisionRecord:
    decision: str
    prompt_version: str
    model_id: str
    tool_calls: list[dict]    # every call with inputs and outputs
    reasoning_trace: str      # the agent's thinking
    input_data: dict
    timestamp: datetime
```

---

## AP-05: Infinite Retry Loops

**The pattern**: Setting aggressive retry policies on all activities — including agent activities — without considering whether retrying actually helps.

**Why it seems right**: "More retries = more resilience."

**Why it fails**:

- A transient API error retries correctly. An LLM producing a wrong answer retries and may produce a different wrong answer — still wrong, but now you've run 3x the LLM cost.
- A cascading failure: workflow retries → multiple simultaneous agent runs → LLM rate limit hit → all retries fail → exponential backoff → system thrashes for 30 minutes.

**The correct pattern**: Distinguish retry categories:

```
Infrastructure failures (retry aggressively):
  - Network timeouts
  - Service unavailable (503)
  - Rate limits with backoff

Agent quality failures (do NOT retry):
  - Agent returned low-confidence answer
  - Agent reached max iterations
  - Agent called wrong tool

Business failures (escalate, don't retry):
  - Customer not eligible
  - Policy violation
  - Insufficient data
```

---

## AP-06: LLM as a Cache

**The pattern**: Calling an LLM to "remember" or "look up" facts that should be stored in a database. "Ask Claude what our refund policy is" instead of reading it from a config file.

**Why it seems right**: "The LLM knows everything — just ask it."

**Why it fails**:

1. **Stale**: The LLM's training data has a cutoff. It does not know your current policy.
2. **Unreliable**: LLMs hallucinate facts they are uncertain about.
3. **Expensive**: A database lookup costs microseconds and fractions of a cent. An LLM call costs 10-1000x more.
4. **Untestable**: You cannot write a unit test that verifies the LLM "remembers" a fact correctly.

**The correct pattern**: Use the LLM to **interpret** rules, not **store** them. Rules live in databases, config files, or DMN tables — retrieved as tool results.

---

## AP-07: One Mega-Agent

**The pattern**: Building a single large agent that handles all scenarios — customer support, billing, compliance, documentation, scheduling — by giving it 40+ tools and a 3,000-word system prompt.

**Why it seems right**: "Simpler architecture — one agent handles everything."

**Why it fails**:

1. **Context window pressure**: 40 tool definitions + long prompt + conversation history bloats the context, degrading quality.
2. **Debugging**: When something goes wrong, which part of the system is responsible?
3. **Permissions**: A mega-agent has access to every tool — a security risk. Compromise of one workflow gives access to all capabilities.
4. **Testing**: You cannot test individual capabilities in isolation.

**The correct pattern**: Specialized agents with narrow scopes, coordinated by a supervisor. See [A2A Orchestration Patterns](./a2a-orchestration-patterns).

---

## AP-08: No Human-in-the-Loop for High Stakes

**The pattern**: Running agents autonomously for decisions with significant consequences — large financial transactions, account deletions, legal documents — without any human approval step.

**Why it seems right**: "Human approval slows things down. We trust the AI."

**Why it fails**: AI systems fail in ways humans would catch trivially. A confident hallucination on a $100,000 loan decision, with no human review, can cause financial and reputational harm that takes months to resolve.

**The correct pattern**: Risk-tier every decision. High-stakes decisions always have a human gate. See [Human-in-the-Loop Architectures](./human-in-the-loop-architectures).

---

## AP-09: No Observability Until It Breaks

**The pattern**: Deploying agentic systems with minimal logging, planning to "add observability if something goes wrong."

**Why it seems right**: "We'll add monitoring when we scale."

**Why it fails**: By the time something breaks, you have no baseline to compare against. You don't know if today's behavior is anomalous because you have no historical data. Root cause analysis requires evidence that was never collected.

**The correct pattern**: Instrument before you deploy. Establish baselines before you go live. See [Observability Framework](./16-observability-framework.md).

```
Minimum viable observability before production:
  ✓ Iteration count per agent run
  ✓ Token usage per run
  ✓ Tool call distribution
  ✓ Error rate and type
  ✓ Business decision distribution
  ✓ Human override rate
```

---

## AP-10: Side Effects in Workflow Code

**The pattern**: Calling external APIs, reading from databases, or generating random values directly in Temporal workflow code (not inside activities).

**Why it seems right**: "Why wrap a simple database read in an activity? It's just one line."

**Why it fails**: Temporal's recovery mechanism replays workflow code. Any non-deterministic operation in workflow code (external call, random, current time) will produce a different result on replay — corrupting the workflow's state and causing silent failures.

```python
# WRONG: side effect in workflow code
@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> dict:
        # This HTTP call happens AGAIN on replay — but the result may differ!
        customer = requests.get(f"/api/customers/{order_id}").json()  # ← Wrong
        ...

# CORRECT: side effects only inside activities
@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> dict:
        customer = await workflow.execute_activity(
            fetch_customer, order_id,
            start_to_close_timeout=timedelta(seconds=10),
        )
        ...
```

---

## AP-11: Trusting Agent Self-Reporting

**The pattern**: Using the agent's own assessment of its confidence or correctness as input to routing decisions. "The agent said it was 95% confident — approve automatically."

**Why it seems right**: "The agent knows what it knows."

**Why it fails**: LLMs are notoriously poorly calibrated. High confidence does not predict correctness — in many scenarios, hallucinations come with high expressed confidence. An agent that fabricates a fact typically does not flag uncertainty.

**The correct pattern**: Route by **outcome type and risk**, not by claimed confidence. If the decision is high-stakes, it goes to a human regardless of what the agent says about its confidence.

---

## Quick Reference

| Anti-Pattern | Root Cause | Fix |
| --- | --- | --- |
| AP-01: Agents = deterministic | Mental model from Temporal activities | Single attempt, escalate on failure |
| AP-02: Logic in prompts | Ease of iteration | Rules in DMN/code, LLM for judgment only |
| AP-03: No prompt versioning | "It's just text" | Prompt registry with full history |
| AP-04: Audit only the answer | Simplicity | Log full provenance — prompt, tools, reasoning |
| AP-05: Infinite retries | "More = better" | Distinguish failure types, retry only infrastructure |
| AP-06: LLM as cache | "It knows everything" | Database for facts, LLM for interpretation |
| AP-07: Mega-agent | "Simpler is better" | Specialized agents + supervisor |
| AP-08: No HITL for high stakes | Speed | Risk-tier all decisions, HITL for high-risk |
| AP-09: No observability | "Add it later" | Instrument before production, establish baselines |
| AP-10: Side effects in workflow code | Temporal misunderstanding | All side effects in activities |
| AP-11: Trust agent confidence | "AI knows best" | Route by risk, not by claimed confidence |

---

## Related

[Reliability Playbook](./reliability-playbook) · [Enterprise Governance Model](./18-enterprise-governance-model.md) · [Human-in-the-Loop Architectures](./human-in-the-loop-architectures) · [Durable Execution vs Cognitive Execution](./durable-vs-cognitive-execution)
