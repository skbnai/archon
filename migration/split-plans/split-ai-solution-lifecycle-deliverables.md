# Split Plan: ai-solution-lifecycle-deliverables

- old_path: `docs/enterprise-architecture/process/ai-solution-lifecycle-deliverables.md`
- domain: architecture
- doc_type: guide (2,000-word ceiling per doc-standards)
- wave: 2

Source is 4,092 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/74-ai-solution-lifecycle-deliverables.md`; discovered
over-ceiling only when the migrator actually read it — mapping.csv corrected
to SPLIT, part2 and part3 rows added). A 2-way split lands part1 at ~2,074
words — over the 2,000 ceiling — so this uses 3 parts instead, splitting
section 4 ("Role Deep-Dives", which has its own `###` sub-headings per
role, 4.1–4.7) across the part boundary.

## Parts (3)

- **part1**: topic_id=`ai-solution-lifecycle-deliverables` target=`docs/architecture/74-ai-solution-lifecycle-deliverables.md`
  Source lines 14–167: §1 Lifecycle Stages, §2 Roles and Audiences, §3
  Master Deliverables Matrix, §4 Role Deep-Dives intro + §4.1 Enterprise
  Architect. ~1,393 words.

- **part2**: topic_id=`ai-solution-lifecycle-deliverables-part2` target=`docs/architecture/parts/28-ai-solution-lifecycle-deliverables-part2.md`
  title: AI Solution Lifecycle Deliverables by Role (Part 2 of 3): Security, RAI/Governance, Solution, Distinguished, Data & Platform Architect Deep-Dives
  Source lines 168–495: §4.2 Security Architect, §4.3 RAI / Governance Lead,
  §4.4 Solution Architect, §4.5 Distinguished / Principal Architect, §4.6
  Data Architect, §4.7 Platform / MLOps Architect. ~1,459 words.

- **part3**: topic_id=`ai-solution-lifecycle-deliverables-part3` target=`docs/architecture/parts/29-ai-solution-lifecycle-deliverables-part3.md`
  title: AI Solution Lifecycle Deliverables by Role (Part 3 of 3): Use Case Walk-throughs & Architect's Checklist
  Source lines 496–end: §5 Use Case Walk-throughs (banking, healthcare,
  government examples — includes one inline code example around line 584,
  keep fenced), §6 Architect's Checklist. ~1,240 words.

part1 owns `supersedes: [docs/enterprise-architecture/process/ai-solution-lifecycle-deliverables.md]`; part2/part3 do not repeat it. Each part gets a "Part N of 3" note cross-linking the other two.
