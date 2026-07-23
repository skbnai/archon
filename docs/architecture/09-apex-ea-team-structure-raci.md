---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-team-structure-raci
title: "APEX EA Part 1: Team Structure, RACI & Operating Model"
date_created: 2026-04-01
last_reviewed: 2026-07-17
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 1 team structure raci operating model
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part1_Team_Structure_RACI.md
tags:
  - enterprise-architecture
  - specialization
  - togaf
  - organizational-design
  - raci-matrix
---

# APEX EA Part 1: Team Structure, RACI & Operating Model

Part 1 of the APEX EA 4-part blueprint. Continues in [Part 2: AI-DLC Methodology & Foundation Architecture](./10-apex-ea-aidlc-methodology.md).

## Organizational Design Principles

APEX organizes around the AI-DLC lifecycle, not traditional IT silos. Each phase (A–D) owns distinct outcomes and decision rights.

### Role Taxonomy

| Role | Accountability | Scope | Staffing model |
|------|---|---|---|
| **Platform AI Architect** | Enterprise AI strategy, reference architecture, standards, ARB chair | Enterprise-wide AI governance and platform direction | 1–2 per enterprise (principal level) |
| **AI Product Lead** | Domain AI use-case portfolio, business case, adoption | Per business unit or customer segment | 1–2 per business unit |
| **AI-DLC Program Manager** | Phase gates, workstream coordination, risk/timeline | Across all AI initiatives; reports to CTO/CRO | 1–2 (PMO function) |
| **Data Architect** | Data readiness, lineage, classification, governance | Enterprise data mesh; inherits from modern data stack | 2–4 |
| **AI/ML Engineer (Foundation Model)** | Model selection, fine-tuning, tokenomics, eval strategy | Per AI initiative or shared services | 2–6 depending on specialization |
| **Prompt Engineer & Context Lead** | RAG design, retrieval quality, context assembly, in-context learning | Per agent; may be same person as AI/ML Engineer | 1–2 per agent team |
| **Agent Infrastructure Engineer** | Harness architecture, orchestration, runtime, safety/policy gates, integration | Shared platform service | 2–4 |
| **Tool API Owner** | Tool catalog, SLA enforcement, schema governance, observability | Per business domain | 1–2 per domain |
| **Observability & Reliability Lead** | Telemetry, tracing, cost metering, SLO definition, incident response | Shared platform service | 1–3 |
| **Risk & Compliance Lead** | Model risk governance, audit trail, regulatory mapping, decision explanation | Enterprise function; coords with Legal/Risk | 1–2 |
| **DevSecOps Engineer** | Supply chain security, IaC, secret rotation, image scanning, runtime enforcement | Platform service; may share with traditional DevSecOps | 1–2 |

### Team Structure

```
CTO / Chief Architect
├─ Platform AI Architect (enterprise AI strategy, standards, ARB chair)
├─ AI-DLC Program Manager (phase gates, risk, timeline)
├─ AI Product Leads [per business unit]
└─ Shared Platform Team
   ├─ Data Mesh & Governance (Data Architects)
   ├─ AI Foundation Services (Model selection, fine-tuning, evaluation)
   ├─ Agent Infrastructure (harness, orchestration, runtime)
   ├─ Observability & Cost (telemetry, SLO, metering)
   ├─ DevSecOps & Compliance
   └─ Tool API Governance
```

### RACI Matrix

**Legend:** R = Responsible (does the work) | A = Accountable (final say) | C = Consulted (input) | I = Informed (updates)

#### Phase A — Discovery & Opportunity Scoping

| Decision | Platform AI Arch | AI Product Lead | Data Architect | AI-DLC PM | Risk/Compliance |
|---|---|---|---|---|---|
| **Business case approval** | C | A | | R | C |
| **Data readiness assessment** | C | C | R | | C |
| **Use-case priority ranking** | A | C | | R | C |
| **Readiness gate (proceed to Phase B?)** | A | | | R | C |

#### Phase B — Architecture Design & Technology Selection

| Decision | Platform AI Arch | AI/ML Eng | Agent Infra Eng | Prompt Eng | Data Architect |
|---|---|---|---|---|---|
| **Model selection & eval framework** | C | R | C | C | |
| **Harness architecture & orchestration pattern** | A | | R | C | |
| **RAG design & retrieval strategy** | C | | C | R | R |
| **Data lineage & governance** | | | | | R & A |
| **Cost estimation & token budget** | | R | | R | |
| **Approval: proceed to Phase C?** | A | | | | |

#### Phase C — Implementation & Data Pipeline

| Decision | Data Architect | AI/ML Eng | Agent Infra Eng | DevSecOps | Observability Lead |
|---|---|---|---|---|---|
| **Data ingestion & quality gates** | A & R | C | C | R | |
| **Model fine-tuning & optimization** | | R & A | | C | C |
| **Agent configuration & deployment prep** | | C | R & A | R | R |
| **Observability & telemetry design** | | | C | | R & A |
| **Security review & policy coding** | | C | | A & R | C |
| **Staging → Production gates (L1–L5)** | | | C | R | A |

#### Phase D — Operations & Continuous Improvement

| Decision | Observability Lead | Risk/Compliance | Prompt Eng | Product Lead | Platform AI Arch |
|---|---|---|---|---|---|
| **Model performance & drift monitoring** | R | | R | C | C |
| **Cost optimization & chargeback** | R & A | | | | |
| **Regulatory/audit reporting (DORA, EU AI Act)** | C | R & A | | | |
| **Go/no-go: continue investment?** | I | C | | A | C |

---

## Operating Model — Decision Rights & Escalation

### Governance Tiers

| Tier | Criteria | Authority | Cadence |
|---|---|---|---|
| **T1 — Standard** | <$100k annual; publicly known model; no regulated data; single business unit | AI Product Lead + Data Architect | Monthly portfolio review |
| **T2 — Strategic** | $100k–$500k; fine-tuning or custom harness; cross-BU data; advisory approval | Platform AI Arch + CTO | Quarterly |
| **T3 — Regulated** | Touches regulated data (PII, financial, healthcare); regulated industry user; external audit log required | ARB + Risk/Compliance + Legal | Pre-launch + annual |
| **T4 — Systemic Risk** | Model failure cascade risk; shared infrastructure dependency; >$500k; multi-region; M&A/divestment risk | Board-level AI committee | Per-initiative + annual |

### Escalation Path

1. **Standard issue → Product Lead resolves**
2. **Cross-team conflict → AI-DLC PM facilitates; Platform AI Arch arbitrates**
3. **Risk flagged → Risk/Compliance gates the tier; escalation to CRO if compliance risk**
4. **Cost overrun >20% → CTO + CFO approval required**
5. **Security or regulatory finding → ARB emergency session**

---

## Staffing Roadmap (12-Month Ramp)

| Month | Hires | Focus | Headcount |
|---|---|---|---|
| **M0–1** | 1 Platform AI Architect; 1 AI-DLC PM | Enterprise strategy; first use-case workstreams | 2 |
| **M2–3** | 2 Data Architects; 1 AI/ML Engineer (evals) | Data mesh design; model selection for first 3 use cases | 5 |
| **M4–5** | 2 Agent Infrastructure Engineers; 1 Prompt Engineer | Harness/orchestration; RAG pipeline tuning | 8 |
| **M6–8** | 1 Observability Lead; 1 DevSecOps; 1 Risk/Compliance Lead | Telemetry; supply chain security; audit trail | 11 |
| **M9–12** | 2 additional AI/ML Engineers; 1 Tool API Owner | Model specialization; tool governance; chargeback | 14 |

By month 12: **14 FTE across platform + 3–5 embedded AI Product Leads in business units = 17–19 FTE total.**

---

Next: [Part 2 — AI-DLC Methodology & Foundation Architecture](./10-apex-ea-aidlc-methodology.md) covers the lifecycle phases (A–D), phase gates, and reference technology architecture.
