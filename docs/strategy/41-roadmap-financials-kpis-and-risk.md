---
title: "Roadmap, Financials, KPIs & Risk"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: roadmap-financials-kpis-and-risk
maturity: expert
personas: ["CFOs", "Chief Strategy Officers", "Executive Leadership", "Board Members"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: ["docs/enterprise-architecture/transformation/06_Roadmap_Financials_KPIs_and_Risk.md"]
tags: ["enterprise-ai", "roadmap", "financial-model", "kpi-framework", "risk-management"]
sources: []
---

From decision to delivery: the executable plan. The roadmap spans 36 months in three horizons with gated funding tranches, benefits audited by Finance, and top-10 risks with owners and mitigations.

## Delivery Roadmap: 30/90-Day Plans & Horizons

### First 30 Days — Mobilize

- Appoint transformation leader; charter CoE and governance bodies; confirm executive sponsors per lighthouse
- Launch discovery sprint: validate assumptions, baseline metrics for the five lighthouses, inventory in-flight AI work and shadow usage
- Publish interim AI acceptable-use policy and data-classification guardrails
- Select AI gateway and initial model set; stand up sandbox environment; begin vendor contract remediation
- Communicate workforce principles enterprise-wide before rumor fills the vacuum

### First 90 Days — Foundations & First Proof

- Platform core v1 live: gateway, logging/tracing, evaluation harness v1, first golden-path template
- Governance operating: risk tiering in force, use-case inventory live, RAI Board reviewing first Tier-2 cases
- Lighthouses 1-3 in build (service copilot, engineering assist, knowledge platform v1); engineering assist in production for first 200 developers
- Skills wave 1: champions network recruited; manager workshop pilot; all-employee AI fluency module launched
- Portfolio Board operating with kill criteria; benefits-audit method agreed with Finance

### Horizon Roadmap

| Horizon | Milestones (exit criteria) | Key Dependencies | Principal Risks |
|---|---|---|---|
| **6 months** | 3 lighthouses in production; knowledge platform serving 2 use cases; 30% of knowledge workers active weekly on governed tools; first audited benefits reported | Data-source access approvals; identity integration; anchor CoE hiring | Discovery reveals worse data quality than assumed (buffer: scope H1 to best-data domains) |
| **12 months** | Maturity Level 3 achieved; 8-12 production use cases; first A1 agents live in service and IT ops; semantic layer v1 (~50 metrics); $25-40M gross benefit run-rate | Platform golden paths stable; BU pods staffed; eval suites mature | Adoption plateau at enthusiasts; middle management disengaged |
| **24 months** | Maturity Level 4; 25-40 production use cases; A2 agents in bounded domains; product-based funding fully adopted; breakeven on cumulative net position; first AI-embedded product feature in market | Governance scales without queueing; knowledge-engineering throughput; talent retention | Governance bottleneck or public AI incident |
| **36 months** | AI-native operations in 2-3 selected processes (A3 in bounds); AI-embedded products contributing revenue; CoE shrunk as designed; $70-130M cumulative net benefit; Level 5 markers present | Sustained exec sponsorship; regulatory landscape absorbed | Strategy drift after leadership change |

---

## Investment & Cost Model (Illustrative)

| Category | Yr 1 | Yr 2 | Yr 3 | Notes |
|---|---|---|---|---|
| Platform & infrastructure | $8–11M | $10–14M | $9–13M | Consumption grows; FinOps offsets 15-25% via routing/caching |
| Model & software licensing | $3–5M | $5–8M | $6–9M | Multi-vendor; unit costs down, volume up |
| Talent (CoE, platform, pods) | $9–12M | $12–16M | $10–13M | ~45-60 FTEs at peak plus federated capacity |
| Data & knowledge engineering | $3–5M | $4–6M | $3–5M | Semantic layer, ingestion, expert-knowledge capture |
| Change, skills & communications | $3–4M | $3–4M | $2–3M | Includes reskilling co-funding commitment |
| Governance, security & assurance | $2–3M | $2–3M | $2–3M | Tooling + assurance capacity in risk/audit |
| **Total investment** | **$28–38M** | **$35–48M** | **$30–42M** | Released in tranches against value gates |

### Benefits Realization Plan

| Benefit Stream | Steady-State Share | How It Is Counted |
|---|---|---|
| **Productivity & cost-to-serve** (service, engineering, finance ops, IT) | ~55% | Pre-registered baselines; Finance-audited; counted at realization (capacity redeployed or cost removed), not at tool rollout |
| **Revenue** (win-rate, personalization, AI-embedded product features) | ~30% | Attribution via controlled rollouts / holdout groups where feasible; conservative haircuts applied |
| **Risk, quality & speed** (error reduction, faster close, compliance efficiency) | ~15% | Quantified where defensible; otherwise reported as non-financial KPIs, never double-counted |

**Governing rule:** Report **net** value after platform and run costs. Portfolio Board publishes kill decisions alongside wins — credibility is a compounding asset.

---

## KPI Framework & Executive Steering Dashboard

| Layer | KPIs (Steering Set) | Target Trajectory |
|---|---|---|
| **Value** | Audited net benefit ($); benefit run-rate vs plan; % Finance-verified | Breakeven months 20-27; 100% verification |
| **Adoption** | Weekly active governed-AI users (% knowledge workforce); use cases in production; median tasks/user | 30% by mo 6, 60% by mo 12, 80%+ by mo 24 |
| **Delivery** | Median idea-to-production time; % initiatives on paved road; platform availability | &lt;30 days by mo 18; >90% paved-road |
| **Quality & trust** | Eval pass rates; hallucination/critical-error rate per 1,000 outputs; CSAT delta; incident count & severity | CSAT never negative; declining error rates |
| **Risk & compliance** | % AI systems inventoried & tiered; Tier-1 reviews on time; audit findings; deletion-propagation SLA | 100% inventory; zero overdue Tier-1 reviews |
| **People** | Certified practitioners; internal mobility from affected roles; sentiment index; attrition in key AI roles | Reskilling commitments met; key-role attrition &lt;10% |
| **Economics** | Cost per unit of work (per resolved ticket, per PR, per document); token spend vs budget | Unit costs declining QoQ |

**Executive Steering Dashboard:** One page, monthly, exactly these seven rows with red/amber/green status, trend arrows, plus the top three decisions needed. Anything longer will not be read.

---

## Risk Register: Top 10

| # | Risk | L | I | Mitigation / Owner |
|---|---|---|---|---|
| 1 | Value not realized: pilots scale activity, not P&L | M | H | Benefits-audit discipline; kill criteria; product funding — CFO |
| 2 | Public AI incident (harmful output, data leak) damages brand/regulatory standing | M | H | Risk tiering, eval & red-team gates, incident playbooks, comms readiness — CRO/CISO |
| 3 | Adoption stalls at enthusiast layer; middle management disengaged | H | H | Manager incentives & toolkits; friction telemetry; co-design — CHRO |
| 4 | Data quality/access worse than assumed, delaying Horizon 1 | H | M | Discovery sprint validation; scope lighthouses to best-data domains; data-product funding — CDO |
| 5 | Governance becomes a queue; teams route around it (shadow AI persists) | M | H | Two-speed model; Tier-3 self-service; 2-week exception SLA — GC/CRO |
| 6 | Key-talent scarcity/attrition in AI engineering and evaluation roles | H | M | Anchor hires + aggressive internal development; retention plans — CHRO/CTO |
| 7 | Vendor lock-in or adverse contract terms (data use, IP, pricing) | M | M | Model-agnostic gateway; contract standards; annual portability test — CTO/Procurement |
| 8 | Regulatory shift (AI Act enforcement, sector rules) invalidates deployments | M | M | Obligations register; inventory & logging as compliance backbone; regulatory watch — GC |
| 9 | Cost overrun: token/GPU spend scales faster than value | M | M | FinOps guardrails; routing to smaller models; unit-economics review — CFO/CTO |
| 10 | Transformation fatigue / leadership change breaks continuity | M | H | Board-level KPI reporting; institutionalized operating model; staged wins narrative — CEO |

**Register reviewed monthly by Portfolio Board; Tier-1 risks reported to Board's risk committee quarterly.**

---

## Related

- [Executive Summary & AI Vision](35-executive-summary-and-ai-vision.md)
- [Target Operating Model, Organization & Change](40-target-operating-model-and-change.md)
- [CTO Transformation Blueprint: FinOps & Security Threat Model](77-enterprise-ai-transformation-blueprint-cto-guide-2026-finops-security-threat-model.md)

## Sources

- Gartner — AI investment benchmarks (2026)
- McKinsey — Transformation program risk management (2026)
- Forrester — Benefits realization for enterprise AI (2026)
