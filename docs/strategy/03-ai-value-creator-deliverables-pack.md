---
title: "AI Value Creator Deliverables: Reference Models & Architecture (1-10)"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ai-value-creator-deliverables-pack
maturity: practitioner
personas:
  - enterprise-architect
  - chief-ai-officer
  - platform-lead
last_reviewed: 2026-07-19
covers_version: ""
supersedes:
  - docs/ai-economics/AI-Value-Creator-Deliverables-Pack.md
tags:
  - ai-economics
  - enterprise-ai
  - deliverables
  - reference-architecture
sources: []
---

# AI Value Creator Deliverables: Reference Models & Architecture (1-10)

## Why This Matters

Consulting-grade AI implementation artifacts are rare in practice — most organizations lack worked examples showing what complete deliverables actually look like. This pack fills that gap by walking a single, realistic agentic AI use case (property & casualty claims automation) through 20 consulting-grade artifacts, letting you see exactly how each deliverable is structured and reuse the templates for your own initiatives. The first ten deliverables cover value creation models, architecture, and foundational strategy; see the companion part 2 for maturity models, governance, and playbooks.

---

## Companion Documents

This is **part 1 of 2** of the AI Value Creator Deliverables Pack. It pairs with:

- **Part 2:** [AI Value Creator Deliverables: Maturity, Governance & Playbooks](53-ai-value-creator-deliverables-pack-maturity-governance-playbooks.md)
- **Related:** [AI Value Creators Synthesis](08-ai-value-creators-synthesis.md) — the research framing for this pack
- **Related:** [Use Case Value Lifecycle: End-to-End Value Realization](05-agentic-ai-use-case-value-lifecycle.md) — companion use-case walk-through with financial modeling

---

## How to Use This Pack

Each deliverable is self-contained and organized for its primary audience:

- **Enterprise Architecture & platform teams** will prioritize Deliverables 1, 5, 6, 7, 9
- **Finance & the Investment Committee** will focus on 2, 8, 15, 17
- **Chief AI Officer & transformation leads** will use 4, 12, 14, 16, 20

---

## Contents (Full Pack: 1–20)

**Part 1 (this document: 1–10):**
1. AI Value Creation Reference Model
2. Enterprise AI Value Map
3. AI Business Capability Map
4. AI Operating Model Blueprint
5. Agentic Enterprise Reference Architecture
6. AI Platform Reference Architecture
7. Enterprise Cognitive Architecture
8. AI Investment Framework
9. AI Opportunity Matrix
10. AI Value Heatmap

**Part 2 (delivered separately: 11–20):**
11. AI Capability Maturity Model
12. AI Transformation Roadmap
13. Executive Decision Framework
14. AI Organization Design Blueprint
15. AI Portfolio Framework
16. AI Governance Model
17. AI Economics Model
18. AI Value Scorecard
19. AI Strategy Playbook
20. Enterprise Architect & Chief AI Officer Playbooks

---

## DELIVERABLE 1: AI Value Creation Reference Model

**Purpose:** The layered model connecting raw data to enterprise outcome — used to explain to executives where value is actually created, not just where AI is deployed.

### Reference Model

| **Layer** | **Claims-specific content** | **Value KPI** |
|---|---|---|
| **Enterprise outcome** | Combined ratio, policyholder retention, premium growth | Combined ratio (pts), NPS, retained premium $ |
| **Value layer** | Cost per claim, cycle time, leakage, CSAT | $ savings by driver (see Value Bridge) |
| **Orchestration layer** | Confidence routing across STP / augmented / human tiers | STP rate, override rate, routing accuracy |
| **Agent capability layer** | FNOL, Coverage, Estimation, Fraud/SIU, Settlement, Subrogation agents | Task success rate, agent accuracy |
| **Data & context layer** | Policy, telematics, weather, claim history, fraud pattern library | Data completeness %, context reuse rate |

### Reading the Model

Value compounds top-down: better context data raises agent accuracy, which raises the safe STP rate, which is what actually moves cost, cycle time, and leakage — the enterprise outcome layer only moves because the layers below it do.

---

## DELIVERABLE 2: Enterprise AI Value Map

**Purpose:** Maps the value stream stage-by-stage against the value levers AI touches and the annual dollar impact at each stage — used to sequence investment.

| **Value stream stage** | **Value levers touched** | **Annual $ impact (steady state)** |
|---|---|---|
| FNOL intake | Cycle time, CSAT | included in LAE savings |
| Triage & routing | Cost/claim, cycle time | included in LAE savings |
| Coverage verification | Cost/claim, leakage (miscoverage errors) | included in leakage savings |
| Damage estimation | Cost/claim, cycle time, leakage | $93M (LAE, blended) |
| Fraud / SIU screening | Leakage | $31M |
| Settlement & payment | Cost/claim, cycle time, CSAT | included in LAE + retention |
| Post-close (subrogation, audit) | Leakage (recovery) | upside not yet modeled — Phase 2 |
| Customer relationship | Retention | $3.2M |

---

## DELIVERABLE 3: AI Business Capability Map

**Purpose:** Rates each business capability in the claims function on current AI maturity and value potential — the input to the Opportunity Matrix (Deliverable 9).

| **Capability** | **AI maturity today** | **Value potential** | **Priority** |
|---|---|---|---|
| Claims intake / FNOL | Piloted | High | HIGH |
| Coverage verification | Piloted | High | HIGH |
| Damage assessment (auto) | Scaling | High | HIGH |
| Damage assessment (property) | Piloted | Medium-High | MED |
| Fraud / SIU detection | Piloted | High | HIGH |
| Reserve setting | Ad hoc | Medium | MED |
| Settlement negotiation (simple) | Piloted | High | HIGH |
| Bodily injury negotiation | Ad hoc | Medium (high value, low feasibility) | LOW |
| Subrogation identification | Ad hoc | Medium | MED |
| Litigation support | Not started | Medium | LOW |
| Customer communication | Scaling | Medium | MED |

---

## DELIVERABLE 4: AI Operating Model Blueprint

**Purpose:** Defines who owns what across the federated model of central Claims AI CoE + embedded human-agent operating pods.

| **Role** | **Reports to** | **Responsibility** |
|---|---|---|
| Chief AI Officer (program sponsor) | CEO / COO | Enterprise AI strategy, funding gates, board reporting |
| Claims AI Product Owner | Chief AI Officer | Roadmap, prioritization, value tracking for the claims program |
| Agent Factory Lead | Claims AI Product Owner | Builds & maintains the specialist agents, evals, prompt/tooling |
| Claims AI Risk & Compliance Officer | Chief Risk Officer (dotted: CAIO) | Model risk sign-off, regulatory review, fair-claims-handling audits |
| Regional Claims Ops Director | Chief Claims Officer | Runs the human-agent pods; owns adoption & override-rate targets |
| Agent Trainers / Eval Engineers | Agent Factory Lead | Curate training data, run evals, tune confidence thresholds |
| Claims AI QA Auditors | Claims AI Risk & Compliance Officer | Sample-audit STP and augmented-tier decisions |

### Design Principle

The CoE builds and governs the agents; Claims Ops owns adoption and outcomes. Splitting "build" from "run" ownership is what prevents the common failure mode of a central team optimizing for agent accuracy while nobody owns whether adjusters actually trust and use the system.

---

## DELIVERABLE 5: Agentic Enterprise Reference Architecture

**Purpose:** Shows how claims flow through the orchestrator, specialist agents, tool calls, and the human-in-loop / audit safety net.

Every specialist agent is stateless with respect to authority — it drafts, scores, or recommends, but only the orchestrator's confidence router (calibrated against the thresholds in Deliverable 13, in part 2) decides whether a claim proceeds straight-through, goes to a human co-signer, or escalates fully to an adjuster.

### Key Components

- **Claims Orchestrator:** Routes FNOL intake to specialist agents
- **Specialist Agents:** FNOL triage, Coverage verification, Estimation, Fraud/SIU scoring, Settlement recommendation
- **Tool Layer:** Policy admin systems, weather/telematics data feeds, repair-cost estimators, sanctions screening, payment rails
- **Human-in-Loop Console:** Escalation point for claims the confidence router doesn't clear
- **Audit Trail:** Immutable logging of all agent decisions and rationales for regulatory examination

---

## DELIVERABLE 6: AI Platform Reference Architecture

**Purpose:** The technical stack underneath the agent architecture — what an EA or platform team actually has to build, buy, or integrate.

### Stack Layers

- **Model Layer:** Foundation model + specialized agent models (possibly fine-tuned for claims domain)
- **Orchestration Framework:** Agent coordination, tool routing, confidence thresholds, escalation logic
- **Integration Layer:** APIs to policy admin system, coverage rules engine, external data feeds
- **Governance Layer:** Model monitoring, drift detection, audit trail storage, policy enforcement
- **Data Layer:** Real-time access to policy data, claim history, fraud patterns, regulatory rules

### Implementation Note

Most carriers buy the model layer and orchestration framework, and build the integration and governance layers themselves — the data layer is almost always the long pole, since claims data lakes and telematics feeds are rarely clean or unified at program start.

---

## DELIVERABLE 7: Enterprise Cognitive Architecture

**Purpose:** How the organization's institutional claims knowledge is captured, structured, and fed back into the agents over time.

| **Memory component** | **What it stores** | **Feedback loop owner** |
|---|---|---|
| Case history graph | Every claim's full lifecycle, decisions, and outcomes, linked by policyholder/peril | Agent Factory Lead |
| Adjuster decision precedent KB | Senior adjuster reasoning on edge cases, captured during pilot audits | Claims Ops Director |
| Fraud pattern library | Confirmed SIU findings, evolving fraud typologies by region | SIU / Fraud Agent owner |
| Regulatory rule base | State-by-state unfair claims practices rules, coverage interpretation precedent | Risk & Compliance Officer |
| Litigation outcome feed | Settled vs. litigated bodily-injury outcomes, used to calibrate reserve accuracy | Claims AI Risk Officer |

---

## DELIVERABLE 8: AI Investment Framework

**Purpose:** Stage-gated funding — money is released in tranches tied to evidence, not committed up front for the full 3-year program.

| **Gate** | **Funding released** | **Decision criteria to pass gate** |
|---|---|---|
| Discover→Business Case | ~$0.3M (analysis only) | Baseline signed off; top 3 opportunities ranked |
| Business Case→Pilot | $8.5M build + $1.8M change mgmt | Investment Committee approves Year 1 case & kill criteria |
| Pilot→Scale | $2.1M scale-out build | Pilot thresholds met (Use Case doc, Section 7) |
| Scale→Sustain (run-rate) | $7.6M / yr recurring | Unit economics hold; no adverse regulatory findings |

---

## DELIVERABLE 9: AI Opportunity Matrix

**Purpose:** Plots every claims sub-process by value potential vs. feasibility — the direct input to sequencing (Deliverable 12 in part 2).

**Sequencing rule used:** Prioritize the top-right quadrant first regardless of theoretical value elsewhere — feasibility gaps compound, so a smaller sure win beats a larger uncertain one.

### Quadrants

- **High value, High feasibility:** Auto glass + small PD claims, FNOL triage — reshape these first
- **High value, Low feasibility:** Bodily injury negotiation, Litigation support — defer or partner with third parties
- **Low value, High feasibility:** Customer communication — nice-to-have, useful for adoption/literacy
- **Low value, Low feasibility:** Litigation support — leave alone initially

---

## DELIVERABLE 10: AI Value Heatmap

**Purpose:** Cross-tabs claim type against value lever to show where the dollars concentrate — used to defend why auto glass and PD were sequenced first.

| **Claim type / Value lever** | **Cost reduction** | **Cycle time** | **Leakage** | **CSAT** | **Total impact** |
|---|---|---|---|---|---|
| Auto physical damage / glass | High | High | Medium | High | **Highest** |
| Property (water, wind, fire) | High | High | Medium | Medium | **High** |
| Liability / bodily injury | Low | Low | High | Medium | **Medium** |

Bodily injury scores lowest on cost/claim and cycle-time capture (agents assist but don't settle), but highest on leakage — which is why the fraud/SIU agent is deployed across all claim types from day one, even though full automation of BI claims themselves is out of scope.

---

## Related Resources

- **Part 2 of this pack:** [AI Value Creator Deliverables: Maturity, Roadmap & Portfolio](53-ai-value-creator-deliverables-pack-maturity-governance-playbooks.md) — Deliverables 11–15
- **Part 3 of this pack:** [AI Value Creator Deliverables: Governance, Economics & Playbooks](parts/01-ai-value-creator-deliverables-pack-playbooks-scorecard.md) — Deliverables 16–20
- **Use Case Walk-Through:** [Use Case Value Lifecycle](05-agentic-ai-use-case-value-lifecycle.md) — detailed financial modeling for this same claims use case
- **Value Framework:** [AI Value Creators Synthesis](08-ai-value-creators-synthesis.md) — the research behind these deliverables

## Sources

_No external sources cited yet; grounding pending (tracked for wave-1 follow-up)._
