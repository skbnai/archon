---
title: "Relationship Maps: AI/Ops Comparisons & Terminology Cross-Reference"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol10-relationship-maps-glossary-part2
maturity: practitioner
personas:
  - enterprise-architect
  - strategy-consultant
  - ai-leader
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - ai-concepts
  - terminology
  - framework-comparison
  - cross-reference
sources: []
pagination_prev: strategy/vol10-relationship-maps-glossary
pagination_next: strategy/vol10-relationship-maps-glossary-glossary-terms-a-g
---

# Relationship Maps: AI/Ops Comparisons & Terminology Cross-Reference

Why this matters: Enterprises adopt frameworks from McKinsey, TOGAF, BIZBoK, SAFe, and Gartner — each using different terminology for the same concepts. A shared terminology cross-reference prevents misalignment when multiple frameworks are in use.

## AI and Operations Concept Comparisons

### AI Model vs. AI System vs. AI Product

**AI Model** is a mathematical function trained on data to make predictions or generate content (e.g., GPT-4, BERT). **AI System** is a model plus infrastructure, data, and interfaces that make the model usable (e.g., a fraud detection system with model, API, monitoring, retrain pipeline). **AI Product** is an AI system wrapped with UX, business logic, and go-to-market (e.g., Grammarly, GitHub Copilot).

### Agent vs. Assistant vs. Copilot vs. Bot

**Bot** is rule-based automation with no LLM. **Assistant** is an LLM-powered conversational interface with low autonomy (executes when asked). **Copilot** is AI embedded in workflow tools assisting humans with low-to-medium autonomy (suggests; human accepts/rejects). **Agent** is autonomous AI that plans and executes multi-step tasks using tools with high autonomy (acts without step-by-step instruction).

### LLM vs. SLM vs. Foundation Model

**Foundation Model** is a large model trained on broad data; general-purpose; fine-tunable (e.g., GPT-4, Claude 3). **LLM (Large Language Model)** is a foundation model for text/language (7B–1000B+ parameters). **SLM (Small Language Model)** is a compact model optimized for efficiency (1B–7B parameters).

### MLOps vs. LLMOps vs. AgentOps

**MLOps** covers deploying and maintaining traditional ML models (feature drift, retraining, A/B testing). **LLMOps** extends MLOps for LLM concerns (prompt versioning, RAG, hallucination control). **AgentOps** extends LLMOps for agentic systems (agent traces, tool invocation logging, multi-agent coordination).

### Fine-tuning vs. RAG vs. Prompt Engineering

**Prompt Engineering** crafts instructions to guide model behavior (low cost, 80% of use cases). **RAG (Retrieval-Augmented Generation)** injects relevant context from a knowledge base at query time (medium cost, for proprietary/current information). **Fine-tuning** trains a model on domain-specific examples to permanently change behavior (high cost, for deep style/domain knowledge).

**Decision guide:** Try prompt engineering first. Add RAG when proprietary knowledge or currency matters. Fine-tune only when prompt + RAG fails.

### Orchestration vs. Choreography

**Orchestration** uses a central coordinator directing all participants (one conductor controlling flow). **Choreography** has each service reacting to events with no central coordinator (each dancer knows their part).

### Horizontal vs. Vertical Integration

**Horizontal integration** combines with competitors at the same level of the value chain (e.g., bank acquiring another bank). **Vertical integration** expands into upstream supply or downstream distribution (e.g., retailer acquiring a manufacturer).

### Synchronous vs. Asynchronous Communication

**Synchronous** communication: caller waits for response (real-time queries, user-facing APIs). **Asynchronous** communication: caller continues; response arrives later (long-running processes, decoupled services).

### Latency vs. Throughput

**Latency** is time from request to response for a single request (milliseconds; P50, P95, P99). **Throughput** is number of requests processed per unit time (RPS, TPS).

### CapEx vs. OpEx (Technology Context)

**CapEx (Capital Expenditure)** is investment in assets providing benefit beyond one year (data center hardware, perpetual licenses). **OpEx (Operating Expenditure)** is day-to-day running costs (cloud subscriptions, SaaS, API calls).

AI via API is OpEx. AI platform build may be CapEx. CFO perspective shapes how AI investment is accounted.

### Accuracy vs. Precision vs. Recall

**Accuracy** is percentage of all predictions that are correct. **Precision** is percentage of positive predictions that are actually positive. **Recall** is percentage of actual positives correctly identified. **F1 Score** is the harmonic mean of precision and recall.

Fraud detection prefers high recall (catch all fraud, accept false positives). Spam filter prefers high precision (don't block legitimate, accept spam).

### Waterfall vs. Agile vs. SAFe

**Waterfall** has full upfront planning and single release at end. **Agile (Team)** has sprint-by-sprint delivery with evolving requirements. **SAFe (Enterprise)** has quarterly PI Planning with multi-team governance.

### SOA vs. Microservices vs. Monolith

**Monolith** is a single deployable unit containing all functionality. **SOA** uses enterprise services shared via ESB (coarse-grained). **Microservices** uses fine-grained, independently deployable services.

### Push vs. Pull (Data and Notification)

**Push** sends data to client when available (real-time notifications, WebSocket). **Pull** has client request data on demand (REST API, batch reporting). **Event-driven (hybrid)** publishes events that consumers pull from.

### Zero-Shot vs. Few-Shot vs. Chain-of-Thought

**Zero-shot** provides task description only; no examples. **Few-shot** provides 2–5 examples in prompt. **Chain-of-thought** provides step-by-step reasoning examples. **Fine-tuning** bakes examples into model weights.

---

## Framework Terminology Cross-Reference

The same concept is named differently across frameworks. This enables translation:

| Concept | McKinsey | TOGAF 10 | BIZBoK | SAFe 6.0 | Gartner |
|---------|---------|---------|--------|---------|---------|
| What we exist to do | Mission/Purpose | Architecture Principles | Business Motivation Model | Mission | Business Purpose |
| Where to play/how to win | Strategy | Architecture Vision | Strategy | Portfolio Vision | Strategic Intent |
| Annual priorities | Strategic Priorities | Architecture Roadmap | Strategic Themes | Portfolio Epics | Strategic Initiatives |
| What we can do | Organizational Capability | Business Capability | Business Capability | Competency | Business Capability |
| How work flows | Process | Business Process | Value Stream | Value Stream | Business Process |
| Investment grouping | Initiative | Architecture Work Package | Initiative | Portfolio Epic | Investment Theme |
| Technology building block | Technology Module | ABB | IT Building Block | Solution | Technology Platform |
| Specific implementation | Technology Solution | SBB | Application | Solution | Vendor Product |
| Governance body | Steering Committee | Architecture Board | Governance Forum | Lean Portfolio Management | IT Steering Committee |
| Performance measure | KPI | Architecture Metric | Performance Indicator | OKR Key Result | KPI |
| Change program | Transformation Initiative | Architecture Transition | Change Initiative | Program Increment Objective | Transformation Program |
| Business context | Business Context | Enterprise Context | Business Environment | Enterprise | Business Context |
| System integration | Integration Layer | Technology Architecture | Integration Domain | Platform | Integration Platform |
| Customer journey | Customer Journey | Business Scenario | Value Stream | Customer Journey | Customer Experience Map |
| Organization model | Organization Model | Organization Architecture | Organization Map | Organization | Operating Model |
| Data governance | Data Strategy | Data Architecture | Information Architecture | Data Management | Data Governance |
| Vendor relationship | Partnership | External Organization | Partner | Supplier | Third Party |
| Risk assessment | Risk & Opportunity | Risk Management | Risk Register | Risk Register | Risk Assessment |

---

## Related

- [Relationship Maps: Concept Hierarchy & Core Comparisons](44-vol10-relationship-maps-glossary.md)
- [Enterprise Glossary: A-G](87-vol10-relationship-maps-glossary-glossary-terms-a-g.md)
---

*Volume 10 of 10 — Enterprise Strategy & Business Architecture Handbook. Part 2 of 5.*
