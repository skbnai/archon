# Split Plan: observability

**Source**: `../knowledge-docs/docs/agentic-ui/observability.md`
**Word count**: 6732 words
**Split strategy**: 3-way split (parts must each be &lt;2600 words per validator)

## Split Boundaries

**Part 1** (target: `docs/agentic-systems/agentic-ui/14-observability.md`):
- Sections 1–4: Four-Pillar Observability Model, Signal Taxonomy, Signal Priority Matrix, Distributed Tracing for Agentic Workflows, Trace Hierarchy, Mandatory Span Attributes (partial)
- Estimated word count: ~2200 words
- Topic ID: `observability`
- Frontmatter: `supersedes: [original_path]`

**Part 2** (target: `docs/agentic-systems/agentic-ui/parts/14-observability-part2.md`):
- Sections 4 (continued)–8: Remainder of Distributed Tracing, AG-UI Event Telemetry, Frontend/UI Telemetry, LLM Observability, Tool Observability, Memory Observability
- Estimated word count: ~2250 words
- Topic ID: `observability-part2`
- Frontmatter: `supersedes: []`

**Part 3** (target: `docs/agentic-systems/agentic-ui/parts/14-observability-part3.md`):
- Sections 8 (continued)–13: Safety Observability, Conversation Analytics, Business Analytics Dashboard, Alerting Strategy, Observability Tool Comparison, Anti-patterns
- Estimated word count: ~2280 words
- Topic ID: `observability-part3`
- Frontmatter: `supersedes: []`

## Nav Links Format (exact)

**Part 1 ending**:
```
**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/14-observability-part2) for AG-UI Telemetry, Frontend Metrics, LLM and Tool Observability. [See Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/14-observability-part3) for Safety Observability, Analytics, and Alerting.**
```

**Part 2 header and footer**:
```
**[Back to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/14-observability)** | **[Continue to Part 3 →](pathname:///archon/agentic-systems/agentic-ui/parts/14-observability-part3)**
```

**Part 3 header**:
```
**[Back to Part 1 ←](pathname:///archon/agentic-systems/agentic-ui/14-observability)** | **[Back to Part 2 ←](pathname:///archon/agentic-systems/agentic-ui/parts/14-observability-part2)**
```

## Frontmatter Template

```yaml
---
title: Observability for Agentic Applications
domain: agentic-systems
status: current
doc_type: guide
topic_id: [observability | observability-part2 | observability-part3]
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes: [../knowledge-docs/docs/agentic-ui/observability.md] # Part 1 only; [] for others
---
```

## Content Preservation

- Total source words: 6732
- Total split words target: >= 6058 (90% retention)
- Every section, code block, table, list, and YAML example must survive
- No paraphrasing or condensing; preserve all technical detail

## Validation

Run `python scripts/validate_frontmatter.py <part-file>` on each part.
Expected result: OK (under 2600 words per doc_type=guide)

## Status

Ready for implementation.
