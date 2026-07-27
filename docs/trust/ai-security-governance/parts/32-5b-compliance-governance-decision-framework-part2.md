---
title: "Compliance & Governance: Anti-Pattern Catalogue & Final Decision Framework (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: 5b-compliance-governance-decision-framework-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol5b_Compliance_Governance_Decision_Framework.md]
tags: [authorization, anti-patterns, cedar, opa, decision-framework]
covers_version: "as of 2026"
---

A complete 15-item authorization anti-pattern catalogue with remediation, and the series' definitive Cedar vs. OPA vs. hybrid decision framework with supporting industry evidence.

## Complete Anti-Pattern Catalogue with Remediation

The following is an exhaustive catalogue of authorization anti-patterns observed in enterprise AI deployments, with specific remediation guidance for each.

1. **[Critical] Authorization Logic in Business Code.** Anti-pattern: `if user.role == 'admin' or user.group in ['Finance_Approvers', 'Payments_Admins']: execute_payment()`. Remediation: extract all authorization logic to Cedar/OPA; the business service calls the PEP, receives Allow/Deny, and only executes on Allow — zero authorization logic in service code.
2. **[High] Direct Identity Store References in Policy.** Anti-pattern: a Cedar policy that checks `principal.groups contains 'Payments_Admins_GUID_abc123'`. Remediation: map Entra groups to canonical capabilities in the normalization layer, so Cedar policies reference only capabilities: `when principal.capabilities contains 'can_approve_payment'`.
3. **[Critical] No Default Deny.** Anti-pattern: authorization returns Allow unless an explicit Deny rule is found (a deny-unless-permitted model). Remediation: Cedar's default is deny with no policy needed; in OPA, set `default allow := false`; the API Gateway Lambda Authorizer should throw an exception on any non-Allow path.
4. **[High] Overly Large JWTs.** Anti-pattern: encoding 500+ group GUIDs in the JWT, producing 8KB tokens that exceed HTTP header limits. Remediation: use the reference-token pattern — issue an opaque token to the client and have the PIP Lambda introspect for full attributes, or use SCIM to pre-populate DynamoDB so the JWT carries only the user ID.
5. **[High] No Policy Versioning.** Anti-pattern: policies edited directly in the AVP console without version control or change history. Remediation: manage all policies in Git as code, populate AVP only via the CI/CD pipeline, and use Git commit history for version control — rollback becomes `git revert` plus a pipeline run.
6. **[Critical] Policy Evaluation After Execution.** Anti-pattern: the agent executes a tool action, then logs the decision, attempting to "undo" it if unauthorized. Remediation: authorization is always evaluated before execution — Cedar's `IsAuthorized` returns before any business logic runs, with no exceptions.
7. **[Critical] Missing Decision Logging.** Anti-pattern: authorization decisions are made but not logged, leaving no record of what was permitted or denied. Remediation: every Cedar `IsAuthorized` call produces an audit record (CloudTrail plus DynamoDB), and both Allow and Deny decisions are logged with full context.
8. **[High] Shared Agent Identity.** Anti-pattern: all agents run under a single shared identity (e.g., `agent-service`), making individual accountability impossible. Remediation: give each agent instance a unique identity composed of agent type, task ID, and timestamp, with delegation carrying the individual user's identity in the `act` claim.
9. **[Critical] No Tool Authorization.** Anti-pattern: the agent selects and invokes tools based purely on LLM reasoning with no policy enforcement, so any tool can be called by any agent. Remediation: route every tool invocation through Cedar authorization, restricting tool access by agent type, user capability, context, and tool-specific policies.
10. **[High] Transitive Trust Between Agents.** Anti-pattern: the orchestrator agent vouches for sub-agent permissions, and sub-agents inherit the orchestrator's full permission set. Remediation: trigger an independent Cedar evaluation at every agent boundary; sub-agent scope must be the intersection of the orchestrator's scope and the sub-agent's permitted scope, never the union.
11. **[High] Single-Environment Policy Store.** Anti-pattern: development, staging, and production all use the same Cedar policy store, so dev policy changes affect production. Remediation: maintain separate AVP policy stores per environment, have the CI/CD pipeline deploy environment-specifically, and protect the production store with SCPs and an IAM condition requiring the pipeline role.
12. **[Critical] No Tenant Isolation in RAG.** Anti-pattern: vector similarity search returns results from all tenants, with tenant filtering applied only at the application layer where it can be bypassed. Remediation: apply the tenant filter as a mandatory metadata filter in the vector query itself (pre-retrieval), backed by post-retrieval Cedar per-chunk authorization as defense in depth.
13. **[Medium] Permissive Cache TTL.** Anti-pattern: authorization decisions cached for 24 hours, so policy changes aren't reflected until the cache expires. Remediation: align cache TTL with JWT expiry (a maximum of 1 hour for the claims cache), set the API Gateway decision cache to 300 seconds, and invalidate the cache immediately on policy change via EventBridge.
14. **[High] No Shadow Evaluation Before Enforcement.** Anti-pattern: new authorization policies deployed directly to production without comparing decisions against the existing system. Remediation: make a shadow-evaluation phase mandatory, achieving greater than 99.9% decision parity before any enforcement, running for at least one hour of production traffic.
15. **[Critical] Authorization Bypass via Direct AWS API Calls.** Anti-pattern: the agent calls S3, DynamoDB, or other AWS services directly via its IAM role, bypassing Cedar authorization entirely. Remediation: keep agent IAM task roles minimally scoped (e.g., `bedrock:InvokeModel` only), route all data access through authorized service APIs, and have S3 bucket policies deny direct agent access.

## The Definitive Decision Framework

This section provides the final, authoritative guidance on authorization engine selection, synthesizing the research across this series into a decision framework supported by industry evidence and implementation patterns.

**When Cedar (AVP) is the clear choice:** for AWS-native deployments, since no other engine integrates as deeply with API Gateway, Lambda, Bedrock, and CloudTrail, and AVP is a managed service with no operational burden; for type-safe business authorization, since Cedar's schema validation and formal verification make it the only engine that can be submitted to regulators as a formally correct authorization system; for banking and other regulated authorization, since Cedar's native CloudTrail integration satisfies PCI DSS Req 10 with zero additional configuration; for agent and tool permissions, since Cedar's entity model naturally represents agent types, tool capabilities, and delegation relationships in a single coherent schema; for multi-tenant SaaS with policy delegation, since Cedar templates and entity hierarchies are purpose-built for multi-tenant policy management; and where fast time-to-value matters, since Cedar policies read like business rules and the security team can write and review them without deep systems-programming knowledge.

**When OPA/Rego is the clear choice:** for Kubernetes and container security, where OPA Gatekeeper is the CNCF-blessed standard for admission control with no comparable ecosystem support elsewhere; for infrastructure-as-code policy gates, where Conftest plus Rego is the standard for Terraform and Helm chart validation in CI/CD; for multi-cloud or cloud-agnostic requirements, since OPA runs identically on AWS, Azure, GCP, and on-premises while Cedar is AWS-specific; where an existing OPA investment already exists, since adding Cedar would create two policy ecosystems to maintain for application authorization; for service mesh policy, since OPA integrates natively with Envoy, Istio, and Linkerd for L7 policy while Cedar has no service-mesh integrations; and for edge/WASM enforcement, since only OPA can compile policies to WebAssembly for enforcement at CDN edge locations.

**When the hybrid architecture wins.** The hybrid architecture — Cedar for application/agent authorization, OPA for infrastructure policy — is the strongest choice for enterprise deployments where: the organization runs EKS and has application authorization requirements simultaneously; Terraform IaC policy gates are required in addition to runtime authorization; a service mesh (Istio/Envoy) provides East-West traffic policy enforcement; the organization is large enough to justify the operational investment in two policy engines; regulatory requirements mandate both infrastructure-level and application-level authorization evidence; or development teams already have Rego expertise that would be lost by migrating entirely to Cedar.

**Best practice — final verdict for the described environment.** An enterprise running AWS, Entra ID, EKS plus ECS, Bedrock AgentCore, banking regulation, multi-tenancy, and Agentic AI should implement the hybrid architecture: Amazon Verified Permissions (Cedar) for all user, agent, tool, RAG, and memory authorization decisions, paired with OPA/Gatekeeper on EKS for Kubernetes admission control, Conftest for Terraform policy gates, and OPA plus Envoy for service mesh L7 policy. A shared claims normalization service provides canonical identity context to both engines. This is not a compromise — it is intentional specialization that delivers the strongest security posture, the clearest compliance evidence, and the most maintainable long-term authorization architecture.

## Additional Industry Evidence: Fine-Grained Authorization at Scale

Beyond the Cedar and OPA deployments already covered in [AWS Implementation & Governance (Part 2)](../parts/31-aws-implementation-governance-part2.md) — Capital One, Netflix, Uber, Goldman Sachs, Intuit, and AWS's own internal use of Cedar — one further data point rounds out the picture for relationship-based authorization at scale: Auth0's Fine-Grained Authorization product (now Okta FGA, built on OpenFGA/Zanzibar) demonstrates the ReBAC model in large multi-tenant SaaS production environments, with published benchmarks showing over 100,000 authorization checks per second at consistently sub-5ms latency. This confirms that relationship-based authorization — used as a complement to Cedar in a hybrid model, per the [Authorization Deep Dive](../24-1b-authorization-deep-dive.md)'s OpenFGA discussion — is production-proven at significant scale, not just a theoretical pattern.

## Related

- [Compliance & Governance: Regulatory Control Mapping (Part 1)](../32-5b-compliance-governance-decision-framework.md)
- [AWS Implementation & Governance](../31-aws-implementation-governance.md)
- [Policy & Authorization Series Overview](../02-policy-authorization-series-overview.md)
