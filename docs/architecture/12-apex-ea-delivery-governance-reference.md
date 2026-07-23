---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-delivery-governance-reference
title: "APEX EA Part 4: Delivery, Governance & Reference"
date_created: 2026-04-01
last_reviewed: 2026-07-17
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 4 delivery governance reference
  - governance model operational framework
  - dora compliance implementation
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part4_Delivery_Governance_Reference.md
tags:
  - enterprise-architecture
  - specialization
  - governance
  - regulatory-compliance
  - delivery-roadmap
  - dora
  - eu-ai-act
---

# APEX EA Part 4: Delivery, Governance & Reference

Part 4 of the APEX EA 4-part blueprint. Continues from [Part 3: Information Systems & Technology Architecture](./11-apex-ea-information-systems-architecture.md).

## Architecture Roadmap

| Work Package | Bolts | Weeks | Horizon | Risk Level |
|---|---|---|---|---|
| Multi-region K8s, zero-trust IAM, Vault, network policy | 2 | 4 | H1 | Low |
| Agent Orchestration platform: framework spike, guardrails, KB | 2 | 4 | H1 | Medium |
| CI/CD L1–L5 + DEA generation service | 2 | 3 | H1 | Medium |
| Security baseline: zero-trust, mTLS, guardrails, Agent Gateway | 2 | 4 | H1 | Low |
| LGTM observability + agent health score + alerting | 1 | 2 | H1 | Low |
| **Pioneer 1** — Risk Scoring Agent | 3 | 8 | H1 | HIGH |
| **Pioneer 2** — Customer Verification Agent | 3 | 7 | H1 | Medium |
| **Pioneer 3** — Advisory Rebalancing Agent | 2 | 6 | H2 | Medium |
| **Pioneer 4** — IT Incident Response Agent | 2 | 5 | H2 | Low |
| **Pioneer 5** — Model Monitoring & Compliance Agent | 3 | 6 | H2 | Medium |
| Self-service portal, agent marketplace, health dashboard | 3 | 8 | H2 | Medium |
| EU AI Act compliance pack + DEA templates + DORA automation | 2 | 5 | H2 | High |

---

## Solution Building Blocks

| SBB | Decision | Cloud-Native Solution | AI-DLC Role |
|---|---|---|---|
| Agent Orchestration Engine | Evaluate OSS preferred | LangGraph / AutoGen / CrewAI; abstraction layer prevents lock-in | AI-DLC generates agent YAML, tool definitions, action config |
| Foundation Models | Buy via provider-agnostic adapter | Provider per task type; LiteLLM-style adapter; no single-vendor lock-in | AI-DLC selects model per task from pre-approved catalogue |
| Vector Store | OSS preferred | Weaviate / Qdrant / Milvus; Embedding Compatibility Contract | AI-DLC generates index schema, query patterns, RAGAS test suite |
| Agent Control Plane | Build | Python FastAPI; K8s; 6 services | AI-DLC builds each service in 1 bolt; L1–L5 on all IaC |
| DEA Generation Service | Build | Python event-driven; K8s; immutable store | AI-DLC builds in 1 bolt; Compliance reviews output |
| Agent Gateway | Build on OSS | Envoy proxy + plugin OR APISIX + plugin | AI-DLC generates gateway config from registry schema |
| Developer Portal | Build | React SPA + API Gateway | AI-DLC scaffolds UI in Mob Construction; UX validated |
| LGTM Observability | OSS | OpenTelemetry + Prometheus + Grafana + Loki + Tempo | AI-DLC generates dashboards-as-code |
| AI Safety Layer | OSS | NeMo Guardrails or Guardrails AI | AI-DLC generates rule sets; red-team tests quarterly |
| Compliance Reporter | Build on OSS | Python pipeline + Superset/Metabase | AI-DLC generates EU AI Act and DORA templates |

---

## 5-Tier Governance Model

| Tier | Scope | Method | SLA | Bypassable? |
|---|---|---|---|---|
| **T1—Auto** | IaC L1 scan, RAGAS score, DEA completeness, tag compliance, budget alert | CI pipeline + K8s admission controllers | Synchronous | NO — physically blocks; no override |
| **T2—Architect** | Pattern conformance, new data flow, data classification audit | Automated flag → architect on-call | 4 business hours | NO — blocks deployment until approval |
| **T3—ARB** | New SBB, significant deviation, agent topology, debt threshold | Weekly ARB session; async urgent | Weekly | Exception ONLY: CTO written approval + compliance log |
| **T4—Reg-Gate** | High-Risk AI (EU AI Act Art.6), DORA change, C4-data flow | Compliance Lead; no delegation | 48 hours | NO — hardcoded; no exception pathway |
| **T5—Exec** | Budget > threshold, strategic change, programme risk | Monthly Steering; emergency 48hr for DORA | Monthly | NO — requires Steering quorum |

---

## Change Intelligence Process

| Change Type | AI Monitoring | Human Decision | DORA Framing | Example |
|---|---|---|---|---|
| **Technology-Driven** | Model release feeds; benchmark auto-run | Enterprise Architect reviews; ARB approves | Formal change event regardless of release frequency | Open-weight model +18% on eval; ARB approves in 3 days with RAGAS evidence |
| **Regulatory-Driven** | Regulatory feed parsed daily; impact classified | Compliance Lead decides; Regulatory Affairs engaged | Regulatory change triggers controlled response | EU AI Act Art.6 date reached; auto-classification activated; DORA pack updated same day |
| **Business-Driven** | Portal onboarding request → intake workflow | ARB intake decision within 5 days; review within 10 | Standard change; ARB record; DORA log if Tier-1 | New division requests APEX for contract analysis |
| **Simplification** | Usage analytics; <3mo utilization threshold | Domain owner: decommission or document retention | Decommission = formal change event | Pioneer v1.2 → v2.0; parallel 4 weeks then decommission with evidence |

---

## Regulatory Cross-Reference Matrix

| Regulation | Key Obligations | APEX Control | Evidence Artefact |
|---|---|---|---|
| **EU AI Act 2024/1689** | High-Risk classification; Risk Management; Transparency; Quality Management | Intake risk classifier; DEA per High-Risk; RAGAS; Model Risk opinion | DEA per decision; Compliance pack; Model Risk opinions; Explainability reports |
| **DORA 2025** | ICT security; Risk management; 72-hr incident notification; Red-team penetration testing | Zero-trust security; DORA change framing (all AI changes = controlled events); Incident Agent; automated notification; quarterly red-team | Evidence Pack (quarterly); DORA change records; incident test results; red-team findings |
| **GDPR / UK GDPR** | Data minimisation; Privacy by design; Security; Cross-border transfers | PII ANONYMIZE in guardrails; data residency enforced; AES-256 CMK; agent memory TTL; Phase Boundary Receipts | Article 30 processing records; Data Flow Maps; Guardrail config; DPO sign-offs |
| **Internal Model Risk** | Model validation; documentation; ongoing monitoring; independent review | Model Risk T4 gate in CI/CD; explainability artefact; RAG explanation in DEA; Model Monitor (Pioneer 5) | Model Risk opinions; Explainability reports; Drift dashboards |
| **BCBS 239** | Data lineage for risk; accuracy, completeness, timeliness | Data catalog integration; RAG retrieval log traces decisions; DEA lineage chain | Data catalog reports; RAG logs (7-year retention); DEA lineage section |
| **MiFID II Art.27** | Best execution; suitability assessment; record-keeping | HITL mandatory for advisory; KB suitability rules; full logging | DEA with HITL section; Suitability records; Session logs; Audit trail |

---

## Cloud-Native Service Mapping

| APEX Capability | OSS / Open-Standard | AWS | GCP | Azure |
|---|---|---|---|---|
| Container Orchestration | Kubernetes (CNCF) | EKS | GKE | AKS |
| Serverless Functions | Knative / OpenFaaS | Lambda | Cloud Functions | Functions |
| Agent Orchestration | LangGraph / AutoGen / CrewAI | Bedrock Agents | Vertex AI Agents | AI Foundry Agents |
| Foundation Model API | Ollama (local) / LiteLLM | Bedrock | Vertex AI | Azure OpenAI |
| Vector Store | Weaviate / Qdrant / Milvus | OpenSearch Serverless | AlloyDB pgvector | AI Search |
| Object Storage | MinIO (S3-compatible) | S3 | Cloud Storage | Blob Storage |
| Managed DB | PostgreSQL (K8s) | Aurora PostgreSQL | Cloud SQL PostgreSQL | DB for PostgreSQL |
| Event Streaming | Kafka / Redpanda | Kinesis / MSK | Pub/Sub / Dataflow | Event Hubs / Service Bus |
| Workflow Engine | Temporal / Argo Workflows | Step Functions | Cloud Workflows | Durable Functions |
| Secrets Management | HashiCorp Vault | Secrets Manager + KMS | Secret Manager + KMS | Key Vault |
| Metrics | Prometheus (CNCF) | CloudWatch Metrics | Cloud Monitoring | Azure Monitor |
| Tracing | Jaeger / Grafana Tempo (OTEL) | X-Ray | Cloud Trace | Application Insights |
| Logging | Loki / OpenSearch | CloudWatch Logs | Cloud Logging | Monitor Logs |
| Dashboards | Grafana (CNCF) | CloudWatch Dashboards | Cloud Dashboards | Azure Dashboards |
| GitOps / CD | Argo CD / Flux (CNCF) | CodePipeline | Cloud Deploy | DevOps Pipelines |
| Service Mesh | Istio / Linkerd (CNCF) | App Mesh | Traffic Director | Istio add-on |
| ML Experiment Tracking | MLflow | SageMaker Experiments | Vertex AI Experiments | ML Experiments |

---

## Key Governance Documents

**ARS-APEX-001** — 162 total requirements across all TOGAF phases with continuous AI-maintained traceability, human review gate before deployment.

**CAF-APEX-001** — 5-Tier governance escalation model with hard gates at T1 and T4; T3 allows exception pathways only through Group CTO.

**DORA-APEX-001** — Every AI model update, KB refresh, and topology change recorded as formal DORA change event with ARB reference and compliance log entry.

**EU-AI-ACT-APEX-001** — High-Risk classification at intake; DEA pattern for all High-Risk agents; Explainability artefact (SHAP/LIME) mandatory CI/CD gate; 7-year immutable retention.

---

## Closing

The APEX EA blueprint demonstrates how to operationalize enterprise AI at scale: combining TOGAF-rigorous governance with AI-DLC's velocity, enforcing regulatory compliance through architecture patterns (not manual processes), and building economic value through platform thinking.

Success requires three elements: committed sponsorship from the Group CTO, investment in AI-native roles and training, and the discipline to keep governance gates inviolable even when velocity pressures mount.

By Q4 2026, APEX will have demonstrated proof of value through five Pioneer agents, delivered sustainable productivity gains measured quarterly against actuals, and established GlobalCorp as an AI-native organization capable of competing on AI capability, not just technology.
