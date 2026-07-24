# Split Plan: claude-best-practices.md → 3-part guide

**Source:** `../knowledge-docs/docs/coding-tools/claude/claude-best-practices.md` (6249 words)
**Domain:** agentic-systems
**Strategy:** 3-part split (faithful full transcription, no condensing)

## File Inventory

| Part | Survivor Path | Topic ID | Word Range | Content | Registered |
| --- | --- | --- | --- | --- | --- |
| Part 1 | docs/agentic-systems/coding-tools/32-claude-best-practices.md | claude-best-practices | 1-2080 | Domain 1 (Agentic Architecture) + Domain 2 (Tool Design) | Yes |
| Part 2 | docs/agentic-systems/coding-tools/parts/32-claude-best-practices-part2.md | claude-best-practices-part2 | 2081-4100 | Domain 3 (Configuration) + Domain 4.1-4.3 (Prompt Engineering intro) | Yes |
| Part 3 | docs/agentic-systems/coding-tools/parts/32-claude-best-practices-part3.md | claude-best-practices-part3 | 4101-6249 | Domain 4.4-4.6 (Prompt Engineering conclusion) + Domain 5 (Context Management) + Quick Reference | Yes |

## Split Points

**Part 1 → Part 2:** Ends at "**4.3 Structured Output via Tool Use**" with closing table. Domain 3 (Sections 3.1-3.5) + Domain 4.1-4.3 complete in Part 1.

**Part 2 → Part 3:** Ends at "**Domain 4 — Prompt Engineering & Structured Output (20%)**" intro + Sections 4.1-4.3 complete. Domain 4.4-4.6 moves to Part 3.

## Frontmatter Standards Applied

**Part 1 (Main):**
- topic_id: claude-best-practices
- supersedes: ["../../../knowledge-docs/docs/coding-tools/claude/claude-best-practices.md"]
- All 5 domains identified in intro table, Part 1 covers Domains 1-2 (45% of exam)

**Part 2:**
- topic_id: claude-best-practices-part2
- supersedes: [] (part1 carries full source supersedes)
- Covers Domain 3 (20%) + part of Domain 4 (Sections 4.1-4.3)

**Part 3:**
- topic_id: claude-best-practices-part3
- supersedes: []
- Covers Domain 4.4-4.6 + Domain 5 (15%) + Quick Reference + Exam Summary

## Word Count Validation

| Part | Word Count (wc -w) | Target | Status |
| --- | --- | --- | --- |
| Part 1 | TBD | ≤2200 | — |
| Part 2 | TBD | ≤2200 | — |
| Part 3 | TBD | ≤2200 | — |
| **Combined** | TBD | ≥5624 (90% of 6249) | — |

## Content Fidelity Checklist

- [x] All 5 domains mentioned in intro
- [x] Domains 1-2 fully covered in Part 1
- [x] Domain 3 fully covered in Part 2
- [x] Domain 4 split: 4.1-4.3 in Part 2, 4.4-4.6 in Part 3
- [x] Domain 5 fully covered in Part 3
- [x] Quick Reference (8 Rules + Exam Summary table) in Part 3
- [x] All tables transcribed in full (no row compression)
- [x] All best-practice/antipattern pairs complete
- [x] Nav-links: Part 1→Part 2, Part 2→Part 1 & Part 3, Part 3→Part 2
- [ ] validate_frontmatter.py pass on all 3 parts
- [ ] Box-drawing char check: 0 count
- [ ] wc -w ratio ≥90%

## Notes

Source file is certified architect exam reference with 5-domain structure. Splitting at domain boundaries (Domain 1-2 in Part 1, Domain 3 + Domain 4.1-4.3 in Part 2, Domain 4.4 + Domain 5 + reference in Part 3) preserves pedagogical flow. Each part is self-contained as exam study material within its domains.
