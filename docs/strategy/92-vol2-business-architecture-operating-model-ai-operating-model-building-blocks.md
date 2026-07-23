---
title: "Business Architecture: AI Operating Model & Building Blocks"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol2-business-architecture-operating-model-part4
maturity: expert
personas: [Chief AI Officer, AI Architect, Enterprise Architect]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - ai-operating-model
  - mlops
  - agentic-systems
  - building-blocks
sources: []
pagination_prev: strategy/vol2-business-architecture-operating-model-organization-operating-model-design
---

# Business Architecture: AI Operating Model & Building Blocks

## Why a Distinct AI Operating Model?

AI capabilities require a fundamentally different operating model from traditional IT:

| Dimension | Traditional IT | AI Operating Model |
|---|---|---|
| **Delivery** | Requirements → Build → Release | Experiment → Validate → Scale |
| **Maintenance** | Bug fixes, features | Model retraining, drift monitoring, prompt updates |
| **Quality** | Functional correctness | Accuracy, fairness, explainability |
| **Governance** | Technical standards | Responsible AI + regulatory compliance |
| **Skills** | Software engineers | ML engineers, data scientists, AI architects |
| **Risk** | System failure | Hallucination, bias, adversarial attack |
| **Lifecycle** | SDLC | MLOps + LLMOps + AgentOps |

## AI Operating Model Components

```mermaid
graph TD
    AIOM["AI OPERATING MODEL"]
    
    GOV["GOVERNANCE LAYER"]
    G1["AI Strategy Alignment"]
    G2["AI Governance Board<br/>oversight, risk, ethics, compliance"]
    G3["Responsible AI Framework<br/>fairness, explainability, safety"]
    G4["AI Risk Register<br/>per-model risk tracking"]
    
    ORG["ORGANIZATION LAYER"]
    O1["AI Center of Excellence<br/>standards, enablement"]
    O2["AI Platform Team<br/>builds/operates AI infrastructure"]
    O3["AI Product Teams<br/>embed AI into value streams"]
    O4["AI Enablement<br/>training, certification, support"]
    
    DEL["DELIVERY LAYER"]
    D1["AIDLC<br/>AI Development Lifecycle"]
    D2["MLOps<br/>traditional ML lifecycle"]
    D3["LLMOps<br/>large language model lifecycle"]
    D4["AgentOps<br/>agentic AI lifecycle"]
    D5["PromptOps<br/>prompt versioning, governance"]
    
    PLAT["PLATFORM LAYER"]
    P1["AI Foundation<br/>Model Registry, Inference, Gateway"]
    P2["Data Foundation<br/>Feature Store, Vector DB, KG"]
    P3["Observability<br/>Monitoring, Drift, Cost"]
    P4["Security<br/>Filtering, Validation, Control"]
    
    AIOM --> GOV
    AIOM --> ORG
    AIOM --> DEL
    AIOM --> PLAT
    
    GOV --> G1 --> G2 --> G3 --> G4
    ORG --> O1 --> O2 --> O3 --> O4
    DEL --> D1 --> D2 --> D3 --> D4 --> D5
    PLAT --> P1 --> P2 --> P3 --> P4
```

Four-layer AI operating model spanning governance, organization, delivery, and platform foundations.

## MLOps, LLMOps, AgentOps Compared

| Dimension | MLOps | LLMOps | AgentOps |
|---|---|---|---|
| **What it governs** | Traditional ML models | Large language models | Agentic AI systems |
| **Training** | Regular retraining from data | Fine-tuning + RLHF | Prompt engineering + RAG |
| **Deployment** | Model serving endpoints | API integration + prompts | Agent orchestration + tools |
| **Monitoring** | Accuracy, drift, feature drift | Hallucination rate, cost/token | Task completion, tool errors |
| **Key tools** | MLflow, SageMaker, Vertex AI | LangSmith, PromptLayer | LangGraph, AutoGen |
| **Risk** | Model drift, bias | Hallucination, prompt injection | Runaway agents, tool misuse |
| **Cost driver** | Training compute | Inference tokens | Tokens + tool calls |
| **Governance** | Model cards, bias testing | Constitutional AI, guardrails | Human-in-the-loop, kill switch |

## PromptOps

**PromptOps** is the operational discipline for managing prompts in production LLM/GenAI systems:

```mermaid
graph LR
    PE["Prompt<br/>Engineering"]
    PT["Prompt<br/>Testing"]
    PR["Prompt<br/>Review"]
    VR["Version<br/>Registry"]
    AB["A/B<br/>Testing"]
    DP["Deployment<br/>Pipeline"]
    MPB["Model-Prompt<br/>Binding"]
    RQM["Response Quality<br/>Monitoring"]
    TCM["Token Cost<br/>Monitoring"]
    PID["Prompt Injection<br/>Detection"]
    
    PE --> PT --> PR --> VR --> AB --> DP --> MPB --> RQM
    MPB --> TCM
    RQM --> PID
```

End-to-end lifecycle for managing prompts in production systems from engineering through testing, deployment, and continuous monitoring.

## AI Centers of Excellence (AI CoE)

**AI CoE Charter:**

Mission: Enable responsible, scalable, and value-creating AI adoption across the enterprise.

Responsibilities:
- STANDARDS: Define AI development standards and guidelines
- PLATFORM: Build and operate shared AI infrastructure
- ENABLEMENT: Train and certify AI practitioners
- GOVERNANCE: Run AI risk reviews and approvals
- INNOVATION: Track emerging AI capabilities
- EVANGELISM: Share success stories; drive adoption

**Operating Model:** Federated — AI CoE sets standards; teams execute within those standards; AI CoE available for consulting support.

## Business Building Blocks

**Building Blocks** are reusable, standardized components — business, application, data, or technology — that can be assembled to create capabilities.

TOGAF distinguishes:
- **Architecture Building Blocks (ABBs)** — Abstract, specification-level components (e.g., "Authentication Service")
- **Solution Building Blocks (SBBs)** — Concrete, implemented components (e.g., "Microsoft Entra ID")

**Business Building Block Taxonomy:**

```mermaid
graph TD
    CAP["BUSINESS CAPABILITIES<br/>What we do<br/>e.g., Customer Onboarding,<br/>Credit Assessment"]
    SER["BUSINESS SERVICES<br/>What we offer<br/>e.g., Digital Account Opening,<br/>Real-time Transfer"]
    PROC["BUSINESS PROCESSES<br/>How we do it<br/>e.g., KYC Verification,<br/>Loan Approval Workflow"]
    RULE["BUSINESS RULES<br/>Constraints on operations<br/>e.g., Loans >$500K<br/>require two approvers"]
    OBJ["BUSINESS OBJECTS<br/>What we manage<br/>e.g., Customer, Account,<br/>Transaction, Claim"]
    EV["BUSINESS EVENTS<br/>What happens<br/>e.g., AccountOpened,<br/>LoanApproved, PaymentReceived"]
    
    CAP --> SER
    SER --> PROC
    PROC --> RULE
    PROC --> OBJ
    PROC --> EV
```

Six levels of business building blocks from capabilities and services through processes, rules, objects, and events.

**Technology Building Blocks (2026):**

| Building Block | Examples |
|---|---|
| **Identity** | Entra ID, Okta, AWS IAM |
| **API Gateway** | Kong, Apigee, AWS API Gateway |
| **Integration** | Kafka, MuleSoft, Azure Service Bus |
| **Observability** | Datadog, Grafana, OpenTelemetry |
| **Container Platform** | Kubernetes, ECS, AKS |
| **CI/CD** | GitHub Actions, ArgoCD, Tekton |
| **AI Inference** | AWS Bedrock, Azure OpenAI, vLLM |
| **Vector Store** | Pinecone, Weaviate, pgvector |
| **Knowledge Graph** | Neo4j, AWS Neptune |
| **Agent Framework** | LangGraph, Strands, AutoGen |

## Business Glossary and Taxonomy

**Business Glossary:** The authoritative dictionary of business terms ensuring everyone uses the same words to mean the same things. Prevents data integration failures and AI model inconsistencies.

**Business Taxonomy:** Hierarchical classification system for organizing concepts (products, customers, geographies, channels). Critical for AI classification models and RAG system accuracy.

## Related

- [Business Architecture: Organization Design](./91-vol2-business-architecture-operating-model-organization-operating-model-design.md)
- [AI Strategy & Transformation](./48-vol5-ai-strategy-transformation-glossary.md)
- [AI Transformation Models](./98-vol5-ai-strategy-transformation-glossary-transformation-maturity-models.md)

## Sources

---
