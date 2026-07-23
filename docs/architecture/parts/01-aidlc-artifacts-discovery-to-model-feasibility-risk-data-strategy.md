---
title: "AIDLC Lifecycle Artifacts: Feasibility, Risk & Data Strategy (Phase 2-3)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-discovery-to-model-part2
maturity: practitioner
personas: [architect, engineer, manager, governance]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, ai-development, artifacts, feasibility, risk, data-governance, templates]
sources: []
---

# AIDLC Lifecycle Artifacts: Feasibility, Risk & Data Strategy (Phase 2-3)

**Part 2 of 3** — continues from [Discovery & Ideation](../01-aidlc-artifacts-discovery-to-model.md): the feasibility validation, risk register, and data governance artifacts (AIDLC Phases 2-3).

## Phase 2: Feasibility & Risk Assessment

**AI Governance Council Approval Gate**

Validate technical feasibility, assess full risk exposure, obtain governance approval to proceed.

**Inputs to this phase:**

- AI Use Case Charter (AUC-001)
- Business Value Canvas (BVC-001)
- Initial Risk Classification (RCS-001)

**Outputs from this phase:**

- Feasibility Report (FR-001)
- AI Risk Register (RR-001)
- Fundamental Rights Impact Assessment (FRIA-001)
- TPRM Vendor Assessment (TPRM-001)
- Compliance Obligation Matrix (COM-001)

### Technical Feasibility Report

**FR-001**

Owner: AI Architect + Data Architect | Phase: Phase 2: Feasibility

| **Data Availability** | *Bureau data: HIGH availability (Equifax, Experian APIs). Alternative data (utility): MEDIUM (3 providers identified, contract negotiation required). Thin-file historical: LIMITED — synthetic augmentation required.* |
|---|---|
| **Data Volume Assessment** | *Training set: 2.3M historical applications (36 months). Positive class ratio: 73% approved. Class imbalance strategy: SMOTE + cost-sensitive learning.* |
| **Model Approach Selected** | *XGBoost ensemble (primary scorer) + SHAP explainer (feature importance) + GPT-4o fine-tuned (adverse action narrative generation). Architecture: RAG for regulatory reason code library.* |
| **Infrastructure Feasibility** | *Azure ML available for training. Azure AI Content Safety for LLM outputs. Inference SLA: p99 &lt;200ms achievable with KServe + model caching. GPU budget: £45K/year training, £28K/year inference.* |
| **Integration Feasibility** | *Core banking API (Temenos): REST available, 200ms SLA. Bureau APIs: SOAP to REST adapter required (2 weeks build). Event streaming: Azure Event Hubs available.* |
| **Team Capability Assessment** | *ML Engineers: 3 available (2 FTE dedicated). Data Scientists: 2 (credit domain expertise). Data Engineers: 2. MLOps: 1 (upskilling required for LLMOps). Gap: LLM fine-tuning expertise — external support needed.* |
| **Overall Feasibility Verdict** | *FEASIBLE with conditions: (1) Alternative data contracts signed by Week 8. (2) LLM fine-tuning specialist engaged. (3) FRIA completed before Phase 4.* |

### AI Risk Register

**RR-001**

Owner: AI Compliance Lead + Model Risk Manager | Phase: Phase 2: Feasibility

| **ID** | **Risk Name** | **Impact** | **Likelihood** | **Rating** | **Description** | **Mitigation** | **Status** |
|---|---|---|---|---|---|---|---|
| RR-01 | Algorithmic Bias | HIGH | HIGH | CRITICAL | Demographic bias in credit scoring causing disparate impact on protected groups | SHAP bias monitoring; fairness metrics at every phase; external audit Phase 6; HITL override capability | Open |
| RR-02 | Data Quality Failure | HIGH | MEDIUM | HIGH | Poor alternative data quality leading to model degradation and wrong decisions | Data quality gates in Phase 3; automated quality monitoring in Phase 8; fallback to bureau-only scoring | Open |
| RR-03 | Regulatory Non-Compliance | HIGH | MEDIUM | HIGH | Failure to comply with EU AI Act, FCA rules, or adverse action notice requirements | FRIA; legal review at Phases 2,4,6; external conformity assessment; compliance obligation matrix | Open |
| RR-04 | Explainability Failure | HIGH | LOW | MEDIUM | Model unable to generate compliant adverse action reasons; black-box rejections | SHAP-based reason codes; LLM adverse action generation; 100% explainability coverage requirement | Open |
| RR-05 | Model Drift | MEDIUM | HIGH | HIGH | Model performance degradation post-deployment due to economic or behavioral shifts | Monthly drift monitoring; automated retraining triggers; p-value drift tests; model refresh SLA | Open |
| RR-06 | Data Breach (PII) | LOW | HIGH | MEDIUM | PII exposure in training data, inference logs, or LLM prompt/response | Azure Key Vault encryption; PII masking in RAG; Presidio in LLM pipeline; audit log access controls | Open |
| RR-07 | Vendor Lock-in | LOW | MEDIUM | LOW | Dependency on single cloud provider or LLM vendor | MLflow open registry; model router abstraction; OpenLineage lineage; LiteLLM multi-provider | Open |

### Fundamental Rights Impact Assessment

**FRIA-001**

Owner: Ethics & Fairness Lead + Legal | Phase: Phase 2: Feasibility

| **System Name** | *Credit Risk AI Scoring Model (AUC-2026-FIN-047)* |
|---|---|
| **FRIA Version** | *v1.0 — Initial Assessment* |
| **Assessment Date** | *5 March 2026* |
| **Lead Assessor** | *Dr. Amara Diallo, Ethics & Fairness Lead* |
| **Legal Counsel** | *Patel & Morrison LLP (FCA regulatory practice)* |

**Affected Populations & Rights at Risk**

| **Affected Group** | **Fundamental Rights at Risk** | **Severity** | **Potential Impact** | **Mitigation Committed** |
|---|---|---|---|---|
| Retail lending applicants (all) | Access to financial services (Art. 8 EU AI Act; Equality Act 2010) | HIGH | Credit denial; financial exclusion | Bias monitoring; HITL override; appeal mechanism |
| Thin-file applicants (young, immigrants, low income) | Non-discrimination; equality of opportunity | HIGH | Systematic exclusion; perpetuation of disadvantage | Alternative data inclusion; demographic parity testing; protected group uplift analysis |
| Rejected applicants | Right to explanation; right to human review | HIGH | Inability to understand or challenge AI decision | 100% explainability; adverse action notice; human review process; written appeal channel |
| Employees (model reviewers) | Right to fair working conditions | LOW | New workload patterns; skill obsolescence | Change management; upskilling; clear HITL responsibilities |

**FRIA Conclusion**

HIGH RISK CONFIRMED — Deployment conditional on: (1) External fairness audit completed in Phase 6. (2) Human review mechanism operational at Phase 7. (3) Written appeal process documented and accessible. (4) Quarterly demographic parity monitoring post-deployment.

**Sign-off**

Dr. Amara Diallo (Ethics Lead) · James Hartley (CRO) · Priya Sharma (Compliance Lead) — 10 March 2026

### Compliance Obligation Matrix

**COM-001**

Owner: AI Compliance Lead + Legal | Phase: Phase 2: Feasibility

| **Regulation / Article** | **Obligation** | **AIDLC Phase & Artifact** | **Priority** |
|---|---|---|---|
| EU AI Act Art. 9 | Risk Management System throughout lifecycle | ALL phases — documented in Risk Register RR-001 | CRITICAL |
| EU AI Act Art. 10 | Data governance: quality, representativeness, bias-free training data | Phase 3 — Data Sheet DS-001 + Bias Baseline BB-001 | CRITICAL |
| EU AI Act Art. 11 | Technical documentation (Architecture, Model Card, Test Results) | Phases 4–6 — ADR-001, MCF-001, RTP-001 | CRITICAL |
| EU AI Act Art. 12 | Automatic logging / record-keeping | Phase 7 — ALC-001 Audit Log Configuration | CRITICAL |
| EU AI Act Art. 13 | Transparency & information to deployers | Phase 7 — UDD-001 User Disclosure Documentation | HIGH |
| EU AI Act Art. 14 | Human oversight measures | Phases 4,7 — HITL design; IRP-001 | CRITICAL |
| EU AI Act Art. 15 | Accuracy, robustness, cybersecurity | Phase 6 — PBR-001, SPT-001 | CRITICAL |
| UK Equality Act 2010 | Non-discrimination across protected characteristics | Phases 3,6,8 — BB-001, FER-001, MMR-001 | CRITICAL |
| UK GDPR / DPA 2018 | Data subject rights, processing lawful basis, PIA | Phase 3 — PIA-001 | CRITICAL |
| FCA SYSC 23 (Operational Resilience) | AI system resilience and recovery capabilities | Phase 7 — IRP-001, Deployment Runbook | HIGH |
| ECOA Adverse Action (equivalent) | Reason codes for credit denial (regulatory adverse action notice) | Phases 4–7 — Explainability design + UDD-001 | CRITICAL |

---

## Phase 3: Data Strategy & Governance

**AI Governance Council Gate: Data Governance Board Approval**

Establish data foundation — provenance, quality, privacy, lineage — for trustworthy AI.

**Inputs to this phase:**

- Risk Register (RR-001)
- Feasibility Report (FR-001)

**Outputs from this phase:**

- Data Sheet / Data Card (DS-001)
- Privacy Impact Assessment (PIA-001)
- Data Lineage Map (DLM-001)
- Bias Baseline Report (BB-001)
- Data Processing Agreements (DPA-001)

### Data Sheet (Data Card)

**DS-001**

Owner: Data Architect + Data Engineer | Phase: Phase 3: Data Strategy

| **Dataset** | **Source** | **Period** | **Volume** | **Storage Location** | **Quality Score** | **Classification** |
|---|---|---|---|---|---|---|
| Primary Training Dataset | Equifax credit bureau records | 36 months (Jan 2023–Dec 2025) | 2,317,442 records | S3://ml-data-prod/credit/bureau/ | 98.7% | PII — Tier 2 |
| Utility Payment History | Equiniti / National Grid utility API | 24 months | 847,291 records | S3://ml-data-prod/credit/utility/ | 94.2% | PII — Tier 2 |
| Rent Payment History | Experian Rental Bureau | 18 months | 312,088 records | S3://ml-data-prod/credit/rental/ | 91.4% | PII — Tier 2 |
| Application Data | Temenos core banking (live) | 36 months | 2,317,442 records | Azure SQL: corebanking.applications | 99.1% | PII — Tier 2 |
| Outcome Labels (Ground Truth) | Core banking 12-month default tracking | 36 months | 2,317,442 labels | S3://ml-data-prod/credit/labels/ | 100% | Internal Conf. |

**Protected Attributes Present**

Age (derived from DOB), postcode (proxy for ethnicity/socioeconomic status), Gender. Action: Age retained for fairness monitoring only — not used as model feature. Postcode retained for fairness monitoring only — not used as model feature.

**Class Imbalance**

73% approved (negative label), 27% default (positive label). Mitigation: SMOTE oversampling of minority class + cost-sensitive learning (FP cost = 3× FN cost).

| **Consent Basis** | *GDPR Article 6(1)(b) — Necessary for performance of contract (credit assessment). Article 9 profiling permitted under Article 22(2)(a).* |
|---|---|
| **Data Retention Policy** | *Training data: 5 years post-model retirement. Inference logs: 7 years (FCA financial records requirement). Synthetic data: 3 years.* |
| **Data Sheet Owner** | *Dr. Nina Kowalski, Lead Data Scientist* |
| **Board Approved Date** | *18 March 2026* |

### Bias Baseline Report

**BB-001**

Owner: Ethics & Fairness Lead + Data Scientist | Phase: Phase 3: Data Strategy

| **Baseline Date** | *Pre-training assessment — 20 March 2026* |
|---|---|
| **Reference Model** | *Current rule-based scorecard (legacy system)* |
| **Fairness Framework** | *Demographic Parity + Equalized Odds + Individual Fairness* |

| **Fairness Metric** | **Group Comparison** | **Baseline Value** | **Target Threshold** | **Mitigation Strategy** |
|---|---|---|---|---|
| Approval Rate Parity | Age 18–25 vs 35–45 | +18.2pp gap (younger applicants approved less often) | 2.0pp | Resampling + fairness constraint in training |
| Approval Rate Parity | Postcode Q1 (most deprived) vs Q4 | +24.1pp gap (deprived areas approved less often) | 2.0pp | Alternative data inclusion; postcode excluded as feature |
| False Negative Rate Equity | Age 18–25 | 2.3× higher than 35–45 (creditworthy youth rejected more) | 1.2× | Cost-sensitive learning; SMOTE for young applicants |
| False Positive Rate Equity | Postcode Q1 | 1.8× higher than Q4 (more defaults in deprived areas approved) | 1.2× | Calibrated thresholds per risk segment |
| Model Calibration | All groups | Brier score 0.14 overall; 0.19 for Age 18–25 (worse) | &lt;0.15 all groups | Separate calibration per age band |

**Bias Baseline Conclusion**

SIGNIFICANT bias found in legacy system. Delta &lt;2pp and equalized odds ratio &lt;1.2× across all measured groups before deployment approval. AI model must achieve demographic parity delta &lt;2pp across all measured groups before deployment approval.

---

## Related

- [AIDLC Artifacts: Discovery & Ideation (Phase 1)](../01-aidlc-artifacts-discovery-to-model.md)
- [AIDLC Artifacts: Model Design & Architecture (Phase 4)](02-aidlc-artifacts-discovery-to-model-model-design-architecture.md)

## Sources

None currently documented.
