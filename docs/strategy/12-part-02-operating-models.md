---
title: "Enterprise AI Operating Models: Centralised to Domain Teams"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-02-operating-models
maturity: practitioner
personas: [cto, enterprise-architect, program-manager]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-02-operating-models.md
tags: ["operating-model", "ai-coe", "hub-spoke", "federated-ai", "organizational-design"]
sources: []
pagination_next: strategy/part-02-operating-models-operating-models-platform-ai-native
---

# Enterprise AI Operating Models: Centralised to Domain Teams

The operating model determines whether AI capabilities scale across the enterprise or remain trapped in proof-of-concept purgatory. McKinsey (2025) identifies operating model misalignment as the primary reason only ~6% of enterprises capture disproportionate AI value. Deloitte's research shows enterprises that design operating models for AI first achieve 3× the ROI compared to those who reverse the sequence.

The right operating model depends on enterprise size, AI maturity, regulatory environment, existing data landscape, cultural readiness, and speed versus control preferences.

## Model 1: Centralised AI Centre of Excellence (CoE)

**Description:** A single central AI team owns all AI strategy, delivery, standards, and governance. Business units consume AI services delivered by the CoE.

**When to Use:** Early AI maturity (Level 1–2); highly regulated industries (banking, pharma, defence); limited AI talent; rapid standardization needed.

**Org Structure:** CoE reports to CTO/CIO/CAIO with functions for Strategy, Platform Engineering, Data Science, Product Management, Responsible AI, and Delivery.

**Funding:** Corporate-funded (centrally held budget); no direct business unit charges; treated as infrastructure cost.

**Ownership:** CoE owns models, platforms, standards, governance, delivery. Business units own requirements, validation, adoption.

**Advantages:** Standards enforced consistently; scarce talent concentrated; centralized governance; consolidated vendor relationships; clear accountability.

**Disadvantages:** Bottleneck as demand scales; distance from business domain knowledge; slow to respond to business changes; empire-building risk; single point of failure.

**KPIs:** AI use cases delivered per quarter; time-to-production (days); business satisfaction; model reuse rate; governance incidents.

**Chargeback:** No chargeback at early maturity; transition to project-based by BU at higher levels.

**Maturity Fit:** Best at Level 1–2; must evolve or becomes bottleneck.

## Model 2: Hub and Spoke

**Description:** Central AI Hub (CoE or platform team) sets standards and builds shared platforms. Business unit "Spokes" have embedded AI capability operating within Hub governance.

**When to Use:** Maturing enterprises Level 2–3; large enterprises with strong BU autonomy; need standardization plus business proximity; scaling beyond pure CoE.

**Org Structure:** Hub owns Platform Engineering, Standards & Governance, Responsible AI, Talent. Spokes embed AI leads and engineers in each BU.

**Reporting:** Hub reports to CAIO/CTO. Spoke AI Leads have dual reporting (functionally to Hub, administratively to BU head).

**Funding:** Hub centrally funded (infrastructure, platform, governance); Spokes BU-funded (headcount, projects); hybrid option: Hub charges Spokes for platform consumption.

**Ownership:** Hub owns platform, standards, governance, talent. Spokes own domain-specific models, prompts, agents, validation.

**Advantages:** Consistent standards across Spokes; business proximity of Spokes; scales beyond CoE; shared platforms reduce duplication; talent rotation pathways.

**Disadvantages:** Coordination overhead; Spoke drift from standards; power dynamics friction; inconsistent maturity; quality variance.

**KPIs:** Hub platform adoption rate; standards compliance; time-to-production; cross-BU reuse rate; Spoke capability maturity.

**Chargeback:** Platform chargeback (Spokes pay Hub); Spoke headcount charged to BU.

**Maturity Fit:** Dominant model for large enterprises at Level 2–4.

## Model 3: Federated AI

**Description:** Business units operate autonomous AI capability with minimal central coordination. Lightweight central function sets guardrails (security, compliance, ethics) without controlling delivery.

**When to Use:** Highly decentralized enterprises (conglomerates, holding companies); divisions with different regulatory environments; fast-moving environments (speed > standardization); Level 3–4 maturity with genuine BU capability.

**Org Structure:** Enterprise AI Governance Council (lightweight, policy-only) with self-contained AI teams per division; council has no delivery authority.

**Reporting:** Each division's AI team reports to division CTO/CIO. Council is cross-divisional body (no reporting authority).

**Funding:** Fully divisional-funded; no central AI budget except governance council operating costs.

**Ownership:** Divisions own everything (strategy, platform, delivery, governance within enterprise guardrails); enterprise council owns enterprise-wide policies.

**Advantages:** Maximum agility per division; deep domain specialization; strong division ownership; no central bottleneck; natural scaling.

**Disadvantages:** Massive duplication of investment; inconsistent governance; talent fragmentation; weak vendor leverage; no enterprise-wide visibility.

**KPIs:** Per-division AI ROI; enterprise-wide policy compliance (audit); duplication index; AI incident rate.

**Chargeback:** No central chargeback; each division self-funded.

**Maturity Fit:** Level 3–5; high risk if used early (governance gaps).

## Model 4: Embedded AI Teams

**Description:** Small AI teams (2–4 people) embedded within product/operations teams. No central AI function. AI treated as engineering competency.

**When to Use:** Tech-native or digital-first enterprises; product-led organizations (software, digital platforms); every product team ships AI; Level 3–5 with strong engineering culture.

**Org Structure:** AI engineers report to product/engineering leads, not central function. Lightweight AI Infrastructure Guild for best-practice sharing (voluntary, advisory).

**Reporting:** Embedded AI engineers report to product/operations leads; Guild is voluntary.

**Funding:** Product team headcount budget includes AI engineers; no separate AI budget line.

**Advantages:** Maximum integration with product context; no handoff friction; AI as first-class engineering; unambiguous ownership; strong accountability.

**Disadvantages:** No enterprise AI standardization; talent costs spread across teams; siloed learning; inconsistent quality; compliance risk.

**Maturity Fit:** Level 3–5 for digital-native companies; risky in regulated industries without governance overlay.

---

## Related

- [Enterprise AI Operating Models: Platform-First to AI-Native](64-part-02-operating-models-operating-models-platform-ai-native.md)
- [Organizational Roles & RACI](18-part-08-organizational-roles.md)
- [AI Platform Operating Model](17-part-07-platform-operating-model.md)

## Sources

