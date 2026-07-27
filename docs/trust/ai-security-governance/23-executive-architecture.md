---
title: "Executive Architecture & Authorization Fundamentals"
doc_type: guide
domain: trust
status: current
topic_id: executive-architecture
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol1_Executive_Architecture.md]
tags: [authorization, ai-security, policy, cedar, opa, zero-trust]
covers_version: "as of 2026"
---

The enterprise authorization landscape for Agentic AI: externalized authorization theory, PEP/PDP/PAP/PIP architecture, Zero Trust principles, engine selection, STRIDE threat modeling, and regulatory compliance mapping.

## Executive Summary

This volume presents a comprehensive, implementation-oriented architecture for building an enterprise-grade authorization and request interception framework for Agentic AI systems deployed on AWS. The framework externalizes authorization decisions from application code and enforces them through policy-as-code using AWS Cedar (Amazon Verified Permissions) and Open Policy Agent (OPA/Rego).

Modern enterprises — particularly those in regulated industries such as banking, healthcare, and government — face an unprecedented challenge: AI agents now act autonomously on behalf of users, invoking tools, querying knowledge stores, accessing databases, and calling enterprise APIs. Each of these actions must be subject to the same rigorous authorization controls as any human user interaction, yet traditional authorization models were never designed for non-human actors operating at machine speed.

**Best practice:** every request made by an agent, tool, workflow, API, MCP server, RAG system, memory system, or downstream application must be policy-evaluated before execution. This is not optional in regulated environments — it is a compliance requirement under PCI DSS, SOC 2, NIST 800-53, and the EU AI Act.

**Target environment:**

| Dimension | Detail |
|---|---|
| Cloud Platform | Amazon Web Services (AWS) |
| Agent Runtime | ECS / EKS / Lambda / Amazon Bedrock AgentCore |
| Identity Provider | Microsoft Entra ID (primary) + legacy ADFS federation |
| Authentication | SAML 2.0 / OIDC — JWT tokens with enterprise claims |
| API Protection | OAuth 2.0 / OIDC for enterprise application APIs |
| Tool Surface | MCP servers exposing discrete tools |
| Authorization Engine | AWS Cedar (Amazon Verified Permissions) + OPA/Rego |
| Architecture Pattern | Zero Trust — default deny, policy-evaluated every request |
| Deployment Model | Multi-tenant, multi-agent workflows |
| Regulatory Context | Banking: PCI DSS, SOC 2, NIST 800-53, DORA, EU AI Act |

## Why Externalized Authorization?

**The problem with embedded authorization.** The dominant pattern in enterprise software for decades has been embedding authorization logic directly within application code: checking roles in service methods, validating permissions in controllers, or hardcoding group membership checks. This creates structural problems that compound as systems grow: authorization logic drift (each service re-implements authorization logic independently, leading to inconsistency and divergence); policy invisibility (rules buried in code that security teams cannot audit or modify without a full deployment cycle); no separation of concerns (business logic and security policy entangled so a change to either requires touching the same codebase); inability to audit (no central record of what decisions were made, when, and why); agent incompatibility (AI agents operate as non-human principals at machine speed with parallelism that embedded authorization cannot scale to or reason about); and compliance failure (regulatory frameworks require demonstrable, auditable access controls that code-embedded authorization cannot satisfy without exhaustive code reviews).

**Anti-pattern:** `if (user.groups.contains('Finance_Approvers')) { approvePayment(); }` embeds identity-store details, business rules, and authorization logic in a single statement. It cannot be audited, versioned, tested, or changed without a code deployment.

**The externalized authorization model.** Externalized authorization separates the authorization decision from the application code: the application delegates the authorization question to a dedicated policy engine and acts on the result. This is the foundation of all modern enterprise authorization frameworks. The flow transforms from a tightly coupled embedded check (`Request → Application Code → IF role check THEN execute ELSE reject`) to a structured policy evaluation pipeline (`Request → PEP (intercept) → PDP (evaluate) → Decision → PEP (enforce) → Service`).

**The three pillars of modern enterprise authorization:** Authentication answers "who are you?" — it verifies the identity of a principal (user, service, agent), produces a verified identity token (JWT), and is managed by Entra ID, ADFS, or an IdP; authorization does not begin until identity is established. Authorization answers "what are you allowed to do?" — it determines whether the authenticated principal may perform a specific action on a specific resource in a given context, is managed by the policy engine (Cedar/OPA), and is context-dependent, evaluated at request time. Business Logic answers "how should it be done?" — it is the actual execution of the operation after authorization is confirmed; business services never make authorization decisions themselves, they trust the PEP enforcement layer.

## Authorization Architecture: PEP, PDP, PAP, PIP

The XACML-originated model of Policy Enforcement Point, Policy Decision Point, Policy Administration Point, and Policy Information Point remains the definitive reference architecture for externalized authorization. All modern systems — Cedar, OPA, OpenFGA, Permit.io — are implementations of this model.

| Component | Role | AWS Implementation | Key Characteristics |
|---|---|---|---|
| PEP (Enforcement) | Intercepts every request; enforces the decision returned by the PDP; never executes without a positive decision | API Gateway Lambda Authorizer, Envoy sidecar, App Mesh, ALB listener rules, application middleware | Must be in the critical path; zero-trust default deny if PDP is unreachable; logs every decision |
| PDP (Decision) | Evaluates the request against applicable policies and returns Allow/Deny with optional obligations | Amazon Verified Permissions (Cedar), OPA sidecar/central server, Styra DAS | Stateless, deterministic evaluation; must be low-latency (&lt;5ms P99); horizontally scalable |
| PAP (Administration) | Where policies are authored, reviewed, tested, versioned, and deployed | AVP Policy Store, OPA Bundle Server (S3), Git repository, Styra DAS console, CI/CD pipeline | GitOps-driven; policy-as-code; version controlled; PR-based review; automated testing |
| PIP (Information) | Provides additional attributes about the subject, resource, or environment required for policy evaluation | DynamoDB attribute store, ElastiCache, Directory Lookup Lambda, SCIM endpoint, STS, Secrets Manager | Enriches the authorization context; cached aggressively; authoritative source of truth for attributes |

**PEP implementation patterns.** The PEP is the most architecturally sensitive component — it must sit in the critical path of every request while adding minimal latency. Enterprises implement PEPs at multiple layers:

| Pattern | Technology | Latency | Best For |
|---|---|---|---|
| API Gateway Authorizer | AWS Lambda Authorizer | 10-50ms | REST APIs, external-facing services |
| Envoy/Service Mesh Filter | Istio + OPA, AWS App Mesh | 1-5ms | Internal microservices, East-West traffic |
| Application Middleware | FastAPI, Express, Spring Filter | 0.5-2ms | Fine-grained business-context authorization |
| gRPC Interceptor | UnaryInterceptor / StreamInterceptor | 0.5-2ms | gRPC service-to-service calls |
| Sidecar Container | OPA sidecar on ECS/EKS pod | 1-3ms | Language-agnostic, containerized services |
| Reverse Proxy | NGINX + OPA, Kong Gateway | 2-10ms | Legacy application fronting |
| Event Stream Filter | EventBridge Rule + Lambda | Async | Event-driven agent workflows |

## Authorization Engine Landscape

Enterprises have multiple policy engine options. The choice depends on the authorization model required, the existing technology stack, the scale of policy management, and the specific use case (infrastructure vs. application vs. agent authorization).

| Engine | Language | Model | Strength | Weakness | Best For |
|---|---|---|---|---|---|
| AWS Cedar (Verified Permissions) | Cedar | RBAC+ABAC+ReBAC | Type-safe, provably correct, AWS-native, formal verification | AWS-only, no infrastructure policy | Application & agent authorization on AWS |
| OPA / Rego | Rego (Datalog-like) | General purpose | Universal, Kubernetes-native, WASM, rich ecosystem | Rego learning curve, no built-in schema validation | Infrastructure, K8s admission, cross-platform |
| XACML | XML Policy | ABAC | Standards-based, mature, rich attribute model | Verbose XML, complex, slow adoption | Legacy enterprise, government standards compliance |
| OpenFGA | OpenFGA DSL | ReBAC (Zanzibar) | Relationship-first, Google Zanzibar-inspired | Relatively new, limited ABAC | Fine-grained relationship-based permissions |
| Zanzibar / SpiceDB | Zed language | ReBAC | Proven at Google scale, consistent global authorization | Operational complexity, self-managed | Global-scale relationship authorization |
| Permit.io | Policy-as-code + UI | RBAC+ABAC+ReBAC | Developer-friendly, multi-model, managed | SaaS dependency, cost at scale | Teams needing rapid policy iteration |
| Styra DAS | Rego + UI | OPA management | Enterprise OPA management, GitOps, audit logs | OPA dependency, cost | Enterprise OPA fleet management |
| Oso | Polar language | RBAC+ReBAC | Embedded in app, simple syntax, developer-first | Less ecosystem, limited at enterprise scale | Developer-embedded authorization |

**Best practice — enterprise recommendation:** for AWS-hosted Agentic AI with Entra ID, the optimal architecture combines AWS Cedar (Amazon Verified Permissions) for application and agent authorization with OPA/Rego for infrastructure and Kubernetes policy. These are complementary, not competing, engines.

## Zero Trust Architecture for Agentic AI

Zero Trust mandates that no request — regardless of its origin, network position, or prior authentication — is trusted by default. Every request must be explicitly verified, authorized, and continuously validated. For Agentic AI, this principle is not merely desirable; it is essential.

| Zero Trust Principle | Implementation for Agentic AI |
|---|---|
| Never Trust, Always Verify | Every tool call, API request, and memory access by an agent is independently authorized, even within a single agent workflow |
| Least Privilege Access | Agents receive the minimum permissions required for their specific task; permissions are not inherited from the invoking user wholesale |
| Assume Breach | Authorization decisions are logged, monitored, and anomaly-detected; agents cannot escalate privileges even if a component is compromised |
| Explicit Verification | Every authorization decision includes the principal identity, resource, action, context, and policy reason |
| Micro-segmentation | Agent-to-agent, agent-to-tool, and agent-to-data access are separately authorized — no transitive trust |
| Continuous Validation | Authorization is re-evaluated at each action boundary; a session-level token is insufficient for tool-level authorization |

## The Request Interceptor Pattern

The request interceptor is the architectural foundation that transforms embedded authorization into externalized policy evaluation — the PEP in practice. The following pipeline represents the authoritative request flow for an Agentic AI system; every layer is mandatory for regulated enterprise deployments: API Gateway (WAF, rate limiting, TLS); JWT Validation (signature, expiry, issuer); Claims Extraction (Entra ID/ADFS JWT claims); Claims Normalization (canonical enterprise claims); Request Context Builder (time, geo, risk, MFA, device); Risk Engine (threat score, anomaly); Policy Decision Point (Cedar/OPA evaluation against the policy store and PIP attributes, returning Allow/Deny plus obligations); Decision Logging (CloudTrail, audit store); Business Service execution (if allowed); Agent Runtime; Tool Authorization (per-tool Cedar policy re-evaluation); Output Filter/Audit.

**Critical design principle:** authorization is evaluated at every boundary crossing, not just at the API gateway. An agent invoking a tool, a tool querying a database, and the agent reading from memory are all separate authorization events requiring independent policy evaluation.

## Threat Model: STRIDE for Agentic AI Authorization

Applying the STRIDE threat model to the authorization layer identifies the key threats that the policy interceptor architecture must mitigate:

| Threat | Example in Agentic AI | Mitigation |
|---|---|---|
| Spoofing | Agent impersonates another user or agent to gain elevated permissions | JWT signature validation, agent identity claims, mutual TLS between agents |
| Tampering | Agent modifies request context to claim false attributes (e.g., elevated role) | Signed context tokens, immutable audit logs, context validation at PDP |
| Repudiation | Agent denies having invoked a tool or accessed data | Comprehensive decision logging to CloudTrail, signed audit records, non-repudiation via KMS |
| Info Disclosure | Agent retrieves documents or memory belonging to another tenant | Tenant isolation in Cedar policies, document-level authorization, output filtering |
| Denial of Service | Excessive tool calls overwhelm PDP evaluation capacity | PDP caching, rate limiting at PEP, circuit breakers, auto-scaling PDP fleet |
| Elevation of Privilege | Agent accumulates permissions across workflow steps (confused deputy) | Per-step authorization, no permission accumulation, explicit obligation enforcement |

## Critical Anti-Patterns to Avoid

The following anti-patterns represent the most common authorization failures observed in enterprise AI deployments — each is a compliance risk and a security vulnerability: authorization logic in business code (security policy cannot be audited, versioned, or changed without code deployment, violating separation of concerns); policies referencing Entra groups directly (Cedar policies checking AD group membership create tight coupling — group changes break authorization without policy changes); tool execution without authorization (agent tools that execute SQL, call APIs, or write to storage without per-invocation authorization create uncontrolled blast radius); overly large JWTs (encoding all authorization attributes in the JWT creates tokens that exceed HTTP header limits and are impossible to revoke mid-session); missing default-deny semantics (any model that allows actions not explicitly denied, instead of denying all not explicitly allowed, is fundamentally insecure); no policy versioning (policies that cannot be rolled back when they cause authorization failures are operational liabilities); policy evaluation after execution (checking authorization after the fact violates Zero Trust and cannot prevent harm); no decision logging (without a record of every decision, breach investigation is impossible and compliance cannot be demonstrated); lack of audit trails (fine-grained records of who accessed what, when, and under which policy are mandatory for banking regulation); and hard-coded claims (embedding specific group names or role strings in policy code rather than canonical claim mappings creates a maintenance nightmare).

## Regulatory Compliance Mapping

The authorization architecture described in this series maps directly to controls required by major regulatory frameworks applicable to banking and financial services:

| Framework | Relevant Controls | How This Architecture Satisfies Them |
|---|---|---|
| NIST 800-53 | AC-2, AC-3, AC-6, AU-2, AU-9, CM-3 | Externalized authorization (AC-3), least privilege (AC-6), comprehensive audit logging (AU-2/AU-9), policy-as-code change management (CM-3) |
| NIST AI RMF | GOVERN 1.1, MAP 2.3, MEASURE 2.6, MANAGE 1.3 | Policy-governed AI actions, risk-contextualized authorization, measurable policy compliance, incident response via policy rollback |
| PCI DSS v4.0 | Req 7, Req 8, Req 10 | Need-to-know access control, unique identity for agents, audit logs for all access to cardholder data |
| SOC 2 Type II | CC6.1, CC6.2, CC6.3, CC7.2 | Logical access controls, authentication management, authorization reviews, monitoring of access controls |
| ISO 27001:2022 | A.5.15, A.5.18, A.8.2, A.8.3 | Access control policy, access rights management, privileged access, information access restriction |
| DORA | Art. 9, Art. 10 | ICT risk management, ICT-related incident management — policy audit trails are mandatory evidence |
| EU AI Act | Art. 9, Art. 13, Art. 17 | Risk management system, transparency & logging, quality management for high-risk AI |

## Related

- [Authorization Deep Dive](24-1b-authorization-deep-dive.md)
- [Identity, Claims & Policy Design](25-identity-claims-policy.md)
- [Policy & Authorization Series Overview](02-policy-authorization-series-overview.md)
