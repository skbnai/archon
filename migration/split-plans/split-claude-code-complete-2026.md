# Split Plan: claude-code-complete-2026

## Overview
Source file `../knowledge-docs/docs/coding-tools/claude/claude-code-complete-2026.md` (5875 words) split into 2 parts to fit within guide doc_type word cap.

## Split Strategy
Logical split at Section 10 (Custom Slash Commands) to balance content across parts while maintaining coherent sections.

## Part 1: 33-claude-code-complete-2026.md
**Topic ID:** claude-code-complete-2026
**Word Count:** 2,550 words
**Doc Type:** guide
**Sections:**
- What Is Claude Code? (behavioral model, comparison to Claude.ai Chat)
- Prerequisites and Installation (Node.js, npm, authentication methods)
- First Run Walkthrough (interactive patterns)
- Core Workflow: Ask → Plan → Edit → Verify
- CLAUDE.md: Project Instructions (hierarchy, best practices)
- Slash Commands Reference (verified commands list)
- Memory System (persistent memory across sessions)
- Hooks System (PreToolUse, PostToolUse, Stop, Notification hooks)
- MCP Integration (configuration, usage, writing minimal MCP servers)

## Part 2: 33-claude-code-complete-2026-part2.md
**Topic ID:** claude-code-complete-2026-part2
**Word Count:** 3,447 words
**Doc Type:** guide
**Sections:**
- Custom Slash Commands (directory structure, file format, examples)
- Skills System (skill definition, invocation patterns)
- Permissions (tool patterns, scoping strategies, interactive prompts)
- CI/CD Integration (CI mode, GitHub Actions, pre-commit hooks, environment variables)
- IDE Extensions (VS Code, JetBrains, CLI vs IDE trade-offs)
- Token Optimization (compact command, cost monitoring, strategies)
- Cost Controls (model selection, session budgets, usage tracking)
- Guardrails (CLAUDE.md restrictions, tool denylists, confirmation requirements)
- Human-in-the-Loop (HITL) Patterns (explicit pause points, diff review, staged execution)
- Best Practices (19 actionable practices)
- Antipatterns (12 common pitfalls to avoid)
- Troubleshooting (authentication, MCP servers, hooks, permissions, context limits, slow responses)

## Metadata
- **Source:** ../knowledge-docs/docs/coding-tools/claude/claude-code-complete-2026.md
- **Original Word Count:** 5,875 words
- **Combined Word Count:** 5,997 words
- **Retention Ratio:** 102.1%
- **Date Created:** 2026-07-24
- **Frontmatter:** Properly formatted with topic_id, domain, doc_type, supersedes, last_reviewed

## Navigation Links
- Part 1 links to Part 2 via split nav link at end
- Part 2 links back to Part 1 via split nav link at end
- Format: `pathname:///archon/agentic-systems/<subpath>/parts/<filename>`
