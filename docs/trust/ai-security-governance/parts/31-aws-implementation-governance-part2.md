---
title: "AWS Implementation & Governance: Case Studies, Migration & Readiness (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: aws-implementation-governance-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol5_AWS_Implementation_Governance.md]
tags: [authorization, aws, migration, production-readiness]
covers_version: "as of 2026"
---

Enterprise authorization case studies, a four-phase migration roadmap from embedded to centralized authorization, a production readiness checklist, and the final Cedar vs. OPA decision framework.

## Enterprise Case Studies

The following case studies illustrate how industry leaders have implemented externalized authorization, PEP/PDP patterns, and policy-as-code.

A major consumer bank was an early adopter of Amazon Verified Permissions and contributed to Cedar's development, using AVP as the central PDP for all customer-facing banking applications; key design decisions include capability-based policies abstracted from AD groups, per-microservice PEP enforcement using Lambda Authorizers, and CloudTrail as the authoritative audit record, reporting under 3ms P99 authorization latency at production scale.

A large streaming platform deployed OPA as its primary policy engine across a heterogeneous stack (Java, Python, Node.js), running OPA as a sidecar in every service pod with policy bundles distributed via S3 every 30 seconds; its key innovation is partial evaluation — compiling policies to queries that enable database-level filtering for authorization — used for both content authorization and internal service-to-service access control.

A global ride-hailing platform built a Zanzibar-inspired authorization system for fine-grained relationship-based access control, storing relationship tuples in globally consistent storage, computing authorization decisions from relationship graphs, and achieving sub-10ms global latency; it uses OPA for infrastructure policy alongside its custom ReBAC system for user-facing authorization.

Major investment banks implement Fine-Grained Access Control using attribute-based models: ADFS/Entra integration for identity, claims normalization to canonical banking roles (trader, approver, risk manager), Cedar/XACML-style policies for per-instrument data access, and immutable audit trails meeting MiFID II and DORA requirements, with trade-level authorization considering instrument type, trading book, region, and counterparty in a single policy evaluation.

AWS itself uses Cedar internally for S3 bucket policies, IAM, and Verified Permissions, contributing formal verification via the Lean theorem prover so that Cedar policies can be mathematically proven non-contradictory — particularly relevant for banking regulation, where authorization policies can be submitted to regulators as formally verified artifacts rather than just code.

A major enterprise software vendor manages OPA across hundreds of services using a declarative authorization management service: an OPA sidecar per service, policies distributed from a central management server, decision logs to Elasticsearch, and a GitOps policy workflow with automated PR reviews, reporting 99.99% authorization availability with under 2ms P99 sidecar evaluation.

## Migration Roadmap: Embedded to Centralized Authorization

Migrating from embedded authorization code to a centralized policy engine is a multi-phase program, sequenced to minimize risk while delivering early value.

**Phase 1 — Foundation (Weeks 1-6).** Establish the authorization platform foundation with no application changes yet: provision the AVP policy store; deploy the OPA sidecar cluster on ECS/EKS; implement the Entra ID/ADFS claims normalization service; build the canonical claims model and role-to-capability mapping; establish the Git repository for policy-as-code; configure CloudTrail for AVP decision logging; and define the Cedar entity schema for the domain.

**Phase 2 — Shadow Mode (Weeks 7-12).** Deploy Cedar/OPA in shadow mode alongside the existing embedded authorization: every request is evaluated by both the existing code and the new policy engine, without changing production behavior. Deploy the Lambda Authorizer with shadow evaluation mode; route all requests through the new PEP in pass-through mode initially; compare Cedar decisions against embedded-code decisions; log and resolve every mismatch in policy or canonical claims; and achieve greater than 99.9% decision parity before proceeding.

**Phase 3 — Canary Enforcement (Weeks 13-18).** Enable policy enforcement for 5-20% of traffic, monitor closely, and expand gradually as confidence grows, rolling back immediately if the mismatch rate exceeds threshold: enable Cedar enforcement for 5% of traffic; monitor authorization metrics in CloudWatch (allow rate, deny rate, latency); expand to 20%, 50%, 80%, and 100% over two-week increments; maintain an automated rollback trigger at greater than 1% unexpected deny rate; and complete removal of embedded authorization checks from application code.

**Phase 4 — Full Production (Weeks 19-24).** Complete the migration: 100% of traffic through the centralized policy engine; embedded authorization code removed from all services; complete compliance documentation (NIST, PCI DSS evidence packages); policy simulation capability deployed for pre-production testing; policy drift detection active via Config rules; and performance optimization complete with a cache hit rate above 90%.

## Production Readiness Checklist

The following checklist must be completed before a policy-enforced authorization system is deemed production-ready for regulated enterprise deployment.

**Identity & claims:** JWT signature validation against a live JWKS endpoint; claims normalization handling both ADFS and Entra ID tokens; group GUID resolution with caching (max 5-minute TTL); role-to-capability mapping complete for all business domains; nested group flattening tested with five or more levels; large-JWT handling via the reference-token pattern for tokens over 4KB; RFC 8693 token exchange tested for agent delegation.

**Cedar policy design:** entity schema validated with `cedar validate`; a default-deny policy is the first policy in every policy set; tenant isolation forbid policies present and tested; all policies reference canonical capabilities rather than Entra groups; policy unit tests achieve greater than 95% decision coverage; shadow evaluation achieves greater than 99.9% parity with the existing system; policy versioning and rollback procedures documented and tested.

**Performance:** P99 authorization latency under 15ms including all cache layers; claims normalization cache hit rate above 90%; AVP `IsAuthorized` P99 under 10ms; PDP horizontal auto-scaling tested to 10x baseline load; cache invalidation tested so stale decisions clear within 5 minutes of a policy change.

**Security:** all PEPs enforce default-deny (an unreachable PDP means deny); mTLS between all internal authorization components; secrets held in Secrets Manager, never in environment variables; KMS encryption for all data at rest with per-tenant CMKs in multi-tenant deployments; VPC endpoints for AVP, DynamoDB, and S3 so authorization traffic never egresses to the internet; GuardDuty enabled and alerting on authorization anomalies; the STRIDE threat model documented and reviewed.

**Audit & compliance:** CloudTrail enabled and capturing all AVP policy decisions; decision logs include principal, action, resource, context hash, decision, and matched policy; audit log retention meets regulatory requirements (PCI DSS: one year online plus one year archive); NIST 800-53 control mapping documented; PCI DSS Requirements 7, 8, and 10 evidence packages generated; SOC 2 CC6 control evidence available.

**Operations:** policy CI/CD pipeline operational with under 15-minute deploy time; policy drift detection alerting configured via Config rules; emergency policy rollback tested end-to-end in under 5 minutes; an on-call runbook exists for authorization-related incidents; a monthly policy review meeting is scheduled; a quarterly access review process runs against the Cedar entity audit.

**Agent-specific:** per-step authorization enforced at all seven agent decision points; agent delegation tokens constrained to the minimum required scope; the MCP PEP gateway deployed and tested for all tools; the human-in-the-loop obligation handler tested for high-risk actions; the RAG pre-retrieval filter tested for tenant isolation; memory authorization policies tested against cross-user access; the output classification filter deployed and tested for PII leakage.

## Final Decision Framework

The decision framework summarizes when to use Cedar, when to use OPA/Rego, and when to use both — the definitive guidance for enterprise architects building on this reference architecture.

| Use Case | Cedar (AVP) | OPA/Rego | Hybrid |
|---|---|---|---|
| Application authorization | Primary choice | | If cross-cloud needed |
| Agent permissions | Best fit — typed, auditable | | |
| Tool invocation control | Per-tool entity model | | |
| Kubernetes admission | | First-class support | |
| Terraform/IaC policy | | Conftest standard | |
| Infrastructure security | | Universal | |
| AWS-native deployment | No operational burden | | OPA for the K8s layer |
| Multi-cloud deployment | | Cloud-agnostic | |
| Formal verification needed | Provably correct | | |
| Large enterprise (&gt;100 services) | | | Cedar for business, OPA for infra |
| RAG authorization | Document entity model | | |
| Memory protection | User scope model | | |
| Service mesh policy | | Envoy/Istio native | |
| Edge/WASM deployment | | WASM compilation | |
| Regulatory banking compliance | CloudTrail native audit | | OPA for infra compliance |

**Best practice — final recommendation.** For the described environment (AWS, Entra ID, Agentic AI, banking regulation), deploy Amazon Verified Permissions (Cedar) as the primary authorization engine for all application, agent, tool, RAG, and memory authorization decisions. Deploy OPA/Rego for Kubernetes admission control (EKS), Terraform policy gates, and infrastructure compliance. Use a shared claims normalization service to provide canonical claims to both engines. This hybrid architecture is the most mature, auditable, and operationally sound choice for regulated financial services.

## Related

- [AWS Implementation & Governance (Part 1)](../31-aws-implementation-governance.md)
- [Compliance & Governance Decision Framework](../32-5b-compliance-governance-decision-framework.md)
- [Policy & Authorization Series Overview](../02-policy-authorization-series-overview.md)
