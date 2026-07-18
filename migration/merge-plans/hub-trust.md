# Merge Plan: hub-trust

## Cluster

| old_path | words | last_reviewed | source_type | ascii_art_suspected |
|---|---|---|---|---|
| docs/ai-security-governance/index.md | 467 | 2026-07-10 | native-md | False |
| docs/ai-security-governance/policy/index.md | 661 | 2026-07-10 | native-md | True |
| docs/ai-security-governance/security/index.md | 86 | 2026-07-10 | native-md | False |
| docs/ai-soc-playbooks/index.md | 929 | 2026-07-16 | native-md | True |
| docs/cybersec-architect/index.md | 801 | 2026-07-10 | native-md | False |
| docs/nist-ai-standards/index.md | 791 | 2026-07-16 | pdf-converted | True |
| docs/sovereign-constitutional-ai/index.md | 1115 | 2026-07-10 | native-md | True |

- target_topic_id: `hub-trust`
- target_path: `docs/trust/index.md`
- domain: `trust`
- wave: 7

All seven rows are `disposition=MERGE-INTO` per `migration/mapping.csv`. There
is no `MIGRATE` row for this cluster — confirmed by grep of mapping.csv.

## Survivor

Survivor is the already-existing fresh hub stub at `docs/trust/index.md`
(read in full: frontmatter `doc_type: hub`, `status: draft`, `topic_id:
hub-trust`, with a "Scope" bullet list and a "Related" links list — no
prose body beyond a one-paragraph intro).

A hub cluster has no old-file survivor by design: per
`governance/DOC_TYPES.md`, `doc_type: hub` is "Links only canonical pages;
curated, not auto" — a hub is authored fresh and hand-curated by the person
building the new domain, not inherited or rolled up from any single old
section-index page. The seven old `index.md` files here are themselves nested
section indexes (one per old top-level folder), and the "one hub per domain"
rule means they all fold into the single new `docs/trust/index.md` as link
targets, not as merged prose. This matches `governance/CANONICAL_REGISTRY.yaml`,
which already lists all seven as `supersedes:` entries under `id: hub-trust` —
no registry gap.

## Unique-Content Map

For each loser, checked against the current stub's Scope bullets (threat
models, AI control mechanisms, identity/authorization, guardrails/red
teaming, governance frameworks, compliance index, AI SOC).

**docs/ai-security-governance/index.md** (467w)
- Unique framing: "AI Security Is a Three-Layer Problem" (Identity/Credentials
  → Behavioral/Architectural → Governance/Compliance) — a useful 3-layer
  mental model not present in the stub's flat bullet list.
- Unique links worth curating: cross-links to `agentic-ui/security-architecture.md`
  and `agentic-ui/devsecops.md` (agentic UI security/DevSecOps) — these are
  outside this cluster's mapping.csv rows and outside docs/trust scope; flag
  for hub "Related" only if those old paths have their own MIGRATE row
  elsewhere (not confirmed in this grep — out of scope for this plan to
  verify further).
- Regulatory Framework Map table (EU AI Act, NIST AI RMF, ISO 42001, OWASP
  Agentic Top 10) — deep content already migrates via the 8-way sprawl rows
  (e.g. `docs/trust/ai-security-governance/33-...` etc.); no unique fact lost,
  just don't let the summary table itself vanish unlinked — the "Compliance
  index" scope bullet already covers this at a category level.

**docs/ai-security-governance/policy/index.md** (661w, ascii_art_suspected=True)
- Unique scope note: introduces OPA vs Cedar as "the two leading engines" —
  already covered by "Identity and authorization" bullet at the concept
  level; the OPA/Rego and Cedar code samples are deep content migrating via
  the Vol0–Vol5b MIGRATE rows (confirmed in mapping.csv, target
  `docs/trust/ai-security-governance/02..32-*.md`).
- Contains an ASCII diagram ("Agent → Tool Call Request → Policy Gateway →
  Allow/Deny/Notify → Tool") and a sidecar-pattern ASCII diagram — flagged
  below under Transform Notes (diagram-standards), not hub content.
- No unique link or fact beyond what "Identity and authorization" already
  scopes — safe to drop as hub content once diagrams are preserved in their
  MIGRATE targets.

**docs/ai-security-governance/security/index.md** (86w)
- Effectively a bare link list to 8 PDF-converted volumes, all of which have
  their own MIGRATE rows. No unique framing, no unique links outside the
  cluster — no unique content, safe to drop.

**docs/ai-soc-playbooks/index.md** (929w, ascii_art_suspected=True)
- Unique framing: "Evolution of Security Operations" timeline (Traditional
  SOC → SOAR → ML-Assisted → LLM-Assisted → Agentic SOC → Autonomous
  Security Operations 2027→) — a useful timeline not in the stub; "AI
  Security Operations Center (AI SOC)" bullet covers the topic but not this
  narrative arc. Worth one curated link/callout, not prose.
- SOC Maturity Snapshot table and Key Findings stats (e.g. "AI triage
  reduces analyst time-to-investigate by 60–75%") — sourced stats that
  belong on the migrated Part-series pages, not the hub; already covered by
  MIGRATE rows to `docs/trust/ai-soc-playbooks/01..13-*.md` (part-12-finops
  is the one exception, MERGE-INTO `docs/operations/02-finops-ai-soc.md`,
  wave 8 — note this playbook has one member routed to a different domain).
- Capability Map ASCII diagram (DETECT/INVESTIGATE/RESPOND/ENABLE) — flagged
  under Transform Notes.
- No unique external links outside the cluster.

**docs/cybersec-architect/index.md** (801w)
- Unique framing: "Three Eras of Enterprise Security" table (Traditional →
  Cloud-Native → AI-Native, with failure modes) — a distinct
  historical/maturity lens not elsewhere in the stub; candidate for a
  curated link callout under a future "Threat models" or "Governance
  frameworks" hub bullet.
- "How Security Connects to Enterprise Architecture" chain diagram (ASCII,
  simple arrows) — low-value, mostly restates the EA layering; not flagged
  as ascii_art_suspected in cluster data (False), treat as low-priority
  cleanup only if touched.
- Cross-Section Navigation table links to `../cloud-platforms/ai-gateway/index.md`
  and `../enterprise-architecture/index.md` — outside this cluster; these
  are candidate "Related" links for the hub if those targets exist as
  canonical pages post-migration (not confirmed here — flag for the
  librarian/reviewer to verify before wiring into "Related").
- Companion link to `usecase-transcript.md` — already tracked separately in
  mapping.csv (disposition=TRACK, target `docs/assets/05-transcript-...md`,
  wave 8); no action needed here beyond noting it exists.

**docs/nist-ai-standards/index.md** (791w, source_type=pdf-converted,
ascii_art_suspected=True)
- Unique framing: "NIST AI Trustworthiness Framework" 7-properties list
  (Valid & Reliable, Safe, Secure & Resilient, Explainable,
  Privacy-Enhanced, Fair, Accountable) mapped to which of AI 100-2/100-4/
  CAISI addresses which property — a useful cross-standard mapping not
  elsewhere in the stub. Worth a curated link into a "Standards mapping"
  sub-bullet if the hub grows one; otherwise the "Compliance index" bullet
  covers it at category level.
- "Quick Reference: Attack to Standard Mapping" table — deep-reference
  content; all seven Part-0X pages have MIGRATE rows to
  `docs/trust/nist-ai-standards/01..07-*.md`, so no fact is lost, only the
  table's own presentation (which is PDF-converted boilerplate, see
  Transform Notes).
- Two ASCII box-diagrams (AI-specific attack surface; trustworthiness
  properties) — flagged under Transform Notes.

**docs/sovereign-constitutional-ai/index.md** (1115w, ascii_art_suspected=True)
- Unique framing: 12-Domain map (Sovereign AI Foundations →
  Constitutional AI Engineering → RAI Operating Model → AI Alignment &
  Control → AI Governance Operating Model → AI Risk Taxonomy → AI Safety
  Framework → AI Assurance & Audit → Constitutional Agent Architecture →
  Policy-as-Code → Democratic & Public Interest AI → Roadmap/Maturity) —
  the most granular domain breakdown in the whole cluster. The stub's
  "Governance frameworks (responsible/constitutional AI, sovereign AI)"
  bullet covers this at the top level only; all 12 domains already have
  MIGRATE rows to `docs/trust/sovereign-constitutional-ai/01-12-*.md`, so no
  content is lost, but this index's "Navigate by Role" table (CAIO, RAI
  Lead, Principal AI Architect, AI Risk Officer, etc.) is a genuinely
  useful persona-routing aid not replicated on the destination pages or the
  stub — worth considering as a learning-path spoke rather than hub
  content (out of scope to create here; flag for follow-up).
- Unique cross-repo links: `../coding-tools/claude/constitutional-ai-safety-2026.md`
  and `../ai-usecases/EU_Banking_AI_Evaluation_Compliance_Guide.md` — outside
  this cluster's mapping.csv rows; flag for librarian to confirm whether
  those old paths have their own disposition before wiring as "Related"
  links on the hub.
- 12-Domain ASCII tree diagram — flagged under Transform Notes.

## Target Structure

Keep `docs/trust/index.md` a short, curated, links-only hub. Proposed
final H2/H3 outline (minimal change from the current stub):

```
## Scope
## Related
```

The existing Scope bullet list already covers every topic surfaced by the
seven losers at the category level (threat models, AI control mechanisms,
identity/authorization, guardrails/red teaming, governance frameworks,
compliance, AI SOC). No new Scope bullets are required.

Comparison against current stub:
- Scope: no additions needed — all loser content is category-covered.
- Related: current stub has 2 links (Protocols Hub, Operations Hub — the
  latter already anticipates the AI-SOC-FinOps handoff to `docs/operations`).
  Consider adding, once the flagship MIGRATE-spoke pages land in wave 7,
  curated links to the flagship overview/spoke pages that replace these
  seven losers as entry points, e.g.:
  - `docs/trust/ai-security-governance/01-ai-control-series-overview.md` (DeepMind 18-part series overview — flagship spoke)
  - `docs/trust/ai-security-governance/02-policy-authorization-series-overview.md` (Policy/Authorization series overview — flagship spoke)
  - `docs/trust/nist-ai-standards/01-part-01-nist-ai-100-2-adversarial-ml.md` (NIST standards entry point)
  - `docs/trust/sovereign-constitutional-ai/03-ai-governance-operating-model.md` (Sovereign/Constitutional AI entry point)
  - `docs/trust/cybersec-architect/01-evolution.md` (Cybersecurity Architect entry point)
  - `docs/trust/ai-soc-playbooks/01-part-01-soc-operating-model.md` (AI SOC entry point)
  This is a wave-7 follow-up once those target pages actually exist; do not
  add dead links now. No prose sections beyond the existing one-paragraph
  intro should be added — hub stays links-only per doc_type=hub.

## Transform Notes

- **PDF-converted artifact**: `docs/nist-ai-standards/index.md` is
  `source_type: pdf-converted`. Its two box-drawn tables/diagrams
  ("AI-specific attack surface", "NIST AI Trustworthiness Properties") are
  converted-PDF layout artifacts, not hand-authored Markdown — strip
  entirely from hub content (the hub takes no prose from this file anyway;
  this note is for the migrator working the MIGRATE targets in
  `docs/trust/nist-ai-standards/`, not for this hub file).
- **ASCII-art → Mermaid (diagram-standards)** — flagged
  `ascii_art_suspected=True` for:
  - `docs/ai-security-governance/policy/index.md` — Policy Gateway flow
    diagram and OPA-sidecar diagram.
  - `docs/ai-soc-playbooks/index.md` — "Evolution of Security Operations"
    timeline and "AI SOC CAPABILITY MAP" box diagram.
  - `docs/sovereign-constitutional-ai/index.md` — 12-Domain tree diagram.
  - `docs/nist-ai-standards/index.md` — attack-surface and trustworthiness
    box diagrams.
  None of these diagrams belong on the hub itself (hub is links-only); this
  is a note for whoever runs `diagram-standards` on the corresponding
  MIGRATE-target pages in wave 7, so the ASCII art doesn't survive verbatim
  into the new corpus.
- **Cross-repo links needing rewrite/verification** (none point at anything
  inside this cluster, so none affect the hub file directly, but they
  surface old-repo paths that may or may not have their own mapping.csv
  disposition — flag for librarian/reviewer before adding as hub
  "Related" links):
  - `../agentic-ui/security-architecture.md`, `../agentic-ui/devsecops.md`
    (from ai-security-governance/index.md)
  - `../cloud-platforms/ai-gateway/index.md`, `../enterprise-architecture/index.md`
    (from cybersec-architect/index.md)
  - `../coding-tools/claude/constitutional-ai-safety-2026.md`,
    `../ai-usecases/EU_Banking_AI_Evaluation_Compliance_Guide.md`
    (from sovereign-constitutional-ai/index.md)
  - `../ai-protocols/auth/index.md` (appears in multiple losers) — likely
    resolves to `docs/protocols/01-auth-standards-reference.md` per the
    `Part7_Standards_Reference.md` MERGE-INTO row in mapping.csv; confirm
    before wiring.

## Doc Type & Template

doc_type: `hub`. No template file exists for the `hub` type in
`.claude/skills/doc-standards/templates/` (only `concept.md`,
`decision-adr.md`, `reference-architecture.md` exist there) — per
`governance/DOC_TYPES.md`, a hub is "links only, curated, not auto": no
template — short curated hub page per `governance/DOC_TYPES.md`.
