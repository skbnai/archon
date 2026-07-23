# Split Plan: eaka-research-study

- old_path: `docs/enterprise-architecture/specialization/EAKA_Research_Study.md`
- domain: architecture
- doc_type: research-report (2,000-word ceiling per doc-standards — the
  6,000-word exception is reference-architecture only)
- wave: 2

Source is 4,677 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/81-eaka-research-study.md`; discovered over-ceiling only
when the migrator actually read it — mapping.csv corrected to SPLIT, part2
and part3 rows added). Split into 3 parts by the source's own numbered `###`
sections (1–14) plus its front/back matter.

## Parts (3)

- **part1**: topic_id=`eaka-research-study` target=`docs/architecture/81-eaka-research-study.md`
  Source lines 16–288: title/header block, "RESEARCH TYPE — Comprehensive
  Study", Table of Contents, Executive Summary, §1 Enterprise Knowledge
  Discovery, §2 Knowledge Classification, §3 Agent Knowledge Planning, §4
  Enterprise Skills Architecture. ~1,492 words.

- **part2**: topic_id=`eaka-research-study-part2` target=`docs/architecture/parts/33-eaka-research-study-part2.md`
  title: Enterprise Agent Knowledge Architecture (EAKA) Research Study (Part 2 of 3): Skill Composition, Governance, Knowledge Graph, MCP & Ecosystem Integration
  Source lines 289–542: §5 Dynamic Skill Composition, §6 Agent Knowledge
  Governance, §7 Enterprise Knowledge Graph, §8 MCP Integration, §9
  Microsoft Agent Ecosystem Integration. ~1,513 words.

- **part3**: topic_id=`eaka-research-study-part3` target=`docs/architecture/parts/34-eaka-research-study-part3.md`
  title: Enterprise Agent Knowledge Architecture (EAKA) Research Study (Part 3 of 3): Context Engineering, Reliability, Reference Architecture, Lifecycle & Maturity Model
  Source lines 543–end: §10 Knowledge Context Engineering, §11 Agent
  Reliability, §12 Enterprise Reference Architecture, §13 AI-Assisted
  Knowledge Lifecycle, §14 Maturity Model & Roadmap, Decision Matrix —
  Platform Comparison. ~1,672 words.

part1 owns `supersedes: [docs/enterprise-architecture/specialization/EAKA_Research_Study.md]`; part2/part3 do not repeat it. Each part gets a "Part N of 3" note cross-linking the other two.
