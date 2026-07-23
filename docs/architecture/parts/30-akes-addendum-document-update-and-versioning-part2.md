---
title: "AKES Addendum: Document Update & Versioning (Part 2 of 2): Changelog, Partial Updates, Retention & Governance Integration"
date_created: 2026-07-11
last_reviewed: 2026-07-17
status: current
doc_type: guide
domain: architecture
topic_id: akes-addendum-document-update-and-versioning-part2
supersedes: []
tags: [enterprise-architecture, knowledge-systems, versioning, standards]
covers_version: "2026"
---

**Part 2 of 2.** This is the continuation of [Part 1](pathname:///archon/architecture/78-akes-addendum-document-update-and-versioning): Overview & Design Intent, Version Lifecycle, Update Triggering, Update Paths, and Version Store Schema.

# A6. Changelog Rollup & Consumer-Facing Views

At high change velocity, a runbook or architecture document may accumulate dozens of micro-versions per week — each one tracking a precise, small change. This granularity is valuable for audit and incident investigation, but it is too noisy for day-to-day consumers who simply want to know "what changed this sprint?"

## Changelog rollup

The Documentation Agent runs a weekly changelog rollup job per artifact. It reads all version diffs since the last rollup and produces a human-readable summary: "This week: added dependency on Queue C (v12, PR #882), updated recovery procedure for DB failover (v13, INC-4502)." This changelog is itself a versioned artifact stored in the version store, with its own provenance (the set of version IDs it summarizes).

The rollup is also available programmatically — agents consuming the knowledge graph via MCP can query "what changed in artifact X between date A and date B?" and receive a structured diff summary rather than iterating through individual versions.

## Consumer-facing version indicators

Published surfaces (developer portal, wiki, on-call dashboards) should surface the following metadata alongside every document, drawing directly from the version store:

| Indicator | What it shows | Why it matters |
|---|---|---|
| Version badge | "v14 — last updated 3 days ago" | Immediately signals whether a document is recent or potentially stale relative to the reader's context |
| Trust level badge | Verified / Disputed / Pending Review | The core governance signal — readers know whether to act on the document with full confidence or treat it as provisional |
| Trigger summary | "Updated after: PR #882 (payments-api)" | Allows readers to immediately understand why the document changed without opening the version history |
| Change history link | Link to full version list with diffs | Supports incident investigation — "what did this runbook say before the outage?" |
| Pending update banner | "An update is pending human review — this document may not reflect recent changes." | Prevents consumers from acting on a document that the system already knows is outdated but cannot yet auto-approve |

# A7. Partial Updates — Section-Level Granularity

One of the three core design properties stated in A1 is that updates are diff-based, not full rewrites. This requires the Documentation Agent to understand artifacts at the section level, not just as flat text blobs. This section details how that works and why it matters.

## Section model

Each knowledge pack artifact is defined by a stable section schema registered in the knowledge graph. For example, the Architecture Knowledge Pack has sections: _System Overview_, _Service Catalog_, _Dependency Graph_, _Data Flows_, _Security Boundaries_. Each section maps to a set of knowledge graph entity types and relationship types that it renders. When a change event affects only the _Dependency Graph_ section (e.g., a new service-to-service call detected), only that section is re-rendered and diffed against the current version — the other sections are copied forward unchanged.

This has three important consequences:

- **Human edits in unaffected sections are preserved.** If an on-call engineer manually annotated the Security Boundaries section of an architecture doc with a note about a known exception, and the next agent update only touches the Dependency Graph section, that annotation survives untouched. The Documentation Agent never re-renders sections it was not asked to update.

- **Blast radius of updates is bounded.** The Governance Agent evaluates severity and confidence per-section, not per-document. A high-confidence, low-blast-radius change to the Service Catalog section of the Architecture Pack can be auto-approved even if the same document has a Pending Review update in progress for the Security Boundaries section.

- **Version diffs are semantically meaningful.** The diff stored in the version store is section-structured — "Security Boundaries: unchanged, Dependency Graph: added edge (payments-api → fraud-queue), Data Flows: unchanged" — rather than a line-level text diff. This is what makes the changelog rollup (Section A6) legible without further LLM processing.

**Implementation note.** The section schema for each pack is itself a versioned artifact in the system. If the Architecture Pack gains a new "Environment Topology" section, that schema change is versioned and the previous section schema is retained — so historical versions of the pack can still be rendered correctly using the schema that was active when they were published.

# A8. Version Retention & Compaction Policy

The version store is append-only and versions are never deleted — but at scale, storing the full content of every micro-version of hundreds of artifacts indefinitely would become impractical. The retention model addresses this through a tiered storage policy that preserves permanent access to key versions while compacting intermediate ones.

## Retention tiers

| Tier | Versions retained | What is kept |
|---|---|---|
| **Full fidelity (permanent)** | All Current versions, All Disputed resolutions, Any version referenced by an incident or postmortem, Any human-reviewed version, First version of any artifact (genesis) | Full content + all metadata + diff from previous |
| **Metadata-only (permanent)** | All Rejected versions, All Superseded versions older than 90 days not referenced by an incident | All metadata fields (see Section A5 schema), content hash, diff summary — but NOT full content body. Content can be reconstructed from the genesis version + the ordered chain of diffs. |
| **Purged** | Draft versions older than 30 days that never left Draft status | Only version_id, artifact_id, created_at, and status: Draft (purged) retained as a tombstone |

## Incident reference lock

When an incident or postmortem document is created, the system queries the version store for all artifacts that were in Current status at the incident start time and records those version IDs in the incident entity in the knowledge graph. This "snapshot at incident time" is locked — those versions are permanently pinned to Full Fidelity retention, regardless of age, because they are potentially needed for future postmortem review, regulatory audit, or comparative analysis ("did the runbook change before or after this class of incident started recurring?").

# A9. Design Decisions (ADR-style)

## ADR-V1: Immutable versions vs. in-place mutation with change tracking

**Decision:** Every version is immutable once it leaves Draft. Changes produce a new version.

**Alternatives considered:** A single mutable document with tracked changes (similar to Word track-changes or Google Docs history). This is the model most wiki tools use.

**Trade-off accepted:** Immutable versions require more storage and a more complex data model than tracked-changes mutation. In exchange, any version is independently addressable by ID, the content hash is a stable integrity guarantee, concurrent edits cannot produce merge conflicts within a single document blob, and incident snapshots are trivial to implement (just reference version IDs).

## ADR-V2: Section-level diffs vs. full document regeneration

**Decision:** The Documentation Agent re-renders only the sections affected by a triggering change event.

**Alternatives considered:** Full document regeneration on every update — simpler to implement and avoids the need for a stable section schema.

**Trade-off accepted:** Requires defining and versioning a section schema per pack (Section A7 implementation note), which is non-trivial. In exchange, human edits in unaffected sections are preserved across agent updates, blast radius of auto-approval is scoped to sections rather than whole documents, and diffs in the version store are semantically meaningful rather than line-level noise.

## ADR-V3: Human edits always win in conflict vs. merge strategy

**Decision:** In a conflict between a concurrent agent draft and a human edit, the human edit always wins and the agent draft is discarded.

**Alternatives considered:** An LLM-mediated merge that attempts to incorporate both the agent's proposed changes and the human's manual edits into a single new version, routed for human approval.

**Trade-off accepted:** The discard-and-re-evaluate approach means some valid agent changes may be delayed (they are resubmitted against the human-edited baseline). The merge approach could produce a higher rate of incorporating valid agent changes, but introduces the risk that the merge result is subtly wrong in ways neither the human nor the agent would independently produce — exactly the wrong-but-confident failure mode the system is designed to prevent. Discard-and-re-evaluate is the safe default; if agent change loss rates prove problematic in practice, the merge approach can be introduced cautiously for specific section types.

## ADR-V4: Content hash for deduplication and tamper detection

**Decision:** Every version stores a SHA-256 hash of its content at creation time, used for deduplication and integrity checking.

**Alternatives considered:** Relying on version IDs and timestamps alone; using a weaker hash (MD5/SHA-1) for performance.

**Trade-off accepted:** SHA-256 is computationally negligible for document-sized content. The deduplication benefit (skipping identical re-publications at high commit velocity) is significant. The tamper-detection benefit is low-probability but high-value — a document that was silently modified outside the normal write path during a security incident is exactly the kind of thing a post-incident audit needs to be able to detect.

# A10. Integration with the Governance & Trust Model

The versioning model in this addendum is the operational implementation of the trust model described in Section 10 of the main AKES brief. The two interlock at three specific points:

## 1. Trust level is a property of the version, not the artifact

An artifact's current trust level (Verified, Disputed, Pending Review, etc.) is derived from its Current version's status in the version store. This means trust level is automatically historical — if you query a previous version, you get its trust level at the time it was Current, not today's trust level. This is critical for incident retrospectives.

## 2. Auto-approve threshold calibration uses version history

The Governance Agent's auto-approval policy is not static. It is calibrated quarterly using the version history: "For agent-produced versions of type Architecture Pack / Dependency Graph section, what fraction of auto-approved versions were subsequently edited by a human reviewer within 30 days?" A high rate of post-publish human edits is a signal that the auto-approve threshold for that combination of pack type + section is too permissive and should be tightened. This closes the governance feedback loop using data the version store naturally accumulates.

## 3. Disputed status is the bridge between drift detection and versioning

When the Drift Detection Agent finds a high-severity contradiction in a Current version, it does not create a new version — it transitions the Current version's status to Disputed. This is a deliberate design choice: the document has not changed, but its trust status has. The resolution of a Dispute — either the Validation Agent confirms the current content is still correct, or the Documentation Agent produces a corrected new Draft — is what eventually produces a new version. This keeps the version history clean (a Dispute is a status event, not a content event) while ensuring that trust degradation is immediately visible to consumers.

**Closing principle.** The versioning model described in this addendum operationalizes a single idea: _every claim in a trusted knowledge artifact should be traceable to a source, a time, an agent or human, and a confidence level_ — and that trace should be queryable by any consumer, human or agent, at any point in time. This is what makes "trusted" a system property rather than a label.
