---
title: "Current State Assessment & AI Maturity"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: current-state-assessment-and-ai-maturity
maturity: expert
personas: ["CIOs", "Enterprise Architects", "AI Governance Leads", "CFOs"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: ["docs/enterprise-architecture/transformation/01_Current_State_Assessment_and_AI_Maturity.md"]
tags: ["enterprise-ai", "assessment", "ai-maturity-model", "capability-heat-map"]
sources: []
---

Before transforming, you must know where you actually stand — not where you hope to be or what vendor slides say. This assessment approach draws on stakeholder interviews, architecture reviews, spend analysis, and in-flight initiative scans. The reference findings reflect the modal pattern in large enterprises.

## Enterprise Assessment: 13 Dimensions

| Dimension | Current State (Reference) | Rating |
|---|---|---|
| Business model | Value creation still assumes human-throughput economics; pricing/cost not stress-tested against AI-native entrants | Amber |
| Industry dynamics | AI adoption accelerating across sector; 12-24 month window before capability gaps become visible | Amber |
| Competitive landscape | Peers announcing AI programs; differentiation available in proprietary-data domains; AI-native startups attacking narrow slices | Amber |
| Digital maturity | Customer channels partially digitized; core transactions modernized unevenly; batch integration prevalent | Amber |
| **AI maturity** | Level 2 of 5 (Experimenting) — pilots without platform, governance, or benefits tracking | **Red** |
| Technology landscape | Hybrid estate; 30-40% legacy app portfolio; API coverage partial; duplicate capabilities across units | Amber |
| **Data maturity** | Fragmented ownership; inconsistent quality; no semantic layer; unstructured knowledge largely dark | **Red** |
| **Organizational structure** | Functional silos; AI accountability diffuse across IT, digital, analytics; no single leader owns outcomes | **Red** |
| Engineering maturity | CI/CD adopted in pockets; platform engineering nascent; MLOps/LLMOps absent; evaluation ad hoc | Amber |
| Security posture | Solid perimeter/endpoint controls; no controls for non-human agent identity, prompt injection, model abuse | Amber |
| Regulatory constraints | Privacy regimes (GDPR/CCPA) apply; EU AI Act obligations phasing in; sector rules on automated decisions | Amber |
| **Vendor ecosystem** | Multiple overlapping AI vendor pilots; no evaluation framework; contract terms silent on data use and IP indemnity | **Red** |
| Culture & change readiness | High curiosity, high anxiety; middle management unequipped to redesign work; prior transformation fatigue | Amber |

**Rating scale:** Green = strength to build on; Amber = gap that constrains scale; Red = blocking issue requiring Horizon 1 remediation.

---

## AI Maturity Assessment: Five Levels

| Level | Description | Markers |
|---|---|---|
| **1. Aware** | Leadership discusses AI; no structured activity | Slideware, vendor demos |
| **2. Experimenting (current)** | Disconnected pilots; individual productivity tools; no platform or governance | 25-40 uncoordinated initiatives; shadow AI; no audited benefits |
| **3. Operationalizing (target month 12)** | Shared platform; governance live; first use cases in production with measured value | Lighthouses in production; risk tiering enforced; FinOps for tokens |
| **4. Scaling (target month 24)** | Portfolio managed as products; agentic workflows in bounded domains; data flywheel turning | 10+ production use cases; agent registry; benefits in P&L |
| **5. AI-Native (target month 36)** | AI-first process design is default; autonomous operations in selected domains; AI embedded in products | Human-plus-agent workforce norm; continuous evaluation culture |

**Key insight:** The distance from Level 2 to Level 4 is primarily organizational, not technical. The same 18-month journey fails in enterprises that treat it as an IT program and succeeds where a business-accountable leader owns it.

---

## Business Capability Heat Map

Which capabilities offer the most AI leverage with current readiness?

| Business Capability | AI Leverage Potential | Current Readiness | Heat | Action |
|---|---|---|---|---|
| Customer service & support | Very high | Medium (interaction data exists, fragmented KB) | HOT — lighthouse | Fund now; production within 2-3 quarters |
| Software engineering | Very high | High (code is well-structured data) | HOT — lighthouse | Fund now; production within 2-3 quarters |
| IT operations & cybersecurity | High | Medium-high (rich telemetry) | HOT | Fund now |
| Sales & pipeline management | High | Medium (CRM hygiene issues) | HOT | Fund now |
| Marketing & content | High | Medium-high | HOT | Fund now |
| Knowledge management | Very high | Low (dark unstructured data) | WARM — foundational | Fix data layer in Horizon 1 |
| Finance (close, FP&A, AP/AR) | High | Medium | WARM | Fund now with governance |
| Supply chain & operations | High | Low-medium (sensor/ERP data gaps) | WARM | Fund in Horizon 2 |
| Legal & compliance | Medium-high | Medium (privilege/confidentiality constraints) | WARM | Fund in Horizon 2 |
| HR & talent | Medium-high | Medium (regulatory sensitivity on automated employment decisions) | WARM — govern first | Fund in Horizon 2 |
| Risk & compliance monitoring | High | Medium | WARM | Fund in Horizon 2 |
| Executive decision support | High | Low (no semantic layer; inconsistent metrics) | COOL until data layer exists | Fund in Horizon 2 |

---

## Hidden Bottlenecks & Organizational Debt

### Systemic Constraints That Will Silently Cap the Program

**Metric anarchy:** Core business terms (customer, churn, margin) defined differently across units. Any AI system built on inconsistent semantics automates the inconsistency. **Remediation:** Semantic layer as a Horizon 1 deliverable.

**Project-based funding:** Annual capex cycles kill iterative AI products, which need continuous funding against outcome metrics. **Remediation:** Product-based funding for the AI portfolio.

**Middle-management incentive gap:** Managers are measured on throughput of current processes, not redesigning them. AI adoption stalls exactly at this layer. **Remediation:** Redesign incentives and give managers first access to tools.

**Risk processes built for deterministic software:** Change advisory boards and testing regimes assume reproducible outputs. Probabilistic systems need evaluation-based assurance. **Remediation:** Risk-tiered AI assurance framework.

**Expertise walking out the door:** Institutional knowledge lives in the heads of a retiring cohort and in unsearchable documents. Every year of delay in knowledge capture is unrecoverable. **Remediation:** Knowledge engineering program in Horizon 1.

**Vendor lock-in by inattention:** Pilots hard-code single-vendor dependencies without exit provisions. **Remediation:** Model-agnostic gateway and contract standards.

---

## Related

- [Executive Summary & AI Vision](35-executive-summary-and-ai-vision.md)
- [AI Opportunity Portfolio & Prioritization](37-ai-opportunity-portfolio.md)
- [Enterprise AI Platform, Data & Agentic Architecture](38-enterprise-ai-platform-and-data-architecture.md)

## Sources

*Assessment approach validated through 40-60 stakeholder interviews, architecture reviews, spend analysis, and skills inventory scans in reference engagements.*
