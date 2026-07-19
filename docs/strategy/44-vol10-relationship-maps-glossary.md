---
title: "Relationship Maps: Concept Hierarchy & Core Comparisons"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol10-relationship-maps-glossary
maturity: practitioner
personas:
  - enterprise-architect
  - strategy-consultant
last_reviewed: 2026-07-19
covers_version: ""
supersedes:
  - docs/enterprise-strategy/vol10-relationship-maps-glossary.md
tags:
  - concept-hierarchy
  - relationships
  - strategy-taxonomy
  - enterprise-concepts
sources: []
---

# Relationship Maps: Concept Hierarchy & Core Comparisons

Why this matters: Enterprise strategy and architecture require a shared language. Without clear definitions of the relationships between strategy, capability, process, and organization, teams ship systems that don't align with the intended business model. This section maps the complete concept hierarchy that binds strategy execution together.

## Concept Hierarchy Maps

### Strategy Hierarchy

Enterprise strategy flows top-down through nested decision levels:

**Vision** (10–25 year aspiration): "What do we want to become?"

**Mission** (5–10 years, why we exist): "What do we do and for whom?"

**Purpose** (permanent, why it matters): "Why does this matter beyond profit?"

**Strategic Intent** (competitive ambition): "Where do we want to lead?"

**Corporate Strategy** (how to compete): "What is our theory of winning?"

**Strategic Themes** (annual focus areas): "What are this year's priorities?"

**Strategic Priorities** (ranked focus within themes)

**Strategic Objectives** (measurable outcomes): "What must change?"

**Strategic Initiatives** (programs enabling objectives)

**Programs** (group of related projects)

**Projects** (temporary; defined deliverable)

**Epics** (large body of user work)

**Features** (user-visible capabilities)

**Stories** (development units)

**Tasks** (implementation activities)

### Business Architecture Hierarchy

Business capabilities organize from broad domains to specific activities:

**Enterprise Level** defines major areas of business activity.

**Business Domain** (e.g., "Finance", "Customer", "Operations")

**Business Capability Level 1** (e.g., "Customer Management")

**Business Capability Level 2** (e.g., "Customer Acquisition")

**Business Capability Level 3** (e.g., "Lead Generation")

**Business Process or Value Stream** describes how the capability is executed.

**Business Activity** is a step within a process.

**Business Rule**, **Business Event**, and **Business Decision** govern activities.

### Application Architecture Hierarchy

Enterprise applications organize by domain, system, and module:

**Application Domain** groups related systems (e.g., "CRM Domain", "ERP Domain")

**Application or System** is a named enterprise system (e.g., "Salesforce", "SAP S/4HANA")

**Application Module** is a functional subset (e.g., "Sales Cloud", "Service Cloud")

**Component or Service** is a deployable unit of functionality.

**API or Interface** defines how components interact.

**Operation or Endpoint** is a specific callable function.

**Data Object or Schema** represents data exchanged via the API.

### Technology Architecture Hierarchy

Infrastructure organizes from domains to configurations:

**Infrastructure Domain** ("Cloud", "Network", "Compute", "Storage")

**Platform** ("AWS", "Azure", "GCP", "On-Premise Data Centre")

**Technology Building Block (ABB)** ("Container Platform", "Message Broker")

**Service or Product (SBB)** ("AWS EKS", "Apache Kafka", "PostgreSQL")

**Instance or Cluster** is a specific deployment.

**Configuration** includes settings, policies, versions.

### AI Architecture Hierarchy

AI capabilities organize from strategic themes to implementation:

**AI Strategic Theme** (e.g., "AI-First Customer Experience")

**AI Capability** (e.g., "Personalised Recommendation")

**AI Use Case** (e.g., "Next Best Offer for Retail Banking Customers")

**AI System or Product** (e.g., "Offers AI v2.1")

**AI Building Block** (e.g., "LLM Gateway", "Vector Database")

**Model, Agent, or Pipeline** (e.g., "Claude Sonnet", "Fraud Agent")

**Prompt, Tool, or Memory** (e.g., "fraud-analysis-prompt-v2")

### Governance Hierarchy

Authority flows from board oversight to team-level standards:

**Board Oversight** sets fiduciary direction.

**Executive Committee** (CEO + C-Suite) makes strategic decisions.

**Investment Committee** allocates capital.

**Architecture Review Board (ARB)** governs technical standards.

**AI Governance Board** governs AI risk and policy.

**Data Governance Council** governs data policy.

**Domain Governance Forum** operates at function/domain level.

**Team-Level Standards** define development and definition of done.

---

## Concept Comparisons

Clarity on the most frequently confused enterprise terms:

### Strategy vs. Tactic

**Strategy** defines where to play and how to win over the long term (3–10 years). **Tactic** defines how to execute within a chosen approach over the short term (weeks to months).

The confusion: people often call tactical choices "strategies." A pricing discount is a tactic. A decision to compete on price as market positioning is a strategy.

### Vision vs. Mission vs. Purpose

**Vision** is what we want to become (10–25 years, aspirational). **Mission** is what we do and for whom (5–10 years, descriptive). **Purpose** is why it matters beyond money (permanent, moral).

### Goal vs. Objective vs. KPI

**Goal** is a broad desired outcome (often qualitative). **Objective** is a specific, measurable desired outcome within a time frame. **KPI** is the metric tracking progress toward the objective.

### Capability vs. Function vs. Process

**Capability** is what the organization can do (stable over time). **Function** is the organizational unit responsible for work (changes with org design). **Process** is the sequence of activities producing an outcome (changes with optimization).

Capabilities remain constant when organizations reorganize — only the function assignment changes.

### Initiative vs. Program vs. Project

**Initiative** is a strategic investment area grouping programs and projects (1–5 years). **Program** is a coordinated group of related projects (1–3 years). **Project** is a temporary endeavor with a defined output (3–18 months).

### Portfolio vs. Program

**Portfolio** groups programs and projects aligned to a strategic theme. **Program** groups related projects managed in a coordinated way.

### Platform vs. Product

**Platform** enables others to create value (consumed by developers and builders). **Product** directly delivers value to end users.

Platform success is measured by adoption rate of products/services built on top. Product success is measured by user satisfaction and revenue.

### Building Block vs. Component

**Building Block** is an architecture-level reusable capability unit (enterprise-wide scope). **Component** is a design/implementation-level unit (within-application scope).

### Architecture vs. Design

**Architecture** comprises system-wide strategic decisions that are costly to change. **Design** comprises detailed implementation decisions that iterate through development.

### Business Architecture vs. Enterprise Architecture

**Business Architecture** covers business strategy, capabilities, processes, and organization. **Enterprise Architecture** covers all four domains: business, data, application, and technology.

### Operating Model vs. Organization Structure

**Operating Model** defines how the organization delivers value (people, process, technology, data, governance). **Organization Structure** defines how people are grouped and who reports to whom.

### Reference Architecture vs. Solution Architecture

**Reference Architecture** is a prescriptive pattern for a class of problems (high reusability). **Solution Architecture** is a specific design for a specific system (low reusability).

### Segment vs. Sector vs. Industry vs. Market

**Industry** is a broad grouping of companies with similar business activities (e.g., Financial Services). **Sector** is a sub-grouping within industry (e.g., Banking). **Market** is the buyers and sellers of a specific product (e.g., UK retail mortgage market). **Segment** is a subset of market with distinct characteristics (e.g., first-time buyer segment).

---

## Related

- [Relationship Maps: AI/Ops Comparisons & Terminology Cross-Reference](86-vol10-relationship-maps-glossary-ai-comparisons-terminology-xref.md)
- [Enterprise Glossary: A-G](87-vol10-relationship-maps-glossary-glossary-terms-a-g.md)
---

*Volume 10 of 10 — Enterprise Strategy & Business Architecture Handbook. Part 1 of 5.*
