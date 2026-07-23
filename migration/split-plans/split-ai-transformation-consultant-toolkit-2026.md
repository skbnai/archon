# Split Plan: ai-transformation-consultant-toolkit-2026

- old_path: `docs/enterprise-architecture/specialization/AI_Transformation_Consultant_Toolkit_2026.md`
- domain: architecture
- doc_type: reference-architecture (reclassified up from `guide`; 6,000-word ceiling per doc-standards — at 9,233 words this is a deep multi-section toolkit, not a simple guide)
- wave: 2

Source is 9,233 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/77-ai-transformation-consultant-toolkit-2026.md`;
discovered over-ceiling only when the migrator actually read it —
mapping.csv corrected to SPLIT, part2 row added). Split in 2 by the source's
own H2 sections.

## Parts (2)

- **part1**: topic_id=`ai-transformation-consultant-toolkit-2026` target=`docs/architecture/77-ai-transformation-consultant-toolkit-2026.md`
  Source lines 14–1131: "AI Transformation" intro, "Client Maturity Journey
  & Archetypes", "AI Readiness Assessment (Scored)", "Discovery
  Questionnaire Bank" (largest single section — keep intact, do not
  truncate). ~4,458 words.

- **part2**: topic_id=`ai-transformation-consultant-toolkit-2026-part2` target=`docs/architecture/parts/27-ai-transformation-consultant-toolkit-2026-part2.md`
  title: AI Transformation Consultant Toolkit 2026 (Part 2 of 2): Interview Templates, Prioritisation, FAQs, Checklists & Deliverables
  Source lines 1132–end: "Stakeholder Interview Templates", "Use Case
  Prioritisation Framework", "FAQ Bank — All Client Scenarios",
  "Phase-Gated Checklists", "Templates & Deliverable Frameworks". ~4,775
  words.

part1 owns `supersedes: [docs/enterprise-architecture/specialization/AI_Transformation_Consultant_Toolkit_2026.md]`; part2 does not repeat it. Each part gets a "Part N of 2" note cross-linking the other.
