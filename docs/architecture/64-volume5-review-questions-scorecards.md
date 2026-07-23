---
title: "Enterprise Review Questions & Scorecards"
doc_type: reference-architecture
domain: architecture
topic_id: volume5-review-questions-scorecards
date_created: 2026-07-23
status: current
last_reviewed: 2026-07-23
covers_version: "N/A"
supersedes:
  - docs/enterprise-architecture/architectural-review-board/Volume5_Review_Questions_Scorecards.md
nav_prev: docs/architecture/63-volume4-artifact-catalog-quality-attributes.md
nav_next: docs/architecture/65-volume6-banking-industry-deepdive.md
---

# Enterprise Review Questions & Scorecards

A structured question bank across seventeen review domains, plus the scorecards that turn review answers into consistent, auditable approval decisions.

Enterprise Architecture Review Board Handbook · Banking & Financial Services Edition

## Part A — Review Question Bank, Domains 1-9

This question bank is organized by domain rather than presented as one undifferentiated list, because the right questions to ask depend heavily on what's actually being reviewed.

**Business Domain.** What business capability does this initiative serve, and is there an existing system already serving it? Surfaces capability redundancy before investment is committed. Expected answer: a specific capability map reference, with explicit acknowledgment of any overlapping existing systems and rationale for why a new build is still warranted. Red flags: "We didn't check" or a capability map reference that doesn't exist.

What is the quantified cost of delay if this is not approved this cycle? Forces economic rigor into the prioritization conversation. Expected answer: a CD3-style calculation or equivalent, with underlying assumptions visible. Red flags: "It's urgent" with no supporting calculation; cost of delay that conveniently equals exactly the requested budget.

Additional questions: Who is the accountable business sponsor? What is the expected business value, and how will it be measured? Does this duplicate another in-flight initiative? What is the minimum viable scope? Has the business case been validated against actual customer research? What happens to current manual processes?

**Architecture Domain.** What architectural pattern does this follow, and why was it chosen over alternatives? Tests whether the design is deliberate or accidental. Expected answer: a named pattern with explicit reference to the trade-off analysis that led to its selection. Red flags: "This is just how we always build things" with no comparison to alternatives.

Extended questions: What are the system's bounded context boundaries? What existing reference architecture does this conform to? What is the blast radius if a core component fails? How does this architecture handle backward/forward compatibility? What architectural debt is this introducing? Is the architecture coupled to a specific vendor?

**Security Domain.** Walk through the authentication and authorization model end to end. Authentication/authorization gaps are among the most common and most severe findings; a verbal walkthrough surfaces gaps a document review alone often misses. Expected answer: clear description of identity provider integration, token handling, and authorization enforcement points. Red flags: authorization logic embedded inconsistently across multiple services rather than centrally enforced; reliance on network-perimeter security as the sole control.

Extended questions: What is the data classification? How is encryption key management handled? What is the threat model? What third-party/vendor components are in the security-critical path? How are secrets managed? What logging and monitoring coverage exists? How does this handle credential compromise? Has penetration testing been performed?

**Cloud Domain.** Which cloud regions/availability zones does this deploy to? Does that satisfy resilience and data residency requirements? Has this been reviewed by the Cloud Center of Excellence against current landing zone standards? What is the auto-scaling configuration? Is this architecture portable across cloud providers? What is the disaster recovery architecture and what are the tested RTO/RPO figures? How are cloud costs projected to scale? What native cloud security services are leveraged?

**Data Domain.** Who is the data owner? Has the Data Governance Council reviewed the data classification? What is the data lineage? What is the data retention policy? Does this introduce a new copy of an existing golden-source data set? What is the data quality validation approach? How is personally identifiable information (PII) handled? What is the master data management approach?

**AI Domain.** What specific model(s) are used, and why? What is the fallback behavior? Has this been reviewed by the AI Governance Board, Responsible AI Council, and/or Model Risk Committee? What is the explainability approach? How is model drift monitored? What data was the model trained on? What is the human-in-the-loop design? How is hallucination risk mitigated? What is the cost-per-interaction at scale?

**Platform Domain.** Does this use existing platform golden paths? What platform SLAs is this dependent on? Is this introducing a new shared platform capability? What is the deployment pipeline?

**Operations Domain.** Is there a completed Support Model artifact, and has the operations team accepted it? What is the on-call escalation path? What runbooks exist for known failure scenarios, and have they been tested? What is the expected operational toil?

**Compliance Domain.** What specific regulations apply? Is there a completed Compliance Matrix? Has Legal/Compliance formally reviewed and signed off? What audit evidence will this produce? Does this cross jurisdictional boundaries?

## Part B — Review Question Bank, Domains 10-17, & Scorecards

**FinOps Domain.** What is the projected monthly run cost at current scale, and at 3x and 10x scale? Has the architecture been reviewed against committed/reserved capacity options? Who owns the cost center? What cost-monitoring alerts are configured?

**Vendor Domain.** What is the vendor's financial stability? What is the contractual exit/migration path? Does this vendor meet third-party risk management requirements? What data does the vendor have access to? Is there meaningful vendor lock-in?

**Agent Domain.** Is there a completed Agent Specification defining scope of autonomy and tool access? What actions can this agent take without human approval? How does the agent handle tasks it cannot complete? What is the audit trail for autonomous actions?

**Memory Domain.** What does this AI system remember across interactions? Is there a documented Memory Policy? How long is memory retained? Can users request their stored memory be reviewed or deleted? What happens if memory becomes stale?

**MCP Domain.** What tools are exposed via MCP to AI agents? Is there a completed MCP Tool Contract for each? What is the permission scope? How is the MCP server itself secured?

**A2A Domain.** Is there a completed A2A Contract defining trust boundary? What prevents a compromised agent from propagating bad actions? Is there a circuit breaker or rate limit? How is communication authenticated?

**Networking Domain.** What network segmentation is applied? What is the latency budget? How is network traffic encrypted? What is the resilience to network partition?

**Identity Domain.** What identity provider is used? How are service-to-service identities managed? What is the process for de-provisioning access? Is privileged access separately controlled?

**Runtime Domain.** What is the runtime environment's patch and vulnerability management process? How does the architecture handle a runtime dependency reaching end-of-life? What container/runtime image provenance process exists?

## Architecture Scorecards

Scorecards convert review answers into consistent, auditable approval decisions. Scorecard structure includes metrics (specific, measurable indicators), thresholds (pass/conditional-pass/fail boundaries), weighting (relative importance), approval criteria, and automation (which metrics can be automatically sourced).

**Business Scorecard.** Quantified business value (NPV) 30% weight; Capability redundancy check 20%; Sponsor accountability 15%; Benefits realization plan 20%; Strategic alignment 15%. Metrics are semi-automated or manual.

**Architecture Scorecard.** Reference architecture conformance 25% weight; Quality attribute coverage 30%; ADR completeness 20%; Technical debt introduced 15%; Pattern catalog alignment 10%. Metrics are semi-automated to manual.

**Security Scorecard.** Threat model completion 25% weight; Vulnerability scan results 20%; Authentication/authorization model 25%; Encryption coverage 15%; Penetration test status 15%. Metrics are fully automated to manual.

**AI/Responsible AI Scorecard.** Fairness testing 20% weight; Explainability requirement 20%; Human-in-the-loop design 20%; Model risk validation 20%; Cost-at-scale modeling 10%; Drift monitoring 10%. Metrics are semi-automated.

A composite passing score should never override a hard-fail on a single non-negotiable metric (e.g., an unmitigated critical security vulnerability). Mature scorecard designs distinguish weighted/compensatory metrics from gate metrics that cannot be averaged away.
