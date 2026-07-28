---
title: "AWS Implementation & Governance: Reference Architecture & CI/CD"
doc_type: guide
domain: trust
status: current
topic_id: aws-implementation-governance
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol5_AWS_Implementation_Governance.md]
tags: [authorization, aws, reference-architecture, ci-cd]
covers_version: "as of 2026"
---

The complete AWS reference architecture and component justification matrix for enterprise authorization, performance benchmarks and multi-layer caching, and the policy-as-code CI/CD pipeline.

## AWS Reference Architecture

The architecture layers from the outside in: an external identity layer where Microsoft Entra ID (primary IdP, OIDC/SAML federation) and legacy ADFS federation issue JWTs into the AWS perimeter; an AWS perimeter of WAF plus an optional CloudFront CDN layer; an API Gateway (REST/HTTP) fronted by a Lambda Authorizer that validates the JWT against Entra's JWKS, extracts claims, calls AVP's `IsAuthorized`, and caches the resulting IAM policy.

Only authorized requests reach the Authorization Core, which runs in a VPC:

| Component | Service | Responsibilities |
|---|---|---|
| Claims Normalization | ECS Fargate | Group GUID resolution, role-to-capability mapping, PIP attribute lookup, ElastiCache (Redis) |
| Policy Decision Point | Amazon Verified Permissions (Cedar Policy Store) | Business authorization, agent permissions, tool policies, `IsAuthorized` API |
| Infrastructure Policy | OPA Sidecar Cluster (ECS / K8s DaemonSet) | Infrastructure policy, K8s admission (EKS) |
| Risk Engine | AWS Fraud Detector + GuardDuty | Risk score computation feeding the authorization context |

The Agent Runtime Layer (ECS/EKS/Lambda) runs Amazon Bedrock AgentCore hosting an Orchestrator Agent plus specialist Payment and Data agents, alongside an MCP PEP Gateway (ECS Fargate) that authorizes every tool call per-tool via Cedar. The Data & Knowledge Layer comprises OpenSearch (RAG/memory), DynamoDB (metadata), RDS/Aurora (business data), and S3 (RAG documents), all KMS-encrypted. The Observability & Compliance Layer ties it together: CloudTrail for every API call, CloudWatch for metrics and alarms, X-Ray for distributed tracing, Security Hub and GuardDuty for compliance and threat detection, Config for resource compliance, a DynamoDB Decision Audit Store, and Macie for PII detection in S3.

**AWS component justification matrix:**

| AWS Service | Role in Architecture | Why This Service |
|---|---|---|
| Amazon Verified Permissions (AVP) | Cedar PDP — business and agent authorization | Managed Cedar, no operational burden, native AWS IAM integration, CloudTrail audit |
| API Gateway (REST/HTTP) | Entry PEP — intercept all external requests | Lambda Authorizer integration, WAF attachment, throttling, caching of auth decisions |
| Lambda Authorizer | JWT validation + AVP `IsAuthorized` call + claims normalization trigger | Serverless, per-request, 300-second TTL caching, IAM policy generation |
| Amazon ECS Fargate | Claims normalization service, MCP PEP gateway, agent runtime | Serverless containers, IAM task roles, VPC networking, no EC2 management |
| Amazon EKS | OPA sidecar deployment, Kubernetes workloads | OPA Gatekeeper for admission control, IRSA for pod-level IAM |
| Amazon Bedrock / AgentCore | LLM inference, agent orchestration, tool invocation | Native AWS, Guardrails integration, Bedrock KB for RAG |
| ElastiCache (Redis) | Claims normalization cache, PDP decision cache | Sub-millisecond cache for normalized claims, reduces PIP lookups &gt;95% |
| DynamoDB | PIP attribute store, audit decision log, memory metadata | Serverless, single-digit ms, TTL for expiry, per-tenant partition |
| Amazon OpenSearch | RAG vector search, semantic memory | Vector search with metadata filtering, per-tenant index, fine-grained access control |
| AWS STS | Token exchange for agent delegation (RFC 8693) | AssumeRoleWithWebIdentity for Entra token exchange, temporary credentials |
| AWS KMS | Encryption for all data at rest, per-tenant CMK | Envelope encryption, key policy, CloudTrail key usage audit |
| AWS Secrets Manager | API keys, credentials for downstream systems | Automatic rotation, VPC endpoint, fine-grained IAM access |
| CloudTrail | Authoritative audit log of all API calls including AVP decisions | Immutable, S3-backed, SNS alerts on policy violations |
| AWS WAF | L7 protection: rate limiting, IP blocking, OWASP rules | Blocks known bad actors before reaching the auth layer |
| Step Functions | Human-in-the-loop approval workflow | Wait-for-task-token pattern, Cedar obligation handler |
| EventBridge | Async event-driven agent workflows, policy change events | Schema registry, rule-based routing, dead-letter queues |
| AWS Config | Detect policy configuration drift, compliance rules | Custom Config rules for AVP policy store changes |

## Performance Benchmarks & Caching Strategy

Authorization must not become a performance bottleneck — the goal is to add less than 5ms of P99 latency to any request, which requires aggressive caching at multiple layers.

**Performance targets:**

| Component | P50 Target | P99 Target | Caching Strategy |
|---|---|---|---|
| JWT Signature Validation | &lt;0.5ms | &lt;1ms | JWKS cached in Lambda memory (15 min TTL) |
| Claims Normalization (cache hit) | &lt;1ms | &lt;3ms | ElastiCache Redis, keyed by token hash |
| Claims Normalization (cache miss) | &lt;15ms | &lt;30ms | Directory lookup + role mapping + cache write |
| Cedar AVP `IsAuthorized` (API) | &lt;3ms | &lt;10ms | Lambda Authorizer IAM policy cache (300s TTL) |
| OPA Sidecar Evaluation | &lt;1ms | &lt;3ms | Policy bundle in-memory, partial evaluation |
| Total Authorization Overhead | &lt;5ms | &lt;15ms | All layers combined, warm cache |
| RAG Pre-filter Construction | &lt;0.5ms | &lt;1ms | Derived from cached canonical claims |
| Post-retrieval Cedar Evaluation | &lt;2ms/chunk | &lt;5ms/chunk | Batch `IsAuthorized` for multiple chunks |

**Multi-layer cache architecture.** Layer 1, the Lambda Authorizer's IAM policy cache, keys on token hash plus resource plus action with a 300-second TTL (the API Gateway maximum), achieving roughly a 70% hit rate on repeat API calls and saving about 15ms per hit. Layer 2, the ElastiCache-backed claims normalization cache, keys on `SHA256(raw_jwt)` with a TTL aligned to JWT expiry (typically 3600s), achieving roughly 95% hit rate within a session and saving about 25ms per hit. Layer 3, the PIP attribute cache, keys on `userId + attribute_type` with a short 300-second TTL since attributes can change, achieving roughly 85% hit rate and saving about 10ms per hit. Layer 4, the OPA policy bundle, lives fully in memory with a 30-second refresh cycle and no I/O on evaluation, keeping evaluation latency under 1ms. With all four layers warm, total overhead stays under 5ms at P99.

**Cache invalidation on policy change.** When a policy changes via the AVP console or CI/CD, CloudTrail emits the event, an EventBridge rule detects the `PutPolicy` event, and a Cache Invalidation Lambda flushes the affected Redis keys by policy-scope tag, issues an API Gateway cache invalidation, and notifies the OPA bundle server to force a refresh — writing a `POLICY_CHANGED — cache invalidated` decision-log entry and, for production changes, triggering a PagerDuty/CloudWatch alert.

## Policy-as-Code CI/CD Pipeline

Policies are code. They must be version-controlled, peer-reviewed, automatically tested, staged, deployed, and monitored for drift — non-negotiable for regulated environments.

**Policy CI/CD pipeline.** A developer writes or modifies a Cedar or Rego policy and commits it to a feature branch. Opening a pull request triggers automated checks: `cedar validate` (schema check), `cedar test` (the unit test suite), OPA Conftest (Rego unit tests), a policy linter (naming conventions, required comments), an automatic security-review flag for policies touching financial actions, and a regression test comparing shadow evaluation against production decisions. Once approved by both the security team and a tech lead, the merge to main triggers the CI/CD pipeline, which runs three stages. Stage 1 (staging) deploys to a staging AVP policy store and Rego bundle, runs 100-plus integration test scenarios, replays an hour of production traffic through shadow evaluation, and requires both automated and human sign-off. Stage 2 (canary, 5% of traffic) deploys to a canary AVP policy store, monitors allow/deny/error rates in CloudWatch, auto-rolls-back on more than a 2% delta versus baseline, and runs for at least 30 minutes. Stage 3 (production) performs the full deployment, force-refreshes all OPA sidecars from the updated S3 bundle, logs a `POLICY_DEPLOYED` CloudTrail event, retains a rollback trigger active for 15 minutes, and closes with a one-hour monitoring window.

**Policy testing framework.** Cedar policy test suites are expressed as YAML scenarios with an expected decision, covering happy paths, negative cases, and cross-tenant isolation:

```yaml
# tests/payment_tool_tests.yaml
tests:
  - name: "Finance user with MFA can invoke payment tool in business hours"
    scenario:
      principal:
        type: BankAI::User
        id: "john.smith"
        attributes:
          capabilities: ["can_approve_payment"]
          mfaVerified: true
          businessUnit: "FINANCE"
          geography: "GB"
      action: BankAI::Action::"InvokeTool"
      resource:
        type: BankAI::Tool
        id: "PaymentApprovalTool"
      context:
        businessHours: true
        riskScore: 15
    expected: ALLOW

  - name: "Finance user WITHOUT MFA is denied payment tool"
    scenario:
      principal:
        type: BankAI::User
        id: "jane.doe"
        attributes:
          capabilities: ["can_approve_payment"]
          mfaVerified: false
    expected: DENY

  - name: "Out of hours access denied regardless of capability"
    scenario:
      context:
        businessHours: false
    expected: DENY

  - name: "Cross-tenant access always denied"
    scenario:
      principal:
        attributes: { tenantId: "tenant-a" }
      resource:
        attributes: { tenantId: "tenant-b" }
    expected: DENY
```

## Related

- [AWS Implementation & Governance (Part 2)](parts/31-aws-implementation-governance-part2.md) — enterprise case studies, the embedded-to-centralized migration roadmap, the production readiness checklist, and the final Cedar vs. OPA decision framework
- [AWS/Entra Federation Patterns](30-4b-aws-entra-federation-patterns.md)
- [Compliance & Governance Decision Framework](32-5b-compliance-governance-decision-framework.md)
