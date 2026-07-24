# Split Plan: prompt-engineering-claude-4

## Overview
Source file `../knowledge-docs/docs/coding-tools/claude/prompt-engineering-claude-4.md` (5992 words) split into 2 parts to fit within guide doc_type word cap.

## Split Strategy
Logical split at Section 12 (Context Window Management) to separate foundational prompt engineering techniques from advanced optimization strategies.

## Part 1: 40-prompt-engineering-claude-4.md
**Topic ID:** prompt-engineering-claude-4
**Word Count:** 3,094 words
**Doc Type:** guide
**Sections:**
- Claude 4.x Behavioral Model (changes from 3.x, practical implications)
- Message Structure (role responsibilities, content block types)
- System Prompt Best Practices (effective structure, production example, antipatterns)
- XML Tag Patterns (core patterns, when to use, prompt injection defense)
- Prefill Technique (how to prefill, use cases)
- Few-Shot Examples (when to use, effective structure, diversity requirements)
- Extended Thinking (API specification, budget_tokens parameter, streaming, cost impact)
- Tool Descriptions (effective tool definition, multi-tool orchestration)
- Structured Output (JSON output pattern, validation retry loops)
- Chain of Thought Without Extended Thinking (scratchpad, step-by-step, verification pass patterns)
- Parallelism Patterns (parallel tool calls, fan-out/fan-in pattern, batch prompts)

## Part 2: 40-prompt-engineering-claude-4-part2.md
**Topic ID:** prompt-engineering-claude-4-part2
**Word Count:** 3,009 words
**Doc Type:** guide
**Sections:**
- Context Window Management (what to include vs omit, compression strategies)
- Prompt Caching (cache control syntax, cache breakpoints, caching rules, verification)
- Guardrails in Prompts (input sanitization, output constraints, refusal handling)
- Explainability (requesting reasoning traces, chain-of-thought for audit trails)
- HITL in Prompt Design (surfacing uncertainty, confirmation points, staged execution)
- RAI: Responsible AI in Prompts (bias reduction, demographic neutrality, output safety)
- Evaluation-Driven Prompt Development (eval-first workflow, eval harness, A/B testing, regression suite)
- Best Practices (15 actionable best practices)
- Antipatterns (15 common pitfalls)
- Prompt Templates (summarization, classification, extraction, generation, agent system, RAG with citations)

## Metadata
- **Source:** ../knowledge-docs/docs/coding-tools/claude/prompt-engineering-claude-4.md
- **Original Word Count:** 5,992 words
- **Combined Word Count:** 6,103 words
- **Retention Ratio:** 101.9%
- **Date Created:** 2026-07-24
- **Frontmatter:** Properly formatted with topic_id, domain, doc_type, supersedes, last_reviewed

## Navigation Links
- Part 1 links to Part 2 via split nav link at end
- Part 2 links back to Part 1 via split nav link at end
- Format: `pathname:///archon/agentic-systems/coding-tools/parts/<filename>`
