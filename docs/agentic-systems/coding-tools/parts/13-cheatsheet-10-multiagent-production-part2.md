---
title: "Multi-Agent Production Patterns — Part 2"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-10-multiagent-production-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

# Multi-Agent Production Patterns — Part 2

**This is Part 2 of 2. [Return to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/13-cheatsheet-10-multiagent-production) for core patterns and state management.**

## CITATION SYSTEM: COMPLETE IMPLEMENTATION

### Citation object schema (define once, use everywhere)

Include this schema definition in EVERY agent's system prompt that handles sources:

```json
CitationObject = {
  "id": "unique_slug",  // e.g. "bloomberg_2025_q1"
  "type": "document|web|db|api",
  "title": "Source display name",
  "author": "optional",
  "date": "2025-03-01",
  "url": "https://...",  // if applicable
  "page": 47,  // if document
  "tool_call": "search_tool('query')",  // if from MCP tool
  "excerpt": "≤50 word exact quote",
  "confidence": "high|medium|low"
}
```

### Inline citation pattern for agent outputs

Agent instruction: "When you make a factual claim, append [source_id] immediately after the claim. Never make a claim without a citation. If you cannot cite it, mark it [INFERRED] so the reporting agent can flag it for human review."

Example agent output: "Market grew 23% [bloomberg_2025_q1]. Three companies account for 78% of revenue [mckinsey_2024_p47]. The trend is expected to continue [INFERRED]."

Reporting agent:
- Replaces [source_id] with footnote numbers
- Flags all [INFERRED] for human verification
- Appends bibliography from citation_registry

### Citation registry — orchestrator implementation

```python
class CitationRegistry:
    def register(self, source: CitationObject):
        if source.id not in self.sources:
            self.sources[source.id] = source

    def merge_from_agent(self, agent_result):
        # Each subagent returns its own citations[]
        for cite in agent_result.citations:
            self.register(cite)

    def to_prompt_context(self):
        # Compact form for passing to synthesis/reporting
        return {id: {title, url, page} for id, src in self.sources.items()}
```

### Multi-source deduplication

**Problem:** agent_1 and agent_3 both cite same document with slightly different IDs or titles

**Solution:** Normalize IDs before registering:

```python
def normalize_source_id(title, url):
    # Hash URL or normalize title to dedup
    return slugify(title)[:30] + "_" + hash(url)[:6]
```

OR: Instruct agents to use canonical IDs: "Source IDs must use this format: `{author_surname}_{year}_{topic_slug}`. Example: mckinsey_2024_market_report"

**[INFERRED] flag:** When an agent makes a claim without a source, require it to mark [INFERRED]. Reporting agent highlights these for human review before publication.

## ERROR RECOVERY IN MULTI-AGENT SYSTEMS

### Failure mode taxonomy

- **Subagent timeout:** Return is_error: true with error="timeout". Orchestrator marks task failed, queues retry.
- **Schema violation:** Subagent returns wrong format. Validate, retry with stricter schema prompt. After 2 retries → use partial or skip.
- **Context overflow:** Compact before subagent receives too-large input. Split input into smaller Tasks.
- **Tool MCP failure:** PostToolUse hook catches error. Subagent retries with alternative tool or graceful degrade.
- **Citation missing:** Validate return has citations[]. If not: retry with citation-enforcement prompt. Mark output [NEEDS_CITATION].
- **Partial batch failure:** Track which doc IDs failed. After primary pass, run retry pass on failed IDs only.

### Retry strategy

```python
for attempt in range(3):
    result = run_subagent(task, prompt)
    if validate_schema(result):
        break
    if attempt == 0:
        prompt += "\nReturn ONLY valid JSON."
    elif attempt == 1:
        prompt = STRICT_SCHEMA_PROMPT  # nuclear option
    else:
        result = DEGRADED_RESULT  # mark as incomplete
```

### Checkpoint pattern for long pipelines

Write checkpoint after each batch completes. Enables resume without reprocessing completed work:

```python
checkpoint = {
    "last_completed_batch": 3,
    "processed_doc_ids": ["doc_1".."doc_30"],
    "results_so_far": {
        # ...30 result objects
    },
    "citation_registry": {
        # ...all sources
    },
    "timestamp": "2026-03-12T14:30:00Z"
}

Write("checkpoint.json", checkpoint)

# On restart/resume:
checkpoint = Read("checkpoint.json")
remaining = all_docs - checkpoint.processed_doc_ids
# Continue from doc_31
```

### Graceful degradation levels

- **Level 1:** Full result → all fields populated, citations ✓
- **Level 2:** Partial result → some fields null, [INFERRED] flags
- **Level 3:** Summary only → just a text summary, no structure
- **Level 4:** Skip + log → task_status="failed", human review

Never silently produce nothing — always return something at the degraded level and mark it clearly.

## 6 AGENT ARCHITECTURES — WHEN TO USE EACH

| Architecture | Use When | Citation Handling | Context Risk |
|---|---|---|---|
| Single Agent | &lt;10 docs, simple task, no parallelism needed | Inline — agent holds all | Low |
| Map-Reduce | 10–1000 docs, batch processing, independent items | Schema per subagent → registry | Low (subagents isolated) |
| Pipeline | Sequential stages, each stage needs prior output | Explicit handoff packet each stage | Medium (accumulates) |
| Hub-and-Spoke | Mixed tasks, dynamic routing, varied tools | Orchestrator holds registry | Medium (orchestrator grows) |
| Agent Teams | Workers need to debate/coordinate with each other | Experimental — design carefully | High (3-4× tokens) |
| Worktree Parallel | Same-repo work needing filesystem isolation | Per-branch — merge required | Low (isolated contexts) |

### Architecture selection guide

1. Does the task involve many similar items (docs, files, records)?
   - YES: Map-Reduce (each item = 1 subagent)
   - NO: continue...

2. Do the subtasks need to share findings with each other?
   - YES: Agent Teams (experimental) or Hub-and-Spoke with central state
   - NO: continue...

3. Do the subtasks need to run in a specific order?
   - YES: Pipeline (pass handoff packet at each stage)
   - NO: continue...

4. Do they need filesystem isolation (same repo, different changes)?
   - YES: Worktrees
   - NO: Subagents with Hub-and-Spoke

## ANTI-PATTERNS — THE 12 PRODUCTION KILLERS

- **All-in-one context:** Processing 50 docs in a single agent loop. Context fills at doc N. Use Map-Reduce instead.
- **Citation in prose:** "Sources: [3]" in free text. Reporting agent can't parse it. Use structured citation schema.
- **Assuming inheritance:** Subagent expected to "know" orchestrator's context. Subagents are context-blind — pass everything explicitly.
- **Large subagent output:** Subagent returns 5000-token analysis. Orchestrator fills immediately. Enforce compact return schema.
- **No task tracking:** No status for each doc/task. Can't retry failures. Can't resume. Always track {id, status, result, error}.
- **Text-based stop check:** Checking if response contains "I'm done" to terminate loop. Use stop_reason === "end_turn" — the only reliable signal.
- **Subagent spawns subagent:** Not supported — causes silent failure. Plan agent exists for this reason. Use Agent Teams if cross-agent work needed.
- **No checkpoint saves:** 50-doc batch fails at doc 48. Must restart from scratch. Checkpoint every 10 docs.
- **Unvalidated JSON:** Trusting subagent JSON is always valid. Always validate schema before aggregating. Retry on schema failure.
- **Prompt for compliance:** "Never call delete_file". Use PreToolUse hook for guaranteed enforcement — prompts are probabilistic.
- **Same-file parallel edits:** Two subagents editing src/auth.ts simultaneously → corruption. Use worktrees or assign non-overlapping file sets.
- **Fixed batch parallelism:** "Run 4 parallel, wait for all 4, then next 4" — inefficient. Let Claude self-manage queue for streaming efficiency.

## COMPLETE EXAMPLE: 50-DOCUMENT RESEARCH REPORT WITH CITATIONS

### Phase 1: Setup + Task Decomposition

Orchestrator prompt (Opus 4.6):

```
You are the orchestrator for a document research pipeline. You have 50 documents to analyze.

RULES:
1. Process in batches of 10 using Task tool (parallel)
2. Each Task must use this EXACT return schema (below)
3. Maintain citation_registry - merge all citations from Tasks
4. Track task_status for every document ID
5. Never read full doc yourself - delegate to Tasks

Return schema for each Task:
{
  "doc_id": "string",
  "summary": "≤100 words",
  "key_claims": [{"claim": "", "source_id": ""}],
  "citations": [CitationObject],
  "status": "complete|partial|failed"
}
```

### Task prompt template

```python
f"""
doc_id: {doc_id}
document: {document_content}

Extract per schema. Every claim needs a source_id. If no source exists for a claim, mark source_id as "INFERRED".
Return ONLY raw JSON starting with {{
"""
```

### Phase 2: Map (10 parallel Tasks × 5 batches)

Let Claude manage queue — no fixed parallelism: "Process all 50 documents using the Task tool. Use the task prompt template for each. As each Task completes, immediately add its citations to citation_registry and update task_status. Continue until all 50 are processed or failed."

After each batch of 10:

```python
Write("checkpoint.json", {
    "processed": completed_ids,
    "citation_registry": registry,
    "results": accumulated_results,
    "failed": failed_ids
})
```

If approaching context limit (use /compact):

```
/compact "Preserve: citation_registry, task_status, all result objects. Compress: intermediate reasoning."
```

### Phase 3: Reduce + Report Generation

Retry failed docs first:

```python
if failed_ids:
    retry_pass(failed_ids, stricter_prompt)
```

Pass to synthesis agent:

```python
synthesis_input = {
    "all_results": results_50,  # compact objects
    "citation_registry": registry,  # full source objects
    "report_brief": "Analyze X trends",
    "task": "Synthesize findings. Cite every claim as [source_id]. Mark [INFERRED] where needed."
}
```

Reporting agent receives synthesis + citation_registry:

```python
report_input = {
    "draft": synthesis_result.draft,
    "citation_registry": registry,
    "task": "Replace [source_id] with footnote numbers. Add References section. Flag all [INFERRED]."
}
```

Output: report.docx with full citations ✓

**Context safe:** Each Task has its own context window. Orchestrator only holds 50 × ~500 token result objects — total ~25K tokens. Well within budget.

**Citations intact:** Every claim in final report has a source_id. citation_registry propagated through all boundaries. Reporting agent has full bibliography.

**Fault tolerant:** Checkpoint every 10 docs. Failed docs retried separately. [INFERRED] flags human review needed. No silent data loss.

**Cost efficient:** Tasks use Haiku (cheap, fast). Orchestrator/Synthesis use Opus (complex reasoning). 10x cost reduction on processing step.

## PRODUCTION CHECKLIST — BEFORE DEPLOYING ANY MULTI-AGENT SYSTEM

### Context management

- ☐ Compact return schema: Every subagent has ≤500 token output spec
- ☐ Checkpoint saves: State written to file every N batches
- ☐ /compact plan: Know when to compact and what to preserve
- ☐ Budget allocation: Orchestrator reserves 20% for synthesis
- ☐ No subagent inheritance assumption: All context explicitly passed

### Citation tracking

- ☐ Citation schema defined: CitationObject with id, title, url, excerpt
- ☐ Schema in all agent prompts: Every research agent uses same schema
- ☐ Registry maintained: Orchestrator merges citations from all agents
- ☐ [INFERRED] flag: Uncited claims flagged for human review
- ☐ Registry passed to reporter: Final agent receives full bibliography

### Reliability

- ☐ Task status tracking: {id, status, result, error} for every item
- ☐ Schema validation: All subagent returns validated before use
- ☐ Retry logic: Max 3 retries with escalating prompt strictness
- ☐ Graceful degradation levels: Full → Partial → Summary → Skip
- ☐ stop_reason check: NOT text parsing — never "I am done"

### Safety

- ☐ PreToolUse hooks: Forbidden operations blocked deterministically
- ☐ Plan mode triggers: Destructive ops require human review
- ☐ File isolation: Parallel agents not editing same files
- ☐ No secrets in prompts: API keys / credentials not in agent context
- ☐ Prompt injection check: External docs treated as untrusted input

## CONTEXT OVERFLOW — COMPLETE DECISION TREE

**Q1:** Are you processing multiple similar items (docs/files)?
- YES: Use Map-Reduce. ONE SUBAGENT PER ITEM.
- NO: Continue to Q2

**Q2:** Will accumulated tool results + history exceed ~20K tokens?
- YES: Plan /compact checkpoints at regular intervals
- NO: Single agent is fine, monitor token usage

**Q3:** Does each subagent return too much data?
- YES: Add compact return schema to task prompt. Enforce max_tokens on subagent API calls
- NO: Continue to Q4

**Q4:** Is the orchestrator filling up from result accumulation?
- YES: Write results to RESULTS.md, /compact with "preserve: citation_registry, task_status"
- NO: Continue to Q5

**Q5:** Are you resuming a session where files changed?
- YES: Start fresh session + explicit context of changes
- NO: Safe to resume

**Q6:** Multiple agents editing the same file simultaneously?
- YES: Assign non-overlapping file sets OR use worktrees
- NO: Safe for parallel execution

### Emergency context recovery

Context is nearly full, work not done:

1. SAVE STATE IMMEDIATELY: `Write("emergency_state.json", full_state_object)`
2. COMPACT with specific preservation: `/compact "CRITICAL - preserve: - citation_registry (complete) - task_status for all 50 docs - accumulated results array - failed_ids list Discard: all intermediate tool call outputs"`
3. VERIFY state survived compaction: `Read("emergency_state.json")` restore if needed
4. CONTINUE from where left off: "Continue processing docs 23-50. State is in emergency_state.json."
