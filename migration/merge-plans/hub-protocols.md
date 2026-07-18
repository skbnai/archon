# Merge Plan: hub-protocols

## Cluster

| old_path | words | last_reviewed | source_type | ascii_art_suspected |
|---|---|---|---|---|
| docs/ai-protocols/a2a/index.md | 776 | 2026-07-16 | native-md | True |
| docs/ai-protocols/auth/index.md | 803 | 2026-07-10 | native-md | True |
| docs/ai-protocols/index.md | 628 | 2026-07-16 | native-md | True |
| docs/ai-protocols/mcp/index.md | 198 | 2026-07-10 | native-md | False |
| docs/ai-protocols/standards/emerging-protocols-beyond-mcp-a2a.md | 774 | 2026-07-11 | native-md | False |
| docs/ai-protocols/standards/index.md | 463 | 2026-07-16 | native-md | False |

- target_topic_id: `hub-protocols`
- target_path: `docs/protocols/index.md`
- domain: `protocols`
- wave: 4

All six rows are `disposition=MERGE-INTO` per `migration/mapping.csv`
(lines 116, 127, 130, 134, 139, 144). There is no `MIGRATE` row for this
cluster — confirmed by grep of `mapping.csv` for `hub-protocols`.

Deep content from the same old folders migrates via separate MIGRATE rows,
out of scope for this plan:
- `docs/ai-protocols/auth/*` — 12 MIGRATE rows (targets
  `docs/protocols/01-*.md` through `12-*.md`); per instructions, these are
  handled across 3 separate merge-plan clusters elsewhere in stage-03 —
  not duplicated here.
- `docs/ai-protocols/mcp/*` — 3 MIGRATE rows (`13-mcp-deep-research-2026.md`,
  `14-mcp-enterprise-security-governance-operations-2026.md`,
  `15-mcp-harness-aidlc.md`).
- `docs/ai-protocols/standards/*` (excluding the emerging-protocols-beyond-
  mcp-a2a.md index file, which is MERGE-INTO here) — 8 MIGRATE rows
  (`16-*.md` through `23-*.md`, plus `emerging-protocols-overview.md` →
  `21-*.md`).
- `docs/ai-protocols/a2a/*` — no additional MIGRATE rows exist beyond
  `index.md` itself; a2a's deep content has no migration destination in
  this dataset (see Unique-Content Map finding below).

## Survivor

Survivor is the already-existing fresh hub stub at `docs/protocols/index.md`
(read in full: frontmatter `doc_type: hub`, `domain: protocols`,
`status: draft`, `topic_id: hub-protocols`, `tags: [hub, protocols]`, with a
one-paragraph intro, a "Scope" bullet list of 5 items — MCP, A2A, emerging
interoperability standards, agent identity/auth, connectors — and a
"Related" list linking to the Agentic Systems Hub and Trust Hub).

A hub cluster has no old-file survivor by design: per
`governance/DOC_TYPES.md`, `doc_type: hub` is "Links only canonical pages;
curated, not auto" — a hub is hand-authored fresh, not inherited or rolled
up from any single old section-index page. All six old files here are
nested section/subfolder indexes (the domain root `ai-protocols/index.md`
plus one index per subfolder: `a2a/`, `auth/`, `mcp/`, `standards/`, plus
the `standards/emerging-protocols-beyond-mcp-a2a.md` series-index — see
below), and the "one hub per domain" rule folds all of them into the single
new `docs/protocols/index.md` as curated link targets, not merged prose.

## Unique-Content Map

Checked against the stub's 5 Scope bullets (MCP; A2A; emerging
interoperability standards; agent identity/auth; connectors).

**docs/ai-protocols/index.md** (628w)
- Protocol Landscape table (10 protocols: MCP, A2A, OAuth 2.1, SPIFFE/SPIRE,
  AG-UI, ANP, AP2, ACP, NLIP, UCP) and a "Decision Framework — Which
  Protocol?" table (10 task→protocol rows) — both are useful wayfinding
  aids, not covered by the stub's flat Scope bullets. Recommend folding a
  condensed version of the decision table into the hub itself (still
  links-only in spirit: each row points at a Scope area).
- "Sections" list with one-paragraph descriptions of each subfolder — this
  is exactly what the stub's Scope bullets replace; no new facts.
- ASCII "Core Protocol Stack" diagram — flagged under Transform Notes, not
  hub content.

**docs/ai-protocols/a2a/index.md** (776w)
- No unique content is *lost* re: Scope (A2A is already a Scope bullet), but
  flag a gap: Core Primitives table, Request Flow diagram, Security Model
  table, and Protocol Versions table are substantive unique content with
  **no MIGRATE destination anywhere in mapping.csv** — a2a/ has zero
  sibling MIGRATE rows. This content will be lost entirely unless curated
  as hub links to the cross-domain deep-dive pages it already cites:
  `enterprise-architecture/ai-architecture/mcp-a2a-protocol-deep-dive.md`,
  `a2a-enterprise-security-governance-guide.md`,
  `agent-interoperability-orchestration.md`,
  `ai-finops-rag-mcp-a2a-economics.md` — these are outside this cluster and
  their own disposition is not confirmed here (different domain/wave); flag
  for librarian/reviewer to verify before wiring as hub "Related" links.

**docs/ai-protocols/auth/index.md** (803w)
- No unique facts beyond the stub's "Agent identity and authentication"
  bullet — this page is itself a link-list wrapper (3LO, OBO, SPIFFE/SPIRE
  narrative + a PDF/detail-page link list) over the 12 auth/ MIGRATE
  targets. Safe to fold as links; deep content is preserved via those 12
  rows (handled by other clusters, not duplicated here).
- Unique cross-links worth surfacing on the hub: `cloud-platforms/ai-gateway/
  kong-ai-gateway-guide.md` (Kong AI Gateway auth proxy) and
  `agentic-ui/identity-auth-architecture.md` — outside this cluster's rows;
  flag for librarian to confirm disposition before adding as "Related".

**docs/ai-protocols/mcp/index.md** (198w)
- No unique content — a bare link list to the 3 mcp/ MIGRATE targets plus
  cross-links to `coding-tools/claude/mcp-deep-guide.md` and the A2A index
  (already an internal cluster link). No unique content — safe to drop.

**docs/ai-protocols/standards/index.md** (463w)
- Protocol Convergence Landscape table — a third near-duplicate of the same
  protocol summary table that also appears in `ai-protocols/index.md` and
  `emerging-protocols-beyond-mcp-a2a.md` (see below); no new facts, but
  confirms the table is worth keeping exactly once, consolidated on the hub.
- Governance Bodies table (Linux Foundation AAIF, IETF, CNCF, Ecma TC56,
  Eclipse Foundation, Google) — genuinely unique, not present in the stub
  or any other loser; worth 1 curated line/table on the hub or folded into
  a "Standards" scope bullet.
- Guides/See Also links — all point at standards/ MIGRATE targets already
  tracked; no unique content beyond the Governance Bodies table.

**docs/ai-protocols/standards/emerging-protocols-beyond-mcp-a2a.md** (774w) —
flagged for careful review per instructions:
- Read in full. Despite its word count and its own frontmatter
  `doc_type: research-series-index`, this file is **not** a standalone
  content piece — it is a series-index/table-of-contents over 5 other files
  that each already have their own MIGRATE row and target topic_id in
  mapping.csv: `emerging-protocols-overview` (21), `emerging-protocols-acp-
  anp` (18), `emerging-protocols-agui-utcp` (19), `emerging-protocols-
  ucp-ap2-nlip-lmos` (22), `emerging-protocols-crosscutting` (20).
- Its content breaks down as: (1) an intro paragraph restating the "nine
  protocols beyond MCP/A2A" framing already in the stub's Scope bullet and
  in `ai-protocols/index.md`'s Sections list; (2) a protocol summary table
  that is a third near-duplicate of the tables in `ai-protocols/index.md`
  and `standards/index.md`; (3) a "Series Structure" section that is pure
  navigation to the 5 already-migrated sections; (4) a "How to Use This
  Series" persona-routing table (CTO → Section 1, architect evaluating
  ANP/ACP → Section 2A, etc.) — a mildly useful wayfinding convenience, but
  it only re-routes to the same 5 sections, adding no new fact; (5) a
  Related Guides list overlapping `standards/index.md`'s See Also.
- **Conclusion: no unique standards content beyond what the 5 MIGRATE
  targets and the hub Scope already cover.** Recommend folding as a single
  curated link (or dropping outright) — does **not** warrant its own spoke
  page or registered topic. Not flagging NEEDS LIBRARIAN REGISTRATION.
  (Noting for the record: this contradicts a naive word-count read of the
  file — the length is series-navigation prose, not unique technical
  depth.)

## Target Structure

Keep `docs/protocols/index.md` a short, curated, links-only hub. Proposed
final H2/H3 outline (modest expansion from the current stub, still
links-only):

```
## Scope
## Which Protocol Do I Need?   (new — condensed decision-framework table)
## MCP
## Agent-to-Agent (A2A)
## Authentication & Identity
## Emerging Protocols & Standards
## Related
```

Comparison against current stub:
- Scope: unchanged, all 5 bullets already cover every loser at category
  level.
- New "Which Protocol Do I Need?" table: condensed 5–6 row version of the
  decision framework repeated across `ai-protocols/index.md` and echoed by
  the protocol-landscape tables in `standards/index.md` and the emerging-
  protocols series index — consolidating the one wayfinding table that
  appeared 3x in the loser set into a single hub location.
- MCP / A2A / Authentication & Identity / Emerging Protocols & Standards:
  each becomes a 1–2 line description plus a bullet-link list to the
  corresponding MIGRATE-target spoke pages once they land in wave 4 (e.g.
  `docs/protocols/13-mcp-deep-research-2026.md`,
  `docs/protocols/01-auth-standards-reference.md`,
  `docs/protocols/18-emerging-protocols-acp-anp.md`, etc.) — do not add
  these links until the target pages actually exist.
- A2A subsection should additionally carry the flagged cross-domain
  "Related" candidates (mcp-a2a-protocol-deep-dive.md,
  a2a-enterprise-security-governance-guide.md, etc.) once their own
  disposition is confirmed by librarian/reviewer.
- Related: keep existing 2 links (Agentic Systems Hub, Trust Hub); consider
  adding the Governance Bodies note from `standards/index.md` as a short
  line under "Emerging Protocols & Standards" rather than a new hub
  section.
- No prose sections beyond the existing one-paragraph intro should be
  added — hub stays links-only per `doc_type=hub`.

## Transform Notes

- **ASCII-art → Mermaid (diagram-standards)** — flagged
  `ascii_art_suspected=True` for:
  - `docs/ai-protocols/index.md` — "The Core Protocol Stack" box diagram.
  - `docs/ai-protocols/a2a/index.md` — "Request Flow" sequence-style ASCII
    diagram (Caller Agent → Agent Card → Task → Remote Agent → Artifact).
  - `docs/ai-protocols/auth/index.md` — "Agent Authentication Stack"
    delegation-chain diagram and the OBO token-exchange ASCII flow.
  None of these diagrams belong on the hub itself (hub is links-only); this
  is a note for whoever runs `diagram-standards` on the corresponding
  MIGRATE-target pages (e.g. the a2a deep-dive destination once one is
  confirmed, and `docs/protocols/07-auth-identity-flows.md` /
  `05-identity-obo-sessions.md`), so the ASCII art doesn't survive verbatim
  into the new corpus.
- `docs/ai-protocols/mcp/index.md` and `docs/ai-protocols/standards/index.md`
  and `emerging-protocols-beyond-mcp-a2a.md` contain no ASCII diagrams
  (matches cluster data `ascii_art False`) — no diagram-standards action
  needed for these three.
- **Cross-repo links needing rewrite/verification** (point outside this
  cluster; flag for librarian/reviewer before wiring into hub "Related"):
  - `../../enterprise-architecture/ai-architecture/mcp-a2a-protocol-deep-dive.md`,
    `a2a-enterprise-security-governance-guide.md`,
    `agent-interoperability-orchestration.md`,
    `ai-finops-rag-mcp-a2a-economics.md` (from `a2a/index.md`).
  - `../../cloud-platforms/ai-gateway/kong-ai-gateway-guide.md`,
    `../../agentic-ui/identity-auth-architecture.md`,
    `../../enterprise-architecture/ai-architecture/agentic-ai-security-identity.md`
    (from `auth/index.md`).
  - `../../coding-tools/claude/mcp-deep-guide.md` (from `mcp/index.md`).
  - `../../agentic-ui/agui-standards-landscape.md` (from the emerging-
    protocols series index).
  - Old-repo absolute-path links of the form
    `/knowledge-docs/ai-protocols/auth/...` in `auth/index.md` — internal
    old-site paths, not old-repo-relative; must resolve to the new
    `docs/protocols/0X-*.md` MIGRATE targets, not be carried over verbatim.

## Doc Type & Template

doc_type: `hub`. No template file exists for the `hub` type in
`.claude/skills/doc-standards/templates/` — per `governance/DOC_TYPES.md`,
a hub is "Links only canonical pages; curated, not auto": no template —
short curated hub page per `governance/DOC_TYPES.md`.

`docs/ai-protocols/standards/emerging-protocols-beyond-mcp-a2a.md` was
checked specifically for whether it needs its own spoke page/doc_type
(e.g. `research-report` or `concept`) per instructions. Finding: it does
**not** — see Unique-Content Map above. It is a series-index duplicate of
already-registered topics, not unique content. No NEEDS LIBRARIAN
REGISTRATION flag raised.
