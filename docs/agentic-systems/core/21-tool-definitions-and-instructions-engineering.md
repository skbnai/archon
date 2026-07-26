---
title: "Tool Definitions & Instructions Engineering"
doc_type: guide
domain: agentic-systems
status: current
topic_id: tool-definitions-and-instructions-engineering
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/agentic-systems/skill/coding/05-tool-definitions-and-instructions-engineering.md
tags:
  - agentic-systems
  - skill
  - coding-tools
  - research
---

# Tool Definitions & Instructions Engineering

## Tool Definitions for Coding Agents

### The Coding-Specific Tool Taxonomy

| Category | Examples | Notes |
| --- | --- | --- |
| Filesystem | read_file, write_file, list_directory, glob | Near-universal, native to every harness |
| Search | grep/ripgrep-backed search, semantic/embedding search | Ripgrep-style exact search is fast/cheap; semantic search is used for concept-level queries ("where do we handle auth") |
| AST/structural | tree-sitter-backed symbol search, "find all references" | Bridges to Language Server ground truth (file `04`) |
| Git | diff, commit, branch, blame, log | Native in nearly all harnesses; a common source of destructive-action risk (force-push, hard reset) requiring approval gates |
| Terminal | run arbitrary shell command | Highest-risk built-in tool; universally sandboxed by mid-2026 (file `10`) |
| Docker/Kubernetes/Terraform | container build/run, cluster ops, IaC apply | Increasingly MCP-mediated rather than raw shell, for auditability |
| Browser | navigate, click, screenshot, extract | Used for visual/E2E testing and for agents that need live web context |
| Testing | run test suite, run a single test, report coverage | Central to the "validation" lifecycle stage (file `03`) |
| Debugger | set breakpoint, step, inspect variable | Less commonly LLM-tool-exposed than the others; still maturing |
| Linter/Formatter | run lint, apply autofix, run formatter | Often auto-invoked post-edit rather than model-selected |
| Package manager | install, add dependency, audit | High blast-radius (supply-chain risk) — should require explicit approval by default |

### Tool Description Best Practice (Specific to Coding Tools)

The same template discipline from the enterprise package (companion file `05`) applies, with coding-specific emphasis:

- **Name**: verb-first, unambiguous (`run_tests`, not `test`). Namespace where a harness exposes many similar tools (`git.diff` vs `git.log`).
- **When to use / when NOT to use**: critical for the terminal tool specifically — a well-written terminal tool description should explicitly steer the agent toward the *dedicated* git/test/lint tools instead of shelling out to `git diff` or `npm test` via raw terminal, because raw terminal calls bypass structured output parsing and are harder to sandbox precisely.
- **Safety constraints**: this is where destructive-operation guardrails belong — "requires explicit confirmation before force-push," "never run against the `main` branch without approval," "package installs from unpinned registries require confirmation."
- **Expected latency**: matters more here than in typical enterprise tools — a full test-suite run can take minutes; the agent (and the developer watching) benefits from the tool description setting that expectation so it doesn't appear "stuck."
- **Failure modes**: compilation errors, test failures, and lint violations are *expected*, common outcomes, not exceptional failures — the tool's return contract should clearly separate "the tool itself failed to execute" from "the tool executed and reported a failing result," since an agent that conflates these two will either give up prematurely or falsely claim success.

### Decision Boundaries — When Should the LLM Invoke Each Tool?

The single highest-value piece of guidance surfaced across multiple vendor docs and community skill authoring guides: **prefer structured tools over raw terminal invocation wherever a structured tool exists**, specifically because (a) structured tools have parseable, typed output the agent reasons over more reliably than raw stdout, and (b) structured tools are the natural place to enforce safety policy (a `git_commit` tool can refuse to commit files matching a secrets pattern; a raw `terminal` tool cannot easily enforce the same rule against an arbitrary `git commit -a` invocation).

## Instructions Engineering

### What Belongs in Instructions, and Where

| Content | AGENTS.md/Rules | Skill |
| --- | --- | --- |
| Language/framework conventions (naming, formatting) | ✅ (always true) | Only if framework-specific and rarely invoked |
| Architecture overview | ✅ (or reference to ADRs, file `06`) | |
| Testing rules (coverage bar, required patterns) | ✅ if always-true | ✅ if a specific, deep testing methodology |
| Security requirements (never commit secrets, required auth patterns) | ✅ | ✅ if the security procedure itself is deep (e.g., a full threat-modeling skill) |
| Performance budgets | ✅ | |
| Accessibility requirements | ✅ | |
| Code review guidelines | ✅ (baseline) | ✅ (a full review-methodology skill) |
| Deployment steps | ✅ if simple; otherwise reference actual CI config | ✅ if the procedure is genuinely multi-step and judgment-heavy |
| Repository-specific gotchas ("this migration is manual," "this test is flaky, ignore it") | ✅ | |

### Repository/Language/Framework/Organization Scoping

- **Repository-specific**: goes in the repo-root AGENTS.md/CLAUDE.md; subdirectory AGENTS.md files scope to that subdirectory automatically in every implementation studied (Windsurf's Cascade, Devin, Roo Code all implement nearest-file-wins directory-tree precedence).
- **Language-specific**: either a subdirectory AGENTS.md (`services/api-python/AGENTS.md`) or, for deeper procedural content, a language-scoped Skill with `repo_scope`/`globs`-equivalent metadata (file `02`).
- **Framework-specific**: same pattern; a React-conventions rule is a good `.cursor/rules/react.mdc`-style glob-scoped rule (`globs: "**/*.tsx"`) rather than a full Skill, since it's a *standing* convention, not an occasional procedure.
- **Organization-specific**: today mostly handled via a shared, symlinked or synced base file across repos (a documented, common pattern: one canonical source file copied via a pre-commit hook into `.cursorrules`, `CLAUDE.md`, `.windsurfrules`, `AGENTS.md`, etc.) — genuine org-level skill/rule distribution ("coming soon" on more than one platform as of mid-2026) is the clearest maturity gap in this whole space (file `11`).

### Anti-patterns

| Anti-pattern | Why it hurts | Fix |
| --- | --- | --- |
| **Prompt duplication** | Five near-identical files (`.cursorrules`, `CLAUDE.md`, `.windsurfrules`, `.clinerules/base.md`, `AGENTS.md`) drift out of sync as only one gets updated | Single canonical source + sync script/symlinks (a documented, common community pattern), or migrate fully to AGENTS.md where the target tool supports it |
| **Conflicting instructions** | A skill and AGENTS.md (or two skills) give contradictory guidance | Skills should defer to AGENTS.md for anything always-true; skills should only add task-specific detail, never override standing rules |
| **Huge prompts** | A single, giant AGENTS.md with everything crammed in degrades reliability and burns tokens every turn | Keep AGENTS.md under roughly 500 lines (the commonly cited community guideline); push deep/rare content to Skills |
| **Hidden logic** | Business-critical rules (e.g., "never touch the billing service without a specific approval") buried in prose deep inside a rarely-loaded skill | Put hard constraints in the always-loaded file, not a conditionally-loaded skill, if violating them would be serious |
| **Instruction drift** | AGENTS.md/skill content and the actual codebase diverge over time (skill says "use Enzyme," codebase migrated to Testing Library six months ago) | Treat instruction files as code: review on every relevant PR, not just at authoring time |

## Best-Practice Templates (Deliverable 5)

### Tool Definition Template

```yaml
tool:
  name: git.commit
  summary: "Stages and commits the given files with the given message."
  when_to_use: ["A discrete, reviewable unit of work is complete and validated."]
  when_not_to_use: ["Mid-task, uncommitted exploratory changes — don't commit broken states."]
  safety_constraints:
    - "Refuses if staged content matches a known secrets pattern (API keys, private keys)."
    - "Requires explicit confirmation if the target branch is 'main' or 'master'."
  failure_modes:
    - code: SECRET_DETECTED
      agent_guidance: "Do not retry with --no-verify. Remove the secret and re-stage."
    - code: NOTHING_STAGED
      agent_guidance: "Stage the intended files first; this is not a fatal error."
```

### Skill Instructions Template

```markdown
---
name: webapp-testing
description: >-
  Generate and structure automated tests for this web application's
  components and API routes. Use when the user asks to add tests, improve
  coverage, or verify behavior with automated checks.
argument-hint: "File path or module name of the test target"
---

# Web App Testing

## When to use
- Adding new tests for existing, untested code.
- Extending an existing test file for a new case.

## When NOT to use
- The user is asking to *debug a failing test* (see debugging-ci-failures skill).
- The change is purely cosmetic/CSS with no behavioral surface.

## Procedure
1. Identify the target module and its existing test file, if any.
2. Follow the Arrange-Act-Assert pattern; one behavior per test.
3. Prioritize boundary values (empty input, max length, off-by-one) over only the happy path.
4. Name files `*.test.ts`, colocated with the source file.
5. Run the new tests; do not report completion until they pass.

## Output
A diff containing the new/updated test file(s), plus a one-line summary
of what behaviors are now covered.
```

## Related

- [Skills vs. MCP & the Full Responsibility Stack](20-skills-tools-mcp-relationship.md) — the previous section in this series.
- [Repository Context Engineering](22-repository-context-engineering.md) — the next section in this series.
