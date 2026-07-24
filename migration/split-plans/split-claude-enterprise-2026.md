# Split Plan: claude-enterprise-2026

**Source**: `../knowledge-docs/docs/coding-tools/claude/claude-enterprise-2026.md`
**Word count**: 6701 words
**Split strategy**: 3-way split (parts must each be &lt;2600 words per validator)

## Split Boundaries

**Part 1** (target: `docs/agentic-systems/coding-tools/34-claude-enterprise-2026.md`):
- Sections 1–5: Deployment Options, Claude Platform on AWS, Amazon Bedrock, Google Cloud Vertex AI, Azure AI Foundry
- Estimated word count: ~2250 words
- Topic ID: `claude-enterprise-2026`
- Frontmatter: `supersedes: [original_path]`

**Part 2** (target: `docs/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part2.md`):
- Sections 6–10: Claude Enterprise Plan, Managed Agents, Security Architecture, Compliance Framework, Cost Governance
- Estimated word count: ~2200 words
- Topic ID: `claude-enterprise-2026-part2`
- Frontmatter: `supersedes: []`

**Part 3** (target: `docs/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part3.md`):
- Sections 11–19: Guardrails, Explainability, Human-in-the-Loop, Responsible AI, High Availability, Performance, Best Practices, Antipatterns, Deployment Checklist
- Estimated word count: ~2250 words
- Topic ID: `claude-enterprise-2026-part3`
- Frontmatter: `supersedes: []`

## Nav Links Format (exact)

**Part 1 ending**:
```
**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part2) for Claude Enterprise Plan, Managed Agents, Security, and Compliance. [See Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part3) for Guardrails, Explainability, Responsible AI, and Deployment Checklists.**
```

**Part 2 header and footer**:
```
**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/34-claude-enterprise-2026)** | **[Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part3)**
```

**Part 3 header**:
```
**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/34-claude-enterprise-2026)** | **[Back to Part 2 ←](pathname:///archon/agentic-systems/coding-tools/parts/34-claude-enterprise-2026-part2)**
```

## Frontmatter Template

```yaml
---
title: Claude Enterprise Deployment 2026
domain: agentic-systems
status: current
doc_type: guide
topic_id: [claude-enterprise-2026 | claude-enterprise-2026-part2 | claude-enterprise-2026-part3]
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: [../knowledge-docs/docs/coding-tools/claude/claude-enterprise-2026.md] # Part 1 only; [] for others
---
```

## Content Preservation

- Total source words: 6701
- Total split words target: >= 6030 (90% retention)
- Every section, code block, table, and list must survive the split
- No paraphrasing or condensing permitted

## Validation

Run `python scripts/validate_frontmatter.py <part-file>` on each part.
Expected result: OK (under 2600 words per doc_type=guide)

## Status

Ready for implementation.
