---
title: "Policy & Authorization Series Overview"
doc_type: guide
domain: trust
status: current
topic_id: policy-authorization-series-overview
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol0_Series_Index_and_Overview.md]
tags: [authorization, ai-security, policy, cedar, opa]
covers_version: "as of 2026"
---

Series index for the Enterprise AI Authorization volumes: policy engine selection, per-step agent authorization, MCP security, RAG data protection, and AWS production governance.

## About This Series

The Enterprise Policy Interceptor Architecture for Agentic AI covers the full authorization stack: policy engine selection and hybrid architectures, per-step agent authorization, MCP security, RAG data protection, and production governance. The series is written for enterprise architects, security engineers, platform engineers, and compliance officers at organizations deploying AI agents in regulated environments — particularly banking, financial services, healthcare, and government.

**Series volume map:**

| Volume | Title | Primary Topics | Key Deliverables |
|---|---|---|---|
| 1 | Executive Architecture & Authorization Fundamentals | Authorization landscape; PEP/PDP/PAP/PIP; Zero Trust; embedded vs. externalized; STRIDE threat model; compliance mapping | Authorization engine comparison; PEP pattern matrix; STRIDE analysis; compliance control map; anti-pattern catalogue |
| 2 | Identity, Claims & Policy Design | ADFS & Entra ID federation; JWT claims normalization; canonical enterprise claim model; Cedar policy design; Rego policy design; hybrid architecture | Canonical claims schema; role-to-capability mapping; Cedar entity schema and policy patterns; Rego policy examples; Cedar vs. Rego matrix |
| 3 | Agent, Tool & MCP Authorization | Agent authorization lifecycle; per-step policy evaluation; tool capability taxonomy; contextual signals; MCP server security; multi-agent workflows; human-in-the-loop | Agent authorization decision matrix; tool capability catalogue; context signal catalogue; MCP authorization architecture; HITL Cedar patterns |
| 4 | RAG, Memory & Data Authorization | Document-level authorization; chunk-level filtering; vector database pre/post filtering; memory type taxonomy; multi-tenant isolation; output classification; DLP integration | RAG authorization pipeline; document metadata schema; Cedar RAG policies; memory authorization patterns; tenant isolation framework |
| 5 | AWS Implementation & Governance | AWS reference architecture; component justification; performance benchmarks; caching strategy; policy CI/CD; enterprise case studies; migration roadmap; production checklist | AWS architecture diagram; performance targets; CI/CD pipeline; test framework; migration phases; production readiness checklist |

**Reading guide by role:**

| Role | Must Read | Recommended |
|---|---|---|
| Enterprise Architect | All volumes | Focus on Vol 1 frameworks and Vol 5 AWS architecture |
| Security Engineer | Vol 1, 2, 3 | Vol 4 for data security; Vol 5 for threat model |
| Platform/DevOps Engineer | Vol 5, Vol 2 (policy CI/CD) | Vol 3 for MCP/tool deployment patterns |
| Compliance Officer | Vol 1 (compliance section), Vol 5 (checklist) | Vol 4 for data residency and DLP |
| AI/ML Engineer | Vol 3 (agent auth), Vol 4 (RAG/memory) | Vol 2 for Cedar policy context |
| Identity/IAM Engineer | Vol 2 (claims normalization) | Vol 1 for authorization landscape |
| CTO / CISO | Vol 1 (executive summary), Vol 5 (case studies) | Series index (this page) |

## Key Architectural Decisions at a Glance

- **Authorization Engine:** Amazon Verified Permissions (Cedar) for application/agent authorization; OPA/Rego for infrastructure and Kubernetes. Hybrid architecture with shared claims normalization.
- **PEP Location:** API Gateway Lambda Authorizer (external requests) + application middleware (internal fine-grained) + MCP PEP Gateway (tool invocation).
- **Identity Integration:** Entra ID (primary OIDC) + ADFS (legacy SAML federation) flowing through a Claims Normalization Service into canonical claims, which populate the Cedar entity context.
- **Claims Abstraction:** Entra groups and roles are never referenced directly in Cedar policies — they are always mapped to business capabilities in the normalization layer.
- **Default Posture:** Default deny everywhere. An unreachable PDP means deny. Missing context means deny. Explicit permit is required for every authorized action.
- **Agent Trust Model:** Agents receive the intersection of their permitted scope and the delegating user's capabilities — never the union. Scope is constrained at delegation time.
- **Tenant Isolation:** Mandatory Cedar forbid policies enforce tenant isolation at the policy layer, defended in depth by storage partition, IAM, and network layer controls.
- **Caching Strategy:** A four-layer cache — Lambda IAM policy cache, ElastiCache claims cache, ElastiCache PIP cache, OPA in-memory bundle — targets a &gt;90% cache hit rate.
- **Audit Trail:** CloudTrail captures every Amazon Verified Permissions `IsAuthorized` call. Decision logs record principal, action, resource, context hash, policy matched, and decision reason.
- **Policy Lifecycle:** GitOps — policies in Git, PR review, automated tests, shadow evaluation, canary deploy, production, drift detection — with a target of &lt;15 min deploy and &lt;5 min rollback.

## Authorization Component Quick Reference

| Component | AWS Service / Tech | Volume Reference |
|---|---|---|
| Primary PDP (Business) | Amazon Verified Permissions (Cedar) | Vol 1, 2 |
| Infrastructure PDP | OPA / Rego (ECS sidecar / EKS DaemonSet) | Vol 2 |
| API Gateway PEP | API Gateway + Lambda Authorizer | Vol 1, 5 |
| Tool/MCP PEP | ECS Fargate MCP Gateway | Vol 3 |
| Claims Normalization | ECS Fargate microservice + ElastiCache | Vol 2 |
| PIP Attribute Store | DynamoDB + ElastiCache Redis | Vol 1, 5 |
| Risk Engine | AWS Fraud Detector + GuardDuty | Vol 3, 5 |
| RAG Vector Search | OpenSearch (with pre-filter) | Vol 4 |
| Memory Store | DynamoDB + Redis + S3 | Vol 4 |
| Output Filter / DLP | Bedrock Guardrails + Amazon Macie | Vol 4 |
| Human Approval Workflow | AWS Step Functions (wait-for-task) | Vol 3 |
| Audit Log | CloudTrail to S3 (immutable) | Vol 5 |
| Policy Store (Cedar) | AVP Policy Store | Vol 2, 5 |
| Policy Store (OPA) | S3 Bundle Server | Vol 2, 5 |
| Policy CI/CD | CodePipeline / GitHub Actions | Vol 5 |
| Token Exchange | AWS STS + RFC 8693 Service | Vol 2 |
| Encryption | AWS KMS (per-tenant CMK) | Vol 5 |
| Secrets Management | AWS Secrets Manager | Vol 5 |
| Threat Detection | GuardDuty + Security Hub | Vol 5 |

**Best practice.** This series represents the state of the art in enterprise Agentic AI authorization as of 2026. The frameworks, patterns, and AWS services described are production-validated across large-scale enterprise deployments. The hybrid Cedar + OPA architecture with canonical claims normalization is the reference architecture recommended for regulated AWS-hosted Agentic AI deployments.

## Series Contents

1. [Executive Architecture & Authorization Fundamentals](23-executive-architecture.md)
2. [Authorization Deep Dive: Identity, Claims & Policy Design](24-1b-authorization-deep-dive.md)
3. [Identity, Claims & Policy Design](25-identity-claims-policy.md)
4. [Advanced Policy Engineering](26-2b-advanced-policy-engineering.md)
5. [Agent, Tool & MCP Authorization](27-agent-tool-mcp-authorization.md)
6. [Agent Authorization Deep Dive](28-3b-agent-authorization-deep-dive.md)
7. [RAG, Memory & Data Authorization](29-rag-memory-data-authorization.md)
8. [AWS/Entra Federation Patterns](30-4b-aws-entra-federation-patterns.md)
9. [AWS Implementation & Governance](31-aws-implementation-governance.md)
10. [Compliance & Governance Decision Framework](32-5b-compliance-governance-decision-framework.md)

## Related

- [AI Control Series Overview](01-ai-control-series-overview.md)
- [Trust Hub](../index.md)
