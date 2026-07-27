---
title: "Cloud Implementation Comparison"
doc_type: guide
domain: trust
status: current
topic_id: cloud-implementation-comparison
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part15_Cloud_Implementation_Comparison.md]
tags: [ai-security, cloud, deepmind, aws, azure, gcp]
covers_version: "as of 2026"
---

A security-capability comparison of AWS Bedrock AgentCore, Azure AI Foundry, and Google Vertex AI Agent Builder, plus an agent framework and open-source security stack comparison.

## Cloud Platform Comparison for Enterprise AI Agents

The three major cloud providers have each built enterprise-grade AI agent platforms with different architectural philosophies, security models, and maturity levels. The choice of platform has significant implications for security architecture, operational complexity, and vendor lock-in. This analysis provides an objective comparison based on publicly available documentation and reported enterprise deployments as of mid-2026.

## AWS: Amazon Bedrock AgentCore

AWS Bedrock AgentCore (launched 2025) provides a production-grade agent execution platform deeply integrated with the AWS security ecosystem. AgentCore focuses on enterprise security primitives, making it the most security-complete platform for enterprises already invested in AWS.

**Security capabilities:**

| Capability | Implementation |
|---|---|
| Identity | AWS IAM with STS AssumeRole; task-scoped session policies; IAM Roles Anywhere for hybrid deployments |
| Authorization | Amazon Verified Permissions using Cedar; fine-grained, goal-aware policy evaluation |
| Tool Security | Bedrock AgentCore MCP server management; tool invocation via Lambda (isolated execution) |
| Memory | AgentCore Memory with DynamoDB backend; encryption at rest with KMS; access logging with CloudTrail |
| Observability | CloudWatch + CloudTrail + Bedrock-specific traces; integrates with Arize Phoenix via Lambda |
| Threat Detection | Amazon GuardDuty for ML-based anomaly detection; Macie for sensitive data detection in agent outputs |
| Network | VPC isolation; PrivateLink for private API access; WAF for agent endpoint protection |
| Compliance | SOC 2, ISO 27001, HIPAA BAA, FedRAMP; GDPR data residency via region selection |

**AWS strengths:** most mature policy-as-code framework (Cedar) in the industry; deep integration with AWS security services provides comprehensive defense-in-depth; GuardDuty and Macie integration provides automated threat detection; best-in-class secret management with Secrets Manager and KMS; IAM fine-grained permissions provide strong least-privilege implementation; AgentCore MCP management provides enterprise-grade tool governance.

**AWS weaknesses:** significant vendor lock-in — Cedar, AgentCore APIs, and Bedrock models are AWS-proprietary; multi-cloud deployments require significant additional architecture work; cost complexity — multiple overlapping services create difficult cost modeling; GuardDuty anomaly detection models not trained on AI agent behavior patterns.

## Microsoft Azure: Azure AI Foundry

Azure AI Foundry (formerly Azure AI Studio, rebranded 2024) provides an integrated development and deployment platform for enterprise AI agents. Microsoft's strength lies in Entra ID integration, Microsoft Defender ecosystem, and Office 365 data connectivity for enterprise agents.

| Capability | Implementation |
|---|---|
| Identity | Entra ID Workload Identity Federation; Managed Identities for Azure compute; Entra External ID for cross-tenant |
| Authorization | Azure RBAC + Entra ID Conditional Access; no Cedar equivalent; custom policy requires Azure Policy or OPA |
| Tool Security | Azure Functions as tool execution; API Management for tool governance; Key Vault for secrets |
| Memory | Azure AI Search + Cosmos DB for memory; CMK encryption; private endpoints |
| Observability | Azure Monitor + Application Insights; Microsoft Security Copilot for AI-assisted SOC functions |
| Threat Detection | Microsoft Defender for Cloud with AI-specific detections; Sentinel for SIEM integration |
| Network | Private Link; VNet integration; Azure Front Door for WAF |
| Compliance | Comprehensive: SOC 2, ISO 27001, HIPAA, FedRAMP High, EU AI Act readiness |

**Azure strengths:** best Microsoft 365 integration for enterprise agents accessing email, calendar, Teams, SharePoint; Microsoft Defender + Sentinel ecosystem for comprehensive threat detection; Entra ID is the enterprise identity standard for Microsoft-heavy organizations; Microsoft Security Copilot provides AI-assisted SOC capabilities; strong compliance coverage particularly for European enterprises.

**Azure weaknesses:** authorization policy framework less mature than Cedar, requiring more custom development; AI-specific security controls less specialized than AWS at time of analysis; Foundry platform more development-oriented than production-operations-oriented.

## Google Cloud: Vertex AI Agent Builder

Google Cloud's agent platform (Vertex AI Agent Builder + Gemini models + Cloud IAM) benefits from Google's deep AI research heritage and the A2A protocol as an open standard for agent interoperability. Google Cloud IAM provides workload identity through Workload Identity Federation.

| Capability | Implementation |
|---|---|
| Identity | Workload Identity Federation; Service Account impersonation; SPIFFE-compatible identity |
| Authorization | Cloud IAM with condition-based access; no Cedar equivalent; VPC Service Controls for perimeter |
| Tool Security | Cloud Functions / Cloud Run for tool execution; Artifact Registry for tool container management |
| Memory | Vertex AI Vector Search + Cloud Bigtable; CMEK; VPC Service Controls |
| Observability | Cloud Logging + Cloud Trace + Cloud Monitoring; Security Command Center for threat detection |
| Threat Detection | Security Command Center; Chronicle SIEM; Event Threat Detection |
| Network | VPC Service Controls; Private Google Access; Cloud Armor WAF |
| Compliance | SOC 2, ISO 27001, HIPAA, FedRAMP; strong GDPR EU region support |

## Agent Framework Comparison

| Framework | Model | Multi-Agent | Human-in-Loop | Production Maturity | Security Features |
|---|---|---|---|---|---|
| LangGraph | Graph-based stateful agents | Yes (multi-node graphs) | Built-in interrupt points | High — widely deployed | Checkpoint/rollback; state persistence; extensible PEP hooks |
| CrewAI | Role-based agent crews | Yes (crew coordination) | Limited built-in | Medium-High | Role-based access within crew; basic tool governance |
| AutoGen | Conversational multi-agent | Yes (conversation framework) | Human proxy agent | Medium | Basic authorization hooks; good for research/prototyping |
| Semantic Kernel | Plugin-based, enterprise-focused | Partial | Process automation integration | High — enterprise use | Strong Azure integration; policy-based plugin governance |
| Anthropic Agents SDK | Native Anthropic integration | Yes | Built-in approval gates | High — production ready | Deep constitutional AI integration; safety-first design |
| LlamaIndex Workflows | Event-driven agentic workflows | Yes (multi-agent) | Event-based interrupts | Medium-High | Good observability; extensible security hooks |

## Open-Source Security Stack

For enterprises that require vendor independence, maximum control, or highly regulated environments, an open-source security stack can provide comparable security to cloud platform native offerings. The stack requires more engineering investment but provides maximum flexibility.

| Layer | Open Source Component | Alternative to | Maturity |
|---|---|---|---|
| Identity | SPIFFE/SPIRE | Cloud Workload Identity | High — CNCF graduated |
| Authorization | OPA / Rego or OpenFGA | Cedar / Azure Policy | High — widely deployed |
| Secrets | HashiCorp Vault (OSS) | AWS Secrets Manager | High — enterprise standard |
| Observability | OpenTelemetry + Grafana + Jaeger | CloudWatch / Azure Monitor | High — CNCF graduated |
| Security Monitoring | Falco (eBPF) + Elastic SIEM | GuardDuty / Sentinel | High — widely deployed |
| Agent Orchestration | LangGraph / Apache Airflow | Bedrock AgentCore | High |
| Vector Memory | Weaviate / Milvus / Qdrant | Vertex Vector Search | High — production ready |
| AI Observability | Langfuse + Arize Phoenix | CloudWatch Bedrock logs | Medium-High |
| Policy Engine | OPA Gatekeeper | Verified Permissions | High |
| Container Security | Falco + Trivy + Cosign | GuardDuty Container | High |

## Related

- [Enterprise Governance](18-enterprise-governance.md)
- [Reference Architecture](20-reference-architecture.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
