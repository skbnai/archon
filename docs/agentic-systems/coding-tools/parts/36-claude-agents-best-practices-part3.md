---
title: "Claude & GitHub Agents: Best Practices Guide (v2) — Part 3"
date: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
topic_id: claude-agents-best-practices-part3
doc_type: guide
supersedes: []
tags: ["coding-tools", "agents", "security", "anti-patterns", "best-practices"]
---

**This is Part 3 of 3. [Part 1 ←](pathname:///archon/agentic-systems/coding-tools/36-claude-agents-best-practices) | [Part 2 ←](pathname:///archon/agentic-systems/coding-tools/parts/36-claude-agents-best-practices-part2)**

## **09**

## **Security — CVEs & Hardening**

Security in Claude Code operates at 7 layers. The April 2026 changelog patched several critical permission bypass vulnerabilities in Bash handling. This chapter covers all known CVEs, the MCP rug pull attack, and hardening patterns.

## **CVE Registry — Full List (Apr 2026)**

|**CVE**|**CVSS**|**Description**|**Fixed In**|
|---|---|---|---|
|CVE-2025-59536|8.7|Hook/MCP init runs before trust dialog — code executes before consent|v1.0.111|
|CVE-2025-55284|7.1|API key exfiltration via DNS (prompt injection abuses dig/nslookup)|v1.0.4|
|CVE-2025-52882|8.8|VS Code WebSocket auth bypass — malicious sites can connect (RCE)|VS Code ext v1.0.24+|
|CVE-2026-21852|5.3|API key exfiltration via malicious ANTHROPIC_BASE_URL|v1.1.x|
|CVE-2026-33068|7.7|Workspace trust dialog bypass via repo-controlled settings files|v2.1.53|
|Bash CVE (Apr 2026)|TBD|Backslash-escaped flag auto-allowed as read-only→arbitrary code exec|v2.1.88+|
|Compound Bash|TBD|Compound commands (&&,\|\|) bypassed safety prompts|v2.1.88+|
|POSIX which CVE|TBD|Command injection in POSIX which fallback for LSP binary detection|Patched|

##### **Critical Rule**

NEVER use --dangerously-skip-permissions in directories you don't fully control. CVE-2025-59536 shows that hooks/MCP can execute before the trust dialog — meaning code runs before you can consent. Fixed in v1.0.111 but the flag itself remains dangerous with untrusted repository content.

## **MCP Rug Pull Attack Pattern**

A malicious MCP server can initially present safe tools, earn trust/caching, then change tool behavior mid-session. Defense:

- Pin MCP server URLs to specific commit hashes, not branch names
- Audit all MCP servers before connecting — review source code
- Use PreToolUse hooks to log all tool invocations for audit trail
- Restrict MCP servers to minimum required tools via allowedTools
- Never connect to MCP servers from untrusted repositories

## **7-Layer Defense Architecture**

|**Layer**|**Mechanism**|**Failure Mode**|
|---|---|---|
|1 - Trust Model|Graduated permissions (sandbox→plan→acceptEdits→bypass)|All share same performance constraints|
|2 - Permission Gate|PreToolUse hook blocks dangerous actions|50+ subcommands bypass security analysis|
|3 - Allowlist|Explicit tool permission lists|Over-broad allowlists defeat purpose|
|4 - Sandboxing|Isolated execution environments|dangerouslySkipPermissions disables all|
|5 - Hooks|Deterministic enforcement scripts|Async hooks don't block (by design)|
|6 - Audit Logging|PostToolUse + PostToolUseFailure logging|Logs don't prevent, only detect|
|7 - Human Review|Human-in-the-loop for destructive ops|27% of tasks attempted only with AI|

## **10**

## **Anti-Patterns Catalog**

These are documented failure modes drawn from Anthropic's official best-practices docs, the Dive-into-Claude-Code architectural analysis, and community research across thousands of production deployments.

## **Skills Anti-Patterns**

#### **Anti-Pattern #1: Kitchen Sink CLAUDE.md**

Problem: CLAUDE.md over 80 lines, includes things Claude already knows, tutorials instead of corrections. Important rules get lost in the noise — Claude ignores half.

**Fix: Ruthlessly prune to &lt;80 lines. If Claude does it correctly without the instruction, delete it or convert to a hook.**

#### **Anti-Pattern #2: Description-less Skills**

Problem: Skills with vague or absent descriptions: 'Handles documents', 'For financial stuff'. Claude never auto-loads them, or loads them on everything.

**Fix: Write descriptions as routing rules with PROACTIVELY signals, negative examples, and explicit trigger phrases.**

#### **Anti-Pattern #3: Overlapping Skills**

Problem: Two skills that could handle the same input (e.g., 'data-analysis' and 'csv-processor'). Claude picks arbitrarily — non-deterministic behavior.

**Fix: Ensure skills are self-contained and non-overlapping. Every skill must justify its existence independently.**

#### **Anti-Pattern #4: Inline Everything**

Problem: All skill knowledge embedded in CLAUDE.md or as inline system prompt context instead of loading on demand. Wastes tokens every turn even when irrelevant.

**Fix: Move domain knowledge to context: fork skills. Load on demand, not on every turn.**

## **Subagent & Routing Anti-Patterns**

#### **Anti-Pattern #5: Agent Teams for Simple Parallelism**

Problem: Using Agent Teams (3-4× token cost, 7× in plan mode) when subagents would suffice. Teams add coordination overhead and amplify errors.

**Fix: Use Agent Teams only when active teammate-to-teammate coordination is required. Use subagents for independent parallel tasks.**

#### **Anti-Pattern #6: Raw File Content Returns**

Problem: Subagents returning raw file contents to main context instead of summaries. Completely defeats the purpose of context isolation.

**Fix: Subagents must return structured summaries. Use 'Return ONLY a structured summary — do not include raw file contents' in system prompt.**

#### **Anti-Pattern #7: All-Opus Routing**

Problem: Using Claude Opus for every task regardless of complexity. Leaf node agents, explorers, and classifiers running on Opus when Haiku suffices.

**Fix: Route by task type: Opus for architecture/security review, Sonnet for implementation, Haiku for search/classify/format.**

#### **Anti-Pattern #8: Subagent Nesting**

Problem: Attempting to spawn subagents from within subagents (infinite nesting). Claude Code prevents this — subagents cannot spawn other subagents.

**Fix: Use the orchestrator-workers pattern with the main agent as orchestrator. Plan subagent handles research in plan mode.**

## **Hooks Anti-Patterns**

#### **Anti-Pattern #9: Over-Formatting Hook**

Problem: Auto-formatting hooks (prettier/black) running on every Edit. Reported to consume 160K+ tokens in 3 rounds due to context inflation from repeated outputs.

**Fix: Run formatters manually between sessions or in PostToolUse with strict output size limits. Consider async hooks to avoid blocking.**

#### **Anti-Pattern #10: Complex Slash Commands**

Problem: Long list of complex custom slash commands as a substitute for skills. Slash commands are manually invoked; skills auto-load when relevant.

**Fix: Convert complex slash commands to skills with invocation: auto. Reserve slash commands for explicit user-triggered actions.**

#### **Anti-Pattern #11: Broad allowedTools in Skills**

Problem: Skills with allowed-tools: '*' or overly broad permissions. Skills execute code — a malicious skill with broad permissions is a security risk.

**Fix: Apply least-privilege to every skill. List only the specific tools needed: allowed-tools: Bash(python3 AnalysisScript.py), Read**

## **Context & Cost Anti-Patterns**

#### **Anti-Pattern #12: The Kitchen Sink Session**

Problem: One session used for multiple unrelated tasks. Context fills with irrelevant history. Performance degrades silently.

**Fix: Use /clear between unrelated tasks. Use /rename before clearing so you can /resume later.**

#### **Anti-Pattern #13: Correction Loop**

Problem: Claude does something wrong → you correct → still wrong → correct again. Context is now polluted with failed approaches, making the problem worse.

**Fix: After two failed corrections: /clear and write a better initial prompt incorporating what you learned.**

#### **Anti-Pattern #14: Trust-Then-Verify Gap**

Problem: Accepting plausible-looking implementation without verification. AI-generated code has 1.5-2× higher security vulnerability rates than human-written code.

**Fix: Always provide verification criteria upfront: tests, linter, screenshot comparison. Claude performs dramatically better when it can verify its own work.**

#### **Anti-Pattern #15: Raw Log Reads**

Problem: Asking Claude to read a 10,000-line log file to find errors. Consumes tens of thousands of tokens when a grep would suffice.

**Fix: Use a PreToolUse hook to preprocess logs before Claude sees them. Filter → 50 relevant lines → massive token reduction.**

## **MCP & Plugin Anti-Patterns**

#### **Anti-Pattern #16: 35-Tool MCP Server**

Problem: Connecting a single MCP server with 35+ tools (e.g., GitHub MCP server unfiltered). ~26K tokens of tool definitions loaded every turn.

**Fix: Use ToolSearch for discovery. Restrict MCP servers to the tools actually needed via the tools parameter.**

#### **Anti-Pattern #17: Untrusted MCP Server**

Problem: Installing MCP servers from unknown sources without code review. MCP rug pull: server can change tool behavior mid-session after earning trust.

**Fix: Only use MCP servers from trusted sources. Pin to commit hashes. Use PreToolUse hooks to audit all invocations.**

## **GitHub Actions Anti-Patterns**

#### **Anti-Pattern #18: Unpinned Model Version**

Problem: Using model: claude-latest or not pinning the model version in CI/CD. Model updates can change behavior unexpectedly in automated workflows.

**Fix: Always pin: model: claude-sonnet-4-6. Update deliberately, not automatically.**

#### **Anti-Pattern #19: No Concurrency Group**

Problem: Multiple Claude reviews running simultaneously on the same PR when new commits arrive. Wastes tokens and produces conflicting review comments.

**Fix:** Add `concurrency: { group: claude-review-${{ github.event.pull_request.number }}, cancel-in-progress: true }`

#### **Anti-Pattern #20: Artifact Paradox**

Problem: Polished AI-generated outputs (code, files) reduce critical human evaluation. Research shows: -5.2pp missing context, -3.7pp fact-checking, -3.1pp reasoning challenge.

**Fix: Maintain human review as a required step. Set CLAUDE.md rule: 'I am ultimately responsible for all code in PRs with my name on it.'**

## **11**

## **Latest Additions (Apr 2026)**

The awesome-claude-code repo (now 35.9K+ stars, 903 commits) hit issue #1000 on March 12 and posted its April 2026 update on April 6. Submissions continue at ~10+ per week.

## **New Skills Repos**

|**Skill ID**|**Purpose**|**API Beta**|**Installs**|
|---|---|---|---|
|Claude Scientific Skills|K-Dense|Ready-to-use skills for research, science, engineering, analysis, finance, writing. Considered one of best skills repos on GitHub.|–|
|Claude Mountaineering Skills|Dmytro Gaivoronsky|Automates mountain route research. Aggregates 10+ sources (Mountaineers.org, PeakBagger, SummitPost) for route beta with weather & avalanche data.|–|
|Book Factory|Robert Guss|Pipeline of Skills replicating traditional publishing infrastructure for nonfiction book creation.|–|
|Codebase to Course|Zara Zhang|Turns any codebase into an interactive single-page HTML course for non-technical users.|–|
|cc-devops-skills|akin-ozer|Detailed DevOps skills: IaC code generation for most major platforms with validations, generators, and CLI tools.|–|
|j4rk0r/claude-skills|j4rk0r|3 expert skills: skill-guard (9-layer security auditor), skill-advisor (smart routing), skill-learner (persistent error correction). All scored A+ 120/120.|–|

## **New Agents & Orchestration (Apr 2026)**

|**Repo**|**Description**|
|---|---|
|AgentSys (avifenesh)|Full workflow automation: task-to-production, PR management, code cleanup, drift detection, multi-agent code review. Includes agnix for linting agent configs.|
|Harness (revfactory)|Meta-skill that designs domain-specific agent teams, defines specialists, and generates their skills. Resources in Korean, English output supported.|
|awesome-claude-code-toolkit|135 agents across 10 categories, 35 curated skills, 400K+ via SkillKit, 42 commands, 176+ plugins, 20 hooks. Was #1 trending GitHub Feb 2026.|
|Claude Code Agents (UndeadList)|E2E dev workflow with subagent prompts for solo devs. Parallel auditors, fix cycles with micro-checkpoint protocols, browser QA.|

## **New Dev Tools (Apr 2026)**

|**Tool**|**Type**|**Key Feature**|
|---|---|---|
|claude-devtools (matt1398)|Desktop app|Session log analysis, turn-based context data, compaction visualization, subagent execution trees, custom notification triggers.|
|notch-so-good|macOS notch widget|Pixel-art crab lives in Mac notch watching Claude Code. Live timers, color-coded notifications, 13 idle animations, mouse-reactive eyes.|
|codebase-graph|MCP + npm|42-language tree-sitter AST parsing, FalkorDB knowledge graphs, 0.944 MRR search quality. npm: @anthropic/codegraph|
|Claudex (Kunwar Shah)|Web browser|Browse Claude Code conversation history across projects. Full-text search, high-level analytics, export options. Completely local, no telemetry.|
|CodeBurn|CLI dashboard|CLI usage analytics: costs, token consumption, efficiency scoring, weekly reports. Supports Codex and Cursor too.|

## **April 2026 Changelog Highlights**

- **--from-pr** now accepts GitLab MR, Bitbucket PR, and GitHub Enterprise PR URLs
- **PostToolUseFailure hook** + duration_ms in PostToolUse inputs
- **MCP parallel startup** — servers connect concurrently instead of serially
- **CLAUDE_CODE_FORK_SUBAGENT=1** — enables forked subagents on external builds
- **/agents redesign** — tabbed layout with Running and Library tabs
- **/resume** now offers to summarize stale large sessions before re-reading
- **Bash permission hardening** — compound commands, env-var prefixes, redirects patched
- **Opus 4.7 context fix** — was incorrectly computing against 200K instead of 1M window
- **OTEL privacy flags** — user prompts and tool content now opt-in for tracing
- **Plugin auto-dependency resolution** — claude plugin marketplace add now resolves deps

## **Academic Resources**

- **Dive-into-Claude-Code** (arXiv 2604.14228) — Source-level analysis of v2.1.88. Key finding: 98.4% deterministic infra, 1.6% AI. Five values → 13 principles → implementation.
- **FlorianBruniaux/claude-code-ultimate-guide** — 41 interactive diagrams, 9-category quiz, configuration decision guide across all 7 config layers.
- **VILA-Lab/Dive-into-Claude-Code** — 27 hook events (not 12), 10-component plugin manifest, 15+ SKILL.md frontmatter fields documented from source.

## **12 Quick Reference & Checklists**

## **New Project Setup Checklist**

1. Create CLAUDE.md (<80 lines, corrections only, architecture overview)
2. Add .claudeignore (node_modules, dist, logs, *.csv,*.lock, .git)
3. Set CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=60 in environment
4. Install relevant pre-built skills: pptx, xlsx, docx, pdf, frontend-design
5. Create .claude/agents/ with domain-specific subagent definitions
6. Add PreToolUse security hook (credential protection + Bash hardening)
7. Add PostToolUse formatting hook (pre-commit or prettier — async: true)
8. Add Stop hook for async notifications (async: true)
9. Set up cost monitoring: ccflare or ccxray dashboard
10. Configure workspace spend limits in Claude Console
11. Add token-efficient-tools beta header to all API calls
12. Enable prompt caching on system prompts and large repeated context
13. Pin model versions everywhere — never use 'latest' in production
14. Add SKIP_REVIEW label support to GitHub Actions workflows
15. Add concurrency groups to all Claude CI/CD jobs

## **Mechanism Decision Guide**

|**'When should I use...'**|**Answer**|
|---|---|
|CLAUDE.md|Project conventions Claude gets wrong without it. Under 80 lines only.|
|Skills|Domain knowledge, org workflows, tasks needing supporting files/scripts.|
|Hooks|Anything that MUST always happen. Deterministic enforcement only.|
|Subagents|Side tasks that would flood main context with search results or file contents.|
|Agent Teams|Active coordination between specialists required — NOT just parallelism.|
|MCP|External services, APIs, databases. Keep total tools <20 per server.|
|Slash commands|Explicit user-triggered workflows. Not for things Claude should auto-detect.|

## **Key Environment Variables**

|**Variable**|**Purpose**|**Recommended Value**|
|---|---|---|
|CLAUDE_AUTOCOMPACT_PCT_OVERRIDE|Trigger compaction before quality degrades|60|
|CLAUDE_CODE_FORK_SUBAGENT|Enable forked subagents on external builds|1|
|CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS|Enable Agent Teams (experimental)|1|
|CLAUDE_CODE_HIDE_CWD|Hide working dir in startup logo|1 (for security)|
|OTEL_LOG_USER_PROMPTS|Include user prompts in telemetry|false (default)|
|ANTHROPIC_BUDGET_TOKEN|Budget enforcement token|your-budget-token|

## **Essential Reference Repos**

|**Repo**|**Stars**|**What to Get From It**|
|---|---|---|
|hesreallyhim/awesome-claude-code|35.9KI|Curated skills, hooks, agents — start here|
|rohitg00/awesome-claude-code-toolkit|Rising|135 agents, 400K+ skills via SkillKit|
|VILA-Lab/Dive-into-Claude-Code|Academic|Source-level architecture analysis|
|FlorianBruniaux/claude-code-ultimate-guide|Community|41 diagrams, decision trees, quizzes|
|K-Dense-AI/claude-scientific-skills|New|Research, science, engineering, finance skills|
|anthropics/claude-code (Releases)|Official|Changelog, CVE fixes, new features|

##### **Final Summary**

The biggest wins are structural, not model selection. Ranking by impact: (1) Context architecture — .claudeignore, skills, compaction tuning. (2) Prompt caching — system prompt + cache-aware ITPM. (3) Hook enforcement — convert best practices to deterministic rules. (4) Model routing — Haiku for leaf nodes, Opus only for critical review. (5) Model selection — last, not first. Developers consistently achieve 60-80% cost reduction with structural changes alone, often in one day of setup.

---

**This is Part 3 of 3. [Part 1 ←](pathname:///archon/agentic-systems/coding-tools/36-claude-agents-best-practices) | [Part 2 ←](pathname:///archon/agentic-systems/coding-tools/parts/36-claude-agents-best-practices-part2)**
