---
title: "AI Service Catalog: Core Inference & Data Services"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-10-service-catalog
maturity: practitioner
personas: [platform-lead, architect, developer]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-10-service-catalog.md
tags: ["service-catalog", "platform", "inference", "embedding", "api-service", "sla"]
sources: []
pagination_next: strategy/part-10-service-catalog-agent-guardrail-observability
---

# AI Service Catalog: Core Inference & Data Services

The enterprise AI platform service catalog defines the complete set of AI-as-a-Service offerings available to development teams. Each service has documented SLA, pricing, limitations, and usage guidelines.

## What is an AI Service Catalog?

The service catalog is the enterprise's **menu of available AI services** with defined SLAs, pricing, quotas, and governance requirements. It eliminates the need for each team to build redundant infrastructure while centralizing governance and cost control.

## Service 1: Inference-as-a-Service (IaaS)

**Purpose:** Centralized, metered access to LLMs and other AI models

**Models Supported:** GPT-4o, Claude 3/4, Gemini 1.5 Pro, Llama 3.1, open-source models

**SLA:**
- Availability: 99.9%
- Latency: &lt;500ms p95 (non-streaming), &lt;100ms first token (streaming)
- Throughput: Auto-scales to organization quota

**Pricing:** Per-1M-tokens consumed (input/output); varies by model. Chargeback to business unit.

**Governance:**
- Rate limiting per team/use case
- API keys with audit logging
- Cost attribution by team, project, model
- Approved model list (not all models available)

**Access:** REST API, Python SDK, JavaScript SDK

**Quotas:** Default 1M tokens/day per team; approval needed for higher

## Service 2: Embedding-as-a-Service

**Purpose:** Convert documents and queries into vector embeddings for RAG systems

**Models Supported:** text-embedding-3-large, Cohere Embed v3, BGE, Jina v3

**SLA:**
- Availability: 99.5%
- Latency: &lt;200ms p95
- Batch processing: &lt;1s per 100 documents

**Pricing:** Per-1M tokens consumed (approximate: 1 document ≈ 100 tokens)

**Use Cases:** Document embedding for RAG, semantic search, similarity matching

**Batch API:** For embedding large document corpuses (>10k documents); asynchronous

**Access:** REST API, batch upload

**Quota:** 10M tokens/month default; higher via approval

## Service 3: Prompt Service

**Purpose:** Registry, versioning, and governance for system prompts

**Features:**
- Prompt versioning with Git-like history
- Approval workflow (peer review, responsible AI review, security)
- Prompt testing and evaluation tooling
- A/B testing infrastructure (routing variant % traffic)
- Prompt analytics (usage, cost per prompt, quality metrics)

**SLA:** 99.9% availability

**Governance:**
- All production prompts must be registered and approved
- Version control: every prompt change is audited
- Approval required before production deployment
- Retirement process: deprecate old prompts gracefully

**Access:** Web portal, CLI, REST API

## Service 4: Vector Database Service

**Purpose:** Managed vector storage for embeddings with semantic search

**Supported Technologies:** Pinecone, Weaviate, Milvus, pgvector (PostgreSQL)

**Capabilities:**
- Store and retrieve embeddings at scale
- Semantic search (cosine similarity, dot product)
- Hybrid search (combine semantic + keyword search)
- Metadata filtering
- Namespace isolation per use case

**SLA:** 99.9% availability, &lt;500ms query latency

**Quota:** 1M vectors default; scale via approval

**Pricing:** Per-million-vector-operations; managed by platform

**Access:** REST API, SDKs

## Service 5: Knowledge Service

**Purpose:** End-to-end managed RAG service

**Components:**
- Document ingestion pipeline (PDF, Word, web, SharePoint)
- Chunking strategy (configurable)
- Embedding and vector storage
- Retrieval optimization (re-ranking, query decomposition)
- Knowledge freshness monitoring

**SLA:** 99.5% availability, &lt;1s end-to-end retrieval

**Governance:**
- PII scanning before indexing
- Access control per knowledge base
- Source attribution tracking
- Freshness monitoring (deprecated content removal)

**Pricing:** Per-document indexed + per-retrieval-operation

**Access:** Web UI for upload, REST API for retrieval

## Service 6: Memory Service

**Purpose:** Managed conversational and episodic memory for agents

**Memory Types:**
- **Short-term:** Current conversation context (token-limited)
- **Episodic:** Past interactions (searchable history)
- **Semantic:** Learned facts and patterns
- **Procedural:** Skills and learned behaviors

**SLA:** 99.5% availability

**Governance:**
- User-controlled deletion (privacy compliance)
- Retention policies per memory type
- Access control (agent accesses only authorized memories)
- Encryption at rest and in transit

**Storage:** Default 1GB per memory namespace; scale via request

**Pricing:** Per-GB-month stored

**Access:** REST API, SDKs

## Service 7: Fine-Tuning Service

**Purpose:** Managed fine-tuning for base models on enterprise data

**Supported Models:** GPT-4, Claude, Llama (depends on vendor support)

**Process:**
1. Upload training data (JSON format: prompt + expected response)
2. Configure training parameters (learning rate, epochs, batch size)
3. Run async training job
4. Evaluate on validation set
5. Deploy fine-tuned model as new version

**SLA:** 99% availability (training jobs); job completion in 24-72 hours typical

**Governance:** Training data logged and audited; fine-tuned model registered in model registry

**Cost:** Per-training-hour (GPU cost)

**Access:** Web portal, REST API

---

## Service Governance Principles

1. **Self-Service:** Developers provision services via portal without tickets
2. **Metered Consumption:** Every API call tracked and attributed to business unit
3. **Clear SLAs:** Every service has defined availability, latency, quota
4. **Cost Transparency:** Teams see usage and cost in real-time dashboards
5. **Governance by Default:** Guardrails, logging, compliance built into each service

---

## Related

- [AI Service Catalog: Agent, Guardrail & Observability Services](71-part-10-service-catalog-agent-guardrail-observability.md)
- [AI Service Catalog: Tiers, Governance & Developer Portal](72-part-10-service-catalog-tiers-governance-developer-portal.md)
- [Platform Operating Model](17-part-07-platform-operating-model.md)

## Sources

