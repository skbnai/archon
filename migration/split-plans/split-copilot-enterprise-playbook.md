# Split Plan: copilot-enterprise-playbook

**Source**: `../knowledge-docs/docs/coding-tools/github-copilot/copilot-enterprise-playbook.md`
**Word count**: 6866 words
**Split strategy**: 3-way split (parts must each be &lt;2600 words per validator)

## Split Boundaries

**Part 1** (target: `docs/agentic-systems/coding-tools/07-copilot-enterprise-playbook.md`):
- Sections 1–3: Title/intro, GitHub Copilot Economics, AI Credits Cost Model, Pricing Reference, Token Billing, Cost Scenarios, Credit Forecasting, ROI Measurement, Coding Workflow Optimization (Green Zone vs Red Zone, Best Practices), Agent Mode Optimization (opening section)
- Estimated word count: ~2250 words
- Topic ID: `copilot-enterprise-playbook`
- Frontmatter: `supersedes: [original_path]`

**Part 2** (target: `docs/agentic-systems/coding-tools/parts/07-copilot-enterprise-playbook-part2.md`):
- Sections 3 (continued)–6: Agent Mode Optimization (remainder), Enterprise Governance, Context Engineering, Model Routing Strategy
- Estimated word count: ~2200 words
- Topic ID: `copilot-enterprise-playbook-part2`
- Frontmatter: `supersedes: []`

**Part 3** (target: `docs/agentic-systems/coding-tools/parts/07-copilot-enterprise-playbook-part3.md`):
- Sections 7–10: Developer Productivity Architecture, Anti-patterns (100 patterns across 10 categories), Principal Architect Playbook, Future Outlook 2026–2030
- Estimated word count: ~2250 words
- Topic ID: `copilot-enterprise-playbook-part3`
- Frontmatter: `supersedes: []`

## Nav Links Format (exact)

**Part 1 ending**:
```
**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/07-copilot-enterprise-playbook-part2) for Agent Governance, Context Engineering, and Model Routing. [See Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/07-copilot-enterprise-playbook-part3) for Anti-patterns, Playbook Checklists, and Roadmap.**
```

**Part 2 header and footer**:
```
**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/07-copilot-enterprise-playbook)** | **[Continue to Part 3 →](pathname:///archon/agentic-systems/coding-tools/parts/07-copilot-enterprise-playbook-part3)**
```

**Part 3 header**:
```
**[Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/07-copilot-enterprise-playbook)** | **[Back to Part 2 ←](pathname:///archon/agentic-systems/coding-tools/parts/07-copilot-enterprise-playbook-part2)**
```

## Frontmatter Template

```yaml
---
title: GitHub Copilot AI Credits Enterprise Mastery Guide
domain: agentic-systems
status: current
doc_type: guide
topic_id: [copilot-enterprise-playbook | copilot-enterprise-playbook-part2 | copilot-enterprise-playbook-part3]
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: [../knowledge-docs/docs/coding-tools/github-copilot/copilot-enterprise-playbook.md] # Part 1 only; [] for others
---
```

## Content Preservation

- Total source words: 6866
- Total split words target: >= 6179 (90% retention)
- Every section, anti-pattern entry, checklist, table, code block, and structured list must survive
- All 100 anti-patterns must be present across the 3 parts; none dropped
- No paraphrasing; preserve exact technical content and examples

## Validation

Run `python scripts/validate_frontmatter.py <part-file>` on each part.
Expected result: OK (under 2600 words per doc_type=guide)

## Status

Ready for implementation.
