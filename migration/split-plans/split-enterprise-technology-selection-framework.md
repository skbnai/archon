# Split Plan: enterprise-technology-selection-framework

- old_path: `docs/enterprise-architecture/process/enterprise-technology-selection-framework.md`
- domain: architecture
- doc_type: reference-architecture (reclassified up from `guide`; 6,000-word ceiling per doc-standards — at 10,077 words this would need 5-6 parts under the 2,000-word guide ceiling, which doc-standards explicitly calls "absurd fragmentation" for this kind of deep multi-phase framework)
- wave: 2

Source is 10,077 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/75-enterprise-technology-selection-framework.md`;
discovered over-ceiling only when the migrator actually read it —
mapping.csv corrected to SPLIT, part2 row added). Split in 2 by the source's
own numbered `##` sections (1–20 + Glossary + Further Reading).

## Parts (2)

- **part1**: topic_id=`enterprise-technology-selection-framework` target=`docs/architecture/75-enterprise-technology-selection-framework.md`
  Source lines 15–729: TOC, §1 Technology Decision Philosophy, §2 Technology
  Classification Framework, §3 Enterprise Decision Criteria, §4 Weighted
  Decision Matrix Methods, §5 Buy vs Build vs Extend vs Partner, §6
  Architecture Fitness Assessment, §7 Technology Lifecycle Management, §8
  Proof of Concept Framework, §9 Enterprise Standards and Exceptions, §10
  Technology Rationalization. ~5,207 words.

- **part2**: topic_id=`enterprise-technology-selection-framework-part2` target=`docs/architecture/parts/25-enterprise-technology-selection-framework-part2.md`
  title: Enterprise Technology Selection & Decision Framework (Part 2 of 2): Risk, Vendor Evaluation, TCO, ARB Process & Templates
  Source lines 730–end: §11 Risk Assessment Framework, §12 Vendor Evaluation
  Framework, §13 Total Cost of Ownership, §14 Organisational Readiness, §15
  ARB Decision Process, §16 Decision Documentation (ADRs), §17 Measuring
  Success After Selection, §18 Common Decision Anti-Patterns, §19 Reference
  Models by Organisation Type, §20 Templates and Checklists, Glossary,
  Further Reading. ~4,870 words.

part1 owns `supersedes: [docs/enterprise-architecture/process/enterprise-technology-selection-framework.md]`; part2 does not repeat it. Each part gets a "Part N of 2" note cross-linking the other.
