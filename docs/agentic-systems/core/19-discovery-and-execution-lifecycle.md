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

# Skill Discovery & Execution Lifecycle

## Discovery Hierarchy

The skill discovery mechanism operates in layers, checking progressively deeper sources:

```
Built-in Skills
   ↓
Organization Skills
   ↓
Repository / Project Skills
   ↓
User / Global Skills
   ↓
Marketplace / Extension-Provided Skills
   ↓
MCP-Discoverable Skills
```

Built-in skills are shipped with the agent itself (e.g., OpenAI's curated catalog: playwright, gh-fix-ci, cloudflare-deploy).

Organization skills form an org-wide catalog — "coming soon" on several platforms as of mid-2026; today mostly simulated via a shared git repo teams clone into their skills directory.

Repository / Project skills live in `.github/skills/`, `.agents/skills/`, `.codex/skills/`, or similar — committed, code-reviewed, and shared via git with the whole team.

User / Global skills are stored in `~/.copilot/skills/`, `~/.agents/skills/`, `~/.codex/skills/`, or equivalents — personal, not committed, cross-project.

Marketplace / Extension-provided skills come from community/vendor catalogs: Agensi, awesome-copilot, ClawHub-equivalents, Codex plugin marketplace — installed explicitly via a CLI installer.

MCP-discoverable skills emerge from Google ADK-style dynamic registries — less common in pure coding-assistant tooling today than in enterprise agent platforms, but the same pattern is emerging via `gh skill` search-and-install.

## Lookup Mechanisms

| Mechanism | How it works | Where observed |
| --- | --- | --- |
| **Keyword/description matching** | Agent compares the user's request text against every loaded skill's `description` | Universal baseline mechanism across all SKILL.md-compatible tools |
| **Slash/explicit invocation** | User types `/skill-name` or `$skill-name`, bypassing matching entirely | Copilot (`/name`), Codex (`$name`), Claude Code (`/name`) |
| **Semantic/embedding search** | Registry-level search over skill descriptions for near-miss phrasing | `gh skill` search across GitHub-hosted skill repos; marketplace search (Agensi and similar) |
| **Provenance-based update checks** | Installed skill's frontmatter carries source repo/ref/tree-SHA; CLI checks upstream for changes | `gh skill update`, which reads its own previously-written provenance metadata |
| **Static registration** | Skills placed in a fixed directory, loaded at session start | Default behavior for local/project/personal skills in nearly every tool |
| **Dynamic/on-demand fetch** | Agent fetches a skill from a remote registry mid-session | Less common in pure coding tools than in enterprise platforms (Google ADK); Codex's `$skill-installer` is the closest coding-tool analogue |

## Execution Lifecycle

### Stage-by-stage Flow

```
Developer Request
   ↓
[1] Intent Detection
   Agent classifies what kind of task this is
   (bug fix, feature, review, refactor, question).
   ↓
[2] Planning
   Agent decomposes into steps; decides whether
   AGENTS.md context alone suffices or a Skill is needed.
   ↓
[3] Skill Selection
   Match request against loaded skill descriptions;
   load full SKILL.md (+ referenced files) on match.
   ↓
[4] Tool Selection
   Within the skill's guidance (or, absent a matching skill,
   the agent's own judgment), pick specific tools.
   ↓
[5] Repository Scan
   Retrieve relevant files via semantic index, AST/tree-sitter
   navigation, grep/ripgrep, or embeddings.
   ↓
[6] Context Collection
   Assemble: AGENTS.md + skill instructions + retrieved files
   + repo docs (README, ADRs) + prior conversation state.
   ↓
[7] Execution
   Tool calls actually run: edits written, commands executed,
   typically inside a sandbox/dev container.
   ↓
[8] Validation
   Compile/build check, linter, test suite run.
   ↓
[9] Response
   Diff/PR/summary presented to the developer.
   ↓
[10] Telemetry
   Spans emitted for every step above to the observability plane.
```

### Failure and Multi-step Paths

**Validation failure loop:** When tests fail at stage [8], the agent reads the failure output and re-enters stage [7] Execution with a fix. This retry is bounded — beyond the bound, the agent reports the failure back to the developer rather than looping indefinitely.

**Skill-not-found / ambiguous match:** When stage [3] finds no skill's description clearly matches, the system falls back to AGENTS.md context + general model capability alone, or asks a clarifying question if the ambiguity is consequential.

**Cross-tool delegation (MCP-mediated):** When stage [4] Tool Selection determines a needed capability lives outside the built-in tool set (e.g., "check the related Jira ticket"), the MCP client connects to the relevant server, executes the tool call, and folds the result into stage [6] Context Collection.

**Human approval gate:** Triggered for destructive or high-risk actions (force-push, `rm -rf`, deploying to production). The lifecycle pauses between stages [6] and [7], requiring explicit approval before proceeding.

## Complete Execution Flow (Deliverable 2)

```
Developer Request
   → Intent Detection
   → Planning
   → Skill Selection
   → Tool Selection
   → Repository Scan
   → Context Collection
   → [Human Approval Gate if high-risk]
   → Execution (in sandbox/dev container)
   → Validation (build/lint/test)
   → [loop back to Execution on failure, bounded]
   → Response
   → Telemetry
```
