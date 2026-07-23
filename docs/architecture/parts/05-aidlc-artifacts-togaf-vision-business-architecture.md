---
title: "AIDLC TOGAF Artifacts: Vision & Business Architecture (Phase A-B)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-togaf-foundation-to-technology-part2
maturity: expert
personas: [architect, governance, manager]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, enterprise-architecture, togaf, adm, ai-first, governance, templates]
sources: []
---

# AIDLC TOGAF Artifacts: Vision & Business Architecture (Phase A-B)

Part 2 of 4 — continues from [Part 1: Preliminary Phase](../03-aidlc-artifacts-togaf-foundation-to-technology.md), continues to [Part 3: Data & Application Architecture (Phase C1-C2)](./06-aidlc-artifacts-togaf-data-application-architecture.md).

Enterprise architecture artifacts for TOGAF ADM Architecture Vision Phase A and Business Architecture Phase B, with AI-First extensions.

**Audience:** Enterprise Architects, Chief Technology Officers, Governance Leaders, AI Governance Council Members

**Coverage:** TOGAF ADM Architecture Vision Phase A · Business Architecture Phase B · AI-First Extensions

**As of:** 2026

---

## TOGAF ADM Architecture Vision Phase A

**ARTIFACTS: SAW-001 · ACA-001 · AVD-001**

### Statement of Architecture Work

**SAW-001**

Owner: Chief Architect | ADM Phase: A | TOGAF 10 + AI-First Extension

**Work Definition**

| **Architecture Work Title** | *GlobalBank AI Transformation Programme — Phase 1: Core Banking AI Integration* |
|---|---|
| **Sponsoring Executive** | *Marcus Chen, Chief Operating Officer* |
| **Architecture Work Description** | *Design and govern the enterprise architecture for integrating AI systems into core banking operations: credit risk scoring, customer service automation, fraud detection. Encompasses 5 AI use cases (see ACA-001), full AIDLC lifecycle governance, and technology platform modernisation to support AI at scale.* |
| **Scope** | *IN SCOPE: UK Retail Banking division, core banking AI systems, data architecture for AI, MLOps platform, agent architecture. OUT OF SCOPE: International operations (Year 2), mortgage AI (separate programme), investment banking (separate governance).* |
| **Constraints** | *1. EU AI Act compliance required for all credit, HR and fraud systems. 2. FCA operational resilience rules apply. 3. Core banking system (Temenos) cannot be replaced in this programme. 4. Maximum cloud budget: £2.8M/year.* |
| **Assumptions** | *Alternative data partners (utility, rent) contracts will be signed by Q2 2026. Azure ML platform will remain enterprise standard for ML workloads. LLM provider contracts available under existing Microsoft EA.* |
| **Deliverables** | *Architecture Vision (AVD-001), Business Architecture (Phase B), Data Architecture (Phase C1), Application Architecture (Phase C2), Technology Architecture (Phase D), Migration Plan (Phase F), Governance Framework (Phase G)* |
| **Timeline** | *Phase A-D: Q1 2026 (12 weeks). Phase E-F: Q2 2026 (8 weeks). Phase G onwards: ongoing.* |
| **Approved By** | *Dr. Priya Mehta (Chief Architect) · Marcus Chen (COO) · AI Governance Council — 22 January 2026* |

### AI Capability Assessment

**ACA-001** (AI-First Extension)

Owner: Chief Architect + AI Lead | ADM Phase: A | TOGAF 10 + AI-First Extension

This artifact is not in standard TOGAF 10. It provides the AI capability inventory and maturity baseline that drives all subsequent AI-impacted architecture decisions.

| **AI Use Case** | **EU AI Act Tier** | **AIDLC Phase** | **Model Type** | **Strategic Status** | **Priority** | **Compliance Requirements** |
|---|---|---|---|---|---|---|
| Credit Risk AI Scoring | T2 — HIGH RISK | Phase 2 (Feasibility) | XGBoost + LLM | Foundational — must deliver | Priority 1 | FRIA required; FCA regulated |
| Customer Service Copilot | T3 — LIMITED RISK | Phase 7 (Production) | GPT-4o RAG | Already live — extend scope | Priority 2 | EU AI Act Art. 50 transparency |
| Fraud Detection AI | T2 — HIGH RISK | Phase 8 (Monitor) | Ensemble + LSTM | Mature — governance uplift | Priority 1 | PCI-DSS; FCA SYSC 23 |
| CV Screening Assistant | T2 — HIGH RISK | Phase 2 (HOLD) | LLM + Embedding | On hold — FRIA first | Priority 3 | EU AI Act Annex III Cat.1 |
| Campaign Targeting AI | T4 — MINIMAL RISK | Phase 5 (Dev) | XGBoost | Progressing normally | Priority 4 | GDPR profiling consent |
| Developer Copilot (GitHub Copilot) | T4 — MINIMAL RISK | Phase 7 (Prod) | Codex/GPT-4o | Shadow AI — register &amp; govern | Priority 3 | AIDLC-Lite track |

**AI Maturity Baseline:** McKinsey AI Maturity Level 2 of 5 (Developing). Proof-of-concept capability exists. Production MLOps immature. Governance framework nascent. Target: Level 3 (Scaling) by end 2026.

**Shadow AI Exposure:** 27 unregistered AI tools identified in SaaS survey (GitHub Copilot, Grammarly, Otter.ai, various ChatGPT integrations). All to be assessed and registered in AI System Inventory within 30 days.

**Architecture Readiness:** Data architecture: MEDIUM (data lake exists, lineage immature). Application: MEDIUM (microservices partially adopted). MLOps: LOW (no enterprise platform). Governance: LOW (nascent). Security: LOW (no zero trust).

### Architecture Vision Document

**AVD-001**

Owner: Chief Architect | ADM Phase: A | TOGAF 10 + AI-First Extension

| **Vision Statement** | *By end 2026, GlobalBank will operate a trusted, explainable, and regulatorily compliant AI capability that delivers £7.3M+ annual value from credit risk automation, reduces manual review by 35%, and serves as a model for responsible AI in UK financial services.* |
|---|---|
| **Target Architecture Descriptor** | *AI-First Enterprise Architecture: 7-layer reference stack (L1 GPU Infrastructure → L7 Business &amp; Governance), AIDLC lifecycle for all AI systems, Data Mesh for AI data products, Zero Trust for AI agents, TOGAF 10 ADM as the governance backbone.* |
| **Key Architecture Principles** | *1. Architecture before AI (no AI before the foundation is ready). 2. Data as first-class product. 3. Explainability by design. 4. Zero Trust at every layer. 5. Governance proportionate to risk. 6. Open standards over vendor lock-in.* |
| **Business Outcomes** | *60-second credit decisions (vs 72 hours), &lt;5% false rejection rate (vs 12%), 100% adverse action explanation coverage, £7.3M ROI Year 1, ISO/IEC 42001 certification Q4 2026.* |
| **Architecture Risks** | *1. Legacy Temenos integration complexity (HIGH). 2. EU AI Act compliance timeline (HIGH). 3. Alternative data vendor contracts (MEDIUM). 4. MLOps talent gap (MEDIUM). 5. Shadow AI exposure (LOW-MEDIUM).* |
| **ARB Approved** | *5 February 2026 — Architecture Review Board unanimous approval* |

---

## TOGAF ADM Business Architecture Phase B

**ARTIFACTS: ACM-001 · HATB-001 · AOM-001 · WIA-001**

### AI Capability Map

**ACM-001** (AI-First Extension)

Owner: Enterprise Architect + Business Analysts | ADM Phase: B | TOGAF 10 + AI-First Extension

This AI-First extension extends the standard TOGAF Business Capability Map to include AI capabilities, their risk classification, AIDLC status, and Human-AI task boundary designation.

| **Business Capability** | **Domain** | **AI System** | **Risk Tier** | **Human-AI Boundary** | **AIDLC Status** | **Target Date** |
|---|---|---|---|---|---|---|
| Credit Decision | Retail Banking | Credit Risk AI Scoring | T2 HIGH RISK | AI-Primary with HITL for &lt;70% confidence cases | Phase 2 | Phase 4 Q2 2026 |
| Adverse Action Explanation | Retail Banking | LLM Adverse Action Generator | T2 HIGH RISK | AI-Primary (SHAP-grounded); human review on appeal | Phase 2 | Phase 7 Q3 2026 |
| Customer Enquiry Resolution | Operations | Customer Service Copilot | T3 LIMITED | AI-Augmented; human escalation for complex cases | Phase 7 (LIVE) | Scope extension Q2 2026 |
| Fraud Transaction Detection | Security | Fraud Detection Ensemble | T2 HIGH RISK | AI-Primary; all alerts to human analyst | Phase 8 (LIVE) | Governance uplift Q2 2026 |
| Candidate CV Screening | HR | CV Screening Assistant | T2 HIGH RISK | AI-Recommend ONLY; human decides | Phase 2 (HOLD) | Subject to FRIA outcome |
| Marketing Segmentation | Marketing | Campaign Targeting AI | T4 MINIMAL | AI-Primary; no individual impact | Phase 5 | Phase 7 Q3 2026 |
| Developer Code Assistance | IT/Engineering | GitHub Copilot (registered) | T4 MINIMAL | AI-Augmented; developer reviews all output | Phase 7 (LIVE) | Registered; AIDLC-Lite |
| Architecture Documentation | EA | EA AI Assistant (proposed) | T4 MINIMAL | AI-Augmented; architect validates | Phase 1 | Proposed for Q3 2026 |

### Human-AI Task Boundary Map

**HATB-001** (AI-First Extension)

Owner: Business Architect + Ethics Lead | ADM Phase: B | TOGAF 10 + AI-First Extension

This AI-First extension documents the precise boundary between human and AI decision authority for every AI-impacted business process. Mandatory for all TIER 1–2 systems. This artifact is reviewed by the AI Governance Council and forms the basis for HITL design in AIDLC Phase 4.

| **Process Step** | **Human-Only Tasks** | **AI-Only Tasks** | **HITL Trigger &amp; Human Decision Role** | **SLA** |
|---|---|---|---|---|
| Credit Application Intake | Capture applicant data; verify identity | AI validates data completeness and identity (automated) | Human if identity verification fails (manual override required) | Instant / 5 min |
| Initial Credit Score | N/A (fully automated for T4 decisions) | AI scores application (XGBoost model); assigns confidence | Human review for ALL applications &lt;70% confidence (~8% of volume) | &lt;60 seconds / 4 hours (HITL) |
| Adverse Action Notice | N/A | AI generates SHAP-grounded rejection notice (LLM) | Human verifies reason codes before delivery if flagged by SHAP-LLM mismatch check | 2 min / 30 min (if flag) |
| Customer Appeal | Receive appeal; notify AI Governance Council | AI provides case summary and supporting SHAP evidence | Human credit analyst makes FINAL determination on ALL appeals | 5 business days |
| Bias Alert Response | Receive alert from monitoring system; notify CRO | AI produces demographic parity report automatically | Human (Ethics Lead + CRO) decides remediation action | 24 hours |
| Model Retirement Decision | N/A | AI drift monitoring flags retirement trigger threshold | Human (ARB + AI Governance Council) approves retirement timeline | 30-day process |

**HITL Design Principles**

1. Every consequential AI decision has a human escalation path.
2. Confidence thresholds are set conservatively (err toward HITL).
3. HITL queue capacity is resourced before deployment.
4. HITL effectiveness is monitored monthly.

**Approval Authority**

HATB-001 approved by: Dr. Amara Diallo (Ethics Lead), James Hartley (CRO), AI Governance Council — 1 March 2026.

### AI Operating Model

**AOM-001** (AI-First Extension)

Owner: Business Architect + HR | ADM Phase: B | TOGAF 10 + AI-First Extension

| **Organisational Unit** | **Type** | **Responsibilities** | **Operating Cadence** | **Accountable Owner** |
|---|---|---|---|---|
| AI Governance Council | Cross-functional steering body | Set AI policy; approve high-risk deployments; review AGPs; manage regulatory relationships | Monthly meetings + emergency sessions | James Hartley (CRO, Chair) |
| Architecture Review Board | EA governance body | Approve AI architecture decisions; enforce standards; review ADRs; conduct compliance assessments | Bi-weekly + ad hoc gate reviews | Dr. Priya Mehta (Chief Architect, Chair) |
| AI Centre of Excellence (CoE) | Central AI delivery team | Deliver AIDLC; operate MLOps platform; publish AI standards; coach business teams | Permanent team of 12 FTE | Dr. Nina Kowalski (Head of AI CoE) |
| Domain AI Squads | Embedded AI teams in business units | Execute AI use cases within domain; own business data products; operate production AI systems | Permanent; 2–4 FTE per domain | Domain VPs + AI CoE matrix reporting |
| Model Risk Management | Risk oversight function | Independent model validation; approve TIER 2 models; conduct ongoing model governance audits | Ad hoc (per model) + quarterly review | CRO direct report |
| Ethics &amp; Fairness Function | Independent advisory function | Conduct FRIAs; lead fairness evaluations; advise on AGP implementation; manage external ethics board | Per-use-case + ongoing monitoring | Dr. Amara Diallo (Ethics Lead) |
| MLOps Platform Team | Platform engineering function | Operate MLflow, Azure ML, LLM Gateway, vector database, monitoring stack for all AI systems | 24/7 production support + continuous improvement | Priya Patel (MLOps Lead) |

---

## Related

- [../03-aidlc-artifacts-togaf-foundation-to-technology.md](../03-aidlc-artifacts-togaf-foundation-to-technology.md) — Part 1: Preliminary Phase
- [./06-aidlc-artifacts-togaf-data-application-architecture.md](./06-aidlc-artifacts-togaf-data-application-architecture.md) — Part 3: Data &amp; Application Architecture (Phase C1-C2)
- [./07-aidlc-artifacts-togaf-technology-architecture.md](./07-aidlc-artifacts-togaf-technology-architecture.md) — Part 4: Technology Architecture (Phase D)
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — AIDLC Phases 1–4 artifact templates
- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — AIDLC Phases 5–8 artifact templates
- [../04-aidlc-artifacts-togaf-migration-to-ea.md](../04-aidlc-artifacts-togaf-migration-to-ea.md) — TOGAF ADM Migration through EA Cross-Cutting artifacts

## Sources

None currently documented.
