---
title: "Skill Anatomy & Metadata Schema"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: agent-skill-anatomy-metadata-schema
supersedes: ["docs/agentic-systems/skill/enterprise/02-skill-anatomy-and-metadata-schema.md", "docs/agentic-systems/skill/coding/02-skill-anatomy-and-metadata-schema.md"]
covers_version: "as of mid-2026"
tags: ["agentic-systems", "skill", "enterprise", "coding-tools", "research"]
---

# Skill Anatomy & Metadata Schema

> **Shared chapter.** The internal structure of a skill — the `SKILL.md` layout, folder anatomy (`references/`, `scripts/`, `templates/`, `evals/`), and the full metadata schema — is identical for enterprise and coding-assistant skills, because both build on the same open Agent Skills spec.

## Physical Structure

```
my-skill/
  SKILL.md          # REQUIRED
  references/       # OPTIONAL: deep docs loaded on demand
  scripts/           # OPTIONAL: helper scripts (executed, not read into context)
  templates/         # OPTIONAL: boilerplate/scaffold files (e.g., bug-report.md)
  evals/             # RECOMMENDED: regression tests (evals.json)
```

This baseline is identical for the enterprise and coding-assistant cases because it's the same open spec. GitHub's own example shows exactly this shape: a `github-issues/` skill next to a `code-review/` skill, each with its own `SKILL.md` and a `templates/` subfolder.

## SKILL.md Frontmatter — Reverse-Engineered Across Vendors

### Spec-baseline (portable everywhere)

| Field | Required | Notes |
| --- | --- | --- |
| `name` | **Yes** | Lowercase, hyphens, no spaces. GitHub caps this at 64 characters. Must match across the directory name convention in most implementations. |
| `description` | **Yes** | The single field every implementation uses for discovery matching. GitHub caps this at 1024 characters. Must state both *what* the skill does and *when* to use it — descriptions that only say "what" produce weak triggering. |

### Common Extensions (vendor-added, not in the minimal spec, but widely supported)

| Field | Seen in | Purpose |
| --- | --- | --- |
| `license` | GitHub Copilot | Legal terms for shared/marketplace skills |
| `argument-hint` | GitHub Copilot | Tells the user what to type after the slash command (`/webapp-testing for the login page`) |
| `user-invokable` | GitHub Copilot, others | Whether the skill appears in the manual `/` menu (default: true) |
| `disable-model-invocation` | GitHub Copilot | Prevents automatic, description-based triggering — skill becomes explicit-only |
| `metadata.author` | GitHub Copilot | Free-form author/team attribution |
| `context: fork` | Claude Code | Runs the skill's procedure in an isolated sub-context rather than the main conversation thread — ignored by non-Claude-Code agents, per Copilot's own documented interoperability behavior |
| `globs` | Cursor (`.mdc` rules, adjacent concept) | File-pattern scoping — not part of the Skill spec itself but frequently confused with it because Cursor's `.cursor/rules/*.mdc` frontmatter looks similar |
| `interface.display_name` / `interface.icon_*` / `interface.brand_color` | OpenAI Codex plugins | UI presentation metadata for the Codex app |
| `policy.allow_implicit_invocation` | OpenAI Codex | Equivalent concept to Copilot's `disable-model-invocation`, inverted polarity |
| `dependencies.tools` | OpenAI Codex | Declares required MCP servers/tools (`type: mcp`, `value`, `transport`, `url`) so the skill fails gracefully or prompts setup if the dependency is missing |
| `default_prompt` | OpenAI Codex | Pre-fills a starting prompt when the skill is explicitly invoked |

**Cross-tool portability note (empirically confirmed):** agent-specific fields not recognized by a given host are simply ignored rather than causing a load failure — Copilot explicitly documents that Claude Code's `context: fork` or Cursor's `globs` are safely dropped when the same `SKILL.md` is read by Copilot, while the `name`/`description`/body core works unmodified. This is precisely what makes "one skill, every agent" viable in practice, not just in theory.

### Enterprise/Team Governance Extensions (not vendor-native; recommended overlay)

| Field | Why add it for organizational use |
| --- | --- |
| `owner` | Accountability — who fixes it when the underlying tool/API changes |
| `version` (semver) | Enables safe updates and rollback in an org skill catalog |
| `repo_scope` | Which repositories/languages this skill is valid for — prevents cross-project misfire |
| `security_reviewed` (bool + date + reviewer) | Given Rules-File-Backdoor-class attacks, this should be mandatory before an org allows auto-loading of a *committed* skill from an untrusted or external source |
| `provenance` | GitHub's own `gh skill` CLI already writes this automatically for skills installed from a repository (source repo, ref, tree SHA) — a strong precedent for making provenance a standard field even beyond GitHub's own tooling |

## The Instructions Body

Recommended structure, synthesized from Anthropic's authoring guidance, GitHub's documentation, and observed high-quality community skills (e.g., the widely-cited "Superpowers" methodology skill):

1. **Purpose restatement** (redundant with `description` intentionally).
2. **Preconditions / required context** — what the agent should already know or have open before starting.
3. **Procedure** — the step-by-step method. High-quality examples enforce explicit stages (e.g., a TDD-enforcing skill requiring a failing test before any implementation code is written).
4. **File filters / language filters** — where relevant, state which file types or languages the procedure applies to (a Python-specific linting skill should say so explicitly, even though this isn't a formal schema field in most implementations — it belongs in prose or, where supported, `globs`-like frontmatter).
5. **Constraints and safety policies** — explicit "never do X" statements (never commit secrets, never force-push to main, never run destructive commands without confirmation).
6. **Examples / non-examples** — concrete before/after, plus a case where a *similar-looking* request should use a different skill or none at all.
7. **Output expectations** — exact format (PR description template, commit message convention, test file naming).
8. **References to bundled files** — explicit pointers, with clear language about whether a referenced item should be *executed* (a script) or *read* (a reference doc) — ambiguity here is a documented source of misfires.

## Mandatory vs. Optional Fields — Summary Table

| Category | Mandatory | Optional |
| --- | --- | --- |
| Spec baseline | `name`, `description`, body | — |
| Invocation control | — | `argument-hint`, `user-invokable`, `disable-model-invocation` / `allow_implicit_invocation` |
| Presentation | — | `license`, `interface.*` |
| Dependencies | — | `dependencies.tools` (MCP requirements) |
| Org governance (recommended overlay) | `owner` (org policy) | `version`, `repo_scope`, `provenance` |
| Security (recommended overlay, especially for externally-sourced skills) | `security_reviewed` for any skill from outside the org (org policy) | for first-party, internally-authored skills |

## Deliverable 4 — Reusable Metadata Schema

```yaml
# SKILL.md frontmatter — union schema (spec-required + common vendor extensions
# + recommended org-governance overlay). Fields not recognized by a given host
# are safely ignored by that host.

name: string                     # required; lowercase-hyphenated; <=64 chars
description: string              # required; <=1024 chars; state WHAT + WHEN
license: string                  # optional
argument-hint: string            # optional; shown after slash-invocation
user-invokable: boolean          # optional; default true
disable-model-invocation: boolean # optional; default false
context: enum[default, fork]     # optional; Claude Code-specific, safely ignored elsewhere

interface:                       # optional; Codex-plugin-style presentation metadata
  display_name: string
  short_description: string
  icon_small: string
  icon_large: string
  brand_color: string
  default_prompt: string

policy:
  allow_implicit_invocation: boolean  # optional; default true

dependencies:
  tools:
    - type: enum[mcp, builtin]
      value: string               # tool/server identifier
      transport: string           # e.g. streamable_http, stdio
      url: string                 # if applicable
      description: string

metadata:
  author: string
  owner: string                  # RECOMMENDED overlay: team/individual + contact
  version: string                # RECOMMENDED overlay: semver
  repo_scope: [string]            # RECOMMENDED overlay: applicable repos/languages
  provenance:                     # RECOMMENDED overlay, auto-populated where possible
    source_repo: string
    ref: string
    tree_sha: string
  security_reviewed:              # RECOMMENDED overlay for externally-sourced skills
    reviewed: boolean
    reviewed_by: string
    reviewed_at: string           # ISO 8601
  evaluation:                     # RECOMMENDED overlay
    eval_suite_ref: string
    last_pass_rate: number
```

This union schema is intentionally a **superset**: any given host reads only the subset it recognizes, and the `metadata.*` block is where organizational governance fields live without colliding with any vendor's reserved namespace.

---

Continue this series with [Execution Lifecycle & Tracing](30-execution-lifecycle-and-tracing.md).

## Related

- [Foundations: What Is an Agent Skill?](29-foundations-what-is-an-agent-skill.md) — the conceptual foundation this metadata schema formalizes.
- [Foundations: What Is a Coding Skill?](18-foundations-what-is-a-coding-skill.md) — the coding-assistant-specific counterpart.
