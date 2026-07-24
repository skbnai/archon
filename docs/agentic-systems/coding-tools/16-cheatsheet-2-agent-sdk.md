---
title: "Agent SDK Cheat Sheet"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-2-agent-sdk
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/Cheatsheet_2_Agent_SDK.md
---

# Agent SDK Cheat Sheet

Agentic Architecture &amp; Orchestration - Anthropic Partner Certification EA

**DOMAIN 1 · 27% - HIGHEST WEIGHT**

## The Agentic Loop — Complete Flow

**1. SEND REQUEST** — Send messages + tools to Claude API. Include full conversation history with all prior tool results.

**2. INSPECT stop_reason** — Check the response's stop_reason field. This controls loop continuation.

**3a. stop_reason = "tool_use"** — Claude wants a tool. Extract tool name + inputs. Execute the tool. Append result to conversation history. **LOOP CONTINUES →**

**3b. stop_reason = "end_turn"** — Claude is done. No more tool calls needed. Extract final response text. **LOOP TERMINATES ✓**

**4. APPEND TO HISTORY** — Tool result goes back into conversation so Claude can reason about it in next iteration.

**⚠️ NEVER check assistant text for "I have completed" as loop termination signal — use stop_reason**

**⚠️ NEVER set arbitrary iteration caps as PRIMARY stopping mechanism — only as safety fallback**

**✓ Loop continues on tool_use. Loop terminates on end_turn. That's the entire control flow.**

## stop_reason Values

```javascript
// Check stop_reason in response
const { stop_reason } = response;

if (stop_reason === "tool_use") {
  // Execute tools, append results
  // Then call API again
  continueLoop(toolResults);
}

if (stop_reason === "end_turn") {
  // Claude is done
  return response.content;
}
```

### All possible stop_reason values

- **tool_use:** Claude invoked a tool — execute it and loop back
- **end_turn:** Claude naturally finished — terminate loop
- **max_tokens:** Hit token limit — handle gracefully (not normal end)
- **stop_sequence:** Custom stop sequence matched — configure termination

### Decision (Model-driven vs Pre-configured)

- **Model-driven:** Claude reasons from context which tool to call next — dynamic, flexible
- **Pre-configured:** Fixed tool sequences or decision trees hardcoded — predictable, rigid

## Multi-Agent Architecture

### Hub-and-Spoke Pattern

**Coordinator Agent (Central Hub)**
- Manages ALL inter-agent communications
- Handles errors centrally
- Routes information to/from subagents

**Subagents (Spokes)**
- Subagent A: web search
- Subagent B: doc analysis
- Subagent C: synthesis
- Subagent D: report gen

### Coordinator Responsibilities

- Decompose complex queries into subtasks
- Delegate to appropriate subagents
- Aggregate results from subagents
- Decide which subagents to invoke (dynamic)
- Route ALL subagent communication centrally

### Context Isolation Rules

- Subagents do NOT automatically inherit coordinator's conversation history
- Coordinator must explicitly pass relevant context when invoking subagents

### Isolation Benefits

- Prevents cross-contamination
- Enables true parallel execution
- Clean independent reasoning per agent
- Consistent, predictable behavior

### Routing Benefit

- Observability: log all communication
- Consistent error handling
- Controlled information flow

### Dynamic vs Full-Pipeline Invocation

- **Dynamic (correct):** Analyze query → invoke only relevant subagents. Simple query? Only search agent. Complex? Full pipeline.
- **Full-pipeline (wrong):** Always routing through all subagents regardless of query complexity → wasteful

## Lifecycle Hooks

### PreToolUse
Intercepts OUTGOING tool calls BEFORE execution. Enforce compliance rules, block forbidden actions.

### PostToolUse
Intercepts tool RESULTS BEFORE model processes them. Normalize data formats, validate responses.

### Hooks vs Prompt Instructions

| **Hooks** | **Prompts** |
|---|---|
| Deterministic | Probabilistic |
| Guaranteed compliance | Best-effort guidance |
| Hard business rules | Style/tone preferences |
| $500 refund block | Be concise |

### PostToolUse: Data Normalization

```javascript
// Different tools return different formats
// Unix timestamp: 1699900000
// ISO 8601: "2024-01-15T10:00:00Z"
// Status code: 200

// PostToolUse hook normalizes ALL
// to consistent format before model sees it

onPostToolUse(result => {
  result.timestamp = toISO8601(result.ts);
  result.status = toText(result.statusCode);
  return result;
});
```

### PreToolUse: Compliance Enforcement

```javascript
onPreToolUse("process_refund", (params) => {
  if (params.amount > 500) {
    // Block and redirect — guaranteed, not probabilistic
    return { blocked: true, redirect: "escalate_to_human" };
  }
});
```

## Task Decomposition

### Task Statement 1.6

- **Subtopic partition:** Assign distinct subtopics or source types to each subagent to minimize duplication
- **Iterative refinement:** Evaluate synthesis → identify gaps → re-delegate with targeted queries → re-synthesize
- **Coverage check:** Continue loop until coverage is deemed sufficient — not just "one pass"

### Decomposition Risk

Overly narrow decomposition → coordinator misses broad coverage of research topics

### Handoff Summaries (Task 1.4)

- **Customer ID** — who is this?
- **Root cause** — what went wrong?
- **Refund amount** — what action is pending?
- **Recommended action** — what should agent do?
- **Needed when:** human lacks transcript access

## Scenario Coverage

### Scenario 1: Customer Support Agent

- **MCP tools:** get_customer, lookup_order, process_refund, escalate_to_human
- **Target:** 80%+ first-contact resolution
- **Escalation:** Confidence threshold, issue category, policy boundaries

### Scenario 3: Multi-Agent Research

- **Subagents:** web search, doc analysis, synthesis, report gen
- **Output:** Comprehensive, cited research reports
- **Domains:** Agentic Arch, Tool &amp; MCP, Context Management

### Task Statements Covered

- 1.1 Agentic loops
- 1.2 Multi-agent
- 1.3 Subagent config
- 1.4 Handoffs
- 1.5 Hooks
- 1.6 Decomposition

## Anti-Patterns (Exam Critical)

- Parsing "I have completed" in response text as loop termination — WRONG
- Iteration caps as PRIMARY stop mechanism — caps = safety fallback only
- Assuming subagents inherit coordinator history — they don't (isolation)
- Prompt instructions for guaranteed compliance — use hooks instead
- Always routing all queries through full pipeline — select relevant subagents dynamically
- Narrow task decomposition on broad topics — leads to gaps in coverage

## Key Exam Facts

- **Domain 1 = 27%** — highest weight on exam
- **stop_reason = the ONLY correct loop terminator**
- **Hooks = deterministic; prompts = probabilistic**
- **Context isolation = subagents start clean**
- **Central routing = observability + consistent errors**
