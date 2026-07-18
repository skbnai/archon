---
title: "Enterprise Building Blocks: Application & Core AI Blocks"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol7-enterprise-building-blocks-part2
maturity: practitioner
personas:
  - enterprise-architect
  - cto
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - application-building-blocks
  - api-management
  - identity-management
  - ai-building-blocks
sources: []
---

# Enterprise Building Blocks: Application & Core AI Blocks

## Application Building Blocks

### API Management

**ABB: API Gateway** — Manages north-south traffic (external client to internal service). Provides authentication, rate limiting, request routing, transformation, and analytics.

| SBB Option | Best For |
|------------|----------|
| **Kong Gateway** | Multi-cloud, open source flexibility |
| **AWS API Gateway** | AWS-native, serverless |
| **Azure API Management** | Microsoft ecosystem |
| **Apigee (Google Cloud)** | Enterprise API management at scale |
| **MuleSoft Anypoint** | Enterprise integration + API management |

**ABB: Service Mesh (East-West Traffic)** — Manages service-to-service communication within the cluster. Provides mutual TLS, load balancing, circuit breaking, retries, observability.

| SBB Option | Ecosystem | Notes |
|------------|-----------|-------|
| **Istio** | Kubernetes | Most feature-rich; higher complexity |
| **Linkerd** | Kubernetes | Lightweight; simpler operations |
| **AWS App Mesh** | AWS | ECS and EKS native |
| **Consul Connect** | Multi-platform | Works beyond Kubernetes |

### Messaging & Eventing

**ABB: Event Bus / Message Broker** — Asynchronous communication between services. Decouples producers from consumers.

| SBB Option | Throughput | Use Case |
|------------|-----------|---------|
| **Apache Kafka** | Very high (millions/sec) | Event streaming, audit logs, data pipelines |
| **AWS EventBridge** | High | AWS event routing, SaaS integration |
| **Azure Service Bus** | High | Enterprise messaging, dead-letter queues |
| **Google Pub/Sub** | Very high | GCP-native, global distribution |
| **RabbitMQ** | Medium | Traditional message queuing, task queues |

### Identity & Access Management

**ABB: Identity Provider (IdP)** — Authenticate users (and services) and issue tokens.

| Capability | Enterprise Standard |
|-----------|---------------------|
| **Human Authentication** | Microsoft Entra ID, Okta |
| **Workforce SSO** | SAML 2.0, OIDC |
| **Customer Identity (CIAM)** | Auth0, Entra B2C, Cognito |
| **Service-to-Service (M2M)** | OAuth 2.0 Client Credentials |
| **AI Agent Identity** | OAuth 2.0 + custom claims |

**ABB: Secret Manager** — Store and rotate credentials, API keys, certificates.

| SBB | Ecosystem |
|-----|-----------|
| **HashiCorp Vault** | Multi-cloud |
| **AWS Secrets Manager** | AWS |
| **Azure Key Vault** | Azure |
| **Google Secret Manager** | GCP |

### Observability Platform

**ABB: Observability Stack (Metrics + Logs + Traces)**

| Pillar | What It Answers | Enterprise SBB |
|--------|----------------|----------------|
| **Metrics** | Is the system healthy? Rate/error/duration? | Prometheus + Grafana, Datadog |
| **Logs** | What happened exactly? Error message? | ELK Stack, Splunk, Datadog |
| **Traces** | Where did latency go? Which service is bottleneck? | Jaeger, Zipkin, Datadog APM |

---

## AI Building Blocks

### AI Building Block Overview

AI layer requires a dedicated building block taxonomy forming the **AI Platform** — shared infrastructure enabling AI delivery across the enterprise.

```
GOVERNANCE LAYER    Safety/Guardrails, Evaluation Pipeline
INTELLIGENCE LAYER  LLM Gateway, Model Registry, Prompt Registry
KNOWLEDGE LAYER     Vector DB, Graph DB, Knowledge Base
MEMORY LAYER        Short-term, Long-term, Episodic, Semantic
DATA LAYER          Feature Store, Training Pipeline, Dataset
```

### LLM Gateway

**Purpose:** Entry point for all LLM calls. Provides model routing, rate limiting, cost control, caching, observability, safety.

| Solution | Deployment | Key Features |
|----------|-----------|-------------|
| **LiteLLM** | Self-hosted | Unified API for 100+ models; cost tracking |
| **Kong AI Gateway** | Enterprise | Rate limiting, semantic caching, plugins |
| **AWS Bedrock** | AWS-managed | Model diversity; enterprise compliance |
| **Azure AI Gateway** | Azure-managed | Native Azure integration |

### Prompt Registry

**Purpose:** Version-controlled, governed storage for prompts. Enables reuse, A/B testing, rollback, audit.

**Key Capabilities:**
- Prompt versioning (semantic versioning)
- Variable templating
- Environment promotion (dev → staging → production)
- A/B testing
- Audit trail

### Agent Runtime

**Purpose:** Hosted execution environment for AI agents. Manages agent lifecycle, tool execution, memory, human-in-the-loop.

| Solution | Deployment | Key Features |
|----------|-----------|-------------|
| **AWS Bedrock AgentCore** | AWS-managed | Native AWS integration; multi-agent; HITL |
| **Azure AI Agent Service** | Azure-managed | Foundry integration; enterprise auth |
| **LangGraph Cloud** | SaaS + self-host | Graph-based agent orchestration |
| **Temporal** | Self-hosted | Durable execution; workflow + agent hybrid |

### Memory Store

**Purpose:** Persistent storage for agent memory across conversations, sessions, time.

| Solution | Best For |
|----------|---------|
| **Redis** | Low-latency working memory, session state |
| **Pinecone** | Semantic long-term memory at scale |
| **Weaviate** | Hybrid semantic + metadata memory |
| **Mem0** | Purpose-built AI memory management |

### Knowledge Base (RAG Infrastructure)

**Purpose:** Infrastructure enabling AI to retrieve enterprise-specific information at query time.

| Solution | Scale | Key Feature |
|----------|-------|------------|
| **Pinecone** | Very large | Managed; fast query |
| **Weaviate** | Large | Hybrid search; GraphQL |
| **Qdrant** | Large | High-performance; Rust |
| **pgvector** | Medium | SQL + vector together |
| **Azure AI Search** | Large | Hybrid search; Azure native |

### Feature Store

**Purpose:** Central store of ML features. Ensures consistency between training-time and inference-time features.

| Solution | Deployment | Notes |
|----------|-----------|-------|
| **Feast** | Open source | Multi-cloud; flexible |
| **Tecton** | SaaS | Managed; strong MLOps integration |
| **AWS SageMaker Feature Store** | AWS | Managed; integrated pipeline |
| **Databricks Feature Store** | Databricks | Unified analytics + ML |

---

## Related

- [Enterprise Building Blocks: Concept & Business Blocks](../50-vol7-enterprise-building-blocks.md)
- [Enterprise Building Blocks: AI Infrastructure & Platform Engineering](06-vol7-enterprise-building-blocks-ai-infrastructure-platform-engineering.md)
---

*Volume 7 of 10 — Part 2 of 4*
