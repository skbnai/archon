---
title: "EA Strategy Playbook: Pitch to Design"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ea-strategy-playbook
maturity: expert
personas: ["Enterprise Architects", "Solution Architects", "Architecture Review Boards"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: ["docs/enterprise-architecture/strategy/EA_Strategy_Playbook.md"]
tags: ["enterprise-architecture", "governance", "raci", "ea-lifecycle", "architecture-review"]
sources: []
---

Enterprise Architecture must create strategy before money is committed. This playbook defines the operational stages from pitch through design, with clear RACI responsibilities, decision gates, and success patterns that prevent expensive mistakes.

## Overview: Pitch → Approve → Design

Every EA initiative moves through seven stages: Pitch, Approve, Design, Build, Operate, Review, and Retire. This section covers the first three, where the EA's job is to shape ideas into rigorous architecture intakes, validate them against governance, and produce blueprints that delivery teams can execute.

### Stage 1: Pitch / Demand (1–3 weeks)

**Strategic purpose:** Prevent expensive mistakes before money is committed. EA brings rigor by validating ideas against the current landscape, existing capabilities, and strategic priorities — transforming informal requests into structured architecture intakes.

**Key plays:**

1. **Run the landscape assessment:** Pull the current application portfolio and search for existing capabilities that match the need. Cross-reference the architecture roadmap for in-flight initiatives that could satisfy the request. Identify integration touchpoints and data domain ownership. Document findings in an Architecture Intake Assessment (AIA) — 1–2 pages max.

2. **Frame the Build/Buy/Reuse decision:** Define the three options explicitly: Build (custom dev), Buy (COTS/SaaS), Reuse (extend existing). Score each option on strategic fit, cost, speed to value, risk, and technical alignment. Make a provisional recommendation in the AIA. Flag any technology choices outside the approved technology radar.

**Checklist - Business Alignment:**
- Confirm the initiative has a named business sponsor with budget authority
- Map the initiative to at least one active strategic theme or OKR
- Document the business problem statement in one paragraph, reviewed by the sponsor
- Identify which business capabilities are impacted or created
- Assess urgency and strategic priority (High/Medium/Low)

**Landscape Assessment:**
- Identify overlapping or redundant initiatives already in flight
- Check for active vendor contracts or licences that may already cover the need
- Document current-state architecture touchpoints (systems, integrations, data flows)

**RACI — Stage 1: Pitch**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Receive and log intake request | R | I | I | C | – |
| Landscape & portfolio assessment | R | C | I | I | – |
| Frame build/buy/reuse options | R | C | I | C | – |
| Produce AIA | R | C | I | A | – |
| Approve AIA & recommend to ARB | R | – | A | C | – |

**Key tip:** Always check the vendor contract register before recommending a 'buy' — the organization may already be paying for a licence that covers the need.

**Watch out:** Sponsors often arrive with a pre-chosen solution. Your job at Pitch is to validate the problem, not rubber-stamp the solution.

**Gate: Architecture Intake Gate**
- Output: Signed Architecture Intake Assessment. Sponsor confirmed. Strategic theme mapped.

---

### Stage 2: Approve / Govern (1–2 weeks)

**Strategic purpose:** The ARB acts as the quality gate that prevents technical debt accumulation, architectural sprawl, and misaligned investment. Every approval must be conditional on standards compliance — not a rubber stamp based on business pressure.

**Key plays:**

1. **Conduct the architecture standards review:** Validate proposed technology stack against the Technology Radar (Adopt/Trial/Hold/Retire). Confirm integration approach: REST API, event-driven, batch, or point-to-point. Verify cloud deployment model aligns with the Cloud Adoption Framework. Confirm security architecture scope: zero trust posture, encryption, IAM approach.

2. **Run the ARB and issue the ADR:** Circulate ARB pack (AIA + options analysis + standards review) 5 business days in advance. Present to ARB: problem, options, recommendation, conditions, risks. Record ARB decision: Approve / Approve with Conditions / Defer / Reject. Publish Architecture Decision Record (ADR) with rationale, constraints, and review date. Assign named Solution Architect before closing the gate.

**Checklist - Business Case Review:**
- Confirm the business case includes quantified benefits with measurement methodology
- Review the options analysis: Build vs Buy vs Reuse vs Partner — EA must validate that all options were genuinely considered
- Validate TCO calculation covers a 3–5 year horizon including run costs
- Confirm ROI methodology is realistic (formula: [(Financial Gain − Cost) / Cost] × 100; target > 15%)

**Architecture Standards Compliance:**
- Confirm proposed integration approach aligns with enterprise integration patterns
- Validate data architecture approach against the enterprise data model
- Check cloud strategy alignment (public/private/hybrid/on-prem policy)
- Confirm security architecture requirements have been scoped

**RACI — Stage 2: Approve**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Prepare ARB submission pack | R | C | I | C | – |
| Present to ARB | R | C | A | I | – |
| Record & publish ARB decision | R | – | A | I | – |
| Issue Architecture Decision Record | R | – | A | I | – |
| Assign Solution Architect | A | R | I | I | – |

**Key tip:** Conditions on ARB approvals must have named owners and resolution dates. A condition without an owner is not a condition — it is deferred risk.

**Watch out:** Business pressure to 'just approve it' is highest here. An EA who approves to avoid conflict is not doing their job.

**Gate: ARB Architecture Approval Gate**
- Output: Signed ARB Decision Record. ADR published. Solution Architect assigned.

---

### Stage 3: Design (2–6 weeks)

**Strategic purpose:** Design translates the approved concept into a technical blueprint that delivery teams can execute. The output must be precise enough to prevent drift, but flexible enough to allow good engineering decisions within guardrails.

**Key plays:**

1. **Produce the Solution Architecture Document (SAD):** Define system context (C4 Level 1): boundaries, actors, and external systems. Define container/component diagrams for all new or significantly modified systems. Document all integration contracts: API specs (OpenAPI), event schemas, data formats. Map data flows and define data ownership, classification (PII/sensitive/public). Define all Non-Functional Requirements: availability, performance, scalability, RTO/RPO.

2. **Publish the architecture guardrails document:** List approved technology versions and permitted third-party libraries. Define mandatory patterns: authentication, error handling, logging, API versioning. Specify architecture compliance checkpoints within the delivery schedule. Define architecture fitness functions where automated compliance checking applies. Obtain peer review of SAD from at least one other EA before submission.

**Checklist - Non-Functional Requirements (NFRs):**
- Define availability SLA (e.g., 99.9% uptime) and validate infrastructure supports it
- Define RTO (Recovery Time Objective) and RPO (Recovery Point Objective) — mandatory for any system touching Tier-1 capabilities
- Specify performance benchmarks (response time, throughput, concurrency)
- Define scalability model (horizontal/vertical/auto-scaling thresholds)
- Complete security architecture review: authentication, authorization, encryption, audit

**RACI — Stage 3: Design**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Produce Solution Architecture Document | C | R | I | I | I |
| NFR definition and validation | C | R | I | C | C |
| Peer review of SAD | R | A | I | I | – |
| ARB review and SAD sign-off | A | R | R | I | I |
| Publish architecture guardrails | A | R | I | I | C |

**Key tip:** NFRs defined here are legally binding for the delivery team. If availability is set at 99.9%, the infrastructure must be designed and costed to deliver it.

**Watch out:** SADs that are too prescriptive stifle good engineering. Define the what and the why — not always the how.

**Gate: Solution Architecture Sign-off Gate**
- Output: Peer-reviewed SAD. ARB chair approved. Guardrails document published.

---

## Related

- [EA Strategy Playbook: Build to Retire](74-ea-strategy-playbook-build-operate-retire-stages.md)
- [RACI Decision Framework](67-part-08-organizational-roles-governance-risk-roles-raci-matrix.md)

## Sources

*No external sources; this is a consolidated operational playbook.*
