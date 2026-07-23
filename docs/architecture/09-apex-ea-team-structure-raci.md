---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-team-structure-raci
title: "APEX EA Part 1: Team Structure, RACI & Operating Model"
date_created: 2026-04-01
last_reviewed: 2026-07-23
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
  - governance
---

# APEX EA Part 1: Team Structure, RACI & Operating Model

This is Part 1 of the APEX: AI Platform of Platforms EA Blueprint series — a 4-part series designed to guide enterprise-scale AI governance and delivery. Continues in [Part 2: AI-DLC Methodology & Foundation Architecture](./10-apex-ea-aidlc-methodology.md).

## APEX Operating Model — Who Does What

The APEX programme operates a federated model: a Platform Core Team builds and runs the shared infrastructure; Domain Squads build and operate agents within it; Governance Bodies provide oversight and approval authority; and Specialist Functions (Security, Compliance, Data) provide embedded expertise throughout the lifecycle.

### Organizational Hierarchy

```mermaid
graph TD
    A["TIER 0 — EXEC<br/>Group CTO Steering Committee<br/>Executive Sponsor, Monthly Oversight"] --> B["TIER 1 — GOVERN<br/>Architecture Board<br/>Chief AI Ethics Officer, Compliance Lead"]
    A --> C["DORA / EU AI Act"]
    B --> D["TIER 2 — PLATFORM"]
    D --> E["VP AI Platform"]
    D --> F["Platform Eng Lead"]
    D --> G["AI/ML Eng Lead"]
    D --> H["SRE Lead"]
    D --> I["DevX Lead"]
    B --> J["TIER 3 — DOMAINS"]
    J --> K["Domain Architects ×5"]
    J --> L["Agent Builders"]
    J --> M["Data Stewards"]
    B --> N["TIER 4 — SPECIALIST"]
    N --> O["Security Architect<br/>CISO Delegate"]
    N --> P["Data Architect<br/>CDO Delegate"]
    N --> Q["Model Risk Lead<br/>MRM Delegate"]
    N --> R["Reg Affairs Lead"]
```

**Governance hierarchy:** TIER 0 (executive) sets strategy and budget. TIER 1 (Architecture Board) approves architecture decisions and phase gates. TIER 2 (Platform core) delivers infrastructure and shared services. TIER 3 (Domain squads) operate agents. TIER 4 (Specialist functions) embed governance expertise throughout.

## Core Team Register

The Core Team Register details each role's tier, FTE allocation, source (internal, new hire, or contractor), and key accountabilities.

| Role ID | Role | Tier | FTE | Source | Key Accountabilities |
| --- | --- | --- | --- | --- | --- |
| T-01 | Group CTO | 0 | 0.1 (sponsor) | Internal | Executive authority; budget approval; regulator-facing sign-off |
| T-02 | VP AI Platform | 2 | 1.0 | Internal | Platform product roadmap; stakeholder alignment; steering pack |
| T-03 | Enterprise Architect | 1 | 1.0 | Internal | ADM governance; all architecture decisions; ARB chair |
| T-04 | Chief AI Ethics Officer | 1 | 1.0 | New hire | AI risk appetite; ethics review; EU AI Act risk classification sign-off |
| T-05 | Platform Engineering Lead | 2 | 1.0 | Internal | Cloud-native infrastructure; Kubernetes clusters; CI/CD platform |
| T-06 | Platform Engineers (×4) | 2 | 4.0 | Internal (×2) + Contractor (×2) | IaC authoring; agent gateway; agent control plane build |
| T-07 | AI/ML Engineering Lead | 2 | 1.0 | Internal | Agent framework selection; orchestration patterns; KB architecture |
| T-08 | AI/ML Engineers (×3) | 2 | 3.0 | Internal (×1) + AWS PS (×2) | Agent development; prompt engineering; guardrail configuration |
| T-09 | SRE / FinOps Lead | 2 | 1.0 | Internal | Platform reliability; cost governance; agent health scoring |
| T-10 | SRE Engineers (×2) | 2 | 2.0 | Internal (×1) + Contractor (×1) | Observability; on-call; canary monitoring; budget enforcement |
| T-11 | Developer Experience Lead | 2 | 1.0 | Internal | Self-service portal; developer documentation; agent marketplace UX |
| T-12 | DevX Engineer | 2 | 1.0 | Internal | Portal frontend; onboarding wizard; developer tooling |
| T-13 | Domain Architect (×5) | 3 | 5.0 | Internal (reassigned from domains) | Domain-level architecture; Pioneer agent design; Domain ARB liaison |
| T-14 | Compliance Analyst (AI) (×2) | 1 | 2.0 | New hire | EU AI Act classification; DORA evidence; DEA review; audit liaison |
| T-15 | Security Architect | 4 | 0.5 (embedded) | Internal (CISO delegate) | Security architecture sign-off; red-team coordination; zero-trust design |
| T-16 | Data Architect | 4 | 0.5 (embedded) | Internal (CDO delegate) | Data classification; embedding governance; data mesh integration |
| T-17 | Model Risk Lead | 4 | 0.5 (embedded) | Internal (MRM delegate) | Model risk opinions; explainability requirements; SR 11-7 alignment |
| T-18 | Regulatory Affairs Lead | 4 | 0.5 (embedded) | Internal (Group Compliance) | Regulator liaison; DORA evidence pack; EU AI Act submissions |

## RACI Matrix — Agent Lifecycle

This RACI matrix governs the key decision points in an agent's end-to-end lifecycle, from onboarding request through production deployment and ongoing operations.

| Activity | Ent. Arch | VP AI Plat | Platform Eng | AI/ML Eng | Domain Arch | Domain Dev | Security Arch | Data Arch | Model Risk | Compliance | SRE / FinOps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Agent onboarding request intake | C | A | I | I | R | C | I | I | I | C | I |
| Data Maturity Gate assessment | A | I | I | I | R | C | I | R | C | C | I |
| Agent architecture blueprint | A | C | C | C | R | C | R | R | C | C | I |
| Security design & threat model | C | I | C | I | C | I | R/A | C | I | I | I |
| Data classification & DPO sign-off | C | I | I | I | C | I | C | R/A | I | C | I |
| Prompt catalog design & review | I | I | C | R/A | C | R | I | C | I | C | I |
| Knowledge base architecture | C | I | C | R/A | C | R | I | R | I | I | I |
| IaC generation (AI-assisted) | I | I | R/A | C | C | R | C | I | I | I | I |
| L1–L5 verification pipeline | I | I | R/A | C | C | C | C | I | I | I | C |
| EU AI Act risk classification | C | I | I | I | C | I | I | I | C | R/A | I |
| Model risk validation opinion | C | I | I | C | C | I | I | I | R/A | C | I |
| DEA generation service config | C | I | R | R | C | C | C | I | C | A | I |
| Guardrail configuration | C | I | C | R/A | C | C | R | I | C | C | I |
| Canary deployment & SLO monitoring | I | I | C | I | I | C | I | I | I | I | R/A |
| Production go-live approval | A | C | C | I | C | I | C | C | C | C | C |
| Agent health score & budget review | I | C | C | I | C | I | I | I | I | I | R/A |
| Agent deprecation decision | C | A | C | I | R | C | I | I | I | I | C |

## RACI Matrix — Platform Governance & Architecture Board

The Architecture Review Board (ARB) meets weekly to approve architecture decisions, ratify principles, and manage deviations. This RACI shows roles in the governance function itself.

| Activity | Ent. Arch | VP AI Plat | Platform Eng | AI/ML Eng | Domain Arch | Domain Dev | Security Arch | Data Arch | Model Risk | Compliance | SRE / FinOps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARB session facilitation | R/A | C | I | I | C | I | C | C | I | I | I |
| Architecture principle ratification | A | C | I | I | C | I | C | C | C | C | I |
| Architecture deviation approval | A | C | I | I | C | I | C | C | I | C | I |
| New SBB build/buy decision | A | R | C | C | C | I | C | C | I | C | C |
| Architecture debt prioritisation | R/A | C | C | C | C | I | I | I | I | I | C |
| Conformance report (T1 automated) | I | I | R/A | I | I | I | C | I | I | I | C |
| Conformance escalation (T2 arch) | R/A | C | C | I | C | I | C | I | I | I | I |
| T4 Regulatory Gate sign-off | C | I | I | I | I | I | C | C | C | R/A | I |
| Executive steering pack | C | R/A | I | I | I | I | I | I | I | C | I |
| Agent marketplace curation | C | A | C | I | C | R | I | I | I | I | I |
| Platform SLA reporting | I | C | C | I | I | I | I | I | I | I | R/A |
| FinOps & chargeback reporting | I | A | R | I | I | I | I | I | I | I | R |

## RACI Matrix — Regulatory & Compliance

This RACI covers the regulatory and compliance activities required for enterprise AI governance, including EU AI Act classification, DORA evidence packs, GDPR data governance, and model risk management.

| Activity | Ent. Arch | VP AI Plat | Platform Eng | AI/ML Eng | Domain Arch | Domain Dev | Security Arch | Data Arch | Model Risk | Compliance | SRE / FinOps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EU AI Act risk tier classification | C | I | I | I | C | I | I | I | C | R/A | I |
| DEA completeness review | I | I | C | I | I | I | C | I | C | R/A | I |
| DORA change record creation | I | I | R | I | C | I | C | I | I | A | I |
| DORA 72-hr incident notification | C | C | C | I | I | I | C | I | I | R/A | C |
| DORA evidence pack compilation | C | I | C | I | C | I | C | C | C | R/A | I |
| GDPR data flow map maintenance | C | I | I | I | C | I | C | R/A | I | C | I |
| Model risk opinion sign-off | C | I | I | C | C | I | I | I | R/A | C | I |
| Explainability evidence (SHAP/LIME) | I | I | C | R | C | C | I | I | A | C | I |
| Regulator liaison & submissions | C | C | I | I | I | I | I | I | C | R/A | I |
| TLPT (penetration testing) oversight | C | I | C | I | I | I | R/A | I | I | C | C |
| Compliance dashboard maintenance | I | I | R | I | I | I | I | I | I | A | I |

## Responsibility Assignment Matrix & Stakeholder Map

### Responsibility Assignment Matrix — Platform Capabilities

The RAM maps each APEX platform capability to its accountable owner and key contributors. This extends the RACI to show structural ownership across the platform.

| Platform Capability | Accountable Owner | Primary Team | Secondary Contributors | Governance Body | Review Cadence |
| --- | --- | --- | --- | --- | --- |
| Agent Lifecycle Management (ALM) | VP AI Platform | AI/ML Engineering | Domain Architects, Compliance, Model Risk | ARB | Per deployment |
| Agent Gateway & Registry | Platform Engineering Lead | Platform Engineers | Security Architect, SRE | ARB (new agents) | Continuous (automated) |
| Knowledge Base Platform | AI/ML Engineering Lead | AI/ML Engineers | Data Architect, Domain Data Stewards | ARB + CDO delegate | Per KB refresh |
| Guardrails & Safety Layer | Chief AI Ethics Officer | AI/ML Engineering | Security Architect, Compliance | ARB + Ethics review | Per agent + quarterly red-team |
| Decision Explanation Artefact (DEA) | Compliance Lead | Platform Engineering | Model Risk, Legal, AI/ML Engineering | T4 Reg-Gate | Per regulated decision |
| CI/CD Pipeline & Layered Verification | Platform Engineering Lead | Platform Engineers | Security Architect, SRE | ARB (pipeline changes) | Per pipeline change |
| Observability & LGTM Stack | SRE Lead | SRE Engineers | Platform Engineering | SRE review | Continuous + weekly review |
| Cost Governance (FinOps) | SRE Lead | SRE Engineers | VP AI Platform, Finance | Monthly steering | Monthly |
| Developer Portal & Marketplace | DevX Lead | DevX Engineer | VP AI Platform, Domain Architects | Quarterly UX review | Per release |
| Regulatory Compliance Programme | Compliance Lead | Compliance Analysts | All Tier 4 specialists | Steering Committee | Monthly + ad-hoc |
| Data Mesh Integration | Data Architect | Domain Data Stewards | AI/ML Engineering, Platform Engineering | CDO governance forum | Per data product change |
| Security Architecture | Security Architect | Platform Engineering | All teams | CISO review board | Per phase + quarterly |
| Pioneer Domain 1 — Risk Scoring Agent | Domain Architect 1 | Domain Dev Team 1 | AI/ML Engineering, Model Risk, Compliance | Domain ARB | Per sprint |
| Pioneer Domain 2 — Verification Agent | Domain Architect 2 | Domain Dev Team 2 | AI/ML Engineering, Compliance | Domain ARB | Per sprint |
| Pioneer Domain 3 — Advisory Agent | Domain Architect 3 | Domain Dev Team 3 | AI/ML Engineering, Model Risk | Domain ARB | Per sprint |
| Pioneer Domain 4 — Incident Agent | Domain Architect 4 | Domain Dev Team 4 | SRE, Platform Engineering | Domain ARB | Per sprint |
| Pioneer Domain 5 — Model Monitor Agent | Domain Architect 5 | Domain Dev Team 5 | Model Risk, Compliance, AI/ML Eng | Domain ARB + MRM | Per sprint |

### Stakeholder Power / Interest Map

Stakeholder engagement strategy is derived from power (organisational authority and decision-making ability) and interest (level of direct impact from APEX).

| Stakeholder | Role | Power | Interest | Quadrant | Strategy | Engagement Cadence |
| --- | --- | --- | --- | --- | --- | --- |
| Group CTO | Executive Sponsor | High | High | KEY PLAYER | Manage closely; regular updates; co-own critical decisions | Monthly steering; ad-hoc for critical decisions |
| VP AI Platform | Programme Owner | High | High | KEY PLAYER | Daily collaboration; roadmap co-ownership; ARB participation | Daily standup; weekly roadmap review |
| Chief Information Security Officer | Security Authority | High | High | KEY PLAYER | Embedded security architect; CISO sign-off gate in ADM | Bi-weekly architecture review; CISO gate per phase |
| Group Compliance Lead | Regulatory Liaison | High | High | KEY PLAYER | Co-own compliance gates; evidence pack review; regulator briefings | Monthly evidence review; weekly during regulatory events |
| Chief Data Officer | Data Governance Authority | High | High | KEY PLAYER | Embedded data architect; Data Mesh integration authority | Bi-weekly; data architecture sign-off |
| Chief AI Ethics Officer | AI Risk Authority | High | High | KEY PLAYER | Direct line into ARB; EU AI Act classification authority | ARB weekly; ethics review per agent class |
| Chief Risk Officer | Enterprise Risk Authority | High | Medium | MANAGE CLOSELY | Quarterly risk briefings; model risk programme alignment | Quarterly + escalation for material AI risks |
| Chief Financial Officer | Budget Authority | High | Medium | MANAGE CLOSELY | Monthly FinOps reports; business case sign-off | Monthly FinOps review; annual budget cycle |
| Industry Regulator (PRA/ECB) | External Oversight | High | Medium | MANAGE CLOSELY | DORA evidence pack; EU AI Act submissions; proactive briefings | Quarterly regulatory briefing |
| Domain COOs (×5) | Pioneer Domain Sponsors | Medium | High | KEEP INFORMED | Regular progress updates; Pioneer milestone reviews | Monthly per domain |
| Domain Dev Teams | Agent Builders | Low | High | KEEP INFORMED | Self-service tooling; developer portal; clear onboarding | Bi-weekly sprint reviews; open ARB office hours |
| Internal Audit | Assurance Function | Medium | Medium | KEEP INFORMED | Annual audit; DORA evidence access; architecture artefacts | Annual audit; ad-hoc evidence requests |
| HR / People Team | Change Management | Low | Medium | MONITOR | Change impact comms; role transition support for displaced tools | Quarterly change update |
| External Cloud Providers | Technology Partners | Low | Low | MONITOR | SLA management; roadmap briefings | Quarterly account review |

### Team Interaction & Dependency Map

The following matrix shows how each team tier interacts with others, the nature of the dependency, and the formal channel for that interaction.

| From ↓ To | Platform Core Team | Domain Squads | ARB / Governance | Specialist Functions | External Stakeholders |
| --- | --- | --- | --- | --- | --- |
| **Platform Core Team** | Internal: sprint reviews, platform roadmap sync | Provides: infrastructure, tooling, self-service portal, CI/CD pipeline, guardrails | Reports to: ARB weekly; steering monthly. Seeks: approval for SBBs and deviations | Consults: Security (each phase), Data (KB design), Model Risk (agent risk) | Cloud provider SLA management; AWS PS engagement for AI/ML |
| **Domain Squads** | Consumes: platform services, agent templates, portal, pipeline. Raises: new agent requests, escalations | Internal: daily standups, shared domain backlog, cross-domain agent dependency reviews | Reports to: Domain ARB. Seeks: architecture approval, compliance sign-off per agent | Consults: Domain Architect (daily), Compliance (per agent intake), Data Steward (data flows) | Business stakeholder demos; UAT with end users |
| **ARB / Governance** | Approves: architecture decisions, SBBs, deviations, phase gate exits | Reviews: agent blueprints, domain architecture artefacts, compliance evidence | Internal: ARB weekly chair + secretariat. Escalates: to Steering Committee for T5 items | Receives: security review (CISO gate), compliance opinion (T4 Reg-Gate), Model Risk opinion | Regulator liaison via Compliance Lead; quarterly briefings |
| **Specialist Functions** | Embedded in: security design, data architecture, CI/CD gates | Provides: domain-level guidance, data classification, embedded model risk reviews | Feeds into: ARB with specialist opinions. Attends: relevant ARB agenda items | Cross-functional: security–compliance alignment; data–model risk alignment | No direct external engagement; all via Compliance Lead or CISO |
| **External Stakeholders** | Receives: SLA reports, FinOps dashboards, compliance packs | None (no direct domain team interaction) | Attends: quarterly regulator briefing. Reviews: DORA evidence pack, EU AI Act submissions | None direct | Peer industry: AI governance working groups; open-source community participation |

---

**Next:** [Part 2 — AI-DLC Methodology & Foundation Architecture](./10-apex-ea-aidlc-methodology.md) covers the AI-DLC delivery methodology and TOGAF Preliminary/Vision/Business phases that this team structure operates within.
