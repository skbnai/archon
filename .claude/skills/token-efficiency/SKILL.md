---
name: token-efficiency
description: >
  Use at the start of any large task (migration wave, audit, bulk research,
  corpus-wide refactor) to plan execution with minimal token usage, and
  whenever context feels bloated or repeated file reads are happening.
---

# Token Efficiency

## Rules of engagement

1. **Manifests over corpus.** Answer "what exists / where / status" questions
   from `migration/inventory.csv` and `CANONICAL_REGISTRY.yaml` (grep them),
   never by re-reading docs.
2. **Subagents for bulk I/O.** Reading >3 long files, web research, or old-repo
   analysis → delegate to a subagent; require a bounded summary format back
   (e.g., "≤ 20 lines per file: purpose, unique sections, dup candidates").
3. **Batch by wave.** Process one domain wave at a time; finish and commit
   before loading the next. Never hold two waves in context.
4. **Targeted reads.** Use grep/head/view-ranges to read the sections you need,
   not whole files.
5. **Don't echo.** Never paste full file contents into responses or plans;
   reference paths + line ranges.
6. **Model tiering.** Mechanical transforms (frontmatter injection, renames,
   link rewrites) → migrator agent on a fast/cheap model; judgment work
   (merge decisions, reviews) → stronger model.
7. **Write once.** Draft complete pages before writing; avoid write-read-rewrite
   loops. Fix validator errors from the hook message, not by re-reading.
8. **Never trust a subagent's self-reported numbers.** Migrator/reviewer agents
   have repeatedly reported wrong word counts, "no ASCII art found" when there
   was, and "all links resolved" when many weren't — even "task complete" at a
   fraction of the batch. After every batch, re-run the real checks yourself
   (`registry_check.py`, `dedup_check.py`, a word-count script, an ASCII-art
   grep, a link-resolution pass) rather than accepting the agent's prose
   summary as ground truth. This is cheap compared to a reviewer bounce.
