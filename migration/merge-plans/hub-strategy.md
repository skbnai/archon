# Merge Plan: hub-strategy

## Cluster

| old_path | words | last_reviewed | source_type | disposition |
|---|---|---|---|---|
| docs/ai-economics/index.md | 308 | 2026-07-10 | native-md | MERGE-INTO |
| docs/enterprise-ai-report/index.md | 2009 | 2026-07-14 | native-md | MERGE-INTO |
| docs/enterprise-architecture/strategy/index.md | 62 | 2026-07-10 | native-md | MERGE-INTO |
| docs/enterprise-architecture/transformation/index.md | 606 | 2026-07-10 | native-md | MERGE-INTO |
| docs/enterprise-strategy/index.md | 525 | 2026-07-15 | native-md | MERGE-INTO (ascii_art_suspected=True) |

- target canonical path: `docs/strategy/index.md`
- domain: strategy
- wave: 1

## Survivor

Survivor = the existing fresh hub stub at `docs/strategy/index.md`, already read in full (17 lines of prose + Scope + Related, frontmatter `doc_type: hub`, `topic_id: hub-strategy`, `canonical: true`). No old file is the survivor.

Hub clusters have no old-file survivor because `doc_type: hub` is governed as "links only, curated, not auto" (governance/DOC_TYPES.md row: `hub | Domain/topic index | 90d | Links only canonical pages; curated, not auto`). A hub is not a content page to merge prose into — it is a hand-curated table of contents for the domain. All five old index.md files below are themselves the same doc_type (nested section indexes), and per the one-hub-per-domain rule they cannot survive as parallel hubs; their only legitimate afterlife is (a) a curated link on the new hub, and (b) their real content already re-homed via individual MIGRATE rows to `docs/strategy/NN-*.md` pages (confirmed by grep of mapping.csv, see below).

## Unique-Content Map

**docs/ai-economics/index.md** — Scope stub already covers "Economics & market landscape." Unique framing not on stub: this was a cross-repo router pointing into `enterprise-architecture/ai-architecture/AI-FinOps-*` guides (FinOps series) plus its own `ai-economics/*` guides (tokenomics, commercial analysis, coding-agent cost, value-creators synthesis) and two PDF/XLSX assets (Cloud Cost Comparison spreadsheet, AI Cost Implementation Guide, Value Creator Deliverables Pack). All deep guides have MIGRATE rows into `docs/strategy/03–10-*.md`. Unique link worth curating: the FinOps series lives under a *different* domain folder (`enterprise-architecture/ai-architecture`) — worth one curated cross-link from the new hub since FinOps cost detail is economics-adjacent but architecturally homed elsewhere.

**docs/enterprise-ai-report/index.md** — Scope stub covers strategy/economics/OKRs broadly but not the "21-part research report" framing or the specific role-based navigation table (CIO/CTO, EA, Security, Platform, Delivery, Consulting, HR). Unique facts: this was the master routing table for the whole enterprise-AI knowledge base (governance, security, observability, DevSecOps, transformation, case studies, deliverables) — spanning far outside the strategy domain into security-governance, ai-development, agentic-systems, cybersec-architect, etc. That breadth is NOT hub-strategy's job going forward (one hub per domain); only the strategy-relevant parts (operating model, transformation roadmap, financial model, org roles) map into strategy MIGRATE targets (`docs/strategy/11–31-*.md`). No unique *scope* language for the stub beyond what's already there; nothing to curate as a link since this was an omnibus router, not a single source, and its outbound links belong to other domain hubs (security, platform, etc.), not strategy.

**docs/enterprise-architecture/strategy/index.md** — Fully redundant — no unique content — safe to drop. Its 5 PDF links (CTO Blueprint, Strategic Brief, EA Strategy Playbook, AI Cost Implementation Guide, Transformation Transcript) are all already covered by MIGRATE (`docs/strategy/32–34-*.md`) or TRACK (transcript → `docs/assets/56-*.md`) rows; nothing here is unrepresented in the stub's "AI strategy and business architecture" scope bullet.

**docs/enterprise-architecture/transformation/index.md** — Scope stub covers "Transformation playbooks" already. Unique framing worth preserving as a curated link: the "7-volume AI-First Enterprise series" (Vol 00–06) and the 6-level AI Maturity Model (Exploring → AI-Native) — this is a well-known, citable framework name distinct from generic "transformation playbooks" language. Consider one curated link to the lead volume (`docs/strategy/35-executive-summary-and-ai-vision.md`, per MIGRATE row) if the hub wants a single entry point into the maturity model, since it's a recognizable artifact readers may search for by name.

**docs/enterprise-strategy/index.md** — Scope stub covers "operating models," "value framework." Unique framing: the "5-volume Enterprise Strategy & Business Architecture Handbook" (Vol 1 Corporate Strategy, Vol 2 Business Architecture/TOM, Vol 3 Portfolio/Governance, Vol 4 Consulting Frameworks, Vol 5 AI Strategy/Glossary) plus a consulting-framework-to-outcome cross-reference (McKinsey 7S, Porter's Value Chain, BCG Growth-Share, Balanced Scorecard, TOGAF ADM, BIZBOK, SAFe, OKR, Wardley Mapping, Business Model Canvas). This mapping table is a distinctive piece of framing not implied by the stub's bullets. All 5 volumes have MIGRATE rows (`docs/strategy/43,45-52-*.md` — note vol10 exists in mapping but not in this index's TOC, minor pre-existing gap in the old repo, not this plan's concern). Contains an ASCII-art concept-hierarchy diagram and a second ASCII arrow-mapping diagram (see Transform Notes).

## Target Structure

Current stub (keep, essentially as-is — it is already short and curated):

```
# Strategy Hub  (frontmatter: doc_type hub, topic_id hub-strategy, canonical true)

<1-paragraph framing prose>

## Scope
- AI strategy and business architecture
- Operating models for AI-enabled organizations
- Transformation playbooks
- Economics & market landscape
- Value measurement and OKRs

## Related
- [Architecture Hub](../architecture/index.md)
- [Operations Hub](../operations/index.md)
```

Proposed final outline (adds one optional section, no prose merge):

```
# Strategy Hub

<existing framing paragraph — unchanged>

## Scope
<existing 5 bullets — unchanged, already domain-complete>

## Key Frameworks
(NEW, optional — curated pointer links only, 3-5 bullets max)
- AI-First Enterprise maturity model → docs/strategy/35-executive-summary-and-ai-vision.md
- Enterprise Strategy & Business Architecture Handbook (Vol 1-5) → docs/strategy/43-vol1-corporate-strategy.md
- Enterprise AI Research Report (operating model/transformation parts) → docs/strategy/11-part-01-evolution.md
- AI Cost & Economics guide series → docs/strategy/03-ai-value-creator-deliverables-pack.md

## Related
<existing 2 bullets, plus optionally:>
- FinOps cost-management detail lives under Architecture Hub → ../enterprise-architecture/ai-architecture (cross-domain note)
```

"Key Frameworks" is optional curatorial sugar, not required — the existing Scope+Related shape already satisfies doc_type=hub. If the hub owner prefers to stay minimal, Scope/Related alone is sufficient and all five old indexes can simply be dropped with no page edit at all.

## Transform Notes

- **diagram-standards**: `docs/enterprise-strategy/index.md` is flagged `ascii_art_suspected=True` and confirmed on read — contains two ASCII diagrams: (1) a "Concept Hierarchy at a Glance" box-drawing tree (Strategy/Architecture/Operating Model/Portfolio/AI Transformation layers), and (2) a "Relationship to Consulting Frameworks" ASCII arrow-mapping (McKinsey 7S → Operating Model Design, etc.). Neither diagram is going into the hub page (hub is links-only), but whichever MIGRATE target absorbs `enterprise-strategy/index.md`'s conceptual content (likely `docs/strategy/43-vol1-corporate-strategy.md` or a dedicated landing section) should convert both to Mermaid per the diagram-standards skill — flagging here for the stage-04 migrator, not resolving in this plan.
- No other member has `ascii_art_suspected=True`.
- **Cross-repo links needing rewrite**: all five old indexes use relative links into sibling old-repo folders (e.g. `../enterprise-architecture/ai-architecture/AI-FinOps-Cost-Management-Guide.md`, `../ai-development/aidlc/...`, `../ai-security-governance/...`) and root-relative PDF asset links (`/knowledge-docs/ai-economics/...`). None of these old-repo relative paths are valid in the new repo; every curated link added to the new hub must point at the *new* `docs/strategy/NN-*.md` (or other domain) canonical paths per mapping.csv, not at the old relative paths. This plan's Target Structure section above already uses new-repo target paths for that reason.
- `docs/ai-economics/index.md` also linked to two PDFs and one XLSX asset via `pathname://` and `/knowledge-docs/...` — these are asset-track concerns (see TRACK dispositions elsewhere in mapping.csv for similar assets), not hub content; no hub link needed for raw asset downloads.

## Doc Type & Template

doc_type: hub — no template — short curated hub page per governance/DOC_TYPES.md.
