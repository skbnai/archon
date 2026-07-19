---
title: "AIDLC Lifecycle Artifacts: Development & Evaluation (Phase 5-6)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-development-to-retirement
maturity: practitioner
personas: [architect, engineer, manager, governance]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: ["docs/ai-development/aidlc/AIDLC_Artifact_Reference_Library_Part2_Development_to_Retirement.md"]
tags: [aidlc, ai-development, artifacts, development, mlops, retirement, templates]
sources: []
---

# AIDLC Lifecycle Artifacts: Development & Evaluation (Phase 5-6)

Part 1 of 3 — continues to [Part 2: Deployment, MLOps & Retirement (Phase 7-8)](./parts/03-aidlc-artifacts-development-to-retirement-deployment-mlops-retirement.md).

Live templates for AIDLC Phases 5 and 6 — development and training, and evaluation and red-teaming.

**Audience:** Enterprise Architects, ML Engineers, MLOps Engineers, Data Scientists, Compliance Teams

**Coverage:** AIDLC Phases 5–6

**As of:** 2026

---

## Phase 5: Development & Training

**AI Governance Council Gate: Development Readiness**

Build, fine-tune, and train the AI system with full traceability and developer accountability.

**Inputs to this phase:**

- Architecture Decision Records (ADR-001)
- Constitutional AI Policy (CAP-001)
- Data Sheet (DS-001)
- Compliance Obligation Matrix (COM-001)

**Outputs from this phase:**

- Experiment Tracking Record (ETR-001)
- Training Run Log (TRL-001)
- Bias Mitigation Report (BMR-001)
- AI-Generated Code Audit Log (CAL-001)
- Model Registry Entry (MRE-001)

### Experiment Tracking Record

**ETR-001**

Owner: Lead Data Scientist | Phase: Phase 5: Development

| **Run ID** | **Model Name** | **Config Description** | **AUC-ROC** | **Gini** | **KS Stat** | **Bias Delta** | **Notes** |
|---|---|---|---|---|---|---|---|
| EXP-001 | XGB-Baseline-v0.1 | Baseline XGBoost, bureau data only | 0.79 | 0.58 | 0.38 | N/A | Baseline established. Bureau-only insufficient for thin-file. |
| EXP-008 | XGB-AltData-v0.3 | + Utility + Rental data added | 0.83 | 0.66 | 0.44 | 18.2pp age gap | Significant improvement. Bias still present. |
| EXP-014 | XGB-FairConstr-v0.6 | + Fairness constraint (exponentiated gradient) | 0.82 | 0.64 | 0.43 | 3.1pp age gap | Bias reduced. Minor perf sacrifice acceptable. |
| EXP-019 | XGB-SMOTE-v0.8 | + SMOTE oversampling for young applicants | 0.83 | 0.65 | 0.43 | 1.8pp age gap | Target threshold achieved. Calibration check needed. |
| EXP-023 | XGB-Final-v1.0 | + Calibrated thresholds per segment | 0.83 | 0.65 | 0.43 | 1.8pp age gap | SELECTED. All targets met. Proceeding to Phase 6. |

**Experiment Tracking Platform**

MLflow — Azure ML workspace. All experiments versioned. Run artifacts stored in Azure Blob. Reproducibility: random seeds fixed; data version pinned via DVC tag v1.0.

**Selected Model**

Run: EXP-023 — XGB-Final-v1.0. Registered in MLflow Model Registry as CreditRisk-XGB-v1.0, stage: Staging.

### AI-Generated Code Audit Log

**CAL-001**

Owner: Tech Lead + All Engineers | Phase: Phase 5: Development

| **Date** | **File / Lines** | **AI Tool** | **Description** | **Reviewer** | **Status** | **Review Notes** |
|---|---|---|---|---|---|---|
| 2026-04-08 | feature_engineering.py (lines 142–210) | GitHub Copilot | Utility payment aggregation pipeline (12-month rolling statistics) | David Lee (ML Eng) | APPROVED | Minor: column naming inconsistency fixed. Logic verified against Data Sheet DS-001. No hallucinated column names. |
| 2026-04-11 | xgb_trainer.py (lines 45–89) | Amazon Q Developer | XGBoost hyperparameter tuning loop with cross-validation | Sarah Wong (ML Eng) | APPROVED | Logic correct. Added explicit random_state for reproducibility (AI missed this). Verified against EXP-019 config. |
| 2026-04-14 | adverse_action_prompt.py (lines 1–156) | GitHub Copilot | LLM prompt template for adverse action notice generation | Raj Patel (ML Eng) | APPROVED WITH CHANGES | AI generated plausible-looking but non-FCA-compliant reason codes. Legal reviewed and corrected 3 reason code templates. CRITICAL fix. |
| 2026-04-17 | fairness_monitor.py (lines 1–98) | Amazon Q Developer | SHAP-based demographic parity monitoring pipeline | David Lee (ML Eng) | APPROVED | Logic verified against BB-001 bias baseline methodology. Protected attribute handling confirmed correct. |

**AWS AI-DLC Mandate Compliance**

All engineers have reviewed and understood every line of AI-generated code. AI-generated code committed without understanding verification sign-off. LLM prompt templates require legal review — not just technical review. Critical finding: No AI-generated code submission without understanding verification sign-off.

---

## Phase 6: Evaluation & Red-Teaming

**AI Governance Council Gate: Deployment Authorisation**

Rigorously validate against safety, fairness, performance, and Constitutional AI requirements.

**Inputs to this phase:**

- Model Registry Entry (MRE-001)
- Constitutional AI Policy (CAP-001)
- Model Card Draft (MCD-001)
- Bias Baseline Report (BB-001)

**Outputs from this phase:**

- Red Team Report (RTR-001)
- Fairness Evaluation Report (FER-001)
- Performance Benchmark Report (PBR-001)
- Constitutional Compliance Audit (CCA-001)
- Final Model Card (MCF-001)
- Security Penetration Test (SPT-001)

### Red Team Report

**RTR-001**

Owner: Security Architect + Ethics Lead | Phase: Phase 6: Evaluation

**Red Team Conducted:** 14–18 April 2026

**Red Team Lead:** Marcus Thompson, Security Architect

**Team Composition:** 2 internal security engineers, 1 external AI red-team specialist (NCC Group), 1 fairness researcher (external)

**Scope:** XGBoost scorer, LLM adverse action generator, API endpoints, data pipeline

| **ID** | **Attack Vector** | **Method** | **Finding** | **Severity** | **Remediation** | **Status** |
|---|---|---|---|---|---|---|
| RT-01 | Adversarial Credit Application | Submit crafted application designed to game scoring model | XGBoost model accepted application with 73% confidence (above threshold). Model not robust to feature manipulation. | HIGH | Feature consistency validation layer added before scoring. Anomaly detection on application feature patterns. | Resolved |
| RT-02 | Prompt Injection (LLM Component) | Inject instruction in applicant name/address fields | LLM successfully rejected 9/10 injection attempts. 1 case caused role confusion ("ignore previous instructions"). | MEDIUM | Lakera Guard prompt injection scanner added. Input sanitisation strengthened. System prompt hardened. | Resolved |
| RT-03 | Demographic Attribute Inference | Probe API responses to infer protected attribute decisions | SHAP values in API response revealed postcode-correlated scores potentially inferring ethnicity. | HIGH | Postcode SHAP values removed from API response. Internal only. Aggregate statistics only in adverse action notice. | Resolved |
| RT-04 | Adverse Action Hallucination | Query LLM for rejection reasons not supported by SHAP values | LLM generated plausible-sounding but factually incorrect reason codes in 3/50 test cases (6%). | HIGH | SHAP verification gate: LLM reasons validated against top-5 SHAP features before delivery. Human review if mismatch. | Resolved |
| RT-05 | Model Extraction | Reverse-engineer model logic via high-volume API queries | Insufficient data to reconstruct model in 10,000 queries. Rate limiting effective. | LOW | Rate limiting confirmed effective. Anomaly detection on unusual query patterns. | Accepted |

**Red Team Verdict**

CONDITIONAL PASS — All HIGH severity findings resolved before this report. Medium/Low findings resolved or accepted with monitoring. External red team specialist confirmed remediation adequate. Deployment may proceed subject to CCA-001 constitutional compliance audit.

### Fairness Evaluation Report

**FER-001**

Owner: Ethics & Fairness Lead (External Auditor) | Phase: Phase 6: Evaluation

| **Metric** | **Protected Groups** | **Baseline Value** | **AI Model Value** | **Threshold** | **Result** |
|---|---|---|---|---|---|
| Demographic Parity — Approval Rate | Age: 18–25 vs 35–45 | +18.2pp (baseline) | +1.6pp (AI model) | 2.0pp | PASS |
| Demographic Parity — Approval Rate | Postcode Quintile 1 vs 5 | +24.1pp (baseline) | +1.9pp (AI model) | 2.0pp | PASS |
| Equalized Odds — False Negative Rate | Age: 18–25 | +2.3× (baseline) | +1.15× (AI model) | 1.2× | PASS |
| Equalized Odds — False Negative Rate | Postcode Q1 | +1.8× (baseline) | +1.18× (AI model) | 1.2× | PASS |
| Individual Fairness | Counterfactual gender swap | N/A (not tested in legacy) | 0.4% decision change rate on gender | &lt;1% | PASS |
| Calibration | Age 18–25 (worst group) | Brier 0.19 (baseline) | Brier 0.14 (AI model) | &lt;0.15 | PASS |
| Adverse Action Parity | Protected vs non-protected | N/A | Reason code distribution parity: p=0.31 (not significant) | p&gt;0.05 | PASS |

**External Auditor**

Algorithmic Justice Institute (AJI) — Independent External Fairness Audit

**Audit Conclusion**

AI Model PASSES all fairness thresholds. Represents substantial improvement over legacy scorecard. Ongoing monitoring mandatory. Annual independent audit recommended.

**Auditor Sign-off**

Dr. Yetunde Adeyemi (AJI), 22 April 2026

### Constitutional AI Compliance Audit

**CCA-001**

Owner: AI Compliance Lead | Phase: Phase 6: Evaluation

| **Principle** | **Test Approach** | **Findings** | **Status** |
|---|---|---|---|
| P1 — Harmlessness | Test 50 adversarial applications; measure unjustified harm rate | All 50 evaluated; 2 borderline cases sent to HITL. 0 clearly harmful decisions. Harm rate: 0%. | PASS |
| P2 — Honesty | Verify 100 adverse action notices against SHAP ground truth | 97/100 notices accurate. 3 cases: SHAP-LLM mismatch detected and caught by verification gate. 0 undetected inaccuracies. | PASS |
| P3 — Fairness | Full FER-001 evaluation | All fairness thresholds met. See FER-001. | PASS |
| P4 — Privacy | Test PII masking on 200 LLM prompts | 0 PII leakage in LLM prompts/responses. Presidio masking 100% effective on test set. | PASS |
| P5 — Transparency | 100 test decisions: verify disclosure + explanation availability | 100/100 decisions produced adverse action notice. AI disclosure text present in 100% of UI flows. | PASS |
| P6 — Human Oversight | Test HITL trigger on 100 low-confidence decisions | HITL triggered correctly in 48/48 sub-70% confidence cases. Human review queue operational. | PASS |
| P7 — Regulatory Compliance | Legal review of all adverse action reason codes | FCA legal counsel (Patel & Morrison) confirmed all 28 reason codes compliant. | PASS |
| P8 — Security & Robustness | Cross-reference with Red Team Report RTR-001 | All HIGH/MEDIUM findings resolved. See RTR-001. | PASS |

**Constitutional Compliance Rate**

100% (8/8 principles PASS)

**Overall Audit Conclusion**

APPROVED FOR DEPLOYMENT — Subject to production monitoring as specified in Phase 8 artifacts.

---

## Related

- [01-aidlc-artifacts-discovery-to-model.md](01-aidlc-artifacts-discovery-to-model.md) — Phases 1–4 (Discovery through Architecture)
- [parts/03-aidlc-artifacts-development-to-retirement-deployment-mlops-retirement.md](./parts/03-aidlc-artifacts-development-to-retirement-deployment-mlops-retirement.md) — Part 2: Deployment, MLOps & Retirement (Phase 7-8)
- [parts/04-aidlc-artifacts-development-to-retirement-ea-artifacts.md](./parts/04-aidlc-artifacts-development-to-retirement-ea-artifacts.md) — Part 3: Enterprise Architecture Artifacts
- [03-aidlc-artifacts-togaf-foundation-to-technology.md](03-aidlc-artifacts-togaf-foundation-to-technology.md) — TOGAF ADM Preliminary through Technology phases
- [04-aidlc-artifacts-togaf-migration-to-ea.md](04-aidlc-artifacts-togaf-migration-to-ea.md) — TOGAF ADM Migration through EA Cross-Cutting artifacts

## Sources

None currently documented.
