---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-information-systems-architecture
title: "APEX EA Part 3: Information Systems & Technology Architecture"
date_created: 2026-04-01
last_reviewed: 2026-07-17
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 3 information systems technology architecture
  - information systems architecture phase c
  - technology architecture phase d
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part3_Information_Systems_Technology_Architecture.md
tags:
  - enterprise-architecture
  - specialization
  - togaf
  - information-systems
  - technology-architecture
  - cloud-native
---

# APEX EA Part 3: Information Systems & Technology Architecture

Part 3 of the APEX EA 4-part blueprint. Continues from [Part 2: AI-DLC Methodology & Foundation Architecture](./10-apex-ea-aidlc-methodology.md); next is [Part 4: Delivery, Governance & Reference](./12-apex-ea-delivery-governance-reference.md).

## Information Systems Architecture (Phase C)

### Data Classification Framework

| Class | Description | Examples | Guardrail Action | Retention |
|---|---|---|---|---|
| **C4** | Highly Restricted | Government IDs, account numbers, biometrics | BLOCK or ANONYMIZE in logs/traces | 7 years (DORA) |
| **C3** | Confidential | Proprietary models, strategic risk parameters | Redact in observability/log exports | 5 years |
| **C2** | Internal | Agent metrics, usage statistics | Standard structured logging | 3 years |
| **C1** | Public | EU AI Act text, public rates, open standards | No restriction | Indefinite |
| **C-AI** | AI Assets | Prompt catalogs, embeddings, feedback logs, model lineage | Inherit from source data class; version-controlled; DPO sign-off | Per source data class |

### AI-Native Data Entities — Governance Model

| Entity | Classification | Governance Owner | Version Control | Key Control | Retention |
|---|---|---|---|---|---|
| **Prompt Catalog** | C-AI | Platform AI Eng + DPO | Git semver | Change triggers regression test suite | Per source data class |
| **Embedding Store** | C-AI | Data Mesh Owner | Embedding model ID + version | Compatibility Contract; RAGAS gate on upgrade | 90 days post-supersession |
| **RAG Retrieval Log** | C2–C4 inherit | Compliance + Audit | Immutable; object lock; append-only | Queryable within 60 seconds | 7 years (DORA) |
| **Feedback Log** | C2–C4 inherit | Model Risk Management | Immutable; object lock; append-only | Drives model drift detection | 7 years (DORA) |
| **Agent Memory** | Inherits source class | Platform Eng + DPO | TTL enforced; max 30 minutes | PII check on write; TTL at gateway | Session TTL only |
| **Model Lineage Record** | C3 | Model Risk Management | ML registry (MLflow) | New version = formal model update event | Model lifecycle + 7 years |
| **Decision Explanation Artifact** | C3 | Compliance + Legal | Generated at decision time; immutable | Assembled from all log sources; 7-year immutable retention | 7 years (EU AI Act + DORA) |

### Application Architecture — Cloud-Native Component Model

| Component | Technology | Pattern | SLA | Key Design Decision |
|---|---|---|---|---|
| **APEX Developer Portal** | React SPA + API Gateway | Backend-for-Frontend (BFF) | 99.9% / p99 <500ms | Agent health score and DEA query visible per agent |
| **Control Plane** | Python FastAPI; K8s OCI | Microservices—bounded contexts | 99.9% / p99 <500ms | 6 services: Agent Lifecycle, Budget Enforcer, Onboarding, Chargeback, Notification, Compliance Reporter |
| **Agent Gateway** | Envoy proxy + plugin OR APISIX | Zero-trust entry point; registry lookup; budget throttle | 99.99% / p99 <50ms | Blocks unregistered agents (403); enforces hard budget throttle at 110% |
| **Agent Orchestration** | LangGraph / AutoGen / CrewAI | Supervisor-Worker multi-agent | 99.95% / p99 <3s | All routing decisions logged to OpenTelemetry; abstraction layer prevents framework lock-in |
| **Tool Functions** | Knative / OpenFaaS | Action Group / Tool Sidecar | 99.95% / p99 <1s | Each function passes L1–L5 verification; tool logs written to structured log for DEA |
| **DEA Generation** | Python event-driven service; K8s | Event-driven async | 99.9% / <5s | Assembles from all log sources; validates completeness; immutably stored |
| **Human Review Portal** | React + Temporal/Camunda | Human-in-the-Loop workflow | 99.5% | HITL outcome written to DEA; marked complete post-review |
| **Observability Stack** | OTel Collector + Prometheus + Grafana + Loki + Tempo | Centralized collection; push-based metrics/traces | 99.5% ingestion | Agent health metrics; emergent behavior alerts (chain >3 hops or latency >10s) |
| **Compliance Reporter** | Python pipeline + Superset/Metabase | Batch + event-driven reporting | 99.5% daily | EU AI Act and DORA templates; DORA change record auto-writer |

### API Catalog

| API | Version | Style | Auth | SLA | Owner |
|---|---|---|---|---|---|
| Agent Registry API | v2 | REST / OpenAPI 3.1 | OAuth 2.0 | 99.9% / p99 <200ms | Platform Eng |
| Agent Invocation API | v1 | REST + SSE streaming | IAM / mTLS | 99.95% / p99 <3s | Platform Eng |
| Knowledge Base API | v1 | REST / JSON | IAM / mTLS | 99.9% / p99 <500ms | AI/ML Eng |
| DEA Query API | v1 | REST / JSON | OAuth 2.0 + MFA | 99.9% / <60s response | Compliance |
| Chargeback API | v1 | REST / JSON | mTLS | 99.9% monthly | SRE / FinOps |

---

## Technology Architecture (Phase D)

### Multi-Region Deployment Model

| Region | Role | Data Scope | Platform Services | Regulatory Basis |
|---|---|---|---|---|
| **Region 1 — Primary (EU/UK)** | ACTIVE PRIMARY | EU/UK personal + sensitive | K8s multi-AZ; LGTM stack; agent gateway; vector store; PostgreSQL multi-AZ; Kafka; Vault; object storage (WORM) | GDPR, UK GDPR, DORA |
| **Region 2 — DR (EU)** | STANDBY / FAILOVER | DR replica only | K8s standby; object storage (CRR); DB replica | DORA Art.11 ICT resilience |
| **Region 3 — Americas** | ACTIVE | US/LATAM data | Mirror of Region 1; independent control plane, agent gateway | CCPA, LGPD, FINRA |
| **Region 4 — APAC** | ACTIVE | SG/HK/AU data | Mirror of Region 1; regional vector store, local storage | PDPA (SG), PIPL (CN), Privacy Act (AU) |

### Security Architecture

| Security Domain | Control | Cloud-Native Implementation | Compliance Basis |
|---|---|---|---|
| **Identity & Access** | Zero-trust; OIDC federation; short-lived credentials | Service mesh mTLS; K8s RBAC; OIDC federation | NIST SP 800-207, DORA Art.9 |
| **Encryption at Rest** | AES-256; customer-managed keys; separate CMK per data class | HashiCorp Vault or cloud KMS; 365-day auto rotation | GDPR Art.32, ISO 27001 |
| **Encryption in Transit** | TLS 1.3 minimum; mTLS between services | Istio/Linkerd service mesh; ingress enforces TLS 1.3 | FIPS 140-2, DORA |
| **Network Isolation** | Zero-trust NetworkPolicy; no public internet egress | K8s NetworkPolicy; egress via controlled proxy; PrivateLink-equivalent | TP-01, Security Policy |
| **Agent Safety** | Content guardrail layer; grounding threshold 0.75; PII anonymization | NeMo Guardrails or Guardrails AI; integrated pre-output | EU AI Act Art.9, BP-02 |
| **IaC Security** | L1 static analysis on every commit; no merge on HIGH/CRITICAL | Checkov + Semgrep + Trivy; Falco runtime; OWASP Dependency Check | CIS Kubernetes, DORA |
| **Prompt Injection** | Input sanitization on all agent inputs before model | Validation middleware in agent gateway; OWASP LLM Top 10; quarterly red-team | OWASP LLM Top 10 |
| **Secrets Management** | All secrets in secrets manager; zero hardcoded credentials; 90-day rotation | HashiCorp Vault or cloud-native; Checkov enforces in CI | CIS Kubernetes, DORA |

### CI/CD Pipeline — Layered Verification Model (L1–L5)

| Stage | Tools | AI-DLC Role | Gate — Bypassable? |
|---|---|---|---|
| **L1 Static Analysis** | Checkov, Semgrep, Trivy, KICS, yamllint | AI explains failures; proposes fixes; cannot self-approve | NEVER — no override path |
| **L2 AI Explanation Artefact** | AI coding assistant; stored 12 months | AI explains every generated block; engineer approves before merge | NEVER — engineer confirms before approving |
| **L3 Property Tests** | Terratest, pytest-infra, contract tests | AI generates test bodies; engineer writes property assertions | NEVER — 100% pass required |
| **RAGAS Evaluation** | RAGAS eval suite; custom harness | AI generates adversarial test cases; scored against baseline | NEVER — >90% pass required |
| **Guardrail Test Suite** | NeMo Guardrails; adversarial library | AI generates edge-case prompts to test coverage | NEVER — 100% pass required |
| **Model Risk Gate (T4)** | Ticket-based approval workflow | AI generates Model Risk evidence draft; Model Risk Lead reviews/signs | NEVER — human sign-off mandatory |
| **L4 Canary Deploy** | Argo Rollouts / Flagger; Prometheus SLO | AI monitors SLOs; triggers automatic rollback on breach | SRE Lead override only; every override logged |
| **DEA Validation** | DEA generation service completeness check | DEA assembled from all sources; completeness validated | NEVER for High-Risk agents |
| **Post-Deploy DORA Record** | Argo CD drift detection; cost validator | AI generates stakeholder summary; DORA change record auto-created | NEVER — mandatory; absence triggers T4 alert |

---

Next: [Part 4 — Delivery, Governance & Reference](./12-apex-ea-delivery-governance-reference.md) covers roadmap, migration strategy, 5-tier governance, requirements traceability, and reference material.
