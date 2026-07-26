---
title: "Claude & GitHub Agents: Best Practices Guide (v2) — Part 1"
date: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: claude-agents-best-practices
doc_type: guide
supersedes: ["../../docs/coding-tools/claude/claude_agents_best_practices_v2.md"]
tags: ["coding-tools", "agents", "best-practices"]
---

**Claude & GitHub Agents** Best Practices Guide — v2 Enriched Edition.

*Skills · Hooks · Plugins · MCP · Routing Design · Agent Teams · Anti-Patterns · Token Optimization*

**April 2026** · Based on Anthropic Official Docs, Community Research & Production Data.

This v2 edition incorporates the **April 2026 Claude Code changelog**, the newly published **Dive-into-Claude-Code architectural analysis** (arXiv 2604.14228), official Anthropic best-practices documentation, production patterns from the awesome-claude-code community (35.9K I), and a comprehensive anti-pattern catalog drawn from real-world failure modes. New sections cover **Routing Design**, **Agent Teams**, and the **Explore-Plan-Execute pipeline**.

# Claude & GitHub Agents: Best Practices Guide (v2)

|**01**|**Architecture Deep Dive**|
|---|---|
|**02**|**Agent Skills — v2 Best Practices**|
|**03**|**Routing Design & Subagents**|
|**04**|**Hooks — All 27 Events**|
|**05**|**MCP & Plugins**|
|**06**|**CLAUDE.md & Context Engineering**|
|**07**|**Token & Cost Optimization**|
|**08**|**GitHub Actions & CI/CD**|
|**09**|**Security — CVEs & Hardening**|
|**10**|**Anti-Patterns Catalog**|
|**11**|**Latest Additions (Apr 2026)**|
|**12**|**Quick Reference & Checklists**|

|ReAct loop, 9-step pipeline, 5-layer compaction, 98.4% infra rule|
|---|
|SKILL.md mastery, description engineering, compaction budget,<br/>SkillKit|
|Explore-Plan-Execute, domain routing, Agent Teams, model<br/>selection|
|Handler types, async, HTTP, security gates, PostToolUseFailure|
|Tool design, ToolSearch, 35-tool problem, Google gws, SkillKit|
|9-source context window, 5 compaction shapers, .claudeignore|
|6-tier stack, cache-aware rate limits, Agent Teams cost math|
|Workflow patterns, GitLab/Bitbucket support, OpenTelemetry|
|April 2026 CVEs, Bash permission hardening, MCP rug pull|
|20 documented failure modes with fixes from official docs|
|New repos, skills, Agent Teams, claude-devtools, SkillKit|
|Setup checklist, decision trees, env vars, cost math|

## **01**

## **Architecture Deep Dive**

A 2026 source-level analysis of Claude Code v2.1.88 (~1,900 TypeScript files, ~512K LOC) reveals a counterintuitive truth: **only 1.6% of the codebase is AI decision logic** . The other 98.4% is deterministic infrastructure — permission gates, context management, tool routing, and recovery logic.

##### **Architectural Insight**

The agent loop is a simple ReAct-pattern while-loop. The real engineering complexity lives in the systems around it: 5 compaction shapers, 9 context sources, 27 hook events, and a 7-layer safety system. Build your agents the same way — keep AI narrow, infrastructure wide.

## **The 9-Step Pipeline Per Turn**

|**Step**|**Name**|**What It Does**|
|---|---|---|
|1|Settings resolution|Merge user/project/org settings, resolve conflicts|
|2|State initialization|Session state, active subagents, permission cache|
|3|Context assembly|Pull from 9 ordered sources (CLAUDE.md, skills, history...)|
|4-8|5 Compaction shapers|Budget Reduction→Snip→Microcompact→Context Collapse→Auto-Compact|
|9|Model call + dispatch|Tool requests→Permission gate→Execution→Stop condition check|

## **The 5-Layer Compaction Pipeline**

Before every model call, five shapers run sequentially — cheapest first. Each targets a different type of context pressure:

|**Layer**|**Name**|**Triggers When**|**Cost**|
|---|---|---|---|
|1|Budget Reduction|Individual tool output overflows size limit|~0 tokens|
|2|Snip|Conversation too deep temporally|~0 tokens|
|3|Microcompact|Cache overhead exceeds threshold|Low|
|4|Context Collapse|History extremely long|Medium|
|5|Auto-Compact|Semantic compression needed (last resort)|High|

##### **Context Rot — Real Threshold**

Quality degrades at 20-40% context full, NOT 80-90% as commonly assumed. Set CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60 to trigger compaction before degradation. The 1M token window on Opus 4.7 is large but does not eliminate this degradation curve.

## **The 9 Context Sources (Ordered)**

Claude Code builds the context window from 9 ordered sources. Understanding this order is critical for debugging unexpected behavior:

- **1.** System prompt (deterministic — always obeyed)
- **2.** Managed settings / org-level policies
- **3.** Project CLAUDE.md (delivered as **user context** — probabilistic compliance, not system prompt!)
- **4.** User-level CLAUDE.md (~/.claude/CLAUDE.md)
- **5.** Active skills (up to 25K shared token budget, most recent first)
- **6.** Subagent system prompts (isolated per subagent)
- **7.** Tool schemas / MCP tool definitions
- **8.** Conversation history (with compaction)
- **9.** Current turn input + tool results

##### **Critical: CLAUDE.md is NOT the System Prompt**

CLAUDE.md instructions are delivered as user context, giving probabilistic compliance. For deterministic enforcement, use Hooks. For standing domain knowledge, use Skills. CLAUDE.md is for project conventions Claude gets wrong without it — keep it under 80 lines.

## **Five Workflow Patterns (Anthropic Canonical)**

|**Pattern**|**Description**|**Claude Code Implementation**|
|---|---|---|
|Prompt Chaining|Output of one call feeds next|Sequential skills with context: inline|
|Routing|Classify input→route to specialist|Subagent descriptions as routing rules|
|Parallelization|Independent tasks run concurrently|Parallel tool calling or Agent Teams|
|Orchestrator-Workers|Master delegates to workers|Main agent + subagents (primary pattern)|
|Evaluator-Optimizer|Output critiqued and improved|Stop hook→evaluate→re-invoke loop|

## **02**

## **Agent Skills — v2 Best Practices**

Skills are the primary mechanism for giving Claude domain expertise. The open standard (Dec 2025) means the same `SKILL.md` works across Claude Code, `claude.ai`, the API, Cursor, Gemini CLI, Codex CLI, and Antigravity IDE. The SkillKit marketplace (Apr 2026) now offers 400,000+ skills.

## **SKILL.md — Full Frontmatter Reference**

```
---
name: financial-analysis        # Unique identifier (used for /slash-command)
description: |                  # THE MOST IMPORTANT FIELD — Claude's routing key
  Analyze financial statements and generate Excel reports.
  Use PROACTIVELY when user mentions revenue, P&L, EBITDA, balance sheet,
  cash flow, or asks to 'analyze numbers'. Do NOT use for simple arithmetic.
invocation: auto                # auto | explicit | none
agent: Explore                  # Explore | Plan | general-purpose | custom-name
context: fork                   # fork (isolated) | inline (main context)
allowed-tools: Bash(python3 *), Read, Write
disallowed-tools: Bash(rm *), Bash(curl *)
model: claude-haiku-4-5         # Override model for this skill
permissionMode: plan            # plan | acceptEdits | bypassPermissions
mcpServers:                     # MCP servers available to this skill
  - name: excel-mcp
    url: http://localhost:8100
---
# Financial Analysis Skill
## Dynamic Context Injection (runs before skill loads)
Current date: !`date +%Y-%m-%d`
Python version: !`python3 --version`
## Instructions
You are a CFO-level financial analyst. Follow this exact pipeline:
1. Load file with Read tool
2. Extract: Revenue, COGS, Gross Margin %, EBITDA, FCF
3. Identify anomalies (flag with [ANOMALY] prefix)
4. Generate Excel via xlsx skill
5. Return structured JSON summary
NEVER invent numbers. Confidence score required (0-100).
```

## **Description Engineering — The Routing Key**

The description field is Claude's routing key for auto-invocation. Poor descriptions cause skills to never fire or fire on everything:

|**Pattern**|**Bad**|**Good**|
|---|---|---|
|Trigger phrase|'Handles documents'|'Use PROACTIVELY when user asks to create Excel (.xlsx) or analyze spreadsheet data'|
|Negative boundary|(none)|'Do NOT use for CSV-only tasks, simple text tables, or Google Sheets'|
|Scope precision|'Financial stuff'|'Income statements, balance sheets, cash flow — NOT general math or budgets'|
|Action verbs|'For reports'|'Generates, analyzes, extracts, transforms, validates'|
|Negative examples|(none)|'Examples that should NOT trigger: word count, sorting a list, unit conversion'|

## **SkillTool vs AgentTool — Critical Distinction**

Not all skill invocations are equal. The context field determines which mechanism is used:

|**Field**|**context: inline (SkillTool)**|**context: fork (AgentTool)**|
|---|---|---|
|Effect|Injects into current context window|Spawns isolated context window|
|Token impact|Consumes from main budget|Separate budget, returns summary only|
|Use for|Standing instructions, quick lookups|Heavy research, file exploration|
|Compaction|Shared 25K skill budget|Completely isolated|
|Can modify files?|Yes (inherits permissions)|Only with allowed-tools: Write|

## **Pre-built Skills (Updated Apr 2026)**

|**Skill ID**|**Purpose**|**API Beta**|**Installs**|
|---|---|---|---|
|pptx|Professional PowerPoint presentations|skills-2025-10-02|–|
|xlsx|Excel with formulas/charts/pivot tables|skills-2025-10-02|–|
|docx|Word documents with rich formatting|skills-2025-10-02|–|
|pdf|PDF analysis and extraction|skills-2025-10-02|–|
|claude-api|Up-to-date API reference, SDK docs|Bundled|–|
|frontend-design|Distinctive UI avoiding 'AI slop' aesthetics|Bundled|277K+|

## **03**

## **Routing Design & Subagents**

Routing is the highest-leverage design decision in any multi-agent system. Claude Code routes via subagent descriptions, model selection per agent, and the `Explore-Plan-Execute` pipeline. Getting this right prevents the two most common failures: context bloat and wrong model for the task.

## **The Explore-Plan-Execute Pipeline (Official Pattern)**

The canonical routing pattern from Anthropic's internal teams and the official best-practices docs:

```
# CLAUDE.md — Agent Delegation Rules
## Routing Policy
### Explore-Plan-Execute pipeline
For ANY task touching >3 files or involving refactoring:
1. Invoke @explore subagent to map relevant files (read-only, Haiku)
2. Feed output to @plan subagent with specific scope
3. Present plan to user for approval
4. Only then invoke @execute with the approved plan as context
### Direct execution (skip pipeline)
- Quick targeted fix: 1 file, &lt;20 lines
- File already open in conversation context
- Tasks needing frequent back-and-forth
### Domain routing (parallel)
For features spanning multiple domains, spawn parallel agents:
- Frontend (React/CSS): @frontend-agent (Haiku)
- Backend (Node/DB): @backend-agent (Sonnet)
- Security review: @security-agent (Opus)
```

## **Built-in Subagents (2026)**

|**Agent**|**Default Model**|**Tools**|**Auto-invoked When**|
|---|---|---|---|
|Explore|Haiku 4.5|Read, Grep, Glob (read-only)|Search/understand codebase without changes|
|Plan|Haiku 4.5|Read, Grep, Glob (read-only)|Plan mode — codebase research before strategy|
|General-purpose|Sonnet 4.6|Full tool access|Complex multi-step tasks needing both exploration and modification|

## **Custom Subagent Design**

```
# .claude/agents/security-reviewer.md
---
name: security-reviewer
description: |
  Specialized security code reviewer. Use PROACTIVELY on any changes
  to auth/, payments/, api/, or middleware/. Checks for OWASP Top 10,
  credential exposure, and injection vulnerabilities.
  Do NOT use for: linting, formatting, test writing.
model: claude-opus-4-6          # Best model for security
context: fork                   # Isolated — returns summary only
allowed-tools: Read, Grep, Glob # Read-only — no modifications
permissionMode: plan            # Show intent before acting
---
You are a senior AppSec engineer. Review changed files for:
- SQL injection, XSS, CSRF, SSRF vulnerabilities
- Hardcoded secrets / credentials in code
- Missing authentication/authorization checks
- Insecure deserialization patterns
- Dependency with known CVEs
SEVERITY LEVELS: [CRITICAL] [HIGH] [MEDIUM] [LOW] [INFO]
Return: structured JSON with findings array + risk_score (0-100).
```

## **Agent Teams — Experimental Feature (2026)**

Agent Teams removes the subagent communication bottleneck. Subagents run within a single session and can only report results back. Agent Teams lets teammates message each other, claim tasks from a shared list, and coordinate directly.

```
# Enable Agent Teams (experimental)
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Or enable forked subagents on external builds
export CLAUDE_CODE_FORK_SUBAGENT=1

# Prompt pattern for Agent Teams
# 'Create a team: one for API layer, one for DB migrations, one for test coverage.
#  Coordinate through shared task list.'
```

|**Feature**|**Subagents**|**Agent Teams**|
|---|---|---|
|Communication|Report to main only|Direct teammate-to-teammate messaging|
|Context|Single session|Each teammate: own context window|
|Token cost|~1× single session|~3-4× single session|
|Time savings|Parallel execution|Parallel + coordinated execution|
|Best for|Independent parallel tasks|Tasks needing active collaboration|
|Stability|Production-ready|Experimental (2026)|

##### **Agent Teams Cost Warning**

Agent Teams use roughly 3-4× the tokens of a single session doing the same work sequentially. Plan mode agent teams cost ~7× tokens. Use Agent Teams only when active coordination between specialists is required — not just parallelism.

## **Model Selection Routing Guide**

|**Task Type**|**Model**|**Reason**|
|---|---|---|
|Architecture decisions, security review, final review|Opus 4.7|Complex reasoning, low frequency|
|Feature implementation, debugging, code generation|Sonnet 4.6|Best code quality/cost ratio|
|Explore subagent, file search, codebase mapping|Haiku 4.5|Fast, cheap, read-only tasks|
|Linting, formatting, simple transforms|Haiku 4.5|Near-instant, sub-cent per call|
|Hook evaluation, prompt classification|Haiku 4.5|Semantic classification at minimal cost|
|Agent Teams — leaf workers|Haiku 4.5|Never use Opus for leaf nodes|

##### **The /agents Redesign (Apr 2026)**

The /agents command now has a tabbed layout: a Running tab shows live subagents, the Library tab adds 'Run agent' and 'View running instance' actions. Use /agents to monitor multi-agent sessions in real time.

## **04**

## **Hooks — All 27 Events (2026)**

Hooks are the deterministic enforcement layer. The April 2026 release expanded hooks significantly: 27 events across 5 categories, 4 execution types, PostToolUseFailure now included, and duration_ms in PostToolUse inputs.

## **27 Hook Events — Categorized**

|**Category**|**Event**|**Can Block?**|**New in 2026?**|
|---|---|---|---|
|User Input|UserPromptSubmit|Yes|–|
|Tool Lifecycle|PreToolUse|Yes|–|
|Tool Lifecycle|PostToolUse|No|duration_ms added|
|Tool Lifecycle|PostToolUseFailure|No|NEW|
|Agent Control|Stop|No|–|
|Agent Control|SubagentStop|No|–|
|Agent Control|AgentStart|No|–|
|Agent Control|AgentStop|No|–|
|Context|PreCompact|No|–|
|Context|PostCompact|No|–|
|Notification|Notification|No|–|
|Monitoring|StatusLine|N/A (display only)|–|

## **4 Handler Types**

|**Type**|**How It Works**|**Best For**|**Error on Failure**|
|---|---|---|---|
|command|Shell script via stdin/stdout, exit codes|Local security gates, formatting|Blocks Claude (non-async)|
|http|POST to web server, JSON body+response|Team-wide policy servers, remote validation|Non-blocking (2xx required to block)|
|prompt|Sends to Claude model for semantic eval|AI-based code review, quality gates|Depends on fast model response|
|agent|Spawns subagent with Read/Grep/Glob|Deep verification, complex analysis|Non-blocking|

## **Async Hooks (Jan 2026)**

```
# Run in background without blocking Claude
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "node notify-slack.mjs",
        "async": true,       // Fire-and-forget
        "timeout": 30        // Still has timeout
      }]
    }]
  }
}
```

## **PostToolUseFailure — New in 2026**

The new PostToolUseFailure event fires when a tool execution fails. It now also receives duration_ms in its input payload, enabling performance-aware error handling:

```
#!/usr/bin/env python3
# PostToolUseFailure hook — log failures + alert on slow timeouts
import json, sys, os
hook = json.load(sys.stdin)
tool = hook.get('tool_name', 'unknown')
error = hook.get('error', '')
duration_ms = hook.get('duration_ms', 0)  # NEW in 2026
# Alert on slow failures (likely timeouts, not logic errors)
if duration_ms > 5000:
    print(f'SLOW_FAILURE: {tool} failed after {duration_ms}ms: {error}',
          file=sys.stderr)
# Log all failures for debugging
with open('/tmp/claude-hook-failures.log', 'a') as f:
    f.write(json.dumps({'tool': tool, 'error': error, 'ms': duration_ms}) + '\n')
```

## **Security Gate — Bash Hardening (Apr 2026)**

The April 2026 changelog patched multiple Bash permission bypasses. Your PreToolUse hook must now handle compound commands, env-var prefixes, redirects, and piped cd segments:

```
#!/usr/bin/env bash
# secure_bash_gate.sh — hardened after Apr 2026 CVEs
INPUT=$(cat)
CMD=$(echo $INPUT | python3 -c 'import sys,json; print(json.load(sys.stdin)["tool_input"].get("command",""))')
# Block dangerous patterns (expanded post-CVE)
DANGEROUS=('rm -rf' 'curl | bash' 'wget | sh' '/dev/tcp' 'base64 -d' 'eval' 'exec'
           '&&' '||'  # Compound commands — now caught
           'ANTHROPIC_API_KEY='  # Env-var prefix bypass — now caught
          )
for pattern in "${DANGEROUS[@]}"; do
  if echo "$CMD" | grep -qF "$pattern"; then
    echo '{"decision":"block","reason":"Blocked by security policy"}'
    exit 0
  fi
done
echo '{"decision":"approve"}'
```

## **05**

## **MCP & Plugins**

MCP (Model Context Protocol) tools load their definitions directly into context. The GitHub MCP server alone carries 35 tools (~26K tokens of definitions). At scale, MCP tool definitions overload the context window — this is 'the 35-tool problem'.

## **The 35-Tool Problem & ToolSearch**

Anthropic's solution (2026): the **ToolSearch tool** . Instead of loading all tool definitions upfront, Claude can discover tools on demand — reducing initial context overhead dramatically:

```
# Enable ToolSearch in API calls
response = client.messages.create(
    model='claude-sonnet-4-6',
    extra_headers={'anthropic-beta': 'token-efficient-tools-2025-02-19'},
    tools=[
        {'type': 'tool_search_20250515', 'name': 'tool_search'},  # Discovery tool
        # Only add tool definitions Claude actually needs
        {'name': 'get_file', 'description': 'Read a file...', 'input_schema': {...}},
    ],
    messages=[{'role': 'user', 'content': user_message}]
)
# ToolSearch ranking fix (Apr 2026): pasted MCP tool names now surface
# the actual tool instead of description-matching siblings
```

## **MCP Tool Design Rules**

|**Rule**|**Description**|**Impact if Violated**|
|---|---|---|
|Self-contained|Complete, unambiguous description. Don't rely on Claude's world knowledge|Wrong tool selected|
|Non-overlapping|Never two tools handling the same input|Non-deterministic selection|
|Explicit params|Clear types, constraints, examples. Avoid optional params|Malformed calls|
|Negative examples|Include what NOT to use the tool for (critical boundary definition)|Over-triggering|
|PROACTIVELY signal|'Use PROACTIVELY when...' prefix for auto-selection|Under-triggering|
|Limit total tools|Target &lt;20 tools per server (Manus, Claude Code use ~12-20)|Context bloat|

## **Plugin Manifest — 10 Component Types**

Claude Code plugins (2026) accept 10 component types in a single manifest:

- commands
- agents
- skills
- hooks
- mcp_servers
- lsp_servers
- output_styles
- channels
- settings
- user_config

## **Google gws — New MCP Server (Mar 2026)**

##### **Google Workspace MCP (gws)**

Released March 2026, hit 4,900 GitHub stars in 3 days. One command gives your agent full access to Drive, Gmail, Calendar, and Sheets via a built-in MCP server. Install: npm install -g @googleworkspace/cli && gws mcp -s drive,gmail,calendar,sheets

## **Concurrent MCP Startup (Apr 2026)**

Subagent and SDK MCP server reconfiguration now connects servers in parallel instead of serially. Faster startup when both local and claude.ai MCP servers are configured (concurrent connect now default). Resources/templates/list is deferred to first @-mention — reducing startup latency further.

## **06**

## **CLAUDE.md & Context Engineering**

Context Engineering is the discipline of optimizing token utility within LLM constraints. The CLAUDE.md + .claudeignore pair is the project-level control surface. Memory is file-based — fully inspectable, editable, and version-controllable (no vector DB required).

## **CLAUDE.md Rules — Official Anthropic Guidance**

- **Under 80 lines** — loaded every turn; ruthlessly prune
- **Corrections only** — never repeat what Claude already knows
- **Use imperative language** — 'ALWAYS run tests' not 'prefer to run tests'
- **Architecture, not tutorials** — key dirs, naming conventions, non-obvious decisions
- **Reference skills, not inline** — 'See /financial-analysis for P&L rules'
- **Hooks > CLAUDE.md for enforcement** — CLAUDE.md = probabilistic; hooks = deterministic

## **Optimal CLAUDE.md Template**

```
# Project: MyApp  [KEEP UNDER 80 LINES]
## Architecture (non-obvious only)
- Frontend: Next.js 14 + TypeScript (src/app/)
- Backend: Node.js + Express (src/api/)
- DB: PostgreSQL + Prisma (prisma/schema.prisma)
- Auth: NextAuth.js — use @auth-review subagent before modifying

## Non-Obvious Rules (corrections only)
- API responses MUST use ApiResponse<T> wrapper (src/types/api.ts)
- Never import from 'lodash' directly — use src/utils/lodash.ts re-exports
- .env.local NEVER committed — secrets in Vault, not env vars in code
- Component max 200 lines — split larger ones

## Required Commands
- ALWAYS run: npm test && npm run type-check before committing
- Build: npm run build (check for type errors first)
## Subagent Routing
See agent delegation rules in .claude/agents/ directory.
# [Total: ~25 lines — well under 80 limit]
```

## **.claudeignore — Context Scoping**

```
# .claudeignore — Exclude from Claude's file access
node_modules/       # Never needed
dist/ build/ .next/ # Generated artifacts
*.log *.lock        # Logs and lockfiles
coverage/           # Test coverage reports
.git/               # Git internals
data/raw/           # Large raw data files
*.csv *.parquet     # Data files (use dedicated data skill instead)
src/generated/      # Auto-generated code
*.d.ts              # TypeScript declarations
__pycache__/ .venv/ # Python artifacts
```

##### **Memory Architecture**

Claude Code uses file-based memory — no vector DB. This means memory is inspectable, editable, diffable, and version-controllable via git. Use ~/.claude/memory/ for personal persistent context across projects. Use .claude/memory/ for project-specific persistent context shared by the team.

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/36-claude-agents-best-practices-part2) for MCP, context engineering, and token optimization.**

## Related

- [Claude Architect Foundations: Best Practices & Anti-Patterns Guide](32-claude-best-practices.md) — the foundational best-practices guide this v2 updates.
- [Claude Code, Hooks, Skills & Subagents](27-module-5-claude-code-agents.md) — the technical reference for the agent features covered here.
