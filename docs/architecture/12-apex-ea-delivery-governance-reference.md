---
doc_type: reference-architecture
domain: architecture
topic_id: apex-ea-delivery-governance-reference
title: "APEX EA Part 4: Delivery, Governance & Reference"
date_created: 2026-04-01
last_reviewed: 2026-07-23
status: current
covers_version: "Final Edition — April 2026"
aliases:
  - apex ea part 4 delivery governance reference
supersedes:
  - docs/enterprise-architecture/specialization/APEX_EA_Final_Part4_Delivery_Governance_Reference.md
tags:
  - enterprise-architecture
  - specialization
  - togaf
  - governance
  - regulatory-compliance
  - cloud-native
---

# APEX EA Part 4: Delivery, Governance & Reference

Continues from [Part 3: Information Systems & Technology Architecture](./11-apex-ea-information-systems-architecture.md). This part covers the roadmap, migration strategy, 5-tier governance model, requirements traceability, and regulatory/service-mapping/glossary reference material.

### APEX 5-Tier Governance Model

```mermaid
graph TB
    Dev["Agent Deployment"] -->|All Changes| T1["T1 Automation<br/>CI Pipeline Checks<br/>L1 IaC Scan, RAGAS,<br/>DEA Completeness<br/>NO Override"]
    T1 -->|Pattern Check| T2["T2 Architect<br/>Automated Flag to<br/>On-Call Architect<br/>4hr SLA<br/>NO Override"]
    T2 -->|Significant Change| T3["T3 ARB<br/>Architecture Review Board<br/>Weekly Session<br/>Exception: CTO Written<br/>Approval Only"]
    T3 -->|High-Risk AI or<br/>DORA Change| T4["T4 Reg-Gate<br/>Compliance Lead<br/>EU AI Act / DORA<br/>48hr SLA<br/>HARDCODED<br/>NO Exception"]
    T4 -->|Budget/Strategic| T5["T5 Executive<br/>Steering Committee<br/>Monthly Review<br/>Emergency 48hr<br/>for DORA Incidents"]
    T5 -->|Approved| Prod["Production<br/>with ARB Record<br/>& DORA Entry"]
    
    style T1 fill:#c8e6c9
    style T2 fill:#fff9c4
    style T3 fill:#ffe0b2
    style T4 fill:#f8bbd0
    style T5 fill:#e1bee7
    style Prod fill:#b3e5fc
```

**All changes flow through T1 automation first, then escalate by governance tier:** Automated checks are non-bypassable. Architect review gates standard changes. ARB approves significant deviations. T4 Reg-Gate is hardcoded for High-Risk AI and DORA events (no exception pathway). Executive approval only for strategic/budget decisions.

## Opportunities, Migration, Governance & Change (Phases E–H)

**PHASES E–H** — Roadmap, SBBs, 5-tier governance, and change intelligence

### Architecture Roadmap — ROAD-APEX-001

| Work Package | WP | Bolts | Wks | Horizon | Risk Level |
| --- | --- | --- | --- | --- | --- |
| Multi-region Kubernetes, zero-trust IAM, HashiCorp Vault, network policy | WP-001 | 2 | 4 | H1 | Low — well-understood pattern; IaC-automated |
| AI Agent Orchestration platform: framework spike, guardrails, KB-001 | WP-002 | 2 | 4 | H1 | Medium — framework lock-in risk; abstraction layer required |
| CI/CD L1–L5 verification + DEA generation service deployment | WP-003 | 2 | 3 | H1 | Medium — DEA service is new pattern; allow spike time in bolt 1 |
| Security baseline: zero-trust, mTLS, guardrails layer, Agent Gateway | WP-004 | 2 | 4 | H1 | Low — automated; well-understood pattern |
| LGTM observability stack + agent health score metrics + alerting | WP-005 | 1 | 2 | H1 | Low |
| Pioneer 1 — Risk Scoring Agent (first full end-to-end; all gates) | WP-006 | 3 | 8 | H1 | HIGH — first end-to-end run; DEA, Model Risk, RAGAS all first-time; allow buffer |
| Pioneer 2 — Customer Verification Agent | WP-007 | 3 | 7 | H1 | Medium — builds on Pioneer 1 learnings; pattern established |
| Pioneer 3 — Advisory Rebalancing Agent [Programme Risk Gate] | WP-008 | 2 | 6 | H2 | Medium — MiFID II HITL adds complexity; suitability rules in KB-003 |
| Pioneer 4 — IT Incident Response Agent | WP-009 | 2 | 5 | H2 | Low — operational domain; fewer regulatory constraints |
| Pioneer 5 — Model Monitoring & Compliance Agent | WP-010 | 3 | 6 | H2 | Medium — DORA reporting integration; cross-domain data access |
| Self-service portal, agent marketplace, agent health dashboard | WP-011 | 3 | 8 | H2 | Medium — developer experience is subjective; UX validation needed |
| EU AI Act compliance pack + DEA template library + DORA automation | WP-012 | 2 | 5 | H2 | High — regulatory interpretation risk; regulatory counsel required |

### Migration Strategy — Existing AI Tool Inventory (IMP-APEX-001)

23 pre-existing AI tools were assessed against APEX capability and governance fit, and sorted into four migration categories:

| Category | Count | Action | AI-DLC Migration Path | Target Date |
| --- | --- | --- | --- | --- |
| ADOPT — Already AWS; add APEX governance | 8 tools | Wrap in APEX tool framework; add guardrails | AI-DLC Operations: IaC wrapping in 1 bolt per tool | Q3 2025 |
| ADAPT — Works well; needs APEX integration layer | 6 tools | Expose as APEX tool; APEX orchestrates | AI-DLC build adapter Lambda in Mob Construction | Q4 2025 |
| REPLACE — Duplicates APEX capability | 7 tools | Pioneer agent replaces; decommission legacy | Parallel-run then canary cutover; AI monitors metrics | Q1 2026 |
| RETIRE — Unused/low value | 2 tools | Immediate decommission; archive audit logs | AI-DLC Operations: IaC teardown + evidence generation | Q2 2025 |

### Solution Building Blocks — SBB-APEX-001

| SBB | Decision | Cloud-Native Solution | AI-DLC Role in Delivery |
| --- | --- | --- | --- |
| Agent Orchestration Engine | EVALUATE OSS preferred | LangGraph / AutoGen / CrewAI — evaluated in WP-002 spike; abstraction layer prevents lock-in | AI-DLC Construction generates agent YAML, tool definitions, and action group config |
| Foundation Models | BUY via provider-agnostic adapter | Provider evaluated per task; no single-vendor lock-in; LiteLLM-style adapter library in all agent code | AI-DLC Construction: AI selects model per task type from pre-approved catalogue updated quarterly |
| Vector Store | OSS preferred | Weaviate / Qdrant / Milvus — Embedding Compatibility Contract applies | AI-DLC Construction generates index schema, query patterns, and RAGAS test suite |
| Agent Control Plane | BUILD | Python FastAPI; Kubernetes; 6 services (ALM, Budget, Onboarding, Chargeback, Notification, Compliance) | AI-DLC builds each service in 1 bolt; L1–L5 verification on all IaC and code |
| DEA Generation Service | BUILD | Python event-driven service; Kubernetes; immutable store | AI-DLC builds DEA assembler in 1 bolt; Compliance Lead reviews output against EU AI Act Art.13 |
| Agent Gateway | BUILD on OSS | Envoy proxy + custom plugin OR APISIX + custom plugin | AI-DLC generates gateway config from agent registry schema; property tests validate enforcement rules |
| Developer Portal | BUILD | React SPA + API Gateway; Amplify or equivalent CDN | AI-DLC scaffolds UI components in Mob Construction in 1 bolt; UX validated with domain dev teams |
| Human Review Portal | BUILD on open framework | React + Temporal / Camunda workflow engine | AI-DLC generates workflow JSON definitions; custom UI mob-built in 1 bolt |
| LGTM Observability | OSS | OpenTelemetry + Prometheus + Grafana + Loki + Tempo (full LGTM stack) | AI-DLC generates dashboards-as-code (Grafana JSON) from agent metric schema definition |
| AI Safety Layer | OSS | NeMo Guardrails or Guardrails AI; configured per agent EU AI Act risk tier | AI-DLC generates guardrail rule sets; red-team adversarial tests AI-generated quarterly |
| IaC Platform | OSS (REUSE) | Terraform / OpenTofu + Argo CD (GitOps); Terratest for property tests | AI-DLC extends existing pipeline; Terratest property tests are mandatory (L3 verification) |
| Compliance Reporter | BUILD on OSS | Python pipeline + Apache Superset or Metabase | AI-DLC generates EU AI Act and DORA report templates; DORA change record auto-writer component added |

### 5-Tier Governance Model — CAF-APEX-001

| Tier | Scope | Method | SLA | Bypassable? |
| --- | --- | --- | --- | --- |
| T1 — Auto | IaC L1 scan; RAGAS score; DEA completeness; tag compliance; budget alert | CI pipeline + Kubernetes admission controllers + scheduled validation jobs | Synchronous | NO — pipeline physically blocks; no human override path |
| T2 — Architect | Pattern conformance; new data flow; data classification audit | Automated flag to architect on-call (Slack/Teams) within 4-hour SLA | 4 business hours | NO — deployment blocked until architect approves |
| T3 — ARB | New SBB; significant deviation; agent topology change; debt threshold breach | Weekly ARB session; async for urgent items between sessions | Weekly | Exception ONLY: Group CTO written approval + compliance register entry; silent bypass is not possible |
| T4 — Reg-Gate | High-Risk AI (EU AI Act Art.6); DORA-reportable change; any C4-data flow change | Compliance Lead; no delegation; Regulatory Affairs Lead engaged | 48 hours | NO — hardcoded in CI pipeline; no exception pathway exists |
| T5 — Exec | Budget above approved threshold; strategic architecture change; programme risk escalation | Monthly Steering Committee; emergency session within 48 hrs for DORA incidents | Monthly | NO — requires Steering Committee quorum |

### Change Intelligence Process — ACHG-APEX-001

| Change Type | AI Monitoring | Human Decision Authority | DORA Framing | Illustrative Example |
| --- | --- | --- | --- | --- |
| T1 — Technology-driven | Model release channels monitored; OSS project feeds; benchmark auto-run vs. GlobalCorp eval suite | Enterprise Architect reviews impact; ARB approves; T4 Reg-Gate if High-Risk agent affected | Formal change event regardless of model release frequency | Open-weight model outperforms current by 18%; ARB approves upgrade in 3 days with RAGAS regression evidence |
| T2 — Regulatory-driven | Regulatory feed parsed daily by compliance-monitoring agent; impact classified against APEX control inventory | Compliance Lead decides; Regulatory Affairs Lead engaged for ambiguous interpretation | Regulatory change triggers controlled response plan; not reactive patching | EU AI Act Art.6 enforcement date reached; APEX intake auto-classification activated; DORA evidence pack updated same day |
| T3 — Business-driven | Onboarding request submitted via self-service portal; intake workflow triggered automatically | ARB intake decision within 5 business days; architecture review within 10 business days | Standard change; ARB record created; DORA log entry if affects Tier-1 service | New Procurement Division requests APEX onboarding for contract analysis use case |
| T4 — Simplification | Usage analytics flags agents below utilisation threshold for 3 consecutive months; auto-review prompt generated | Domain owner decides: decommission or document justification for retention | Decommission = formal change event; IaC teardown + DEA archive + compliance record | Pioneer 1 v1.2 superseded by v2.0; v1.2 parallel-run for 4 weeks then decommissioned with full evidence trail |

## Requirements Management — Continuous

**REQ MGMT** — Living ARS — 162 total requirements across all phases

Requirements Management is the continuous central process of the TOGAF ADM. AI-DLC's Semantic Context Building and persistent context storage transform this from a periodic document into a living, AI-maintained traceability system with a human review gate before every deployment.

### Key Requirements — ARS-APEX-001

| Req ID | Category | Statement | Priority | Source | Status |
| --- | --- | --- | --- | --- | --- |
| BR-001 | Business | Platform supports at minimum 120 concurrent agent interactions per region under normal load | Must | Capacity model | In Design |
| BR-003 | Business | All agent decisions logged with full context and queryable for a minimum of 7 years | Must | DORA Art.11 | In Design |
| BR-006 | Business | EU AI Act risk tier automatically classified for every agent at the point of intake | Must | EU AI Act Art.6 | In Design |
| BR-007 | Business | Productivity gains tracked quarterly against actuals; reported to Steering Committee | Must | BP-01 | In Design |
| DR-001 | Data | Personal data never persisted in conversation logs, session memory, or observability traces | Must | GDPR Art.5 | In Design |
| DR-002 | Data | Embedding model ID and version stored in data catalog for every KB; RAGAS gate on any upgrade | Must | DP-05 | In Design |
| DR-003 | Data | Previous embedding index retained for 90 days post-upgrade to support rollback | Must | DP-05 | In Design |
| AR-001 | Application | Agent Control Plane API achieves p99 response time below 500ms under 500 RPS | Must | SLA Policy | In Design |
| AR-002 | Application | DEA generation service produces complete DEA within 5 seconds; stored immutably for 7 years | Must | TP-06 | In Design |
| AR-003 | Application | Agent Gateway enforces registry lookup; unregistered agents receive 403 at gateway | Must | BP-03 | In Design |
| TR-001 | Technology | All AI model invocations travel exclusively over private network paths; no public internet egress from agent pods | Must | TP-01 / TP-02 | In Design |
| TR-002 | Technology | All AI-generated IaC passes L1–L5 layered verification; L2 explanation artefact retained 12 months | Must | TP-05 | In Design |
| SR-001 | Security | Customer-managed encryption keys rotated on a maximum 365-day cycle; rotation enforced by automated check | Must | GDPR Art.32 | In Design |
| SR-002 | Security | Red-team adversarial testing of every agent completed and documented before production deployment approval | Must | AI Risk Policy / OWASP LLM | In Review |
| CR-001 | Compliance | EU AI Act risk classification documented and stored in agent registry for every agent in all environments | Must | EU AI Act Art.9 | In Design |
| CR-002 | Compliance | Model explainability method (SHAP, LIME, or equivalent) documented; evidence artefact generated before production | Must | EU AI Act Art.13 | In Design |
| CR-003 | Compliance | DORA 72-hour ICT incident notification workflow automated and tested quarterly under simulated conditions | Must | DORA Art.17 | In Review |
| CR-004 | Compliance | Every High-Risk AI agent produces a DEA for every regulated decision; DEA queryable by compliance team | Must | EU AI Act Art.13 / DEA | In Design |
| CR-005 | Compliance | Every AI model update, KB refresh, and agent topology change recorded as a formal DORA change event with ARB reference | Must | DORA Art.11 | In Design |

## Regulatory Cross-Reference Matrix

| Regulation | Key Obligations | APEX Architecture Control | Evidence Artefact |
| --- | --- | --- | --- |
| EU AI Act 2024/1689 | Art.6 (High-Risk classification), Art.9 (Risk Management System), Art.13 (Transparency — addressed by DEA pattern), Art.17 (Quality Management) | EU AI Act risk classifier at intake (WP-012); DEA pattern for all High-Risk agents; RAGAS gate; Model Risk opinion; DEA export API; explainability artefact in CI/CD | DEA per regulated decision; EU AI Act compliance pack (WP-012); Model Risk Opinions; CI/CD explainability reports |
| DORA (EU) 2025 | Art.9 (ICT security policy), Art.11 (ICT risk management — all AI changes = controlled change events), Art.17 (72-hr incident notification), Art.26 (TLPT) | Zero-trust security architecture; DORA change framing protocol (every AI change = formal change event with ARB record); Incident Agent (Pioneer 4); automated 72-hr notification workflow; quarterly red-team testing | DORA Evidence Pack (quarterly); DORA change records per AI update; incident runbook test results; red-team findings |
| GDPR / UK GDPR | Art.5 (data minimisation), Art.25 (privacy by design — Phase Boundary Receipts enforce this), Art.32 (appropriate security), Art.46 (cross-border transfer controls) | PII ANONYMIZE in guardrail layer; data residency enforced via NetworkPolicy; AES-256 CMK encryption; agent memory TTL; Phase Boundary Receipt requires DPO sign-off before C4 data flows go to production | Article 30 records of processing; Data Flow Maps per Pioneer agent; Guardrail configuration evidence; DPO sign-off artefacts |
| Internal Model Risk (aligned SR 11-7) | Model validation before production; documentation of assumptions; ongoing performance monitoring; independent review | Model Risk opinion gate (T4 Reg-Gate) in CI/CD; explainability artefact (SHAP/LIME); RAG retrieval explanation in DEA; Model Monitoring Agent (Pioneer 5) for drift detection | Model Risk Opinions per Pioneer agent; Explainability reports (SHAP/LIME per model); Drift monitoring dashboards (Pioneer 5) |
| BCBS 239 | Data lineage for risk aggregation; accuracy, completeness, and timeliness of risk data reporting | Data catalog lineage integration; RAG retrieval log traces every agent decision to source data; DEA RAG section provides full lineage chain to regulators and auditors | Data catalog lineage reports; RAG retrieval log exports (7-year retention); DEA RAG retrieval section per regulated decision |
| MiFID II Art.27 | Best execution obligations; suitability assessment for investment advice; record-keeping for advisory decisions | Human-in-the-Loop mandatory for all investment advisory outputs; HITL outcome written to DEA; KB-003 contains suitability rules; full session and decision logging | DEA with HITL section; Suitability assessment records; Session logs per advisory interaction; Agent audit trail |

## Cloud-Native Service Mapping

| APEX Capability | OSS / Open-Standard | Provider A (AWS) | Provider B (GCP) | Provider C (Azure) |
| --- | --- | --- | --- | --- |
| Container Orchestration | Kubernetes (CNCF) | EKS | GKE | AKS |
| Serverless Functions | Knative / OpenFaaS | AWS Lambda | Cloud Functions | Azure Functions |
| Agent Orchestration | LangGraph / AutoGen / CrewAI | Bedrock Agents | Vertex AI Agents | Azure AI Foundry Agents |
| Foundation Model API | Ollama (local) / LiteLLM adapter | Bedrock (Claude, Titan) | Vertex AI (Gemini, Claude) | Azure OpenAI (GPT-4o, o1) |
| Vector Store | Weaviate / Qdrant / Milvus | OpenSearch Serverless | AlloyDB + pgvector | Azure AI Search |
| Object Storage | MinIO (S3-compatible API) | S3 | Cloud Storage | Azure Blob Storage |
| Managed Relational DB | PostgreSQL (self-managed on K8s) | Aurora PostgreSQL | Cloud SQL PostgreSQL | Azure DB for PostgreSQL |
| Event Streaming | Apache Kafka / Redpanda | Kinesis / MSK | Pub/Sub / Dataflow | Azure Event Hubs / Service Bus |
| Workflow Engine | Temporal / Argo Workflows | Step Functions | Cloud Workflows | Azure Durable Functions |
| Secrets Management | HashiCorp Vault | AWS Secrets Manager + KMS | Secret Manager + Cloud KMS | Azure Key Vault |
| Metrics | Prometheus (CNCF) | CloudWatch Metrics | Cloud Monitoring | Azure Monitor |
| Tracing | Jaeger / Grafana Tempo (OTEL) | AWS X-Ray | Cloud Trace | Azure Application Insights |
| Logging | Loki / OpenSearch | CloudWatch Logs | Cloud Logging | Azure Monitor Logs |
| Dashboards | Grafana (CNCF) | CloudWatch Dashboards | Cloud Monitoring Dashboards | Azure Dashboards |
| GitOps / CD | Argo CD / Flux (CNCF) | CodePipeline | Cloud Deploy | Azure DevOps Pipelines |
| Service Mesh | Istio / Linkerd (CNCF) | AWS App Mesh | Traffic Director | Azure Istio add-on |
| ML Experiment Tracking | MLflow | SageMaker Experiments | Vertex AI Experiments | Azure ML Experiments |
| AI Safety / Guardrails | NeMo Guardrails / Guardrails AI | Bedrock Guardrails | Vertex AI Safety Filters | Azure AI Content Safety |
| IaC | Terraform / OpenTofu + Terratest | AWS CDK / CloudFormation | Deployment Manager | Bicep / ARM Templates |
| Progressive Delivery | Argo Rollouts / Flagger | CodeDeploy | Cloud Deploy canary | Azure Deployment Strategies |
| Agent Gateway | Envoy + plugin / APISIX + plugin | API Gateway + Lambda authoriser | Apigee + custom policy | API Management + policy |
| IaC Security (L1) | Checkov + Semgrep + Trivy | CodeGuru + Inspector | Artifact Registry scanning | Defender for DevOps |
| Runtime Security | Falco (CNCF) | GuardDuty | Security Command Center | Defender for Containers |
| DEA Store | PostgreSQL + object storage (WORM) + Athena | S3 Object Lock + Athena | Cloud Storage (locked) + BigQuery | Azure Immutable Blob + Synapse |

## Glossary

**SBB** — Solution Building Block: specific implementation of an Architecture Building Block; defines what is built, bought, or reused for a given platform capability.

**Semantic Context** — AI-DLC concept: rich, structured context provided to AI coding agents through steering files so they apply GlobalCorp-specific standards automatically and consistently.

**TLPT** — Threat-Led Penetration Testing: DORA Art.26 obligation for major entities; GlobalCorp APEX conducts TLPT quarterly for the agent gateway and core platform components.

**Unit of Work** — AI-DLC equivalent of an Agile Epic; decomposed into bolts. APEX planning baseline: 1 Unit of Work for a Pioneer Domain agent = 3 bolts, 6–8 calendar weeks including governance gates.

**Zero-Trust** — Security model where no identity or network location is inherently trusted; every request is authenticated, authorised, and logged regardless of origin; enforced by service mesh mTLS.

## Document Control

| Version | Issue Date | Authors | Description | Approved By |
| --- | --- | --- | --- | --- |
| 1.0 | January 2025 | Enterprise Architecture Team | Initial release — TOGAF 10 ADM phases A–D | Architecture Review Board |
| 2.0 | March 2025 | Enterprise Architecture Team | Full ADM coverage; Architecture Contracts; Governance model added | Group CTO |
| 3.0 | April 2026 | Enterprise Architecture Team | Cloud-native edition (vendor-agnostic); AI-DLC integrated; table formatting improved | Group CTO |
| 4.0 — FINAL | April 2026 | Enterprise Architecture Team | Final edition: team structure added (org model, core team register, RACI: Agent Lifecycle, RACI: Platform Governance, RACI: Regulatory, Responsibility Assignment Matrix, Stakeholder Map, Team Interaction Map); DEA service; Agent Gateway; Embedding Compatibility Contract; Data Maturity Gate; Phase Boundary Receipts; DORA change framing; Layered Verification Model; Agent Sprawl governance; 19 requirements; 24-entry Cloud-Native Service Mapping; full glossary | Group CTO |
| 5.0 — SERIES SPLIT | July 2026 | Enterprise Architecture Team | Split into a 4-part series per repo multi-part-series standard; no content changes beyond re-pagination | Enterprise Architecture Team |

---

TOGAF® is a registered trademark of The Open Group. EU AI Act, DORA, GDPR, MiFID II, and BCBS 239 are legislative instruments of their respective issuing bodies. All product names mentioned as cloud-provider equivalents are trademarks of their respective owners.

This is the final part of the series. For the full programme overview and links to all 4 parts, return to [Part 1: Team Structure, RACI & Operating Model](./09-apex-ea-team-structure-raci.md).
