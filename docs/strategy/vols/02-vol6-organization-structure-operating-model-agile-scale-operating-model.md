---
title: "Organization Structure: Operating Models & Design"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol6-organization-structure-operating-model-part2
maturity: practitioner
personas:
  - enterprise-architect
  - cto
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - operating-model
  - digital-operating-model
  - ai-operating-model
  - cloud-operating-model
sources: []
pagination_prev: strategy/vol6-organization-structure-operating-model
pagination_next: strategy/vols/vol6-organization-structure-operating-model-target-operating-model-ai-coe
---

# Organization Structure: Operating Models & Design

Why this matters: Organization structure defines *who reports to whom*. Operating model defines *how work actually gets done*. Both must align for strategy execution.

## Operating Model Design

An **Operating Model** defines how an organization delivers value—the combination of people, processes, technology, data, and governance that enables strategy execution.

**The Five Operating Model Dimensions:**
1. **People:** Roles, skills, culture
2. **Processes:** Workflows, standards, controls
3. **Technology:** Systems, platforms, data
4. **Data:** Ownership, quality, products
5. **Governance:** Policies, controls, decisions

### Jeanne Ross MIT Operating Model Framework

Jeanne Ross (MIT Sloan CISR) defines four operating model archetypes based on two dimensions: **process standardization** and **process integration**.

**The Four Archetypes:**

| Model | High Std/Low Int | High Std/High Int | Low Std/Low Int | Low Std/High Int |
|-------|-----------------|-----------------|-----------------|-----------------|
| **Name** | REPLICATION | UNIFICATION | DIVERSIFICATION | COORDINATION |
| **Examples** | Retail chains | Airlines, banks | Conglomerates | B2B companies |

**Implications for AI Strategy:**

| Model | AI Challenge | AI Opportunity |
|-------|-------------|----------------|
| Unification | Single model must serve all BUs | Enterprise-wide AI reuse is highest |
| Coordination | Shared customer data enables personalization | Cross-BU AI insights are natural |
| Replication | Each BU wants its own AI | Template-based AI deployment scales well |
| Diversification | No shared foundation | AI is BU-by-BU; little enterprise leverage |

### Digital Operating Model

**Definition:** A digital operating model is purpose-built for continuous delivery of digital products and services. It replaces project-based delivery with product-based delivery, and waterfall governance with agile governance.

**Key Design Principles:**

| Traditional | Digital |
|-------------|---------|
| Project teams (temporary) | Product teams (permanent) |
| Deliver and handoff | Build-operate-improve |
| Annual budgets | Rolling investment decisions |
| Stage-gate approvals | Continuous deployment |
| IT as service provider | Technology as core capability |
| Functional ownership | End-to-end ownership |

**Components:**
- Product Teams: Long-lived, cross-functional, end-to-end ownership
- Platform Engineering: Internal developer platform reduces friction
- DevOps Culture: Developers own deployment and operations
- Customer Feedback Loops: Continuous measurement of user behavior
- OKR Governance: Outcomes measured quarterly; investment adjusted

### AI Operating Model

**Definition:** An AI Operating Model defines how an organization develops, deploys, governs, and continuously improves AI capabilities at scale. It extends the digital operating model with AI-specific constructs.

**AI Operating Model Dimensions:**

| Dimension | Key Decisions |
|-----------|--------------|
| **AI Team Model** | Centralized COE vs. federated vs. embedded vs. hybrid |
| **AI Development** | Build vs. buy vs. partner; fine-tune vs. prompt vs. RAG |
| **AI Governance** | Who approves AI use cases, models, deployments? |
| **AI Data Model** | Who owns AI training data? What quality standards apply? |
| **AI Risk Model** | How is AI risk categorized and managed? |
| **AI Talent Model** | What AI roles does the enterprise need? |
| **AI Platform Model** | What shared infrastructure enables AI delivery? |
| **AI Value Model** | How are AI investments measured and justified? |

**AI Operating Model Maturity:**

```
Level 5: AI-NATIVE    — AI-first in all decisions
Level 4: AI-SCALING   — Systematic AI deployment
Level 3: AI-BUILDING  — Repeatable AI capability
Level 2: AI-EXPERIMENTING — Structured pilots
Level 1: AI-UNAWARE   — Ad hoc or none
```

### Platform Operating Model

**Definition:** The organization operates as a platform business—providing internal (and sometimes external) customers with reusable capabilities, infrastructure, and services rather than delivering projects.

**Platform Types in Enterprise:**

| Platform | Primary Consumer | Core Capabilities |
|----------|-----------------|-------------------|
| **Developer Platform** | Engineering teams | CI/CD, environments, templates |
| **Data Platform** | Analytics and AI teams | Data products, pipelines, governance |
| **AI Platform** | Product teams, data scientists | LLM access, fine-tuning, evaluation |
| **Security Platform** | All teams | IAM, secrets, vulnerability scanning |
| **Observability Platform** | Engineering teams | Metrics, logs, traces, alerts |

### Cloud Operating Model

**Definition:** A cloud operating model governs how the enterprise uses public cloud services—covering procurement, consumption management, security, governance, and FinOps.

**Key Design Decisions:**

| Decision | Options |
|----------|---------|
| **Cloud Strategy** | Single cloud, multi-cloud, hybrid |
| **Cloud Governance** | Centralized landing zone vs. federated |
| **FinOps Model** | Central FinOps team vs. federated cost ownership |
| **Security Baseline** | Central security; distributed compliance |
| **Workload Placement** | Which workloads go to cloud vs. stay on-premises |

### Data Operating Model

**Definition:** A data operating model governs how enterprise data is owned, managed, shared, and consumed to create value.

**Data Mesh vs. Data Fabric:**

| Dimension | Data Mesh | Data Fabric |
|-----------|-----------|-------------|
| **Core Philosophy** | Data as a product; domain ownership | Connected metadata layer across all data |
| **Ownership** | Distributed (domain teams) | Central data team or shared |
| **Architecture** | Decentralized storage, shared governance | Centralized access, distributed storage |
| **Governance** | Federated computational | Centralized metadata |
| **Best Fit** | Large organizations with multiple domains | Organizations wanting unified data view |

---

## Related

- [Organization Structure: Why Org Design Matters & Core Structures](../49-vol6-organization-structure-operating-model.md)
- [Organization Structure: Target Operating Model & AI COE](03-vol6-organization-structure-operating-model-target-operating-model-ai-coe.md)
- [Organization Structure: AI Maturity & Deliverables](04-vol6-organization-structure-operating-model-ai-maturity-deliverables.md)
---

*Volume 6 of 10 — Enterprise Strategy & Business Architecture Handbook (Part 2 of 4)*
