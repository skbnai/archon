---
title: "AI Solution Lifecycle Deliverables by Role (Part 3 of 3): Use Case Walk-throughs & Architect's Checklist"
doc_type: guide
domain: architecture
topic_id: ai-solution-lifecycle-deliverables-part3
date_created: 2026-07-07
last_reviewed: 2026-07-10
status: current
supersedes: []
source_type: native-md
tags: ["enterprise-architecture", "process", "use-cases"]
covers_version: "as of 2026-07-10"
---

:::info Part 3 of 3
This is the third and final part of a three-part guide. Start with [Part 1](pathname:///archon/architecture/74-ai-solution-lifecycle-deliverables) (Lifecycle, Roles, Matrix & Enterprise Architect) and [Part 2](pathname:///archon/architecture/parts/28-ai-solution-lifecycle-deliverables-part2) (Security, RAI/Governance, Solution, Distinguished, Data & Platform Architect Deep-Dives).
:::

---

## 5. Use Case Walk-throughs

### 5.1 Banking: AI Loan Underwriting Agent

**Context:** A Tier-1 bank in the EU deploys an autonomous loan underwriting agent. This system is High-Risk under EU AI Act (Annex III §5b). It is subject to Supervisory Review 11-7, Directive on Operational Resilience for the Financial Sector (DORA), and MiFID II suitability rules. Reference: Sterling case study.

**Key regulatory constraints:**
- EU AI Act Art. 13: Transparency — must disclose AI involvement
- EU AI Act Art. 14: Human oversight — adverse decisions require human review
- GDPR Art. 22: No fully automated adverse credit decisions without opt-out
- Supervisory Review 11-7: Model documentation, independent validation, ongoing monitoring
- DORA: Operational resilience, incident reporting within 4 hours

**Stage swimlane (selected roles):**

| Stage | Enterprise Architect | Security Architect | RAI Lead | Data Architect | MLOps |
| --- | --- | --- | --- | --- | --- |
| **Incubation** | AI Strategy Brief; AI Safety Level: SL3 | Preliminary threat model | AI Impact Assessment v0: HIGH-RISK | Data landscape assessment | Platform readiness |
| **RFP** | Vendor arch criteria (sovereign infra mandatory) | Security RFP (DORA resilience; customer-managed encryption keys) | RAI RFP criteria (SHAP mandatory; AIF360) | Data residency: EU-only | MLOps RFP (drift detection; model registry) |
| **Design & Build** | Reference arch (sovereign EU cloud); ARB | Threat model; Cedar agent capabilities | Banking AI Constitution; model card; fairness spec | Data contract (7yr retention; SHAP fields) | Eval gates (demographic parity gate; Supervisory Review 11-7 docs) |
| **Operate** | Post-impl review (90d) | Security monitoring; quarterly pentest | Monthly fairness report; annual ethics audit | Data quality SLA; annual residency audit | Drift pipeline; FinOps dashboard |
| **Retire** | Decommission arch review | Secure wipe plan | Responsible retirement checklist | Data deletion + Supervisory Review 11-7 proof of retention | Model archival (7yr regulatory) |

**Sample RAI Impact Assessment stub (banking):**

The loan underwriting agent serves retail loan applicants in the EU, processing approximately 50,000 applications per year. Vulnerable groups at risk include low-income applicants and first-time borrowers.

Key harms identified: (H1) Discriminatory credit denial (Medium probability, High impact) — mitigated by demographic parity gate and monthly fairness audit. (H2) Unexplainable adverse decision (Low probability, High impact) — mitigated by mandatory SHAP explanations and plain-language decision within 30 days. (H3) Data residency breach (Low probability, Critical impact) — mitigated by EU-sovereign deployment and annual residency audit.

Autonomy level is Assisted (AI recommends; human signs off). Mandatory human oversight applies to all adverse decisions per GDPR Art. 22. Constitutional basis: BANK-CONST-001 v1.0. Key constitutional rules applied: (BP1) Fair lending checks before any credit decision, (BP3) Dual authorization for transactions above threshold, (BP5) Human review required for all adverse decisions.

---

### 5.2 Healthcare: Prior Authorization Agent

**Context:** A large hospital network deploys an AI prior authorization agent. FDA Software as a Medical Device (SaMD) considerations apply; HIPAA is mandatory; Human-in-the-Loop review is required for all clinical decisions. Reference: Cascadia case study.

**Key regulatory constraints:**
- HIPAA: Patient data protection, minimum necessary standard
- FDA SaMD: If the system makes or assists clinical decisions, may require clearance
- EU Medical Device Regulation: If used in EU hospitals
- Joint Commission: Clinical AI oversight standards

**Stage swimlane:**

| Stage | Enterprise Architect | RAI Lead | Data Architect | Solution Architect |
| --- | --- | --- | --- | --- |
| **Incubation** | AI Strategy Brief; SL3 (clinical) | AI Impact Assessment: HIGH + FDA SaMD check | Protected Health Information landscape assessment | Clinical workflow feasibility |
| **RFP** | Architecture criteria (HIPAA BAA mandatory) | RAI criteria (clinical evidence base; bias by demographic) | Protected Health Information data contract requirements | Clinical integration requirements (EHR APIs) |
| **Design & Build** | Healthcare AI reference arch | Healthcare AI Constitution; clinician override design; bias spec by demographic | Protected Health Information data contract (de-identification; Institutional Review Board) | Clinical workflow SDD; Human-in-the-Loop design |
| **Operate** | Post-impl (90d clinical audit) | Monthly equity report (demographic disparity); annual ethics audit | Protected Health Information residency monitoring; consent audit | Clinical runbook; escalation to clinician |
| **Retire** | Decommission (patient care continuity) | Retirement assessment (patient data dignity) | Protected Health Information deletion (HIPAA right of access preserved) | Clinical handover protocol |

**Sample AI Constitution excerpt (Healthcare):**

Prohibited actions: (HP1) Never approve/deny prior authorization without validated evidence base — BLOCK enforcement, requiring level 2 or above Oxford Centre for Evidence-Based Medicine levels. (HP3) Never override a clinician's documented decision — BLOCK enforcement.

Required behaviors: (HR4) Always provide clinician override capability with mandatory rationale field.

Escalation rules: If payer policy falls outside standard clinical guidelines, ESCALATE_TO_SENIOR_CLINICIAN. If patient demographic is outside training data distribution, ALERT_CLINICIAN_AND_LOG.

---

### 5.3 Government: Citizen Benefits Navigation Agent

**Context:** A national government deploys an AI agent guiding citizens through benefits eligibility. Sovereign infrastructure is mandatory. Reference: StateDHS case study.

**Key regulatory constraints:**
- EU AI Act Art. 14: Human oversight mandatory (benefits determination is High-Risk Annex III §1)
- GDPR: Citizen data protected, right to human review of automated decisions
- Data sovereignty: Citizen data must remain on sovereign national infrastructure
- Administrative law: AI decisions must be contestable through formal legal process

**Stage swimlane:**

| Stage | Enterprise Architect | Security Architect | RAI Lead | Data Architect |
| --- | --- | --- | --- | --- |
| **Incubation** | AI Strategy Brief; sovereign infra mandatory; SL3 | Threat model (citizen targeting attack surface) | AI Impact Assessment: HIGH-RISK (Annex III §1); democratic governance assessment | Data sovereignty assessment (citizen data classification) |
| **RFP** | Sovereign infra requirements (air-gappable); on-prem preferred | Security requirements (sovereign data center; government security standards) | Democratic governance criteria; AI Bill of Rights compliance | Sovereign residency mandatory; citizen data never leaves national infra |
| **Design & Build** | Government sovereign AI reference arch; ARB submission to government architecture board | Government security architecture (national security standards) | Government AI Constitution; Algorithmic Impact Assessment (public) | Citizen data contract (sovereign; GDPR; right to deletion) |
| **Operate** | Quarterly parliamentary report (AI in government register) | Annual security audit (government standards) | Monthly equity report; annual democratic AI audit; public AI register update | Annual citizen data residency certification |
| **Retire** | Decommission with parliamentary notification | Secure deletion (government classification) | Responsible retirement (citizen communication; right to human-only service preserved) | Citizen data deletion (GDPR Art. 17; certificate of deletion) |

---

## 6. Architect's Checklist

Use the following checklist to verify comprehensive lifecycle governance:

- [ ] **DL1** — Every AI initiative has named architect owners for all 7 roles
- [ ] **DL2** — AI Safety Level classified and documented in model registry before Stage 2
- [ ] **DL3** — AI Impact Assessment completed at Incubation (preliminary) and Design (full)
- [ ] **DL4** — ARB submission includes: RAI sign-off, security sign-off, data residency confirmation
- [ ] **DL5** — AI Constitution ratified and deployed to policy engine before production
- [ ] **DL6** — Model card published before any user-facing deployment
- [ ] **DL7** — Data contract and lineage documented and signed off by Data Architect
- [ ] **DL8** — Evaluation gate framework in CI/CD; deployment blocked if gates fail
- [ ] **DL9** — Decommission plan exists from Day 1 of Design stage (not an afterthought)
- [ ] **DL10** — Use-case-specific regulatory checklist completed per sector
