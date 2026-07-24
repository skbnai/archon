# Split Plan: mcp-deep-guide

**Source:** `../knowledge-docs/docs/coding-tools/claude/mcp-deep-guide.md` (8415 words)

## Split Strategy

Semantic split into two balanced parts:
- **Part 1:** Protocol fundamentals, architecture, and implementation (Sections 1-10)
- **Part 2:** Enterprise deployment, operations, and best practices (Sections 11-20)

## Line Ranges

| Part | Start Line | End Line | Content | Words (est.) |
|------|-----------|----------|---------|--------------|
| Part 1 | 1 | 1206 | Frontmatter + Sections 1-10: Protocol overview, primitives, architecture, transport options, FastMCP Python server, TypeScript SDK, 2026 features, MCP Apps, Tasks extension, OAuth 2.1 authorization | ~4100 |
| Part 2 | 1207 | 2014 | Sections 11-20: Enterprise MCP governance, ecosystem, MCP Inspector, best practices, antipatterns, guardrails, versioning policy, performance, testing, evaluation harness | ~4200 |

## Frontmatter Settings

**Part 1:**
- `topic_id: mcp-deep-guide`
- `supersedes: ["../knowledge-docs/docs/coding-tools/claude/mcp-deep-guide.md"]`
- Continuation link to Part 2

**Part 2:**
- `topic_id: mcp-deep-guide-part2`
- `supersedes: []`
- Back-link to Part 1

## Key Content Preservation

- All 20 sections distributed: Part 1 (Sections 1-10), Part 2 (Sections 11-20)
- All code examples, JSON schemas, and tables preserved
- All tables of contents references intact
- Cross-references rewritten via mapping.csv
