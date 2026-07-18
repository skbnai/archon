---
title: "Part 18 — Industry Case Studies & Vendor Perspectives"
doc_type: guide
domain: strategy
topic_id: part-18-case-studies
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "strategy-lead"]
supersedes: ["docs/enterprise-ai-report/part-18-case-studies.md"]
tags: ["case-studies", "aws", "microsoft", "google", "openai", "anthropic", "mckinsey", "deloitte", "gartner"]
sources: []
---

# Part 18 — Industry Case Studies & Vendor Perspectives

Cloud providers, AI vendors, and consulting firms each recommend distinct operating models for enterprise AI. This page synthesises vendor perspectives, consulting firm frameworks, and industry-specific patterns.

## Cloud Provider Operating Models & Best Practices

### AWS

**AWS AI Strategy:** "Builders first" — provide the components; enterprises assemble.

| Dimension | AWS Approach |
|-----------|-------------|
| **Operating Model** | Platform-first; Bedrock as managed foundation; AgentCore for agent lifecycle |
| **Governance** | Bedrock Guardrails; model evaluation; automated safety |
| **Cost Model** | Pay-per-token; no commitment required; volume discounts via Savings Plans |
| **Delivery** | Bedrock Knowledge Bases (managed RAG); Strands (agent framework) |
| **Differentiator** | Broadest model choice (Amazon, Anthropic, Mistral, Meta, Cohere in one API) |

AWS recommends enterprises use Bedrock as a multi-model abstraction layer to avoid LLM lock-in. AgentCore provides the agent runtime, memory, and observability scaffolding so teams focus on agent logic.

### Microsoft Azure

**Microsoft AI Strategy:** "Copilot everywhere" — AI embedded in productivity stack.

| Dimension | Microsoft Approach |
|-----------|-------------------|
| **Operating Model** | Azure AI Foundry as the enterprise AI platform; Copilot Studio for business user agents |
| **Governance** | Azure AI Content Safety; Responsible AI dashboard; Purview for AI data governance |
| **Identity** | Entra ID as the identity backbone for AI agents; managed identity for workloads |
| **Delivery** | Azure OpenAI (GPT-4o, o1); Azure AI Search (RAG); Semantic Kernel; AutoGen |
| **Differentiator** | Deepest Microsoft 365 / Dynamics integration; broadest regulated industry compliance |

Microsoft's enterprise motion centres on extending existing M365 investments into AI. Copilot for Microsoft 365 democratises GenAI; Azure AI Foundry enables custom enterprise AI. Entra ID is the identity layer.

### Google Cloud

**Google AI Strategy:** "Multi-modal AI native" — deepest AI research; Gemini at the centre.

| Dimension | Google Approach |
|-----------|----------------|
| **Operating Model** | Vertex AI as the unified AI platform; Agent Builder for no-code agent creation |
| **Governance** | Vertex AI Model Evaluation; Responsible AI Toolkit; DLP integration |
| **Delivery** | Gemini 1.5 Pro/Flash; Vertex AI Search; LangChain integration; Agent Space |
| **Differentiator** | Multi-modal from the ground up (text, image, video, audio); best-in-class search |

## AI Vendor Perspectives

### OpenAI

**Operating Model Recommendation:** GPT-4o/o1 for reasoning; Assistants API for agent-like behaviour; enterprise agreement for data privacy.

Enterprise should establish AI policy before deploying ChatGPT Enterprise. Use system prompts as primary governance. Evaluate every 3 months as model capability evolves rapidly.

### Anthropic

**Operating Model Recommendation:** Claude for safety-sensitive, regulated, and high-stakes applications. Constitutional AI as governance foundation. Claude Code SDK for building agent systems.

Design for human oversight from day one. Use the Model Specification as reference for how Claude reasons. Prefer Claude for legal, financial, healthcare, and any use case where factual accuracy and safety are paramount.

### NVIDIA

**Operating Model Recommendation:** NIM (NVIDIA Inference Microservices) for self-hosted inference; NeMo for enterprise fine-tuning; RAPIDS for GPU-accelerated data processing.

For enterprises with strict data residency or latency requirements, self-hosted inference on NVIDIA infrastructure avoids cloud LLM API constraints. H100/B200 clusters provide compute backbone for training and inference.

## Consulting Firm Perspectives

### McKinsey & Company

**Key frameworks:** *Rewired* (2023) — the definitive blueprint for enterprise AI transformation, emphasising integrated teams, digital/AI factory operating model, and talent transformation.

**Operating model view:** Integrated cross-functional teams (business + data + engineering) organised around the value chain, supported by a central AI factory for repeatable use cases.

**Key stat:** McKinsey estimates £2.6–£4.4 trillion annual value from GenAI across industries; 75% concentrated in customer operations, marketing, software engineering, and R&D.

### Deloitte

**Key framework:** *AI Readiness Index* — five dimensions: Strategy, Talent, Data, Technology, Trust & Ethics.

**Operating model view:** "Three-speed" model: fast (edge experimentation), medium (business unit AI), slow (central platform and governance). Governance must be designed for the enterprise's risk appetite.

### Accenture

**Key framework:** *AI Maturity Index* — six levels; emphasises that operating model transformation lags technology adoption by 18–24 months.

**Operating model view:** Enterprises which embed AI engineers directly in business functions (vs. keeping them in a central CoE) achieve 40% faster time-to-value. But this requires the central platform to be self-service enough that embedded teams operate independently.

### BCG (Boston Consulting Group)

**Key framework:** *AI@Scale* — distinguishes between AI factory (repeatable use cases at speed) and AI R&D (novel capabilities requiring research investment). These require separate operating models.

**Key finding:** Only 28% of enterprise AI PoCs make it to production. Biggest barriers: data quality issues (42%), lack of business buy-in (38%), and governance bottlenecks (31%).

### Gartner

**Key prediction (2025):** By 2027, 15% of new applications will be built using agentic AI patterns. By 2028, autonomous AI agents will handle 50% of routine enterprise decisions.

**Operating model view:** Start with the "Minimum Viable AI Operating Model" — just enough structure to govern and deliver — then scale. Over-engineering the operating model at L1 is a common failure mode.

### Bain & Company

**Key framework:** *AI Advantage* — identifies four strategic postures: AI Fast Follower, AI Specialist, AI Transformer, AI Leader. Most enterprises should target Fast Follower to Transformer based on competitive context.

### Big Four (EY, PwC, KPMG)

**EY:** Focus on responsible AI and regulatory compliance as the foundation. Audit ability and explainability from day one.

**PwC:** "Responsible AI Toolkit" — practical implementation checklist for EU AI Act compliance. Start compliance work immediately; conformity assessment for high-risk AI takes 6–12 months.

**KPMG:** Emphasis on AI risk management integrated with enterprise risk framework (ERM). AI risks must be owned by the Chief Risk Officer.

## Industry-Specific Patterns

| Industry | Typical Pattern | Key Considerations |
|----------|----------------|---------------------|
| **Banking** | Brownfield — 30+ years of core banking, AML, credit systems | Legacy integration is the technical challenge |
| **Digital banks** | Greenfield — no legacy; AI-native from launch | Market risk for new products |
| **Healthcare** | Brownfield — EMR systems (Epic, Cerner) are constraint and asset | Regulatory burden (FDA, HIPAA) |
| **Retail (large)** | Brownfield — ERP, e-commerce, loyalty systems | Integration across systems |
| **Retail (D2C)** | Greenfield / Hybrid — modern stack with AI from day one | Faster time-to-value |
| **Manufacturing** | Brownfield — OT/IT integration; industrial IoT added to legacy MES/ERP | Asset maintenance complexity |
| **Government** | Brownfield — decades-old systems; strict compliance; high change resistance | Regulatory and procurement overhead |
| **Telecom** | Brownfield — BSS/OSS systems from 1990s; network data is asset | Massive data volumes |
| **Tech companies** | Greenfield by culture — even legacy systems regularly replaced | AI-native from start |

## Authoritative Guides

Case study collections and vendor deep-dives are available in **Use Cases** and **Platform** domains. These include:

- Industry-specific case studies (banking, healthcare, manufacturing, telecom, government)
- Agentic AI enterprise scenarios (15+ case studies)
- Enterprise Architecture masterclass case studies with AI decisions
- Cloud provider technical deep-dives (AWS, Azure, GCP)

## Related

- [Part 1 — Evolution](11-part-01-evolution.md) — Evolution stages illustrated through real examples
- [Part 2 — Operating Models](12-part-02-operating-models.md) — Operating model patterns from case studies
- [Part 17 — Transformation Roadmap](27-part-17-transformation-roadmap.md) — Roadmap informed by consulting firm guidance

## Sources

[No external sources for this page.]
