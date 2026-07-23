---
title: "Best Practices & Jargon Guide"
doc_type: guide
domain: architecture
topic_id: ea-bestpractices-jargon
date_created: 2026-07-23
status: current
last_reviewed: 2026-07-23
covers_version: "N/A"
supersedes:
  - docs/enterprise-architecture/best-practices/EA_BestPractices_Jargon.md
---

# Best Practices & Jargon Guide

Pitch to Retire — Terminology, Standards & Golden Rules

The definitive reference guide for EA practitioners, business stakeholders, and delivery teams. Part 1 covers the 20 EA Golden Rules. Part 2 is an A–Z jargon buster of 60+ enterprise architecture terms, acronyms, and frameworks used across the full capability lifecycle.

## Part 1 — The 20 EA Golden Rules

These twenty principles represent the distilled best practices of enterprise architecture across strategy, governance, delivery, and portfolio management.

### 1. Architecture Is an Enabling Function, Not a Gatekeeper

The EA exists to accelerate value delivery, not to slow it down. Every governance process must add more value than the friction it creates. If your ARB is seen as a bureaucratic blocker, the architecture function has failed.

Make governance fast, transparent, and outcome-focused. Publish architecture principles and standards so teams can self-serve. Measure EA value by business outcomes, not documents produced. Don't make the ARB a committee that exists to say no.

### 2. Never Approve a Solution Before Understanding the Problem

The most expensive architectural mistakes begin when a sponsor arrives with a pre-chosen solution and EA rubber-stamps it. The pitch stage exists to validate the problem, not to confirm the sponsor's preferred answer.

Always start with a problem statement signed off by the sponsor. Challenge solution assumptions respectfully and with data. Run the build/buy/reuse assessment before any technology is selected.

### 3. Technical Debt Is a Business Risk — Treat It as One

Technical debt is not a technical problem. It is a business liability that compounds over time, reducing agility, increasing risk, and raising operating costs. The EA must make debt visible to business leaders in business language.

Maintain a technical debt register with business impact scores. Present debt as risk-adjusted cost in every portfolio review. Set a debt reduction target as a formal KPI (e.g. 10% per quarter).

### 4. Every Architecture Decision Must Have a Record

Architecture Decision Records (ADRs) are the institutional memory of the organisation's technology choices. Without them, the same debates happen repeatedly and institutional knowledge walks out the door with departing staff.

Write ADRs in plain language: context, options, decision, consequences. Publish ADRs in a shared, searchable repository accessible to all engineers. Review ADRs at each annual rationalisation cycle.

### 5. Standards Must Be Enforced, Not Just Published

A technology standard that is not enforced is a wish list. Governance without teeth creates the illusion of control while architectural sprawl continues unchecked. Enforcement must be automated wherever possible.

Implement architecture fitness functions in delivery pipelines. Include standards compliance in the pre-production sign-off gate. Track and report the architecture adoption rate as a KPI.

### 6. Design for the Organisation You Are Becoming, Not the One You Are

The architecture must support the organisation's strategic trajectory, not just its current state. A three-to-five year architecture roadmap grounded in strategic themes prevents constant reactive rebuilding.

Maintain a 1/3/5 year architecture roadmap aligned to corporate strategy. Review and recalibrate roadmaps quarterly, not just annually. Map all major initiatives to at least one strategic theme.

### 7. Build/Buy/Reuse — In That Order of Scrutiny

Before committing to a build or a buy, the EA must genuinely explore reuse. The most sustainable architectures are built on a lean portfolio of well-used platforms, not a collection of specialist point solutions.

Check the existing portfolio before every intake assessment. Challenge vendor selections with a reuse analysis. Track and reduce the number of duplicate capabilities in the portfolio.

### 8. Non-Functional Requirements Are Not Optional

NFRs define the quality of the system, not just its features. An application that works but fails under load, cannot be recovered in an incident, or leaks data is a liability, not an asset.

Define availability, RTO, RPO, performance, and scalability at design time. Make NFR testing mandatory for every pre-production gate. Tier NFRs by system criticality.

### 9. The 30% Review Is Your Most Cost-Effective Governance Investment

A structural architectural mistake caught at 30% of delivery costs a fraction of what it costs at 90% or in production. The 30% architecture review is not a status update — it is a diagnostic intervention.

Schedule the 30% review as a mandatory delivery milestone. Focus on structural decisions: system boundaries, integration patterns, data ownership. Document findings as formal exceptions requiring resolution before 70% gate.

### 10. Observability Is Architecture, Not an Afterthought

A system you cannot see is a system you cannot manage. Logging, monitoring, alerting, and distributed tracing must be designed in from the start and validated before any system enters production.

Include observability requirements in the SAD as a mandatory NFR. Validate the observability stack in the pre-production compliance sign-off. Define SLO dashboards for every Tier-1 system.

### 11. Application Rationalisation Is a Business Conversation, Not a Technical One

Business owners must be active participants in rationalisation decisions. The EA provides the technical health score; the business provides the value score. Neither can make a rationalisation decision alone.

Run joint scoring workshops with business owners annually. Use usage data, integration counts, and revenue attribution to anchor value discussions. Present rationalisation recommendations in business language, not technical.

### 12. Retirement Is a Project — Resource and Govern It as One

Decommissioning a system is as complex as deploying a new one. Dependency resolution, data migration, contract termination, and access removal all require dedicated effort. Unmanaged retirements create orphaned integrations, data breaches, and zombie cost.

Give every retirement a project code, a project manager, and a timeline. Mandate 90-day notice periods to all dependent teams. Make access removal the final mandatory step in every decommission runbook.

### 13. Use Your Technology Radar to Prevent Sprawl

The Technology Radar (Adopt / Trial / Hold / Retire) is the EA's most powerful tool for controlling technology sprawl. Every technology in the estate should have a published position, reviewed annually.

Publish and socialise the Technology Radar organisation-wide. Reject any ARB submission proposing a technology on the 'Hold' or 'Retire' list. Review and publish an updated radar at least annually.

### 14. Strategic Alignment Is the EA's North Star

Every architecture decision, every investment recommendation, and every rationalisation choice must be traceable to at least one strategic theme. An EA who cannot articulate the strategic rationale for a decision is operating as a technical function, not a strategic one.

Map every initiative to a strategic theme at intake. Report strategic alignment % as a headline EA KPI. Challenge any initiative that cannot be mapped to a strategic objective.

### 15. EA Metrics Must Tell a Business Story

Activity metrics (reviews completed, documents produced) do not demonstrate value. Business outcome metrics (TCO reduced, time to market improved, risk incidents prevented) do. The EA must measure and communicate in the language of business.

Maintain a dual dashboard: EA activity metrics + business outcome metrics. Present EA value in terms of cost saved, risk reduced, and speed improved. Tie EA KPIs to the corporate OKR cycle.

### 16. Stakeholder Trust Is Built Through Consistency, Not Perfection

Business leaders do not trust EA because it produces perfect architectures — they trust it because it is consistent, transparent, and delivers what it promises. Reliability over time is the foundation of strategic influence.

Meet every governance commitment and communicate early when you cannot. Publish architecture principles and stick to them consistently. Follow up on every ARB condition with the owner.

### 17. Cloud Is a Deployment Model, Not a Strategy

Cloud adoption must be governed by the same architectural rigour as any other technology decision. 'Move to cloud' is not a strategy. The EA must define a Cloud Adoption Framework that covers placement policy, cost governance, security posture, and operating model.

Define and publish a cloud placement policy (public/private/hybrid criteria). Implement FinOps governance to prevent cloud cost sprawl. Validate cloud architecture against the Well-Architected Framework for every design.

### 18. Security Architecture Is Non-Negotiable

Security is not a feature to be added later. The EA must ensure that every design incorporates security-by-design principles: zero trust posture, least privilege access, encryption at rest and in transit, and comprehensive audit logging.

Make security architecture review mandatory at the Design gate. Require penetration testing or DAST scanning before every production gate. Track open security architecture findings by severity as a portfolio KPI.

### 19. Integration Patterns Are the Connective Tissue of the Enterprise

Poorly governed integration is the root cause of most enterprise architectural crises. Point-to-point integrations create fragile, unmaintainable webs. The EA must enforce approved integration patterns (API-first, event-driven, canonical data model) as non-negotiable standards.

Publish and enforce an enterprise integration pattern catalogue. Mandate API-first design for all new integrations. Maintain an integration dependency register and review it quarterly.

### 20. Great EAs Enable Change — They Do Not Resist It

The most common failure mode of enterprise architecture functions is becoming the department of 'no'. EA must continuously evolve its standards, patterns, and frameworks to embrace new paradigms — AI, platform engineering, composable architecture — before they arrive uninvited.

Maintain a formal EA innovation backlog reviewed quarterly. Pilot new paradigms through controlled trials on low-risk initiatives. Invite emerging technology perspectives into the Technology Radar process.

## Part 2 — EA Jargon Buster (A–Z)

**ADR** — Architecture Decision Record. A short document capturing the context, options considered, decision made, and consequences of a significant architectural choice. ADRs create an auditable trail of architectural reasoning.

**ARB** — Architecture Review Board. A governance body that reviews and approves architecture proposals, sets standards, and manages architectural risk across the enterprise.

**AIA** — Architecture Intake Assessment. The output document of the Pitch stage. A structured 1–2 page assessment covering the business problem, landscape findings, build/buy/reuse recommendation, and initial risk flags.

**AFC** — Architecture Fitness Function. An automated test or metric that objectively assesses whether an architecture characteristic conforms to defined standards.

**SAD** — Solution Architecture Document. The primary design artefact produced during the Design stage. Covers functional requirements, non-functional requirements, integration architecture, data flows, and security design.

**CoE** — Centre of Excellence. A team of subject matter experts who define, maintain, and promote best practices in a specific domain (e.g. Data CoE, Cloud CoE, Integration CoE).

**TOGAF** — The Open Group Architecture Framework. The dominant global EA framework — adopted by 60% of Fortune 500 companies.

**ArchiMate** — Enterprise Architecture Modelling Language. The standard visual notation for EA, maintained by The Open Group.

**C4 Model** — Context, Container, Component, Code. A lightweight, developer-friendly notation for software architecture diagrams.

**ITIL** — IT Infrastructure Library. A framework of best practices for IT service management. Relevant to EA in the Operate stage.

**Zachman** — Zachman Framework. A 6x6 matrix framework for organising architectural artefacts by stakeholder perspective and abstraction level.

**SAFe** — Scaled Agile Framework. A framework for applying agile and lean principles at enterprise scale.

**Tech Radar** — Technology Radar. A framework that classifies technologies into Adopt, Trial, Hold, and Retire rings.

**MTTR** — Mean Time to Recover. Average time from a failure being detected to service being restored. Key DORA/SRE metric.

**Maturity Model** — Architecture Capability Maturity Model. Assesses the capability maturity of an architecture function across levels from Initial to Optimising.

**App Rat** — Application Rationalisation. The process of evaluating every system in the portfolio on business value and technical health to determine its lifecycle disposition.

**Zombie System** — A production system that is no longer actively used but continues to draw operating cost because no one has formally retired it.
