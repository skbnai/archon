---
title: "Part 15 — Enterprise Architecture Mapping"
doc_type: guide
domain: strategy
topic_id: part-15-enterprise-architecture
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "enterprise-architect"]
supersedes: ["docs/enterprise-ai-report/part-15-enterprise-architecture.md"]
tags: ["enterprise-architecture", "togaf", "capability-map", "value-stream", "business-architecture", "reference-architecture"]
sources: []
---

# Part 15 — Enterprise Architecture Mapping

Enterprise architecture for AI permeates the four TOGAF domains: Business, Application, Information, and Technology. This page maps how AI transforms each domain and provides the TOGAF-aligned capability framework.

## AI in the Four Architecture Domains (TOGAF ADM)

The TOGAF Architecture Development Method structures enterprise architecture across four domains. AI transforms all four:

### Business Architecture

**How AI changes business capability:**

AI adds value through three mechanisms: intelligence (better decisions), automation (faster execution), and personalisation (tailored outcomes).

| Business Capability | Without AI | With AI |
|--------------------|-----------|---------|
| Customer Service | Human agents; IVR | AI copilots, autonomous service agents |
| Risk & Compliance | Manual reviews; rule-based | AI risk scoring; automated monitoring |
| Sales & Marketing | Human-led outreach | AI-personalised; agent-managed campaigns |
| Finance & Accounting | Manual reconciliation | Autonomous agents; AI audit |
| HR & Talent | Manual screening | AI screening, coaching, workforce planning |
| Operations | Rule-based automation | Agentic process automation |
| Strategy & Planning | Human analysis | AI-augmented strategy; scenario modelling |

**Value Stream Mapping with AI:** AI adds value at three points in any value stream: intelligence, automation, and personalisation.

### Application Architecture

**AI-Native Application Patterns:**

| Pattern | Description | Example |
|---------|-------------|---------|
| **AI Copilot** | AI embedded in existing UI to assist human | Coding assistant, drafting assistant |
| **AI Gateway** | AI-powered processing layer between systems | Document classification before routing |
| **Autonomous Agent** | Replaces a human workflow step | Invoice approval agent, scheduling agent |
| **Multi-Agent System** | Orchestrated agents for complex workflows | Research → analysis → recommendation workflow |
| **AI-Enhanced API** | Existing API response enriched with AI | Search results re-ranked by semantic relevance |
| **Conversational Interface** | Natural language replaces structured UI | Chatbot replacing form-based portal |

**Application Architecture Principles for AI:**
- AI capability exposed as platform services (not embedded in each application)
- Applications consume AI via the AI Service Catalog
- AI integration through event-driven architecture where possible (async, resilient)
- AI components independently deployable and rollback-capable

### Information Architecture

**AI-Specific Information Architecture:**

<!-- TODO(diagram): Convert information layers table to Mermaid diagram -->

AI requires a multi-layered information architecture:

- **Knowledge Layer:** Document stores, knowledge graphs, ontologies, curated corpora
- **Vector Layer:** Embedding stores, semantic indexes, multimodal indexes
- **Context Layer:** Conversation history, session state, user profiles, agent working memory
- **Feature Layer:** Computed features for ML models, feature store
- **Data Foundation:** Source systems, data lake, data warehouse, streaming data

**Key information governance questions AI forces:**
- Who owns the AI training data? (and its quality, bias, privacy)
- How do we version the knowledge base? (reproducibility for audit)
- What is the authoritative source for a given domain? (RAG grounding integrity)
- How do we govern AI-generated data? (is it enterprise data? can it feed back into training?)

### Technology Architecture

**AI Technology Reference Architecture:**

<!-- TODO(diagram): Convert technology layers to Mermaid -->

The enterprise AI technology architecture spans five layers:

- **Presentation:** Web / Mobile / API / Conversational UI
- **Application:** AI Features, Agent Applications, Copilots, Autonomous Workflows
- **AI Platform:** Inference, Embedding, RAG, Agent Runtime, Memory, Tool Registry, Guardrails, Policy, Observability
- **Data:** Knowledge Bases, Vector DBs, Data Lake, Feature Store, Streaming
- **Compute & Cloud:** GPU Clusters, Serverless, Containers, Multi-cloud (AWS + Azure + GCP)

### Security Architecture

See Part 13 for the complete AI security model.

**TOGAF security principles applied to AI:**
- Security by design (not bolted on): guardrails, identity, and policy baked into the AI platform
- Principle of least privilege: agents, models, and users access only what they need
- Defence in depth: multiple security controls at each architecture layer
- Secure by default: new AI services inherit security controls automatically

### Integration Architecture

**AI Integration Patterns:**

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **API Integration** | AI feature exposed/consumed via REST/gRPC | Standard synchronous AI features |
| **Event-Driven** | AI trigger on event; result delivered async | Async document processing, monitoring |
| **MCP (Model Context Protocol)** | Tool integration for AI agents | Agent-to-tool connections |
| **A2A (Agent-to-Agent)** | Agent delegating to sub-agents | Multi-agent orchestration |
| **Streaming** | Real-time AI inference with token streaming | Chat interfaces, live generation |
| **Batch** | Scheduled AI processing of data volumes | Bulk document processing, analysis |

## AI Capability Map

The AI capability map organises enterprise AI capabilities into five levels:

**Level 5 — AI-Native Operations:** Autonomous decision-making, constitutional AI, sovereign AI infrastructure

**Level 4 — Agentic Capabilities:** Multi-agent orchestration, long-horizon task execution, digital workforce

**Level 3 — GenAI Capabilities:** Text generation, code generation, conversation, document intelligence

**Level 2 — ML Capabilities:** Prediction, classification, anomaly detection, personalisation, optimisation

**Level 1 — AI Platform Foundation:** Inference, embedding, evaluation, observability, governance, security

Each level builds on the one below. Enterprises must build Level 1 before pursuing Level 5.

## TOGAF Concepts Applied to AI

| TOGAF Concept | AI Application |
|---------------|----------------|
| **Architecture Vision** | AI strategy: why AI? what capabilities? what outcomes? |
| **Business Architecture** | AI-enabled value streams, AI capabilities by domain |
| **Information Architecture** | Knowledge architecture, data for AI, vector layer |
| **Application Architecture** | AI application patterns, agent architectures |
| **Technology Architecture** | AI platform, infrastructure, cloud mapping |
| **Opportunities & Solutions** | AI use case portfolio, prioritisation |
| **Migration Planning** | AI transformation roadmap (see Part 17) |
| **Implementation Governance** | AI ARB, delivery governance, quality gates |
| **Architecture Change Management** | AI architecture evolution as capability matures |

## Authoritative Guides

Comprehensive enterprise architecture guidance is available in the **Enterprise Architecture** and **Agentic Systems** domains. Consult specialised guides for:

- TOGAF-aligned AI platform architecture
- All four architecture domains (business, application, information, technology)
- Application architecture patterns for AI
- Business architecture and value stream mapping
- Integration architecture (MCP, A2A protocols)
- Capability maps and maturity models

## Related

- [Part 1 — Evolution](11-part-01-evolution.md) — How architecture evolves at each stage
- [Part 7 — Platform Operating Model](17-part-07-platform-operating-model.md) — Technology architecture (AI platform layer)
- [Part 13 — Security Model](23-part-13-security-model.md) — Security architecture
- [Part 17 — Transformation Roadmap](27-part-17-transformation-roadmap.md) — Roadmap from current to target architecture state

## Sources

[No external sources for this page.]
