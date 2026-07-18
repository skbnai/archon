# Merge Plan: hub-architecture

## Cluster

| old_path | words | last_reviewed | source_type |
|---|---|---|---|
| docs/ai-development/aidlc/index.md | 250 | 2026-07-16 | native-md |
| docs/ai-development/index.md | 17 | 2026-07-10 | native-md |
| docs/ai-foundations/index.md | 461 | 2026-07-10 | native-md (ascii_art_suspected: True) |
| docs/enterprise-architecture/ai-architecture/index.md | 1297 | 2026-07-10 | native-md |
| docs/enterprise-architecture/architectural-review-board/index.md | 1507 | 2026-07-10 | native-md |
| docs/enterprise-architecture/best-practices/index.md | 37 | 2026-07-10 | native-md |
| docs/enterprise-architecture/index.md | 206 | 2026-07-10 | native-md |
| docs/enterprise-architecture/process/index.md | 94 | 2026-07-10 | native-md |
| docs/enterprise-architecture/specialization/index.md | 133 | 2026-07-10 | native-md |

Target canonical path: `docs/architecture/index.md`
Domain: architecture
Wave: 2

All nine are section/subfolder indexes from four old top-level trees
(`ai-development/`, `ai-foundations/`, `enterprise-architecture/` and its five
subfolders). Per mapping.csv every row above is `MERGE-INTO` →
`hub-architecture` with rationale "Nested section/subfolder index; one hub
per domain rule — folds into hub-architecture." None are `MIGRATE`.

## Survivor

Survivor = the existing fresh hub stub at `docs/architecture/index.md`
(read in full: frontmatter `doc_type: hub`, `topic_id: hub-architecture`,
`canonical: true`, `last_reviewed: 2026-07-18`; body has a one-paragraph
intro, a `## Scope` bullet list of 7 items, and a `## Related` list of 3
links). This stub is the survivor, not any old file.

Hub clusters have no old-file survivor because `doc_type: hub` is defined
(governance/DOC_TYPES.md, reinforced by docs/architecture/00-wiki-governance.md
§4) as a **curated, hand-authored links page**, not an auto-generated or
merged-prose document. A hub's job is to give an architect a map of the
domain and hand them off to canonical pages elsewhere; it is explicitly not
supposed to absorb body content from the pages it replaces. All nine old
section indexes here were themselves just link lists (17–1507 words, mostly
tables of "Read: X" links to their own subpages) — exactly the kind of
content a hub supersedes by curation, not merger. So the fresh stub already
authored in this repo stays as-is in structure; the old files contribute at
most new *links* to the Scope/Related sections, never prose.

Note: `docs/architecture/00-wiki-governance.md` (topic_id: `wiki-governance`,
doc_type: `guide`) is a separate, already-registered page in this same
domain — it documents the registry/hooks/CI machinery, not the architecture
subject matter. It is one of the `## Related` links from the hub stub, not
a member of this cluster and not touched by this plan.

## Unique-Content Map

**docs/ai-development/aidlc/index.md** — Nested one level under the
ai-development index; its 5-row "Contents" table just enumerates AIDLC
documents that all have their own MIGRATE rows into docs/architecture/
(01, 02, 03, 04, 13, 14, 15, 16 per mapping.csv). No unique scope beyond
"AIDLC framework" which the hub stub's Scope bullet "Domain-driven design
for agentic systems" / general architecture framing already implies loosely.
Unique link worth curating: none new — all targets already have canonical
homes. No unique content — safe to drop.

**docs/ai-development/index.md** — 17-word stub: "AIDLC, testing frameworks,
evaluation methodologies, and quality assurance for agentic systems." The
testing/evaluation half of this is already out of scope for hub-architecture
(mapping.csv routes `ai-development/testing/*` to `hub-operations` /
`docs/operations/`, wave 8). No unique content — safe to drop.

**docs/ai-foundations/index.md** (ascii_art_suspected: True) — Has real
unique framing not yet on the stub: the "Agentic AI Primer" (agent
definition, 5-step Agent Loop), a "Four Building Blocks" table (LLM
backbone/Tools/Memory/Orchestration), and a "Memory Taxonomy" table
(in-context/episodic/semantic/procedural). These are foundational-concepts
framing the hub's Scope bullets don't explicitly name. Recommend adding a
Scope bullet like "Agentic AI foundations (agent loop, memory taxonomy)" —
the deep content itself already has a MIGRATE row (ai-foundations/index.md's
sibling files land at docs/architecture/17-35-*.md). Contains one ASCII Agent
Loop box-diagram and one ASCII tool-call sequence diagram — see Transform
Notes.

**docs/enterprise-architecture/ai-architecture/index.md** — 1297-word link
hub with ~13 sub-topic sections (foundations, patterns, governance/
compliance, skills assessment, security/identity, interoperability, ML-EA,
guardrails, reliability, harness, MCP/A2A, memory/planning, comms/gateway,
reference architectures) plus a "Key Resources in Other Sections" table and
a "Model Landscape" pricing table. The sub-topic breadth (security,
guardrails, reliability, harness, protocols, memory) is materially wider
than the current hub Scope bullets, which only say "Reference architecture
catalog / Pattern and anti-pattern catalogs / ADR library / DDD / Integration
patterns / ARB process" — no explicit mention of security, guardrails,
reliability/observability, or the agent harness. Recommend folding these as
new Scope bullets. The pricing/model-landscape table is stale operational
data, not hub scope — drop.

**docs/enterprise-architecture/architectural-review-board/index.md** — Deep
ARB content (functions, operating model, ADR template, review criteria,
economic framework, standards library, exceptions) all covered by the
existing "ARB process" Scope bullet — no new scope, just confirms the hub
should keep an explicit ARB link (stub's Related list doesn't currently
link ARB directly; consider adding one alongside the reference-architecture
link once the ARB volumes land at docs/architecture/60-67-*.md).
No unique scope beyond what's already named — safe to drop prose, keep ARB
as a named catalog item already covered.

**docs/enterprise-architecture/best-practices/index.md** — 37-word stub,
just a pointer to two PDFs (jargon, glossary). No unique scope. No unique
content — safe to drop.

**docs/enterprise-architecture/index.md** — Top EA section index; "Sections"
list (Strategy, Frameworks, Processes, Best Practices, ARB, Specialization)
and a Quick Reference table. Two entries route outside this domain per
mapping.csv (`strategy/` → docs/strategy/, several `specialization/*` →
docs/architecture but data-architecture sub-link → knowledge-engineering) —
not this hub's concern once those pages exist independently. The
"Frameworks" (TOGAF 10 APEX) angle isn't explicitly named in the current
Scope bullets; consider adding "Enterprise architecture frameworks (TOGAF)"
as a bullet. Otherwise no unique content beyond what's already implied.

**docs/enterprise-architecture/process/index.md** — 94-word pointer to
EA lifecycle/mastery/playbook PDFs, already covered by hub's implicit
"landing zones"/process framing; no new scope concept. No unique content —
safe to drop.

**docs/enterprise-architecture/specialization/index.md** — Points to data
architecture, principal-architect, and consultant-toolkit PDFs; the "Data
Architecture" sub-link explicitly routes to `../../knowledge-engineering/data/`
in the old repo — cross-domain, not this hub's concern (knowledge-engineering
is a separate new-repo domain). No unique architecture-domain scope beyond
what's covered. No unique content — safe to drop.

Confirmed via mapping.csv grep: deep content from these members lands at
`docs/architecture/0*-9*.md` (bulk, wave 2, "Section default" rationale),
with the testing/evaluation slice at `docs/operations/*` (wave 8), some
transcripts/templates at `docs/assets/*` (wave 8, "assets track per
doctrine"), and EA strategy content at `docs/strategy/*` — all via their own
MIGRATE/TRACK rows, not this hub. This plan only tracks scope/framing/links
otherwise lost from the hub page.

## Target Structure

Final H2/H3 outline of `docs/architecture/index.md` (short curated hub —
links only, no prose merge):

```
# Architecture Hub  (frontmatter unchanged: doc_type hub, topic_id
                     hub-architecture, domain architecture)

<intro paragraph — unchanged>

## Scope
- Architectural foundations and landing zones
- Agentic AI foundations (agent loop, memory taxonomy)         <- new
- Reference architecture catalog
- Pattern and anti-pattern catalogs
- ADR library
- Domain-driven design for agentic systems
- Integration patterns
- Enterprise architecture frameworks (TOGAF)                    <- new
- Security, guardrails, reliability & observability for agentic
  systems                                                       <- new
- ARB process

## Related
- How This Wiki Governs Itself (./00-wiki-governance.md)        <- unchanged
- Agentic Systems Hub (../agentic-systems/index.md)              <- unchanged
- Platforms Hub (../platforms/index.md)                          <- unchanged
```

Comparison against current stub: intro paragraph and 3 Related links are
kept verbatim; Scope grows from 7 to 10 bullets to explicitly cover the
foundational/security/frameworks framing that was only implicit before.
No new H2/H3 sections are added — the hub stays link-only per doc_type
rules, no prose sections, no new subsections.

## Transform Notes

- **diagram-standards**: `docs/ai-foundations/index.md` is flagged
  `ascii_art_suspected: True` and does contain two ASCII diagrams (the
  boxed "AGENT LOOP" cycle diagram and the linear tool-call sequence
  diagram under "Tool Use via MCP"). Since this file is MERGE-INTO (not
  MIGRATE) and only its scope/framing folds into the hub link list, these
  diagrams themselves are not carried into the hub page — flagging here so
  whichever canonical page ends up owning the "Agent Loop" concept (likely
  one of the docs/architecture/17-35-*.md landing-zone/foundations MIGRATE
  targets) applies diagram-standards and converts them to Mermaid there.
  No other cluster member has ascii_art_suspected=True or a raw ASCII
  diagram.
- Cross-repo links needing rewrite: several old files link with old-repo
  relative paths that no longer resolve in the new structure, e.g.
  `enterprise-architecture/ai-architecture/index.md`'s
  `../../coding-tools/claude/*.md`, `../../knowledge-engineering/knowledge/index.md`,
  `../../agentic-systems/index.md`, `../../ai-economics/index.md`; and
  `architectural-review-board/index.md`'s absolute
  `/knowledge-docs/enterprise-architecture/...` volume links and
  `../../ai-security-governance/index.md`. None of these are carried
  verbatim into the new hub (which only keeps the 3 curated Related links
  already on the stub) — flagging only so the migrator building the
  eventual MIGRATE targets for these subtrees knows the old cross-links
  need re-pointing to new-repo canonical paths, not copied as-is.
- `enterprise-architecture/process/index.md` contains inline HTML comments
  noting two old files were already merged pre-migration ("EA_Lifecycle_
  Artifact_Templates_2026.md merged... 2026-07-17", "EA_Lifecycle_
  Checklist.md merged... 2026-07-17") — informational only, no action
  needed here since neither is a member of this cluster.

## Doc Type & Template

doc_type: hub — no template — short curated hub page per
governance/DOC_TYPES.md.
