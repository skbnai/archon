---
title: "AIDLC Lifecycle Artifacts: Deployment, MLOps & Retirement (Phase 7-8)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-development-to-retirement-part2
maturity: practitioner
personas: [architect, engineer, manager, governance]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, ai-development, artifacts, deployment, mlops, retirement, templates]
sources: []
---

# AIDLC Lifecycle Artifacts: Deployment, MLOps & Retirement (Phase 7-8)

Part 2 of 3 — continues from [Part 1: Development & Evaluation (Phase 5-6)](../02-aidlc-artifacts-development-to-retirement.md), continues to [Part 3: Enterprise Architecture Artifacts](./04-aidlc-artifacts-development-to-retirement-ea-artifacts.md).

Live templates for AIDLC Phases 7 and 8 — deployment and MLOps, and monitoring, auditing, and retirement.

**Audience:** Enterprise Architects, ML Engineers, MLOps Engineers, Data Scientists, Compliance Teams

**Coverage:** AIDLC Phases 7–8

**As of:** 2026

---

## Phase 7: Deployment & MLOps

**AI Governance Council Final Deployment Approval**

Deploy with full operational governance, safety controls and human oversight mechanisms active.

**Inputs to this phase:**

- Final Model Card (MCF-001)
- Red Team Report (RTR-001)
- Constitutional Compliance Audit (CCA-001)
- Governance Approval (from Phase 6)

**Outputs from this phase:**

- Deployment Runbook (DRB-001)
- Incident Response Plan (IRP-001)
- Audit Log Configuration (ALC-001)
- User Disclosure Documentation (UDD-001)
- Runtime Monitoring Dashboard Spec (RMD-001)

### Deployment Runbook

**DRB-001**

Owner: MLOps Engineer + DevOps | Phase: Phase 7: Deployment

| **Model** | CreditRisk-XGB-v1.0 + Adverse Action-GPT-v1.0 |
|---|---|
| **Deployment Strategy** | Blue/Green Deployment with 5% Canary for 72 hours before full traffic |
| **Target Environment** | Azure Kubernetes Service (AKS) — prod-credit-scoring-cluster |
| **Deployment Owner** | Priya Patel, MLOps Engineer |

| **Step** | **Phase** | **Action** | **Owner** | **Type** | **SLA** |
|---|---|---|---|---|---|
| PRE-01 | Pre-flight | Verify model artifacts match signed registry entry (SHA-256 hash check) | MLOps Engineer | MANUAL | &lt;5 min |
| PRE-02 | Pre-flight | Confirm all runtime guardrails active: Lakera Guard, Presidio, Azure Content Safety | Security Engineer | AUTOMATED | &lt;2 min |
| PRE-03 | Pre-flight | Verify audit log stream connected to Splunk SIEM | MLOps Engineer | AUTOMATED | &lt;1 min |
| DEP-01 | Deploy | Deploy to blue/green canary (5% traffic). Monitor error rate, latency, SHAP stability for 72h. | MLOps Engineer | AUTOMATED | 72 hours |
| DEP-02 | Deploy | If canary metrics stable: promote to 100% traffic. Zero downtime switch. | MLOps Engineer | AUTOMATED | &lt;5 min |
| POST-01 | Post-deploy | Run post-deployment validation suite: 50 test applications, expected outputs | QA Engineer | AUTOMATED | &lt;15 min |
| POST-02 | Post-deploy | Activate Phase 8 monitoring: drift alerts, bias alerts, cost dashboard | MLOps Engineer | AUTOMATED | &lt;5 min |
| ROLL-01 | Rollback (if needed) | Revert to previous model version. Route 100% traffic to stable version. Alert AI Governance Council. | MLOps Engineer | SEMI-AUTO | &lt;3 min |

### AI Incident Response Plan

**IRP-001**

Owner: AI Compliance Lead + Security Architect | Phase: Phase 7: Deployment

| **Severity** | **Trigger** | **Response Actions** | **SLA** |
|---|---|---|---|
| P0 — CRITICAL | Systemic bias detected (demographic parity delta &gt;4pp) | Immediate model suspension. CRO and AI Governance Council alerted within 15 min. FCA notification within 24h. External audit commissioned. | &lt;15 min suspend; &lt;24h FCA notify |
| P0 — CRITICAL | Security breach: PII exfiltration via LLM | Model suspension. ICO notification (72h GDPR deadline). Forensic investigation. Customer notification as required. | &lt;15 min suspend; &lt;72h ICO |
| P1 — HIGH | Model accuracy degradation &gt;5% from baseline | HITL rate increased to 100%. Retraining pipeline triggered. AI Governance Council briefed within 2h. | &lt;2h escalation; &lt;48h retrain |
| P1 — HIGH | Hallucination rate &gt;2% (SHAP-LLM mismatch) | LLM adverse action generator suspended. Fallback to template-based notices. Root cause investigation. | &lt;1h suspend LLM component |
| P2 — MEDIUM | Drift alert: input feature distribution shift &gt;15% | Investigation initiated. Retraining evaluation. Daily monitoring until resolved. | &lt;4h response; &lt;5 day resolution |
| P2 — MEDIUM | HITL queue backlog &gt;200 cases | Additional analyst resource assigned. Queue processing time monitored hourly. | &lt;4h resource response |
| P3 — LOW | Single decision complaint / appeal received | Standard appeal process initiated. Human credit analyst reviews within 5 business days. | 5 business days |

### User Disclosure Documentation

**UDD-001**

Owner: Legal + Product Manager | Phase: Phase 7: Deployment

**Customer-Facing Disclosure** (approved text)

Your credit application is assessed using an automated AI system that analyses your financial history and alternative data to make a credit decision. You have the right to request human review of any automated decision. Please contact us at [appeals@bank.com] or call [0800-XXX-XXXX] to exercise this right.

**Adverse Action Notice Template**

We have been unable to approve your credit application at this time. The primary reasons for this decision are: [SHAP Reason Code 1: e.g., "Insufficient credit history over the past 24 months"]. [SHAP Reason Code 2]. [SHAP Reason Code 3]. This decision was made by an AI system. You have the right to request a human review. Reference: [Decision ID: DEC-XXXXXXX].

**Internal Deployer Disclosure**

This AI system (CreditRisk-XGB-v1.0) is classified as HIGH RISK under the EU AI Act. Human oversight is mandatory for all decisions below 70% confidence. The system may not be used outside of UK retail lending applications. Bias monitoring reports are produced monthly and reviewed by the AI Governance Council.

**Right to Explanation Implementation**

Every rejected applicant receives: (1) Top 3 SHAP-grounded reason codes in plain English. (2) Written appeal right with 30-day response SLA. (3) Alternative product suggestions where appropriate.

AI Act Article 13 Compliance: Instructions for deployers provided. System purpose, accuracy, limitations, human oversight requirements, and data sources documented. Legal review: COMPLIANT (Patel &amp; Morrison, 2 May 2026).

---

## Phase 8: Monitor, Audit & Retire

**Quarterly Governance Review + Annual Compliance Certification**

Maintain ongoing trustworthiness through continuous monitoring, audits, and disciplined retirement.

**Inputs to this phase:**

- Runtime monitoring data
- Deployment Runbook (DRB-001)
- Audit Log Configuration (ALC-001)
- Compliance Obligation Matrix (COM-001)

**Outputs from this phase:**

- Monthly Monitoring Report (MMR-001)
- Drift Alert Log (DAL-001)
- Quarterly Audit Report (QAR-001)
- Regulatory Change Log (RCL-001)
- Model Sunset Plan (MSP-001)

### Monthly Monitoring Report

**MMR-001**

Owner: MLOps Engineer + Ethics Lead | Phase: Phase 8: Monitor

**Report Period:** May 2026 (Month 1 post-deployment)

**Report Prepared By:** Priya Patel (MLOps) + Dr. Amara Diallo (Ethics)

**Overall Status:** GREEN — All metrics within thresholds

| **Metric** | **Threshold / Target** | **May 2026 Actual** | **Alert Level** | **Status** |
|---|---|---|---|---|
| Model Accuracy (AUC-ROC) | 0.83 (deployment baseline) | 0.827 | 0.79 (alert) | GREEN — Within 0.4% of baseline |
| Decision Volume | 50,000/month (expected) | 47,832 | &lt;30,000 or &gt;70,000 | GREEN — Within expected range |
| HITL Trigger Rate | 8% (Phase 4 target) | 7.3% | &gt;15% (model degradation signal) | GREEN |
| Demographic Parity Delta | &lt;2.0pp (threshold) | 1.7pp | 2.0pp (threshold) | GREEN — 0.3pp headroom; WATCH |
| LLM Hallucination Rate (SHAP mismatch) | &lt;1% (target) | 0.4% | &gt;2% (alert) | GREEN |
| Constitutional Compliance Rate | 100% (Phase 6 baseline) | 99.7% | &lt;98% (alert) | GREEN |
| Adverse Action Notice Coverage | 100% | 100% | &lt;100% (critical fail) | GREEN |
| Mean Inference Latency (p99) | 200ms (SLA) | 143ms | 250ms (breach) | GREEN |
| Cost per Decision | £0.0034 (budget) | £0.0031 | &lt;£0.005 (budget breach) | GREEN |
| Open Incidents | 0 P0/P1 | 0 P0, 0 P1, 1 P2 (resolved) | Any P0 = immediate alert | GREEN |

**Actions Required**

WATCH on demographic parity delta (1.7pp, threshold 2.0pp). Increase monitoring frequency for protected group approval rates. No model changes required at this time.

**Next Review Date**

4 June 2026

### Model Sunset Plan

**MSP-001**

Owner: AI Governance Council | Phase: Phase 8: Retire

| **Model to Retire** | CreditRisk-XGB-v1.0 (example: when replaced by v2.0) |
|---|---|
| **Planned Sunset Date** | To be determined — triggered by: (1) Model drift breach; (2) Regulatory change requiring new architecture; (3) Successor model Phase 6 approval |

**Sunset Triggers**

AUC-ROC decline below 0.79 for 2 consecutive months; Demographic parity delta exceeds 2.0pp; Successor model CreditRisk-XGB-v2.0 approved.

**Data Retention Post-Sunset**

Training data: retained 5 years per DS-001. Inference logs: retained 7 years (FCA requirement). Model artifacts: archived in MLflow, not deleted — required for regulatory enquiry response.

**Lineage Preservation**

OpenLineage graphs retained indefinitely. All data-to-model-to-decision lineage preserved for audit trail. Accessible via Atlan data catalog.

**Customer Impact Management**

All in-flight applications processed before sunset. No customer disruption. Transition to successor model tested in shadow mode for 30 days minimum.

**Regulatory Notification**

FCA notified of system retirement 60 days in advance. EU AI Act post-market surveillance report filed at retirement.

---

## Related

- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — Part 1: Development & Evaluation (Phase 5-6)
- [./04-aidlc-artifacts-development-to-retirement-ea-artifacts.md](./04-aidlc-artifacts-development-to-retirement-ea-artifacts.md) — Part 3: Enterprise Architecture Artifacts
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — Phases 1–4 (Discovery through Architecture)
- [../03-aidlc-artifacts-togaf-foundation-to-technology.md](../03-aidlc-artifacts-togaf-foundation-to-technology.md) — TOGAF ADM Preliminary through Technology phases
- [../04-aidlc-artifacts-togaf-migration-to-ea.md](../04-aidlc-artifacts-togaf-migration-to-ea.md) — TOGAF ADM Migration through EA Cross-Cutting artifacts

## Sources

None currently documented.
