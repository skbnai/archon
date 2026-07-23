---
title: "A.R.T. — Agility · Risk · Tenacity: Enterprise Execution Framework for Agentic AI"
doc_type: reference-architecture
domain: architecture
status: current
canonical: true
topic_id: art-framework-agentic-ai-execution
maturity: expert
personas: [architect, executive-leadership, platform-engineer]
last_reviewed: 2026-07-19
covers_version: "as of July 2026"
supersedes:
  - docs/enterprise-architecture/ai-architecture/ART-Framework-Agentic-AI-Execution.md
tags:
  - art-framework
  - enterprise-ai
  - agility
  - risk
  - tenacity
  - maturity-model
  - agentic-ai
  - execution-framework
  - governance
sources: []
---

# A.R.T. — Agility · Risk · Tenacity

## Enterprise Execution Framework for Agentic AI Systems

Between 80% and 95% of enterprise AI initiatives fail to deliver measurable business value. MIT reported in 2025 that 95% of generative AI pilots show no measurable P&L return. For every 33 proofs of concept an enterprise starts, only four reach production. The average sunk cost per abandoned AI initiative is $7.2 million.

This guide covers a validated execution methodology for planning, building, deploying, operating, governing, and continuously improving Agentic AI systems in enterprise environments. A.R.T. (Agility · Risk · Tenacity) addresses the three documented failure clusters: inability to adapt, inability to govern risk, and inability to sustain. The framework includes research foundations, lifecycle model, maturity model, KPIs, organizational model, and critical evaluation against established frameworks like SAFe, TOGAF, NIST AI RMF, and DORA.

---

## Mermaid Diagram: A.R.T. Execution Lifecycle

```mermaid
graph LR
    A[VISION] -->|Agility-dominant| B[STRATEGY]
    B -->|Agility + Risk| C[PORTFOLIO]
    C -->|Risk-dominant| D[ARCHITECTURE]
    D -->|Agility + Risk| E[BUILD]
    E -->|Risk + Tenacity| F[DEPLOY]
    F -->|Tenacity-dominant| G[OPERATE]
    G -->|Tenacity + Agility| H[IMPROVE]
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#fff9c4
    style F fill:#ffe0b2
    style G fill:#ffccbc
    style H fill:#e1f5ff
```

---

## Executive Summary

These failures are organizational, not technical. The research identifies three recurring root-cause clusters:

| Failure Cluster | Root Causes |
|----------------|-------------|
| **Cannot adapt** | Technology-first thinking, unclear success criteria, no product thinking, rigid delivery processes |
| **Cannot govern risk** | Fading executive sponsorship, poor data foundations, compliance gaps, uncontrolled agent behavior |
| **Cannot sustain** | No operational discipline, no ownership, no feedback loops, initiatives abandoned when novelty fades |

**A.R.T.** addresses each cluster directly:

- **Agility** — the organizational capability to adapt, experiment, and deliver AI value incrementally
- **Risk** — the governance discipline to identify, measure, control, and learn from AI-related risks
- **Tenacity** — the operational discipline to sustain AI systems in production and improve them continuously

A.R.T. is not a replacement for TOGAF, SAFe, ITIL, or NIST AI RMF. It is a unifying **execution layer** that sits above these frameworks and provides the connective tissue for delivering Agentic AI at enterprise scale.

---

## Part 1: Research Validation of the Three Pillars

### Pillar 1: Agility

**Evidence for the gap:**
- Organizations that redesign workflows around AI achieve 2.1× more ROI than those that just deploy tools (Gartner 2026)
- Only 16.2% of organizations achieve on-demand deployment; 23.9% deploy less than once per month (DORA 2025)
- AI coding assistants improve individual output 21–98%, but organizational delivery metrics stay flat — indicating the workflow, not the tool, is the limiting factor

**What Agility means for Agentic AI:**

| Dimension | What It Means for Agentic AI |
|-----------|------------------------------|
| **Product thinking** | AI initiatives framed as products with owners, roadmaps, and user metrics — not projects with end dates |
| **Experiment velocity** | Rapid iteration on agent prompts, tools, memory architectures, and evaluation criteria |
| **Continuous delivery** | Agent updates deployed safely via CI/CD with automated evaluation gates |
| **Organizational learning** | Feedback from production incidents feeds into the next iteration within days, not quarters |
| **Platform thinking** | Internal developer platforms for AI that reduce the cognitive load on product teams |

**KPIs for Agility:**

| KPI | Target (Elite) |
|----|---------------|
| Time to first working agent prototype | &lt;2 weeks |
| Deployment frequency | Weekly or more |
| Lead time for changes | &lt;1 day |
| Change failure rate | &lt;5% |
| Experiment velocity | ≥4 agent experiments/sprint |
| Time to production (pilot → scale) | &lt;90 days |

### Pillar 2: Risk

**Evidence for the gap:**
- 84% of companies have not redesigned roles around AI; only 21% have a mature AI-agent governance model (Deloitte 2026)
- 59% of organizations do not know how quickly they could halt an AI system during a security incident (ISACA 2026)
- Gartner predicts 40%+ of agentic AI projects will be canceled by end of 2027 due to governance and ROI failures
- OWASP Agentic Top 10 (December 2025) identifies 10 categories of agent-specific security risk not covered by traditional controls

**What Risk means for Agentic AI:**

| Risk Category | Description |
|--------------|-------------|
| **Model risk** | Hallucination, confabulation, behavioral drift, evaluation gaming |
| **Agent runtime risk** | Prompt injection, goal hijack, memory poisoning, tool misuse (OWASP ASI01–ASI10) |
| **Operational risk** | Cascading failures, blast radius propagation across multi-agent systems |
| **Compliance risk** | EU AI Act, NIST AI RMF, ISO 42001 obligations not met |
| **Data governance risk** | PII/PHI leakage through agent tool calls; cross-border data residency violations |
| **Organizational risk** | Shadow AI, unauthorized agent deployment, no ownership |
| **Vendor risk** | Dependency on third-party model providers; model changes breaking production agents |

**KPIs for Risk:**

| KPI | Target |
|----|--------|
| AIDR-detected incidents per 1,000 agent sessions | &lt;5 |
| Policy violation rate | &lt;0.5% of tool calls |
| Hallucination rate (evaluated) | &lt;2% on production tasks |
| Compliance audit pass rate | 100% for high-risk systems |
| AI security incidents per quarter | 0 critical; &lt;3 medium |
| Shadow AI discovery score | 100% of AI tools inventoried |
| Mean Time to Contain an agent incident | &lt;30 minutes |

### Pillar 3: Tenacity

**Evidence for the gap:**
- 55% of companies cite lack of MLOps practices as a major obstacle to AI deployment (Zarour et al., 2025)
- 89% of CIOs rank agent-based AI as a top strategic priority, but the vast majority of teams have no systematic way to understand why agents fail, what they cost per session, or whether they stay within scope (AgentOps research, 2026)
- 42% of companies abandoned most AI initiatives in 2025, up from 17% the year before — demonstrating the execution endurance problem

**What Tenacity means for Agentic AI:**

| Dimension | What It Means |
|-----------|--------------|
| **AgentOps maturity** | Systematic monitoring, tracing, cost tracking, failure analysis for every production agent |
| **Continuous evaluation** | Automated evals on every deployment; regression detection; human review of edge cases |
| **SRE practices for agents** | SLOs, error budgets, circuit breakers, runbooks, on-call rotations |
| **Kaizen culture** | Regular retrospectives on agent performance data; iterative improvement cycles |
| **Cost discipline** | Token budget management, model tiering, caching strategies |
| **Organizational resilience** | AI programs survive leadership changes, budget cycles, and technology shifts |

**KPIs for Tenacity:**

| KPI | Target |
|----|--------|
| Agent task success rate | &gt;90% (domain-dependent) |
| MTTR (Mean Time to Recover) | &lt;15 minutes for P1 agent failures |
| Agent uptime | &gt;99.5% for critical workflows |
| Cost per agent session | Tracked, trending down QoQ |
| User adoption rate | &gt;70% of target users actively using |
| Continuous improvement rate | ≥2 measured improvements per agent per sprint |
| Business value delivered (ROI) | Positive within 6 months of production |

---

## Part 2: Five-Level A.R.T. Maturity Model

### Overview

| Level | Name | Description |
|-------|------|-------------|
| **L1** | Experimental | Ad-hoc AI exploration; no systematic execution |
| **L2** | Managed | Individual AI projects with some structure; governance reactive |
| **L3** | Standardized | Repeatable processes; proactive risk management; basic operations |
| **L4** | Optimized | Continuous improvement culture; advanced observability; enterprise-wide AI platform |
| **L5** | Autonomous Enterprise | AI-native; self-improving systems; governance by design; AI-augmented AI operations |

The maturity assessment scorecard rates each dimension 1–5 per pillar, summing to determine organizational readiness for production deployment.

---

## Trade-Offs: When to Use A.R.T. vs. Alternatives

### A.R.T. vs. SAFe

| Dimension | A.R.T. | SAFe |
|-----------|--------|------|
| **Scope** | Agentic AI execution layer | Enterprise software delivery framework |
| **Primary value** | AI-specific failure modes, KPIs, operational patterns | Agile scaling across teams |
| **Risk focus** | Model behavior, hallucination, autonomy | Feature delivery, dependency management |
| **When to choose A.R.T.** | Building agentic AI products; model-specific risks dominate | Choose SAFe for the outer portfolio framework; use A.R.T. as the AI execution layer within SAFe trains |

### A.R.T. vs. NIST AI RMF

| Dimension | A.R.T. | NIST AI RMF |
|-----------|--------|------------|
| **Scope** | Execution lifecycle, team operating model, KPIs | Risk management framework for AI systems |
| **Primary value** | Operational playbook, maturity roadmap, team structure | Governance architecture, compliance evidence |
| **Typical adoption** | Engineering + product teams | CRO, compliance, risk management |
| **When to choose A.R.T.** | Operational execution; "how do we run this?" | Choose both: NIST for risk taxonomy, A.R.T. for execution implementation |

### A.R.T. vs. LLMOps / MLOps

| Dimension | A.R.T. | LLMOps / MLOps |
|-----------|--------|---------|
| **Scope** | Three-pillar execution framework | Model operations (training, evaluation, deployment) |
| **Primary value** | Agility, risk governance, organizational tenacity | Model lifecycle management |
| **When to choose A.R.T.** | End-to-end agentic AI delivery | Choose both: LLMOps for model layer, A.R.T. for agent/product layer |

---

## Key Takeaways

1. **Three-pillar framework** addresses the three documented failure clusters at enterprise scale
2. **Maturity model** provides a roadmap from experimental (L1) through autonomous enterprise (L5)
3. **KPI framework** measures success across execution, not just infrastructure uptime
4. **Organizational model** defines roles, accountability, and governance structures
5. **Compatibility with existing frameworks**: A.R.T. fills the gap between strategic frameworks (TOGAF, SAFe) and operational frameworks (ITIL, DORA)

---

## Related

- [Agentic AI Reliability, Observability & Governance](43-agentic-ai-reliability-observability-governance.md)
- [Agent Reliability Engineering](42-agent-reliability-engineering.md)
- [Enterprise AI Architecture Patterns](49-enterprise-ai-architecture-patterns.md)
- [AI Harness Architecture & Orchestration](pathname:///archon/architecture/ai-harness-architecture-orchestration)
- [Enterprise AI Governance & Compliance](51-enterprise-ai-governance-compliance.md)

---

## Sources

- MIT Report: 95% of GenAI Pilots Failing (Fortune, Aug 2025)
- DORA 2025: AI Impact on Dev Metrics (Faros.ai)
- AI-Native SAFe 2026 Release (Scaled Agile)
- NIST AI RMF (https://www.nist.gov/itl/ai-risk-management-framework)
- OWASP Top 10 for Agentic Applications 2026 (https://genai.owasp.org)
- Accelerate: Building and Scaling High Performing Technology Organizations (Forsgren, Humble, Kim)
- SRE Books (https://sre.google)
