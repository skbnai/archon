---
title: "Identity, Claims & Policy Design (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: identity-claims-policy-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol2_Identity_Claims_Policy.md]
tags: [authorization, policy, opa, rego, token-exchange]
covers_version: "as of 2026"
---

Rego/OPA policy design patterns, the Cedar vs. Rego decision matrix, hybrid Cedar+OPA enterprise architecture, and RFC 8693 token exchange for agent delegation.

## Rego / OPA Policy Design

Open Policy Agent (OPA) with the Rego policy language is the de facto standard for infrastructure policy — Kubernetes admission, Terraform validation, network policy, and cross-platform authorization. It is the ideal complement to Cedar in a hybrid architecture.

**OPA deployment patterns:**

| Pattern | Topology | Latency | Use Case |
|---|---|---|---|
| Embedded OPA | OPA Go library compiled into the service | &lt;0.5ms | Ultra-low-latency, single-service |
| OPA Sidecar | OPA container in the same pod/task | 0.5-2ms | Kubernetes/ECS per-service isolation |
| Central OPA Server | Shared OPA cluster (HA) | 2-10ms network | Centralized policy, policy federation |
| OPA + Styra DAS | Managed OPA fleet + central management | 2-10ms | Enterprise OPA at scale |
| OPA + WASM | Rego compiled to WASM, run in browser/edge | &lt;1ms | Edge authorization, CDN enforcement |

**Rego policy examples.** Kubernetes admission, requiring non-root containers:

```rego
package kubernetes.admission.security

deny[msg] {
  input.request.kind.kind == "Pod"
  container := input.request.object.spec.containers[_]
  container.securityContext.runAsNonRoot != true
  msg := sprintf("Container '%v' must run as non-root", [container.name])
}
```

Terraform policy, prohibiting public S3 buckets:

```rego
package terraform.aws.s3

deny[msg] {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket"
  resource.change.after.acl == "public-read"
  msg := sprintf("S3 bucket '%v' must not be public", [resource.address])
}
```

API authorization for agent tool invocation:

```rego
package agent.authorization

import future.keywords.if
import future.keywords.contains

default allow := false

allow if {
  input.action == "invoke_tool"
  input.principal.capabilities[_] == required_capability
  input.context.risk_score < max_risk_threshold
  business_hours
}

required_capability := cap if {
  tool_capability_map[input.resource.tool_name] == cap
}

tool_capability_map := {
  "sql_query_tool": "can_query_database",
  "payment_tool": "can_approve_payment",
  "hr_tool": "can_view_hr_records",
}

max_risk_threshold := 70

business_hours if {
  hour := time.clock(time.now_ns())[0]
  hour >= 8
  hour < 18
}
```

Data classification policy, denying PII access without DLP and SECRET export outside the corporate network:

```rego
package data.classification

deny[msg] if {
  input.resource.classification == "PII"
  not input.context.dlp_active
  msg := "PII resource requires active DLP controls"
}

deny[msg] if {
  input.resource.classification == "SECRET"
  input.action == "export"
  input.context.network_zone != "CORPORATE"
  msg := "SECRET data cannot be exported from non-corporate network"
}
```

## Cedar vs. Rego: Decision Matrix

Cedar and Rego are complementary tools serving different domains. The choice between them should be driven by use case, not preference — the most mature enterprise architectures deploy both, with clear domain boundaries.

| Dimension | AWS Cedar | OPA / Rego | Recommendation |
|---|---|---|---|
| Primary Domain | Application & user authorization | Infrastructure, K8s, cross-platform | Use both in the appropriate domain |
| Policy Language | Cedar DSL — SQL-like, readable | Rego — Datalog-inspired, powerful | Cedar for business, Rego for infra |
| Type Safety | Strongly typed, schema-validated | Dynamically typed | Cedar for type-critical policies |
| Formal Verification | Yes — provably correct policies | No — runtime evaluation only | Cedar where correctness is critical |
| AWS Integration | Native (Amazon Verified Permissions) | Requires self-management or DAS | Cedar wins for AWS-native |
| Kubernetes | Not applicable | First-class (Gatekeeper/Konstraint) | OPA for K8s admission |
| Terraform/IaC | Not applicable | Excellent (OPA Conftest) | OPA for infrastructure policy |
| Ecosystem | AWS-specific, growing | Massive open-source ecosystem | OPA for cross-platform |
| Performance | Sub-millisecond (AVP managed) | 1-5ms sidecar, &lt;0.5ms embedded | Comparable for low-latency |
| Policy Management | AVP Console + CLI | Bundle server (S3) + Styra DAS | Styra DAS for enterprise OPA |
| Decision Logging | Native to AVP | Requires configuration | Cedar easier for compliance logging |
| Multi-tenant | Native entity hierarchy | Custom implementation in Rego | Cedar simpler for multi-tenancy |
| WASM Support | No | Yes — compile to WASM | OPA for edge/CDN enforcement |
| Audit Trail | CloudTrail native integration | OPA decision logs to Elasticsearch | Cedar easier on AWS |
| Learning Curve | Low — business-readable | Medium — Datalog concepts | Cedar for business teams |

## Hybrid Cedar + Rego Architecture

The most effective enterprise architecture uses Cedar and OPA together, with clear domain ownership — this is not a compromise, but an intentional design that leverages the strengths of each engine.

**Two-domain model.** Infrastructure policy runs on OPA/Rego: Kubernetes admission, Terraform validation, network policy, secret access policy, Docker image policy, service mesh mTLS, compliance scanning, and CI/CD pipeline gates, with policy stored as an S3 bundle, managed via Styra DAS, and deployed through GitOps. Application/agent policy runs on AWS Cedar (Verified Permissions): user authorization, agent permissions, tool invocation control, resource access control, memory/knowledge access, payment/trade approval, data classification access, multi-tenant isolation, and audit trail (CloudTrail), with policy in the AVP Policy Store, managed via the AVP console and IaC, and deployed via CI/CD and CodePipeline.

Both domains share a Claims Normalization Service, through which canonical claims flow to both engines, and a Policy Decision Aggregator, which combines Cedar and OPA decisions where a request spans both domains.

**Industry evidence.** Large-scale enterprises commonly run OPA for infrastructure (Kubernetes, deployment pipelines) alongside application-layer policy engines for content and business authorization; AWS-native enterprises use Cedar with Amazon Verified Permissions for fine-grained banking application authorization; and platform companies with heterogeneous stacks use OPA for cross-cutting microservice authorization. The hybrid model is the enterprise standard.

**Decision framework — when to use which engine:**

| Use Case | Recommended Engine | Rationale |
|---|---|---|
| Kubernetes Pod Security | OPA (Gatekeeper) | K8s-native, Gatekeeper is the standard |
| Terraform/CloudFormation policy gates | OPA (Conftest) | IaC scanning is OPA's strongest use case |
| User authorization to invoke an agent | Cedar (AVP) | User-resource model, AWS-native, audit trail |
| Agent permission to call a tool | Cedar (AVP) | Fine-grained, type-safe, traceable |
| Agent access to RAG knowledge | Cedar (AVP) | Document-level entity model, tenant isolation |
| Payment approval workflow | Cedar (AVP) | Formal verification, compliance audit trail |
| Network egress policy | OPA (Envoy integration) | L7 policy, service mesh native |
| CI/CD deployment gates | OPA (Conftest/Rego) | Pipeline integration, multi-cloud |
| Agent memory protection | Cedar (AVP) | Entity hierarchy, per-user scoping |
| Cross-cloud authorization | OPA | Cloud-agnostic, universal engine |
| Service-to-service mTLS policy | OPA (Istio/Envoy) | Service mesh integration standard |
| AI model output filtering | Cedar (AVP) | Structured output classification policy |

## Token Exchange and On-Behalf-Of Flows

Agentic AI introduces a new authorization challenge: an agent acts on behalf of a user, which means the authorization context must carry both the agent's identity and the user's delegated authority. RFC 8693 (OAuth 2.0 Token Exchange) is the standard mechanism.

**Token exchange flow for agent delegation:** the user authenticates and receives an Entra ID JWT scoped to the AI Platform; the agent is invoked with the user's JWT as the subject token; the Token Exchange Service takes the subject token (user JWT), an actor token (agent service JWT), a requested scope (e.g., `agent_tool_invocation`), and a target resource (a specific tool URN); it issues a composite delegation token carrying `sub: agent-runtime-01`, `act.sub: john.smith@bank.com`, `scope: tool:payment_approval`, `delegated_capabilities: [can_approve_payment]`, and delegation constraints such as `{ max_amount: 50000, currency: GBP, expiry: 2026-06-26T10:30:00Z }`; Cedar then evaluates the request using both the agent's identity and the delegated user context.

**Security principle:** the delegation token must enforce the minimum of the user's permissions and the agent's permitted scope. An agent cannot grant itself capabilities the user does not have, nor can the user's token grant the agent capabilities beyond its authorized scope — it is always the intersection of permission sets, never the union.

**Managed identity for AWS services.** For agent-to-AWS-service calls (Bedrock, S3, DynamoDB, etc.), use IAM roles for ECS/EKS task execution rather than long-lived credentials. Two identities operate in parallel and are both required: the IAM Task Role (AWS identity) controls which AWS API calls the ECS task or EKS pod may make, while the Cedar principal (business identity) controls application-layer authorization — tool invocation, user data access, payment approval. IAM controls *what* AWS services can be called; Cedar controls *who* can invoke *what* business action.

## Related

- [Identity, Claims & Policy Design (Part 1)](../25-identity-claims-policy.md)
- [Advanced Policy Engineering](../26-2b-advanced-policy-engineering.md)
- [Agent, Tool & MCP Authorization](../27-agent-tool-mcp-authorization.md)
