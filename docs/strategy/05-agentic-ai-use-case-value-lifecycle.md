---
title: "Use Case Value Lifecycle: Overview, Stages & Baseline"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: agentic-ai-use-case-value-lifecycle
maturity: practitioner
personas:
  - chief-ai-officer
  - finance-partner
  - business-leader
last_reviewed: 2026-07-19
covers_version: ""
supersedes:
  - docs/ai-economics/Agentic-AI-Use-Case-Value-Lifecycle.md
tags:
  - ai-economics
  - use-case-methodology
  - value-lifecycle
  - agentic-ai
sources: []
---

# Use Case Value Lifecycle: Overview, Stages & Baseline

## Why This Matters

A worked example of an agentic AI use case walked through the complete enterprise value lifecycle — from baseline diagnosis through business case, pilot, scale, and measured value realization. This is **part 1 of 2**, covering the end-to-end methodology and baseline metrics. See part 2 for the financial model and assumptions.

---

## Executive Summary

A national P&C carrier deploys a multi-agent claims system — FNOL intake, coverage verification, damage estimation, fraud screening, settlement recommendation agents — orchestrated with human-in-the-loop checkpoints across auto and property claims. The program is scoped, funded, and measured using the value lifecycle: **Discover** → **Business Case** → **Pilot & Build** → **Scale** → **Sustain & Optimize** → **Measure & Reinvest**.

Value is a bridge of three distinct streams (efficiency, loss-cost leakage, retention), realized against a ramp schedule mirroring actual rollout claim-line by claim-line, region by region.

---

## Six-Stage Value Lifecycle

### Stage 1 — Discover (Weeks 1–8)
Baseline current-state: cost per claim, cycle time, leakage rate, CSAT, adjuster capacity by claim type and region. Build AI Opportunity Matrix to rank sub-processes by value potential × feasibility.

**Gate criteria:** Baseline metrics signed off by Finance and Claims Ops; top 3 opportunities selected.

### Stage 2 — Business Case & Design (Weeks 6–14)
Build value bridge and 3-year financial model. Define target architecture (orchestrator + specialist agents + human-in-loop). Define STP eligibility rules and confidence thresholds with Legal, Compliance, Model Risk.

**Gate criteria:** Investment Committee approves Year 1 funding against defined ramp and kill criteria.

### Stage 3 — Pilot & Build (Months 3–6)
Build orchestration layer and two highest-feasibility agents (FNOL triage, auto glass/small-PD settlement). Launch in 2 regions with 100% human audit for 30 days, stepping down to statistical sampling.

**Gate criteria:** STP accuracy ≥97%, human override rate &lt;12%, cycle time ≥30% reduction vs. baseline.

### Stage 4 — Scale (Months 6–24)
Extend to property and additional regions; then national auto and liability augmentation. Each wave repeats pilot gate at smaller scale.

**Gate criteria:** Unit economics hold or improve; no adverse regulatory findings.

### Stage 5 — Sustain & Optimize (Month 24+)
Continuous learning loop: settlement outcomes, litigation results, SIU findings feed back into agent training and fraud libraries. Governance council reviews model drift and override-rate trends quarterly.

### Stage 6 — Measure & Reinvest (Ongoing, quarterly)
Actual realized value measured against baseline. Delta between plan and actual determines next wave's funding.

**Gate criteria:** Realized value within 15% of plan maintains funding pace; below that triggers re-baseline.

---

## Baseline vs. Target State (Year 3 Steady State)

| **Metric** | **Baseline (today)** | **Target (Yr 3)** | **Change** |
|---|---|---|---|
| Annual claims volume | 480,000 | 480,000 | Flat for comparison |
| Straight-through (STP) rate | 8% | 42% | +34 pts |
| Agent-augmented rate | 0% | 40% | New tier |
| Avg. cost per claim (LAE) | $625 | $431 | -31% |
| Avg. cycle time FNOL→settlement | 13.4 days | 8.3 days | -38% |
| Leakage (% of indemnity) | 4.2% | 2.6% | -38% relative |
| Claims CSAT | 71% | 79% | +8 pts |
| Adjuster FTE (attrition-managed) | 1,100 | 830 | -25%, no layoffs |

---

## Use Case Scope

### In Scope
- Auto physical damage & auto glass claims
- Residential property (water, wind, fire) claims
- Coverage verification & policy interpretation
- Damage estimation (agent-drafted, human-approved >$5K)
- Fraud / SIU referral scoring
- Settlement recommendation & payment (STP tier only)

### Out of Scope (Phase 1)
- Commercial lines, catastrophe, litigation, total-loss disputes, reinsurance, bodily injury settlement authority

### Claim Mix (Baseline)
- **Auto physical/glass:** 65%, low-medium complexity → STP + agent-augmented
- **Property:** 20%, medium complexity → Agent-augmented
- **Liability/BI:** 15%, high complexity → Agent-assisted (human-led)

---

## Related Documents

**Part 2:** [Use Case Value Lifecycle: Financial Model & Assumptions](56-agentic-ai-use-case-value-lifecycle-financial-model-assumptions.md) — detailed 3-year financial model, value bridge, sensitivity analysis

**Related:**
- [AI Value Creator Deliverables Pack](03-ai-value-creator-deliverables-pack.md) — 20 worked deliverables for this same use case
- [AI Value Creators Synthesis](08-ai-value-creators-synthesis.md) — research foundation for value lifecycle methodology

## Sources

_No external sources cited yet; grounding pending (tracked for wave-1 follow-up)._
