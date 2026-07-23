---
title: "Portfolio Consulting Frameworks: Portfolio Management"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol8-portfolio-consulting-frameworks
maturity: practitioner
personas:
  - enterprise-architect
  - portfolio-manager
last_reviewed: 2026-07-19
covers_version: ""
supersedes:
  - docs/enterprise-strategy/vol8-portfolio-consulting-frameworks.md
tags:
  - portfolio-management
  - investment
  - frameworks
sources: []
pagination_next: strategy/vols/vol8-portfolio-consulting-frameworks-pmo-evolution-strategy-frameworks
---

# Portfolio Consulting Frameworks: Portfolio Management

Why this matters: Portfolio management translates strategy into investment decisions. Frameworks for prioritization, benefits realization, and capital planning drive where work actually happens.

## Portfolio Hierarchy

Enterprise work exists in a hierarchy—from most strategic to most tactical.

| Level | Definition | Time Horizon | Owner |
|-------|-----------|--------------|-------|
| **Portfolio** | Collection of programs/projects aligned to strategy | 1-5 years | CPO, CDO |
| **Program** | Group of related projects with coordinated benefits | 1-3 years | Programme Director |
| **Project** | Temporary endeavour with defined start, end, deliverable | 3-18 months | Project Manager |
| **Epic** | Large body of user work representing a business outcome | 1-6 months | Product Owner |
| **Feature** | User-facing capability that delivers business value | 1-4 weeks | Product Owner |

## Investment Portfolio Models

**Gartner Run / Grow / Transform (RGT)**

```
RUN (60-70%): Keep the lights on; business operations; mandatory compliance
GROW (20-30%): Enhance existing capabilities; expand market share
TRANSFORM (10-15%): Disruptive change; new business models; emerging technology
```

**McKinsey Three Horizons**

| Horizon | Time Frame | Focus | Management Mode |
|---------|-----------|-------|----------------|
| **H1: Core** | 0-1 year | Protect and extend core business | Performance management |
| **H2: Emerging** | 1-3 years | Build emerging businesses | Growth management |
| **H3: Options** | 3-7 years | Seed real options for future | Exploration |

**AI Across Three Horizons:**
- H1: AI in core operations (fraud detection, claims processing, demand forecasting)
- H2: AI products (AI-powered customer service, copilots, AI-native workflows)
- H3: AI business model transformation (AI agents replacing headcount, AI-driven pricing)

## AI Investment Portfolio Design

**AI Investment Tiers:**

| Tier | Description | Investment Characteristics |
|------|-------------|---------------------------|
| **Foundation** | AI platform, data infrastructure, talent | High CapEx; long payback; enables all other tiers |
| **Differentiation** | AI capabilities improving existing products | Moderate investment; 6-18 month payback |
| **Disruption** | AI-native business model innovations | High risk; long horizon; asymmetric upside |

**Target Allocation (Mature Enterprise):**
- Foundation (30-40%): AI platform, data governance, MLOps, talent
- Differentiation (45-55%): AI use cases in core business
- Disruption (10-15%): AI-native business model experiments

## Portfolio Prioritization Frameworks

**WSJF (Weighted Shortest Job First — SAFe)**

```
WSJF = Cost of Delay / Job Duration

Cost of Delay = User-Business Value + Time Criticality + Risk Reduction
```

**ICE Score**

```
ICE = Impact × Confidence × Ease
```

**RICE Score (Intercom)**

```
RICE = (Reach × Impact × Confidence) / Effort
```

**KANO Model** — Classifies features by effect on customer satisfaction:
- Must-Be (Basic): Expected; absence dissatisfies
- Performance: More = better; linear satisfaction
- Attractive (Delighter): Unexpected; presence delights

## Benefits Realization Management

**Output-Outcome-Impact Hierarchy:**

```
OUTPUT → "We deployed an AI chatbot"
OUTCOME → "Customer service handle time reduced 35%"
IMPACT → "Customer satisfaction +8 points; $12M annual cost saving"
```

**Common Benefits Categories:**

| Category | Example Metric |
|----------|---------------|
| **Cost reduction** | FTE hours saved, headcount avoided |
| **Revenue growth** | Conversion rate uplift, new products |
| **Risk reduction** | Fraud loss reduced, error rate reduced |
| **Speed** | Process cycle time reduction |
| **Quality** | Error rate, rework rate, NPS |

## Capital Planning for AI

**OpEx vs. CapEx:**

| Cost Type | OpEx | CapEx |
|-----------|------|-------|
| Cloud AI API calls | Yes | No |
| SaaS AI platform subscriptions | Yes | No |
| Custom AI model development | Depends | May qualify |
| AI platform build (internal) | No | Yes |

---

## Related

- [Portfolio Consulting Frameworks: PMO Evolution & Strategy](vols/08-vol8-portfolio-consulting-frameworks-pmo-evolution-strategy-frameworks.md)
- [Portfolio Consulting Frameworks: Architecture & Operating Delivery](vols/09-vol8-portfolio-consulting-frameworks-architecture-operating-delivery.md)
---

*Volume 8 of 10 — Part 1 of 4*
