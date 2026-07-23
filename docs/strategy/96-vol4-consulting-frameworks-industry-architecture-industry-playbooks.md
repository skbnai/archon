---
title: "Consulting Frameworks: Architecture & Industry Playbooks"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol4-consulting-frameworks-industry-part3
maturity: expert
personas: [Chief Architect, Chief Strategy Officer]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - togaf
  - bizbok
  - zachman
  - industry-strategy
  - banking
  - healthcare
sources: []
pagination_prev: strategy/vol4-consulting-frameworks-industry-strategy-execution-frameworks
pagination_next: strategy/vol4-consulting-frameworks-industry-framework-selection-glossary
---

# Consulting Frameworks: Architecture & Industry Playbooks

## TOGAF (The Open Group Architecture Framework)

**TOGAF** is the most widely adopted enterprise architecture framework globally, providing systematic architecture development and governance.

**TOGAF Architecture Development Method (ADM):**

```mermaid
graph TD
    PREL["PRELIMINARY<br/>Framework Setup"]
    AV["A: ARCHITECTURE<br/>VISION"]
    BA["B: BUSINESS<br/>ARCHITECTURE"]
    IA["C: INFORMATION<br/>ARCHITECTURE"]
    TA["D: TECHNOLOGY<br/>ARCHITECTURE"]
    OPS["E: OPPORTUNITIES &<br/>SOLUTIONS"]
    ACM["H: ARCHITECTURE<br/>CHANGE MGMT"]
    MP["F: MIGRATION<br/>PLANNING"]
    IG["G: IMPLEMENTATION<br/>GOVERNANCE"]
    RM["REQUIREMENTS MANAGEMENT<br/>Throughout all phases"]
    
    PREL --> AV
    AV --> BA
    BA --> IA
    IA --> TA
    TA --> OPS
    OPS --> ACM
    ACM --> MP
    MP --> IG
    RM -.-> PREL
    RM -.-> AV
    RM -.-> BA
    RM -.-> IA
    RM -.-> TA
```

TOGAF's eight-phase architecture development method with continuous requirements management.

**TOGAF Architecture Domains:**

| Domain | Covers | Artifacts |
|---|---|---|
| **Business Architecture** | Capabilities, value streams, organization | Capability map, value stream map |
| **Data Architecture** | Data entities, relationships, governance | Data model, data flow, dictionary |
| **Application Architecture** | Systems, integrations, APIs | Application portfolio, integration map |
| **Technology Architecture** | Infrastructure, platforms, cloud | Technology stack, network topology |

## Zachman Framework

The **Zachman Framework** (John Zachman, 1987) is a classification schema for organizing architecture artifacts by perspective (who, what, how, where, when, why) and stakeholder level.

## Industry Strategy Playbooks

### Banking & Financial Services 2026

**Strategic Context:** Embedded finance, AI-native challengers, open banking mandates, BNPL, crypto/DeFi, post-SVB regulatory tightening.

**Banking Strategy 2026 Playbook:**

```mermaid
graph TD
    DEF["DEFEND<br/>Protect Existing Revenue"]
    D1["Retention<br/>AI-powered churn prediction"]
    D2["Cost<br/>Process automation RPA→AI"]
    D3["Risk<br/>AI-enhanced fraud/AML"]
    
    GRW["GROW<br/>Expand Within Market"]
    G1["Digital<br/>Mobile-first, no-branch"]
    G2["SMB<br/>Embedded financial services"]
    G3["Wealth<br/>AI-powered accessible wealth"]
    
    TRN["TRANSFORM<br/>Build Future"]
    T1["BaaS<br/>API banking for embedding"]
    T2["AI-native Credit<br/>Explainable AI underwriting"]
    T3["Platform<br/>Financial ecosystem"]
    
    DEF --> D1 --> D2 --> D3
    GRW --> G1 --> G2 --> G3
    TRN --> T1 --> T2 --> T3
```

Three-pronged strategic approach: defend existing revenue, grow in current markets, and transform with new business models.

**Banking Capability Priorities:**

| Capability | Current | Target | Importance |
|---|---|---|---|
| Digital Onboarding | L2 | L5 | Critical |
| AI Credit Scoring | L1 | L4 | Critical |
| Real-time Payments | L3 | L5 | High |
| Open Banking API | L2 | L4 | High |
| AI Fraud Detection | L3 | L5 | Critical |
| Customer 360 Analytics | L2 | L4 | High |

### Healthcare 2026

**Strategic Context:** Payer-provider convergence, GLP-1 drugs, AI diagnostics, value-based care, staffing shortage, ambient AI.

**Healthcare Strategy 2026 Playbook:**

```mermaid
graph TD
    DEF["DEFEND<br/>Protect Quality & Safety"]
    D1["Quality<br/>AI clinical decision support"]
    D2["Safety<br/>Predictive early warning systems"]
    D3["Compliance<br/>AI governance for clinical AI"]
    
    GRW["GROW<br/>Expand Care Delivery"]
    G1["Virtual Care<br/>Hybrid in-person + telehealth"]
    G2["Preventive<br/>Chronic disease management"]
    G3["Partnerships<br/>Payer integration, value-based"]
    
    TRN["TRANSFORM<br/>AI-Enabled Care"]
    T1["AI-Augmented Care<br/>Ambient AI, diagnostic AI"]
    T2["Integrated Platform<br/>Unified patient journey"]
    T3["Data Monetization<br/>Anonymized research datasets"]
    
    DEF --> D1 --> D2 --> D3
    GRW --> G1 --> G2 --> G3
    TRN --> T1 --> T2 --> T3
```

Healthcare's three-pronged strategy: defend clinical quality, grow care delivery channels, and transform with AI.

**Healthcare AI Use Cases by ROI:**

| Use Case | Difficulty | ROI | Timeline |
|---|---|---|---|
| AI clinical documentation | Low | High | 0–6 months |
| Predictive readmission | Medium | High | 6–12 months |
| AI medical imaging | High | Very High | 12–24 months |
| Drug interaction detection | Medium | High | 6–12 months |
| Claims automation | Low | Medium | 3–6 months |
| Patient scheduling | Low | Medium | 3–6 months |

### Retail 2026

**Strategic Context:** Unified commerce, social commerce, q-commerce (15-min delivery), AI personalization, retail media, sustainability.

**Retail Capability Map (AI-Era):**

| Capability | Traditional | AI-Transformed |
|---|---|---|
| Demand Forecasting | Historical averages | AI + real-time signals |
| Pricing | Manual schedule | AI dynamic pricing |
| Inventory | Safety stock buffers | AI-optimized lean |
| Personalization | Segment-based | Individual-level AI |
| Customer Service | Call center | AI agent + human |
| Supply Chain | Reactive | AI predictive |

### Manufacturing 2026

**Strategic Context:** Industry 4.0/5.0, digital twin, reshoring, green manufacturing, labor automation, predictive maintenance.

**Smart Factory Roadmap:**

```mermaid
graph TD
    Y1["YEAR 1: CONNECT<br/>Foundation & Connectivity"]
    Y1A["IoT sensors on critical<br/>equipment"]
    Y1B["Data lake for<br/>operational data"]
    Y1C["Basic monitoring<br/>dashboards"]
    
    Y2["YEAR 2: ANALYZE<br/>Intelligence & Insight"]
    Y2A["Predictive maintenance AI"]
    Y2B["Quality vision AI"]
    Y2C["OEE optimization"]
    
    Y3["YEAR 3: AUTOMATE<br/>Autonomous Operations"]
    Y3A["AI production<br/>scheduling"]
    Y3B["Autonomous quality<br/>control"]
    Y3C["Digital twin<br/>simulation"]
    
    Y4["YEAR 4: OPTIMIZE<br/>Integrated Excellence"]
    Y4A["Supply chain AI<br/>integration"]
    Y4B["Energy optimization<br/>AI"]
    Y4C["Autonomous material<br/>handling"]
    
    Y1 --> Y1A --> Y1B --> Y1C
    Y1C --> Y2
    Y2 --> Y2A --> Y2B --> Y2C
    Y2C --> Y3
    Y3 --> Y3A --> Y3B --> Y3C
    Y3C --> Y4
    Y4 --> Y4A --> Y4B --> Y4C
```

Four-year roadmap for smart factory transformation: connect, analyze, automate, and optimize manufacturing operations.

## Related

- [Consulting Frameworks Overview](./47-vol4-consulting-frameworks-industry.md)
- [Strategy Execution Frameworks](./95-vol4-consulting-frameworks-industry-strategy-execution-frameworks.md)
- [Framework Selection Guide](./97-vol4-consulting-frameworks-industry-framework-selection-glossary.md)

## Sources

---
