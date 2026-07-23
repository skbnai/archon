---
title: "AIDLC TOGAF Artifacts: Opportunities, Migration & Implementation Governance (Phase E-G)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-togaf-migration-to-ea
maturity: expert
personas: [architect, governance, manager]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: ["docs/ai-development/aidlc/AIDLC_Artifact_Reference_Library_Part4_TOGAF_Migration_to_EA_CrossCutting.md"]
tags: [aidlc, enterprise-architecture, togaf, adm, ai-first, governance, migration, templates]
sources: []
---

# AIDLC TOGAF Artifacts: Opportunities, Migration & Implementation Governance (Phase E-G)

Part 1 of 3 — continues to [Part 2: Change Management & Cross-Cutting Artifacts (Phase H)](./parts/08-aidlc-artifacts-togaf-change-management-cross-cutting.md).

Enterprise architecture artifacts for TOGAF ADM Opportunities & Migration Phase E/F and Implementation Governance Phase G, with AI-First extensions.

**Audience:** Enterprise Architects, Chief Technology Officers, Governance Leaders, AI Governance Council Members

**Coverage:** TOGAF ADM Opportunities & Migration (E/F) · Implementation Governance (G) · AI-First Extensions

**As of:** 2026

---

## TOGAF ADM Opportunities & Migration Phase E/F

**ARTIFACTS: AUP-001 · ARTA-001 · ARM-001**

### AI Use Case Portfolio & Sequencing Plan

**AUP-001** (AI-First Extension)

Owner: Chief Architect + AI CoE Lead | ADM Phase: EF | TOGAF 10 + AI-First Extension

| **AI Use Case** | **Business Value** | **Strategic Fit** | **Risk Tier** | **Est. Duration** | **Current Status** | **Next Milestone** | **Target Live** | **Key Constraints** |
|---|---|---|---|---|---|---|---|---|
| Credit Risk AI Scoring | £7.3M p.a. | HIGH | T2 HIGH | 14 months | ARB Approved Q4 2025 | Q1 2026 Phase 3 | Q3 2026 Phase 7 | Foundation use case; FRIA complete; external audit booked |
| Fraud Detection Governance Uplift | £2.1M (risk reduction) | HIGH | T2 HIGH | 3 months | Production already — governance gap | Q1 2026 Governance Audit | Q2 2026 Complete | Existing system; compliance uplift only; fast track |
| Customer Service Copilot Expansion | £1.4M incremental | MEDIUM | T3 LIMITED | 6 months | Live v2.1 — expand to more channels | Q2 2026 Scope Extension | Q3 2026 Full deployment | Low risk; accelerated AIDLC track |
| Campaign Targeting AI | £0.9M p.a. | MEDIUM | T4 MINIMAL | 9 months (in progress) | Phase 5 Development | Already in progress | Q3 2026 Phase 7 | AIDLC-Lite track; consent management focus |
| Developer Copilot (GitHub Copilot) | Productivity — unmeasured | MEDIUM | T4 MINIMAL | 1 month (register only) | Shadow AI — in use | Immediate registration | Done — ongoing monitoring | Register in ASI-001; code audit policy; AIDLC-Lite |
| CV Screening Assistant | £0.6M (efficiency) | LOW | T2 HIGH | 18+ months | ON HOLD — FRIA required | FRIA Q2 2026 | Subject to FRIA | EU AI Act Annex III; highest scrutiny; FRIA outcome gating |

**Sequencing Rationale**

Risk-adjusted sequencing: (1) High business value + compliance foundation first (Credit Risk). (2) Production gap-fills second (Fraud governance). (3) Low-risk progressions third. (4) High-scrutiny on hold until governance matures.

**Architecture Dependencies**

Credit Risk AI (Phase 7) is the REFERENCE IMPLEMENTATION. MLOps platform, LLM Gateway, vector database, and monitoring stack must be operational before any subsequent AI system can reach Phase 7.

### AI-Readiness Transition Architecture

**ARTA-001** (AI-First Extension)

Owner: Chief Architect + Solution Architects | ADM Phase: EF | TOGAF 10 + AI-First Extension

| **Architecture State** | **Data Architecture** | **MLOps / LLMOps** | **Application Architecture** | **Agent Architecture** | **Security Architecture** | **Governance** | **AI Maturity Level** |
|---|---|---|---|---|---|---|---|
| Baseline (Q1 2026) | Data Lake (unstructured, no lineage) | No MLOps; manual training+deploy | LLM calls via direct API (no gateway) | No agent infrastructure | Perimeter only; no ZTA | Ad hoc; no ARB process | L1 (Initial) — McKinsey AI Maturity |
| Transition 1 (Q2 2026) | Lakehouse + DVC versioning; 2 domains on Mesh; OpenLineage installed | MLflow model registry; Azure ML pipelines; Feast MVP | Kong LLM Gateway live; Lakera Guard + Presidio active | LangGraph framework standard; OPA agent policy MVP | Agent identity registry; HashiCorp Vault deployed | ARB gates for AI systems; AGP published | L2 (Developing) |
| Transition 2 (Q3 2026) | Full Data Mesh (6 domains); Weaviate production; Feature Store certified | Full LLMOps monitoring: Arize AI, hallucination detection, drift alerts | RAG pipelines production-grade; MCP standard adopted for new APIs | 3 production agents; ATF trust levels active; circuit breakers live | Zero Trust for agents fully implemented; MAESTRO threat model done | ISO/IEC 42001 gap assessment; EU AI Act compliance audit | L3 (Scaling) |
| Target State (Q4 2026) | Enterprise AI Data Catalog (Atlan); automated lineage; all AI data products quality-certified | Autonomous retraining MVP; unified MLOps+LLMOps platform | Agent mesh production; full MCP integration; semantic caching | Agentic workflows in production across 3 business domains | Full MAESTRO controls; quarterly zero trust review | ISO/IEC 42001 certified; EU AI Act high-risk documented | L4 (Optimising) |

---

## TOGAF ADM Implementation Governance Phase G

**ARTIFACTS: ACC-001 · ASRF-001 · ARB-001**

### Architecture Compliance Checklist

**ACC-001**

Owner: Architecture Review Board | ADM Phase: G | TOGAF 10 + AI-First Extension

**Purpose:** Every AI system must complete this checklist before the ARB grants Architecture Compliance Certificate (ACC). This checklist integrates TOGAF Phase G governance with AIDLC Phase 6 (Evaluation) gate requirements.

| **Compliance Artefact** | **AIDLC Phase** | **Requirement** | **Evidence Provided** | **Status** |
|---|---|---|---|---|
| Use Case Charter (AUC-001) | AIDLC Phase 1 | AI use case formally defined with business value hypothesis, risk flags, and sponsor sign-off | AUC-2026-FIN-047 v1.2 — Approved 19 Feb 2026 | PASS |
| Risk Classification (RCS-001) | AIDLC Phase 1 | EU AI Act risk tier assigned; governance intensity set | RCS-001 — T2 HIGH RISK — 22 Feb 2026 | PASS |
| Feasibility Report (FR-001) | AIDLC Phase 2 | Technical and organisational feasibility confirmed | FR-001 v1.0 — 5 March 2026 | PASS |
| FRIA Completed (FRIA-001) | AIDLC Phase 2 | Fundamental Rights Impact Assessment completed for T2 systems | FRIA-001 — Signed CRO + Ethics Lead 10 Mar 2026 | PASS |
| Architecture Decision Records (ADR) | AIDLC Phase 4 | All key architecture decisions documented with options and rationale | ADR-2026-FIN-047-001 — ARB Approved 2 Apr 2026 | PASS |
| Constitutional AI Policy (CAP) | AIDLC Phase 4 | Constitutional AI Policy approved by AI Governance Council | CAP-001 v1.0 — AI Gov Council 5 Apr 2026 | PASS |
| Red Team Report (RTR-001) | AIDLC Phase 6 | All HIGH severity findings resolved; MEDIUM findings remediated or accepted | RTR-001 — All HIGH resolved 22 Apr 2026 | PASS |
| Fairness Evaluation (FER-001) | AIDLC Phase 6 | All fairness metrics within thresholds; external audit completed for T2 | FER-001 — AJI External Audit 22 Apr 2026 | PASS |
| Constitutional Compliance Audit (CCA) | AIDLC Phase 6 | All 8 Constitutional AI Principles assessed and PASS | CCA-001 — 100% compliance 25 Apr 2026 | PASS |
| AI System Inventory Registration | EA Cross-cutting | System registered in ASI-001 with complete metadata | ASI-001 — AUC-2026-FIN-047 registered | PASS |
| Agent Action Boundary Register | EA Cross-cutting | Agent boundaries documented for any agentic components | AABR-001-EA — Non-agent system; N/A | N/A |
| Data Lineage Map (DLM-001) | AIDLC Phase 3 | End-to-end data lineage documented and accessible via Atlan | DLM-001 — All 7 nodes documented | PASS |
| Deployment Runbook (DRB-001) | AIDLC Phase 7 | Blue/green deployment plan with rollback procedures documented | DRB-001 — MLOps Lead sign-off 30 Apr 2026 | PASS |
| User Disclosure Documentation | AIDLC Phase 7 | Customer-facing AI disclosure text legal-reviewed and approved | UDD-001 — Legal sign-off 2 May 2026 | PASS |

**ARB Decision**

ARCHITECTURE COMPLIANCE CERTIFICATE GRANTED — CreditRisk-XGB-v1.0. Authorised for deployment. Approval: Dr. Priya Mehta (Chief Architect), James Hartley (CRO), AI Governance Council — 5 May 2026.

**Conditions of Certificate**

1. Monthly Monitoring Reports (MMR-001) reviewed by ARB quarterly.
2. Annual external fairness audit maintained.
3. Any material model change requires new ACC application.

### AI System Registration Form

**ASRF-001** (AI-First Extension)

Owner: Business Owner + AI CoE | ADM Phase: G | TOGAF 10 + AI-First Extension

| **System ID (assigned by AI CoE)** | *AUC-2026-FIN-047* |
|---|---|
| **System Name** | *Credit Risk AI Scoring Model* |
| **Business Owner** | *Sarah Chen, VP Credit Risk, Retail Banking Division* |
| **Technical Owner** | *Dr. Nina Kowalski, Head of AI CoE* |
| **System Description** | *ML-based credit scoring model (XGBoost) with LLM adverse action notice generator (GPT-4o fine-tuned). Used for automated credit decisions on UK retail lending applications (50,000/month).* |
| **AI Category** | *ML Classification (primary) + Generative AI (adverse action narrative)* |
| **EU AI Act Risk Tier** | *TIER 2 — HIGH RISK (Annex III, Category 5b: creditworthiness assessment)* |
| **Regulated By** | *FCA, PRA, ICO, EU AI Act National Competent Authority* |
| **Personal Data Processed** | *YES — Applicant financial history, utility payment history, rent history. Processing basis: Art. 6(1)(b) GDPR (contractual necessity).* |
| **Third-Party AI Components** | *Equifax Credit Bureau API, GPT-4o (Azure OpenAI), Lakera Guard, Microsoft Presidio* |
| **Deployment Environment** | *Production — Azure Kubernetes Service (AKS), UK South region* |
| **Date Registered** | *5 May 2026* |

**ACC Certificate Number**

ACC-2026-FIN-047-001 (Architecture Compliance Certificate granted 5 May 2026)

---

## Related

- [01-aidlc-artifacts-discovery-to-model.md](01-aidlc-artifacts-discovery-to-model.md) — AIDLC Phases 1–4 artifact templates
- [02-aidlc-artifacts-development-to-retirement.md](02-aidlc-artifacts-development-to-retirement.md) — AIDLC Phases 5–8 artifact templates
- [03-aidlc-artifacts-togaf-foundation-to-technology.md](03-aidlc-artifacts-togaf-foundation-to-technology.md) — TOGAF ADM Preliminary through Technology phases
- [parts/08-aidlc-artifacts-togaf-change-management-cross-cutting.md](./parts/08-aidlc-artifacts-togaf-change-management-cross-cutting.md) — Part 2: Change Management & Cross-Cutting Artifacts (Phase H)
- [parts/09-aidlc-artifacts-togaf-artifact-cross-reference.md](./parts/09-aidlc-artifacts-togaf-artifact-cross-reference.md) — Part 3: Artifact Cross-Reference

## Sources

None currently documented.
