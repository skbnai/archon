# Merge Plan: hub-assets

## Cluster

| old_path | words | last_reviewed | source_type | disposition |
|---|---|---|---|---|
| docs/ai-usecases/index.md | 379 | 2026-07-10 | native-md | MERGE-INTO hub-assets |
| docs/ea-masterclass/deliverables/index.md | 1613 | 2026-07-10 | native-md | MERGE-INTO hub-assets |
| docs/ea-masterclass/module-13-case-studies/index.md | 2496 | 2026-07-10 | native-md | MERGE-INTO hub-assets |
| docs/ea-masterclass/transcripts/index.md | 1826 | 2026-07-10 | native-md | MERGE-INTO hub-assets |

- target canonical path: `docs/assets/index.md`
- domain: assets
- wave: 8

## Survivor

Survivor is the existing fresh hub stub at `docs/assets/index.md` (read in full — 34 lines, frontmatter `doc_type: hub`, `topic_id: hub-assets`, `status: draft`, intro paragraph framing this as "the library for that: templates, checklists, workshop kits, and the unified glossary referenced across every other domain," Scope bullets: Downloadable templates / Checklists / Workshop kits / Transcripts / Case studies / Unified glossary; a Related section linking to Learning Paths Hub and Career Hub).

None of the four old files above is the survivor. Per doc-standards, `doc_type: hub` is a curated navigation page, not a content page — links only, curated, not auto. A hub is authored fresh from the current canonical set of TRACK'd/MIGRATE'd children and is deliberately not a merge/concatenation of old prose. All four old files are nested section/subfolder indexes whose individual link targets (templates, case studies, transcripts, industry playbooks) already have their own MIGRATE/TRACK rows into `docs/assets/*` and `docs/trust/*` under separate topic_ids — the "one hub per domain" rule folds the index itself in as curated links, discarding the old duplicate navigation scaffolding.

## Unique-Content Map

**docs/ai-usecases/index.md** (379 words)
- Pure link index: Markdown guides, PDFs (EU Bank AI Copilot, APEX combined case studies), a DOCX link, a JSX source-code link ("Airgapped Banking Architecture"), 10 industry-sector playbooks, 15 agentic AI case studies, CEO Agent resources, one reference case study, and a pointer to Soft Skills.
- Every link target is already individually TRACK'd/MIGRATE'd/MERGE-INTO'd elsewhere in mapping.csv (lines 213-253): industry playbooks → `docs/assets/22-31`; agentic case studies → `docs/assets/34-48`; CEO Agent resources → `docs/assets/32-33,51`; EU Bank Copilot cluster (parts 1-4 + duplicate drafts) → `docs/assets/01-04` (eu-bank-copilot-* topic_ids, out of scope here per the task — handled by other agents); `airgapped-banking-architecture.md` → `docs/trust/01-airgapped-banking-infrastructure.md` (wave 7, MIGRATE, reclassified as sovereign-AI/trust content, not a case study).
- No unique framing beyond "real-world AI architecture case studies spanning industry sectors, enterprise agentic deployments, and strategic frameworks" — already subsumed by the hub's existing Scope bullet "Case studies."
- No unique content — safe to drop.

**docs/ea-masterclass/deliverables/index.md** (1613 words)
- Structured as 3 groups (Business Case Templates 1-6, Governance Templates 7-10, Consulting Templates 11-20) with a one-paragraph descriptive blurb per template (20 blurbs total) plus an "info" callout on how to use templates as starting points, not fill-in-the-blank forms.
- Verified by reading the actual target files: `business-case-templates.md` (5,482 words), `governance-templates.md` (5,938 words), `consulting-templates.md` (7,271 words) each already contain the full per-template content (e.g. Template 1's complete chapter structure) — the index's blurbs are short summaries of content that survives intact in the three already-TRACK'd target files (`docs/assets/19-21`, topic_ids template-business-case / template-governance-and-decision / template-consulting-and-practice).
- No unique framing beyond "20 templates, copy-paste ready, organized by business-case/governance/consulting" — already subsumed by the hub's existing Scope bullet "Downloadable templates."
- No unique content — safe to drop.

**docs/ea-masterclass/module-13-case-studies/index.md** (2496 words) — checked carefully per instructions
- Grepped mapping.csv for `ea-masterclass/module-13` (lines 417-424): all 6 individual case studies (global-bank, healthcare, retail, telecom, government, energy-utilities) are separately TRACK'd into `docs/assets/08-14` — their full narrative content is preserved and NOT at risk.
- However, the index page itself carries real synthesis content that is NOT reproduced in any of the 6 individual case files and is NOT covered by any other mapping.csv row:
  - "Active Reading Method" + "Study Group Facilitation" — a pedagogical framework for how to use the case studies (pre-read hypothesis, annotation-focused re-read, cohort facilitation format).
  - "The Six Industries at a Glance" — six short scenario abstracts, one per case, distinct from (shorter than) the full case files but not literally duplicated text.
  - "Industry Comparison Table" — a 6-row table cross-comparing investment, payback period, and key outcome across all six cases side by side. This comparative view does not exist inside any single case file.
  - "The 12-Step Engagement Pattern" — a named methodology (Org Background → Business Problem → ... → Key Takeaways) with a 12-box **ASCII diagram** (lines 89-103 of the source file) plus a paragraph explaining each of the 12 steps. **Flagging a metadata discrepancy: cluster data states `ascii_art False` for this file, but the file as read does contain an ASCII flow diagram** — relevant for diagram-standards conversion if this content is ever migrated.
  - "Case Study Navigation" table and "Recommended Reading Sequence" / "Cross-Module Connections" callouts (which case to read first/last and why; how the case patterns connect to other EA Masterclass modules).
- Verdict: this is not a pure index — it is a standalone pedagogical/methodology page layered on top of the 6 case studies. None of this synthesis content is captured by the hub's Scope bullet "Case studies" (which only implies a link list) nor by any of the 6 individually-tracked case files. **This content would be lost if the index is only folded into hub-assets as curated links.**

**docs/ea-masterclass/transcripts/index.md** (1826 words) — checked carefully per instructions
- Grepped mapping.csv for `ea-masterclass/transcripts` (lines 431-435): all 4 individual transcripts (bank-discovery-workshop, healthcare-executive-presentation, manufacturing-arb-review, retail-proposal-negotiation) are separately TRACK'd into `docs/assets/15-18` — their full transcript content is preserved and NOT at risk.
- As with module-13, the index carries real synthesis content not reproduced elsewhere and not covered by any other mapping.csv row:
  - "What These Transcripts Are" / "How to Use These Transcripts" (self-study, workshop facilitation, mentoring, pre-engagement prep modes) / "How to Read Annotations" — a methodology for using the transcripts as a training instrument, not present in the transcripts themselves.
  - Four per-scenario summaries (situation / why it matters / political-or-financial-or-decision dimension / primary skill demonstrated) — framing content distinct from the verbatim transcripts.
  - "Patterns to Watch Across All Four Transcripts" — 5 named cross-cutting patterns (practitioner speaks less than expected; bad news delivered early; concession as trust instrument; political conflict acknowledged not arbitrated; decisions shaped not imposed) synthesized across all four scenarios. This is genuine comparative analysis that cannot be reconstructed from any single transcript file.
  - "Navigation Table" cross-referencing setting/practitioner/stakeholders/primary-skill per transcript.
- Verdict: same conclusion as module-13 — this is a standalone pedagogical/synthesis page, not a pure link index. This content would be lost if the index is only folded into hub-assets as curated links.

## Target Structure

Base hub stays a short curated hub — links only, no merged prose — for the `ai-usecases` and `deliverables` losers, which are safe to fold as-is:

```
# Asset Library Hub  (title, frontmatter unchanged)

<intro paragraph — unchanged>

## Scope
- Downloadable templates
- Checklists
- Workshop kits
- Transcripts
- Case studies
- Unified glossary

## Related
- Learning Paths Hub
- Career Hub
```

No structural change to the hub itself is required by `ai-usecases/index.md` or `deliverables/index.md` — both are fully covered by existing Scope bullets and their link targets are already reachable via the individually-tracked destination pages under `docs/assets/*` (and `docs/trust/*` for the one reclassified file).

**NEEDS LIBRARIAN REGISTRATION**: the synthesis content identified above in `module-13-case-studies/index.md` and `transcripts/index.md` has no home in the current mapping. It should not be invented as a topic_id here — flagging for the librarian to register two new spoke pages once the six case-study and four transcript TRACK targets have landed:
- a case-studies collection/methodology page (candidate scope: "Active Reading Method," "12-Step Engagement Pattern" incl. the ASCII diagram converted to Mermaid, "Industry Comparison Table," reading-sequence guidance) — likely doc_type `guide` or `collection-overview`, sibling to `docs/assets/08-14`.
- a transcripts collection/methodology page (candidate scope: "How to Use These Transcripts," per-scenario framing, "Patterns to Watch Across All Four Transcripts," navigation table) — likely doc_type `guide` or `collection-overview`, sibling to `docs/assets/15-18`.
Until those are registered, the hub's Scope bullets "Case studies" and "Transcripts" should link to whichever of the two new pages or the raw TRACK'd files exist at the time; no change to the hub outline above is needed in the meantime.

## Transform Notes

- ASCII art: none in `ai-usecases/index.md` or `deliverables/index.md`. **One ASCII flow diagram found in `module-13-case-studies/index.md`** (the 12-Step Engagement Pattern box diagram, source lines 89-103) — contradicts the cluster metadata's `ascii_art False` flag. If/when the flagged spoke page above is created, this diagram should be converted to a Mermaid flowchart per diagram-standards. No ASCII art found in `transcripts/index.md`.
- Cross-repo/absolute links needing rewrite if any prose or links from these files were ever reused:
  - `ai-usecases/index.md` uses old-repo absolute paths (`/knowledge-docs/ai-usecases/...`) for PDFs, DOCX, and the JSX source file — these do not resolve in the new repo and are not carried onto the hub (curated bullets only).
  - The JSX link ("Airgapped Banking Architecture") points at a `.jsx` file that does not exist in the old-repo clone (only a `.md` of the same base name does); the actual content is the already-migrated `docs/ai-usecases/airgapped-banking-architecture.md` → `docs/trust/01-airgapped-banking-infrastructure.md`. Stale/broken link, not carried forward.
  - `deliverables/index.md` uses relative sibling links (`business-case-templates.md`, `governance-templates.md`, `consulting-templates.md`) — these resolve to the already-TRACK'd target pages under `docs/assets/19-21`; no rewrite needed since only curated bullets are carried onto the hub.
  - `module-13-case-studies/index.md` and `transcripts/index.md` use relative sibling links to the six case files / four transcript files — same pattern, resolves to `docs/assets/08-14` and `docs/assets/15-18` respectively.
- Reminder per task scope: this hub cluster excludes the `eu-bank-copilot-*` content clusters referenced from `ai-usecases/index.md` (PDF/DOCX/monolith/parts) — those are handled by other agents and are not re-planned here.

## Doc Type & Template

doc_type: hub — no template — short curated hub page per governance/DOC_TYPES.md.

If the librarian registers the two flagged spoke pages, their likely doc_type is `guide` (or `collection-overview` if that type exists in governance/DOC_TYPES.md) — not `hub`, since each would carry real methodology/synthesis prose rather than curated links.
