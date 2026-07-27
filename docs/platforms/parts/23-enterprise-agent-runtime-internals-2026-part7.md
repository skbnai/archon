---
title: "Enterprise AI Agent Runtime Internals: AWS, Azure & GCP (2026) (Part 7)"
doc_type: guide
domain: platforms
status: current
topic_id: enterprise-agent-runtime-internals-2026-part7
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, azure, gcp, comparative-analysis, references]
covers_version: "as of 2026-07-11 — AWS Bedrock AgentCore GA, Azure AI Foundry Agent Service, Google Vertex AI Agent Engine"
---

> Continues from [Enterprise AI Agent Runtime Internals: AWS, Azure & GCP (2026)](../23-enterprise-agent-runtime-internals-2026.md), closing with the comparative analysis tables, the documented-vs-inferred breakdown for each vendor, and the report's references.

## Comparative Analysis Tables

### Runtime Implementation

| Dimension | AWS Bedrock AgentCore | Azure AI Foundry Agent Service | GCP Vertex AI Agent Engine |
|---|---|---|---|
| **Execution substrate** | ECS/Fargate (containerized) [I] | Azure Container Apps [E] | Cloud Run (gVisor) [D] |
| **Scheduler** | ECS scheduler → EC2 Nitro VM [D] | AKS scheduler → Hyper-V VM [D] | Borg → KVM host [D] |
| **Isolation unit** | Per-session Fargate task [I] | Per-agent ACA replica [D] | Per-session Cloud Run instance [D] |
| **Sandbox** | Linux namespaces + cgroups [D] | Linux namespaces (pod) [D] | gVisor (userspace kernel) [D] |
| **Hardware isolation** | Nitro hypervisor (bare metal) [D] | Hyper-V hypervisor [D] | KVM + Titan security chip [D] |
| **Cold start** | "Single-digit seconds" [D] | "Sub-second" (warm) [D] | 1–5s (gVisor overhead) [D] |
| **Warm pool** | Yes (pre-started containers) [I] | Yes (min replicas) [D] | Yes (min instances) [D] |
| **SDK** | Strands (Python) / AgentCore SDK | Azure AI SDK (Python, JS, .NET) | Google ADK (Python) / LangChain |
| **Tool execution** | AWS Lambda [D] | Azure Functions [D] | Cloud Functions / Extensions [D] |
| **State store** | DynamoDB [D] | Cosmos DB [D] | Firestore [D] |
| **Maturity** | GA June 2025 | GA November 2025 | GA March 2026 |

*[D] = DOCUMENTED, [E] = EVIDENCE, [I] = INFERRED*

### Security Architecture

| Dimension | AWS | Azure | GCP |
|---|---|---|---|
| **Auth standard** | SigV4 + IAM | Entra Bearer + MSAL | OAuth 2.0 + GCP IAM |
| **Workload identity** | IAM Task Role (IRSA) [D] | System Managed Identity [D] | Workload Identity Federation [D] |
| **Policy engine** | Cedar (Verified Permissions) [D] | Azure Policy + OPA [I] | IAM Conditions + OPA [I] |
| **mTLS** | App Mesh (Envoy) [D] | Azure Service Mesh (Istio) [D] | Anthos Service Mesh (Istio) [D] |
| **SPIFFE support** | Via App Mesh CA [I] | Via Istio CA [I] | Via Anthos Service Mesh [D] |
| **Prompt injection** | Bedrock Guardrails [D] | Azure Content Safety [D] | Vertex AI Model Armor [D] |
| **Anomaly detection** | GuardDuty [D] | Microsoft Defender [D] | Security Command Center [D] |
| **Audit log** | CloudTrail [D] | Azure Monitor [D] | Cloud Audit Logs [D] |
| **Secret management** | Secrets Manager + KMS [D] | Key Vault [D] | Secret Manager + Cloud KMS [D] |
| **Network isolation** | VPC + PrivateLink [D] | VNet + Private Endpoint [D] | VPC + Private Google Access [D] |
| **Data sovereignty** | GovCloud regions [D] | Sovereign Cloud (Azure DE, etc.) [D] | Google Sovereign Cloud [D] |
| **Compliance** | SOC2, HIPAA BAA, FedRAMP [D] | SOC2, HIPAA BAA, FedRAMP High [D] | SOC2, HIPAA BAA, FedRAMP Moderate [D] |

### MCP Integration

| Dimension | AWS | Azure | GCP |
|---|---|---|---|
| **MCP proxy** | AgentCore Gateway [D] | APIM + MCP policy [D] | Vertex AI Toolbox [D] |
| **MCP transport** | HTTP+SSE [D] | HTTP+SSE [I] | HTTP+SSE + gRPC [D] |
| **Tool registry** | AgentCore Registry [D] | AI Foundry tool config [D] | Extensions registry [D] |
| **Auth translation** | SigV4 at gateway [D] | MI token via APIM [I] | GCP SA via Anthos [I] |
| **Schema caching** | Registry cache [D] | APIM cache [I] | Extensions registry [D] |
| **Version negotiation** | Gateway handles [D] | APIM handles [I] | ADK client handles [D] |
| **Max MCP servers** | Not published | Not published | Not published |

### Strengths and Weaknesses

| Platform | Strengths | Weaknesses |
|---|---|---|
| **AWS AgentCore** | Most mature security stack (Cedar, GuardDuty, Macie, IAM); deep AWS service integration; Firecracker for Lambda tools; Step Functions for complex workflows | Runtime internals less documented; complex IAM/Cedar learning curve; AWS ecosystem lock-in; higher operational complexity |
| **Azure AI Foundry** | Fastest developer onboarding; Entra OBO for user delegation; Dapr for state/messaging; native M365 integration (SharePoint, Graph); Code Interpreter built-in | Runtime internals least documented; ACA session limits; OPA integration still preview; lower throughput for high-volume |
| **GCP Vertex AI Agent Engine** | Best infrastructure lineage (Borg scheduler, gVisor isolation, Anthos Service Mesh); SPIFFE via Anthos; Cloud Armor ML-based DDoS; most scalable foundation | Agent-specific features still maturing; Model Armor released late (2026); fewer enterprise case studies; Gemini model concentration |

## Documented vs Inferred Analysis

### What Each Vendor Has Documented

**AWS — Documented:**

- Cedar policy syntax and AgentCore integration
- DynamoDB as session + memory store
- Lambda as tool execution layer
- AgentCore Gateway as MCP proxy
- IAM Task Role model
- Bedrock Guardrails (all layers)
- Bedrock Invocation Logging
- Memory extraction pipeline
- Pricing model

**AWS — Undocumented (inferred):**

- Specific compute substrate (ECS/Fargate vs EKS)
- Per-session vs per-agent container granularity
- Internal service mesh implementation
- Warm pool size and management policy
- Exact DynamoDB schema for sessions

**Azure — Documented:**

- Cosmos DB for thread/agent storage
- Azure Functions for tool execution
- Managed Identity for service auth
- ACA as runtime substrate (implied)
- APIM for MCP proxy
- OBO flow for user delegation
- Dapr state store integration

**Azure — Undocumented (inferred):**

- Session affinity mechanism details
- ACA scale-out policy per session
- Internal Istio service mesh configuration
- Policy enforcement between APIM and ACA
- Warm pool management strategy

**GCP — Documented:**

- Cloud Run as execution substrate
- Firestore for session storage
- Spanner for Memory API
- gVisor sandbox
- Anthos Service Mesh with SPIFFE
- Workload Identity Federation
- Vertex AI Toolbox (MCP)
- Model Armor (pre-model guardrails)
- VPC Service Controls

**GCP — Undocumented (inferred):**

- Borg vs GKE scheduling boundary
- Session affinity implementation in Cloud Run
- Memory API Spanner schema
- Cross-region session failover mechanism
- Internal network path from Cloud Run to Vertex AI

## References

This report is grounded in the following categories of publicly available evidence gathered as of 2026-07-11:

**AWS:**

- AWS re:Invent 2024: "BOA405 — Amazon Bedrock AgentCore: Production-Grade Agent Infrastructure"
- AWS Blog: "Introducing Amazon Bedrock AgentCore" (June 2025)
- AWS Bedrock AgentCore Documentation (docs.aws.amazon.com/bedrock-agentcore)
- Amazon Verified Permissions (Cedar) Documentation
- AWS Fargate Isolation Model (ECS best practices guide)
- Firecracker Paper: "Firecracker: Lightweight Virtualization for Serverless Applications" (NSDI 2020)
- AWS Well-Architected Framework for Generative AI
- AgentCore GitHub Samples (aws-samples/amazon-bedrock-agentcore-samples)

**Azure:**

- Microsoft Build 2024/2025: "AI Foundry Agent Service" sessions
- Azure AI Foundry Documentation
- Azure Container Apps Documentation
- Azure Content Safety Documentation
- Dapr Documentation (dapr.io/docs)
- Azure Service Mesh Documentation
- Microsoft Entra ID OBO Flow documentation
- Semantic Kernel GitHub (microsoft/semantic-kernel)

**Google Cloud:**

- Google I/O 2024/2025: "Vertex AI Agent Engine" sessions
- Vertex AI Agent Engine Documentation
- Cloud Run Security Overview
- gVisor Documentation
- Anthos Service Mesh Documentation
- Google ADK Documentation
- Google Cloud Workload Identity Federation documentation
- Cloud Run Architecture (Borg reference blog post)

**Standards and cross-platform:**

- SPIFFE Specification
- OPA Documentation
- gVisor Paper: "gVisor: Sandboxing Cloud Native Applications" (HotCloud 2019)
- Borg: "Large-scale cluster management at Google with Borg" (EuroSys 2015)
- Firecracker: "Firecracker: Lightweight Virtualization for Serverless Applications" (NSDI 2020)
- CNCF Landscape: AI/ML
- OpenTelemetry

## Related

- [Enterprise Agent Runtime Internals](../23-enterprise-agent-runtime-internals-2026.md) — executive summary, runtime architecture, compute isolation
- [Enterprise Agent Runtime Internals (Part 6)](23-enterprise-agent-runtime-internals-2026-part6.md) — Networking internals, observability, multi-tenancy strategy
- [Amazon Bedrock AgentCore & Strands SDK — Deep Technical Research Report](../18-agentcore-strands-deep-research-report.md) — companion deep-dive on the AWS AgentCore platform and Strands SDK
- [AgentCore Memory Architecture Guide](../15-agentcore-memory-architecture-guide.md)
- [AWS Native, Standards-First Agentic Platform Architecture](../11-aws-native-standards-first-agentic-architecture.md)
- [AI Gateway: Full Comparison](../05-ai-gateway-full-comparison.md)
- [MCP Enterprise Security, Governance & Operations (2026)](../../protocols/14-mcp-enterprise-security-governance-operations-2026.md)
