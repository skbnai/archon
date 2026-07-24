---
title: 'THE ENTERPRISE PR REVIEW PLAYBOOK (Part 2)'
doc_type: guide
domain: agentic-systems
topic_id: pr-review-handbook-vol2-deep-domain-reviews-part2
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---


**This is Part 2 of 2. [Back to Part 1 ←](pathname:///archon/agentic-systems/coding-tools/43-pr-review-handbook-vol2-deep-domain-reviews) for the beginning.**

### **5.2 Kubernetes, Helm, and Dockerfiles**

#### **Kubernetes / Container Review Checklist**

|**Item**|**Why It's Reviewed**|
|---|---|
|Resource requests/limits|Missing or unrealistic requests/limits are the single most common cause of<br/>noisy-neighbor incidents — a pod without limits can starve every other<br/>workload on its node.|
|Liveness/readiness probes|Missing or misconfigured probes mean Kubernetes cannot tell a hung process<br/>from a healthy one, defeating the platform's own self-healing.|
|Non-root containers|Dockerfiles that run as root by default are a standing privilege-escalation risk if<br/>the container is ever compromised; reviewers should expect an explicit<br/>non-root USER.|
|Image provenance|Is the base image pinned to a digest (not `latest`), from a trusted registry, and<br/>ideally signed and verifiable at admission time via a policy controller?|
|Rollback safety|Does the deployment strategy (rolling update, blue/green, canary) allow a fast,<br/>automated rollback, or does a bad deploy require manual intervention to<br/>reverse?|

### **5.3 CI/CD Pipeline Review**

The pipeline definition itself (GitHub Actions workflows, GitLab CI configs, ArgoCD/Flux application manifests) is code, and increasingly the highest-value target for an attacker, since it often runs with deployment credentials. Review should treat pipeline changes with at least the scrutiny of production application code, and often more, since a compromised pipeline can affect every downstream deployment.

- <sup>Are third-party GitHub Actions pinned by commit SHA rather than a mutable tag or branch name?</sup>

- <sup>Do pipeline runners use ephemeral, isolated environments rather than long-lived shared runners that could</sup> retain secrets or artifacts between jobs?

- <sup>Are deployment credentials scoped per-environment and short-lived (OIDC-based, not long-lived static keys</sup> checked into a secrets store forever)?

- <sup>For GitOps tools (ArgoCD, Flux): does a change to the desired-state repository require the same review rigor as</sup> application code, since merging to that repo is functionally equivalent to deploying?

### **5.4 Zero Trust, RBAC, Cost, and Autoscaling**

- <sup>Zero Trust posture: does this change assume network location implies trust (e.g., "it's fine, it's inside the VPC"),</sup> or does it enforce identity-based verification regardless of network position?

- <sup>RBAC scope creep: does a new cluster role or service account request broader permissions than the workload</sup> actually needs, "to be safe"?

- <sup>Cost review: does a new autoscaling configuration have a sane maximum, or can a traffic spike (or a bug</sup> causing a request loop) scale the infrastructure bill without bound?

- <sup>Autoscaling correctness: are scale-up and scale-down thresholds tuned to avoid flapping (rapid scale up/down</sup> cycles that increase cost and reduce stability without improving capacity)?

## **Section 6 — Database Review**

Database changes are disproportionately dangerous in review because their failure mode is often irreversible or extremely expensive to reverse — unlike application code, which can usually just be rolled back. A database reviewer's default posture is paranoid, and for good reason.

#### **Database Migration Review Checklist**

|**Concern**|**Reviewer Question**|
|---|---|
|Indexes|Does a new query pattern have a supporting index? Conversely, does a<br/>migration drop an index that something still depends on? Index creation on a<br/>large table should default to an online/concurrent build to avoid locking writes.|
|Locks and transactions|Does this migration take a long-held lock on a large, high-traffic table (e.g.,<br/>adding a column with a default value on some database engines can rewrite<br/>the whole table under lock)? Is the transaction scope as narrow as possible?|
|Backward compatibility /<br/>roll-forward-only|Can the application run against both the old and new schema simultaneously<br/>during a rolling deploy? If not, this is a coordinated-deployment risk, not a<br/>routine merge.|
|Rollback strategy|Is there a tested down-migration, or is this a one-way door (e.g., a destructive<br/>column drop) that needs an explicit backup/snapshot step before it runs?|
|Large-table operations|Has the migration been tested against production-scale data volume, not just<br/>a small development database where the same operation completes<br/>instantly?|
|Partitioning and CDC|Does this change interact with existing partitioning strategy or<br/>change-data-capture (CDC) pipelines that downstream systems depend on for<br/>replication or analytics ingestion?|
|Replication lag|For a write-heavy migration, has the reviewer considered the impact on<br/>replication lag to read replicas that other services depend on for read<br/>consistency?|

**The expand/contract pattern** is the standard mitigation for nearly every risk in this table: add the new column/table/index alongside the old one (expand), migrate reads and writes over in a separate, reversible step, then remove the old structure only once nothing references it (contract). A reviewer seeing a migration that tries to do all three steps in a single PR should generally ask for it to be split.

## **Section 7 — API Review (REST, GraphQL, gRPC, Async)**

### **7.1 Cross-Cutting API Concerns**

- <sup>**Contract-first discipline**— was the OpenAPI/protobuf/GraphQL schema change reviewed and agreed before</sup> implementation, or does the schema get generated from whatever the implementation happened to produce (a common source of accidental breaking changes)?

- <sup>**Versioning strategy**— is a breaking change versioned explicitly (new endpoint version, new field deprecation</sup> cycle) rather than mutating the existing contract in place?

- <sup>**Pagination**— does a new list endpoint paginate by default, or does it return an unbounded result set that will</sup> become a performance and cost problem as data grows?

- <sup>**Error model consistency**— does this endpoint's error response follow the same shape (status codes, error</sup> body schema) as the rest of the API, or does it invent a bespoke format that every client now has to special-case?

- <sup>**Idempotency**— for any mutating operation that a client might retry (payments being the canonical example), is</sup> there an idempotency key mechanism so a retried request doesn't double-execute?

- <sup>**Rate limiting**— is this endpoint covered by existing rate-limit policy, or does it bypass it because it's "internal</sup> only" (a classification that has a way of becoming untrue over time)?

- <sup>**Observability**— does this endpoint emit the standard request/latency/error metrics and distributed tracing</sup> spans by default, or will it be invisible in the dashboards until someone notices it's missing during an incident?

### **7.2 By Protocol**

#### **Protocol-Specific Review Focus**

|**Protocol**|**What Reviewers Check**|
|---|---|
|REST / OpenAPI|Reviewer checks the OpenAPI diff for removed fields, changed types, or tightened<br/>validation on existing fields — all of which are breaking even if the endpoint path is<br/>unchanged. Tooling (e.g., openapi-diff style checks) can gate this automatically in<br/>CI.|
|GraphQL|Field deprecation via `@deprecated` rather than removal; N+1 query risk from a<br/>new resolver that doesn't batch/dataload; whether a new field exposes more data<br/>than the client actually needs, widening the effective API surface silently.|
|gRPC / Protobuf|Field number reuse is the classic breaking mistake — removing a field and<br/>reusing its number for something new corrupts data for any client still on the old<br/>schema. Reviewers check that removed fields are reserved, not reused.|
|Async / Event APIs|See Section 3.3 — compatibility mode enforcement via schema registry, and<br/>whether a new consumer needs to handle both old and new event shapes during<br/>a transition window.|

## **Section 8 — Documentation Review**

Documentation review is frequently treated as optional in PR review, which is precisely why it decays. Mature organizations treat a documentation gap the same way they'd treat a missing test: a reason to request changes, not a nice-to-have.

#### **Documentation Review Checklist**

|**Artifact**|**Reviewer Question**|
|---|---|
|README|Does it still accurately describe how to run and test the system after this change,<br/>or does the PR silently make the README wrong?|
|ADRs|Does an architecturally significant change have a corresponding ADR, linked from<br/>the PR description? (See Section 9.)|
|Runbooks / playbooks|For a change that affects on-call response (new failure mode, new alert, changed<br/>rollback procedure), is the runbook updated in the same PR, not as a follow-up<br/>that never happens?|
|Diagrams|Do sequence or architecture diagrams still reflect reality, or is this the change that<br/>makes the diagram lie? Diagrams-as-code (Mermaid, PlantUML) checked into the<br/>same repo as the change they describe age far better than static images<br/>maintained separately.|
|Decision logs / wiki|Is there a single source of truth being updated, or is this creating a second,<br/>soon-to-be-conflicting copy of information that already lives in the wiki?|
|Developer guides|If this PR changes a public interface or a common workflow, does the<br/>onboarding/developer guide for that area need a corresponding update?|

The practical mechanism that makes this stick: a PR template checkbox ("Architecture Impact — has an ADR been created or updated?") costs nothing to add and, per practitioner guidance on ADR adoption, is one of the most effective low-friction ways to keep documentation review from being silently skipped.

## **Section 9 — ADR-Driven Development**

### **9.1 What an ADR Is and Isn't**

An Architecture Decision Record captures a single, architecturally significant decision — the context that made it necessary, the alternatives considered, and the consequences of the choice. The format was popularized by Michael Nygard in 2011 and has since been adopted from startups to national government digital services. The discipline is not the format (several templates compete: Nygard's original Context/Decision/Consequences, MADR, Y-Statements) — it is the habit of writing one down before the decision disappears into a PR nobody will reread.

#### **Minimal Nygard-style template**

```
# ADR-NNNN:
## Status
Proposed | Accepted | Superseded by ADR-XXXX
## Context
What is the problem or requirement forcing this decision?
What constraints (technical, business, team) apply?
## Decision
What are we doing, stated as a clear, single sentence if possible.
## Alternatives Considered
- Option A — pros / cons
- Option B — pros / cons
## Consequences
What becomes easier? What becomes harder? What follow-up
decisions does this create?
```

### **9.2 ADRs Before, During, and After Review**

#### **ADR Lifecycle Touchpoints**

|**Phase**|**Practice**|
|---|---|
|Before coding|An architecturally significant decision — new data store, new external<br/>dependency, a pattern that will be replicated elsewhere — gets an ADR in<br/>Proposed status before implementation starts, so the review of the idea happens<br/>before the review of hundreds of lines of code built on it.|
|During PR review|The reviewer's job shifts from re-litigating the decision to checking conformance:<br/>does the implementation match what the accepted ADR says? A reviewer who<br/>disagrees with the decision itself should reopen the ADR discussion, not block the<br/>PR with a design debate that was supposed to already be settled.|

|**Phase**|**Practice**|
|---|---|
|After merge|Some teams schedule a lightweight after-action review — commonly around one<br/>month later — comparing what the ADR predicted against what actually<br/>happened, closing the loop on whether the decision-making process itself is<br/>improving over time.|

### **9.3 Traceability and Governance**

- <sup>**Append-only, superseded not edited**— once accepted, an ADR is not rewritten; if the decision changes, a</sup> new ADR is written that explicitly supersedes the old one and links back to it, preserving the historical record of why direction shifted.

- <sup>**Central, discoverable storage**— ADRs kept in the same repository as the code they govern (commonly</sup> `docs/adr/`), in a lightweight diffable format (Markdown), so they show up in the same review and search tooling engineers already use.

- <sup>**One decision per record**— an ADR that documents "our entire database strategy" is a design document, not</sup> an ADR; each record should be short enough to read in the 10–15 minutes of a readout-style review meeting.

- <sup>**Confidence level**— recording how confident the team was at decision time (not just what was decided) gives</sup> future readers useful context for whether a decision is due for reconsideration.

### **9.4 Anti-Patterns**

- <sup>ADRs written after the fact purely to satisfy a process checkbox, with alternatives listed that were never</sup> seriously considered — this produces documentation that looks rigorous but carries no real decision-making value.

- <sup>ADRs that never reach Accepted status and pile up as permanent Proposed clutter, which trains the team to</sup> stop reading them.

- <sup>Combining multiple unrelated decisions into a single ADR to save time, producing a document nobody can</sup> cleanly supersede later without also relitigating the unrelated parts.

## **Section 10 — RFC-Driven Engineering**

### **10.1 RFCs vs. ADRs**

Where an ADR records a decision already made, an RFC (Request for Comments) is the mechanism used to reach that decision for anything large enough to need broad, structured input before it's settled. Companies with strong public engineering cultures — including Cloudflare, Stripe, and large parts of Google and Meta's internal process — use RFC-style documents for anything that changes a widely-depended-on system, a public-facing product surface, or an internal platform other teams will build on.

### **10.2 How RFCs Affect PR Review**

#### **RFC Lifecycle and Its Relationship to PR Review**

|**Aspect**|**Practice**|
|---|---|
|Review lifecycle|An RFC typically moves through draft→circulated for comment→revised→<br/>approved by a named decision-maker or review board, with the comment period<br/>being the actual review — not a formality before an already-decided outcome.|
|Ownership|A named owner (often, but not always, the author) is responsible for driving the<br/>RFC to resolution and is the point of contact when a later PR appears to diverge<br/>from what was agreed.|
|Evolution|Once approved, an RFC — like an ADR — is not silently edited; material changes<br/>in direction get a follow-up RFC or an amendment section with a clear date stamp,<br/>preserving why the team believed what it believed at the time.|
|Downstream PR review|PRs implementing an approved RFC are reviewed for conformance to the RFC,<br/>with substantive design disagreement redirected back to an RFC amendment<br/>rather than re-litigated in PR comments — this is what keeps large, cross-team<br/>implementations from getting stuck in endless per-PR debate.|

### **10.3 When to Use an RFC vs. an ADR vs. Neither**

- <sup>**Use an RFC**when the decision affects multiple teams, is not yet settled, and needs broad input before it can be</sup> made — the RFC process itself is the decision-making mechanism.

- <sup>**Use an ADR**when a decision has already been made (by an individual, a small team, or as the outcome of an</sup> RFC) and needs to be recorded for future reference — the ADR process is a record-keeping mechanism, not a debate mechanism.

- <sup>**Use neither**for reversible, low-blast-radius decisions that a competent engineer or small team can make and</sup> adjust without ceremony — over-applying either process to routine decisions is the most common way organizations kill the practice's credibility.

## **About This Series**

This is Volume 2 of a five-part Enterprise PR Review Playbook. Volume 1 covers workflow, ownership models, and role-based review playbooks. Volumes 3 and 4 cover AI-assisted and agentic review architectures. Volume 5 collects case studies, master checklists, and a review maturity model.

*Generated as a synthesized practitioner reference. Standards references (OWASP Top 10:2025, SLSA) reflect the current published versions as of mid-2026; company-specific practices are drawn from public engineering blogs and evolve continuously.*
