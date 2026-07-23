---
title: AIDLC Lifecycle Artifacts - Discovery & Ideation
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-discovery-to-model
maturity: practitioner
personas: [architect, engineer, manager, governance]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: ["docs/ai-development/aidlc/AIDLC_Artifact_Reference_Library_Part1_Discovery_to_Model_Design.md"]
tags: [aidlc, ai-development, artifacts, discovery, model-design, templates]
sources: []
---


# AIDLC Lifecycle Artifacts: Discovery & Ideation

**Part 1 of 3** — live templates for AIDLC Phase 1 (Discovery & Ideation), the first of four stages that precede any model training, with field definitions and example content for every artifact. Continues in [Feasibility, Risk & Data Strategy](parts/01-aidlc-artifacts-discovery-to-model-feasibility-risk-data-strategy.md) and [Model Design & Architecture](parts/02-aidlc-artifacts-discovery-to-model-model-design-architecture.md).

**Audience:** Enterprise Architects, AI Delivery Leads, Program Managers, Governance Teams

**Coverage:** AIDLC Phase 1 · Template Field Definitions

**As of:** 2026

## How to Read This Document

This guide presents structured templates for every artifact produced in the first four AIDLC phases. Each artifact appears as a template with example values shown in blue italic text. The examples illustrate a hypothetical "Credit Risk AI Scoring Model" use case at a fictional financial services enterprise.

Phase headers use colored banners with phase number, name, and governance gate. Input/output flow boxes indicate artifacts consumed by (green left) and produced by (blue right) each phase. Each artifact includes field definitions and example data. Gray background marks field labels; blue italic text shows illustrative example values for your reference.

**Replace all blue italic example values with your actual project data before submission for governance approval.**

---

## Phase 1: Discovery & Ideation

**AI Governance Council Registration**

Define the AI use case, business value hypothesis, and initial feasibility signal.

**Inputs to this phase:**

- Strategic Business Goals
- Market / Competitive Analysis
- Stakeholder Pain Points
- Regulatory Landscape Brief

**Outputs from this phase:**

- AI Use Case Charter (AUC-001)
- Business Value Canvas (BVC-001)
- Initial Risk Classification Sheet (RCS-001)
- Executive Sponsor Sign-off (ESO-001)

### AI Use Case Charter

**AUC-001**

Owner: Business Owner / Product Manager | Phase: Phase 1: Discovery

| **Use Case ID** | *AUC-2026-FIN-047* |
|---|---|
| **Use Case Name** | *Credit Risk AI Scoring Model — Retail Lending* |
| **Business Domain** | *Retail Banking — Credit Risk Management* |
| **Business Owner** | *Sarah Chen, VP Credit Risk, Retail Banking* |
| **Product Manager** | *David Okafor, Senior PM, AI & Analytics* |
| **Date Initiated** | *12 February 2026* |
| **Charter Version** | *v1.2* |
| **Status** | *Approved — Proceeding to Phase 2* |

**Problem Statement**

| **Problem Statement** | *The current credit scoring process takes 72 hours on average, relies on manual review for 40% of applications, and results in a 12% false-rejection rate for creditworthy customers in underserved segments. This causes customer churn, missed revenue, and equity concerns.* |
|---|---|
| **Business Pain Points** | *72-hour decision cycle; 40% manual review burden; 12% false-rejection rate; Inability to serve thin-file customers; Manual process inconsistency across regions* |
| **Target Opportunity** | *Reduce decision time to &lt;60 seconds for 80% of applications; reduce false-rejection rate to &lt;5%; enable thin-file credit assessment via alternative data* |

**AI Solution Hypothesis**

| **Proposed AI Solution** | *ML-based credit scoring model using gradient boosting + alternative data (utility payments, rent history) combined with LLM-powered adverse action explanation generator* |
|---|---|
| **AI Approach** | *Supervised ML classification (creditworthy / not creditworthy) + RAG-powered explanation generation for regulatory adverse action notices* |
| **AI vs Non-AI Decision** | *AI preferred: decision volume (50,000/month), pattern complexity, regulatory explainability requirement, real-time speed requirement. Non-AI alternatives (rule engine, scorecard) evaluated and rejected.* |
| **Build vs Buy vs Fine-Tune** | *Buy: Foundation credit risk models (FICO, Equifax). Fine-tune: LLM for adverse action explanation. Build: Alternative data pipeline and ensemble orchestration.* |

**ROI & Value Hypothesis**

| **Metric** | **Baseline** | **AI Target Annual Value Impact** |
|---|---|---|
| Decision Cycle Time | 72 hours | &lt;60 seconds: £2.1M saved (FTE reduction + faster revenue recognition) |
| Manual Review Rate | 40% | &lt;8%: £1.4M saved (analyst hours) |
| False Rejection Rate | 12% | &lt;5%: £3.8M recovered revenue (re-captured creditworthy customers) |
| Customer NPS (Credit) | 34 | &gt;55: Brand value; reduced churn |
| **Total Projected Annual ROI** | — | £7.3M (payback period: 9 months) |

**Initial Risk Flags**

| **Preliminary EU AI Act Tier** | *HIGH RISK — Annex III Category: Access to financial services (creditworthiness assessment). Full AIDLC + FRIA required.* |
|---|---|
| **Protected Attributes Involved** | *Age, Gender, Ethnicity, Postcode (proxy for protected attributes). Bias mitigation mandatory from Phase 3.* |
| **Regulatory Bodies** | *FCA (UK), PRA, ICO, EU AI Act National Competent Authority (if EU customers)* |
| **Explainability Requirement** | *MANDATORY — ECOA/Regulation B-equivalent (UK) requires adverse action notice with specific reason codes. Every rejection must be explainable.* |

**Executive Sponsor Sign-off**

| **Executive Sponsor** | *James Hartley, Chief Risk Officer* |
|---|---|
| **Sign-off Date** | *19 February 2026* |
| **Approval Conditions** | *1. Full FRIA completed before development begins. 2. External fairness audit in Phase 6. 3. Quarterly bias monitoring post-deployment.* |
| **Escalation Path** | *AI Governance Council → CRO → Board Risk Committee* |

### Business Value Canvas

**BVC-001**

Owner: Product Manager | Phase: Phase 1: Discovery

| **Canvas Dimension** | **Example Content** |
|---|---|
| AI System | Credit Risk AI Scoring Model (AUC-2026-FIN-047) |
| Customer Segments Served | Retail banking applicants: prime, near-prime, thin-file, underserved |
| Value Propositions | 60-second credit decisions; fair thin-file assessment; consistent explainable outcomes; 24/7 availability |
| Key Activities | Alternative data ingestion, real-time scoring, adverse action generation, bias monitoring |
| Key Resources | Credit data (bureau + alternative), GPU inference cluster, model team, compliance expertise |
| Key Partners | Equifax/Experian (bureau data), Utility data providers, FCA regulatory counsel |
| Revenue Streams | Net interest income on approved loans, reduced cost of risk (fewer defaults), fee income |
| Cost Structure | Model development (£420K), annual MLOps (£180K), compliance (£95K), data licensing (£240K) |
| Success Metrics | Decision time &lt;60s (80% of apps); false rejection &lt;5%; bias delta &lt;2%; Explainability coverage 100% |
| Failure Risks | Regulatory rejection (FRIA outcome); bias discovery post-deployment; data quality failure; model drift |

### Initial Risk Classification Sheet

**RCS-001**

Owner: AI Governance Council | Phase: Phase 1: Discovery

| **Use Case ID** | *AUC-2026-FIN-047* |
|---|---|
| **EU AI Act Annex III Check** | *YES — Category 5(b): AI used for creditworthiness assessment of natural persons* |
| **Assigned Risk Tier** | *TIER 2 — HIGH RISK* |
| **FRIA Required** | *YES — Fundamental Rights Impact Assessment mandatory* |
| **External Audit Required** | *YES — Independent conformity assessment before deployment* |
| **Governance Intensity** | *Full AIDLC all 8 phases; AI Governance Council sign-off at Phases 2, 4, 6, 7* |
| **Classification Approved By** | *Priya Sharma, AI Compliance Lead* |
| **Classification Date** | *22 February 2026* |

---

## Related

- [AIDLC Artifacts: Feasibility, Risk & Data Strategy (Phase 2-3)](parts/01-aidlc-artifacts-discovery-to-model-feasibility-risk-data-strategy.md)
- [AIDLC Artifacts: Model Design & Architecture (Phase 4)](parts/02-aidlc-artifacts-discovery-to-model-model-design-architecture.md)
- [AIDLC Artifacts: Development to Retirement](02-aidlc-artifacts-development-to-retirement.md) — Phases 5-8 and Enterprise Architecture artifacts

## Sources

None currently documented.
