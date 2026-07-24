---
title: "Claude & GitHub Agents: Best Practices Guide (v2) — Part 2"
date: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: claude-agents-best-practices-part2
doc_type: guide
supersedes: []
tags: ["coding-tools", "agents", "mcp", "context-engineering", "token-optimization"]
---

**This is Part 2 of 3. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/36-claude-agents-best-practices) | [Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/36-claude-agents-best-practices-part3)**

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
|Limit total tools|Target <20 tools per server (Manus, Claude Code use ~12-20)|Context bloat|

## **Plugin Manifest — 10 Component Types**

Claude Code plugins (2026) accept 10 component types in a single manifest: commands, agents, skills, hooks, mcp_servers, lsp_servers, output_styles, channels, settings, user_config.

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

## **07**

## **Token & Cost Optimization**

Combined optimization can reduce monthly API costs by **60-80%** for production agent applications. Average enterprise cost: $13/developer/active day, $150-250/developer/month. 90% of users stay under $30/active day.

## **The 6-Tier Optimization Stack**

#### **Tier 1: Prompt Caching (Biggest Win)**

Cache-aware rate limits (2026): cached tokens no longer count against ITPM limits. This compounds with pricing discounts on cache reads:

```
# Cache system prompt + large knowledge base
response = client.messages.create(
    model='claude-sonnet-4-6',
    extra_headers={'anthropic-beta': 'token-efficient-tools-2025-02-19'},
    system=[{
        'type': 'text',
        'text': SYSTEM_PROMPT + KNOWLEDGE_BASE,
        'cache_control': {'type': 'ephemeral'}  # Cached reads: cheaper + no ITPM
    }],
    messages=conversation_history
)
# Manus team: cache hit rate is their #1 production metric
# Claude Code would be cost-prohibitive without caching
```

#### **Tier 2: Token-Efficient Tool Use**

```
# One header = 20-30% output token reduction
extra_headers={'anthropic-beta': 'token-efficient-tools-2025-02-19'}
# Available: Sonnet 4.6, Opus 4.7, Haiku 4.5
# Combined with caching: 60-80% total reduction
```

#### **Tier 3: Model Tiering**

Obsessing over Opus vs Sonnet is the 4th or 5th most important optimization. Structural decisions (context, isolation, hooks) matter more:

|**Task**|**Model**|**Why**|
|---|---|---|
|Architecture, final security review|Opus 4.7|Most capable, infrequent|
|Feature dev, debugging, code gen|Sonnet 4.6|Best quality/cost ratio|
|Explore/Plan subagents, search|Haiku 4.5|Fast, cheap, read-only|
|Hook evaluation, classification|Haiku 4.5|Sub-cent per call|

#### **Tier 4: Context Management**

- **/clear between tasks** — stale context wastes tokens on every subsequent message
- **CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60** — compact at 60% full, before quality degradation
- **.claudeignore** — exclude node_modules, dist, logs — highest single-file leverage
- **Subagents for exploration** — file reads in subagents return summaries, not raw content
- **Specific file references** — 'Read src/auth/login.ts' beats 'read the auth module'

#### **Tier 5: Preprocessing Hooks**

Hooks run outside model context — zero token cost. Highest ROI preprocessing:

- Filter 10,000-line logs → 50 error lines before Claude sees them
- Pre-summarize large JSON API responses to key fields only
- SkillActivationHook: load only relevant skills based on prompt keywords (21 categories)
- Convert binary files to text summaries before Read tool fires

#### **Tier 6: Automation Safeguards**

```
# Cap automation — prevent runaway costs in CI/CD
claude --max-turns 15 --timeout-minutes 30 'Run test suite'

# Set workspace spend limits
# Console > Workspaces > Claude Code > Spend Limit

# Environment variables for budget enforcement
export CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60
export ANTHROPIC_BUDGET_TOKEN=your-budget-token
```

## **Agent Teams Cost Math**

|**Configuration**|**Token Multiplier**|**When Worth It**|
|---|---|---|
|Single session|1×|Always baseline|
|Subagents (parallel)|~1× (isolated context)|Independent tasks|
|Agent Teams (3 members)|~3-4×|Active coordination needed|
|Agent Teams (plan mode)|~7×|Avoid unless critical|

## **08**

## **GitHub Actions & CI/CD**

The April 2026 Claude Code update brought major CI/CD improvements: --from-pr now accepts GitLab merge-request, Bitbucket pull-request, and GitHub Enterprise PR URLs. OpenTelemetry tracing now honors privacy flags.

## **Multi-Platform PR Integration (Apr 2026)**

```
# .github/workflows/claude-review.yml
name: Claude AI Code Review
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]
jobs:
  review:
    if: "!contains(github.event.pull_request.labels.*.name, 'skip-review')"
    runs-on: ubuntu-latest
    concurrency:
      group: claude-review-${{ github.event.pull_request.number }}
      cancel-in-progress: true
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          model: claude-sonnet-4-6   # Pin — never use 'latest'
          max_turns: 10
          timeout_minutes: 20
          # Works for: GitHub, GitHub Enterprise, GitLab MR, Bitbucket PR (Apr 2026)
          from_pr: ${{ github.event.pull_request.html_url }}
          prompt: |
            Review for: security vulnerabilities, breaking API changes,
            missing tests, performance regressions. Be specific with line refs.
```

## **OpenTelemetry Tracing (Privacy-Aware)**

```
# .env — Privacy-first tracing (Apr 2026)
OTEL_LOG_USER_PROMPTS=false     # Opt-in only (default: off)
OTEL_LOG_TOOL_DETAILS=false     # Opt-in only
OTEL_LOG_TOOL_CONTENT=false     # Opt-in only
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## **CI/CD Pattern Matrix**

|**Pattern**|**Model**|**Trigger**|**Max Turns**|
|---|---|---|---|
|PR Security Scan|Sonnet 4.6|on: push to any branch|8|
|Issue Triage & Label|Haiku 4.5|on: issues opened|3|
|PR Description Generator|Haiku 4.5|on: PR opened (no body)|5|
|Architecture Review|Opus 4.7|on: PR to main only|15|
|Dependency Risk Analysis|Sonnet 4.6|on: dependency update PRs|8|
|Release Notes Generator|Sonnet 4.6|on: push to release/v*|10|
|Test Failure Analysis|Haiku 4.5|on: CI failure|5|

##### **CI Cost Tip**

Add 'skip-review' label support to skip Claude review on docs-only PRs. Use concurrency groups to cancel in-progress reviews when new commits arrive. Together these reduce CI costs 25-35% on active repos.

---

**This is Part 2 of 3. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/36-claude-agents-best-practices) | [Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/36-claude-agents-best-practices-part3)**
