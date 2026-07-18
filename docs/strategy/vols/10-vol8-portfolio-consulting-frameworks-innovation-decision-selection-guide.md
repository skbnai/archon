---
title: "Portfolio Consulting Frameworks: Innovation, Decision & Selection"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol8-portfolio-consulting-frameworks-part4
maturity: practitioner
personas:
  - enterprise-architect
  - strategy-consultant
  - portfolio-manager
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - innovation-frameworks
  - decision-frameworks
  - business-model-innovation
sources: []
---

# Portfolio Consulting Frameworks: Innovation, Decision & Selection

## Innovation Frameworks

### Wardley Mapping

**Core Concept:** Map the value chain onto two axes—user need visibility (y-axis) and evolutionary stage (x-axis). Reveals where to invest, what to commoditize, and where disruption is coming.

**Evolution Axis:**

```
GENESIS → CUSTOM-BUILT → PRODUCT → COMMODITY/UTILITY
(Novel,   (Rare,       (Increasingly (Ubiquitous,
uncertain) competitive) standardised) utility-like)
```

**Strategic Gameplay:**

| Play | When to Use |
|------|------------|
| **Exploit evolution** | Buy commodity; don't build what's commoditizing |
| **Accelerate** | Push competitors' differentiators to commodity |
| **Tower and moat** | Build proprietary capability above commoditized layer |
| **Sensing engines** | Invest in sensing emerging capabilities before they become products |

**AI Application:** Foundation models moving from Product toward Commodity rapidly. Enterprise play is building proprietary capabilities (data, processes, workflows) *above* the commoditizing LLM layer.

### Design Thinking

**Five Stages:**

```
EMPATHIZE → DEFINE → IDEATE → PROTOTYPE → TEST
```

| Stage | Purpose | Key Activities |
|-------|---------|----------------|
| **Empathize** | Understand users deeply | Interviews, observation, journey mapping |
| **Define** | Frame the right problem | Problem statement, "How Might We" questions |
| **Ideate** | Generate many solutions | Brainstorming, SCAMPER, worst possible idea |
| **Prototype** | Make ideas tangible | Paper prototypes, wireframes, role-play |
| **Test** | Learn from real users | User testing, A/B experiments |

**Design Thinking for AI Products:**
- Empathize: Understand what task users accomplish; what are they afraid AI will do wrong?
- Define: Define the job to be done; define what "good" looks like
- Ideate: How might AI augment (vs. replace) the user?
- Prototype: Build prompt+UI prototype; test concept before building
- Test: Measure accuracy, trust, adoption

### Business Model Canvas

**Nine Building Blocks:**

| Block | Question |
|-------|---------|
| **Customer Segments** | Who are we creating value for? |
| **Value Propositions** | What value do we deliver to the customer? |
| **Channels** | How do we reach customers? |
| **Customer Relationships** | What type of relationship does each segment expect? |
| **Revenue Streams** | What are customers willing to pay for? |
| **Key Resources** | What resources do we need? |
| **Key Activities** | What do we need to do? |
| **Key Partners** | Who are our key partners and suppliers? |
| **Cost Structure** | What are the most important costs? |

**AI Business Model Canvas Variant:**

| Block | AI-Specific Consideration |
|-------|--------------------------|
| **Value Propositions** | AI-derived insights, predictions, automation |
| **Key Resources** | Training data, compute, model IP, AI talent |
| **Key Activities** | Model training, data collection, evaluation, safety |
| **Revenue Streams** | Per-query, per-seat, outcome-based, data monetization |
| **Cost Structure** | Token/compute costs, data acquisition, human review |

### Value Proposition Canvas

**Two Sides:**

```
CUSTOMER PROFILE:        VALUE MAP:
- Customer Jobs          - Products & Services
- Pains                  - Pain Relievers
- Gains                  - Gain Creators
```

"Fit" exists when the value map addresses the most important jobs, pains, and gains of the customer profile.

---

## Decision Frameworks

### RACI Matrix

**The Four Roles:**

| Role | Definition |
|------|-----------|
| **Responsible** | Does the work; multiple people can share responsibility |
| **Accountable** | Owns the outcome; only one person per task |
| **Consulted** | Input required before decision; two-way communication |
| **Informed** | Notified of outcome; one-way communication |

**RACI Rules:**
- Every task must have exactly one Accountable
- Accountable can also be Responsible
- Too many Consulted roles slows decisions—be selective
- Informed roles don't block the decision

### DACI (Driver, Approver, Contributors, Informed)

**Origin:** Intuit; popularized by product management teams.

| Role | Definition |
|------|-----------|
| **Driver** | Drives the process; owns the schedule; ensures decision happens |
| **Approver** | Single person who approves the final decision |
| **Contributors** | Provide input and expertise; do not have veto |
| **Informed** | Notified of the decision |

DACI often preferred over RACI for product decisions because it clarifies that "Approver" is one person (not a committee).

### Decision Rights Matrix for AI Governance

| AI Decision | Who Decides | Who Approves | Who Is Consulted |
|-------------|------------|--------------|-----------------|
| New AI use case approval | Business Unit | AI Governance Board | Legal, Risk, IT |
| AI model selection | AI COE | CAIO | Business Unit |
| AI production deployment | AI Platform Team | CISO + Risk | Business Unit |
| AI incident response | AI Operations | CISO | CAIO |
| AI policy creation | Legal + Risk | Board (for high-risk) | All stakeholders |

---

## Framework Selection Guide

### Which Framework When?

**Strategy Questions:**

| Question | Framework |
|----------|-----------|
| "What should our strategy be?" | Porter's Five Forces, Ansoff, Blue Ocean |
| "Is our organization aligned to execute?" | McKinsey 7S |
| "How should we allocate investment?" | Three Horizons, BCG Matrix |
| "How do we translate strategy to execution?" | OKR, Balanced Scorecard |
| "Where is disruption coming from?" | Wardley Mapping |

**Architecture Questions:**

| Question | Framework |
|----------|-----------|
| "How do we structure our architecture program?" | TOGAF ADM |
| "How do we map all architecture artifacts?" | Zachman Framework |
| "How do we map business capabilities?" | BIZBoK |

**Delivery Questions:**

| Question | Framework |
|----------|-----------|
| "How do we scale agile across the enterprise?" | SAFe 6.0 |
| "How do we set team goals?" | OKR |
| "How do we govern large portfolios?" | Lean Portfolio Management |
| "How do we track performance?" | Balanced Scorecard |

---

## Related

- [Portfolio Consulting Frameworks: Portfolio Management](../51-vol8-portfolio-consulting-frameworks.md)
- [Portfolio Consulting Frameworks: PMO Evolution & Strategy](08-vol8-portfolio-consulting-frameworks-pmo-evolution-strategy-frameworks.md)
---

*Volume 8 of 10 — Part 4 of 4*
