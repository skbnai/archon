---
title: "Target Operating Model, Organization & Change"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: target-operating-model-and-change
maturity: expert
personas: ["CHROs", "Transformation Leads", "COOs", "Executive Leadership"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: ["docs/enterprise-architecture/transformation/05_Target_Operating_Model_and_Change.md"]
tags: ["enterprise-ai", "operating-model", "organizational-design", "change-management", "workforce-transformation"]
sources: []
---

The human system that makes the technology pay. A federated hub-and-spoke model on a shared platform: central AI CoE owns standards and governance; business-unit AI pods own use cases and value; the platform team turns repeated needs into products.

## Target Operating Model: Hub, Spokes & Platform

| Element | Hub (AI CoE) | Spokes (BU AI Pods) | Platform Team |
|---|---|---|---|
| **Owns** | Strategy execution, standards, governance ops, evaluation service, enablement | Use-case selection, domain data, adoption, benefits delivery | AI platform, golden paths, MCP catalog, SRE for AI |
| **Funded by** | Central transformation budget | BU P&L; with central co-investment in Horizon 1 | Central, with chargeback visibility from Year 2 |
| **Accountable for** | Time-to-production, control effectiveness | Audited business value | Platform reliability, developer experience, unit cost |
| **Anti-pattern guarded against** | Ivory-tower CoE building demos | Shadow platforms and vendor sprawl | Platform as gatekeeper rather than enabler |

**Funding model shift:** From project-based to **product-based.** Persistent teams funded against outcome metrics with quarterly portfolio rebalancing, replacing annual business cases for the AI portfolio.

---

## AI Center of Excellence: Charter & New Roles

### CoE Charter (Sunset-Aware)

The CoE is chartered for 24-30 months with an explicit ambition to shrink: as spokes mature, delivery capacity transfers to them, and the CoE converges on standards, governance, platform, and frontier scanning. A CoE that grows forever has failed.

### New and Evolved Roles

| Role | Mandate | Where |
|---|---|---|
| **Chief AI / Transformation Officer** | Single accountable executive for the program; chairs Portfolio Board; reports to CEO | Executive team |
| **AI Product Manager** | Owns an AI product's outcomes, backlog, and benefits case | Spokes (8-15 by Yr 2) |
| **AI Engineer / Agent Engineer** | Builds RAG apps, agents, and integrations on the paved road | Platform + spokes |
| **Evaluation & Quality Lead** | Owns golden datasets, eval harness standards, human-review calibration | CoE |
| **Knowledge Engineer** | Converts expert know-how and content into retrievable, evaluable assets | CoE then spokes |
| **AI Risk & Assurance Specialist** | Runs tiering, reviews, incident taxonomy; partner to RAI Board | Risk function |
| **Agent Operations (AgentOps)** | Monitors production agents: behavior, cost, drift, entitlements | Platform team |
| **Change & Adoption Lead** | Owns enablement, communications, and adoption analytics per function | Transformation office |

---

## Skills Transformation & Workforce Enablement

| Population | Target Capability | Mechanism |
|---|---|---|
| **All employees (100%)** | Fluent, safe daily use of governed AI tools; prompt craft; judgment about verification | Role-based curriculum; licensed access for all knowledge workers; usage embedded in onboarding |
| **Power users / citizen developers (10-15%)** | Build self-service automations on the paved road within guardrails | Certification path; sandbox; community of practice with real support |
| **Managers (100% of people leaders)** | Redesign workflows for human+agent teams; manage performance in augmented work | Workshop series; redesign toolkits; manager KPIs include adoption quality |
| **Technical staff** | AI engineering, LLMOps, evaluation, agent security | Deep bootcamps; pairing with CoE; external hiring for anchor roles only |
| **Executives & Board** | Risk-informed AI judgment; ability to challenge and sponsor | Quarterly executive sessions; board education twice yearly |

---

## Change Management Strategy

### Workforce Principles (State Them Before Rumors Do)

- **Transparency:** Leadership communicates honestly which roles change, which shrink, which grow; silence is the most expensive communication strategy.

- **Reinvestment:** A defined share (recommended 20-30%) of Year 1-2 AI savings funds reskilling and internal mobility before external hiring.

- **Augment-first sequencing:** Tools land as assistants before any autonomy; affected teams co-design the workflows that change their jobs.

- **No stealth automation:** Process changes with headcount implications go through a defined consultation path; trust, once spent, does not refinance.

### Adoption Engine

- **Champions network:** 1-2% of workforce as trained champions with real time allocation, not a mailing list.

- **Visible wins cadence:** Monthly internal showcases of measured results — adoption follows evidence, not mandates.

- **Friction telemetry:** Adoption analytics (active use, task completion, satisfaction) reviewed like product metrics; low adoption is a product defect first, a people problem second.

- **Two-way channel:** Standing mechanism for employees to flag AI errors, risks, and ideas — the cheapest risk sensor you have.

---

## Leadership Responsibilities & Incentives

| Leader | Accountability in the Transformation |
|---|---|
| **CEO** | Owns the narrative; protects multi-year funding through budget cycles; breaks cross-functional ties |
| **CFO** | Owns benefits audit discipline and the investment gate process; sponsors the finance lighthouse |
| **CIO/CTO** | Owns platform delivery and paved-road quality; retires shadow platforms |
| **CHRO** | Owns skills transformation, workforce principles, and role redesign |
| **CRO/GC/CISO** | Own two-speed governance that is fast for Tier 3 and rigorous for Tier 1 |
| **BU Presidents** | Own use-case value; AI-attributed outcomes enter their scorecards from Year 1 |

**Incentive rule of thumb:** If AI outcomes appear in no one's compensation, the transformation is a hobby. Tie a meaningful share of executive variable pay to audited adoption and value metrics from Year 1.

---

## Related

- [Executive Summary & AI Vision](35-executive-summary-and-ai-vision.md)
- [Governance, Responsible AI & Security Architecture](39-governance-responsible-ai-and-security.md)
- [Roadmap, Financials, KPIs & Risk](41-roadmap-financials-kpis-and-risk.md)

## Sources

- Deloitte — Workforce transformation for AI (2026)
- SHRM — Change management best practices
- McKinsey — Organization transformation during technology transitions
