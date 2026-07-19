---
title: "AIDLC TOGAF Artifacts: Data & Application Architecture (Phase C1-C2)"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-artifacts-togaf-foundation-to-technology-part3
maturity: expert
personas: [architect, governance, manager]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, enterprise-architecture, togaf, adm, ai-first, governance, templates]
sources: []
---

# AIDLC TOGAF Artifacts: Data & Application Architecture (Phase C1-C2)

Part 3 of 4 — continues from [Part 2: Vision & Business Architecture (Phase A-B)](./05-aidlc-artifacts-togaf-vision-business-architecture.md), continues to [Part 4: Technology Architecture (Phase D)](./07-aidlc-artifacts-togaf-technology-architecture.md).

Enterprise architecture artifacts for TOGAF ADM Data Architecture Phase C1 and Application Architecture Phase C2, with AI-First extensions.

**Audience:** Enterprise Architects, Chief Technology Officers, Governance Leaders, AI Governance Council Members

**Coverage:** TOGAF ADM Data Architecture Phase C1 · Application Architecture Phase C2 · AI-First Extensions

**As of:** 2026

---

## TOGAF ADM Data Architecture Phase C1

**ARTIFACTS: DAB-001 · DM-001 · VDA-001 · FLS-001**

### Data Architecture Blueprint

**DAB-001**

Owner: Data Architect | ADM Phase: C1 | TOGAF 10 + AI-First Extension

| **Data Architecture Pattern** | *Data Lakehouse (Apache Iceberg on Azure Data Lake Gen2) + Data Mesh domain ownership + Feature Store for ML serving consistency* |
|---|---|
| **Primary Platform** | *Azure Data Lake Gen2 (storage) + Azure Databricks (Iceberg/Delta) + dbt (transformations) + Azure Event Hubs (streaming)* |
| **Data Domains** | *6 domains: Credit &amp; Risk, Customer, Operations, Marketing, HR, Enterprise (shared reference data). Each domain owns its AI training data and RAG knowledge base.* |
| **AI Data Products** | *Each domain publishes: (1) Training datasets (DVC-versioned, quality-certified). (2) Feature Store features (Feast). (3) RAG knowledge base (domain-specific vector namespace in Weaviate).* |
| **Lineage Standard** | *OpenLineage (Apache Airflow + dbt plugins). All data transformations emit lineage events. Lineage graph stored in Apache Atlas. Queryable via Atlan data catalog. EU AI Act Article 10 evidence package auto-generated.* |
| **Quality Gates** | *Data products must achieve quality score ≥90% (completeness, accuracy, freshness, consistency) before certification for AI training use. Quality scores published in Atlan catalog.* |
| **PII Handling** | *All PII fields tagged in Atlan. PII masking enforced at Feature Store and RAG retrieval layers via Microsoft Presidio. No PII may flow into LLM prompts unmasked.* |
| **Freshness SLAs** | *Training data refresh: weekly. Feature Store: 15-minute maximum lag. RAG knowledge bases: 4-hour maximum lag. Inference logs: real-time. Monitoring dashboards: 5-minute lag.* |

### Data Mesh Domain Design

**DM-001** (AI-First Extension)

Owner: Data Architect + Domain Architects | ADM Phase: C1 | TOGAF 10 + AI-First Extension

| **Domain** | **Key Data Assets** | **Business Owner / Data Owner** | **AI Data Products Published** | **Storage Location** | **Quality Status** |
|---|---|---|---|---|---|
| Credit &amp; Risk | Credit Applications, Scoring History, Default Records, Alternative Data (Utility/Rent) | Sarah Chen / Dr. Nina Kowalski | CreditRisk-XGB v1.0 training set; Adverse Action RAG knowledge base; Credit features in Feast | S3://credit-domain/ + Feast:credit-features + Weaviate:credit-kb | 98.7% completeness; lineage 100% coverage |
| Customer | CRM records, Interaction History, Segment Data, Consent Records | Lena Hoffmann / Domain Data Owner | CSCopilot RAG knowledge base; Customer segment features | S3://customer-domain/ + Weaviate:customer-kb | 97.2%; GDPR consent tracking automated |
| Operations | Ticket Data, Process Logs, SLA Records, Agent Interaction Logs | Ops VP / Domain Data Owner | Operations knowledge base for Copilot; Process optimisation features | S3://ops-domain/ + Weaviate:ops-kb | 94.1%; freshness SLA 2h |
| Security | Transaction Logs, Fraud Labels, Anomaly Patterns, Network Logs | John Kim / Domain Data Owner | FraudDet-ENS v3.1 training; real-time feature feed | S3://security-domain/ + Feast:fraud-features (real-time) | 99.3%; p99 freshness &lt;5min (critical) |
| Marketing | Campaign Data, Response Rates, Channel Attribution, Consent | Marketing VP / Domain Data Owner | Campaign Targeting AI training set; segment propensity features | S3://marketing-domain/ + Feast:mkt-features | 95.8%; GDPR consent flag mandatory |
| HR | Job Postings, CV Pool (anonymised), Assessment Data, Outcome Labels | Maria Santos / Domain Data Owner | CV Screening AI (ON HOLD — FRIA pending); Workforce planning features | S3://hr-domain/ (restricted access) | RESTRICTED; FRIA must complete before AI use |

### Vector Database Architecture

**VDA-001** (AI-First Extension)

Owner: Data Architect + AI Architect | ADM Phase: C1 | TOGAF 10 + AI-First Extension

| **Platform Selected** | *Weaviate (self-hosted on AKS) — selected over Pinecone (lock-in risk) and Azure AI Search (limited OSS portability). See ADR: EA-C1-VDA-001.* |
|---|---|
| **Embedding Models** | *text-embedding-3-large (OpenAI) for knowledge bases; domain-specific fine-tuned E5-large for credit/regulatory content. All models versioned in MLflow.* |
| **Namespace Architecture** | *One Weaviate namespace per domain-use-case: credit-kb, customer-kb, ops-kb, regulatory-kb (shared), code-kb (IT). Namespace isolation enforces data product boundaries.* |
| **Access Control** | *Weaviate API key per consuming service. Agent access requires scoped API key registered in HashiCorp Vault. No cross-namespace access without ARB approval.* |
| **Freshness SLA** | *credit-kb: ≤4 hours. regulatory-kb: ≤1 hour (regulatory changes are time-sensitive). All others: ≤8 hours. Freshness monitored in Datadog; breach triggers P2 alert.* |
| **Embedding Drift Monitoring** | *Weekly cosine similarity baseline check across namespaces. &gt;10% average cosine drift triggers embedding model review and potential re-embedding. Monitored via Arize AI.* |
| **GDPR Deletion Capability** | *Weaviate supports object-level deletion by UUID. DPO-triggered PII deletion workflows documented and tested. 72-hour deletion SLA from subject access request.* |
| **EU AI Act Evidencing** | *Embedding model versions stored in MLflow with training data provenance. Namespace contents versioned with DVC. Full lineage from source document to vector queryable via OpenLineage.* |

---

## TOGAF ADM Application Architecture Phase C2

**ARTIFACTS: LLMG-001 · AOB-001 · CSD-001 · ASAP-001**

### LLM Gateway Architecture

**LLMG-001** (AI-First Extension)

Owner: AI Architect + Security Architect | ADM Phase: C2 | TOGAF 10 + AI-First Extension

This AI-First extension is the mandatory control plane for ALL LLM API calls within GlobalBank. No LLM call may bypass the gateway. This is the application-layer equivalent of the network security perimeter for AI traffic.

| **Platform** | *Kong AI Gateway (enterprise licence) — deployed on AKS in GlobalBank's Azure subscription* |
|---|---|
| **Model Routing** | *LiteLLM abstraction layer behind Kong. Routes to: Azure OpenAI (primary), Anthropic Claude via Bedrock (secondary), Llama 3 (self-hosted, sensitive data). Failover automatic.* |
| **Mandatory Controls** | *Every LLM call through gateway must pass: (1) Prompt injection detection (Lakera Guard API). (2) PII masking (Presidio). (3) Content safety filter (Azure AI Content Safety). (4) Token budget enforcement. (5) Audit log write.* |
| **Rate Limiting** | *Per-service rate limits: Credit scoring LLM = 500 RPM. Customer Copilot = 2000 RPM. Developer Copilot = 5000 RPM. Burst: 2× sustained for 60s. Exceeding burst → 429 + alert.* |
| **Audit Logging** | *100% of LLM requests logged to Splunk: service ID, model, token count, latency, safety score, redacted prompt summary. PII-free log. Immutable append-only. Retained 7 years (FCA).* |
| **Cost Attribution** | *Every LLM call tagged with: cost-centre, use-case-ID, model-version, environment. FinOps dashboard in Azure Cost Management. Weekly cost report to business owners.* |
| **Response Caching** | *Semantic caching enabled for deterministic queries (e.g., regulatory Q&amp;A). Cache TTL = 4 hours. Cache hit rate target &gt;30% to reduce costs. Privacy: cached responses never contain PII.* |

### Agent Orchestration Blueprint

**AOB-001** (AI-First Extension)

Owner: AI Architect | ADM Phase: C2 | TOGAF 10 + AI-First Extension

| **Orchestration Framework** | *LangGraph (primary for stateful multi-step agents) + LangChain (for RAG chains). AutoGen reserved for experimental multi-agent workflows pending governance maturity.* |
|---|---|
| **Integration Protocol** | *Model Context Protocol (MCP) as the standard for agent-to-enterprise-service integration. All enterprise APIs exposed via MCP servers to agents. No direct REST calls from agents.* |
| **Agent Identity Model** | *Each agent has a dedicated service identity in Azure Managed Identity. Agent identity is SEPARATE from human IAM. Agent credentials are short-lived (15-min TTL). Stored in HashiCorp Vault.* |
| **Action Boundaries** | *Agent action boundaries defined in Agent Action Boundary Register (AABR-001-EA). Enforced at runtime by OPA (Open Policy Agent) sidecar on each agent pod. Violations logged and alerted.* |
| **ATF Trust Levels** | *Agents are assigned ATF trust levels 0–4 by the AI Governance Council. Promotion requires: demonstrated accuracy over evaluation period, security audit, clean operational history, explicit stakeholder approval.* |
| **Memory Architecture** | *Working memory: in-context (per session, ephemeral). Episodic memory: Redis (session history, 24h TTL). Semantic memory: Weaviate vector store (persistent, access-controlled). No unlimited persistent memory.* |
| **Circuit Breakers** | *All agents wrapped with Resilience4j circuit breaker. If error rate &gt;5% in 60s window → circuit opens, agent paused, P1 alert. Prevents runaway agent cascades.* |

### Agent-Safe API Design Pattern

**ASAP-001** (AI-First Extension)

Owner: Solution Architect | ADM Phase: C2 | TOGAF 10 + AI-First Extension

| **Design Requirement** | **Standard** | **Example Implementation** |
|---|---|---|
| Idempotency | All state-changing endpoints MUST be idempotent (safe to retry). Idempotency key in header. | POST /decisions: X-Idempotency-Key: {uuid} prevents duplicate credit decisions on agent retry |
| Semantic Versioning in Metadata | API version communicated in response metadata, not just URL. Allows agents to self-discover deprecation. | Response header: X-API-Version: 2.3.1, X-API-Deprecation-Date: 2027-01-01 |
| Action Documentation | Every state-changing endpoint documents: action type (reversible/irreversible), scope of impact, human approval requirement. | POST /decisions: {"reversible": false, "scope": "customer-credit-file", "hitl_required": true} |
| Burst Rate Limits | Agent-specific rate limits documented in API spec. Differentiated from human user limits. Exponential backoff required. | Agent client: burst 500 RPM sustained 200 RPM. Retry-After header provided on 429. |
| Webhook Callbacks | Long-running operations return 202 + callback URL. Agents register webhook endpoint. No synchronous waiting. | POST /model-retraining → 202 {callbackUrl: "/retrain-status/{job-id}"} |
| Dry-Run Mode | Irreversible operations support ?dryRun=true parameter for agent testing without side effects. | DELETE /model-version?dryRun=true → returns what would happen, no deletion |
| Audit Trail in Response | Every state-changing response includes audit trail ID for traceability from agent action to business outcome. | Response: {"auditId": "AUD-2026-FIN-048371", "agentId": "AGT-OPS-001"} |

---

## Related

- [../03-aidlc-artifacts-togaf-foundation-to-technology.md](../03-aidlc-artifacts-togaf-foundation-to-technology.md) — Part 1: Preliminary Phase
- [./05-aidlc-artifacts-togaf-vision-business-architecture.md](./05-aidlc-artifacts-togaf-vision-business-architecture.md) — Part 2: Vision &amp; Business Architecture (Phase A-B)
- [./07-aidlc-artifacts-togaf-technology-architecture.md](./07-aidlc-artifacts-togaf-technology-architecture.md) — Part 4: Technology Architecture (Phase D)
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — AIDLC Phases 1–4 artifact templates
- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — AIDLC Phases 5–8 artifact templates
- [../04-aidlc-artifacts-togaf-migration-to-ea.md](../04-aidlc-artifacts-togaf-migration-to-ea.md) — TOGAF ADM Migration through EA Cross-Cutting artifacts

## Sources

None currently documented.
