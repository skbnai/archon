---
title: "Skill Discovery & Execution Lifecycle"
doc_type: concept
domain: agentic-systems
status: current
topic_id: discovery-and-execution-lifecycle
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/agentic-systems/skill/coding/03-discovery-and-execution-lifecycle.md
tags:
  - agentic-systems
  - skill
  - coding-tools
  - research
---

# Part 3 — Skill Discovery & Part 4 — Execution Lifecycle (+ Deliverable 2)

## PART A: Discovery

### 3.1 The discovery hierarchy

```mermaid
flowchart TD
    A["Built-in Skills<br/>shipped with the agent itself, e.g. OpenAI's curated catalog:<br/>playwright, gh-fix-ci, cloudflare-deploy"] --> B
    B["Organization Skills<br/>org-wide catalog — 'coming soon' on several platforms as of mid-2026;<br/>today mostly simulated via a shared git repo teams clone into their skills directory"] --> C
    C["Repository / Project Skills<br/>.github/skills/, .agents/skills/, .codex/skills/ —<br/>committed, code-reviewed, shared via git with the whole team"] --> D
    D["User / Global Skills<br/>~/.copilot/skills/, ~/.agents/skills/, ~/.codex/skills/ —<br/>personal, not committed, cross-project"] --> E
    E["Marketplace / Extension-Provided Skills<br/>community/vendor catalogs: Agensi, awesome-copilot, ClawHub-equivalents,<br/>Codex plugin marketplace — installed explicitly via a CLI installer"] --> F
    F["MCP-Discoverable Skills<br/>Google ADK-style dynamic registries — less common in pure coding-assistant<br/>tooling today than in enterprise agent platforms, but the same pattern is<br/>emerging via `gh skill` search-and-install"]
```

*Discovery hierarchy for agent skills, from narrowest to broadest scope: built-in, then organization, repository, user, marketplace, and finally MCP-discoverable registries.*

### 3.2 Lookup mechanisms

| Mechanism | How it works | Where observed |
| --- | --- | --- |
| **Keyword/description matching** | Agent compares the user's request text against every loaded skill's `description` | Universal baseline mechanism across all SKILL.md-compatible tools |
| **Slash/explicit invocation** | User types `/skill-name` or `$skill-name`, bypassing matching entirely | Copilot (`/name`), Codex (`$name`), Claude Code (`/name`) |
| **Semantic/embedding search** | Registry-level search over skill descriptions for near-miss phrasing | `gh skill` search across GitHub-hosted skill repos; marketplace search (Agensi and similar) |
| **Provenance-based update checks** | Installed skill's frontmatter carries source repo/ref/tree-SHA; CLI checks upstream for changes | `gh skill update`, which reads its own previously-written provenance metadata |
| **Static registration** | Skills placed in a fixed directory, loaded at session start | Default behavior for local/project/personal skills in nearly every tool |
| **Dynamic/on-demand fetch** | Agent fetches a skill from a remote registry mid-session | Less common in pure coding tools than in enterprise platforms (Google ADK); Codex's `$skill-installer` is the closest coding-tool analogue, though it is typically a one-time install step, not a per-turn dynamic fetch |

### 3.3 Ranking and caching

- **Ranking** is largely implicit today (best-match-by-description), not yet a formalized quality-score-driven ranking system like the enterprise registries in the companion package — this is a maturity gap worth flagging for any org building internal tooling on top of these ecosystems.
- **Caching**: once loaded for a session, a skill's content typically stays resident for that session/conversation; most tools reload from disk on session restart rather than maintaining a long-lived server-side cache (consistent with the local-first, filesystem-based design of nearly every coding-assistant Skill implementation, in contrast to the server-hosted registries common in enterprise platforms).

---

## PART B: Execution Lifecycle (Deliverable 2)

### 4.1 Stage-by-stage flow

```mermaid
flowchart TD
    R[Developer Request] --> S1
    S1["[1] Intent Detection<br/>Agent classifies what kind of task this is<br/>(bug fix, feature, review, refactor, question)"] --> S2
    S2["[2] Planning<br/>Agent decomposes into steps; decides whether AGENTS.md<br/>context alone suffices or a Skill is needed"] --> S3
    S3["[3] Skill Selection<br/>Match request against loaded skill descriptions;<br/>load full SKILL.md (+ referenced files) on match"] --> S4
    S4["[4] Tool Selection<br/>Within the skill's guidance (or the agent's own judgment),<br/>pick specific tools: read_file, run_terminal, git_diff, etc."] --> S5
    S5["[5] Repository Scan<br/>Retrieve relevant files via semantic index, AST/tree-sitter<br/>navigation, grep/ripgrep, or embeddings — not the whole repo"] --> S6
    S6["[6] Context Collection<br/>Assemble AGENTS.md + skill instructions + retrieved files<br/>+ repo docs (README, ADRs) + prior conversation state"] --> S7
    S7["[7] Execution<br/>Tool calls actually run: edits written, commands executed,<br/>typically inside a sandbox/dev container"] --> S8
    S8["[8] Validation<br/>Compile/build check, linter, test suite run —<br/>'it compiles and the tests pass' as the completion bar"] --> S9
    S9["[9] Response<br/>Diff/PR/summary presented to the developer, following<br/>the skill's declared output format if one exists"] --> S10
    S10["[10] Telemetry<br/>Spans emitted for every step above to the observability plane"]
```

*The ten-stage execution lifecycle, from developer request through intent detection, planning, skill/tool selection, repository scan, context assembly, execution, validation, response, and telemetry.*

### 4.2 Sequence diagram — single-skill, single-tool happy path

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Harness as Agent Harness
    participant Store as Skill Store
    participant Repo as Repo Index
    participant Sandbox
    participant Telemetry

    Dev->>Harness: "add tests"
    Harness->>Store: match description
    Store-->>Harness: webapp-testing SKILL.md
    Harness-)Telemetry: emit span: skill_selected
    Harness->>Repo: retrieve relevant files (semantic/AST search)
    Repo-->>Harness: file set
    Harness-)Telemetry: emit span: repo_scan (files, method)
    Harness->>Sandbox: execute: write test file per skill's AAA pattern
    Harness-)Telemetry: emit span: tool_call(write_file)
    Harness->>Sandbox: execute: run test suite
    Sandbox-->>Harness: pass/fail
    Harness-)Telemetry: emit span: validation(test_result)
    Harness-->>Dev: diff + summary
    Harness-)Telemetry: emit span: response, session_summary
```

*Happy-path sequence for a single skill, single tool call: the harness matches a skill, scans the repo, executes and validates, then responds — emitting a telemetry span at every step.*

### 4.3 Failure and multi-step paths

**A. Validation failure loop**

```mermaid
flowchart TD
    A["[8] Validation → tests fail"] --> B["Agent reads failure output,<br/>re-enters [7] Execution with a fix"]
    B --> C["[8] Validation (attempt N+1)<br/>bounded retry count"]
    C -->|"beyond the bound"| D["Agent reports the failure back to the developer<br/>rather than looping indefinitely"]
```

*A directly observed anti-pattern is unbounded fix-retry loops burning tokens/time without escalating — the bounded retry count exists to prevent it.*

**B. Skill-not-found / ambiguous match**

```mermaid
flowchart TD
    A["[3] Skill Selection: no skill's description clearly matches"] --> B["Fall back to AGENTS.md context<br/>+ general model capability alone"]
    A --> C["OR ask a clarifying question if the ambiguity<br/>is consequential (destructive action, unclear scope)"]
```

**C. Cross-tool delegation (MCP-mediated)**

```mermaid
flowchart TD
    A["[4] Tool Selection determines the needed capability lives<br/>outside the built-in tool set (e.g., 'check the related Jira ticket')"] --> B["MCP client connects to the relevant server → tool call"]
    B --> C["Result folded into [6] Context Collection<br/>as if it were a local file"]
```

**D. Human approval gate**
Triggered for destructive or high-risk actions (force-push, `rm -rf`, deploying to production, auto-approving further tool calls) — the lifecycle pauses between [6] and [7]. This checkpoint is precisely what several documented CVEs (file `10`) attack: tricking the agent into silently modifying its own approval settings to skip this gate.

### 4.4 Deliverable 2 — the complete flow, one more time as a single artifact

```mermaid
flowchart LR
    A[Developer Request] --> B[Intent Detection] --> C[Planning] --> D[Skill Selection] --> E[Tool Selection]
    E --> F[Repository Scan] --> G[Context Collection] --> H{High-risk?}
    H -->|yes| I[Human Approval Gate]
    H -->|no| J
    I --> J["Execution (sandbox/dev container)"]
    J --> K["Validation (build/lint/test)"]
    K -->|fail, bounded retry| J
    K -->|pass| L[Response] --> M[Telemetry]
```

*The complete lifecycle end to end, showing the optional human approval gate before execution and the bounded retry loop on validation failure.*
