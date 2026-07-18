---
title: "Part 17 — AI Transformation Roadmap & Maturity Model"
doc_type: guide
domain: strategy
topic_id: part-17-transformation-roadmap
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "cto", "caio"]
supersedes: ["docs/enterprise-ai-report/part-17-transformation-roadmap.md"]
tags: ["transformation-roadmap", "maturity-model", "ai-first", "ai-native", "implementation-roadmap", "30-60-90-day"]
sources: []
---

# Part 17 — AI Transformation Roadmap & Maturity Model

Enterprise AI maturity progresses through six distinct levels. This guide provides the maturity model, phased roadmap, and 30/60/90-day playbook for new Chief AI Officers.

## AI Maturity Model

### Five-Level Model

| Level | Name | Characteristics |
|-------|------|-----------------|
| **1** | Exploring | Ad-hoc pilots; no enterprise AI strategy; shadow AI rife; no governance |
| **2** | Experimenting | Structured pilots; AI CoE forming; governance being defined; ROI uncertain |
| **3** | Scaling | Production AI systems; established governance; measurable ROI; AI platform forming |
| **4** | Optimising | AI embedded in core processes; feedback loops; agentic AI emerging; AI factory |
| **5** | AI-First | AI is the operating fabric; autonomous agents at scale; constitutional governance |
| **6** | AI-Native | AI IS the organisation's operating model; sovereign infrastructure; proprietary models |

*Approximate enterprise distribution 2026: L1 (~15%), L2 (~35%), L3 (~30%), L4 (~15%), L5 (~4%), L6 (<1%)*

### Maturity Assessment Dimensions

| Dimension | L1 | L2 | L3 | L4 | L5 |
|-----------|----|----|----|----|-----|
| **Strategy** | None | Emerging | Defined | Embedded | Competitive differentiator |
| **Capabilities** | PoCs only | 1–5 in production | 10–50 in production | 50–200 in production | 200+ agents/features |
| **Process** | Ad hoc | AI-specific gates | AIDLC adopted | ADLC + factory | Continuous improvement |
| **Organisation** | No AI roles | AI CoE started | Hub & Spoke | Domain teams + platform | AI-native workforce |
| **Technology** | Direct API access | Managed LLM access | AI platform (L3) | AI platform (L4–5) | Sovereign AI infrastructure |
| **Governance** | None | Policy drafted | Governance active | Automated governance | Constitutional governance |
| **Investment** | <£500K | £500K–£5M | £5M–£50M | £50M–£200M | £200M+ |
| **KPIs** | N/A | Activity KPIs | Output KPIs | Outcome KPIs | Enterprise value KPIs |

## Transformation Roadmap

### Phase 0: Foundation (Months 0–3)

**Goal:** Establish the prerequisites for sustainable AI transformation.

| Action | Owner | Output |
|--------|-------|--------|
| Appoint CAIO (or interim AI Lead) | CEO | CAIO in post |
| Conduct AI maturity assessment | CAIO + External Advisor | Current state report |
| Define enterprise AI principles (6–8) | CAIO + Legal + Ethics | AI principles document |
| Identify first 3 high-value AI use cases | CAIO + Business Leaders | Use case shortlist |
| Establish AI governance framework basics | CAIO + CRO + Legal | AI governance charter |
| Set up AI budget (initial allocation) | CFO + CAIO | AI budget approved |

### Phase 1: Prove It (Months 1–6, L1 → L2)

**Goal:** Demonstrate AI value with 2–3 production use cases; build credibility.

**Operating Model:** Small centralised AI team (5–10 people) + 1–2 business unit champions.

**Technology:** Direct LLM API access; basic prompt engineering; off-the-shelf RAG.

**Key milestones:**
- 2 GenAI features in production, with measurable business metrics
- AI governance policy published and acknowledged by all AI participants
- AI cost dashboard live (basic visibility)
- First AI all-hands: share learnings, invite contribution

**Investment:** £500K–£2M (talent + API costs + tooling)

### Phase 2: Scale It (Months 6–18, L2 → L3)

**Goal:** Scale AI delivery beyond the CoE into business units; establish the AI platform.

**Operating Model:** Hub & Spoke — central AI platform team + BU-embedded AI engineers.

**Technology:** Internal AI platform (L3): inference service, embedding service, guardrails, basic RAG.

**Key milestones:**
- AI platform live with 3+ consuming teams
- 10+ AI use cases in production across 3+ business units
- AI delivery lifecycle (AIDLC) adopted
- Prompt governance and model registry operational
- First AI governance board meeting
- AI talent programme: 50+ employees trained in AI fundamentals

**Investment:** £5M–£15M (platform build + talent + expanded API usage)

### Phase 3: Embed It (Months 12–24, L3 → L4)

**Goal:** Embed AI into core business processes; launch the Agent Factory.

**Operating Model:** Hub & Spoke + Agent Factory. Business domain teams with genuine AI capability.

**Technology:** AI platform (L4–5): full service catalog, agent runtime, self-service developer portal.

**Key milestones:**
- 50+ AI use cases in production
- First autonomous agents in production (low-to-medium risk class)
- Agent Factory operational with first 5 agents delivered
- AI FinOps operational with chargeback to BUs
- AI observability dashboard live (quality, cost, business metrics)
- External AI audit completed (ISO 42001 or equivalent)

**Investment:** £15M–£50M

### Phase 4: Optimise It (Months 24–36, L4 → L5)

**Goal:** AI as a competitive differentiator; digital workforce at scale.

**Operating Model:** Digital Workforce + AI Shared Services. AI is embedded in every function.

**Technology:** Full AI platform; agentic AI at scale; exploring sovereign AI infrastructure.

**Key milestones:**
- 200+ AI use cases and agents in production
- Digital workforce managing >30% of high-volume process tasks
- AI-native product features in core customer products
- AI FinOps saving >20% vs. unconstrained spend through optimisation
- Board-level AI KPI reporting dashboard
- Constitutional AI governance framework implemented for highest-risk AI

**Investment:** £50M–£200M

### Horizon 3: AI-Native (Year 3+, L5 → L6)

**Goal:** AI IS the operating model. Proprietary AI capability as competitive moat.

**Technology:** Sovereign AI infrastructure; proprietary fine-tuned models; constitutional AI.

**Investment:** £200M+

## 30 / 60 / 90 Day Playbook (For New CAIO)

### First 30 Days: Listen, Assess, and Win Quick

- **Week 1–2:** Stakeholder listening tour — CIO, CTO, CDO, CFO, business unit heads, CISO
- **Week 2–3:** AI inventory — what AI is already running? (sanctioned and shadow)
- **Week 3–4:** Quick win identification — one AI feature that can go live in 60 days
- **Deliverable:** 30-day report: current state, quick win, initial risk assessment

### Days 31–60: Build the Foundation

- Appoint the AI governance structure (even if lightweight at first)
- Publish AI acceptable use policy
- Stand up the AI team (CoE nucleus)
- Start the quick win delivery
- Select the first AI platform components (start with managed inference)
- **Deliverable:** AI governance charter; AI team in place; quick win in progress

### Days 61–90: Deliver and Communicate

- Launch the quick win (real production, real users, real metrics)
- Present AI strategy to leadership team for endorsement
- Begin business case for Year 1 AI investment
- Launch AI literacy programme for leadership team
- **Deliverable:** First AI in production; AI strategy deck; Year 1 business case draft

## KPI Framework by Maturity Level

| KPI Category | L1–L2 | L3 | L4 | L5 |
|-------------|-------|----|----|----|
| **Delivery** | PoCs completed | Use cases in production | Time-to-production, factory throughput | Agent fleet size, agent task volume |
| **Quality** | User satisfaction | Evaluation score | Hallucination rate | Quality SLA adherence |
| **Cost** | API spend tracked | Cost per use case | Cost per outcome | AI ROI enterprise-wide |
| **Adoption** | Team count using AI | % employees with AI tool access | AI-assisted process coverage | % processes AI-native |
| **Governance** | Policy published | Governance incident rate | Compliance rate | Constitutional policy coverage |
| **Value** | Qualitative benefits | £ productivity gain | £ cost avoided | £ enterprise AI value |

## Authoritative Guides

Comprehensive AI transformation guidance is available in the **Enterprise Architecture** domain. Consult specialised guides for:

- Maturity assessment instruments and scoring methodology
- 3-year roadmap, financials, KPIs, and risk register
- CTO-level transformation guidance
- Consulting delivery toolkits for AI transformation
- Real-world transformation case narratives

## Related

- [Part 2 — Operating Models](12-part-02-operating-models.md) — Operating models at each maturity level
- [Part 8 — Organizational Roles](18-part-08-organizational-roles.md) — Roles to build as maturity increases
- [Part 16 — Financial Model](26-part-16-financial-model.md) — Investment and ROI at each level
- [Part 18 — Case Studies](28-part-18-case-studies.md) — Real-world examples at different maturity levels

## Sources

[No external sources for this page.]
