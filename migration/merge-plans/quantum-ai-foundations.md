# Merge Plan: quantum-ai-foundations

## Cluster

| old_path | words | last_reviewed | source_type | mermaid_count | disposition |
| --- | --- | --- | --- | --- | --- |
| `docs/quantum/zero-to-mastery-part1-foundations.md` | 3098 | 2026-07-17 | native-md | 0 | MIGRATE (survivor) |
| `docs/quantum/zero-to-mastery.md` | 778 | 2026-07-17 | native-md | 1 | MERGE-INTO (loser) |

- **target_topic_id:** `quantum-ai-foundations`
- **target canonical path:** `docs/platforms/01-quantum-ai-foundations.md`
- **domain:** platforms
- **wave:** 6

**Series context (not this plan's job to resolve):** `zero-to-mastery-part1-foundations.md` is part 1 of a 4-part series. `migration/mapping.csv` already carries the other three parts as independent MIGRATE rows in the same wave:

- `docs/quantum/zero-to-mastery-part2-quantum-ai.md` → `docs/platforms/02-quantum-ai-applications.md` (`quantum-ai-applications`)
- `docs/quantum/zero-to-mastery-part3-architecture.md` → `docs/platforms/03-quantum-ai-architecture.md` (`quantum-ai-architecture`)
- `docs/quantum/zero-to-mastery-part4-appendices.md` → `docs/platforms/04-quantum-ai-appendices.md` (`quantum-ai-appendices`)

Only the loser (`zero-to-mastery.md`, the 12-week series index/monolith overview) touches this cluster — it is not itself split out to any of parts 2–4, so no cross-plan duplication risk. This plan only disposes of the part1 + overview pair; parts 2–4 keep their own separate merge-plan (or direct-migrate) work, out of scope here. The loser's "Series Parts" table and per-part week links should be treated as the connective tissue across all four target pages — series navigation, not content to duplicate into part 1 beyond a short pointer forward.

## Survivor

Confirmed after reading both files in full: **survivor = `docs/quantum/zero-to-mastery-part1-foundations.md`** (3098 words, `last_reviewed: 2026-07-17`, `doc_type: multi-part-series`, `series_part: 1` of `series_total: 4`). It contains the entire Phase 1 curriculum (Weeks 1–4: quantum mechanics primer, qubits/gates/circuits, algorithms, hardware/error handling) with full code samples, tables, and a capstone. The loser (`zero-to-mastery.md`, 778 words, `doc_type: guide`) is the series' front-matter/index page — a program map, rationale for the series, and a table of contents pointing at all four parts. It has real but non-overlapping content: no week-level teaching material at all. Per doctrine ("never leave two monoliths standing"), the loser does not survive as a separate page; it folds into part 1 as a short intro/overview.

## Unique-Content Map

Content in the loser absent from the survivor, worth preserving as intro material (this is a "keep as short overview," not a "safe to drop" case):

1. **Programme framing / hook** — the "quantum era is not coming, it is here" opening paragraph and the one-line stakes statement (disruption to cryptography, drug discovery, logistics, financial modeling, ML by 2030). Survivor has no equivalent hook.
2. **"Why Quantum Now?" business case** — McKinsey 2026 Quantum Technology Monitor stat (>$10M/yr allocated by a third of large enterprises) and the $1B→$4.4B (2025→2028) revenue trajectory. Not present in survivor at all; strong opening motivation for a Principal-Architect audience.
3. **Classical-limit vs. quantum-opportunity 3-row table** (Optimisation / ML-AI / Security axes) — a compact framing device survivor never states explicitly (survivor dives straight into physics).
4. **The Mermaid programme map diagram** (`flowchart TD`, Phase 1→2→3→Appendices) — see Transform Notes; visualizes how this part fits the whole series. Directly relevant as an orientation aid at the top of part 1.
5. **"How to Use This Guide" navigation guidance** — the instruction that this is one continuous programme (not four unrelated docs) and that unfamiliar terms are very likely defined in an earlier part. Useful signal to carry forward in shortened form.
6. **Series Parts summary table** (what's unique to each of the 4 parts) — condense to a short forward-pointer rather than reproduce in full, since parts 2–4 already exist as their own target pages.
7. **Companion cert-guide pointers** (IBM Associate/Developer Cert Guides) and the cross-reference footer links (AI Foundations, Agentic AI Systems, Cloud Platforms, AI Security & Governance, Enterprise Architecture Patterns) — check each against `migration/mapping.csv` for a live MIGRATE target before carrying forward (see Transform Notes).

Everything else in the loser (weeks-1–4 topic breakdown, phase 2/3 previews) duplicates or is superseded by the survivor's own much deeper content and the sibling part2/part3/part4 target pages, so it is *not* carried forward beyond the short pointer in item 6.

## Target Structure

Outline for `docs/platforms/01-quantum-ai-foundations.md` (survivor's Week 1–4 structure kept intact, loser's unique framing compressed into a new lead-in section):

```
# Quantum AI Foundations

<1-paragraph "why this matters," synthesized from loser items 1–2:
 the quantum-era stakes line + the McKinsey/$1B-$4.4B business case>

## Why Quantum, Why Now
  (loser item 3: classical-limit vs. quantum-opportunity table)
  (Mermaid programme map — loser item 4, adapted: this page = Phase 1 box;
   Phases 2/3 + Appendices link out to the sibling target pages)
  (loser item 5, one or two sentences: read in order, terms build across
   the series)

## Phase 1 — Foundations
  ### Week 1: Quantum Mechanics Primer for Engineers
  ### Week 2: Qubits, Gates & Quantum Circuits
  ### Week 3: Quantum Algorithms — Grover, Shor, Deutsch-Jozsa
  ### Week 4: Quantum Hardware, Error Mitigation & Error Correction

## Continue the Series
  (loser item 6, condensed to a 2-3 line pointer + table linking to
   quantum-ai-applications, quantum-ai-architecture, quantum-ai-appendices)

## Related
## Sources
```

**Word count and recommendation: TRIM, do not split further.** Combined raw word count is ~3876 (3098 + 778). The doc-standards ~2,000-word soft limit is already being satisfied at the *series* level — this cluster is explicitly part 1 of a 4-part split, which is the mechanism the soft limit calls for ("larger topic → split into a series with a hub/index page"). Re-splitting part 1 itself is out of scope for this merge plan and would fragment a curriculum that is designed to be read week-by-week in one sitting.

Recommended trim to land close to the survivor's original ~3100 words (accepting this page runs longer than the general soft limit, consistent with the existing multi-part-series exception):
- Compress the loser's ~430-word "How to Use This Guide" + full Series Parts table down to ~120–150 words (items 5–6 above) — this is the bulk of the loser's contribution.
- Drop the loser's companion cert-guide paragraph unless mapping.csv confirms both cert guides have live MIGRATE targets (see Transform Notes) — if dropped, that's another ~40 words saved.
- Keep the McKinsey stat, the 3-row table, and the Mermaid diagram verbatim — these are the highest-value unique additions and are already compact.
- Net addition to the survivor: roughly 250–350 words, landing the merged page around ~3350–3450 words. Flag for the reviewer that this still exceeds the general 2,000-word guideline; the recommendation is to accept the overage as inherent to a 4-part curriculum series rather than force a fifth split.

## Transform Notes

- **Links needing rewrite:**
  - Survivor's own inbound pointer, "read the [Quantum AI: Zero to Mastery index](./zero-to-mastery.md) first" — this becomes circular once the index is merged in; delete this sentence entirely (the merged page now opens with that framing directly).
  - Survivor's closing "**Next:** continue to [Part 2 — Quantum AI (Weeks 5–8)](./zero-to-mastery-part2-quantum-ai.md)" — rewrite to the new sibling target path (`docs/platforms/02-quantum-ai-applications.md` per mapping.csv row 641).
  - Loser's per-week deep links into `zero-to-mastery-part1-foundations.md#week-1-...` anchors — these become same-page anchors once merged; verify the heading slugs still match after any heading-text edits.
  - Loser's links to parts 2/3/4 (`zero-to-mastery-part2-quantum-ai.md`, `-part3-architecture.md`, `-part4-appendices.md`) — rewrite to `docs/platforms/02-quantum-ai-applications.md`, `03-quantum-ai-architecture.md`, `04-quantum-ai-appendices.md` per mapping.csv rows 641–643.
  - Loser's cross-reference footer links (`../ai-foundations/index.md`, `../agentic-systems/index.md`, `../cloud-platforms/index.md`, `../ai-security-governance/index.md`, `../enterprise-architecture/ai-architecture/enterprise-ai-architecture-patterns.md`) and the two IBM cert-guide links (`./IBM_Associate_Quantum_CertGuide.md`, `./IBM_Developer_Quantum_CertGuide.md`) — none of these old paths are confirmed live in this plan; check each against `migration/mapping.csv` before carrying forward, and drop any without a MIGRATE row rather than link to a retired page.

- **Mermaid diagram:** the loser's "Programme Map" diagram (`flowchart TD` with `subgraph`s `P1`/`P2`/`P3` and an `APP` node) is already valid Mermaid syntax, not ASCII art — confirmed by direct inspection of the source. No diagram-standards conversion pass is needed. Placement: carry it into the new "Why Quantum, Why Now" section near the top of the merged page (per Target Structure above), immediately after the classical-vs-quantum table, so it orients the reader before Week 1 begins. No edits needed to the diagram body itself beyond confirming its internal links still resolve once parts 2–4 land at their new `docs/platforms/0N-*.md` paths (the diagram itself has no embedded hyperlinks, only labels, so no change is actually required there).

## Doc Type & Template

**doc_type: guide** (not `concept` or `learning-path` as initially suspected from the "Zero to Mastery" framing).

Rationale: `concept` carries a hard ≤1,200-word cap (per `governance/DOC_TYPES.md`) that this page — even after trimming — cannot meet; the page is fundamentally procedural (four weeks of "you'll be able to," hands-on schedule, code-along exercises, capstone deliverable), which matches `guide`'s definition ("How to do X" — prereqs + steps + verification) far better than `concept`'s "explain one idea." `learning-path` was also considered ("Ordered links + outcomes per stage") but its own definition describes a page that is itself mostly *links out* to per-stage content elsewhere — that describes the loser (the series index) far better than the survivor, which carries the actual substantive teaching content inline rather than linking out to it. Once merged, the page's dominant character is hands-on instructional content with weekly outcomes and a capstone verification step, so `guide` is the better fit.

Template: no dedicated `guide` (or `learning-path`) template file currently exists under `.claude/skills/doc-standards/templates/` — only `concept.md`, `decision-adr.md`, and `reference-architecture.md` are present. Recommend following the general page anatomy from the doc-standards `SKILL.md` (why-this-matters → body → Related → Sources) plus the `guide` special requirement from `DOC_TYPES.md` (prereqs + steps + verification — satisfied by the existing "You'll be able to..." objectives per week and the Phase 1 Capstone). Flag for whoever owns `.claude/skills/doc-standards/templates/` that a `guide.md` template gap exists; out of scope for this merge plan to create it.
