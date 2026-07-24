---
title: 'THE ENTERPRISE PR REVIEW PLAYBOOK (Part 1)'
doc_type: guide
domain: agentic-systems
topic_id: pr-review-handbook-vol1-traditional-review
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - ../knowledge-docs/docs/coding-tools/code-review/PR_Review_Handbook_Vol1_Traditional_Review.md
---
# THE ENTERPRISE PR REVIEW PLAYBOOK
Volume I — Traditional Review Discipline

How Pull Requests Actually Flow Through Elite Engineering Organizations — Workflow, Ownership, Role-Based Review Playbooks, Anti-Patterns, and Metrics

A practitioner-level reference synthesized from published engineering practices at Google, Meta, Microsoft, Netflix, Amazon, Uber, Airbnb, Stripe, Shopify, LinkedIn, Datadog, and Cloudflare, plus DORA/SPACE research and open-source tooling documentation.

Series: 5 Volumes · Volume 1 of 5 July 2026

## **Contents**

How to Use This Series

Section 1 — How PR Review Works in Elite Engineering Organizations

1.1 The canonical pipeline: developer to production

1.2 Ownership models and CODEOWNERS

1.3 Company-by-company review culture

1.4 Merge queues, stacked PRs, and trunk-based development

1.5 Monorepo vs. polyrepo review dynamics

Section 2 — Role-Based Review Playbooks

2.1 Junior Developer 2.2 Senior Developer 2.3 Staff Engineer

2.4 Principal Engineer / Distinguished Engineer

2.5 Enterprise Architect 2.6 Security Architect 2.7 Platform Engineer 2.8 Site Reliability Engineer (SRE)

2.9 QA Engineer 2.10 Data Engineer 2.11 AI Engineer 2.12 AI Architect

Section 12 — Review Anti-Patterns Catalog

Section 13 — PR Metrics: DORA, SPACE, and Review Health

About This Series

## **How to Use This Series**

This is Volume 1 of a five-part reference on how pull requests are actually reviewed inside high-performing engineering organizations, covering both the traditional human review discipline and — in later volumes — the emerging discipline of AI-assisted and agentic review.

Volume 1 focuses on **mechanics and human judgment** : how PRs physically move through an organization, what each reviewing role is actually looking for, the failure modes that recur across companies regardless of tooling, and the metrics organizations use to know whether review is working. It is written for engineers who already know how to open a pull request and want to understand the judgment layer that sits on top of the mechanics — the difference between a reviewer who checks syntax and one who protects a system's future.

##### **Companion volumes in this series:**

- <sup>**Volume 2**— Deep domain reviews: architecture/ADR/RFC discipline, security review, infrastructure-as-code,</sup> database migrations, API contracts, documentation review.

- <sup>**Volume 3**— AI-assisted review today: Copilot, Claude Code, Cursor, CodeRabbit, Greptile, Graphite, Amazon</sup> Q — capabilities, failure modes, and where human oversight remains non-negotiable.

- <sup>**Volume 4**— Agentic AI review architecture: multi-agent reviewer design, MCP/A2A orchestration, policy</sup> engines, and governance for autonomous review pipelines.

- <sup>**Volume 5**— Case studies, master checklists, scorecards, and a review maturity model.</sup>

*A note on sourcing:* claims about specific companies are drawn from published engineering blogs, the *Software Engineering at Google* book, conference talks, and vendor documentation where available, and are marked as such. Where a practice is common but not tied to a single public source, it is presented as general industry practice rather than attributed to a specific company.

**Section 1 — How PR Review Works in Elite Engineering Organizations**

### **1.1 The Canonical Pipeline**

Beneath the surface differences in tooling, nearly every mature engineering organization runs pull requests through the same conceptual pipeline. What differs is which stages are automated, which are mandatory, and how much human judgment is layered on top of each gate.

- <sup>**Author self-review**— the developer re-reads their own diff before requesting review; at Google this is</sup> supported by presubmit checks run inside the review tool itself before a human ever sees the change.

- <sup>**Continuous Integration**— build, unit tests, linting, type-checking; a change that fails CI is not eligible for</sup> human review time in almost every serious organization.

- <sup>**Static analysis / SAST**— automated analyzers annotate the diff directly; Google's internal analyzer ecosystem</sup> (historically Tricorder) surfaces findings inline in the review tool, and reviewers can mark a finding "please fix" or "not useful" to tune the signal over time.

- <sup>**Security scanning**— secrets detection, dependency/SCA scanning, and for sensitive paths, a human security</sup> reviewer.

- <sup>**Architecture / design conformance**— for changes that touch a system boundary, a check against an existing</sup> ADR/RFC or a request for one to be written.

- <sup>**Owner review**— the human decision point: does someone with context and authority over this code agree the</sup> change should exist in this form?

- <sup>**Merge**— via direct merge, merge queue, or stacked-PR cascade depending on org maturity.</sup>

- <sup>**Deployment**— progressive rollout (canary, staged, feature-flagged) rather than a single big-bang release.</sup>

- <sup>**Post-deployment validation**— SLO dashboards, automated rollback triggers, and in the best organizations,</sup> an explicit "bake time" before a change is considered safe.

The single biggest structural difference between elite and average organizations is not the presence of these stages — most companies have all of them on paper — it is how much is enforced by tooling versus left to reviewer discipline, and how fast the loop runs. Google's internal data, reported in *Software Engineering at Google* , put the median time for a change to receive its first review at roughly four hours, with small changes reviewed within about an hour and larger ones within about five — fast enough that review is not experienced as a queueing system.

### **1.2 Ownership Models and CODEOWNERS**

Two philosophies dominate how organizations decide who is allowed to approve a change.

#### **Explicit path-based ownership (CODEOWNERS)**

GitHub, GitLab, and most polyrepo shops use a CODEOWNERS file mapping directory globs to teams or individuals. A PR touching `/payments/**` automatically requests review from the payments team and, depending on branch protection settings, cannot merge without their sign-off. This scales well in polyrepo or modular-monorepo setups but tends to fragment as an organization grows — stale CODEOWNERS files listing

people who have left the team are one of the most common sources of review latency in mid-size companies.

#### **Certification-based ownership (Google's readability model)**

Google's model, described extensively in its public engineering practices documentation, decouples "do you own this directory" from "are you qualified to approve this language's style and idiom." Every changelist requires approval from someone with **readability certification** in the language being changed — a credential earned through a structured review-of-reviews process, obtained once per language and then held for the engineer's tenure. Combined with an ownership requirement for the specific code area, this is why Google can run on a single-approver norm at enormous scale: the certification substitutes for having many senior people re-litigate style on every review.

Most organizations outside Google use a hybrid: CODEOWNERS for domain authority, plus informal or semi-formal recognition ("senior engineer," "tech lead") for judgment authority, without a structured certification process.

### **1.3 Company-by-Company Review Culture**

#### **Representative Review Cultures**

|**Review Question**|**Why It Matters**|
|---|---|
|Google|Single-approver norm (ownership + readability). Reviews run through Critique,<br/>Google's internal tool, with inline static-analysis findings, an "attention set"<br/>mechanism showing whose turn it is to act, and a stated cultural goal of<br/>same-day turnaround.|
|Meta|Heavy internal tooling (Phabricator historically, now largely internal successors)<br/>with stacked-diff workflows as the default rather than the exception — Meta's<br/>Sapling source control system was built specifically to make stacked, iterative<br/>review the natural way of working.|
|Microsoft|More heterogeneous than Google's monoculture; a mix of tool-driven review and<br/>over-the-shoulder / pairing-style review is explicitly sanctioned, reflecting<br/>Microsoft's more federated engineering culture across product groups.|
|Netflix, Stripe, Shopify,<br/>Airbnb, Uber, LinkedIn,<br/>Datadog, Cloudflare|Broadly converge on GitHub/GitLab-based review with required<br/>CODEOWNERS approval, CI gating, and increasing adoption of merge queues;<br/>these companies are also the primary commercial adopters and case studies<br/>behind stacked-PR tooling such as Graphite, reflecting a shared pain point of<br/>large-PR review latency in fast-growing product organizations.|

*Sourced from public engineering blogs, the Software Engineering at Google book, and vendor case-study material; treat company-specific claims as illustrative of broad practice rather than a verbatim account of any single team's current process, which evolves continuously.*

### **1.4 Merge Queues, Stacked PRs, and Trunk-Based Development**

As PR volume grows, two related but distinct problems emerge: (1) large, long-lived branches produce painful, low-quality reviews, and (2) even well-reviewed PRs collide with each other at merge time, producing "semantic" conflicts that pass CI individually but break trunk in combination.

#### **Trunk-based development**

The practice of merging small, frequent changes directly into a shared trunk (often behind feature flags for anything incomplete) rather than maintaining long-lived feature branches. It is the precondition for everything else in this subsection — a team cannot productively adopt merge queues or stacking without first being comfortable with short-lived branches and rapid integration.

#### **Stacked pull requests**

Rather than one large PR, an engineer decomposes a feature into a sequence of small, dependent PRs, each branched from the previous one. Each layer is independently reviewable and mergeable; a reviewer can approve the bottom of the stack while the top is still being iterated on. Tools purpose-built for this — Graphite, Meta's Sapling, and lighter-weight open-source tools like ghstack and stack-pr — automate the tedious part: when an early PR in the stack changes, every dependent PR above it must be rebased, and doing this by hand is where manual stacking breaks down. Graphite's own guidance to teams adopting stacking recommends keeping PRs under roughly 200 lines and targeting sub-24-hour review turnaround as the concrete standards that make the workflow pay off.

#### **Merge queues**

A merge queue serializes the final integration step: PRs approved for merge enter a queue, are rebased onto the latest trunk, re-validated by CI, and merged in order — preventing the situation where two individually-safe PRs combine into a broken trunk. Stack-aware merge queues (Graphite's is the most prominent example) go further, validating and fast-forwarding an entire approved stack together rather than serializing every layer through CI individually, which matters once a team is merging dozens of stacked PRs a day.

### **1.5 Monorepo vs. Polyrepo Review Dynamics**

#### **Monorepo vs. Polyrepo — What Changes for the Reviewer**

|**Review Question**|**Why It Matters**|
|---|---|
|Blast radius visibility|Monorepo reviewers can see every downstream consumer of a changed<br/>interface in the same review; polyrepo reviewers often cannot see consumers at<br/>all without cross-repo tooling or a service catalog.|
|Ownership enforcement|Monorepos need path-based CODEOWNERS at massive scale (Google's is<br/>famous for this); polyrepos get ownership "for free" from repo boundaries but<br/>lose cross-cutting visibility.|
|CI cost and selectivity|Monorepo CI must be smart about only building/testing affected targets<br/>(Bazel-style dependency graphs); polyrepo CI is naturally scoped but duplicated<br/>across repos.|
|Cross-cutting refactors|Trivial in a monorepo (one PR touches everything); in polyrepo, a breaking API<br/>change requires coordinated, sequenced PRs across many repos and often a<br/>deprecation period enforced by contract testing.|

## **Section 2 — Role-Based Review Playbooks**

The same diff produces a different review depending on who is reading it. A junior developer and a principal engineer looking at the identical PR are running different mental models — not because one is more careful, but because they are optimizing for different failure modes. This section documents, role by role, what an experienced person in that seat is actually looking for, what they deliberately let go, and what they say when something is wrong.

#### **2.1 Junior Developer**

|**What they review**|Correctness of the immediate change; does the code do what the description<br/>says; obvious null/boundary bugs; whether tests exist and pass; adherence to<br/>visible style conventions.|
|---|---|
|**What they deliberately**<br/>**ignore**|Whether this is the right architectural approach at all; long-term maintainability;<br/>whether this duplicates logic that exists elsewhere in a part of the codebase they<br/>haven't seen.|
|**Questions they ask**|"Does this match the ticket?" "Did I break any existing tests?" "Is there an example<br/>elsewhere in the codebase I should follow?"|
|**Approval criteria**|Tests pass, the diff matches the stated intent, and a more senior reviewer has<br/>also looked at it — junior review is rarely the last gate on anything consequential.|
|**Common comments**|"Nit: variable name could be clearer." "Should this have a test for the empty-list<br/>case?" "I don't understand what this line does — can you add a comment?"|
|**Anti-patterns they flag**|Rubber-stamping because the CI is green; reviewing only the lines that changed<br/>and never opening the surrounding file for context.|

#### **2.2 Senior Developer**

|**What they review**|Correctness plus local design: is this the right abstraction for this file/module; error<br/>handling completeness; test coverage of edge cases and failure paths; whether<br/>the change respects existing module boundaries.|
|---|---|
|**What they deliberately**<br/>**ignore**|Broader system architecture debates that belong in a design doc, not a PR<br/>comment; micro-style issues already caught by linters.|
|**Questions they ask**|"What happens when this call fails?" "Is this concurrency-safe?" "Why this<br/>approach instead of [alternative]?" "Does this need a migration plan for existing<br/>data?"|
|**Approval criteria**|The change is correct, tested, and consistent with the module's existing patterns;<br/>any deviation from convention is deliberate and justified in the PR description, not<br/>accidental.|
|**Common comments**|"This will race under concurrent access — see line X." "Can we extract this into a<br/>shared utility instead of duplicating it?" "This needs a test for the timeout case."|
|**Anti-patterns they flag**|Approving because "it looks like the surrounding code" without checking whether<br/>the surrounding code is itself a known problem; nitpicking style while missing a<br/>logic error.|

#### **2.3 Staff Engineer**

|**What they review**|Cross-team and cross-service impact; whether the change introduces coupling<br/>that will be expensive to unwind later; consistency with architectural direction the<br/>org has committed to; whether the change is the right size (should this be split, or<br/>does it belong in a bigger redesign).|
|---|---|
|**What they deliberately**<br/>**ignore**|Line-by-line style; test naming conventions; anything already enforced by CI.|
|**Questions they ask**|"Who else consumes this interface, and did they get a heads-up?" "Does this<br/>quietly become load-bearing infrastructure that nobody signed up to own?" "Is<br/>there a simpler way to get 80% of the value?"|
|**Approval criteria**|The change is technically sound_and_organizationally sound — it doesn't create a<br/>surprise dependency, doesn't silently expand another team's on-call surface, and<br/>is proportionate to the problem.|
|**Common comments**|"This creates a hard dependency from team A to team B's internal data model —<br/>can we go through the public API instead?" "This PR is doing three unrelated<br/>things; can we split it?"|
|**Anti-patterns they flag**|Blocking a reasonable PR to relitigate an architecture decision that was already<br/>made in an ADR; over-engineering a simple change because of hypothetical<br/>future scale.|

#### **2.4 Principal / Distinguished Engineer**

|**What they review**|Strategic fit: does this move the system toward or away from where the<br/>organization is trying to go; second-order consequences (what does this make<br/>easier or harder to do next); whether this is solving the real problem or a<br/>symptom; organizational risk (does this quietly become a single point of failure or<br/>a key-person dependency).|
|---|---|
|**What they deliberately**<br/>**ignore**|Implementation detail that a competent staff engineer has already covered;<br/>anything that is purely a matter of team preference.|
|**Questions they ask**|"What does this foreclose?" "If this succeeds, what do we build next on top of it,<br/>and does this design support that?" "Is this the right layer for this decision, or are<br/>we solving an organizational problem with a technical one?"|
|**Approval criteria**|The change is defensible not just today but as a precedent — other teams will<br/>point to this PR as "how we do X here." Principal-level approval is often about<br/>setting a pattern, not just clearing a diff.|

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/coding-tools/parts/42-pr-review-handbook-vol1-traditional-review-part2) for continued content.**
