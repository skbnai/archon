---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-information-systems-architecture
title: "APEX EA Part 3: Information Systems & Technology Architecture"
date_created: 2026-04-01
last_reviewed: 2026-07-23
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 3 information systems technology architecture
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part3_Information_Systems_Technology_Architecture.md
tags:
  - enterprise-architecture
  - specialization
  - togaf
  - data-architecture
  - technology-architecture
  - cloud-native
---

# APEX EA Part 3: Information Systems & Technology Architecture

Continues from [Part 2: AI-DLC Methodology & Foundation Architecture](./10-apex-ea-aidlc-methodology.md). This part covers TOGAF Phases C and D — data, AI-native entities, application components, and cloud-native infrastructure.

## Information Systems Architecture (Phase C)

**PHASE C** — Data, AI-native entities, application components, and API catalogue

### Data Classification Framework

| Class | Description | Examples | Guardrail Action | Retention |
| --- | --- | --- | --- | --- |
| C4 — Highly Restricted | PII and highly sensitive data | Government IDs, account numbers, biometrics | BLOCK or ANONYMIZE in all agent logs and traces | 7 years (DORA mandate) |
| C3 — Confidential | Sensitive internal business data | Proprietary models, strategic risk parameters | Redact in all observability traces and log exports | 5 years |
| C2 — Internal | Non-sensitive operational data | Agent performance metrics, usage statistics | Standard structured logging | 3 years |
| C1 — Public | Regulatory and market reference data | EU AI Act text, public rates, open standards | No restriction | Indefinite |
| C-AI — AI Assets | Prompt catalogs, embeddings, feedback logs, model lineage | Versioned prompt templates, vector embeddings, RLHF datasets | Inherit from source data class; version-controlled; DPO sign-off for C3/C4-adjacent | Per source data class rules |

### AI-Native Data Entities — Governance Model

| Entity | Classification | Governance Owner | Version Control | Key Control | Retention |
| --- | --- | --- | --- | --- | --- |
| Prompt Catalog | C-AI | Platform AI Eng + DPO | Git semver; PR mandatory | Prompt change triggers full regression test suite before merge | Per source data class |
| Embedding Store | C-AI | Data Mesh Domain Owner | Embedding model ID + version in data catalog metadata | Embedding Compatibility Contract: RAGAS gate on model upgrade; 90-day rollback | 90 days post-supersession |
| RAG Retrieval Log | C2–C4 inherit | Compliance + Audit | Immutable; object lock; append-only | Queryable by compliance team within 60 seconds; feeds DEA assembly | 7 years (DORA) |
| Feedback Log | C2–C4 inherit | Model Risk Management | Immutable; object lock; append-only | Drives model drift detection; feeds Model Monitoring Agent (Pioneer 5) | 7 years (DORA) |
| Agent Memory | Inherits source class | Platform Eng + DPO | TTL enforced in KV store; max 30 minutes | PII check on every write; TTL enforced at gateway; no persistence after session | Session TTL only |
| Model Lineage Record | C3 | Model Risk Management | ML model registry (MLflow equivalent) | New model version = formal model update event requiring ARB record | Model lifecycle + 7 years |
| Decision Explanation Artefact | C3 | Compliance + Legal | Generated at decision time; immutable; DEA service validates completeness | Assembled from all log sources; queryable on demand; 7-year immutable retention | 7 years (EU AI Act + DORA) |

### Application Architecture — Cloud-Native Component Model

| Component | Technology | Pattern | SLA | Key Design Decision |
| --- | --- | --- | --- | --- |
| APEX Developer Portal | React SPA + API Gateway (Kong/Nginx/cloud-native) | Backend-for-Frontend (BFF) | 99.9% / p99 &lt;500ms | Agent health score and DEA query link visible per agent; AI-DLC scaffolds UI in 1 bolt |
| APEX Control Plane | Python FastAPI; Kubernetes OCI containers; 6 microservices | Microservices — bounded contexts | 99.9% / p99 &lt;500ms | Agent Lifecycle, Budget Enforcer, Onboarding Orchestrator, Chargeback, Notification, Compliance Reporter services |
| Agent Gateway | Envoy proxy + custom plugin OR APISIX + plugin | Zero-trust entry point; registry lookup; budget throttle | 99.99% / p99 &lt;50ms | Blocks unregistered agents (403); enforces budget hard-throttle at 110%; logs all agent dependency calls |
| Agent Orchestration Engine | LangGraph / AutoGen / CrewAI OR cloud-managed equivalent (evaluated in WP-002 spike) | Supervisor-Worker multi-agent pattern | 99.95% / p99 &lt;3s | All routing decisions logged to OpenTelemetry trace for DEA assembly; abstraction layer prevents framework lock-in |
| Serverless Tool Functions | Knative / OpenFaaS / cloud FaaS (OCI container-based) | Action Group / Tool Sidecar pattern | 99.95% / p99 &lt;1s | Each function passes L1–L5 verification; tool invocation logs written to structured log for DEA |
| DEA Generation Service | Python event-driven service; Kubernetes; triggered on regulated decision | Event-driven async; completeness validation before store | 99.9% / &lt;5s | Assembles DEA from all log sources; validates completeness; stores immutably; queryable via DEA API |
| Human Review Portal | React + Temporal / Camunda workflow engine | Human-in-the-Loop (HITL) review workflow | 99.5% / SLA defined per agent risk tier | HITL outcome written to DEA; DEA marked complete only after HITL where required by risk classification |
| LGTM Observability Stack | OpenTelemetry Collector + Prometheus + Grafana + Loki + Tempo | Centralised OTEL collector; push-based metrics and traces | 99.5% ingestion; real-time dashboards | Agent health score metrics; emergent behaviour alert rules (chain >3 hops or latency >10s) |
| Compliance Reporter | Python data pipeline + Apache Superset or Metabase | Batch + event-driven reporting | 99.5% daily run | EU AI Act and DORA report templates; DORA change record auto-writer; DEA export API |

### API Catalogue

| API | Version | Style | Auth | SLA | Owner |
| --- | --- | --- | --- | --- | --- |
| Agent Registry API | v2 | REST / OpenAPI 3.1 | OAuth 2.0 (APEX scope) | 99.9% / p99 &lt;200ms | Platform Eng |
| Agent Invocation API | v1 | REST + SSE streaming | IAM / mTLS | 99.95% / p99 &lt;3s | Platform Eng |
| Knowledge Base API | v1 | REST / JSON | IAM / mTLS | 99.9% / p99 &lt;500ms | AI/ML Eng |
| Onboarding API | v1 | REST / JSON | OAuth 2.0 | 99.5% / p99 &lt;1s | Platform Eng |
| DEA Query API | v1 | REST / JSON | OAuth 2.0 + MFA | 99.9% / &lt;60s response | Compliance |
| Chargeback API | v1 | REST / JSON | mTLS | 99.9% monthly run | SRE / FinOps |
| Compliance Report API | v1 | REST / JSON | OAuth 2.0 + MFA | 99.5% daily run | Compliance |

### APEX Cloud-Native Technology Stack

```mermaid
graph TB
    subgraph "External Systems"
        LLM["Foundation Models<br/>(Claude, GPT-4o, Gemini)"]
        DataMesh["Data Mesh<br/>(Source Systems)"]
    end
    
    subgraph "APEX Platform"
        Gateway["Agent Gateway<br/>(Envoy/APISIX)"]
        ControlPlane["Control Plane<br/>(FastAPI Services)"]
        Orchestration["Agent Orchestration<br/>(LangGraph/AutoGen)"]
        KB["Knowledge Base<br/>(Vector Store)"]
        DEA["DEA Generation<br/>Service"]
        Portal["Developer Portal<br/>(React SPA)"]
    end
    
    subgraph "Observability & Governance"
        OTEL["OpenTelemetry<br/>Collector"]
        Prom["Prometheus"]
        Grafana["Grafana"]
        Logs["Loki/OpenSearch"]
        Compliance["Compliance Reporter"]
    end
    
    subgraph "Infrastructure"
        K8s["Kubernetes Cluster<br/>(Multi-region)"]
        Vault["Vault<br/>(Secrets)"]
        DB["PostgreSQL<br/>(Control Plane)"]
    end
    
    LLM -->|API Call| Gateway
    DataMesh -->|Data Ingest| KB
    Gateway -->|Route| ControlPlane
    ControlPlane -->|Orchestrate| Orchestration
    Orchestration -->|RAG Query| KB
    ControlPlane -->|Generate| DEA
    Portal -->|API Call| ControlPlane
    Gateway -->|Emit Trace| OTEL
    Orchestration -->|Emit Trace| OTEL
    OTEL -->|Scrape| Prom
    OTEL -->|Ingest| Logs
    Prom -->|Display| Grafana
    DEA -->|Report| Compliance
    ControlPlane -->|Secrets| Vault
    ControlPlane -->|Store| DB
    K8s -.->|Runtime| Gateway
    K8s -.->|Runtime| ControlPlane
    K8s -.->|Runtime| Orchestration
    K8s -.->|Runtime| Portal
    
    style Gateway fill:#e3f2fd
    style ControlPlane fill:#c8e6c9
    style Orchestration fill:#fff9c4
    style KB fill:#f8bbd0
    style DEA fill:#e1bee7
    style Portal fill:#c0caf5
```

**APEX integrates foundation models via provider-agnostic adapter, routes agents through zero-trust gateway, orchestrates multi-agent workflows, and feeds all decision context into DEA assembly and compliance reporting.**

## Technology Architecture (Phase D)

**PHASE D** — Cloud-native infrastructure, security, CI/CD with Layered Verification

### Multi-Region Deployment Model

| Region | Role | Data Scope | Key Platform Services | Regulatory Basis |
| --- | --- | --- | --- | --- |
| Region 1 — Primary (EU/UK) | ACTIVE PRIMARY | EU/UK personal + sensitive data | Kubernetes cluster (multi-AZ); LGTM stack; agent gateway; vector store; PostgreSQL multi-AZ; Kafka; Vault; object storage (WORM) | GDPR, UK GDPR, DORA |
| Region 2 — DR (EU) | STANDBY / FAILOVER | DR replica only; no new data processing | Kubernetes cluster (standby); object storage (CRR target); DB replica | DORA Art.11 ICT resilience; GDPR Art.32 |
| Region 3 — Americas | ACTIVE | US/LATAM institutional + customer data | Mirror of Region 1 topology; independent control plane and agent gateway | CCPA, LGPD, FINRA (where applicable) |
| Region 4 — APAC | ACTIVE | SG/HK/AU customer data | Mirror of Region 1 topology; regional vector store; local object storage | PDPA (SG), PIPL (CN), Privacy Act (AU) |

### Security Architecture

| Security Domain | Control | Cloud-Native Implementation | Compliance Basis |
| --- | --- | --- | --- |
| Identity & Access | Zero-trust; OIDC federation; short-lived credentials for all service accounts | Service mesh mTLS (Istio/Linkerd); Kubernetes RBAC; OIDC-based identity federation | NIST SP 800-207, DORA Art.9 |
| Encryption at Rest | AES-256; customer-managed keys; separate CMK per data classification | HashiCorp Vault or cloud KMS; 365-day automatic key rotation enforced | GDPR Art.32, ISO 27001 |
| Encryption in Transit | TLS 1.3 minimum; mTLS between all internal services | Istio/Linkerd service mesh enforces mTLS; ingress enforces TLS 1.3 minimum externally | FIPS 140-2, DORA |
| Network Isolation | Zero-trust NetworkPolicy; no public internet egress from agent runtime pods | Kubernetes NetworkPolicy; egress via controlled proxy; PrivateLink-equivalent for cloud API calls | TP-01, Security Policy |
| Agent Safety | Content guardrail layer; grounding threshold 0.75; PII anonymisation | NeMo Guardrails or Guardrails AI; integrated in agent invocation path before output to caller | EU AI Act Art.9, BP-02 |
| IaC Security | L1 static analysis on every commit; no merge on any HIGH or CRITICAL finding | Checkov + Semgrep + Trivy in CI; Falco at runtime; OWASP Dependency Check | CIS Kubernetes, DORA |
| Prompt Injection | Input sanitisation and validation on all agent inputs before model invocation | Validation middleware in agent gateway; OWASP LLM Top 10 controls; red-team testing quarterly | OWASP LLM Top 10 |
| Secrets Management | All secrets in secrets manager; zero hardcoded credentials; 90-day rotation | HashiCorp Vault or cloud-native secrets manager; Checkov enforces in CI | CIS Kubernetes, DORA |

### CI/CD Pipeline — Layered Verification Model (L1–L5)

| Stage | Tools | AI-DLC Role | Gate — Bypassable? |
| --- | --- | --- | --- |
| L1 Static Analysis | Checkov, Semgrep, Trivy, KICS, yamllint | AI explains failures and proposes fixes; cannot self-approve | NEVER — pipeline blocks merge; no override path exists |
| L2 AI Explanation Artefact | AI coding assistant; explanation stored as PR artefact (12 months) | AI explains every generated block before engineer approval; explanation is retained | NEVER — engineer confirms AI explanation before approving |
| L3 Property Tests | Terratest, pytest-infra, contract tests | AI generates test bodies; engineer writes property assertions that define correctness | NEVER — 100% pass required |
| RAGAS Evaluation Gate | RAGAS eval suite; custom GlobalCorp eval harness | AI generates adversarial test cases; regression scored against baseline | NEVER — >90% score required; regression blocks merge |
| Guardrail Test Suite | NeMo Guardrails test harness; adversarial prompt library | AI generates edge-case and adversarial prompts to test guardrail coverage | NEVER — 100% pass required |
| T4 Model Risk Gate | Ticket-based approval workflow (Jira / Linear / equivalent) | AI generates Model Risk evidence pack draft; Model Risk Lead reviews and signs | NEVER — human sign-off mandatory; T4 Reg-Gate; no automation path |
| L4 Canary Deploy | Argo Rollouts / Flagger; Prometheus SLO monitoring | AI monitors SLOs in real time; triggers automatic rollback on breach | SRE Lead override only; every override logged with justification |
| DEA Validation | DEA generation service completeness check; validation before production mark | DEA assembled from all log sources; completeness validated | NEVER for High-Risk AI agents |
| Post-Deploy DORA Record | Argo CD drift detection; cost tag validator; DORA change record writer | AI generates stakeholder summary; DORA change record auto-created with ARB reference | NEVER — records are mandatory; absence triggers T4 alert |

---

**Next:** [Part 4 — Delivery, Governance & Reference](./12-apex-ea-delivery-governance-reference.md) covers the roadmap, migration strategy, 5-tier governance model, requirements traceability, and regulatory/service-mapping/glossary reference material.
