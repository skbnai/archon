# Split Plan: AgentCore Memory — Gaps, Extensions & 2026 Research

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/aws/AgentCore_Memory_Gaps_Extensions_2026.md` (3167 words)

**Reason:** Word count exceeds guide doc_type cap (2000 words)

## Split Boundary

**Part 1 (Main):** `docs/platforms/16-agentcore-memory-gaps-extensions-2026.md`
- Source lines: 1–191
- Sections: 1 (FileSessionManager), 2 (Conversation Managers), 3 (Custom Strategy Wiring)
- Content: Session persistence backends, sliding window/summarizing managers, built-in vs self-managed extraction strategies, Lambda infrastructure wiring
- Target word count: ~1500 words

**Part 2 (Supplementary):** `docs/platforms/parts/16-agentcore-memory-gaps-extensions-2026-part2.md`
- Source lines: 192–399
- Sections: 4 (Structured Extraction), 5 (Graph Memory), 6 (Emerging Research), 7 (Decision Guide)
- Content: Pydantic schema design, Graphiti/MAGMA temporal graphs, research landscape (Zep, MAGMA, MemOS, Nemori, HyperGraphRAG), benchmark comparison, memory layer decision matrix
- Target word count: ~1667 words

## Mapping

| Section | Part | Title |
|---------|------|-------|
| 1 | 1 | FileSessionManager — The Missing Chapter |
| 2 | 1 | Conversation Managers — Sliding Window, Summarising & Null |
| 3 | 1 | Custom Strategy Wiring — Built-in Overrides & Self-Managed Lambda |
| 4 | 2 | Structured Extraction — Schema, Wiring & Prompt Changes |
| 5 | 2 | Graph Memory — Graphiti, MAGMA & Integration Patterns |
| 6 | 2 | Emerging Research & Adoptions — Agent Memory 2025–2026 |
| 7 | 2 | Consolidated Decision Guide — Which Memory Layer for Which Problem |

## Navigation

- Part 1 ends with: "See Part 2 (docs/platforms/parts/16-agentcore-memory-gaps-extensions-2026-part2.md) for advanced memory patterns: structured extraction, graph memory, and 2026 research landscape..."
- Part 2 begins with: "Continuation from Part 1 (Sections 1–3). Covers advanced memory patterns and emerging 2025–2026 research."
- Topic ID: Both parts share `agentcore-memory-gaps-extensions-2026`
- Part 1 is canonical (`topic_id: agentcore-memory-gaps-extensions-2026`)
- Part 2 uses `topic_id: agentcore-memory-gaps-extensions-2026-part2` and `supersedes: []`
