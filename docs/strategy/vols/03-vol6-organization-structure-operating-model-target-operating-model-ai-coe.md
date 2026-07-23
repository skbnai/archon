---
title: "Organization Structure: Target Operating Model & AI COE"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol6-organization-structure-operating-model-part3
maturity: practitioner
personas:
  - enterprise-architect
  - cto
  - chief-people-officer
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - target-operating-model
  - ai-coe
  - ai-center-of-excellence
sources: []
pagination_prev: strategy/vols/vol6-organization-structure-operating-model-agile-scale-operating-model
pagination_next: strategy/vols/vol6-organization-structure-operating-model-ai-maturity-deliverables
---

# Organization Structure: Target Operating Model & AI COE

Why this matters: A Target Operating Model (TOM) is your north star for transformation. Without it, organizations don't know where they're going. An AI Center of Excellence translates that vision into executable teams.

## Target Operating Model (TOM) Design

A **Target Operating Model (TOM)** is a blueprint of how an organization needs to operate in the future to execute its strategy. It is the "operating model at the end of a transformation"—the north star for organizational change programs.

### TOM Design Methodology

**Phase 1: Understand the Strategy**
- Review corporate strategy, strategic themes, and priorities
- Identify strategic requirements that drive operating model change
- Understand transformation drivers (regulatory, competitive, technology)

**Phase 2: Assess the Current State**
- Current organization structure and spans/layers analysis
- Process maturity assessment (CMMI or equivalent)
- Technology landscape review (application inventory, technical debt)
- Data quality and governance maturity
- Culture and capability gap analysis

**Phase 3: Design the Future State**
- Define operating model principles (the guardrails for design)
- Design organizational structure options (typically 2–3 alternatives)
- Define process model: which processes stay, transform, or are eliminated
- Define technology blueprint: which systems enable the TOM
- Define governance model: decision rights, forums, reporting
- Define talent model: capabilities needed, sourcing strategy

**Phase 4: Gap Analysis**
- Map current → future state for each TOM dimension
- Identify gaps: organizational, process, technology, data, capability
- Quantify transformation effort and investment required

**Phase 5: Define the Transition**
- Sequence the change: what changes in Year 1, Year 2, Year 3?
- Define the organizational change management (OCM) plan
- Establish governance for the transformation program

### TOM Artifacts

| Artifact | Purpose | Owner |
|----------|---------|-------|
| **Operating Model Canvas** | One-page summary of TOM across all dimensions | Programme Director |
| **Organisation Design Blueprint** | Org charts, spans and layers, role profiles | HR / OD Lead |
| **Process Architecture** | Level 0-2 process map, ownership, maturity targets | Process Architect |
| **Application Blueprint** | Systems landscape, integration patterns | Enterprise Architect |
| **Data Architecture Blueprint** | Data domains, ownership, governance | Data Architect |
| **Governance Model** | Decision rights, forums, escalation paths | Governance Lead |
| **RACI Matrix** | Responsibility assignment for all key processes | Programme Director |
| **Service Catalogue** | Catalogue of capabilities and services offered | COO / CTO |
| **Transition Roadmap** | Multi-year transition plan | Programme Director |
| **Transformation Business Case** | Investment justification with benefits realization | CFO / Sponsor |

### Common TOM Anti-Patterns

| Anti-Pattern | Description | Consequence |
|--------------|-------------|-------------|
| **TOM as Org Chart** | TOM reduced to a box-and-line org chart | Misses process, technology, governance |
| **Aspirational TOM** | TOM describes an ideal state with no feasible path | Credibility loss; transformation stalls |
| **Technology-First TOM** | Technology choices made before operating model designed | Systems don't support the model |
| **Consultant-Dependent TOM** | TOM designed entirely by external consultants | Not adopted; sits on shelf |
| **Static TOM** | TOM designed once; never updated as strategy evolves | Increasingly irrelevant |
| **Big Bang TOM** | Entire TOM implemented simultaneously | Change overload; high failure risk |
| **Missing Transition** | TOM defines future state but not the journey | Organisation doesn't know how to get there |

---

## AI Center of Excellence Models

### Why an AI COE?

An AI Center of Excellence (COE) is an organizational construct that centralizes AI expertise, standards, platforms, and governance while enabling distributed delivery across the enterprise. Without some form of COE:

- Every team reinvents the same AI infrastructure
- Model risk is ungoverned
- AI talent is scattered and hard to develop
- Standards for safety, privacy, and quality are inconsistent
- Investment is duplicated; results are fragmented

The COE solves the "how do we scale AI responsibly?" problem.

### Centralized AI COE

**Model:** Single team with all AI expertise, responsible for building and deploying AI across the organization.

**Governance Model:**
- AI Steering Committee (C-suite): quarterly strategy and investment review
- AI Governance Board (BU heads + CDO + CISO): monthly risk and standards review
- AI Review Panel (technical): weekly review of new use cases and models

**Pros:**
- Highest consistency of standards and practices
- Deep expertise concentration enables state-of-the-art work
- Clear accountability for enterprise AI outcomes
- Easiest to govern and audit

**Cons:**
- Becomes a bottleneck as demand grows
- Risk of ivory-tower disconnect from business needs
- Business units feel disempowered and may shadow-build
- Single point of failure for AI delivery

**Best For:** Enterprises early in AI journey; highly regulated industries; organizations with significant model risk exposure.

### Federated AI COE (Hub-and-Spoke)

**Model:** A central hub defines standards, provides the platform, and leads governance. Spoke teams within each business unit execute AI delivery with local context.

**Pros:**
- Scales delivery without bottleneck
- Maintains standards and governance
- Business units feel ownership while benefiting from central expertise
- Best of both worlds for most enterprises

**Cons:**
- Coordination overhead between hub and spokes
- Cultural alignment required
- Hub quality must be high enough to be worth the coordination cost
- Risk of spoke teams drifting from standards over time

**Best For:** Large enterprises with multiple distinct business units; enterprises past initial AI pilots; organizations where speed is critical.

### Embedded AI Teams

**Model:** Small AI squads embedded directly within product or business teams. No central COE; AI capability is fully distributed.

**Pros:**
- Maximum speed; AI closest to the business problem
- No bottleneck; each team is self-sufficient
- Deep domain expertise in AI teams
- High business alignment

**Cons:**
- Inconsistency in standards, tools, and practices
- Duplication of infrastructure build
- Hard to recruit and retain dispersed AI talent
- Governance gaps; model risk may be unmanaged

**Best For:** Technology-native companies; organizations with strong engineering culture; post-COE scaling when norms are established.

### AI Factory (High-Volume Delivery Model)

**Definition:** An industrial-scale operating model for AI delivery, treating AI use case development as a repeatable manufacturing process rather than a series of one-off projects.

**McKinsey AI Factory Model:**
- Factory Floor: Standardized delivery process (discovery → build → deploy → operate)
- Quality Control: Automated evaluation, monitoring, and human review
- Supply Chain: Reusable components (data pipelines, features, models, prompts)
- Management System: Throughput metrics, cycle time tracking, quality KPIs

---

## Related

- [Organization Structure: Why Org Design Matters & Core Structures](../49-vol6-organization-structure-operating-model.md)
- [Organization Structure: Operating Models & Design](02-vol6-organization-structure-operating-model-agile-scale-operating-model.md)
- [Organization Structure: AI Maturity & Deliverables](04-vol6-organization-structure-operating-model-ai-maturity-deliverables.md)
---

*Volume 6 of 10 — Enterprise Strategy & Business Architecture Handbook (Part 3 of 4)*
