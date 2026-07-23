# Split Plan: akes-addendum-document-update-and-versioning

- old_path: `docs/enterprise-architecture/specialization/AKES_Addendum_Document_Update_and_Versioning.md`
- domain: architecture
- doc_type: guide (2,000-word ceiling per doc-standards)
- wave: 2

Source is 3,685 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/78-akes-addendum-document-update-and-versioning.md`;
discovered over-ceiling only when the migrator actually read it —
mapping.csv corrected to SPLIT, part2 row added). Note: the source's own
section numbering has gaps (A2 and A9 don't exist in this document) —
that's intentional in the source, not a migration error; don't renumber.
Split in 2 by the source's own `##` sections.

## Parts (2)

- **part1**: topic_id=`akes-addendum-document-update-and-versioning` target=`docs/architecture/78-akes-addendum-document-update-and-versioning.md`
  Source lines 16–202: Contents, A1 Overview & Design Intent, A3 How Updates
  Are Triggered, A4 The Three Update Paths, A5 Version Store — Schema &
  Provenance. ~1,896 words.

- **part2**: topic_id=`akes-addendum-document-update-and-versioning-part2` target=`docs/architecture/parts/30-akes-addendum-document-update-and-versioning-part2.md`
  title: AKES Addendum: Document Update & Versioning (Part 2 of 2): Changelog, Partial Updates, Retention & Governance Integration
  Source lines 203–end: A6 Changelog Rollup & Consumer-Facing Views, A7
  Partial Updates — Section-Level Granularity, A8 Version Retention &
  Compaction Policy, A10 Integration with the Governance & Trust Model.
  ~1,789 words.

part1's 1,896-word count is close to the 2,000 ceiling — during page-styling cleanup, trim any redundant PDF-conversion filler if present to keep real headroom; do not let it land over 2,000 after frontmatter/nav additions. part1 owns `supersedes: [docs/enterprise-architecture/specialization/AKES_Addendum_Document_Update_and_Versioning.md]`; part2 does not repeat it. Each part gets a "Part N of 2" note cross-linking the other.
