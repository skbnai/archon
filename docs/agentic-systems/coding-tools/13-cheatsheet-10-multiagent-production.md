---
title: "Multi-Agent Production Patterns"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-10-multiagent-production
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/Cheatsheet_10_MultiAgent_Production.md
---

# Multi-Agent Production Patterns

Complete field guide for building agent systems that work at production scale — covering every failure mode, design pattern, and fix for real scenarios.

- Context fills mid-batch
- Citations lost across agents
- Reporting agent missing sources
- State not passed on handoff
- Subagent token budget blowout
- Fan-out/fan-in aggregation
- Partial failure in pipeline
- Map-reduce over documents

**Failure Modes:** 12  
**Patterns:** 8  
**Architectures:** 6

## PROBLEM 1: CONTEXT OVERFLOW MID-BATCH

*For example, filling at doc 22/50*

### Why It Happens

Every document read + every LLM response + every prior tool result accumulates in context. By doc 22, the window is full — Claude sees only recent history, loses earlier docs.

### Root Fix

Never process multiple documents inside one agent's single loop. Use a **Map-Reduce architecture** — one subagent per document, each with its own clean context.

**Anti-pattern — everything accumulates in ONE context:**

```python
for doc in documents[0:50]:
    result = claude.read(doc)  # +doc tokens
    summary = claude.summarize(result)  # +summary tokens
    findings.append(summary)  # context GROWS every iteration
    # Context explodes by doc 22 → truncation → lost findings
```

**Correct: Map-Reduce — subagent per document:**

Orchestrator spawns one Task per document (up to 10 parallel):

- `Task(doc_1)` → `{ summary, key_points, metadata, source_id: "doc_1" }`
- `Task(doc_2)` → `{ summary, key_points, metadata, source_id: "doc_2" }`
- ... up to doc_50 (queued, max 10 parallel)

Each subagent has a FRESH context window for its 1 doc. Returns a COMPACT structured result (not full doc content). Orchestrator context only holds 50 small result objects.

**Prompt for each Task:**

"Read ONLY this document. Extract: `{summary (≤100 words), key_claims: [], entities: [], source_id}`. Return JSON. Nothing else."

### ORCHESTRATOR COLLECTS RESULTS

Orchestrator receives 50 compact JSON objects. Each is ~200 tokens vs 5000 tokens for raw doc. Total: 50 × 200 = 10,000 tokens — fits easily.

```json
results = [
  {
    "source_id": "doc_1",
    "summary": "...",
    "key_claims": [...]
  },
  {
    "source_id": "doc_2",
    "summary": "...",
    "key_claims": [...]
  }
  // ... × 50
]
```

Now pass to synthesis agent with full citation provenance.

**Context budget rule:** Each subagent should return ≤500 tokens. If 50 subagents each return 500 tokens, orchestrator receives 25,000 tokens total — still safe.

## PROBLEM 2: CITATIONS UNAVAILABLE IN REPORTING AGENT

### Why It Happens

Research subagents hold citations in their own isolated context. When they return a text summary to the orchestrator, citations are stripped. The reporting agent receives findings without sources.

### Root Fix

Citations must be part of the structured return schema. Every agent that finds evidence must return source IDs alongside the finding — not embedded in prose.

**Wrong: Citation in prose → lost:**

Research agent returns this — citations buried in text:

- "The market grew 23% (Source: McKinsey 2024 Report)."
- "Revenue hit $4.2B (per Bloomberg Terminal, March 2025)."

Reporting agent receives text → cannot extract structured cites. Result: report has no footnotes, no source links.

**Correct: Citation as structured field in return schema:**

Define this schema for EVERY research subagent:

```json
return {
  "findings": [
    {
      "claim": "Market grew 23% in 2024",
      "confidence": "high",
      "source": {
        "id": "mckinsey_2024_q3",
        "title": "McKinsey Global Report Q3 2024",
        "page": 47,
        "url": "https://...",
        "quote": "exact supporting text ≤50 words"
      }
    }
  ]
}
```

Reporting agent prompt: "Each finding in the findings array has a source.id field. When writing the report, cite as [source.id] after each claim. Append a References section listing all source objects."

**Citation chain rule:** source_id must propagate through every agent boundary — research → orchestrator → synthesis → reporting. If any agent drops it, it's gone forever.

### CITATION REGISTRY PATTERN (for large systems)

Orchestrator maintains a flat citation registry:

```python
citation_registry = {}  # Each subagent return is registered immediately

for finding in agent_result.findings:
    cid = finding.source.id
    citation_registry[cid] = finding.source  # persist

# Reporting agent receives:
# 1. Synthesized findings (with source_id references)
# 2. The full citation_registry lookup table
# → can render complete footnotes
```

## MAP-REDUCE: BATCH DOCUMENT PROCESSING

### Architecture

**ORCHESTRATOR (Opus — planning + synthesis)**
- Splits 50 docs into batches of 10
- Task(doc_1..10): 10 parallel subagents
  - Each: fresh context, 1 doc, returns compact JSON
  - Output: ~500 tokens per agent
- Collects batch 1 results (10 × 500 = 5k tokens)
- Task(doc_11..20): next 10 parallel subagents
  - Repeat for 5 batches total
- **Synthesis Agent:** receives all 50 result objects
  - citation_registry passed alongside
  - Produces final report with full citations

- **Max parallel:** 10 simultaneous Tasks — rest queued automatically
- **Batch strategy:** Don't specify parallelism level → streaming queue (more efficient than fixed batches)
- **Orchestrator budget:** Save 60% of context for result aggregation — don't fill it during mapping
- **Failure handling:** Track success/fail per task ID — retry failed tasks in next batch pass

## PIPELINE PATTERN: SEQUENTIAL AGENT CHAIN

### Architecture — Research → Analysis → Report

- **Stage 1: Research Agent**
  - Input: topic + search queries
  - Output: `{ findings[], citations[], raw_data }`
  - ↓ (explicit context packet passed)

- **Stage 2: Analysis Agent**
  - Input: findings + citations + analysis_brief
  - Output: `{ insights[], patterns[], gaps[], citations[] }`
  - ↓ (same citation IDs carried forward)

- **Stage 3: Synthesis Agent**
  - Input: insights + citations + format_spec
  - Output: `{ draft_report, citation_map }`
  - ↓

- **Stage 4: Reporting Agent**
  - Input: draft + citation_map + style_guide
  - Output: final_report_with_footnotes.docx

**Key rule:** Each stage receives ONLY what it needs — not the full prior conversation. Explicit handoff packets prevent context bloat.

### Handoff packet structure

```json
{
  "stage": "analysis",
  "prior_stage_summary": "Brief summary of what stage 1 did",
  "data": {
    // ...stage 1 outputs
  },
  "citation_registry": {
    // ...all source objects so far
  },
  "task": "Analyze these findings and extract patterns",
  "constraints": {
    "max_output_tokens": 2000,
    "format": "JSON"
  }
}
```

## ORCHESTRATOR DESIGN: HUB-AND-SPOKE

### Core responsibilities

- **Decompose:** Break task into independent subtasks assignable to specialized agents
- **Route dynamically:** Only invoke relevant subagents — not always the full pipeline
- **Pass context explicitly:** Subagents do NOT inherit orchestrator history — pass what they need
- **Maintain registry:** Keep citation_registry, task_status, and partial_results
- **Aggregate results:** Collect all subagent outputs before synthesis pass
- **Handle failures:** Track which subagents failed, retry or degrade gracefully

### Orchestrator context budget

```
System prompt + task spec:        ~2,000 tokens (10%)
Subagent result accumulation:     ~10,000 tokens (50%)
Citation registry:                ~3,000 tokens (15%)
Task status + error log:          ~1,000 tokens (5%)
Reserved for synthesis:           ~4,000 tokens (20%)

Total budget:                     20,000 tokens
```

If approaching limit → /compact before synthesis pass.

**Anti-pattern:** Orchestrator reads every subagent's full working context. Instead, define compact return schemas — orchestrator sees only the summary.

## STATE MANAGEMENT ACROSS AGENT BOUNDARIES

### The fundamental problem

Subagents have NO access to orchestrator conversation history. Every boundary is a context reset. Anything not explicitly passed is invisible.

### What MUST be explicitly passed

- **Task spec:** What the subagent should do, in full
- **Relevant prior results:** Only the subset it needs — not all results
- **Citation registry:** All source objects accumulated so far
- **Constraints:** Output format, max length, required fields
- **Global context:** Company/project context (from CLAUDE.md or system prompt)
- **Task ID:** For result tracking and failure recovery

### Persistent state object pattern

Orchestrator maintains this throughout the session:

```python
state = {
    "session_id": "report_2026_03",
    "tasks": {
        "doc_1": {"status": "complete", "result": {...}},
        "doc_2": {"status": "failed", "error": "timeout"},
        "doc_3": {"status": "pending"},
    },
    "citation_registry": {
        # ...all sources seen so far
    },
    "partial_report": "...",  # built incrementally
    "failed_tasks": ["doc_2"],  # for retry pass
}
```

### Handoff summary pattern (human or agent)

When passing to next agent OR human:

```python
agent_handoff = {
    "completed_by": "research_agent",
    "task_status": "partial — 22/50 docs processed",
    "completed_items": ["doc_1" .. "doc_22"],
    "remaining_items": ["doc_23" .. "doc_50"],
    "findings_so_far": {
        # ...22 result objects
    },
    "citation_registry": {
        # ...all sources found
    },
    "next_agent_task": "Continue from doc_23. Use the citation_registry for all source refs.",
    "blockers": ["doc_7 timeout — retry needed"]
}
```

### Resume pattern after context limit

When orchestrator approaches context limit mid-batch:

1. Save state to RESULTS.md in worktree: `Write("RESULTS.md", json.dumps(state))`
2. Compact with preservation instruction: `/compact "Keep: citation_registry, task_status, partial_report. Discard: raw tool outputs."`
3. Continue — state is now summarized, not lost
4. On resume: `Read("RESULTS.md")` to restore state

## TOKEN BUDGET MANAGEMENT PER AGENT

### Token budget tiers

| Agent Role | Model | Budget |
|---|---|---|
| Orchestrator | Opus 4.6 | 20K–50K in |
| Research agents | Sonnet 4.6 | 8K in, 1K out |
| Doc processing | Haiku 4.5 | 4K in, 500 out |
| Synthesis agent | Opus 4.6 | 30K in, 4K out |
| Reporting agent | Sonnet 4.6 | 15K in, 8K out |

### Routing by complexity

Set subagent model via env var:

```bash
export CLAUDE_CODE_SUBAGENT_MODEL="claude-haiku-4-5-20251001"
```

Main session (orchestrator) uses Opus. Subagents (doc processing) use Haiku. Cost reduction: ~10x on processing step.

For Agent Teams — per-agent model override:

```yaml
agent: code-reviewer
model: claude-sonnet-4-6  # override for this agent
```

### Output size discipline per agent

**Compact return rule:** Subagent output should be ≤10% of its input size. A 5000-token doc should produce a ≤500-token result.

Enforce via prompt: "Return a JSON object. Summary ≤100 words. key_claims ≤5 items. No full quotes."

- **max_tokens parameter:** Set max_tokens on subagent API call to hard-cap output size
- **Schema validation:** Validate return schema — reject oversized responses and retry with stricter prompt
- **Token tracking:** Log usage.output_tokens per subagent — alert if &gt;budget threshold

### Budget exceeded → response

When subagent hits max_tokens:

```python
# stop_reason === "max_tokens"
# → append partial + continue: "Please finish the JSON"
# OR → retry with more constrained output instructions
# OR → use the partial result if schema is satisfied
```

**This is Part 1 of 2. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/13-cheatsheet-10-multiagent-production-part2) for citation systems, error recovery, agent architectures, anti-patterns, complete examples, and production checklist.**

## Related

- [MCP Pipeline Error & Context Handling](14-cheatsheet-11-mcp-pipeline-errors.md) — the companion cheatsheet on MCP-specific production failures.
- [Claude Code Agents & Parallelism](22-cheatsheet-9-agents-parallelism.md) — the parallelism cheatsheet this production guidance builds on.
