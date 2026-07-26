---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-aidlc-methodology
title: "APEX EA Part 2: AI-DLC Methodology & Foundation Architecture"
date_created: 2026-04-01
last_reviewed: 2026-07-23
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 2 ai-dlc methodology foundation architecture
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part2_AI_DLC_Methodology_Foundation_Architecture.md
tags:
  - enterprise-architecture
  - specialization
  - togaf
  - ai-dlc
  - architecture-vision
  - business-architecture
  - governance
---

# APEX EA Part 2: AI-DLC Methodology & Foundation Architecture

Continues from [Part 1: Team Structure, RACI & Operating Model](./09-apex-ea-team-structure-raci.md). This part covers the AI-DLC delivery methodology and TOGAF Preliminary/Vision/Business phases (A–B) that the team structure operates within.

### AI-DLC Lifecycle Overview

```mermaid
graph LR
    A["Inception<br/>(Mob Elaboration)<br/>Days to Weeks"] -->|Structured Requirements| B["Construction<br/>(Mob Construction)<br/>Hours to Days per Bolt"]
    B -->|AI-Generated IaC & Components| C["Operations<br/>(AI-DLC Ops)<br/>Continuous Delivery"]
    C -->|Approved Changes| D["Production<br/>Governed & Monitored"]
    D -->|Monitoring & Feedback| E["Continuous Learning"]
    E -->|Architecture Debt| B
    
    B -.->|L1-L5 Verification| C
    C -.->|DORA Change Events| F["Governance Gates<br/>ARB, T4 Reg-Gate"]
    
    style A fill:#e1f5ff
    style B fill:#c8e6c9
    style C fill:#fff9c4
    style D fill:#f8bbd0
    style F fill:#f3e5f5
```

**AI-DLC phases compress traditional development cycles:** Inception (Mob Elaboration) transforms business intent into structured requirements in days. Construction (Mob Construction) generates architecture components and IaC in bolts (hours to days). Operations applies accumulated context to deployment and monitoring in continuous delivery. Every transition includes governance gates and verification layers.

## AI-DLC: Methodology, Phases & EA Impacts

### What is AI-DLC?

The AI-Driven Development Lifecycle (AI-DLC) was introduced by AWS in July 2025 and featured at AWS re:Invent 2025. It emerged from 100+ enterprise experiments and observed that AI-assisted (too narrow) and AI-autonomous (too unreliable) both produced suboptimal results. AI-DLC positions AI as a central collaborator throughout every development activity — design, build, test, deploy, and operate.

#### Proven Results

Enterprise adopters report 2–5× sustainable productivity gains across the full lifecycle. In well-scoped greenfield tasks with high-quality semantic context, gains reach 7–10×. Teams using AI-DLC consistently report improved code quality alongside velocity: the Qodo 2025 report showed quality improvements rising from 55% to 81% with AI-assisted review; the Atlassian RovoDev 2026 study found AI code review comments led to additional fixes in 38.7% of cases.

### AI-DLC Core Phases

| Phase | Name | AI Role | Human Role | Architecture Impact |
| --- | --- | --- | --- | --- |
| 1 | INCEPTION (Mob Elaboration) | Transforms business intent into structured requirements, user stories, capability maps, and architecture units at speed | Validates AI outputs; provides business context, domain knowledge, and political nuance that AI cannot infer | Vision, requirements, and capability maps produced in days not weeks; must be preceded by a political context capture session |
| 2 | CONSTRUCTION (Mob Construction) | Proposes architecture components, generates IaC, writes serverless functions, builds tests from semantic context | Clarifies technical decisions and architectural choices in real time; reviews every AI-generated artefact before merge | Phases B/C/D produced concurrently in bolts; concurrent execution requires Phase Boundary Receipts for regulated data flows |
| 3 | OPERATIONS | Applies accumulated context to IaC deployment, canary monitoring, incident pattern recognition, and drift detection | Reviews and approves all changes; monitors SLOs; makes judgment calls in novel failure scenarios | Phases F/G/H compressed into continuous delivery; every AI-driven change is a formal DORA change event with ARB record |

### Terminology Reference — AI-DLC vs. Traditional

| Traditional Term | AI-DLC Term | Duration Change | Enterprise Architecture Implication |
| --- | --- | --- | --- |
| Sprint | Bolt | 2–4 weeks → hours to days | ADM governance must operate within bolt cadence; tiered model required |
| Epic | Unit of Work | Months → days to weeks | Architecture work packages shrink; ARB meets weekly not bi-weekly |
| User Story | AI-Elaborated Requirement | Days → minutes | Requirements traceability automated; ARS auto-updated with human review gate |
| Architecture Review | Real-time Mob Construction | Weeks → concurrent | ARB provides real-time guidance; final sign-off authority retained |
| Documentation | Persistent Semantic Context | Post-sprint → continuous | Architecture repository auto-updated; EA team shifts from authors to reviewers |
| Code Review (PR) | AI-Augmented Quality Scan | Hours → minutes | L1–L5 Layered Verification Model enforced in pipeline; no hero review |
| Retrospective | Continuous Learning Loop | End of sprint → continuous | Architecture debt auto-detected; agent health scoring continuous |

### AI-DLC Impact Across All 10 TOGAF ADM Phases

| TOGAF Phase | AI-DLC Capability | Human Guard Required | Architecture Adaptation |
| --- | --- | --- | --- |
| Preliminary | AI generates architecture principle drafts; governance rules codified as steering files | Architects validate all AI-generated principles; formal ratification gate mandatory | Steering files maintained in version control; breaking changes require architect approval |
| Phase A — Vision | AI transforms business intent into draft Architecture Vision Statement in hours | Political nuance, power dynamics, and unwritten constraints require human capture before Mob Elaboration | Political Blindspot Protocol precedes every Mob Elaboration session |
| Phase B — Business | AI auto-generates business capability maps from existing documentation; value streams modelled in minutes | Existing documents may be stale; Data Maturity Gate required before AI elaboration begins | Data Maturity Gate: 5-check assessment mandatory before Phase B AI execution |
| Phase C — Data | AI creates data models, entity diagrams, and API schemas; prompt catalogs and embeddings become first-class governed entities | Embedding model upgrades require Embedding Compatibility Contract and RAGAS regression gate | Embeddings versioned; RAGAS gate on model upgrade; 90-day rollback window maintained |
| Phase C — Application | AI proposes application component models and cloud-native integration patterns | AI may propose patterns inconsistent with org standards without tight steering files | Org standards loaded as steering files; all AI-proposed patterns reviewed by ARB |
| Phase D — Technology | AI generates IaC, security policies, and deployment configs from architecture context | AI-generated IaC requires L1–L5 Layered Verification; IaC hallucinations are a real risk | L1–L5 Layered Verification Model enforced in CI/CD; no merge without engineer confirmation |
| Phase E — Opportunities | AI analyses gap reports and proposes build/buy/reuse options at machine speed | AI may miss regulatory obligations, vendor relationship context, and political constraints | Legal, procurement, and compliance participate in Mob Elaboration for all build/buy decisions |
| Phase F — Migration | Bolts replace work packages; migration plans near-real-time | Over-acceleration may skip governance gates | Compliance gates pipeline-enforced; AI-DLC speed contained within governance boundaries |
| Phase G — Governance | AI automates conformance checking; real-time drift detection replaces periodic reviews | Automated checks inform; humans decide; ARB retains final sign-off authority | 5-tier governance model; T1 automated always-on; T4 Reg-Gate inviolable |
| Phase H — Change | AI monitors model releases and regulatory changes; flags architecture impacts automatically | Continuous change proposals require human filtering to avoid architecture instability | Change type classification; AI flags; humans prioritise; DORA change framing applied to all AI changes |
| Req. Management | AI generates and maintains requirements traceability from business intent to deployed code | Context drift across sessions; requirements must be forward-traced before each deployment | Context Integrity Protocol; session summary archive; forward-trace validation per deployment |

### Operating Model Transformations Required

AI-DLC is not just a development methodology — it requires structural changes to the enterprise architecture operating model. Research from Intelance, Staun & Stender, and CIO.com (2025) identifies five critical transformation areas GlobalCorp must address:

**1. Governance Tempo: From Quarterly to Near Real-Time** — Traditional EA governance operates on quarterly review cycles. AI-DLC's "bolt" cadence means architecture decisions are needed in hours. GlobalCorp must establish a tiered governance model: automated checks run continuously (Cat A/B compliance), architect-in-the-loop reviews occur daily, full ARB convenes weekly rather than bi-weekly. Research from Staun & Stender (2025) confirms that "these are not quarterly review topics; they are near real-time decisions."

**2. EA Artefacts: From Static Documents to Living Digital Twins** — Gartner (2025) notes that Forrester identified AI agents in EA suites are now automating data validation, capability mapping, and artefact creation. GlobalCorp's architecture repository (LeanIX) must transition from a periodic-update model to a continuously auto-updated environment where AI-DLC tools write back architecture artefacts as they are generated. The EA team shifts from artefact authors to artefact reviewers.

**3. New Roles: Enterprise AI Architect & Chief AI Ethics Officer** — BCG research found that 89% of C-level executives ranked AI/GenAI in their top three strategic priorities for 2024. In response, organisations are introducing dedicated roles such as the Enterprise AI Architect. GlobalCorp must create this role (filled internally from the APEX Architecture team) and formalise the Chief AI Ethics Officer position proposed in the APEX Business Architecture.

**4. Data Architecture Extension: AI-Native Entities** — TOGAF's traditional data architecture covers conceptual, logical, and physical models. AI-DLC introduces new first-class data entities that must be governed: **embeddings** (versioned vector representations), **prompt catalogs** (regulated as code + data), **feedback logs** (agent decision outcomes), and **model lineage records** (EU AI Act traceability). MLflow's Prompt Registry exemplifies this shift in tooling, as identified in the TOGAF BDAT stress-test research (Medium, Sept 2025).

**5. Business Architecture: Dynamic Capabilities Replace Static Models** — Traditional Business Architecture documents stable capabilities. AI-DLC and agentic AI create capabilities that "learn and adapt in motion." Examples: Walmart and Carrefour already use AI to shift pricing and promotions dynamically — what was a quarterly campaign is now an hourly decision. GlobalCorp's Business Capability Map (BCM-APEX-001) must be updated to flag "adaptive capabilities" and their governance implications separately from static capabilities.

### AI-DLC Adoption Roadmap

GlobalCorp will adopt AI-DLC in a phased approach aligned to APEX delivery horizons, to avoid disrupting in-flight architecture governance while capturing productivity gains:

| Horizon / Period | AI-DLC Adoption Scope | EA Impact | Governance Gate |
| --- | --- | --- | --- |
| H0: Observe (Q1 2025) | AI-DLC training for architecture team; pilot on 2 work packages | Minimal; existing ADM retained | CTO sign-off on pilot |
| H1: Adopt for Build (Q2–Q3 2025) | AI-DLC Construction phase for Pioneer Domain 1 & 2 delivery | Phase C/D artefacts AI-assisted; peer review mandatory | ARB approves AI-assisted artefacts |
| H2: Extend to Inception (Q4 2025) | Mob Elaboration for Pioneer 3–5 requirements and architecture vision | Phase A/B artefacts AI-generated; ARB review process updated | Steering Committee endorses |
| H3: Full AI-DLC (Q1–Q2 2026) | End-to-end AI-DLC across all APEX workstreams; real-time governance | Full operating model transformation; LeanIX AI integration | Architecture Board annual review |

## Preliminary Phase — Foundation

**PRELIMINARY** — Architecture capability, principles, tailored ADM, repository

The Preliminary Phase establishes GlobalCorp's architecture capability for APEX. Governance structures are put in place, the ADM is tailored for regulatory context, and architecture principles that govern every subsequent decision are ratified.

### Architecture Principles — APD-001

#### Business Principles

| ID | Principle | Statement | Implication |
| --- | --- | --- | --- |
| BP-01 | AI as Business Capability | Every APEX agent traces to a measurable business outcome in the Corporate Strategy Map; productivity gains are tracked quarterly against actuals | Business Value Case required before APEX onboarding; quarterly actuals vs. targets reported to steering committee |
| BP-02 | Human-in-the-Loop — Inviolable | All agents acting on sensitive data or high-stakes decisions have a human escalation path that is pipeline-enforced and cannot be bypassed for velocity | HITL gates configured in the agent gateway; any removal requires Group CTO written exception logged in compliance register |
| BP-03 | Platform Thinking with Sprawl Controls | No division procures standalone AI tools if APEX can meet the need within 90 days; equally, no agent is created without registry entry and monthly health score | ARB approval for procurement; agent registry is the source of truth; unregistered agents blocked at gateway |
| BP-04 | Data Maturity Before AI Velocity | AI-DLC Construction cannot begin for any domain until the Data Maturity Gate (5 checks) is passed | Data maturity assessment is the first deliverable of every Pioneer Domain onboarding; it is a programme gate not a guideline |

#### Data Principles

| ID | Principle | Statement | Implication |
| --- | --- | --- | --- |
| DP-01 | Data Sovereignty | Personal and sensitive data processed by APEX agents must remain within the contractually agreed jurisdiction | AI inference endpoints provisioned per jurisdiction; network policy blocks cross-border calls for C4-class data at the kernel level |
| DP-02 | Data as Shared Asset | All data consumed by agents is catalogued in the Data Mesh with documented lineage before an agent goes to production | No agent deployed without data catalog entry covering every data source it touches; Data Architect sign-off required |
| DP-03 | Explainability Before Deployment | Every model has a documented explainability method — including the retrieval stage of RAG, not just the generation stage | RAG retrieval explanation is part of the DEA; explainability report is a mandatory CI/CD gate artefact |
| DP-04 | AI Assets as Governed Data | Prompt templates, embeddings, feedback logs, and model lineage records are first-class governed data assets with the same rigor as operational data | Embedding Compatibility Contract applies; ML model registry tracks all lineage; DPO sign-off for sensitive-adjacent prompts |
| DP-05 | Embedding Compatibility Enforced | Any embedding model upgrade triggers automatic full re-indexing of all dependent knowledge bases; RAGAS regression gate blocks production activation | CI/CD pipeline blocks embedding upgrade without RAGAS pass; 90-day rollback window maintained |

#### Technology Principles

| ID | Principle | Statement | Implication |
| --- | --- | --- | --- |
| TP-01 | Cloud-Native Open Standards | Platform uses CNCF-hosted and open-standard components; proprietary cloud SDKs used only where equivalent OSS is not production-ready | All components containerised; OpenAPI for agent interfaces; OpenTelemetry for observability; no cloud SDK in core business logic |
| TP-02 | Security by Design | Security architecture is approved by the CISO delegate before any IaC is written for a given Pioneer Domain | Security is a Phase D entry gate; it is not a Phase G concern; zero-trust NetworkPolicy defined before build begins |
| TP-03 | Observability as First-Class | Every agent emits OpenTelemetry traces, Prometheus metrics, and structured logs from the first commit; no agent reaches UAT without a Grafana dashboard | Dashboard-as-code is generated in bolt 1; observability is part of the Definition of Done for every agent |
| TP-04 | Cost Transparency with Hard Throttle | Each agent has a tagged cost centre; budget enforced with a hard throttle at 110% of monthly budget that cannot be self-overridden by the agent | Budget throttle is enforced at the agent gateway level, not just an alert; SRE Lead is the only person who can override with a logged justification |
| TP-05 | Layered Verification | AI-generated IaC passes five verification layers (L1 static analysis, L2 AI explanation artefact, L3 property tests, L4 canary deploy, L5 drift detection) before merge; no single-person hero review is sufficient at enterprise scale | CI/CD enforces L1–L4 automatically; L2 AI explanation artefact retained 12 months per IaC commit |
| TP-06 | Decision Explanation Artefact by Default | Every High-Risk AI agent (EU AI Act Art.6) produces a Decision Explanation Artefact (DEA) for every regulated decision — assembled from all log sources and stored immutably for 7 years | DEA generation service is a mandatory platform component; deployed with Pioneer 1 and applied to all subsequent Pioneers |

## Architecture Vision (Phase A)

**PHASE A** — Scope, mandate, and stakeholder alignment

### Architecture Vision Statement

"By Q4 2026, GlobalCorp will operate a unified AI Agent Platform (APEX) on cloud-native open standards, reducing time-to-market for AI use cases to a planning baseline of 5–6 weeks, achieving full EU AI Act and DORA compliance, and generating positive NPV within 24 months through platform economics. Productivity gains are tracked quarterly against actuals."

### Programme Scope

**In scope:** Cloud-native multi-region agent platform (4 regions); AI agent lifecycle management; multi-agent orchestration; self-service developer portal; shared knowledge bases; centralised observability and cost management; EU AI Act compliance automation; DEA generation; Agent Gateway; and 5 Pioneer Domain agents.

**Out of scope:** Foundation model training; customer-facing AI chatbots (Digital Channel programme); autonomous execution agents (requires separate regulatory approval pathway); data mesh platform build (existing programme).

### Architecture Constraints — SAW-APEX-001

| Constraint | Source | Architecture Impact |
| --- | --- | --- |
| Personal and sensitive data must remain within contractual jurisdiction | GDPR / PDPA / LGPD | Multi-region deployment; network policy blocks cross-border agent calls for personal data at kernel level |
| All AI models require Model Risk validation before production | Internal Model Risk Policy (aligned to SR 11-7) | Model Risk Gate in CI/CD is a T4 Reg-Gate; DEA required for High-Risk agents; explainability artefact mandatory |
| Cloud-native open standards; no proprietary SDK in core business logic | TP-01 | LLM calls via provider-agnostic adapter library; agent logic portable across cloud providers; OpenAPI for all agent interfaces |
| Zero-downtime deployment for critical services | Enterprise SLA | Argo Rollouts canary; SLO-based auto-rollback; no manual blue-green steps required |
| EU AI Act enforcement from August 2026 | EU Regulation 2024/1689 | High-Risk classification at intake; DEA pattern deployed from Pioneer 1; compliance pack (WP-012) delivered in H2 |
| All AI evolution must be framed as controlled DORA change | DORA Art.11 | Every model update, KB refresh, and agent topology change is a formal change event with ARB record and DORA change log |

### Five Pioneer Domains — Proof of Value

| # | Division | Agent | Use Case | Key Regulation | AI-DLC Bolts | Owner |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Customer Division | RiskScoringAgent | Automated risk-based decisioning with human escalation for high-value cases | Internal Model Risk Policy, GDPR | 3 bolts (~8 weeks) | Domain Architect 1 |
| 2 | Enterprise Division | VerificationAgent | Continuous customer verification monitoring, sanctions screening, and report drafting | AML Directive, FATF 40 | 3 bolts (~7 weeks) | Domain Architect 2 |
| 3 | Advisory Division | RebalancingAgent | Rule-based portfolio rebalancing recommendations with full suitability assessment | MiFID II Art.27, GDPR | 2 bolts (~6 weeks) | Domain Architect 3 |
| 4 | IT Operations | IncidentAgent | L1/L2 ticket triage, root-cause pattern recognition, and auto-remediation with SRE oversight | DORA Art.11 ICT Risk | 2 bolts (~5 weeks) | Domain Architect 4 |
| 5 | Risk & Compliance | ModelMonitorAgent | Model drift detection, backtesting orchestration, and regulatory evidence report generation | EU AI Act Art.9, Internal Policy | 3 bolts (~6 weeks) | Domain Architect 5 |

## Business Architecture (Phase B)

**PHASE B** — Capability model, value streams, and adaptive capability governance

### Business Capability Map — BCM-APEX-001

| L1 Capability | Type | Critical Gaps | APEX | AI-DLC Adaptive? | Governance Model |
| --- | --- | --- | --- | --- | --- |
| 1. AI Strategy & Governance | STATIC | 4 critical | 5/5 | Partial — policy enforcement via agents | Standard ARB quarterly review |
| 2. Agent Development | ADAPTIVE | 5 critical | 5/5 | YES — AI-DLC Construction | Bolt-level ARB; L1–L5 verification; bolt Definition of Done |
| 3. Agent Orchestration | ADAPTIVE | 4 critical | 4/4 | YES — AI-DLC Operations | Agent dependency map maintained; topology change = formal DORA change event |
| 4. Knowledge Management | ADAPTIVE | 4 critical | 4/4 | YES — continuous KB refresh | KB refresh = content change event; RAGAS gate; DPO sign-off for sensitive content |
| 5. AI Operations (AIOps) | ADAPTIVE | 5 critical | 5/5 | YES — AI-DLC Operations | DORA change framing applied; real-time monitoring; agent health scoring continuous |
| 6. Data Integration | STATIC | 2 critical | 3/4 | PARTIAL — Data Mesh governed | Data Mesh domain governance; quarterly data product review; APEX integrates, not owns |
| 7. Platform Enablement | STATIC | 4 critical | 4/4 | YES — portal AI-scaffolded | Standard deployment cadence; portal releases are standard CI/CD pipeline deployments |

### Value Stream — Agent Delivery End-to-End

| Stage | Baseline | APEX Plan | AI-DLC Planning Baseline | Key Constraints |
| --- | --- | --- | --- | --- |
| Intake & Qualification | 2–4 weeks | 5 days | 2 days | Data Maturity Gate may add 1–2 weeks in early cohorts (F-06) |
| Architecture & Design | 4–8 weeks | 10 days | 4–5 days | ARB Gate cannot be bypassed; political context capture session adds structured time in complex domains |
| Build & Integrate | 8–16 weeks | 3 weeks | 2 weeks | L1–L5 verification non-negotiable; DEA service adds 1 bolt for High-Risk agents |
| Validate & Govern | 6–10 weeks | 10 days | 7–8 days | T4 Reg-Gate (Model Risk opinion) is inviolable; explainability artefact mandatory for High-Risk |
| Deploy & Monitor | 2–4 weeks | 1 week | 3 days | DORA change framing adds a compliance record step; canary monitoring adds 1–2 days |
| TOTAL TIME-TO-MARKET | ~9 months | ~9.5 weeks | 5–6 weeks | Planning baseline used for budgets; 9.5 weeks used for business cases as conservative estimate |

## Related

- [APEX EA Part 1: Team Structure, RACI & Operating Model](09-apex-ea-team-structure-raci.md) — the team structure that executes this methodology.
- [APEX EA Part 3: Information Systems & Technology Architecture](11-apex-ea-information-systems-architecture.md) — the architecture this methodology produces.
- [AIDLC Enterprise Framework](14-aidlc-enterprise-framework-2025.md) — a parallel enterprise-wide AIDLC framework.

---

**Next:** [Part 3 — Information Systems & Technology Architecture](./11-apex-ea-information-systems-architecture.md) covers TOGAF Phases C and D — data, AI-native entities, application components, and cloud-native infrastructure.
