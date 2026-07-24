---
title: Split Plan for claude-routines-guide
topic_id: claude-routines-guide
date_created: 2026-07-24
---

# Split Plan: claude-routines-guide

## Overview

Source file: `../knowledge-docs/docs/coding-tools/claude/claude_routines_guide.md` (749 lines, 3849 words)

Split into two parts due to guide doc_type word cap (2600 words):

- **Part 1:** Lines 1-565 (foundational concepts, setup, core scheduling tiers)
- **Part 2:** Lines 566-749 (advanced patterns, anti-patterns, quick reference)

## Target Files

| Part | Target Path | Topic ID | Lines | Status |
|------|------------|----------|-------|--------|
| 1 | `docs/agentic-systems/coding-tools/37-claude-routines-guide.md` | `claude-routines-guide` | 1-565 | Written |
| 2 | `docs/agentic-systems/coding-tools/parts/37-claude-routines-guide-part2.md` | `claude-routines-guide-part2` | 566-749 | Written |

## Split Rationale

Natural section boundary after "One-Time Reminders" section (line 565):
- Part 1 covers introduction through foundational patterns (sections 01-10)
- Part 2 covers advanced design patterns, anti-patterns, and reference (sections 11-16)

This split ensures both parts are under the 2600-word guide cap while maintaining thematic coherence.

## Navigation Links

- Part 1 includes: `[Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/37-claude-routines-guide-part2)`
- Part 2 includes: `[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/37-claude-routines-guide)`

## Frontmatter Configuration

Both parts:
- `domain: agentic-systems`
- `status: current`
- `date_created: 2026-07-24`
- `last_reviewed: 2026-07-24`

Part 1 only:
- `supersedes: [../knowledge-docs/docs/coding-tools/claude/claude_routines_guide.md]`

Part 2:
- `supersedes: []`
