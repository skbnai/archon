---
title: "Portfolio Consulting Frameworks: Architecture & Operating Delivery"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol8-portfolio-consulting-frameworks-part3
maturity: practitioner
personas:
  - enterprise-architect
  - strategy-consultant
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - architecture-frameworks
  - togaf
  - delivery-frameworks
sources: []
---

# Portfolio Consulting Frameworks: Architecture & Operating Delivery

## Architecture Frameworks

### TOGAF 10 Deep Dive

**Architecture Development Method (ADM) Phases:**

| Phase | Name | Key Outputs |
|-------|------|------------|
| **Preliminary** | Framework & Principles | Architecture principles; governance model |
| **A** | Architecture Vision | Statement of Architecture Work |
| **B** | Business Architecture | Business Architecture baseline and target |
| **C** | Information Systems Architecture | Application & Data Architecture |
| **D** | Technology Architecture | Technology Architecture |
| **E** | Opportunities & Solutions | Implementation roadmap; Architecture Roadmap |
| **F** | Migration Planning | Transition Architecture; Migration Plan |
| **G** | Implementation Governance | Architecture Contracts |
| **H** | Architecture Change Management | Updated baseline architecture |
| **Requirements Management** | Central (ongoing) | Requirements repository |

**Four Architecture Domains:**

| Domain | What It Covers |
|--------|---------------|
| **Business Architecture** | Strategy, governance, organization, capabilities, processes |
| **Data Architecture** | Data assets, data management, data flows |
| **Application Architecture** | Application systems and their interactions |
| **Technology Architecture** | Infrastructure, platforms, middleware, networks |

### Zachman Framework

**Core Concept:** Classification schema organizing architectural artifacts. Rows represent stakeholder perspectives; columns represent interrogatives (What, How, Where, Who, When, Why).

**Use When:**
- Ensuring enterprise architecture artifact completeness
- Communicating with different stakeholders
- Organizing architecture repository

**Limitations:** Not a methodology; doesn't tell you how to create artifacts; very academic; rarely used in full in practice.

### BIZBoK (Business Architecture Guild)

**Core Domains:**

| Domain | What It Contains |
|--------|----------------|
| **Business Capability Map** | What the organization must be able to do; hierarchical |
| **Value Streams** | End-to-end sequences of activities delivering value |
| **Organization Map** | How business units and roles are organized |
| **Business Information Map** | Key information concepts used by the business |
| **Initiative Map** | How strategies and initiatives align to capabilities |
| **Strategy Map** | Strategic goals and their relationships |

**When to Use BIZBoK:**
- Enterprise business capability mapping
- Strategy-to-execution alignment analysis
- Business transformation planning
- AI capability gap analysis

---

## Operating & Delivery Frameworks

### SAFe 6.0 (Scaled Agile Framework)

**Four Core Values:** Alignment, Built-in Quality, Transparency, Program Execution

**Essential SAFe (Most Common Entry Point):**

```
PORTFOLIO: Strategic themes → Portfolio Epics → WSJF prioritization
PROGRAM (ART): PI Planning → Iteration → System Demo → Inspect & Adapt
TEAM: Sprint planning → Daily standup → Sprint review → Retrospective
```

**Program Increment (PI) Planning:**
- 2-day event every 10-12 weeks (5 sprints)
- All ART members attend
- Business owners present objectives
- Teams create team PI objectives and identify dependencies

**Lean Portfolio Management (LPM):**
1. Strategy and Investment Funding: Connect portfolio to enterprise strategy
2. Agile Portfolio Operations: Coordinate value stream execution
3. Lean Governance: Forecast, budget dynamically; measure portfolio performance

**SAFe for AI Programs:**
- AI use cases become Epics at portfolio level
- AI platform delivery is dedicated Value Stream
- Model governance checkpoints in Definition of Done
- AI ethics review as part of PI System Demo

### OKR Framework

**OKR Structure:**

```
OBJECTIVE: Qualitative, inspirational, direction-setting
  KEY RESULT 1: Quantitative, measurable, time-bound
  KEY RESULT 2: Quantitative, measurable, time-bound
  KEY RESULT 3: Quantitative, measurable, time-bound
```

**OKR Hierarchy:**

| Level | Purpose | Cadence |
|-------|---------|---------|
| **Company OKRs** | Strategic priorities for the year | Annual, with quarterly check |
| **Department OKRs** | How department contributes | Quarterly |
| **Team OKRs** | Specific team commitments | Quarterly |

**Google OKR Scoring:**
- 0.0-0.4: Failed to make progress
- 0.5-0.6: Partial progress
- 0.7-0.9: Good progress (ideal "sweet spot")
- 1.0: Fully achieved (may indicate insufficient ambition)

**OKR Anti-Patterns:**

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Activity OKRs** | "Launch the AI platform" is a task, not outcome | Write: "AI platform adopted by 80% of teams" |
| **Too many OKRs** | 10+ objectives = no focus | 3-5 objectives; 2-4 KRs each |
| **Sandbagging** | Teams write OKRs they know they'll achieve | Calibrate for 70% achievement as success |
| **No cascading** | Team OKRs disconnected from company OKRs | Explicit alignment mapping |

### Balanced Scorecard

**Four Perspectives:**

| Perspective | Question | Example KPIs |
|-------------|----------|-------------|
| **Financial** | How do we look to shareholders? | Revenue growth, EBITDA, ROI |
| **Customer** | How do customers see us? | NPS, CSAT, churn rate |
| **Internal Process** | What must we excel at? | Cycle time, defect rate, on-time delivery |
| **Learning & Growth** | How can we improve? | Employee skills, system capabilities |

**AI Integration with Balanced Scorecard:**
- Financial: Add "AI investment ROI" and "AI cost per outcome"
- Customer: Add "AI-enabled service rating" and "AI personalization score"
- Internal Process: Add "AI model accuracy" and "AI automation rate"
- Learning & Growth: Add "AI literacy index" and "AI capability maturity score"

---

## Related

- [Portfolio Consulting Frameworks: Portfolio Management](../51-vol8-portfolio-consulting-frameworks.md)
- [Portfolio Consulting Frameworks: Innovation, Decision & Selection](10-vol8-portfolio-consulting-frameworks-innovation-decision-selection-guide.md)
---

*Volume 8 of 10 — Part 3 of 4*
