# Merge Plan: hub-platforms

## Cluster

| old_path | words | last_reviewed | source_type |
|---|---|---|---|
| docs/cloud-platforms/ai-gateway/index.md | 73 | 2026-07-10 | native-md |
| docs/cloud-platforms/aws/index.md | 116 | 2026-07-10 | native-md |
| docs/cloud-platforms/azure/index.md | 101 | 2026-07-13 | native-md |
| docs/cloud-platforms/gcp/index.md | 90 | 2026-07-13 | native-md |
| docs/cloud-platforms/iac/index.md | 11 | 2026-07-10 | native-md |
| docs/cloud-platforms/iac/terraform/index.md | 12 | 2026-07-10 | native-md |
| docs/cloud-platforms/index.md | 262 | 2026-07-10 | native-md |
| docs/cloud-platforms/kubernetes/index.md | 123 | 2026-07-10 | native-md |
| docs/databricks-agentic-ai/index.md | 1309 | 2026-07-16 | native-md (ascii_art_suspected: True) |
| docs/quantum/index.md | 458 | 2026-07-18 | native-md |

Target canonical path: `docs/platforms/index.md`
Domain: platforms
Wave: 6

All ten are section/subfolder indexes from three old top-level trees
(`cloud-platforms/` and its six subfolders, `databricks-agentic-ai/`, and
`quantum/`). Per mapping.csv every row above is `MERGE-INTO` →
`hub-platforms` with rationale "Nested section/subfolder index; one hub per
domain rule — folds into hub-platforms" (quantum's row additionally notes
"quantum's technical anchor domain"). None are `MIGRATE`.

## Survivor

Survivor = the existing fresh hub stub at `docs/platforms/index.md` (read in
full: frontmatter `doc_type: hub`, `topic_id: hub-platforms`,
`canonical: true`, `domain: platforms`, `status: draft`,
`last_reviewed: 2026-07-18`; body has a one-paragraph intro, a `## Scope`
bullet list of 7 items — platform engineering for AI workloads; AWS, Azure,
GCP; Kubernetes for AI; API/model gateways; runtimes/inference
serving/AI silicon; infrastructure-as-code; edge deployment — and a
`## Related` list of 2 links, to the Architecture Hub and the Operations
Hub). This stub is the survivor, not any old file.

Hub clusters have no old-file survivor because `doc_type: hub` is defined
(governance/DOC_TYPES.md: "Domain/topic index... Links only canonical
pages; curated, not auto") as a curated, hand-authored links page, not an
auto-generated or merged-prose document. A hub's job is to give an
architect a map of the domain and hand them off to canonical pages
elsewhere; it is explicitly not supposed to absorb body content from the
pages it replaces. All ten old section indexes here are themselves just
link/pointer lists (11–1309 words — mostly tables of "Read: X" links to
PDFs or sibling markdown files, plus one large vendor-reference doc) —
exactly the kind of content a hub supersedes by curation, not merger. So the
fresh stub already authored in this repo stays as-is in structure; the old
files contribute at most new *scope framing* or *links*, never prose.

Note on `docs/quantum/index.md`: quantum computing is not a cloud/hyperscaler
topic, and folding it into `hub-platforms` rather than a standalone
`hub-quantum` (there is no such hub in the taxonomy) is a **deliberate
cross-domain placement**, not a mapping mistake — mapping.csv's own
rationale calls `platforms` "quantum's technical anchor domain" because
quantum hardware/QPU access is consumed as infrastructure (IBM Quantum,
AWS Braket-style access, cloud-hosted QPUs) in the same way AWS/Azure/GCP
compute is. The quantum *market and career* content splits elsewhere via
separate MIGRATE/TRACK rows (see Unique-Content Map below) — only the
technical-anchor overview page folds here.

## Unique-Content Map

**docs/cloud-platforms/ai-gateway/index.md** — Points to Kong AI Gateway
setup/auth guides and three gateway-comparison PDFs. Concept ("API/model
gateways") is already a named Scope bullet; no new scope concept. Vendor
name "Kong" isn't named on the stub but is implementation detail, not
scope. No unique content — safe to drop.

**docs/cloud-platforms/aws/index.md** — Points to the AWS hyperscaler
deep-dive and Bedrock AgentCore Code Interpreter doc, plus memory/Strands
PDFs. Fully covered by the "AWS, Azure, GCP" Scope bullet. No unique
scope concept beyond what's already named. No unique content — safe to
drop.

**docs/cloud-platforms/azure/index.md** — Points to the Azure hyperscaler
deep-dive; `## Related` links `../enterprise-agent-runtime-internals-2026.md`
(in-domain, has its own MIGRATE row) and
`../../ai-protocols/auth/agent-identity-entra-vs-awsagentcore.md`
(cross-domain, outside `cloud-platforms`). Covered by "AWS, Azure, GCP"
Scope bullet; no new scope concept. Cross-domain link needs rewrite — see
Transform Notes. Otherwise no unique content — safe to drop.

**docs/cloud-platforms/gcp/index.md** — Points to the GCP hyperscaler
deep-dive; `## Related` links the same
`../enterprise-agent-runtime-internals-2026.md` and
`../../ai-protocols/standards/AI_Protocols_Standards_Service_Industry_Guide_2026.md`
(cross-domain, A2A protocol coverage). Covered by "AWS, Azure, GCP" Scope
bullet; no new scope concept. Cross-domain link needs rewrite — see
Transform Notes. Otherwise no unique content — safe to drop.

**docs/cloud-platforms/iac/index.md** — 11-word stub: "Documentation and
resources for Infrastructure as Code." Fully covered by the
"Infrastructure-as-code" Scope bullet. No unique content — safe to drop.

**docs/cloud-platforms/iac/terraform/index.md** — 12-word stub: "Guides
covering Terraform mastery and AI-assisted infrastructure as code
practices." Terraform isn't named explicitly on the stub but is an
implementation detail of the existing IaC bullet, not a new scope concept.
No unique content — safe to drop.

**docs/cloud-platforms/index.md** — The richest loser (262 words). Has
framing not yet on the stub: a "Cross-Platform Comparison" pointing to the
21-dimension runtime-internals whitepaper (compute isolation
Firecracker/gVisor/Hyper-V, session management, MCP integration, auth
SigV4/Entra MI/GCP WIF, multi-tenancy) and a "Hyperscaler Deep Dive Series"
table naming each hyperscaler's strategic differentiator (AWS: Firecracker
microVM isolation/AgentCore workload capture; Azure: M365/Entra/Graph data
moat + Entra Agent ID; GCP: TPU economics + A2A/Linux Foundation
standards leadership). Recommend adding a Scope bullet like
"Cross-hyperscaler architecture & runtime-internals comparison" — the
current "AWS, Azure, GCP" bullet doesn't capture that there's a dedicated
comparative-analysis angle. Deep content itself already has MIGRATE rows
(`docs/platforms/23-*`, `20/22/24-*`, wave 6) — this plan only adds the
missing scope framing.

**docs/cloud-platforms/kubernetes/index.md** — Intro to the 16-part K8s
handbook (infrastructure evolution through AI/agentic workloads,
internals, networking, storage, security, platform engineering, future
outlook). Fully covered by the "Kubernetes for AI" Scope bullet already —
comprehensive, but no new scope concept beyond what's named. No unique
content — safe to drop.

**docs/databricks-agentic-ai/index.md** (ascii_art_suspected: True,
1309 words) — Substantial vendor-platform content not named anywhere in
the current Scope: Databricks' Lakehouse/Mosaic AI agentic platform (Agent
Bricks, Omnigent meta-harness, Genie One/Ontology, Unity Catalog + Unity AI
Gateway, Lakebase, LTAP, Lakeflow, Apache Iceberg v3). This is a real scope
gap — "Databricks" or "Lakehouse AI" appears nowhere on the current stub.
Recommend adding a Scope bullet, e.g. "Databricks Lakehouse / Mosaic AI
agentic platform." Contains one ASCII-art architecture diagram (5-layer
box diagram: Experience / Agentic Intelligence / Governance & Control
Plane / Data & Compute / Storage layers) — flagged `ascii_art_suspected:
True`, confirmed present — see Transform Notes. The deep content itself
splits across three destinations per mapping.csv: most parts (01-04, 07-09,
13) → `docs/platforms/43-50-*.md` (wave 6, "Section default"); part-05
(lakehouse data infra) and part-06 (Iceberg/open formats) → `docs/
data-knowledge/01-02-*.md` (wave 5, explicit data-knowledge taxonomy
scope); part-12 (FinOps) → `docs/operations/02-finops-ai-soc.md` (wave 8,
MERGE-INTO an existing survivor, duplicate AI-SOC-FinOps subject). This
plan only recommends the missing scope bullet and flags the diagram — the
prose itself is not merged here.

**docs/quantum/index.md** (458 words) — Entirely new topic area for this
hub: quantum computing commercialization (IBM Nighthawk/Loon, Google
Willow, Microsoft Majorana 1, Quantinuum logical qubits, NIST
post-quantum-cryptography standards FIPS 203-205), pointers to the
12-week "Zero to Mastery" quantum-AI program, IBM certification guides,
and industry-landscape reports (tech giants, startups, consultancies). None
of this is covered by any current Scope bullet — recommend adding, e.g.,
"Quantum computing platforms & quantum-AI convergence." Per the cluster
rationale, this folds here as quantum's *technical anchor domain*, but the
market/consultancy reports and the IBM cert guides are routed to different
hubs entirely: `Quantum_AI_Consultancies_Report.md` and
`Quantum_AI_Startups_Report.md` → `docs/strategy/01-02-*.md` (wave 1,
"market/vendor landscape -> strategy, not platforms"); both IBM cert guides
→ `docs/career/28-29-*.md` (wave 8, `TRACK` disposition, "certification
study guide -> career track per doctrine"); the 4-part Zero-to-Mastery
series and its monolith wrapper → `docs/platforms/01-04-*.md` (wave 6,
MIGRATE, with the monolith folding into part 1 rather than standing as a
second doc); `Quantum_AI_Zero_to_Mastery.md` (the raw PDF import) is
`DROP`ped outright as superseded by the split. This plan only recommends
the new Scope bullet and notes that curated links for the quantum program
should point at the eventual `docs/platforms/01-*` landing page, not at
old-repo paths.

Confirmed via mapping.csv grep: deep content from these members lands at
`docs/platforms/0*-9*.md` (bulk, wave 6, "Section default" rationale) and
`docs/platforms/43-50-*.md` (databricks bulk, wave 6), with a data-modeling
slice at `docs/data-knowledge/01-02-*.md` (wave 5), a FinOps slice merged
into `docs/operations/02-finops-ai-soc.md` (wave 8), a market-landscape
slice at `docs/strategy/01-02-*.md` (wave 1), and a certification slice
tracked at `docs/career/28-29-*.md` (wave 8) — all via their own
MIGRATE/MERGE-INTO/TRACK rows, not this hub. This plan only tracks
scope/framing/links otherwise lost from the hub page.

## Target Structure

Final H2/H3 outline of `docs/platforms/index.md` (short curated hub —
links only, no prose merge, grouped by cloud provider / vendor):

```
# Platforms Hub  (frontmatter unchanged: doc_type hub, topic_id
                  hub-platforms, domain platforms)

<intro paragraph — unchanged>

## Scope
- Platform engineering for AI workloads
- AWS, Azure, GCP                                              <- unchanged
- Cross-hyperscaler architecture & runtime-internals comparison <- new
- Kubernetes for AI
- API/model gateways
- Runtimes, inference serving, and AI silicon
- Infrastructure-as-code
- Edge deployment
- Databricks Lakehouse / Mosaic AI agentic platform             <- new
- Quantum computing platforms & quantum-AI convergence          <- new

## Related
- Architecture Hub (../architecture/index.md)                   <- unchanged
- Operations Hub (../operations/index.md)                       <- unchanged
```

Comparison against current stub: intro paragraph and both Related links
are kept verbatim; Scope grows from 7 to 10 bullets to explicitly cover the
cross-hyperscaler-comparison, Databricks, and quantum framing that would
otherwise be silently dropped when the old section indexes are deleted. No
new H2/H3 sections are added — the hub stays link-only per doc_type rules;
once the wave-6 MIGRATE targets exist, curated links to the AWS/Azure/GCP
deep-dives, the Kubernetes handbook entry point, the AI Gateway guide, the
Terraform guide, the Databricks reference (`docs/platforms/43-*.md`), and
the Quantum foundations page (`docs/platforms/01-*.md`) should be added
under Scope or a future short "Start Here" grouping — left to the stage-04
migrator/librarian once those canonical paths exist, not specified further
here.

## Transform Notes

- **diagram-standards**: `docs/databricks-agentic-ai/index.md` is flagged
  `ascii_art_suspected: True` and does contain one ASCII box-diagram (the
  5-layer "DATABRICKS DATA INTELLIGENCE PLATFORM" architecture map:
  Experience / Agentic Intelligence / Governance & Control Plane / Data &
  Compute / Storage). Since this file is MERGE-INTO (not MIGRATE) and only
  its scope/framing folds into the hub link list, the diagram itself is not
  carried into the hub page — flagging here so whichever canonical page
  ends up owning the Databricks platform-architecture overview (likely
  `docs/platforms/43-part-01-platform-vision-agentic-services.md` or a
  dedicated Databricks landing page) applies diagram-standards and
  converts it to a proper Mermaid C4-style diagram there. No other cluster
  member has `ascii_art_suspected: True` or a raw ASCII diagram.
- Cross-repo links needing rewrite: `cloud-platforms/azure/index.md` links
  `../../ai-protocols/auth/agent-identity-entra-vs-awsagentcore.md`
  (old-repo relative path into a sibling top-level tree); `cloud-platforms/
  gcp/index.md` links `../../ai-protocols/standards/
  AI_Protocols_Standards_Service_Industry_Guide_2026.md`. Both point outside
  `cloud-platforms/` into what is now the `protocols` domain in the new
  repo. Neither is carried verbatim into the new hub (which only keeps the
  2 curated Related links already on the stub) — flagging only so the
  migrator building the eventual Azure/GCP MIGRATE targets
  (`docs/platforms/21-22-*.md`, `24-*.md`) knows these old cross-links need
  re-pointing to new-repo canonical paths under `docs/protocols/`, not
  copied as-is. `quantum/index.md`'s links to
  `/knowledge-docs/quantum/IBM_Associate_Quantum_CertGuide` etc. are
  old-repo static-asset absolute paths that also need re-pointing once the
  TRACK targets exist at `docs/career/28-29-*.md`.

## Doc Type & Template

doc_type: hub — no template — short curated hub page per
governance/DOC_TYPES.md.
