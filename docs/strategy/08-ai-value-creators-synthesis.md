---
title: "AI Value Creators: Key Findings & Core Themes"
doc_type: research-report
domain: strategy
status: current
canonical: true
topic_id: ai-value-creators-synthesis
maturity: expert
personas:
  - chief-ai-officer
  - enterprise-architect
  - strategy-lead
last_reviewed: 2026-07-19
covers_version: "2026-07-10"
supersedes:
  - docs/ai-economics/ai-value-creators-synthesis.md
tags:
  - ai-economics
  - value-creation
  - enterprise-ai
  - research
sources:
  - url: https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai
    title: "The State of AI in 2026"
    tier: 1
    retrieved: 2026-07-19
---

# AI Value Creators: Key Findings & Core Themes

## Why This Matters

AI adoption is near-universal (88% of organizations per McKinsey), but enterprise financial impact is rare: only ~6% are "AI high performers" with 5%+ of EBIT attributable to AI. This is **part 1 of 2**, covering the key findings from research across 1,993 enterprises in 105 countries, identifying value creation patterns, failure modes, and the characteristics of leaders. Part 2 covers advanced themes and recommendations.

---

## TL;DR

- **The adoption–value gap is the central fact of 2025–2026.** 88% use AI, 62% experimenting with agents, but only 39% report enterprise EBIT impact.
- **The failure cause is organizational, not technical.** McKinsey high performers are 3.6x more likely to pursue transformative workflow redesign (55% vs. ~20% of others).
- **The economics of intelligence are collapsing but not to zero.** Token costs fell >280x since Nov 2022, but agentic task cost exceeds inference — it adds coordination, memory, context, trust, governance.
- **Value compounds through flywheels.** Proprietary data + usage → better models → better decisions → more usage, creating structural moats.
- **Agentic value is created by re-architecting work, not by chasing model accuracy.**

---

## Key Findings

### Finding 1: The Adoption–Value Gap

| **Metric** | **Value** | **Source** |
|---|---|---|
| AI adoption | 88% | McKinsey Nov 2025[^1] |
| Experimenting with agents | 62% | McKinsey Nov 2025[^1] |
| Any enterprise EBIT impact | 39% | McKinsey Nov 2025[^1] |
| "AI high performers" (≥5% EBIT impact) | ~6% (109 of 1,993) | McKinsey Nov 2025[^1] |
| GenAI pilots with no P&L impact | 95% | MIT NANDA |
| Enterprise AI project failure rate | 80.3% | RAND 2025 |
| Firms abandoning most AI initiatives | 42% (2025) vs. 17% (2024) | S&P Global; ~$18B written off |

**The gap:** Most organizations have pilots and proof-of-concepts, but few have scaled AI to measurable business impact.

*Grounding note: the McKinsey figures above are independently confirmed[^1]. The MIT NANDA, RAND, S&P Global, BCG, IBM, JPMorgan, Klarna, Salesforce, and Palantir figures elsewhere on this page are carried over from the original source material as attributed and were not independently re-verified in the wave-1 grounding pass — treat as directional, not audited.*

### Finding 2: The Failure Cause is Organizational

MIT's "learning gap": tools that can't retain feedback, adapt to context, or integrate into workflows stall.

**McKinsey high performers** (top 6%) are:
- 3.6x more likely to pursue **transformative change**
- 55% report **fundamental workflow redesign** (vs. ~20% of others)
- Operate AI as a **self-reinforcing flywheel** (data → model → decisions → outcomes → more data)

**The 10/20/70 rule (BCG):** 10% algorithms, 20% data/tech, 70% people/process.

### Finding 3: Economics of Intelligence

- **Token cost collapse:** GPT-3.5-equivalent fell from $20/million tokens (Nov 2022) to $0.07 (Oct 2024) — >280x reduction (Gemini-Flash-8B)
- **But total spend rises (Jevons Paradox):** As costs fall, consumption grows faster
- **Agentic task cost ≠ inference cost.** Agentic tasks add: coordination, memory retrieval, context engineering, trust verification, governance/audit
- **Real scalable cost model:** service-as-software and outcome-based pricing, not flat-rate SaaS

### Finding 4: Value Compounds Through Flywheels

Proprietary data + usage → better models → better decisions → more usage = structural moat.

**Example:** IBM internal orchestration ("Client Zero") on track for $4.5B savings by end-2025; AskHR answers 94% of common employee inquiries.

### Finding 5: Agentic Value via Workflow Redesign

Agents create value beyond copilots via planning, reflection, tool orchestration, autonomous execution, and memory. **But:** agents amplify only where the end-to-end workflow is redesigned. You can't redesign a workflow if humans must orchestrate every step.

BCG: Agents = 17% of AI value in 2025, rising to 29% by 2028.

---

## Value Creation Patterns (High Performers)

| **Pattern** | **How it works** | **Example** |
|---|---|---|
| **Advisor/Analyst (copilot)** | Augment knowledge worker; 30–40% efficiency gain | JPMorgan 200K+ employees on LLM Suite |
| **Engineer** | Code assistant; 10–20% productivity | JPMorgan dev team usage |
| **Operator** | Autonomous execution on bounded workflows | Klarna support (~700→853 FTEs, $40M→$60M profit improvement) |
| **Orchestrator** | Multi-agent value streams | Salesforce Agentforce 32K conversations/week, 83% resolution |
| **Operating system** | Ontology-driven enterprise (perception → memory → reasoning → action → learning) | Palantir AIP |

---

## Anti-Patterns (Failures)

- "Pilot purgatory" — pilots that never reach production gates
- AI as cost-only (no revenue or capability angle)
- "AI confetti" — sprinkling AI across 20 processes (should concentrate on 2–3 reshape bets)
- Deploying autonomy on ungoverned data
- Treating AI as technology problem when it's organizational

---

## Footnotes

[^1]: McKinsey, "The State of AI in 2026": 88% adoption, 62% experimenting with agents, 39% report enterprise EBIT impact, ~6% (109 of 1,993 surveyed) are "high performers" with ≥5% EBIT impact. Source: https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai (tier 1, retrieved 2026-07-19)

---

## Related Documents

**Part 2:** [AI Value Creators: Advanced Themes & Recommendations](61-ai-value-creators-synthesis-advanced-themes-recommendations.md)

**Related:**
- [AI Value Creator Deliverables Pack](03-ai-value-creator-deliverables-pack.md) — 20 worked deliverables
- [Use Case Value Lifecycle](05-agentic-ai-use-case-value-lifecycle.md) — end-to-end example with financial model
