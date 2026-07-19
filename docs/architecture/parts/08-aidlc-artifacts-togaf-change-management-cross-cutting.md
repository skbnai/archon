---
title: "AIDLC TOGAF Artifacts: Change Management & Cross-Cutting Artifacts (Phase H)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-togaf-migration-to-ea-part2
maturity: expert
personas: [architect, governance, manager]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, enterprise-architecture, togaf, adm, ai-first, governance, templates]
sources: []
---

# AIDLC TOGAF Artifacts: Change Management & Cross-Cutting Artifacts (Phase H)

Part 2 of 3 — continues from [Part 1: Opportunities, Migration & Implementation Governance (Phase E-G)](../04-aidlc-artifacts-togaf-migration-to-ea.md), continues to [Part 3: Artifact Cross-Reference](./09-aidlc-artifacts-togaf-artifact-cross-reference.md).

Enterprise architecture artifacts for TOGAF ADM Architecture Change Management Phase H and EA Cross-Cutting Artifacts, with AI-First extensions.

**Audience:** Enterprise Architects, Chief Technology Officers, Governance Leaders, AI Governance Council Members

**Coverage:** TOGAF ADM Architecture Change Management (H) · EA Cross-Cutting Artifacts · AI-First Extensions

**As of:** 2026

---

## TOGAF ADM Architecture Change Management Phase H

**ARTIFACTS: ACR-001 · APR-001 · AIM-001**

### Architecture Change Request

**ACR-001**

Owner: Requestor + Architecture Review Board | ADM Phase: H | TOGAF 10 + AI-First Extension

| **Change Request ID** | *ACR-2026-FIN-047-002* |
|---|---|
| **Date Submitted** | *15 June 2026* |
| **Requestor** | *Dr. Nina Kowalski, Head of AI CoE* |
| **System Affected** | *CreditRisk-XGB-v1.0 (AUC-2026-FIN-047)* |
| **Change Title** | *Integrate Real-Time Rental Bureau Data (Experian API) — Model Retraining* |
| **Change Description** | *Add Experian Rental Bureau as a new alternative data source for credit scoring. Requires: (1) New data pipeline (rental-bureau-pipeline). (2) Feature engineering for 6 new rental features. (3) Model retraining with new features. (4) Fairness re-evaluation (new data source may affect demographic groups). (5) Red team re-assessment of new data pipeline.* |
| **Change Classification** | *SIGNIFICANT — New data source changes model behaviour and requires Phase 5-6 re-run for new features. Does NOT require full Phase 1-4 restart.* |
| **AIDLC Impact Assessment** | *Phases required: Phase 3 (Data Sheet update for rental data) → Phase 5 (Retrain with new features) → Phase 6 (Fairness re-evaluation, bias re-assessment) → Phase 7 (Re-deployment runbook). Estimated: 6 weeks.* |
| **Regulatory Notification Required** | *NO — change is additive, does not alter the fundamental model architecture or purpose. Legal review confirms no new regulatory obligations.* |
| **Architecture Risk Assessment** | *LOW-MEDIUM: (1) New data source may reveal unexpected bias (mitigated: mandatory re-run of FER-001). (2) Vendor reliability of Experian Rental Bureau API (mitigated: fallback to bureau-only scoring if API down).* |
| **ARB Decision** | *APPROVED with conditions: (1) FER-001 re-run must show no degradation in fairness metrics. (2) Rental data DPA signed before data ingestion. (3) Updated Data Sheet signed by Data Governance Board. — ARB 22 June 2026* |

### AI Portfolio Review Report

**APR-001** (AI-First Extension)

Owner: Chief Architect + AI CoE Lead | ADM Phase: H | TOGAF 10 + AI-First Extension

**Purpose:** Quarterly review of the full AI system portfolio. Aggregates monitoring data from all deployed systems, identifies patterns and risks, and makes portfolio-level architectural recommendations.

**Review Period:** Q2 2026 (April–June 2026)

**Portfolio Status:** 5 systems in production, 1 in development (Campaign Targeting), 1 on hold (CV Screening)

| **System** | **Tier** | **Status** | **RAG** | **Model Performance** | **Fairness Status** | **Incidents** | **Action Required** |
|---|---|---|---|---|---|---|---|
| CreditRisk-XGB-v1.0 | T2 | Production | GREEN | 0.827 AUC (↓0.3% from baseline; within threshold) | 1.7pp (threshold: 2.0pp) — WATCH | 0 P0, 0 P1, 1 P2 resolved | Rental data integration approved (ACR-002); no immediate action |
| CSCopilot-v2.1 | T3 | Production | GREEN | 4.3/5 CSAT (↑0.2 from Q1) | N/A (non-credit; no parity requirement) | 0 P0, 0 P1, 2 P3 resolved | Expand to mobile channel Q3; backlog prioritised |
| FraudDet-ENS-v3.1 | T2 | Production | AMBER | AUROC 0.94 (stable); TPR 91% (↓2% from Q1) | N/A (anomaly detection) | 1 P1 (false positive spike wk 4; resolved) — learning point | Investigate TPR degradation; retraining evaluation in progress |
| DevCopilot (GitHub Copilot) | T4 | Production | GREEN | Developer satisfaction 4.6/5; code review escalations: 3/month | N/A | 0 incidents | AIDLC-Lite compliance verified; shadow AI register clean |
| CampaignTarget-v0.3 | T4 | Development | N/A | In Phase 5 development; no production metrics | N/A | N/A | Phase 6 evaluation scheduled Q3; consent management integration on track |
| CVScreening (HOLD) | T2 | On Hold | N/A | Not deployed; FRIA in progress | N/A | N/A | FRIA expected Q3 2026; proceed only if FRIA clears |

**Portfolio-Level Risks**

1. Fraud Detection TPR degradation (AMBER) — prioritise retraining evaluation.
2. Credit Risk bias delta approaching threshold (WATCH) — increase monitoring frequency.

**Architecture Recommendations**

1. Fraud Detection model retraining approved — execute Phase 5 re-run by end Q3.
2. Strengthen fairness monitoring alerting: reduce bias delta alert threshold from 2.0pp to 1.8pp across all T2 systems.

**Next Portfolio Review**

Q3 2026 — 15 September 2026

---

## TOGAF ADM EA Cross-Cutting Artifacts

**ARTIFACTS: EADR-001 · AABR-EA-001 · ASI-EA-001 · RAIMP-001**

### EA Architecture Decision Record (AI-First)

**EADR-001**

Owner: Architecture Review Board | ADM Phase: EA | TOGAF 10 + AI-First Extension

**Purpose:** Documents enterprise-level architecture decisions that affect multiple AI systems or the AI platform itself. Distinct from AIDLC Phase 4 ADRs (which are use-case-specific). EA ADRs are binding on all teams and permanent record.

| **EA ADR ID** | *EADR-2026-PLAT-003* |
|---|---|
| **Title** | *LLM Provider Strategy: Multi-Provider via LiteLLM Router — Mandatory Standard* |
| **Status** | *ACCEPTED — Architecture Review Board — 15 March 2026* |
| **Decision Makers** | *Dr. Priya Mehta (Chief Architect), AI Governance Council, Technology Leadership* |
| **Context** | *GlobalBank has three AI systems consuming LLM APIs from three different providers (Azure OpenAI, Anthropic, self-hosted Llama 3). Without standardisation, each team manages its own client library, rate limiting, cost tracking, safety filtering, and audit logging. This creates governance gaps, duplicated effort, and single-provider dependency risk.* |
| **Decision** | *ALL LLM API calls from GlobalBank systems MUST be routed through the Kong AI Gateway with LiteLLM abstraction layer. Direct LLM provider API calls are prohibited. Providers: Azure OpenAI (primary), Anthropic Claude (secondary via Bedrock), Llama 3 (self-hosted, sensitive data). Failover automated by LiteLLM.* |
| **Options Considered** | *(A) Multi-provider via LiteLLM gateway (SELECTED). (B) Azure OpenAI only (rejected: vendor lock-in risk). (C) Self-hosted LLMs only (rejected: capability gap). (D) Each team manages own clients (rejected: governance impossible).* |
| **Consequences (Positive)** | *Single governance point for LLM traffic. Unified audit log. Cost attribution. Safety filtering standardised. Provider switch without code changes. 30-40% cost reduction via semantic caching.* |
| **Consequences (Negative)** | *Gateway becomes single point of failure (mitigated: active-active HA). Migration effort for 3 existing systems (estimated: 2 sprints each). LiteLLM abstraction adds ~5ms latency (acceptable).* |
| **Compliance Link** | *EU AI Act Article 12 (logging); NIST AI RMF GOVERN-1.7 (documentation); GlobalBank AGP-6 (security); AGP-7 (accountability)* |
| **Review Date** | *Reviewed annually or when major provider change occurs* |

### Enterprise Agent Action Boundary Register

**AABR-EA-001** (EA Cross-Cutting)

Owner: AI Architect + Security Architect | ADM Phase: EA | TOGAF 10 + AI-First Extension

**Register Purpose:** Single source of truth for all AI agent action boundaries. Enforced at runtime by OPA sidecar. Updated when agents are deployed or their scope changes. Reviewed quarterly by ARB.

**Enforcement Mechanism:** OPA (Open Policy Agent) reads AABR as policy source. Agent presents signed manifest with claimed identity. OPA validates identity + requested action against AABR before execution.

*Note: this is the enterprise-wide, cross-system register maintained by EA; it supersets the single-system Agent Action Boundary Register shown under Enterprise Architecture Artifacts.*

| **Agent ID** | **System** | **Framework** | **Permitted Actions** | **Denied Actions** | **ATF Level / HITL** | **Hard Boundaries** | **Owner** |
|---|---|---|---|---|---|---|---|
| AGT-FIN-001 | CreditRisk-XGB-v1.0 | Scorer (non-agent) | bureau-api:READ, utility-api:READ, temenos-api:READ, decision-log:WRITE | ALL payment APIs, account-modify-api, customer-data-api:WRITE | ATF 1 — All decisions confirmed by core banking | None — non-agent | CRO |
| AGT-OPS-001 | CSCopilot-v2.1 | LangGraph stateful | crm-api:READ, kb-search:READ, ticket-api:CREATE-ONLY, order-api:READ | payment-api:ALL, account-modify-api:ALL, pii-export:ALL | ATF 3 — Notify human; refunds &gt;£100 need HITL | No payment; no account mod; no PII export | VP Operations |
| AGT-IT-001 | InfraAgent-v1.0 | AutoGen sub-agent | cloudwatch:READ, github-api:PR-CREATE-ONLY, slack-api:POST | production-deploy:ALL, iam:ALL, secrets:ALL, db:WRITE | ATF 2 — All code changes need human PR approval | No prod deploys; no IAM; no secret access | CISO |
| AGT-DATA-001 | DataQualityAgent-v1.0 | LangChain single-agent | data-catalog:READ, quality-metrics:READ, atlan-api:TAG-WRITE | training-data:WRITE, feature-store:WRITE, s3:DELETE | ATF 2 — Quality remediations &gt;Tier2 need approval | No training data modification; no feature deletion | Chief Data Officer |

### Responsible AI Maturity Programme

**RAIMP-001** (EA Cross-Cutting)

Owner: AI Governance Council | ADM Phase: EA | TOGAF 10 + AI-First Extension

| **Maturity Level** | **Characteristics** | **Remaining Gaps** | **GlobalBank Timeline** |
|---|---|---|---|
| L1 — Initial | Ad hoc AI deployments; no governance; reactive to incidents | Shadow AI; no bias testing; no HITL; no audit trail; regulatory non-compliant | No programme in place |
| L2 — Developing | AIDLC framework adopted; AI Governance Council established; AGPs published; first ARB gate process | Some systems lack full compliance; MLOps immature; data lineage partial; no zero trust | Q1 2026 — GlobalBank baseline |
| L3 — Scaling (TARGET 2026) | Full AIDLC for all T2 systems; LLM Gateway live; Data Mesh 6 domains; MLOps+LLMOps unified platform; ZTA for agents; ISO/IEC 42001 gap closed | Some T3/T4 systems still on AIDLC-Lite; autonomous retraining not yet live | Q4 2026 — Target state |
| L4 — Optimising | Continuous governance monitoring; autonomous retraining; AI portfolio optimisation; proactive regulatory engagement; industry-leading transparency reporting | Constant vigilance required; risk of complacency | 2027 target |
| L5 — Leading | Industry benchmark; external thought leadership; contributing to standards bodies (The Open Group, NIST, EU AI Act implementation); open-sourcing governance tooling | Resource-intensive to maintain | 2028+ aspiration |

**Current Maturity Level (May 2026)**

L2 transitioning to L3. AI Governance Council operational. AIDLC in use for 3 production systems. MLOps platform MVP live. Data Mesh 2 of 6 domains. Zero Trust scoped but not deployed.

**Target by Dec 2026**

L3 — Scaling. ISO/IEC 42001 certified. EU AI Act high-risk documentation complete. All 6 Data Mesh domains live. Full ZTA deployed. LLM Gateway enforced enterprise-wide.

**KPIs**

% AI systems with full AIDLC coverage (target 100% T2); Bias delta all T2 systems &lt;2pp; HITL trigger rate within designed range; Governance cost as % of AI programme (target &lt;15%)

---

## Related

- [../04-aidlc-artifacts-togaf-migration-to-ea.md](../04-aidlc-artifacts-togaf-migration-to-ea.md) — Part 1: Opportunities, Migration & Implementation Governance (Phase E-G)
- [./09-aidlc-artifacts-togaf-artifact-cross-reference.md](./09-aidlc-artifacts-togaf-artifact-cross-reference.md) — Part 3: Artifact Cross-Reference
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — AIDLC Phases 1–4 artifact templates
- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — AIDLC Phases 5–8 artifact templates
- [../03-aidlc-artifacts-togaf-foundation-to-technology.md](../03-aidlc-artifacts-togaf-foundation-to-technology.md) — TOGAF ADM Preliminary through Technology phases

## Sources

None currently documented.
