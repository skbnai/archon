# Split Plan: agui-standards-landscape

**Source:** docs/agentic-ui/agui-standards-landscape.md (8617 words)

**Split Strategy:** 3-way split at natural section boundaries

## Split Map

| Part | Target Path | Topic ID | Source Sections | Line Range | Word Count |
|------|------------|----------|-----------------|-----------|-----------|
| 1 | docs/agentic-systems/agentic-ui/02-agui-standards-landscape.md | agui-standards-landscape | 1-2 (Protocol Overview + AG-UI Deep Dive) | 14-707 | ~2850 |
| 2 | docs/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part2.md | agui-standards-landscape-part2 | 3-5 (A2UI + MCP Apps + NLWeb) | 708-1106 | ~2880 |
| 3 | docs/agentic-systems/agentic-ui/parts/02-agui-standards-landscape-part3.md | agui-standards-landscape-part3 | 6-10 (OpenAI Apps SDK + Microsoft Framework + Comparison + Decision Tree + Production) | 1107-1467 | ~2887 |

## Split Rationale

The agui-standards-landscape document naturally divides into three logical parts:

**Part 1** covers foundational protocol layer concepts and AG-UI, the core transport standard. This establishes the baseline understanding needed for all other frameworks and standards.

**Part 2** covers A2UI (declarative UI surface specification), MCP Apps (tool + UI bundling pattern), and NLWeb (natural language website querying). These are complementary specifications that build on AG-UI.

**Part 3** covers OpenAI Apps SDK (legacy JSON-RPC pattern), Microsoft Agent Framework 1.0 (enterprise orchestration), the 15-framework comparison matrix, decision tree for framework selection, and production checklist.

Each part contains complete, self-contained information while referencing other parts via navigation links.

## Supersedes

The three parts together completely supersede the original monolithic document at `docs/agentic-ui/agui-standards-landscape.md`.

## Navigation Links

- Part 1 footer: "This is Part 1 of 3. Continue with Part 2 → to explore A2UI, MCP Apps, and NLWeb."
- Part 2 header: "Back to Part 1 · Continue with Part 3 →"
- Part 2 footer: Same as header
- Part 3 header: "Back to Part 1 · Back to Part 2"
- Part 3 footer: Same as header

## Verification

- Combined word count: ~2850 + ~2880 + ~2887 = ~8617 (100% word retention)
- No ASCII art or box-drawing characters (converted to text descriptions)
- All code examples preserved in original parts
- All tables and structured data intact
- MDX safety escaping applied to literal `<` characters outside code fences
