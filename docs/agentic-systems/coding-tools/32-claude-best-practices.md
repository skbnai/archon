---
title: "Claude Architect Foundations: Best Practices & Anti-Patterns Guide — Part 1"
date: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: claude-best-practices
doc_type: guide
supersedes: ["../../../knowledge-docs/docs/coding-tools/claude/claude-best-practices.md"]
tags: ["coding-tools", "claude", "architecture", "best-practices"]
---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/32-claude-best-practices-part2)**

**CLAUDE ARCHITECT FOUNDATIONS**
**Best Practices & Anti-Patterns Guide**
*A Reference for the Claude Certified Architect – Foundations Exam*
Covering all 5 domains · 25+ task statements · 6 exam scenarios
March 2026

# How to Use This Guide

This document synthesizes Anthropic's official documentation, the Claude Certified Architect exam guide, and current production patterns into a single reference. Each section follows the same structure: a conceptual overview, a best practices vs. antipatterns comparison table, and detailed guidance with real-world context.

| Domain | Key Best Practices |
| --- | --- |
| Domain 1 (27%) | Agentic loop termination · Multi-agent hub-and-spoke · Context passing · Hooks for deterministic enforcement · Task decomposition · Session management |
| Domain 2 (18%) | Tool description quality · Structured MCP error responses · Least-privilege tool distribution · Project vs user MCP scoping · Grep vs Glob selection |
| Domain 3 (20%) | CLAUDE.md hierarchy · Path-scoped rules · Plan mode vs direct execution · Slash commands & skills · CI/CD with -p flag |
| Domain 4 (20%) | Explicit criteria over vague instructions · Few-shot for consistent output · tool_use for schema compliance · Retry loops · Batch API SLA constraints |
| Domain 5 (15%) | Persistent facts blocks · Lost-in-the-middle mitigation · Escalation triggers · Structured error propagation · Provenance preservation |

## **Domain 1 — Agentic Architecture & Orchestration  (27%)**

Agentic systems extend Claude beyond single-turn responses into multi-step, tool-driven loops that gather context, take action, verify results, and repeat. This domain covers how to architect those loops correctly, orchestrate multiple agents, and enforce business rules deterministically.

## **1.1  Agentic Loop Termination**

The core agentic loop pattern is: send request → check stop_reason → if 'tool_use', execute tool and append result → loop back; if 'end_turn', terminate. Every deviation from this pattern introduces fragility.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Terminate on stop_reason === 'end_turn'; continue on 'tool_use'. This is the API contract, not a heuristic. | Parsing Claude's text content for phrases like 'TASK COMPLETE' to detect completion. Natural language signals are unreliable. |
| Append every tool result to conversation history before the next API call so Claude accumulates information across iterations. | Discarding tool results after each step. Each iteration then starts without the findings of prior steps. |
| Set an explicit MAX_ITERATIONS cap in orchestration code. Terminate gracefully and escalate when exceeded. | Unbounded loops with no iteration limit. A stuck agent can run indefinitely, exhausting budget without progress. |
| Implement circuit-breaker logic: detect repeated identical tool calls without state change and escalate rather than retry. | Allowing the agent to call the same tool dozens of times in a row with no detection of the runaway loop. |

## **1.2  Multi-Agent Orchestration**

Hub-and-spoke is the correct topology: ALL communication between subagents routes through the coordinator. Direct subagent-to-subagent communication breaks observability, consistent error handling, and makes debugging nearly impossible.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Route all inter-subagent communication through the coordinator. The coordinator is the single source of truth. | Allowing subagents to communicate directly with each other, creating unobservable side channels. |
| Design coordinator prompts around research GOALS and quality criteria rather than step-by-step procedures. | Over-specifying coordinator procedures, which prevents adaptive task decomposition when subtopics vary in complexity. |
| Emit multiple Task tool calls in a SINGLE coordinator response to achieve parallel subagent execution. | Emitting Task calls across separate turns, which forces sequential execution even when tasks are independent. |
| Set maximum wait times for parallel subagents; proceed with partial results and flag missing coverage explicitly. | Waiting indefinitely for all subagents to return before the pipeline can produce any output. |

| KEY INSIGHT: Coordinator Task Decomposition Determines Coverage The most common multi-agent failure is overly narrow task decomposition by the coordinator — not downstream agent failures. If you research 'creative industries' and the coordinator decomposes into only visual arts subtasks, all downstream agents will execute correctly but the report will still miss music, writing, and film. Always audit your coordinator's subtask generation, not just the quality of individual subagent outputs. |
| --- |

## **1.3  Subagent Context & Isolation**

Subagents start with an empty context window. They do NOT inherit coordinator context, prior subagent outputs, or any findings from other pipeline stages unless those are explicitly passed in their Task prompt.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Explicitly pass all required context into each subagent's Task prompt — prior findings, source materials, constraints, and the specific subtask. | Assuming subagents share context with the coordinator or with each other. They have isolated context windows by design. |
| Include 'Task' in the coordinator's allowedTools configuration to enable subagent spawning. | Expecting the coordinator to spawn subagents without 'Task' in allowedTools. The tool simply won't be available. |
| Pass structured data (key facts, citations, relevance scores) rather than verbose summaries when context budgets are constrained. | Passing entire 3,000-word subagent output verbatim to downstream agents, exhausting their context budgets. |
| Use structured data formats that separate content from metadata (source URLs, dates, document names) to preserve provenance. | Passing mixed content-and-citation strings that downstream agents cannot parse programmatically. |

## **1.4  Hooks for Deterministic Enforcement**

Claude is probabilistic. Prompt instructions have non-zero failure rates. When a business rule requires GUARANTEED compliance — financial thresholds, identity verification, audit logging — hooks provide the determinism that prompts cannot.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use PreToolUse hooks to block disallowed tool calls before execution (e.g., intercept process_refund when amount > $500). | Relying on system prompt instructions ('never process refunds above $500') to enforce financial policy. Will fail at some rate. |
| Use PostToolUse hooks for data normalization — converting Unix timestamps, inconsistent status codes, or mixed formats before the model processes them. | Asking Claude to normalize data formats via instructions. The model occasionally misinterprets edge case formats. |
| Use PostToolUse hooks for audit logging — capturing file paths, content sizes, and timestamps without affecting agent behavior. | Post-hoc filesystem monitoring. Captures events but loses Claude's intent and reasoning context for each action. |

| DETERMINISTIC vs. PROBABILISTIC The exam's most important concept: hooks = deterministic (the code either runs or it doesn't), prompts = probabilistic (a very good model still fails 1–3% of cases at scale). For business logic that cannot tolerate ANY failures — identity verification before financial transactions, security policy enforcement, compliance audit trails — always use programmatic enforcement via hooks. Never rely on prompt instructions alone. |
| --- |

## **1.5  Task Decomposition Strategies**

Two primary strategies: Prompt chaining (fixed sequential steps) and Dynamic adaptive decomposition (subtasks generated based on intermediate discoveries). Choosing correctly determines whether complex tasks succeed or produce incomplete results.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Prompt chaining: use for predictable multi-aspect tasks with known structure (per-file code review → cross-file integration pass). | Using prompt chaining for open-ended tasks with unknown structure. Fixed steps cannot adapt when discoveries reveal unexpected complexity. |
| Dynamic adaptive decomposition: use when the correct next step depends on what the current step discovers (legacy codebase analysis, novel research). | Using step-by-step fixed pipelines for exploratory tasks. The agent cannot adapt when initial assumptions prove incorrect. |
| Split large reviews into focused passes: per-file local analysis + separate cross-file integration pass for data flow. | Single-pass review of 14+ files. Attention dilutes — some files get thorough review, others get superficial attention. |

## **1.6  Session Management**

Named sessions, fork_session, /compact, and --resume are tools for managing expensive, long-running analysis sessions. Use the right tool for the right situation.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use fork_session to branch from a shared analysis baseline when exploring two competing approaches simultaneously. | Exploring divergent approaches sequentially in a single session, polluting earlier analysis with later conclusions. |
| Use /compact during extended sessions to summarize earlier conversation while retaining key findings and continuing work. | Starting a fresh session when context fills — loses all accumulated analysis. /compact preserves discoveries. |
| When resuming after file modifications, explicitly inform the agent which specific files changed for targeted re-analysis. | Resuming a session assuming the agent knows what changed. It will apply stale analysis to modified files. |

## **Domain 2 — Tool Design & MCP Integration  (18%)**

Tool quality is the most under-appreciated factor in agent reliability. A model cannot use a tool well if it cannot understand what the tool does, what it expects, and when to choose it over similar tools.

## **2.1  Tool Descriptions as the Primary Selection Mechanism**

The LLM uses tool descriptions — not the tool name, not the system prompt — as the primary signal for tool selection. Minimal descriptions produce unreliable selection. Every tool needs four elements: what it does, what it accepts, what it returns, and when to use it versus similar tools.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Include input formats accepted, 2–3 example queries, output schema, and disambiguation from similar tools in every description. | 'Gets customer data.' — minimal descriptions cause unreliable selection especially among tools with overlapping names. |
| When a specialist tool is underused in favor of a general one, update the specialist's description to explain WHY it's better for specific cases. | Adding system prompt instructions 'always use the Jira MCP for ticket operations'. Instructions are less reliable than descriptions. |
| Split multi-purpose tools into purpose-specific variants with clear, non-overlapping descriptions. | A single analyze_document tool with a 'mode' parameter covering citation extraction, summarization, and verification. |

## **2.2  Structured Error Responses**

Tool errors must include enough information for the agent to make an intelligent recovery decision. All errors looking identical forces the agent to guess — leading to inappropriate retries or missed escalations.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Return structured errors: errorCategory (transient/validation/business/permission), isRetryable (bool), and a customer-friendly explanation. | Returning generic 'Operation failed' for all error types. The agent cannot distinguish retry-worthy from non-retryable errors. |
| Distinguish valid empty results (query returned no matches) from access failures (service timeout) — they require different coordinator responses. | Returning identical error responses for 'no results found' and 'service unavailable'. The coordinator misclassifies coverage gaps as access failures. |
| For business errors (policy violations), include the specific policy constraint and actionable next steps in the error response. | Returning isError: true with no context for policy violations. The agent can't explain the rejection to the customer. |

| Error Category Reference TRANSIENT: Timeout, service unavailable — retry with backoff. VALIDATION: Invalid input format — ask user to clarify. BUSINESS: Policy violation, data constraint — explain to user, do not retry. PERMISSION: Authorization failure — escalate to admin. Each category requires a different agent response strategy. |
| --- |

## **2.3  Least-Privilege Tool Distribution**

Too many tools degrades selection reliability. Each agent should receive only the tools needed for its designated role. This improves selection accuracy, reduces security risk, and makes agents more predictable.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Assign each subagent only the tools relevant to its role (synthesis agents get synthesis tools, not web search tools). | Giving all agents access to all 18 tools. Selection reliability degrades significantly beyond 4–5 tools. |
| Give high-frequency simple operations a scoped tool (verify_fact) rather than full tool suite access. Handles 85% of cases; coordinator handles the 15% complex cases. | Routing every verification request through the coordinator. Adds 40% latency for cases that could be handled directly. |
| For CI review agents, include only review tools. Deployment tools should NEVER be accessible to review agents. | Giving a CI code review agent access to deployment and database migration tools. Creates risk of unintended production changes. |

## **2.4  MCP Server Configuration**

MCP configuration has two scopes: project-level (.mcp.json, version-controlled, shared with team) and user-level (~/.claude.json, personal, not version-controlled). Credentials must always use environment variable expansion, never hardcoded values.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Use .mcp.json at project root for team-shared MCP servers. Commit to version control so all developers get access on clone. | Configuring shared MCP servers in ~/.claude.json on each developer's machine. New team members miss the configuration. |
| Use `${GITHUB_TOKEN}` syntax in .mcp.json for credentials. Each developer sets the environment variable locally. | Hardcoding credentials in .mcp.json, even with .gitignore. Risks accidental credential exposure across build artifacts. |
| Audit active MCP servers and deactivate those not needed day-to-day. Too many active servers = too many tools = degraded selection. | Configuring 12 MCP servers simultaneously. Tool proliferation causes the same selection problems as 18+ inline tools. |
| Use existing community MCP servers for standard integrations (Jira, GitHub, Slack). Reserve custom servers for proprietary workflows. | Building custom MCP servers for integrations that already have community implementations. Wastes development time and results in less-tested tooling. |

## **2.5  Built-in Tool Selection: Grep vs Glob vs Edit**

Claude Code's built-in tools have precise, non-overlapping use cases. Using the wrong tool for a task is a common source of subtle errors.

| ✅  BEST PRACTICE | ❌  ANTIPATTERN |
| --- | --- |
| Glob (**/*.test.ts) for finding files by NAME pattern. Grep for finding files by CONTENT pattern. Never swap them. | Using Grep to find test files ('search for test'). Returns files containing the word test in their content, not test files by naming convention. |
| Always Read a file before using Edit on it to establish current state. Edit requires accurate anchor text. | Using Edit without a prior Read. Edit may silently no-op or match the wrong occurrence if the file was modified externally. |
| When Edit fails with 'non-unique match', fall back to Read + Write: load the full file, modify in memory, write back. | Repeatedly retrying Edit with the same anchor text after a non-unique match error. It will continue to fail. |
| Combine Glob + Grep for scoped content search: Glob to identify the file set, Grep to search contents within that set. | Using only Grep across all files when you only care about a specific subdirectory or file type. Processes irrelevant files. |

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/32-claude-best-practices-part2) for configuration and workflows.**
