---
title: "Claude Code Cheat Sheet"
doc_type: guide
domain: agentic-systems
topic_id: cheatsheet-1-claude-code
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/Cheatsheet_1_Claude_Code.md
---

# Claude Code Cheat Sheet

Complete Reference Cheat Sheet - Anthropic Partner Certification EA

## Built-in Tools — Selection Guide

### Grep

Search **FILE CONTENTS** for patterns

→ Finding function callers, error messages, import statements, string patterns inside files

### Glob

Match **FILE PATHS/NAMES** by pattern

→ **/*.test.tsx finds all TS test files recursively. Navigate structure, not content

### Read

**Full file read** — entire file into context

→ Always Read before Write to preserve unmodified content

### Write

**Full file write** — overwrites completely

→ Use after Read when Edit fails on non-unique matches

### Edit

**Targeted modification** via unique text matching

→ Specify exact text to find (must be unique) → replace. Surgical, minimal diff

### Bash

**Execute shell commands** in the environment

→ Run tests, git ops, npm install, lint checks, build commands

**⚠️ Edit FAILS when text appears more than once → fallback: Read + Write**

## CLAUDE.md — Configuration Reference

### What to include

- **Project context:** Repository structure, tech stack, architecture overview, key directories
- **Coding conventions:** Style guide, naming patterns, design patterns to follow/avoid
- **Test commands:** How to run unit/integration tests so Claude can self-validate changes
- **Build/lint commands:** npm run build, eslint, prettier — Claude runs these after changes
- **Custom slash cmds:** /review, /deploy, /test — shortcuts to trigger specific behaviors
- **Agent Skills:** Reusable team-specific capabilities that persist across sessions
- **MCP servers:** Which servers to connect, what tools they expose, when to use them

### Do NOT include
- API keys, secrets, credentials — use environment variables

**✓ CLAUDE.md persists knowledge across sessions — team shares conventions without re-explaining**

### Agent Skills vs Slash Commands

**Agent Skills:**
- Reusable capabilities
- Complex multi-step behaviors
- Team knowledge (deploy process)
- Defined in CLAUDE.md

**Slash Commands:**
- Quick shortcuts
- Trigger specific skill/behavior
- /review, /test, /explain
- Saves repetitive typing

## Plan Mode vs Direct Execution

| **PLAN MODE** | **DIRECT MODE** |
|---|---|
| Proposes actions first | Executes immediately |
| Human reviews before run | No review step |
| Higher safety, slower | Fast iteration |
| High-risk operations | Low-risk dev tasks |
| Major refactoring | Bug fixes, additions |
| Production changes | Local development |
| File deletions | Read operations |

**✓ Plan mode = human oversight at critical decision points**

## Session Management

- **fork_session:** Creates parallel branches from current state — compare 2 refactoring approaches simultaneously
- **Session resume:** Continues from prior context — use when prior state is still valid/relevant
- **Fresh + summaries:** Start new session, inject summarized context — use when tool results are stale
- **Targeted re-analysis:** Inform resumed session about specific file changes — avoids full re-exploration

### When to Resume vs Fresh Start

- **Resume:** prior context mostly valid, files unchanged, continuing same task
- **Fresh:** file system changed, new requirements, stale tool results, new codebase

## CI/CD Integration

### System Capabilities
- Automated code review on every PR
- Test case generation for new code
- PR feedback with structured output
- Runs in pipeline — no human trigger

### Prompt Design Goals
- **Actionable feedback:** File + line + issue + severity + suggested fix
- **Minimize false positives:** Clear criteria, scope boundaries, what NOT to flag
- **Severity levels:** error / warning / suggestion — not all equal weight

### Primary Domains Tested
- Claude Code Config
- Prompt Engineering

## Tool Selection Decision Tree

### Goal: Find something

- Function all callers? → Grep (content)
- All .tsx files? → Glob (paths)
- Error message in logs? → Grep (content)
- Config file location? → Glob (paths)
- Import pattern? → Grep (content)

### Goal: Modify a file

- Change one unique thing? → Edit
- Edit fails (non-unique)? → Read+Write
- Create new file? → Write directly
- Large restructure? → Read+Write

## Glob Pattern Examples

```
# All TypeScript test files
**/*.test.tsx
**/*.spec.ts

# All files in src/
src/**/*

# Config files
**/*.config.js
**/.env*

# Nested components
src/components/**/*.tsx
```

## Grep Examples

```
# Find all callers of fn
grep -r "myFunction(" .

# Find imports
grep -r "from 'lodash'" .

# Error messages
grep -r "Cannot read" logs/
```

## Anti-Patterns & Common Mistakes

- Using Edit on non-unique text → always fails silently or wrong match
- Writing files without Reading first → overwrites unintended content
- Using Glob to search file content → only matches paths/filenames
- Using Grep to find files by name → use Glob for paths
- Storing secrets in CLAUDE.md → use environment variables
- Running destructive Bash without plan mode → data loss risk
- Not informing resumed session of file changes → stale re-analysis

## EXAM TRAPS

- **Grep vs Glob:** Grep=contents, Glob=paths — exam loves this distinction
- **Edit fallback:** non-unique match → Read+Write (not just retry Edit)
- **Plan mode:** requires human review BEFORE execution, not just logging
- **fork_session:** parallel exploration branches — not git fork

## Scenario 2: Code Generation

**Context:** Team uses Claude Code for gen, refactoring, debugging, docs

**Key task:** Integrate into dev workflow with CLAUDE.md + custom commands + plan mode

**Primary domains:** Claude Code Config, Context Management

### Setup Checklist

- CLAUDE.md with project structure
- Custom slash commands for common tasks
- Test command so Claude self-validates
- Define Agent Skills for team workflows
- MCP servers for Jira/GitHub integration
- Plan mode for risky operations

## Key Exam Facts — Domain 3

- **Domain weight:** 20% of exam (tied with Domain 4)
- **Primary scenarios:** Scenario 2 (Code Gen), Scenario 4 (Dev Productivity), Scenario 5 (CI/CD)
- **CLAUDE.md purpose:** Project context, conventions, commands — persists across sessions
- **Plan mode trigger:** High-risk, production changes, major refactoring, deletions
- **fork_session:** Parallel exploration branches, NOT git fork
- **Edit requirement:** Text must appear EXACTLY ONCE — otherwise fails
- **Grep:** = content. Searches inside files for patterns
- **Glob:** = paths. Matches file/directory names and patterns

## Scenario 4: Developer Productivity

**Context:** Integrating Claude into day-to-day dev workflow for productivity

**Primary domains:** Tool Design &amp; MCP, Claude Code Config, Agentic Architecture

### Productivity Patterns

- MCP connects Claude to Jira, GitHub, Slack
- Slash commands for code review workflow
- Agent Skills for team-specific processes
- fork_session for A/B refactoring
- Plan mode before production deployments
- Resumed sessions preserve work context

**✓ Dev productivity = tool integrations + configured conventions + smart session management**
