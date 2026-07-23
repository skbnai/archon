---
title: "Artifact Catalog & Quality Attributes"
doc_type: reference-architecture
domain: architecture
topic_id: volume4-artifact-catalog-quality-attributes
date_created: 2026-07-23
status: current
last_reviewed: 2026-07-23
covers_version: "N/A"
supersedes:
  - docs/enterprise-architecture/architectural-review-board/Volume4_Artifact_Catalog_Quality_Attributes.md
nav_prev: docs/architecture/62-volume3-knowledge-management-capability-mapping.md
nav_next: docs/architecture/64-volume5-review-questions-scorecards.md
---

# Artifact Catalog & Quality Attributes

Enterprise Architecture Review Board Handbook · Banking & Financial Services Edition

Every artifact an Architecture Review Board should expect to see — purpose, owner, consumers, lifecycle, and automation — paired with a modern quality attribute taxonomy that goes beyond generic NFRs to cover AI explainability, agent reliability, and memory consistency.

## Part A — The Complete Artifact Catalog

An ARB that doesn't have a clear, enforced artifact catalog ends up with wildly inconsistent submission quality. This catalog defines what "good" looks like for every artifact a mature banking ARB should expect across the full lifecycle, from business case through retirement.

### Strategy & Vision Artifacts

Business Case justifies investment with cost, benefit, and risk quantification. Owner is business sponsor; consumers are Executive Steering Committee and Finance. Lifecycle is created at project intake, reviewed at key gates, and retired at project close. Automation is low — fundamentally a judgment artifact, though cost models can pull from FinOps tooling.

Vision Document articulates the desired future state and why it matters strategically. Owner is business sponsor plus Chief Architect jointly; consumers are ARB, delivery teams, broader organization. Automation is none — narrative artifact.

Architecture Vision translates business vision into target architecture direction and guiding principles. Owner is Chief Architect or Lead Solution Architect; consumers are ARB and all contributing architects. Automation is low — references the pattern catalog and reference architectures.

Capability Map traces the initiative to business capabilities affected. Owner is business capability owner plus Enterprise Architect; consumers are ARB and capability redundancy analysis. Automation is medium — generated/updated from the knowledge graph.

### Architecture Description Artifacts

Context Diagram shows the system's boundary and external interactions (C4 Level 1 or equivalent). Automation is medium — can be partially generated from API gateway/service mesh metadata.

Container Diagram shows the major deployable units and their interactions (C4 Level 2). Automation is medium — generatable from infrastructure-as-code definitions.

Deployment Diagram maps the architecture onto physical/cloud infrastructure topology. Automation is high — should be generated directly from IaC rather than hand-drawn, to guarantee accuracy.

Threat Model identifies attack surfaces, threat actors, and mitigations (e.g., STRIDE-based analysis). Automation is medium — threat modeling tools can pre-populate from architecture diagrams, but expert review remains essential.

### Decision & Risk Artifacts

Architecture Decision Record (ADR) captures a single significant decision, its context, options considered, and rationale. Automation is medium — AI-assisted drafting from decision context is increasingly viable.

Risk Register tracks identified architectural and technology risks with likelihood, impact, and mitigation status. Automation is medium — risk scoring can be templated; identification requires human judgment.

Decision Log provides chronological record of all ARB decisions, distinct from individual ADRs — the meeting-level audit trail. Automation is high — should be a direct, automatically timestamped system output, not manually transcribed.

Compliance Matrix maps architecture decisions/controls to specific regulatory requirements. Automation is medium — control-to-regulation mapping can be templated and reused across initiatives in the same regulatory domain.

### Integration & Interface Artifacts

Integration Contract defines the agreed interface, data, and behavioral contract between two systems/teams. Automation is high — contract testing tooling can validate compliance automatically and continuously post-approval.

API Specification is formal, typically OpenAPI/Swagger-based definition of a REST API's structure and behavior. Automation is high — should be the literal source of truth; the gateway and documentation are generated from it, not parallel hand-maintained documents.

AsyncAPI is equivalent specification standard for event-driven/asynchronous interfaces. Automation is high — same principle as API Specification, applied to event schema.

### AI-Specific Artifacts

Prompt Library contains versioned, tested collection of system prompts and prompt templates used in production AI features. Automation is high — should be under version control with the same rigor as code, with automated regression testing against known good/bad outputs.

Memory Policy defines what an AI agent or system remembers across interactions, retention duration, and access boundaries. Automation is low — policy definition is a judgment artifact, though enforcement can be automated.

Agent Specification defines an AI agent's scope of autonomy, available tools/actions, escalation triggers, and human-override mechanisms. Automation is medium — see Volume 7 for the full Agent Specification template.

MCP Tool Contract defines the interface, permissions, and behavioral contract for a tool exposed to AI agents via Model Context Protocol or equivalent. Automation is high — should be machine-validated against actual tool implementation, given the security sensitivity of agent tool access.

A2A Contract defines the interaction protocol and trust boundary between two autonomous AI agents (agent-to-agent). Automation is medium — an emerging artifact type as multi-agent architectures mature.

### Operational & Lifecycle Artifacts

Runbooks provide step-by-step operational procedures for known scenarios (incident response, failover, recovery). Automation is medium — common scenarios can be automated as runbook-as-code (e.g., automated failover scripts), reducing reliance on manual procedure execution under pressure.

Support Model defines who supports the system, escalation tiers, SLAs, and handoff between development and operations. Automation is low — organizational/process artifact.

Retirement Checklist ensures clean, complete decommissioning — data archival/deletion per retention policy, dependency verification, access revocation. Automation is medium — dependency verification can be automated via the knowledge graph; data handling steps require careful manual verification given regulatory consequences.

The Retirement Checklist is, by a wide margin, the most frequently skipped artifact in this catalog — decommissioning rarely has an executive sponsor pushing for rigor the way a new build does, and the consequences of skipping it often surface years later as audit findings or security incidents rather than immediately. Treating Retirement Checklist completion as a mandatory ARB gate, with the same rigor as new-build approval, is one of the highest-leverage low-cost governance improvements available.

## Part B — Architecture Quality Attributes

Generic non-functional requirements ("the system should be fast and secure") are useless as governance criteria because they aren't testable. This part defines twenty-one quality attributes with banking-relevant, testable framing for each — including seven AI/agent-specific attributes that don't appear in pre-2023 architecture references and that most ARB charters still haven't formally incorporated.

### Classic Quality Attributes

**Performance.** Response time, throughput, and resource utilization under specified load, expressed as percentiles (p50/p95/p99), not averages. Peak-period scenarios (month-end, year-end, market-open) often dominate, not steady-state averages.

**Availability.** Uptime percentage with explicit measurement window and what counts as "down" (full outage vs. degraded). Payment and trading systems frequently carry contractual or regulatory availability SLAs distinct from generic best-effort targets.

**Scalability.** Defined scaling dimension (users, transactions, data volume) and the mechanism (horizontal/vertical) with concrete headroom targets. Should explicitly address both gradual growth and sudden demand spikes (e.g., a viral product launch or market event).

**Security.** Specific control objectives (authentication, authorization, encryption at rest/in transit, audit logging) mapped to a recognized framework (NIST, ISO 27001). Must explicitly address regulatory-driven controls (PCI-DSS for payments, data residency for cross-border operations).

**Privacy.** Data minimization, purpose limitation, and subject rights (access, deletion, portability) as concrete, testable controls. GDPR and equivalent regimes impose specific, auditable obligations distinct from general security posture.

**Maintainability.** Mean time to implement a defined class of change, code complexity metrics, test coverage thresholds. Particularly material for core banking systems with multi-decade expected lifespans.

**Operability.** Ease of routine operation — deployment frequency achievable, monitoring/alerting completeness, runbook coverage. Should be assessed against the Support Model artifact at review time, not assumed.

**Deployability.** Deployment frequency achievable, rollback time, blast radius of a failed deployment. Banking change-freeze windows constrain this and should be designed around explicitly.

**Observability.** Coverage of metrics, logs, and traces sufficient to diagnose an unknown failure mode without code changes. Increasingly a regulatory expectation itself — operational resilience regimes expect demonstrable real-time visibility into critical system health.

**Recoverability.** Recovery Time Objective (RTO) and Recovery Point Objective (RPO), tested via actual recovery drills, not just documented targets. Subject to formal regulatory testing requirements in many jurisdictions.

**Auditability.** Completeness and tamper-evidence of the audit trail for a defined set of sensitive actions. A first-class design requirement in banking, not an afterthought.

**Compliance.** Explicit mapping to applicable regulations with control evidence. Should be assessed per-jurisdiction for multi-jurisdiction banks, since requirements diverge materially.

**Portability.** Effort required to move the system to a different infrastructure provider or environment. Directly relevant to vendor-concentration risk management.

**Usability.** Task completion rate and time-on-task for defined user journeys, typically measured via usability testing. Customer-facing and internal operations/back-office usability are both relevant and frequently under-prioritized for the latter.

### AI & Agent-Specific Quality Attributes

**AI Explainability.** Ability to produce a human-understandable rationale for a specific AI-driven decision, at a level of detail proportionate to the decision's stakes. Credit decisioning and similar high-stakes AI use cases typically face explicit regulatory explainability requirements that constrain model architecture choices.

**AI Fairness.** Measured outcome parity across protected/relevant demographic groups against defined fairness metrics (demographic parity, equalized odds, etc., chosen deliberately since these metrics can conflict with each other). Fair lending regulatory regimes impose specific obligations; the choice of fairness metric itself should be a documented, defensible decision.

**AI Robustness.** Performance degradation under adversarial input, distribution shift, or edge cases, tested via deliberate red-teaming and stress testing. Fraud detection and similar adversarial-environment AI use cases face active, adaptive adversaries, unlike most traditional software quality attributes.

**Safety.** Bounded worst-case behavior — what is the AI system structurally prevented from doing, regardless of input or failure mode. Should be addressed through architectural constraints (tool permission scoping, action approval gates) rather than relying solely on model behavior, which cannot be guaranteed with certainty.

**Trustworthiness.** A composite, harder-to-test attribute combining calibrated confidence (the system's stated confidence matches its actual accuracy) with consistent behavior over time. Increasingly a named requirement in AI governance frameworks even where not yet precisely testable.

**Agent Reliability.** Task completion rate for defined agent workflows, including graceful failure and appropriate escalation when the agent cannot complete a task, rather than silent failure or fabricated success. Particularly critical where agents take real-world actions (initiating payments, modifying records) rather than only generating text.

**Memory Consistency.** An AI agent's recalled context/memory remains accurate and internally consistent across a session and across sessions where persistence is intended. A novel attribute with essentially no pre-2023 precedent; testing methodology is still maturing across the industry.

### Resolving Quality Attribute Trade-offs

Many of these attributes are in direct tension — Security and Usability frequently trade off against each other; Performance and Auditability can conflict when comprehensive audit logging adds latency; AI Explainability and raw model performance often trade off, since the most explainable model architectures aren't always the most accurate ones.

For any architecturally significant initiative, require an explicit statement of which quality attributes were deliberately prioritized and which were consciously deprioritized, with rationale — rather than a checklist where every attribute is rated "addressed." A design that explicitly says "we are accepting reduced AI Explainability in exchange for materially better fraud detection accuracy, because [rationale], and this trade-off has been reviewed by [Responsible AI Council]" is far more defensible under audit.
