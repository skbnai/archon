---
title: "Claude Architect Foundations: Best Practices & Anti-Patterns Guide — Part 2"
date: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: claude-best-practices-part2
doc_type: guide
supersedes: []
tags: ["coding-tools", "claude", "configuration", "workflows"]
---

**This is Part 2 of 3. [Part 1 ←](pathname:///archon/agentic-systems/coding-tools/32-claude-best-practices) | [Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/32-claude-best-practices-part3)**

## **Domain 3 — Claude Code Configuration & Workflows  (20%)**

Claude Code's behavior is shaped by a hierarchy of configuration files, each with different scope and sharing properties. Understanding what loads when, and for whom, is essential for consistent team behavior.

## **3.1  CLAUDE.md Hierarchy**

Three levels: user (~/.claude/CLAUDE.md, personal, not version-controlled), project (.claude/CLAUDE.md, shared, version-controlled), and subdirectory (CLAUDE.md within directories, scoped to files in that subtree). All active levels load simultaneously.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Put team-shared standards in .claude/CLAUDE.md at project root and commit to version control. | Putting team standards in ~/.claude/CLAUDE.md. New team members get different behavior than existing members. |
| Use @import syntax to share common instruction blocks across multiple CLAUDE.md files without duplication. | Copy-pasting the same instructions into multiple CLAUDE.md files. Changes must be made in every copy. |
| Run /memory to audit which memory files are currently loaded when debugging inconsistent behavior. | Guessing which CLAUDE.md files are active based on the directory structure. /memory shows exactly what's loaded. |

## **3.2  Path-Scoped Rules**

Monolithic CLAUDE.md files load entirely for every session, wasting tokens on irrelevant conventions. .claude/rules/ files with YAML frontmatter path patterns load conditionally — only when editing files matching the glob.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Create .claude/rules/testing.md with paths: ['**/*.test.*'] to apply testing conventions to all test files regardless of directory. | Creating a CLAUDE.md in every directory containing test files. Cannot centrally manage conventions that span the codebase. |
| Split a monolithic CLAUDE.md into topic-specific rule files (testing.md, api-conventions.md, security.md) with path scopes. | A single 1,200-line CLAUDE.md that loads entirely for every session, filling context with irrelevant conventions. |
| Use separate path-scoped files for directory-specific conventions (src/postgres/**, src/mongodb/**) with their respective standards. | A single database.md covering multiple conflicting database conventions that always loads regardless of context. |

## **3.3  Slash Commands & Skills**

Slash commands package repeatable workflows. Skills package domain expertise with progressive disclosure. The key distinction for sharing: .claude/commands/ is project-scoped (version-controlled, shared), ~/.claude/commands/ is personal (not shared).

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Put team slash commands in .claude/commands/ and commit to version control. All developers get them on clone. | Creating shared team commands in ~/.claude/commands/. Not shared via version control — every developer must copy manually. |
| Use context: fork in skill frontmatter for skills that produce verbose intermediate output (codebase analysis). Returns summary only to main conversation. | Running large exploration skills without context: fork. All intermediate output pollutes the main conversation context. |
| Create personal variants in ~/.agents/skills/ with a different name rather than modifying team skills in .agents/skills/. | Editing .agents/skills/ directly for personal customization. Affects all teammates via version control. |
| Use $ARGUMENTS placeholder in skill body and argument-hint in frontmatter to create parameterized skills. | Creating a separate skill file for each module name or variation. Leads to combinatorial skill proliferation. |

## **3.4  Plan Mode vs. Direct Execution**

Plan mode enables safe codebase exploration and architectural design before committing to changes. Direct execution is for well-scoped, simple changes where the correct approach is already known.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Plan mode for: architectural decisions, large-scale refactoring, multi-file changes, tasks where the correct approach depends on codebase analysis. | Using plan mode for every task including simple single-file bug fixes. Adds unnecessary overhead for well-scoped changes. |
| Direct execution for: single-file bug fixes with clear stack traces, adding a known validation check, routine well-defined changes. | Using direct execution for monolith-to-microservices restructuring. Commits to implementation before discovering dependency complexity. |
| When the correct implementation depends on discovering codebase patterns (sync vs async, existing patterns), use plan mode to investigate first. | Directly implementing 'add error handling' without analyzing whether affected transactions are sync or async. |

## **3.5  CI/CD Integration**

Claude Code integrates into CI pipelines via non-interactive mode. The correct flag, output format, and retry logic determine whether the integration is reliable or brittle.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use -p (or --print) flag for non-interactive CI mode: claude -p 'prompt'. Processes prompt, outputs to stdout, exits. | Running claude without -p in CI. The process waits for interactive input and hangs indefinitely. |
| Use --output-format json to produce machine-parseable output. Parse programmatically to check severity, fail builds, extract findings. | Parsing Claude's prose output with regex to detect critical issues. Fragile and misses findings with varied phrasing. |
| Provide existing test files in context when generating tests to prevent duplicate test case generation. | Generating tests without context of existing test suite. Produces duplicate coverage and wastes tokens. |
| Use Message Batches API ONLY for non-blocking jobs (nightly reports, weekly audits). Use synchronous API for pre-merge checks developers wait for. | Switching pre-merge blocking checks to Message Batches for cost savings. 24-hour SLA is incompatible with developer workflow. |

## **Domain 4 — Prompt Engineering & Structured Output  (20%)**

Prompt engineering is the discipline of communicating intent to Claude with enough precision that outputs are consistent, correct, and well-formed. Context engineering — managing everything in the context window including tools, examples, and conversation history — is its natural extension.

## **4.1  Explicit Criteria Over Vague Instructions**

Vague quality descriptors ('thoroughly', 'carefully', 'high-confidence only') produce inconsistent results because they don't specify WHAT to do or avoid. Explicit, enumerated criteria produce consistent, measurable outputs.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Enumerate specific review categories: 'Check for: null pointer dereference, SQL injection, off-by-one errors. Skip minor style issues.' | 'Thoroughly check the code for issues.' Inconsistent depth — some runs detailed, others superficial, no shared definition of thorough. |
| Define escalation criteria by case type: 'Escalate if: customer explicitly requests human, policy is silent on the request, error persists after 2 retries.' | Using sentiment or frustration level as an escalation proxy. Frustrated customers may have simple issues; calm customers may have unsolvable ones. |
| When false positives in one category undermine trust in all categories, temporarily disable that category while improving its prompt. | Keeping a high-false-positive category active. It erodes developer trust in the entire review system, not just that category. |

## **4.2  Few-Shot Examples**

Few-shot examples are the most reliable technique for consistent output format and behavior. Examples show rather than describe — and showing is more reliable than describing.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Wrap examples in <example> tags inside <examples> so Claude distinguishes them from instructions. Include 3–5 examples. | Embedding examples as free-form text mixed with instructions. Claude may treat example content as instructions to follow. |
| After one successful happy-path example, prioritize edge case examples: missing fields, non-standard layouts, ambiguous values. | Adding 5 more happy-path examples. The model already understands the standard case — edge cases are where it fails. |
| For consistently missed behaviors, provide a concrete failing input/output example rather than more detailed prose description. | After 8 iterations of refined prose, still not communicating the edge case. Concrete test cases communicate better than descriptions. |
| For escalation calibration, use few-shot examples showing exactly which case types escalate and which resolve autonomously. | Relying on a separate ML classifier to predict escalation. Over-engineered before few-shot optimization has been fully explored. |

## **4.3  Structured Output via Tool Use**

tool_use with JSON schemas eliminates syntax errors. It does NOT eliminate semantic errors. Two-layer validation is required for production extraction systems.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use tool_use with JSON schema for extraction. Guarantees schema-compliant output, eliminates JSON syntax errors at the source. | Post-processing prose output with a JSON repair library. Treats symptoms, not the cause, and still fails on edge cases. |
| Make schema fields optional/nullable when source documents may not contain the information. | Marking all fields required. Forces the model to fabricate plausible-looking values for absent information (hallucination). |
| Add 'other' + companion detail field to enums for extensible categorization. Prevents misclassification when new types emerge. | Hard-coding a closed enum with no 'other' option. New document types get misclassified as the nearest existing category. |
| Apply application-level semantic validation (line items sum to total, dates are chronological) as a second layer after schema compliance. | Assuming tool_use guarantees semantic correctness. Schemas validate structure, not business logic. |

---

**This is Part 2 of 3. [Part 1 ←](pathname:///archon/agentic-systems/coding-tools/32-claude-best-practices) | [Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/32-claude-best-practices-part3) for validation, retry loops, and batch API guidance.**
