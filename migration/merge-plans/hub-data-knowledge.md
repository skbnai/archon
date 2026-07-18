# Merge Plan: hub-data-knowledge

## Cluster

| old_path | title | words | last_reviewed | source_type |
| --- | --- | --- | --- | --- |
| docs/knowledge-engineering/data/index.md | Data Architecture | 88 | 2026-07-10 | native-md |
| docs/knowledge-engineering/index.md | Knowledge Engineering | 112 | 2026-07-10 | native-md |
| docs/knowledge-engineering/industry-practices/index.md | Industry Knowledge Systems | 530 | 2026-07-10 | native-md |
| docs/knowledge-engineering/knowledge/index.md | Knowledge Engineering | 42 | 2026-07-10 | native-md |

- target canonical path: `docs/data-knowledge/index.md`
- domain: data-knowledge
- wave: 5
- disposition (all four): MERGE-INTO hub-data-knowledge — "Nested section/subfolder index; one hub per domain rule — folds into hub-data-knowledge." (per migration/mapping.csv lines 597, 598, 604, 609)

Confirmed via mapping.csv: all deep content under this old subtree (the PDF/DOCX reports themselves) has separate MIGRATE rows with the `docs/data-knowledge/NN-*.md` target prefix — lines 594–596 (data reports), 599–603 & 605 (industry-practices reports), 606–608 (knowledge/ reports). Only the four *index* pages above are MERGE-INTO/losers in this plan.

## Survivor

Survivor = the existing fresh hub stub at `docs/data-knowledge/index.md` (read in full — frontmatter `doc_type: hub`, `topic_id: hub-data-knowledge`, `last_reviewed: 2026-07-18`, with a Scope list and a Related list).

Hub clusters have no old-file survivor because `doc_type: hub` is defined in governance/DOC_TYPES.md as "Links only canonical pages; curated, not auto" — a hub is a short, hand-curated table of contents for a domain, not a merge of prose from multiple source documents. None of the four old index pages qualifies as a hub in the new sense: each is a mechanically-generated section/subfolder index (one per directory level) whose job was pure navigation within the old repo's nesting, not curation across a domain. Carrying any of their prose forward as the "survivor" would reintroduce the auto-generated, uncurated pattern the hub doc_type exists to avoid. The new stub was authored fresh and already lists the domain's real scope (data architecture/engineering, RAG hub, knowledge graphs/GraphRAG, memory, lineage, lakehouse) — broader and better organized than any single old index.

## Unique-Content Map

**docs/knowledge-engineering/data/index.md** (Data Architecture, 88 words)
- Scope line ("data systems, lineage, governance, AI-native data platform evolution") — already covered by hub stub's "Data architecture and engineering for AI" and "Data lineage" bullets.
- Cross-links in the "See also" callout: to `../industry-practices/governance-rai.md` (in-cluster, target now `docs/data-knowledge/09-governance-rai.md`), to `../../enterprise-architecture/transformation/index.md` (cross-repo — that old hub is itself MERGE-INTO hub-strategy → `docs/strategy/index.md`), and to `../../enterprise-architecture/specialization/index.md` (cross-repo — MERGE-INTO hub-architecture → `docs/architecture/index.md`). These three cross-domain relationships (data-knowledge ↔ strategy, data-knowledge ↔ architecture) are not represented in the current stub's "Related" section (which only lists agentic-systems and platforms) — worth a mention but not required, since Related links target hubs, not old files.
- No other content. Report links (3 PDFs) — all separately MIGRATE'd, not unique here.

**docs/knowledge-engineering/index.md** (Knowledge Engineering, 112 words)
- Framing line: "How enterprises turn raw data into governed, grounded, evaluated knowledge that AI systems can safely serve." — a good one-line mission statement not currently on the stub; stub's intro paragraph covers similar ground ("Agent quality is bounded by what an agent can retrieve...") so this is redundant framing, not new information.
- The three "Sections" descriptions (Data Architecture / Knowledge & RAG / Industry Knowledge Systems) are internal-cluster navigation only — all three targets are other MERGE-INTO members of this same cluster, so nothing new to preserve; their underlying content already surfaces via the stub's Scope bullets.
- No unique content beyond internal cluster navigation — safe to drop.

**docs/knowledge-engineering/industry-practices/index.md** (Industry Knowledge Systems, 530 words) — largest file, has real unique framing:
- "Why this matters now" — 3-force argument (production failures traced to data governance not models; EU AI Act GPAI enforcement Aug 2026 + ISO 42001 + NIST AI RMF; evaluation-as-CI-discipline via RAGAS/DeepEval/TruLens). This is genuine analytical framing not present anywhere on the stub — the stub's Scope bullets name topics (RAG, knowledge graphs, memory, lineage) but carry none of this governance/regulatory rationale.
- ASCII-art four-layer architecture diagram (Evaluation & Monitoring / Grounded Serving / Governance-Context Layer / Knowledge & Data Foundation) — unique conceptual model, currently only as box-drawing characters. Candidate for a curated link callout or a future Mermaid diagram on a governance/RAG page — not something the hub itself should render (hub = links only), so this is a candidate for the child pages, not the hub.
- Table of 5 sub-pages (tech-companies.md, consulting-firms.md, governance-rai.md, grounding.md, evaluation.md) — all separately MIGRATE'd (lines 599–603); their one-line summaries are useful blurbs the migrator should carry into those individual pages' frontmatter/intros, but not hub content.
- "Related sections" links to data/index.md and knowledge/index.md — pure in-cluster navigation, redundant with Scope bullets.
- Net: the "why this matters now" framing and the four-layer model are the only content genuinely at risk of being lost; both belong in the migrated child content (e.g., a grounding/governance overview page), not the short hub — noted here so the migrator doesn't drop them entirely.

**docs/knowledge-engineering/knowledge/index.md** (Knowledge Engineering, 42 words)
- Scope line: "Research and architecture guides for autonomous knowledge systems, RAG, enterprise knowledge graphs, and AI-native knowledge management." — already covered by stub's "RAG hub" and "Knowledge graphs and GraphRAG" bullets.
- Lists 3 reports (AKES, Enterprise Knowledge Architectures Report, Complex RAG Deep Dive) — all separately MIGRATE'd (lines 606–608).
- No unique content — safe to drop.

**Duplicate-title check — docs/knowledge-engineering/index.md vs docs/knowledge-engineering/knowledge/index.md:**
These are NOT duplicates of each other despite the identical title. `docs/knowledge-engineering/index.md` is the top-level parent hub for the whole `knowledge-engineering/` subtree, describing and linking to all three child sections (data, knowledge, industry-practices) at a summary level. `docs/knowledge-engineering/knowledge/index.md` is one specific leaf subsection — a short, PDF-only listing scoped narrowly to autonomous knowledge engineering / RAG / knowledge-graph reports. Different scope, different altitude (parent vs. leaf); the shared title is a naming collision from the old repo's folder-mirrors-title convention, not redundant content. Both are still correctly disposed as MERGE-INTO with no unique content worth preserving beyond what's noted above.

## Target Structure

Final H2/H3 outline of `docs/data-knowledge/index.md` (unchanged from current stub — no new sections needed; all reviewed old content is either already represented in Scope/Related or belongs on migrated child pages, not the hub):

```
# Data & Knowledge Hub
(intro paragraph — unchanged)

## Scope
- Data architecture and engineering for AI
- Retrieval-Augmented Generation (RAG) hub
- Knowledge graphs and GraphRAG
- Semantic and long-term memory
- Data lineage
- Lakehouse architecture

## Related
- Agentic Systems Hub
- Platforms Hub
```

Comparison to current stub: no structural change proposed. This plan confirms the stub already covers everything salvageable from the four old index pages at the hub altitude. (Optional, non-blocking: the "Related" list could later gain Strategy Hub / Architecture Hub cross-links to mirror the old `data/index.md` "See also" callout, but that is a content decision for whoever owns the stub, not a merge-plan requirement.)

## Transform Notes

- **diagram-standards**: `docs/knowledge-engineering/industry-practices/index.md` (ascii_art_suspected=True, confirmed) contains a 4-row ASCII box diagram (Evaluation & Monitoring → Grounded Serving → Governance/Context Layer → Knowledge & Data Foundation) using box-drawing characters. Per the diagram-standards skill this should be converted to a Mermaid diagram if/when this content is carried into a migrated child page (e.g. a grounding or governance overview) — it must NOT be reproduced on the hub itself, since hub pages are links-only. None of the other three members are flagged for ascii_art.
- **Cross-repo link rewrites** (relevant only if a future non-hub page carries this content forward; not applicable to the hub itself, which has no such links):
  - `docs/knowledge-engineering/data/index.md` → `../industry-practices/governance-rai.md` rewrites to `docs/data-knowledge/09-governance-rai.md` (in-cluster MIGRATE target).
  - same file → `../../enterprise-architecture/transformation/index.md` rewrites to `docs/strategy/index.md` (that old hub is itself MERGE-INTO hub-strategy).
  - same file → `../../enterprise-architecture/specialization/index.md` rewrites to `docs/architecture/index.md` (MERGE-INTO hub-architecture).
- All four old index pages' internal "Sections"/"Related sections" cross-links point only to other members of this same cluster or to other MERGE-INTO hub targets — none require preservation on the hub page itself.

## Doc Type & Template

doc_type: hub — no template — short curated hub page per governance/DOC_TYPES.md.
