---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-aidlc-methodology
title: "APEX EA Part 2: AI-DLC Methodology & Foundation Architecture"
date_created: 2026-04-01
last_reviewed: 2026-07-17
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 2 ai-dlc methodology foundation architecture
  - ai-dlc enterprise framework
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part2_AI_DLC_Methodology_Foundation_Architecture.md
tags:
  - enterprise-architecture
  - specialization
  - togaf
  - ai-dlc
  - methodology
  - architecture-vision
---

# APEX EA Part 2: AI-DLC Methodology & Foundation Architecture

Part 2 of the APEX EA 4-part blueprint. Continues from [Part 1: Team Structure, RACI & Operating Model](./09-apex-ea-team-structure-raci.md); next is [Part 3: Information Systems & Technology Architecture](./11-apex-ea-information-systems-architecture.md).

## AI-DLC: Methodology, Phases & Enterprise Architecture Impacts

### What is AI-DLC?

The AI-Driven Development Lifecycle (AI-DLC) emerged from 100+ enterprise experiments and positions AI as a central collaborator throughout every development activity—design, build, test, deploy, and operate. Enterprise adopters report 2–5x sustainable productivity gains across the full lifecycle. In well-scoped greenfield tasks with high-quality semantic context, gains reach 7–10x.

### Phases and Roles

| Phase | Name | AI Role | Human Role | Architecture Impact |
|---|---|---|---|---|
| **1** | Inception (Mob Elaboration) | Transforms business intent into structured requirements, user stories, capability maps | Validates outputs; provides business context and domain knowledge | Vision, requirements, maps produced in days not weeks |
| **2** | Construction (Mob Construction) | Proposes architecture components, generates IaC, writes functions, builds tests | Clarifies decisions; reviews every AI-generated artifact before merge | Phases B/C/D concurrent in bolts; requires Phase Boundary Receipts |
| **3** | Operations | Applies accumulated context to IaC deployment, canary monitoring, drift detection | Reviews/approves changes; monitors SLOs; makes judgment calls | Phases F/G/H compressed to continuous delivery; every AI change is formal DORA event |

### Terminology Reference—AI-DLC vs. Traditional

| Traditional | AI-DLC | Duration Change | Enterprise Architecture Implication |
|---|---|---|---|
| Sprint | Bolt | 2–4 weeks → hours to days | ADM governance must operate within bolt cadence; tiered model required |
| Epic | Unit of Work | Months → days to weeks | Architecture workpackages shrink; ARB meets weekly |
| User Story | AI-Elaborated Requirement | Days → minutes | Requirements traceability automated; ARS auto-updated |
| Architecture Review | Real-time Mob Construction | Weeks → concurrent | ARB provides real-time guidance; retains final sign-off |
| Documentation | Persistent Semantic Context | Post-sprint → continuous | EA team shifts from authors to reviewers |
| Code Review | AI-Augmented Quality Scan | Hours → minutes | L1–L5 Layered Verification enforced; no hero review |

### AI-DLC Operating Model Transformations

**1. Governance Tempo: Quarterly → Near Real-Time** — AI-DLC's bolt cadence requires architecture decisions in hours. Tiered governance: automated checks continuous, architect-in-the-loop daily, ARB weekly.

**2. EA Artifacts: Static Documents → Living Digital Twins** — Architecture repository transitions to continuously auto-updated environment. EA team shifts from authors to reviewers.

**3. New Roles: Enterprise AI Architect & Chief AI Ethics Officer** — Organizations introducing dedicated roles to support AI-native delivery.

**4. Data Architecture Extension: AI-Native Entities** — Embeddings, prompt catalogs, feedback logs, and model lineage records become first-class governed data assets.

**5. Business Architecture: Dynamic Capabilities Replace Static Models** — Capabilities that learn and adapt in motion require separate governance from static capabilities.

---

## Architecture Principles (Preliminary Phase)

### Business Principles

| ID | Principle | Implication |
|---|---|---|
| **BP-01** | AI as Business Capability | Every agent traces to measurable business outcome; productivity tracked quarterly |
| **BP-02** | Human-in-the-Loop—Inviolable | All agents on sensitive data have pipeline-enforced human escalation path |
| **BP-03** | Platform Thinking with Sprawl Controls | No division procures standalone AI tools if APEX meets need within 90 days; agent registry is source of truth |
| **BP-04** | Data Maturity Before AI Velocity | AI-DLC Construction cannot begin until Data Maturity Gate (5 checks) is passed |

### Data Principles

| ID | Principle | Implication |
|---|---|---|
| **DP-01** | Data Sovereignty | Personal/sensitive data must remain within contractually agreed jurisdiction |
| **DP-02** | Data as Shared Asset | All data consumed by agents catalogued in Data Mesh with documented lineage |
| **DP-03** | Explainability Before Deployment | Every model has documented explainability method (including RAG retrieval stage) |
| **DP-04** | AI Assets as Governed Data | Prompt templates, embeddings, feedback logs, model lineage are first-class governed data |
| **DP-05** | Embedding Compatibility Enforced | Embedding model upgrade triggers automatic re-indexing; RAGAS regression gate blocks activation |

### Technology Principles

| ID | Principle | Implication |
|---|---|---|
| **TP-01** | Cloud-Native Open Standards | CNCF-hosted and open-standard components; proprietary SDKs only where no OSS equivalent |
| **TP-02** | Security by Design | Security architecture approved by CISO before any IaC written; zero-trust NetworkPolicy defined upfront |
| **TP-03** | Observability as First-Class | Every agent emits OpenTelemetry traces, Prometheus metrics, structured logs from first commit |
| **TP-04** | Cost Transparency with Hard Throttle | Each agent tagged to cost centre; budget enforced with hard throttle at 110% |
| **TP-05** | Layered Verification | AI-generated IaC passes L1–L5 verification (static analysis, AI explanation, property tests, canary, drift detection) |
| **TP-06** | Decision Explanation Artifact by Default | High-Risk agents produce DEA for every regulated decision; immutably stored 7 years |

---

## Architecture Vision & Constraints

**Vision Statement**: "By Q4 2026, operate a unified AI Agent Platform (APEX) on cloud-native open standards, reducing time-to-market for AI use cases to 5–6 weeks baseline, achieving full EU AI Act and DORA compliance, and generating positive NPV within 24 months."

**Key Constraints**:
- Personal/sensitive data must remain within contractual jurisdiction (GDPR/PDPA/LGPD)
- All AI models require Model Risk validation before production
- Cloud-native open standards only; no proprietary SDK in core business logic
- Zero-downtime deployment for critical services
- EU AI Act enforcement from August 2026
- All AI evolution framed as controlled DORA change

---

## Five Pioneer Domains

| # | Division | Agent | Use Case | Regulation | Timeline | Owner |
|---|---|---|---|---|---|---|
| **1** | Customer | RiskScoringAgent | Automated risk-based decisioning with human escalation | Model Risk Policy, GDPR | 8 weeks | Domain Architect 1 |
| **2** | Enterprise | VerificationAgent | Continuous verification, sanctions screening, report drafting | AML Directive, FATF 40 | 7 weeks | Domain Architect 2 |
| **3** | Advisory | RebalancingAgent | Portfolio rebalancing recommendations with suitability assessment | MiFID II Art.27, GDPR | 6 weeks | Domain Architect 3 |
| **4** | IT Operations | IncidentAgent | L1/L2 triage, root-cause pattern recognition, auto-remediation | DORA Art.11 | 5 weeks | Domain Architect 4 |
| **5** | Risk & Compliance | ModelMonitorAgent | Model drift detection, backtesting, regulatory evidence generation | EU AI Act Art.9 | 6 weeks | Domain Architect 5 |

---

Next: [Part 3 — Information Systems & Technology Architecture](./11-apex-ea-information-systems-architecture.md) details data architecture, application components, APIs, cloud topology, security, and CI/CD.
