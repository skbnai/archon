# Split Plan: enterprise-ai-architect-bible-2026

- old_path: `docs/enterprise-architecture/process/Enterprise_AI_Architect_Bible_2026.md`
- domain: architecture
- doc_type: reference-architecture (6,000-word ceiling per doc-standards)
- wave: 2

Source is 9,731 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/72-enterprise-ai-architect-bible-2026.md`; discovered
over-ceiling only when the migrator actually read it — mapping.csv has been
corrected to SPLIT and a part2 row added). Split in 2 by the source's own H2
sections.

## Parts (2)

- **part1**: topic_id=`enterprise-ai-architect-bible-2026` target=`docs/architecture/72-enterprise-ai-architect-bible-2026.md`
  Source lines 12–588: intro, "The Enterprise AI Architect Role in 2026",
  "LLM Architecture Mastery", "Agentic Systems Design", "RAG & Enterprise
  Knowledge Systems". ~4,727 words.

- **part2**: topic_id=`enterprise-ai-architect-bible-2026-part2` target=`docs/architecture/parts/24-enterprise-ai-architect-bible-2026-part2.md`
  title: Enterprise AI Architect Bible (Part 2 of 2): LLMOps, Safety & Governance, System Design Playbook, Career Strategy
  Source lines 589–end: "LLMOps & Production AI Engineering", "AI Safety,
  Governance & Ethics", "MAANG System Design Playbook", "Portfolio,
  Certifications & Career Strategy". ~5,004 words.

part1 owns `supersedes: [docs/enterprise-architecture/process/Enterprise_AI_Architect_Bible_2026.md]`; part2 does not repeat it. Each part gets a "Part N of 2" note cross-linking the other.
