# Merge Plan: hub-career

## Cluster

| old_path | words | last_reviewed | source_type | disposition |
|---|---|---|---|---|
| docs/interview-prep/ea/index.md | 57 | 2026-07-10 | native-md | MERGE-INTO hub-career |
| docs/interview-prep/fde/index.md | 426 | 2026-07-13 | native-md | MERGE-INTO hub-career |
| docs/interview-prep/index.md | 122 | 2026-07-10 | native-md | MERGE-INTO hub-career |
| docs/soft-skills/index.md | 734 | 2026-07-14 | native-md | MERGE-INTO hub-career |

- target canonical path: `docs/career/index.md`
- domain: career
- wave: 8

## Survivor

Survivor is the existing fresh hub stub at `docs/career/index.md` (read in full — 33 lines, frontmatter `doc_type: hub`, `topic_id: hub-career`, `status: draft`, Scope bullets: Interview preparation / Certifications / Soft skills / Mental models / Role guides; a Related section linking to Learning Paths Hub and Asset Library Hub).

None of the four old files above is the survivor. Per doc-standards, `doc_type: hub` pages are curated navigation pages, not content pages — a hub is authored fresh from the current canonical set of TRACK'd children, not merged/concatenated from old prose. All substantive content in these four old index/section pages either (a) is a list of links to sibling documents that already have their own MIGRATE/TRACK rows into `docs/career/*` and `docs/assets/*` under separate topic_ids (per mapping.csv lines 570-593, 645-656), or (b) is section-organizing scaffolding (tables, "how to use this hub" guidance, navigation-by-goal tables) whose only durable value is the framing/scope it implies — which is captured by folding it into the hub's Scope/Related bullets, not by preserving old prose.

## Unique-Content Map

**docs/interview-prep/ea/index.md** (57 words)
- Body is a one-line description + 4 links to PDFs (EA Interview Master Guide, EA Interview Handbook, EA Interview Handbook DELTA, EA Interview Vol 3 — CTO & AI).
- All 4 targets already individually TRACK'd/MERGE'd (mapping.csv lines 584-587) into `docs/career/05,19,20-*`.
- No unique framing beyond "EA interview prep covers technical depth, AI strategy, leadership communication, CTO-level questions" — already subsumed by hub Scope bullet "Interview preparation."
- No unique content — safe to drop.

**docs/interview-prep/fde/index.md** (426 words)
- Comparison table "What Makes FDE Different" (FDE vs EA vs Solutions Architect across 6 dimensions) — not present elsewhere; useful framing but belongs in the FDE role-skills content itself (`interview-fde-role-skills-map`, mapping.csv line 591), not the domain hub.
- Market-sizing stat: "FDE job postings grew 729% YoY (Apr 2025→Apr 2026); comp $350K-$750K" — candidate fact for the FDE study-map page, not the hub; flagging so it isn't silently lost, but out of scope for this short curated hub.
- "Cross-Repo Study Path" — six-cluster reading order spanning coding-tools/claude, agentic-systems, ai-protocols, knowledge-engineering, ai-development, enterprise-architecture. This cross-domain reading order is real unique framing not captured anywhere in the hub stub or in the individually-tracked FDE pages. Recommend a short "Related" bullet on the hub pointing to the FDE track page once migrated, rather than reproducing the reading order on the hub itself.
- Links to Skills & Study Map, Life Transcript — both individually TRACK'd (interview-fde-role-skills-map → docs/career/23-*, fde-life-transcript → docs/assets/06-*).
- "Related Interview Guides" links (Enterprise Architect in the Age of AI, EA Senior Interview Questions, AI Agent Systems Interview Guide, ML & AI Interview Mastery Guide) — all individually TRACK'd elsewhere in interview-prep (lines 570, 575, 578, 581).
- Net: link targets fully covered by other MIGRATE/TRACK rows; only the comparative framing/stats are novel, and they belong on the destination FDE page, not the hub — noted for the migrator/researcher of that page, not for this hub.

**docs/interview-prep/index.md** (122 words)
- One-line description + links across Markdown/PDF/DOCX guides (Enterprise Architect in the Age of AI, EA Senior/HITL/Quality/Soft-Skills Interview Questions, AI Agent Systems Interview Guide, Agentic AI Platforms Questionnaire, EY AI Architect Guide, Enterprise GenAI Architect Guide, AI Engineer Question Bank, Hard Scenarios Interview Prep, ML & AI Interview Mastery Guide).
- Every single link target already has its own TRACK row into `docs/career/06` through `18` (mapping.csv lines 570-582).
- No unique framing beyond "question banks, scenario prep, behavioral guides for EA and AI roles" — already subsumed by hub Scope bullet "Interview preparation."
- No unique content — safe to drop.

**docs/soft-skills/index.md** (734 words) — checked carefully per instructions
- Structural framing not present in the hub stub: names "four skill areas" grouped as two thinking-skill guides (Problem-Solving, Creative Thinking) + two communication-training tracks (28-day starter, 12-week CTO deep track). This taxonomy (thinking skills vs. communication tracks) is real organizing content, not just a link list.
- Explicit sequencing relationship: "Problem-solving is convergent... Creative thinking is divergent... use them in sequence: reframe first, decompose second." — a genuine cross-document relationship claim, not captured by the hub's flat "Soft skills" / "Mental models" bullets.
- "Navigate by Goal" table (goal → starting document) — a curated routing table; useful pattern but keyed to old filenames/paths that no longer apply post-migration.
- "How the Two Programs Relate" — explains STAR/3-Act (30-Day Plan, Workbook) vs. Vinh Giang Hormone Framework/7 Storytelling Secrets (CTO program) use different but compatible terminology, and that a Workbook's "Personal Story Library" feeds into the CTO program's "Story Bank." This is a nuanced cross-reference between two now-separately-tracked pages (soft-skills-voice-training-30-day-plan → docs/career/27, soft-skills-cto-voice-mastery → docs/career/24) that is not reconstructable from either page's title alone.
- All 6 underlying documents are already individually TRACK'd (Problem_Solving_Skills → career/26, Creative_Thinking_Skills → career/25, Voice_Training_30Day_Plan → career/27, Mental_Models_for_Voice_Training → MERGE-INTO mental-models-executive-cognition, Storytelling_Exercise_Workbook → assets/07, CTO_Voice_Mastery_Program → career/24).
- Verdict: link targets are fully covered elsewhere; the sequencing/relationship framing (convergent-then-divergent; Story Library feeds Story Bank) is the one piece of real cross-document narrative in this cluster. It is a candidate for a one-line "Related" callout on the hub (e.g., "start with problem-solving/creative-thinking before the voice-training tracks") but is prose-level detail that belongs on the destination pages themselves (e.g., as a "Related" note on `soft-skills-voice-training-30-day-plan` or `soft-skills-cto-voice-mastery`), not duplicated onto the short curated hub. Flagging for the stage-04/05 migrator of those two pages rather than pulling it into hub-career.

## Target Structure

Keep the current stub's shape — short curated hub, links only, no merged prose:

```
# Career Hub  (title, frontmatter unchanged)

<intro paragraph — unchanged>

## Scope
- Interview preparation
- Certifications
- Soft skills
- Mental models
- Role guides

## Related
- Learning Paths Hub
- Asset Library Hub
```

Comparison to current stub: no structural change is required by this cluster. All four losers' link targets are already reachable through the individually-tracked destination pages under `docs/career/*` and `docs/assets/*`, which will themselves be linked from the domain's sidebar/category index once those pages land (stage-04 migration), not from this hub's prose. No new H2/H3 needed on the hub itself. Optional (non-binding) enhancement for whoever next edits this hub: the Scope bullet ordering could mirror the two natural sub-groupings surfaced above (interview prep vs. soft-skills thinking/communication tracks), but this is a nice-to-have, not a requirement of this merge plan.

## Transform Notes

- ASCII art: none flagged in any of the 4 old files (confirmed on read).
- Cross-repo/absolute links needing rewrite if any prose from these files were ever reused: `docs/interview-prep/ea/index.md` and `docs/interview-prep/index.md` use absolute `/knowledge-docs/interview-prep/...` paths to PDFs — these are old-repo-relative asset links and do not resolve in the new repo. Since this hub only receives curated bullets (not reproduced links to PDFs), no rewrite is needed here; this is noted only in case any destination TRACK page re-derives a link from these old paths.
- `docs/interview-prep/fde/index.md`'s "Cross-Repo Study Path" fenced block lists paths like `coding-tools/claude/`, `agentic-systems/skill/enterprise/`, `ai-protocols/mcp/`, etc. — these are old-repo section paths, not target paths, and would need remapping to new canonical topic_ids if ever reproduced. Not carried onto the hub.

## Doc Type & Template

doc_type: hub — no template — short curated hub page per governance/DOC_TYPES.md.
