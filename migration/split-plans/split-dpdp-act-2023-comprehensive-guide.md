# Split Plan: dpdp-act-2023-comprehensive-guide

- old_path: `docs/enterprise-architecture/specialization/DPDP_Act_2023_Comprehensive_Guide.md`
- domain: architecture
- doc_type: guide (2,000-word ceiling per doc-standards — this is a regulatory
  compliance guide, not a technical blueprint, so it does NOT qualify for the
  reference-architecture exception even though it's long)
- wave: 2

Source is 5,054 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/79-dpdp-act-2023-comprehensive-guide.md`; discovered
over-ceiling only when the migrator actually read it — mapping.csv corrected
to SPLIT, part2 and part3 rows added). Split into 3 parts by the source's
own numbered `##` sections (1–19). This page makes regulatory claims (India's
Digital Personal Data Protection Act 2023 / DPDP Rules 2025) — flag all
three parts for a research-grounding pass before the reviewer gate; do not
let the migrator ground these claims itself.

## Parts (3)

- **part1**: topic_id=`dpdp-act-2023-comprehensive-guide` target=`docs/architecture/79-dpdp-act-2023-comprehensive-guide.md`
  Source lines 18–238: TOC, §1 Executive Summary & Why This Matters Now, §2
  Legislative Background & Constitutional Foundation, §3 Core Framework —
  Key Definitions & Scope, §4 Seven Guiding Principles, §5 Data Principal
  Rights, §6 Data Fiduciary Obligations, §7 Significant Data Fiduciary (SDF)
  — Enhanced Obligations, §8 Consent Management. ~1,643 words.

- **part2**: topic_id=`dpdp-act-2023-comprehensive-guide-part2` target=`docs/architecture/parts/31-dpdp-act-2023-comprehensive-guide-part2.md`
  title: DPDP Act 2023 & DPDP Rules 2025 (Part 2 of 3): Data Discovery, DLP, Breach Notification, DPO & Penalties
  Source lines 239–552: §9 Data Discovery & Classification, §10 Data
  Protection & DLP Controls, §11 Breach Notification, §12 DPO as a Service &
  Managed Compliance, §13 Penalty Structure, §14 Implementation Roadmap
  (2025–2027). ~1,825 words.

- **part3**: topic_id=`dpdp-act-2023-comprehensive-guide-part3` target=`docs/architecture/parts/32-dpdp-act-2023-comprehensive-guide-part3.md`
  title: DPDP Act 2023 & DPDP Rules 2025 (Part 3 of 3): Anti-Patterns, GDPR Comparison, Technology Architecture & Compliance Checklist
  Source lines 553–end: §15 Anti-Patterns, §16 DPDP vs GDPR — Comparative
  Analysis, §17 Technology Architecture for DPDP Compliance, §18 Compliance
  Checklist, §19 Key Takeaways & Strategic Recommendations. ~1,586 words.

part1 owns `supersedes: [docs/enterprise-architecture/specialization/DPDP_Act_2023_Comprehensive_Guide.md]`; part2/part3 do not repeat it. Each part gets a "Part N of 3" note cross-linking the other two.
