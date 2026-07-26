---
title: "Foundations: What Is a Coding Skill?"
doc_type: concept
domain: agentic-systems
status: current
topic_id: foundations-what-is-a-coding-skill
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/agentic-systems/skill/coding/01-foundations-what-is-a-coding-skill.md
tags:
  - agentic-systems
  - skill
  - coding-tools
  - research
---

# Foundations: What Is a Coding Skill?

## 1.1 Definition

A **Coding Skill** is a discoverable, on-demand-loaded package of procedural knowledge — a `SKILL.md` file (YAML frontmatter + Markdown body) plus optional scripts, templates, and reference material — that a coding agent loads into context only when a developer's request matches the skill's declared purpose. It is the coding-assistant-world instantiation of the same Agent Skills open standard (agentskills.io) used by enterprise business agents, and by mid-2026 it is read natively by GitHub Copilot, Claude Code, Claude Desktop, VS Code (Copilot agent mode), OpenAI Codex CLI, Cursor, Gemini CLI/Antigravity, and dozens of smaller tools.

The mechanism is identical to the enterprise case: **progressive disclosure**. Only the skill's `name` and `description` sit in context by default; the agent reads the full `SKILL.md` (and, as needed, bundled reference files) only when a task appears to match. GitHub's own documentation states this plainly: skills "load content progressively to keep your context efficient," and the discovery step is literally the agent reading the YAML frontmatter to decide whether to load the body.

## 1.2 Why coding assistants introduced Skills instead of just exposing tools

Before Skills, coding assistants had tools (filesystem, terminal, git) and, at best, a single always-loaded instructions file. This created a real gap: tools tell the agent *what it can technically do*, but not *the team's opinion on how and when to do it well*. A `run_tests` tool doesn't know your project uses the AAA pattern, prioritizes boundary-value cases, and names files `*.test.ts`. Before Skills, that knowledge either lived nowhere (agent improvises, inconsistently) or got crammed into an always-loaded instructions file (context bloat, cost, dilution of the important always-true rules among rarely-needed procedural detail).

SmartScope's guidance on this is a clean summary of the resulting two-plane split now standard across the ecosystem: **Custom Instructions/AGENTS.md are for rules that should always apply** (coding standards, "use tabs not spaces"); **Skills are for specialized workflows that only matter in certain contexts** (a debugging procedure for a specific class of CI failure, a multi-step test-generation methodology). Conflating the two — either stuffing everything into the always-loaded file, or trying to make a skill do the job of a standing rule — is the most common authoring mistake observed across vendor documentation and community guides alike.

## 1.3 Skill vs. every adjacent concept

### Skill vs. Agent

An **Agent** is the runtime/harness (Claude Code, Copilot agent mode, Codex CLI) that plans, selects skills/tools, executes, and validates. A Skill has no independent runtime — it's inert content the agent interprets. One agent can load many skills across a session; a skill does not itself "run."

### Skill vs. Slash Command

A **Slash Command** (`/fix`, `/test`, `/review`) is typically a *shortcut that invokes a specific, predefined prompt or skill directly*, bypassing the agent's own discovery/matching step. GitHub Copilot's `/skillname` and Codex's `$skillname` are exactly this — an explicit invocation path that coexists with automatic, description-based discovery. Frontmatter fields like `user-invokable` and `disable-model-invocation` (seen in Copilot's SKILL.md spec extensions) let an author control whether a skill is reachable only via slash command, only via automatic matching, or both.

### Skill vs. Prompt

A **Prompt** is a single, often one-off, instruction. A Skill is a *versioned, reusable, independently-discoverable* package that may contain many prompts, examples, and procedural steps, structured for repeated reuse across many future tasks and, often, many different team members.

### Skill vs. Tool

A **Tool** is an atomic, typed capability the harness exposes (read file, run shell command, git commit). A Skill is judgment about *when and how* to combine tools to accomplish a class of task. This is the same distinction as the enterprise case (see the companion enterprise research package, file `01`), applied one layer down: a coding agent's tools are lower-level and more uniform (filesystem, terminal, git) than an enterprise agent's tools (business API calls), but the Skill/Tool boundary is conceptually identical.

### Skill vs. Workflow

A **Workflow**, in the coding context, is often an *external, deterministic* process (a GitHub Actions pipeline, a CI/CD gate) that a skill's instructions may reference or trigger but does not itself constitute. A skill can *describe* a workflow in prose ("first run lint, then tests, then open a PR"), but compliance-critical or infrastructure-level workflow steps are usually better encoded as actual CI configuration than trusted to be followed via prose every time.

### Skill vs. Task

A **Task** is typically the unit of work a developer or an issue tracker hands to an agent ("fix bug #4821"). A Skill is reusable knowledge that may apply across *many* different tasks of a similar shape. One task might trigger zero, one, or several skills.

### Skill vs. Command

Overloaded across ecosystems: in some CLIs (Roo Code, Cline), "custom commands" are closer to macros/shortcuts than to full Skill packages; in others (Copilot CLI, Codex), "command" refers to the CLI's own subcommands (`copilot skill list`), unrelated to skill content itself. Always check the specific tool's vocabulary before assuming cross-tool equivalence.

### Skill vs. Extension / Plugin

An **Extension** (VS Code extension, JetBrains plugin) is IDE-level software — it can add UI, commands, language support, and can itself *ship* skills, MCP configs, and rules bundled together, but it is a much larger unit than a Skill. A **Plugin** in the Claude Code / Codex sense is typically a *distribution bundle* that packages one or more skills plus MCP server configuration plus presentation assets (icons, display names) — visible directly in OpenAI's plugin manifest format (`agents/openai.yaml` with `interface`, `policy`, and `dependencies.tools` sections). Skills are content; Plugins/Extensions are the containers that ship content.

### Skill vs. MCP Tool

An **MCP Tool** is a tool exposed over the Model Context Protocol by an external server (a GitHub MCP server's `create_pull_request` tool, a database MCP server's `run_query` tool). A Skill may *declare a dependency* on an MCP tool (OpenAI's skill manifest format explicitly supports a `dependencies.tools` list with `type: mcp`), but the skill itself contains no protocol logic — that's the MCP server's job.

### Skill vs. IDE Action

An **IDE Action** (a VS Code command, a JetBrains intention/quick-fix) is a discrete, often single-keystroke-triggered editor operation, typically deterministic and not LLM-mediated at all, or LLM-mediated but scoped to a single, narrow transformation (rename symbol, extract method). Skills are broader, multi-step, and always LLM-interpreted.

### Skill vs. Background Agent

A **Background Agent** (Cursor's background agents, GitHub Copilot's cloud/coding agent, Devin) is a *deployment mode* — an agent running asynchronously, often in an isolated cloud VM, triggered by an event (issue assignment, scheduled job) rather than an interactive session. Background agents consume Skills exactly as interactive agents do; "background" describes *where and how* the agent runs, not a different content type.

### Skill vs. Recipe / Template

**Recipe** and **Template** are informal, community-facing synonyms often used interchangeably with "Skill" in blog content and marketplaces (e.g., "cookbook," "playbook"). Where a formal distinction exists, a Template is usually a *static* scaffold (boilerplate files) with no procedural instructions, whereas a Skill is *procedural* (instructions the agent actively follows) and may *reference* templates as bundled assets.

## 1.4 Skill vs. AGENTS.md/CLAUDE.md/Rules — the most consequential distinction

This deserves its own subsection because it recurs throughout the whole package (see file `00`, §2 and §5). The field has converged on treating these as genuinely different tools for different jobs:

| | AGENTS.md / CLAUDE.md / Rules | Skill |
| --- | --- | --- |
| **Loading** | Always, every turn | On demand, when description matches |
| **Content** | Stack, conventions, boundaries, verification steps — things true on every task | Deep, specialized procedural knowledge for a specific class of task |
| **Cost model** | Fixed token cost every turn (small file ≈ negligible; large file adds up) | Zero cost until matched; then a one-time load cost |
| **Portability** | AGENTS.md is a genuine cross-tool open standard (28+ tools per the tracking site); CLAUDE.md/GEMINI.md are single-vendor equivalents | SKILL.md is a genuine cross-tool open standard, adopted independently of AGENTS.md |
| **Governance surface** | Usually one file (or a small hierarchy) per repo, reviewed like any other committed file | Potentially many skills, each independently versioned/ownable |

Both are necessary; neither substitutes for the other. The empirical Vercel finding cited in file `00` — skills invoked without an explicit pointer in AGENTS.md were ignored 56% of the time — means in practice the two are not fully independent: **the always-loaded file should actively route to the on-demand file**, not just coexist with it.

## 1.5 When to author a Skill vs. put it in AGENTS.md vs. skip both

1. **Is it true on every single task in this repo?** → AGENTS.md/CLAUDE.md/Rules.
2. **Is it a deep, multi-step procedure only relevant to a specific class of task** (debugging a category of CI failure, a design-to-code workflow, a specific migration pattern)? → Skill.
3. **Is it genuinely reusable across many repos/teams**, not just this one? → Skill, and consider publishing to an org-wide or public marketplace (file `11`).
4. **Is it a one-off instruction for this single conversation?** → Neither; just say it in the prompt.
5. **Does an existing skill already cover this?** → Extend it; don't fork (file `11`).
6. **Would combining this with AGENTS.md make that file unwieldy or slow down every single turn** with content only occasionally needed? → Split it out into a Skill, and add one line to AGENTS.md pointing to it — directly following the Vercel-validated "AGENTS.md as router" pattern.

## Related

- [Agent Skills & Skill Registries — Complete Playbook 2026 (Part 1)](16-agent-skills-complete-playbook-2026.md) — the previous section in this series.
- [Skill Discovery & Execution Lifecycle](19-discovery-and-execution-lifecycle.md) — the next section in this series.
