# Split Plan: ai-invoice-auditor-architecture

- old_path: `docs/enterprise-architecture/specialization/AI_Invoice_Auditor_Architecture_v5.md`
- domain: architecture
- doc_type: reference-architecture (6,000-word ceiling per doc-standards)
- wave: 2

Source is ~6,700 words (originally mapped as a plain MIGRATE row targeting
`docs/architecture/76-ai-invoice-auditor-architecture.md`; discovered
over-ceiling only when the migrator actually read it — mapping.csv corrected
to SPLIT, part2 row added). Only marginally over the 6,000 ceiling, but
genuinely exceeds it, so split in 2 rather than force a single 6,700-word
page.

**IMPORTANT page-styling note**: this source has NO fenced code blocks —
Python snippets are written as raw unfenced text with `##`-prefixed comment
lines mixed directly into prose (e.g. lines 55–73 under "2.2 SQLite
Checkpointer Setup"). These `##` lines are NOT markdown headings even though
they match heading syntax — they are code comments belonging to the
surrounding snippet. Wrap every such snippet in proper ```python fences
during migration; do not treat `## src/core/persistence.py`-style lines as
section headings or split boundaries. The real section structure uses bold
`**N. Title**` H2 headings (§1–§13), which is what this split follows.

## Parts (2)

- **part1**: topic_id=`ai-invoice-auditor-architecture` target=`docs/architecture/76-ai-invoice-auditor-architecture.md`
  Source lines 26–753: §1 What Changed in v5.0, §2 SQLite-First
  Infrastructure, §3 Human-in-the-Loop (HumanInTheLoopMiddleware), §4
  Multi-Agent Handoffs, §5 Runtime Context Injection, §6 Short-Term &
  Long-Term Memory. ~3,127 words (post-fencing count may shift slightly).

- **part2**: topic_id=`ai-invoice-auditor-architecture-part2` target=`docs/architecture/parts/26-ai-invoice-auditor-architecture-part2.md`
  title: AI Invoice Auditor Architecture v5 (Part 2 of 2): Skills, Observability, UI Pages, Deployment & Glossary
  Source lines 754–end: §7 Skills (Prompt-Driven Progressive Disclosure), §8
  Observability (SQLite MetricsDB), §9 UI Pages Specification, §10 Updated
  Project Folder Structure, §11 requirements.txt, §12 Updated Sprint Plan,
  §13 Glossary. ~3,543 words.

part1 owns `supersedes: [docs/enterprise-architecture/specialization/AI_Invoice_Auditor_Architecture_v5.md]`; part2 does not repeat it. Each part gets a "Part N of 2" note cross-linking the other.
