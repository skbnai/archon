---
title: "Repository Context Engineering"
doc_type: guide
domain: agentic-systems
status: current
topic_id: repository-context-engineering
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/agentic-systems/skill/coding/06-repository-context-engineering.md
tags:
  - agentic-systems
  - skill
  - coding-tools
  - research
---

# Repository Context Engineering

## Why Repository Context Matters Beyond AGENTS.md and Skills

AGENTS.md and Skills are *authored* context — someone deliberately wrote them for the agent. **Repository context** is the much larger body of material that exists for humans but that a well-built agent should also mine: README, architecture docs, ADRs, CONTRIBUTING, SECURITY, issue/PR history, wiki, and code ownership records. The difference matters because authored context requires maintenance discipline that inevitably lags reality, while repository context (especially git history and issue/PR discussion) captures *decisions and their reasoning* that rarely make it into a rules file at all.

## Source-by-Source Retrieval Strategy

| Source | What it uniquely provides | Retrieval approach |
| --- | --- | --- |
| **README** | High-level project purpose, setup steps | Usually loaded eagerly/early — cheap, high value, low volatility |
| **Architecture docs / design docs** | System boundaries, major components, data flow | Retrieved on demand when a task touches cross-cutting concerns |
| **ADRs (Architecture Decision Records)** | The *why* behind a past technical choice — critical for avoiding an agent "helpfully" reverting a deliberate decision | Semantic search over the ADR directory, triggered when a task's scope overlaps a documented decision |
| **CONTRIBUTING.md** | PR process, commit conventions, required checks | Loaded when the task involves opening a PR or making a commit |
| **STYLEGUIDE** | Formatting/naming conventions beyond what a linter enforces | Often folded directly into AGENTS.md rather than kept separate |
| **SECURITY.md** | Disclosure process, known sensitive areas | Loaded when a task touches auth, secrets, or user data handling |
| **Issue tracker / PR history** | Precedent for how similar problems were previously solved; active discussion context | MCP-mediated (GitHub/Jira/Linear MCP servers) — retrieved per-task |
| **Wiki** | Institutional knowledge not co-located with code | Same pattern as issue tracker — MCP or search-API mediated |
| **CODEOWNERS** | Who to attribute a PR to / whose conventions apply in a given path | Used to route review requests and to weight whose past patterns are most authoritative |
| **Monorepo / workspace settings** | Which package a given file belongs to; build/test commands per package | Read from the monorepo's own manifest (package.json workspaces, Bazel BUILD files, Nx project.json) |
| **Semantic index / embeddings** | Concept-level retrieval ("where do we handle rate limiting") beyond exact keyword match | Pre-built index queried at context-collection time |
| **AST / tree-sitter** | Structural navigation (find all callers, class hierarchy) | Used for precise, exact-match structural queries |

## Retrieval Strategy Selection

**Flowchart for selecting retrieval strategy:**

1. Is the query exact/structural ("find all callers of X")?
   - YES → AST/tree-sitter or LSP-backed search
   - NO → proceed to step 2

2. Is the query conceptual ("where do we validate input")?
   - YES → Semantic/embedding search over codebase index
   - NO → proceed to step 3

3. Is the query about a past decision or discussion, not current code?
   - YES → ADR search / issue-tracker MCP query
   - NO → proceed to step 4

4. Is it a small, stable, high-value fact true of the whole repo?
   - YES → Belongs in AGENTS.md (pre-loaded)

## Retrieval Failure Modes to Guard Against

- **Stale index**: a semantic index built once at onboarding and never refreshed will confidently point the agent at deleted or heavily refactored code. Index freshness should be tied to CI (rebuild on merge to main).
- **Over-retrieval**: dumping too many "relevant" files into context degrades reasoning quality and burns tokens — retrieval should be precision-oriented rather than recall-maximizing.
- **Silently ignoring ADRs**: without an explicit retrieval trigger, an agent can "fix" code in a way that directly contradicts a documented, deliberate architectural decision — treat ADR search as a default step whenever a task touches a documented decision area.

## Repository Context Engineering Framework (Deliverable 6)

### Tier 1 — Always-loaded (belongs in AGENTS.md/CLAUDE.md, not retrieved)

- Stack and tooling (languages, frameworks, package manager, build system).
- Core conventions (naming, formatting — beyond what a linter auto-enforces).
- Hard boundaries ("never touch `legacy/`," "the billing service requires a second approver").
- Verification steps ("run `pnpm test` before considering a task complete").

### Tier 2 — Retrieved on demand, triggered by task scope

- README (cheap enough to often sit in Tier 1 for smaller repos).
- Architecture docs / ADRs, retrieved when the task's file scope overlaps a documented area.
- CONTRIBUTING/SECURITY, retrieved when the task involves a PR or touches sensitive surface area.
- CODEOWNERS, retrieved when routing review or resolving whose convention applies.

### Tier 3 — Retrieved via structural/semantic search, not stored as documents

- Codebase content itself, via AST/tree-sitter for exact queries and embeddings for conceptual queries.
- Issue/PR/wiki content, via MCP-mediated API queries scoped tightly to the current task.

### Governance Overlay

- Tier 1 content changes should go through the same PR review as code.
- Tier 2 content (especially ADRs) should be linked from Tier 1 where highly relevant, so the always-loaded context can point the agent to deeper material rather than trying to inline it.
- Tier 3 retrieval infrastructure (the semantic index) should have an owner and a freshness SLA tied to CI, exactly like any other piece of build infrastructure.
