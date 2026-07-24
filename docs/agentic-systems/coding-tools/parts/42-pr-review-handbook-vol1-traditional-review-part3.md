---
title: 'THE ENTERPRISE PR REVIEW PLAYBOOK (Part 3)'
doc_type: guide
domain: agentic-systems
topic_id: pr-review-handbook-vol1-traditional-review-part3
status: current
date_created: 2026-07-24
last_reviewed: 2026-07-24
supersedes: []
---

**This is Part 3 of 3. [Back to Part 2 ←](pathname:///archon/agentic-systems/coding-tools/parts/42-pr-review-handbook-vol1-traditional-review-part2) | [To Part 1 ←](pathname:///archon/agentic-systems/coding-tools/42-pr-review-handbook-vol1-traditional-review)**

## **Section 13 — PR Metrics: DORA, SPACE, and Review Health** (continued)

### **13.2 SPACE Framework**

Where DORA measures delivery outcomes, the SPACE framework (from Microsoft Research, GitHub, and academic collaborators) is designed to capture developer productivity more holistically, explicitly warning against optimizing on any single dimension — including review-specific ones — in isolation.

- **Satisfaction and well-being** — do engineers find the review process fair and useful, or a source of dread and delay.

- **Performance** — outcome-based, not activity-based; a PR merged fast that causes an incident is not high performance.

- **Activity** — volume of PRs, commits, reviews completed; useful as a leading indicator, dangerous as a target in itself (Goodhart's Law applies directly to "number of reviews done").

- **Communication and collaboration** — quality of review discussion, cross-team review participation, knowledge transfer happening through comments.

- **Efficiency and flow** — how much a developer's work is interrupted by context-switching while waiting on review, which stacked-PR and merge-queue tooling directly targets.

### **13.3 Review-Specific Metrics**

#### **Operational Review Metrics**

|**Review Question**|**Why It Matters**|
|---|---|
|Review latency (time to first review)|The clock from PR-opened to first human comment. Google's internal norm is measured in hours, not days; organizations with multi-day review latency should treat it as a top-tier engineering-productivity problem, not a personnel issue.|
|Time to merge|PR-opened to merged. Distinct from review latency — a PR can get fast first feedback and still take days to merge through review-comment cycles.|
|Review depth / comment density|Comments per line changed, tracked as a trend rather than an absolute target; a sudden drop across an org is a leading indicator of LGTM-without-review culture.|
|Defect escape rate|Bugs found in production that should have been caught in review, typically traced back via incident postmortems to a specific PR and reviewer chain.|
|Post-deployment incident rate|Incidents per N deployments, segmented by PR size and review depth where possible — this is the metric that closes the loop on whether review is actually working, as opposed to merely happening.|
|PR size distribution|Median and p90 lines changed per PR; a rising p90 over time is an early warning that trunk-based/small-PR discipline is eroding.|

**A caution on all of the above:** every metric in this section degrades once it becomes a target used to evaluate individual engineers rather than a signal used to improve the system. Review latency measured to reward the fastest approver produces LGTM-without-review; comment density used to reward "thorough" reviewers produces nitpicking on trivial PRs while missing real issues. Treat these as organizational health indicators, reviewed in aggregate and in trend, not as individual performance targets.

## **About This Series**

This volume is part of a five-part Enterprise PR Review Playbook. Volume 2 covers deep domain review — architecture, security, infrastructure, database, API, and documentation review in practitioner-level detail. Volumes 3 and 4 cover AI-assisted and agentic review architectures. Volume 5 collects case studies, master checklists, and a review maturity model for enterprise adoption.

*Generated as a synthesized practitioner reference. Company-specific claims are drawn from public engineering blogs, official documentation, and published research current as of mid-2026; internal practices at any given company evolve continuously and specific tooling names may change.*
