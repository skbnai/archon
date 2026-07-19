---
title: "AIDLC Lifecycle Artifacts: Model Design & Architecture (Phase 4)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-discovery-to-model-part3
maturity: practitioner
personas: [architect, engineer, manager, governance]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, ai-development, artifacts, model-design, architecture, templates]
sources: []
---

# AIDLC Lifecycle Artifacts: Model Design & Architecture (Phase 4)

**Part 3 of 3** — continues from [Feasibility, Risk & Data Strategy](01-aidlc-artifacts-discovery-to-model-feasibility-risk-data-strategy.md): the architecture decision, constitutional AI policy, and model card artifacts (AIDLC Phase 4).

## Phase 4: Model Design & Architecture

**AI Governance Council Gate: Architecture Review**

Design AI system architecture aligned with governance constraints and compliance requirements.

**Inputs to this phase:**

- Data Sheet (DS-001)
- Risk Register (RR-001)
- Bias Baseline Report (BB-001)

**Outputs from this phase:**

- Architecture Decision Record (ADR-001)
- Constitutional AI Policy (CAP-001)
- Model Card Draft (MCD-001)
- AI Threat Model (ATM-001)
- Explainability Design (EXD-001)

### Architecture Decision Record

**ADR-001**

Owner: AI Architect | Phase: Phase 4: Architecture

| **ADR ID** | *ADR-2026-FIN-047-001* |
|---|---|
| **Title** | *Model Architecture Selection: XGBoost Ensemble + LLM Adverse Action Generator* |
| **Status** | *ACCEPTED — Architecture Review Board 2 April 2026* |
| **Deciders** | *Rahul Mehta (AI Architect), Dr. Nina Kowalski (Lead DS), Priya Sharma (Compliance), James Hartley (CRO)* |

**Decision**

XGBoost gradient boosting ensemble for primary credit scoring. SHAP for feature attribution and reason code generation. GPT-4o fine-tuned on FCA adverse action templates for human-readable rejection notices. Redis feature cache for sub-100ms inference.

**Context**

Need: real-time scoring (&lt;200ms p99), regulatory explainability (reason codes), thin-file capability (alternative data), demographic fairness constraints.

**Options Considered**

| **Option** | **Architecture** | **Performance** | **Complexity** | **Explainability** | **Regulatory Fit** |
|---|---|---|---|---|---|
| Option A (Selected) | XGBoost + SHAP + GPT-4o | HIGH | MEDIUM | HIGH | HIGH — full SHAP reason codes; LLM narration |
| Option B | Deep Neural Network + LIME | HIGH | HIGH | MEDIUM | MEDIUM — LIME less reliable for tabular data |
| Option C | Logistic Regression scorecard | LOW | LOW | HIGH | HIGH — fully transparent but low performance on thin-file |
| Option D | Black-box LLM (GPT-4o end-to-end) | HIGH | HIGH | LOW | LOW — cannot satisfy regulatory explainability |

**Consequences**

(+) Best performance + explainability + regulatory compliance. (−) Two-model architecture adds deployment complexity. LLM fine-tuning cost £18K one-time. Requires LLMOps monitoring for GPT component.

### Constitutional AI Policy Document

**CAP-001**

Owner: AI Governance Council | Phase: Phase 4: Architecture

| **Field** | **Value** |
|---|---|
| **System Name** | *Credit Risk AI Scoring Model (AUC-2026-FIN-047)* |
| **Policy Version** | *v1.0 — Approved 5 April 2026* |
| **Policy Owner** | *Priya Sharma, AI Compliance Lead* |
| **Review Cycle** | *Quarterly or upon any regulatory change* |

| **#** | **Principle** | **Policy Statement** | **Implementation Controls** |
|---|---|---|---|
| P1 | Harmlessness | This system must not generate credit decisions that cause unjustified financial harm. All decisions must be backed by explainable, auditable evidence. No output may be used to discriminate against protected groups. | Demographic parity monitoring; HITL override; adverse action audit trail |
| P2 | Honesty | The system must not fabricate or embellish adverse action reasons. All reason codes must be traceable to actual model feature contributions (SHAP values). Uncertainty in predictions must be communicated to human reviewers. | SHAP attribution verification; confidence score thresholds; human review triggers below 70% confidence |
| P3 | Fairness | The system must achieve demographic parity delta &lt;2pp and equalized odds ratio &lt;1.2× across age bands and postcode deprivation quintiles. Any detected bias triggers automatic review and potential model suspension. | Continuous fairness monitoring in Phase 8; automated bias alert at &gt;1.5× delta; quarterly external audit |
| P4 | Privacy | PII must be masked before LLM processing. No applicant PII may appear in LLM prompts or responses. All inference logs must be encrypted. Data retained only within policy limits. | Presidio PII masker in LLM pipeline; encrypted audit logs; automated retention enforcement |
| P5 | Transparency | Every applicant receiving a credit decision must receive a clear explanation. The system must never deny knowing it is AI. Human review must be offered to every rejected applicant. | 100% adverse action notice generation; "AI-powered" disclosure; appeal mechanism in UI |
| P6 | Human Oversight | All decisions below 70% confidence must be flagged for human review. All appeals trigger human review. CRO has authority to suspend the system at any time. No autonomous credit limit changes above £5,000. | HITL workflow in core banking; confidence threshold monitoring; CRO kill switch; action boundary register |
| P7 | Regulatory Compliance | The system must comply with EU AI Act, UK Equality Act, UK GDPR, FCA SYSC 23, and ECOA-equivalent adverse action requirements at all times. Regulatory changes trigger immediate compliance review. | Automated regulatory change scanning; compliance obligation matrix; quarterly legal review |
| P8 | Security & Robustness | The system must resist prompt injection in the LLM component. The XGBoost model must maintain performance under distributional shift. Adversarial credit applications must not destabilize scoring. | Input validation; prompt injection scanner; drift monitoring; adversarial robustness testing in Phase 6 |

### Model Card (Draft)

**MCD-001**

Owner: Lead Data Scientist | Phase: Phase 4: Architecture

| **Model Name** | *CreditRisk-XGB-v1.0* |
|---|---|
| **Model Type** | *XGBoost Gradient Boosting Classifier (binary: creditworthy / not creditworthy)* |
| **Intended Use** | *Automated credit scoring for retail lending applications at [Bank Name] UK* |
| **Out-of-Scope Uses** | *Commercial lending, mortgage decisioning, insurance pricing, fraud detection (separate models required)* |
| **Primary Users** | *Automated system (80% of decisions); Human credit analysts (20% of decisions; all appeals)* |
| **Training Data** | *As per Data Sheet DS-001. 2.3M records, 36 months, Jan 2023–Dec 2025* |
| **Evaluation Data** | *Hold-out test set: 15% stratified split. Temporal validation: most recent 3 months reserved.* |
| **Model Limitations (Draft — updated in Phase 6)** | *Performance gap for thin-file applicants (N&lt;12 months credit history); Postcode proxy effects require monitoring; LLM narrative component may hallucinate reason details — SHAP values are ground truth* |
| **Performance Metrics (Draft — TBC in Phase 6)** | *AUC-ROC target &gt;0.82; Gini &gt;0.64; KS statistic &gt;0.42; Demographic parity delta &lt;2pp* |
| **Model Card Status** | *DRAFT — To be finalized in Phase 6 post evaluation* |

---

## Related

- [AIDLC Artifacts: Discovery & Ideation (Phase 1)](../01-aidlc-artifacts-discovery-to-model.md)
- [AIDLC Artifacts: Feasibility, Risk & Data Strategy (Phase 2-3)](01-aidlc-artifacts-discovery-to-model-feasibility-risk-data-strategy.md)
- [AIDLC Artifacts: Development to Retirement](../02-aidlc-artifacts-development-to-retirement.md) — Phases 5-8

## Sources

None currently documented.
