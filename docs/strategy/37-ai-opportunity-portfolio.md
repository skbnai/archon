---
title: "AI Opportunity Portfolio & Prioritization"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ai-opportunity-portfolio
maturity: expert
personas: ["Chief Strategy Officers", "Portfolio Managers", "AI Product Managers", "CFOs"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: ["docs/enterprise-architecture/transformation/02_AI_Opportunity_Portfolio.md"]
tags: ["enterprise-ai", "portfolio", "opportunity-assessment", "prioritization", "lighthouse-use-cases"]
sources: []
---

Value lives in specific capabilities, not everywhere. The portfolio method prioritizes opportunities based on impact, complexity, required data, technique, and expected ROI horizon. Discipline: benefits count only when audited by Finance against a pre-registered baseline. Every funded opportunity must consume the shared platform, making each use case cheaper than the last.

## Portfolio Method: Value Cases, Not Use Cases

Each opportunity is assessed on:
- Business value and impact
- Complexity and technical feasibility
- Required data and AI technique
- Expected ROI horizon (time from build start to audited net benefit)
- Principal risks and mitigations

Two disciplines matter most: (1) **benefits audited by Finance,** not self-reported, and (2) **every use case consumes the shared platform,** creating a compounding platform advantage.

---

## Opportunity Inventory Across 16 Business Functions

| Function / Opportunity | Value Driver | Value | Complexity | Technique | ROI Horizon |
|---|---|---|---|---|---|
| **Customer service — AI resolution & copilot** | 40-70% faster handling; 30-60% autonomous deflection | VH | M | RAG + tool agents | 6-12 mo |
| **Software engineering — AI-assisted SDLC** | 20-40% cycle-time gain; higher review coverage | VH | L-M | Code assistants + agentic PR review | 3-9 mo |
| **Sales — intelligence & proposal automation** | 5-12% win-rate lift; 30-50% less admin per rep | H | M | RAG + generation + scoring | 6-12 mo |
| **Marketing — content ops & personalization** | 3-8x content throughput; segment-of-one campaigns | H | M | Generation + brand-tuned eval | 3-9 mo |
| **Finance — close automation & FP&A copilot** | 30-50% faster close tasks; narrative reporting on demand | H | M-H | Agents + structured retrieval | 9-18 mo |
| **Finance — AP/AR & contract-to-invoice** | Touchless invoice rate to 70-85% | M-H | M | Document AI + rules + LLM exception handling | 6-12 mo |
| **HR — talent acquisition & internal mobility** | 30-50% faster screening; better internal matching | M-H | M | Matching + generation; strict human decision rights | 9-18 mo |
| **Legal — contract review & clause intelligence** | 50-70% faster first-pass review | M-H | M | RAG + extraction + redline | 6-12 mo |
| **Procurement — spend intelligence & sourcing** | 2-5% addressable-spend savings | M-H | M | Classification + negotiation agents | 9-18 mo |
| **Supply chain — demand sensing & disruption watch** | 10-20% forecast-error reduction | H | H | ML forecasting + LLM signal fusion | 12-24 mo |
| **Manufacturing/ops — quality & maintenance** | 15-30% unplanned-downtime reduction | H | H | Predictive ML + technician copilot | 12-24 mo |
| **IT ops — AIOps & self-service** | 40-60% L1 ticket deflection; faster MTTR | H | M | RAG + remediation agents (guarded) | 6-12 mo |
| **Cybersecurity — triage & detection engineering** | 50-70% faster alert triage | H | M | LLM triage + enrichment agents | 6-12 mo |
| **Knowledge management — enterprise brain** | Foundational multiplier for all other cases | VH (enabling) | M-H | Ingestion + RAG + permissions-aware search | 6-12 mo |
| **Risk & compliance — monitoring & reg-change** | 60-80% faster regulatory impact analysis | M-H | M | RAG + classification + workflow | 9-18 mo |
| **Executive decision support — enterprise copilot** | Faster, evidence-linked decisions | H | H | Text-to-analytics + narrative synthesis | 18-30 mo |

**Legend:** VH = very high value; H = high; M = medium; L = low. ROI horizon = time from build start to audited net benefit.

---

## Five Lighthouse Deep-Dive Cards

### Lighthouse 1: Customer Service AI (Copilot First, Autonomy Second)

- **Approach:** Phase A: agent-assist copilot (suggested answers, auto-summarization, next-best-action). Phase B: autonomous resolution for top 10-20 routine intents with confidence thresholds and instant escalation.
- **Expected ROI:** Cost-to-serve down 25-40% in covered intents by month 18; CSAT neutral-to-positive as a hard gate.
- **Key risks:** Hallucinated policy answers (mitigate: retrieval-grounded with citation checks); agent morale (position as augmentation, involve agents in design).
- **Why first:** Rich data, measurable baseline, high visibility, forces the knowledge platform to be built properly.

### Lighthouse 2: AI-Assisted Software Engineering

- **Approach:** Governed coding assistants for all engineers; agentic code review and test generation in CI; migration agents for legacy remediation in Horizon 2.
- **Expected ROI:** 15-30% throughput gain measured by cycle time and change failure rate — never by lines of code.
- **Key risks:** Insecure generated code (mitigate: security scanning in CI, provenance tagging); license contamination (mitigate: policy + tooling).
- **Why first:** Fastest time-to-value in the portfolio and builds the internal skill base the platform team needs.

### Lighthouse 3: Enterprise Knowledge Platform

- **Approach:** Permissions-aware ingestion of documents, wikis, tickets, call transcripts into a governed retrieval layer; exposed as a service to every other use case.
- **Expected ROI:** Indirect but foundational: measured via search success rate, time-to-answer, reuse by downstream use cases.
- **Key risks:** Over-permissive retrieval leaking sensitive content (mitigate: document-level ACL enforcement at query time).
- **Why first:** Every ambitious use case dies without it; building it once prevents 20 teams building it badly.

### Lighthouse 4: Finance Close & FP&A Copilot

- **Approach:** Reconciliation and flux-analysis agents with deterministic validation; narrative reporting drafted by AI, approved by controllers.
- **Expected ROI:** 2-4 days off monthly close tasks; analyst capacity shifted from assembly to analysis.
- **Key risks:** Errors in financial reporting (mitigate: AI drafts, humans certify; full audit trail; SOX-aligned controls).
- **Why first:** Creates credible, CFO-sponsored proof that AI works under control-heavy conditions — unlocking governance trust.

### Lighthouse 5: IT Ops & Security Triage

- **Approach:** RAG over runbooks and ticket history for L1 deflection; alert-triage agents that enrich and prioritize but don't auto-remediate in Phase A.
- **Expected ROI:** 40-60% L1 deflection; 30-50% triage-time reduction in SOC.
- **Key risks:** Automated actions causing outages (mitigate: read-only Phase A; graduated autonomy).
- **Why first:** IT is a willing early adopter and telemetry to measure impact already exists.

---

## Impact vs. Effort Prioritization Matrix

| Quadrant | Opportunities | Decision rule |
|---|---|---|
| **Quick wins** (high impact, low-med effort) | SW engineering assist, customer-service copilot, marketing content ops, IT/SOC triage | Fund now; production within 2-3 quarters |
| **Strategic bets** (high impact, high effort) | Knowledge platform, finance close, supply chain sensing, autonomous service resolution | Fund now with staged gates; 12-24 month value horizon |
| **Fill-ins** (moderate impact, low effort) | Meeting/document summarization, HR policy assistant, sales-call summaries | Deliver via platform self-service, minimal central investment |
| **Deprioritize** (low impact or unready) | Executive enterprise copilot (until semantic layer exists), fully autonomous HR decisions (regulatory), moonshot product bets without data | Revisit at 12-month portfolio review |

**Sequencing logic:** Quick wins fund credibility, strategic bets build the moat, platform mandate ensures the two share infrastructure. Portfolio rebalanced quarterly by the AI Portfolio Board with explicit kill criteria — a pilot that cannot show a path to audited value within two quarters is stopped.

---

## Related

- [Executive Summary & AI Vision](35-executive-summary-and-ai-vision.md)
- [Enterprise AI Platform, Data & Agentic Architecture](38-enterprise-ai-platform-and-data-architecture.md)
- [Roadmap, Financials, KPIs & Risk](41-roadmap-financials-kpis-and-risk.md)

## Sources

*Value pools and benchmarks derived from Gartner CIO Survey (2026), Forrester AI adoption studies, and client engagement portfolio analysis.*
