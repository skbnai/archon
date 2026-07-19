---
title: "AI Platform Operating Model"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-07-platform-operating-model
maturity: practitioner
personas: [cto, platform-lead, architecture-lead]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-07-platform-operating-model.md
tags: ["ai-platform", "platform-engineering", "self-service-ai", "agent-platform", "inference-platform", "developer-experience"]
sources: []
---

# AI Platform Operating Model

An enterprise AI platform is the shared infrastructure layer enabling every team to build, deploy, operate, and govern AI capabilities without reinventing core components. It is analogous to the cloud platform but purpose-built for AI workloads.

## What a Mature AI Platform Provides

- **Self-service access** to AI capabilities via APIs and developer portals
- **Shared infrastructure** (inference, embedding, vector stores, memory)
- **Governance guardrails** baked into platform (guardrails, policy enforcement, audit logging)
- **Observability** across all AI usage enterprise-wide
- **Cost management** with metered consumption and chargeback
- **Developer experience** (SDKs, documentation, onboarding support)

## Platform Architecture Layers

**Developer Experience Layer:** Developer portal, SDKs, self-service APIs

**Application Services:** Agent runtime, workflow orchestration, memory service, tool registry

**Governance Services:** Guardrail service, policy engine, evaluation service, content moderation

**Observability Services:** Logging, tracing, AI observability dashboards, FinOps

**Knowledge Layer:** Knowledge service, vector databases, context service, document processing

**Foundation Layer:** Inference service, embedding service, model registry, fine-tuning service

**Security Layer:** AI identity (SPIFFE/SPIRE), secrets service, prompt service

**Infrastructure Layer:** GPU clusters, cloud AI services, hardware management

For the full service specification, see Part 10 (AI Service Catalog).

## Platform Team Structure

**Foundation Platform Squad:** Inference service, model routing, GPU management, model registry

**Knowledge Platform Squad:** RAG service, vector databases, document processing, context service

**Agent Platform Squad:** Agent runtime, memory service, tool registry, workflow orchestration

**Governance & Security Squad:** Guardrails, policy engine, content moderation, AI identity

**Observability & FinOps Squad:** Logging, tracing, AI observability dashboards, cost management

**Developer Experience Squad:** Developer portal, SDKs, documentation, onboarding

## Platform Team Responsibilities

| Responsibility | Description |
|---|---|
| **Build & operate shared services** | Own every service in the Service Catalog |
| **Define standards** | API design, security standards, observability requirements |
| **Enable self-service** | Developer portal, self-service provisioning, documentation |
| **Enforce governance** | Guardrails, policy engine, audit logging built into platform |
| **Manage costs** | FinOps tooling, cost attribution, optimization recommendations |
| **Drive adoption** | Onboarding programmes, developer advocacy, inner-source community |
| **Vendor management** | LLM providers, vector DB vendors, inference hardware |

## Build vs Buy Decision

| Factor | Build Internal Platform | Use External Cloud Services |
|---|---|---|
| Governance control | High; enterprise-specific requirements | Standard cloud controls |
| Multi-cloud portability | Critical | Not required |
| Cost optimization | Centrally managed across enterprise | Per-team responsibility |
| Custom guardrails | Required | Standard moderation sufficient |
| Team size | >10 AI teams (scale economies) | &lt;5 AI teams (speed) |
| Implementation | Build (lower per-team cost at scale) | Buy as-a-service (fast time-to-value) |

**Recommendation:** Enterprises with >10 AI teams benefit from internal platform. Below that, direct cloud services + lightweight governance is more cost-effective.

## Platform Maturity Levels

| Level | Platform Capability | Self-Service | Governance |
|---|---|---|---|
| **L1 — Ad Hoc** | Direct LLM API access per team | No | Manual |
| **L2 — Shared Gateway** | AI gateway with rate limiting, logging, cost tracking | Partial | API key + audit log |
| **L3 — Managed Services** | Inference, embedding, RAG as managed services | Yes (API) | Guardrails + policy |
| **L4 — Full Platform** | All services in catalogue; developer portal | Yes (portal) | Full automated governance |
| **L5 — AI-Native** | Platform is the AI operating fabric | Native | Constitutional |

## Key Design Principles

1. **Self-service over gated requests** — Teams should provision AI capability without raising tickets
2. **Governance by design** — Guardrails, logging, policy enforcement automatic, not optional
3. **Abstraction over lock-in** — Platform abstracts underlying LLM vendor; swap vendors without changing APIs
4. **Metered consumption** — Every API call attributed to team and use case for cost visibility
5. **Developer experience first** — If developers don't love using the platform, they work around it

## Cloud Platform Mapping

| Component | AWS | Azure | GCP |
|---|---|---|---|
| Inference | Bedrock + API Gateway | Azure OpenAI + APIM | Vertex AI + API Gateway |
| Agent Runtime | Bedrock AgentCore | Azure AI Foundry | Vertex AI Agents |
| Vector Database | OpenSearch / Pinecone | Azure AI Search | Vertex AI Vector Search |
| Knowledge Service | Bedrock Knowledge Bases | Azure AI Search + OpenAI | Vertex AI RAG |
| Workflow | Step Functions / Temporal | Logic Apps | Cloud Workflows |
| Observability | CloudWatch + X-Ray | Azure Monitor | Cloud Trace + Monitoring |
| FinOps | Cost Explorer + Bedrock metrics | Azure Cost Management | Cloud Billing + Vertex metrics |
| Guardrails | Bedrock Guardrails | Azure Content Safety | Vertex AI Safety |
| AI Identity | IAM Roles / Cognito | Entra ID Managed Identity | Service Accounts |

## Platform Success Metrics

- **Adoption:** % of AI teams consuming platform services
- **Throughput:** AI use cases deployed per month via platform
- **Cycle time:** Days from request to service provisioning
- **Cost savings:** Cost per AI use case vs. pre-platform baseline
- **Compliance:** % deployments passing governance gate on first submission
- **Developer satisfaction:** NPS for platform developer experience

## Platform Operating Model Maturity

**Level 1 (Ad Hoc):** No centralized platform; teams implement their own integration; high duplication, inconsistent quality.

**Level 2 (Emerging):** Lightweight shared gateway for LLM access; no advanced services; manual governance.

**Level 3 (Scaling):** Managed services for core AI capabilities (inference, embedding, RAG); basic governance; partial self-service.

**Level 4 (Optimized):** Full self-service platform; all services in catalogue; automated governance; cost transparency; strong adoption.

**Level 5 (AI-Native):** Platform is the operating fabric; every team uses it; governance is constitutional; competitive advantage through platform.

## Deep-Dive Resources

- [Operating Models](12-part-02-operating-models.md) — Operating model for platform team
- [AI Service Catalog](20-part-10-service-catalog.md) — Full service specifications
- [DevSecOps](21-part-11-devsecops.md) — DevSecOps for platform itself
- [Observability](24-part-14-observability.md) — Platform observability

## Related

- [AI Delivery Lifecycle](13-part-03-ai-delivery-lifecycle.md)
- [Governance Model](16-part-06-governance.md)
- [Organizational Roles](18-part-08-organizational-roles.md)

## Sources

