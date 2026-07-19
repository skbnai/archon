---
title: "AI Value Creator Deliverables: Maturity, Roadmap & Portfolio (11-15)"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ai-value-creator-deliverables-pack-part2
maturity: practitioner
personas:
  - enterprise-architect
  - chief-ai-officer
  - platform-lead
  - ai-governance
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - ai-economics
  - enterprise-ai
  - deliverables
  - governance
  - maturity-model
sources: []
---

# AI Value Creator Deliverables: Maturity, Roadmap & Portfolio (11-15)

## Why This Matters

This is **part 2 of 3** of the AI Value Creator Deliverables Pack, covering capability maturity models, multi-year transformation roadmaps, organizational design blueprints, and portfolio governance. Deliverables 11–15 ground the strategic decisions from part 1 in operational realities: how capabilities actually mature, how portfolios get ranked, how organizations reshape, and how the transformation stays on track across multiple years.

---

## Context & Related Documents

This part is a continuation of:

- **Part 1:** [AI Value Creator Deliverables: Reference Models & Architecture](03-ai-value-creator-deliverables-pack.md) — Deliverables 1–10 covering value creation models, architecture, and strategy
- **Part 3:** [AI Value Creator Deliverables: Governance, Economics & Playbooks](parts/01-ai-value-creator-deliverables-pack-playbooks-scorecard.md) — Deliverables 16–20 covering governance, economics, and role-specific playbooks
- **Use Case:** [Use Case Value Lifecycle](05-agentic-ai-use-case-value-lifecycle.md) — worked financial model for the same claims use case
- **Synthesis:** [AI Value Creators Synthesis](08-ai-value-creators-synthesis.md) — the research foundation for all 20 deliverables

---

## Contents (Part 2: Deliverables 11–15)

| Deliverable | Type | Primary Audience |
|---|---|---|
| 11. AI Capability Maturity Model | Governance & measurement | CoE, platform teams |
| 12. AI Transformation Roadmap | Timeline & phasing | Executive sponsors, PMO |
| 13. Executive Decision Framework | Routing rules & thresholds | Orchestrator design teams |
| 14. AI Organization Design Blueprint | Workforce planning | CAIO, HR, operations |
| 15. AI Portfolio Framework | Initiative ranking | Executive leadership |

---

## DELIVERABLE 11: AI Capability Maturity Model

**Purpose:** Five maturity levels used consistently across every capability so progress can be tracked on a common scale. This provides a common vocabulary for discussing readiness across the organization.

### Maturity Levels

| **Level** | **Definition** |
|---|---|
| **1 — Ad hoc** | Manual process; AI used informally or not at all |
| **2 — Piloted** | Agent deployed in a controlled pilot, human-audited at high sample rates |
| **3 — Scaling** | Agent live in production across multiple regions/lines, sampled audit |
| **4 — Optimized** | Agent performance actively tuned against a value scorecard; feedback loop live |
| **5 — Autonomous** | Agent operates within governed authority limits with minimal human review |

### Claims Program Maturity (Illustrative)

| **Capability** | **Current Level** | **Target (Year 3)** | **Path** |
|---|---|---|---|
| Claims intake / FNOL triage | Level 3 — Scaling | Level 4 — Optimized | Optimize routing accuracy; improve cycle time |
| Auto physical damage estimation | Level 3 — Scaling | Level 4 — Optimized | Expand to property lines; tune price thresholds |
| Property damage estimation | Level 2 — Piloted | Level 3 — Scaling | Expand regions; build damage-pattern library |
| Fraud / SIU scoring | Level 3 — Scaling | Level 4 — Optimized | Increase fraud-detection accuracy; reduce false positives |
| Settlement recommendation (STP tier) | Level 4 — Optimized | Level 4 — Optimized | Defend performance; hold margins |
| Bodily injury negotiation support | Level 1 — Ad hoc | Level 2 — Piloted | Pilot adjuster-facing drafting agent |
| Subrogation identification | Level 1 — Ad hoc | Level 2 — Piloted | Build recovery-pattern library; pilot scoring |

### Maturity Progression Rules

- Capabilities move through levels only after gate criteria are met (see part 1, Deliverable 8)
- Regression to a lower level is allowed if performance drift or safety issues emerge
- "Optimized" and "Autonomous" require active feedback loops — no passive holding of a level

---

## DELIVERABLE 12: AI Transformation Roadmap

**Purpose:** The 36-month phased rollout, tied to the funding gates in part 1, Deliverable 8. This serves as the master schedule driving both technical and organizational changes.

### Phase Timeline

| **Milestone** | **Target month** | **Owner** | **Key Deliverables** |
|---|---|---|---|
| Baseline signed off; business case approved | M3 | Claims AI Product Owner | Baseline metrics finalized; Investment Committee approval |
| Pilot live: auto glass + small PD, 2 regions | M6 | Agent Factory Lead | FNOL + settlement agents live; 30 days 100% human audit |
| Property line added; national auto rollout begins | M15 | Regional Claims Ops Directors | Property estimation agent live; auto agents deployed to 8 regions |
| Liability augmentation live; full national scale | M24 | Claims AI Product Owner | Liability drafting agent live; all regions operational |
| Continuous optimization loop fully operational | M36 | Claims AI CoE | Feedback loops established; quarterly value scorecard reviews live |

### Key Phase Gates

- **Pilot gate (M6→Scale):** STP accuracy ≥97%, override rate &lt;12%, cycle time ≥30% reduction vs. baseline
- **Scale gate (M15→Rollout):** Unit economics hold; no adverse regulatory findings; field readiness confirmed
- **National gate (M24→Sustain):** All regions reporting; adoption targets met (>75% STP where authorized); payback achieved

---

## DELIVERABLE 13: Executive Decision Framework

**Purpose:** The actual routing rules the orchestrator applies — this is what "agent confidence" cashes out to operationally. These rules translate governance policy into executable code.

### Confidence-Threshold Decision Table

| **Condition** | **Routing decision** | **Rationale** |
|---|---|---|
| Claim value &lt; $5,000 AND agent confidence > 92% AND no prior fraud flag | Straight-through: auto-settle, no human touch | Low value + high confidence + clean history = safe automation |
| Claim value $5,000–$50,000 AND agent confidence > 80% | Agent-drafted estimate/settlement; adjuster co-signs | Medium value requires human review, but agent draft accelerates process |
| Fraud/SIU score above threshold | Route to SIU regardless of claim value | Fraud risk overrides confidence thresholds |
| Bodily injury or litigation flag present | Human-led; agents provide research & drafting support only | High-stakes decisions require human authority |
| Agent confidence below threshold for its tier, any claim | Escalate to next tier up (never auto-approve on low confidence) | Fail-safe: uncertainty always escalates |

### Implementation Notes

- Confidence thresholds are calibrated during pilot (Section 7, part 1, Deliverable 8 gate criteria)
- Thresholds are reviewed quarterly; changes require Model Risk Committee approval
- All escalations are logged with reason code for governance audit

---

## DELIVERABLE 14: AI Organization Design Blueprint

**Purpose:** How the claims workforce actually changes shape — headcount, new roles, and the reskilling path, not just net FTE change.

### Workforce Transition Plan

| **Role** | **Today (Year 0)** | **Year 1** | **Year 2** | **Year 3** | **Notes** |
|---|---|---|---|---|---|
| Claims adjuster | 1,100 | 1,050 | 920 | 830 | Attrition-managed (12–15%/year) |
| Supervisors | 150 | 145 | 140 | 130 | Scaled with adjuster headcount |
| Agent Trainers / Eval Engineers | 0 | 4 | 14 | 24 | New role; hired externally + internal transitions |
| Claims AI QA Auditors | 0 | 2 | 8 | 18 | New role; promoted from high-performing adjusters |
| Complex-claims specialists | — | — | 45 | 90 | Redeployed from high-volume simple claims |

### Reskilling Path

**Why "Redeployment Path, Not Just Reduction":** The FTE reduction is managed entirely through attrition over 24 months (typical adjuster attrition runs 12–15%/year). Adjusters freed from simple, high-volume claims are the pipeline for the new QA auditor and complex-claims specialist roles — the reskilling path is built into the roadmap, not left to chance.

### Implementation

- Identify top-performing adjusters for auditor roles in Month 2–3 (before pilot launch)
- Offer training and promotion pipeline for new roles starting Month 6
- Avoid layoffs; manage reduction through voluntary transitions and attrition
- Board-level commitment to reskilling investment (budget for training ~$2–4M over 3 years)

---

## DELIVERABLE 15: AI Portfolio Framework

**Purpose:** All active AI initiatives in the claims division, ranked and risk-rated the same way — prevents the program from being judged on one flagship use case alone.

### Claims AI Initiative Portfolio

| **Initiative** | **Stage** | **Owners** | **Est. annual value** | **Risk** | **Kill criteria** |
|---|---|---|---|---|---|
| FNOL triage agent | Scaling | Claims AI Product Owner | Included in LAE savings (~$15M) | Low | STP rate &lt;25% at M12 |
| Auto glass / small-PD STP agent | Optimized | Regional Ops Directors | ~$38M (largest single contributor) | Low | Unit economics deteriorate >10% |
| Property estimation agent | Piloted | Agent Factory Lead | ~$22M | Medium | Accuracy &lt;92% at M9; pilot gates missed |
| Fraud / SIU scoring agent | Scaling | SIU/Fraud owner | $31M | Medium | False-positive rate >50% (loses adjuster trust) |
| Subrogation identification agent | Not started | Finance & SIU | ~$6M (Phase 2 estimate) | Medium | Defer to Phase 2 funding gate |
| Customer status chat agent | Scaling | Customer Experience | CSAT contribution, not separately valued | Low | Adoption &lt;40% at M12 |

### Portfolio Rules

- **High value + High risk initiatives** get quarterly reviews by the Model Risk Committee and executive sponsor
- **Kill criteria** are set at initiative kickoff and reviewed quarterly; a missed gate triggers automatic kill-or-pivot decision
- **Rebalancing happens quarterly** — a successful initiative can free budget for new starts; a struggling initiative gets remediation support before kill

---

## Related Resources

- **Part 1 of this pack:** [AI Value Creator Deliverables: Reference Models & Architecture](03-ai-value-creator-deliverables-pack.md) — Deliverables 1–10
- **Part 3 of this pack:** [AI Value Creator Deliverables: Governance, Economics & Playbooks](parts/01-ai-value-creator-deliverables-pack-playbooks-scorecard.md) — Deliverables 16–20
- **Use Case Walk-Through:** [Use Case Value Lifecycle](05-agentic-ai-use-case-value-lifecycle.md) — detailed financial modeling for this same claims use case
- **Value Framework:** [AI Value Creators Synthesis](08-ai-value-creators-synthesis.md) — the research behind these deliverables

## Sources

_No external sources cited yet; grounding pending (tracked for wave-1 follow-up)._
