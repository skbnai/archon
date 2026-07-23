---
title: "AIDLC Lifecycle Artifacts: Enterprise Architecture Artifacts"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-development-to-retirement-part3
maturity: practitioner
personas: [architect, engineer, manager, governance]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, ai-development, artifacts, enterprise-architecture, governance, templates]
sources: []
---

# AIDLC Lifecycle Artifacts: Enterprise Architecture Artifacts

Part 3 of 3 — continues from [Part 2: Deployment, MLOps & Retirement (Phase 7-8)](./03-aidlc-artifacts-development-to-retirement-deployment-mlops-retirement.md).

Cross-lifecycle artifacts maintained by the EA team and AI Governance Council continuously alongside every AIDLC phase.

**Audience:** Enterprise Architects, ML Engineers, MLOps Engineers, Data Scientists, Compliance Teams

**Coverage:** Enterprise Architecture Artifacts · Cross-Phase Governance

**As of:** 2026

---

## Enterprise Architecture Artifacts

**Continuous — AI Governance Council**

Cross-lifecycle artifacts maintained by the EA team and AI Governance Council.

**Inputs:**

- All AIDLC Phase Artifacts
- Business Strategy
- Regulatory Frameworks (NIST AI RMF, EU AI Act, ISO 42001)

**Outputs:**

- AI System Inventory (ASI-001)
- AI Capability Map (ACM-001)
- Agent Action Boundary Register (AABR-001)
- AI Architecture Decision Record EA (EADR-001)
- Data Lineage Map (DLM-001)

### AI System Inventory

**ASI-001**

Owner: AI Compliance Lead | Phase: Cross-Phase

| **Use Case ID** | **System Name** | **Risk Tier** | **AIDLC Phase** | **Business Owner** | **Regulations** | **Platform** |
|---|---|---|---|---|---|---|
| AUC-2026-FIN-047 | Credit Risk AI Scoring Model | T2 — HIGH RISK | Phase 7 (Production) | Sarah Chen (VP Credit Risk) | EU AI Act, FCA, UK GDPR | Azure ML + AKS |
| AUC-2026-OPS-012 | Customer Service Copilot | T3 — Limited Risk | Phase 7 (Production) | Lena Hoffmann (VP Ops) | EU AI Act Art. 50 | Azure OpenAI |
| AUC-2026-MKT-008 | Campaign Targeting Model | T4 — Minimal Risk | Phase 5 (Development) | Ahmed Al-Rashid (CMO) | GDPR profiling consent | AWS SageMaker |
| AUC-2026-HR-003 | CV Screening Assistant | T2 — HIGH RISK | Phase 2 (Feasibility — HOLD) | Maria Santos (CHRO) | EU AI Act Annex III Cat.1 | TBD |
| AUC-2026-SEC-019 | Fraud Detection Engine | T2 — HIGH RISK | Phase 8 (Monitor) | John Kim (CISO) | EU AI Act, PCI-DSS, FCA | GCP Vertex AI |

**Last Updated:** 8 May 2026

**Next Review:** 8 June 2026 (monthly update cycle)

**Maintained In:** Collibra AI Data Catalog — accessible to all AI Governance Council members and EA team

### Agent Action Boundary Register

**AABR-001**

Owner: AI Architect + Security Architect | Phase: Cross-Phase

**Purpose**

Defines the permitted tools, API endpoints, data namespaces, and action types for each deployed AI agent. Source of truth for runtime Zero Trust access control.

**Enforcement**

HashiCorp Vault + OPA (Open Policy Agent) — agent presents signed manifest; Vault validates permissions; OPA enforces at every tool call

| **Agent ID** | **System Name** | **Permitted Actions** | **Trust Level / HITL** | **Hard Boundaries** | **Business Owner** |
|---|---|---|---|---|---|
| AGT-FIN-001 | CreditRisk-XGB-v1.0 | READ: bureau-api, utility-api, temenos-api; WRITE: decision-log-stream; DENIED: all other endpoints | ATF Level 1 — All decisions require core banking confirmation | None above £5,000 credit limit | James Hartley (CRO) |
| AGT-OPS-001 | CSCopilot-v2.1 | READ: crm-api, kb-search-api; WRITE: ticket-api (create only); DENIED: payment-api, account-modify-api | ATF Level 3 — Refunds &gt;£100 require HITL | No payment initiation; No account modification | Lena Hoffmann (VP Ops) |
| AGT-IT-001 | InfraAgent-v1.0 | READ: cloudwatch, github-api; WRITE: github-api (PR only); DENIED: production deploy, IAM changes | ATF Level 2 — All code changes require human PR approval | No direct production deploys; No IAM changes | Marcus Thompson |

### Data Lineage Map

**DLM-001**

Owner: Data Architect | Phase: Cross-Phase (Updated each Phase)

**Lineage Tracking Platform:** OpenLineage + Apache Atlas + Atlan Data Catalog

**Lineage Scope:** End-to-end: Source data → Ingestion → Feature engineering → Training → Model artifact → Inference → Decision log → Audit trail

| **Node** | **Source** | **Data Product** | **Transformation** | **Destination** | **Governance Controls** |
|---|---|---|---|---|---|
| L1 | Equifax Bureau API | Raw credit records | Ingestion pipeline (Azure Data Factory) | S3://raw/equifax-YYYY-MM-DD/ | Encrypted; PII Tier 2; Access: data-eng group |
| L2 | S3://raw/equifax-* | Cleaned + standardised bureau data | Feature engineering job (feature_engineering.py v1.3) | S3://features/bureau-std/ | DVC tagged v1.0; quality score 98.7% |
| L3 | S3://features/bureau-std/ + utility + rental | Merged feature matrix | Feature merge pipeline (merge_pipeline.py v2.1) | Feast feature store: credit-scoring-features v1.0 | Feast versioned; training/serving consistent |
| L4 | Feast: credit-scoring-features v1.0 | Trained XGBoost model | Training job (xgb_trainer.py v1.4) — EXP-023 | MLflow: CreditRisk-XGB-v1.0 (SHA: a7f3d2c) | Signed; EU AI Act Art.11 documentation |
| L5 | CreditRisk-XGB-v1.0 + Application (live) | Credit decision + SHAP values | Inference service (KServe endpoint) | Decision log stream (Azure Event Hubs) | Every decision logged; immutable audit trail |
| L6 | Decision log stream | Adverse action notice | LLM pipeline (AdverseAction-GPT-v1.0) | CRM: adverse-action-notices collection | SHAP verification gate applied; FCA compliant |
| L7 | All above | Regulatory audit package | Audit assembly pipeline | Splunk SIEM + Collibra catalog | 7-year retention; FCA accessible |

**EU AI Act Compliance**

Full lineage from Article 10 (data governance) through Article 12 (logging) documented and machine-readable via OpenLineage API. Accessible to National Competent Authority on request.

---

## Related

- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — Part 1: Development & Evaluation (Phase 5-6)
- [./03-aidlc-artifacts-development-to-retirement-deployment-mlops-retirement.md](./03-aidlc-artifacts-development-to-retirement-deployment-mlops-retirement.md) — Part 2: Deployment, MLOps & Retirement (Phase 7-8)
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — Phases 1–4 (Discovery through Architecture)
- [../03-aidlc-artifacts-togaf-foundation-to-technology.md](../03-aidlc-artifacts-togaf-foundation-to-technology.md) — TOGAF ADM Preliminary through Technology phases
- [../04-aidlc-artifacts-togaf-migration-to-ea.md](../04-aidlc-artifacts-togaf-migration-to-ea.md) — TOGAF ADM Migration through EA Cross-Cutting artifacts

## Sources

None currently documented.
