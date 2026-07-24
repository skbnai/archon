---
title: Split Plan for ruflo-agentic-ai-guide
topic_id: ruflo-agentic-ai-guide
date_created: 2026-07-24
---

# Split Plan: ruflo-agentic-ai-guide

## Overview

Source file: `../knowledge-docs/docs/coding-tools/claude/ruflo-agentic-ai-guide.md` (1288 lines, 5471 words)

Split into two parts due to guide doc_type word cap (2600 words):

- **Part 1:** Lines 1-650 (overview through parallelism concepts)
- **Part 2:** Lines 651-1288 (token optimization, cost optimization, guardrails, governance)

## Target Files

| Part | Target Path | Topic ID | Status |
|------|------------|----------|--------|
| 1 | `docs/agentic-systems/coding-tools/41-ruflo-agentic-ai-guide.md` | `ruflo-agentic-ai-guide` | Written |
| 2 | `docs/agentic-systems/coding-tools/parts/41-ruflo-agentic-ai-guide-part2.md` | `ruflo-agentic-ai-guide-part2` | Written |

## Split Rationale

Split after section 11 (Parallelism) to provide:
- Part 1: Foundation, architecture, multi-agent patterns, memory systems, evaluation, stress testing, and parallelism
- Part 2: Optimization strategies (token and cost), guardrails, governance, CI/CD integration, best practices, and anti-patterns

Both parts under 2600-word guide cap while maintaining thematic coherence.

## Word Count Verification

- Source: 5471 words
- Part 1 + Part 2: 5520 words
- Ratio: 100.9% (PASS ✓)

## Navigation Links

- Part 1 includes: `[Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/41-ruflo-agentic-ai-guide-part2)`
- Part 2 includes: `[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/41-ruflo-agentic-ai-guide)`
