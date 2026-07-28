---
title: "Authorization Deep Dive: Engines, Interceptor Patterns & XACML"
doc_type: guide
domain: trust
status: current
topic_id: 1b-authorization-deep-dive
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol1b_Authorization_Deep_Dive.md]
tags: [authorization, ai-security, policy, xacml, openfga, cedar]
covers_version: "as of 2026"
---

A deep dive into the authorization engine landscape (XACML, OpenFGA/Zanzibar) and complete PEP interceptor pattern reference implementations for API Gateway, service mesh, application middleware, and gRPC.

## XACML — The Standard That Defined Enterprise Authorization

eXtensible Access Control Markup Language (XACML) is the OASIS standard that first formalized the PEP/PDP/PAP/PIP model. While XACML's XML verbosity has limited its modern adoption, understanding it is essential because all modern engines (Cedar, OPA, OpenFGA) implement XACML's conceptual model.

**XACML request/response model.** An XACML authorization request packages subject (`john.smith@bank.com`), environment (`FINANCE`, `invoke-tool`), and resource attributes into an XML envelope. The PDP returns `Permit`/`Deny` with optional obligations.

**XACML vs. Cedar — structural comparison:**

| Dimension | XACML 3.0 | AWS Cedar |
|---|---|---|
| Policy Format | Verbose XML — 50+ lines per rule | Concise DSL — 5-10 lines per policy |
| Combining Algorithms | 14 combining algorithms (deny-overrides, permit-overrides, etc.) | Implicit: forbid overrides permit always |
| Obligations | Full obligation model in standard | Obligations via context and PEP conventions |
| Schema Validation | XML Schema (XSD) | Cedar schema — strongly typed |
| Performance | XML parsing overhead — typically 20-100ms | Sub-millisecond evaluation |
| Standards Body | OASIS standard — government/healthcare mandate | AWS proprietary (open-source spec) |
| Formal Verification | No | Yes — Lean theorem prover |
| Vendor Implementations | IBM, Axiomatics, ForgeRock | AWS AVP only (growing ecosystem) |
| Use Today | Legacy enterprises, government mandates | New AWS-native projects |

This volume also covers event-driven authorization, the OpenFGA relationship model at Zanzibar scale, a complete STRIDE threat model with mitigations, and performance benchmark data (continued in Part 2).

## OpenFGA & Zanzibar — Relationship-Based Authorization

Google Zanzibar (2019 paper) described the authorization system that powers Google Drive, YouTube, Calendar, and Maps, serving trillions of authorization checks per day. OpenFGA (Open Fine-Grained Authorization) is an open-source implementation of the Zanzibar model. Both solve a problem RBAC and ABAC cannot: authorization based on entity relationships.

**The relationship model:**

```
// OpenFGA authorization model (Zanzibar-style)
// Defines types and their allowed relations
model
  schema 1.1

type user

type agent
  relations
    define delegated_from: [user]

type document
  relations
    define owner: [user]
    define editor: [user, agent] or owner
    define viewer: [user, agent] or editor
    define tenant_member: [user]

type folder
  relations
    define owner: [user]
    define viewer: [user] or owner
    define parent: [folder]

// Zanzibar relationship tuples (stored as facts):
// user:john#owner@document:m-and-a-brief
// user:jane#viewer@document:m-and-a-brief
// user:john#member@tenant:bank-prod
// agent:payments-agent#delegated_from@user:john
```

An authorization check for "can `agent:payments-agent` view `document:m-and-a-brief`?" resolves as: the agent is `delegated_from` `user:john`; `user:john` is `owner` of the document; `owner` is a superset of `viewer`; the check returns **ALLOW**.

**When ReBAC beats RBAC and ABAC.** ReBAC (Relationship-Based Access Control) is the superior model when authorization depends on the relationship between the principal and the resource, not just attributes:

| Scenario | RBAC/ABAC Approach | ReBAC Approach |
|---|---|---|
| Can John edit his own documents? | Add a "document-editor" role globally — too broad | Tuple: `john#editor@document:john-doc` — precise |
| Can a manager see their team's reports? | Check department attribute match — brittle | Tuple: `manager:jane#viewer@report-group:team-3` |
| Can this agent access the user's calendar? | Add a "calendar-reader" capability — grants all calendars | Tuple: `agent:X#delegated_reader@calendar:john-cal` |
| Google Drive share with specific people | Create a group for every share — explosion | Tuple per share: `user:guest#viewer@doc:shared` |

For Agentic AI, the most powerful ReBAC use case is agent-to-user-data relationships. Instead of "agent has calendar-access capability" (too broad), use relationship tuples: "agent:X is delegated_reader of user:john's calendar." This means the agent can only access John's calendar for this session, not all calendars covered by that capability.

**Hybrid: Cedar + OpenFGA.** For enterprise Agentic AI, a pragmatic hybrid uses Cedar for business authorization policy and OpenFGA (or Cedar's own entity hierarchy) for relationship facts. OpenFGA stores facts:

```
user#owner@document
agent#delegated_from@user
team#member@project
```

Cedar evaluates policy:

```
permit(principal, read, resource)
when principal is owner of resource
and resource.classification <= user.clearance
```

**PIP bridge:** OpenFGA check results flow into the Cedar authorization context as boolean attributes — `context.isOwner = true/false`, `context.isDelegatedFrom = true/false`.

## PEP Interceptor Patterns — Complete Reference

The Policy Enforcement Point must be positioned at every boundary where authorization is required. The following four reference implementations cover the primary enterprise deployment surfaces.

**API Gateway Lambda Authorizer (AWS-native).** The authorizer extracts the JWT from the incoming request, validates it and resolves canonical claims, builds a Cedar authorization request from those claims plus request context (business hours, risk score, MFA status, tenant ID, geography), calls Amazon Verified Permissions' `IsAuthorized`, and on `ALLOW` generates and caches an IAM policy document for API Gateway (300s TTL) while logging the decision; on `DENY` or any error it logs the decision and raises an unauthorized exception, defaulting to deny.

```python
def handler(event, context):
    token = event["authorizationToken"].replace("Bearer ", "")
    http_method, resource_path = parse_method_arn(event["methodArn"])
    try:
        claims = get_canonical_claims(token)
        authz_request = build_cedar_request(claims, http_method, resource_path, event)
        response = avp_client.is_authorized(**authz_request)
        if response["decision"] == "ALLOW":
            log_decision("ALLOW", authz_request, response)
            return generate_allow_policy(event["methodArn"], claims)
        log_decision("DENY", authz_request, response)
        raise Exception("Unauthorized")  # 403
    except Exception as e:
        log_decision("ERROR", {}, {"error": str(e)})
        raise Exception("Unauthorized")  # default deny
```

**Envoy/Istio external authorization (service mesh).** For East-West (service-to-service) traffic in EKS/ECS, Envoy's `ext_authz` HTTP filter calls an authorization service before forwarding requests — ideal for microservice-to-microservice agent calls. The authorization service receives all request headers (including the JWT), the request path and method, the source principal from the mTLS certificate, and optionally the request body; it returns `200 OK` to forward the request or `403 Forbidden` to block it. Critically, `failure_mode_allow` is set to `false` so that a timeout or authorization-service outage defaults to deny, not open. An OPA sidecar deployed alongside Envoy typically evaluates in under 1ms from an in-memory policy bundle loaded from S3.

**FastAPI middleware PEP.** For Python agent services, an `AuthorizationMiddleware` intercepts every request (skipping health/metrics endpoints), extracts canonical claims injected upstream by the Lambda Authorizer (or validates the JWT directly), builds a Cedar authorization request scoped to `BankAI::Agent` principals, calls Amazon Verified Permissions (or a cached decision), and on any non-`ALLOW` decision logs the denial with full context and raises a 403. On success it attaches the claims to request state for downstream handlers and proceeds to execute the handler, with an optional post-response output-classification check for sensitive-data endpoints.

**gRPC interceptor PEP.** For agent-to-agent gRPC calls, a `ServerInterceptor` extracts the JWT from gRPC metadata, resolves canonical claims, maps the gRPC method name to a Cedar action (for example `/bankai.AgentService/InvokeTool` maps to the `InvokeTool` action), and calls Amazon Verified Permissions with the agent's identity as principal and the requested resource. A non-`ALLOW` decision logs the denial and aborts the call with `PERMISSION_DENIED`; only an `ALLOW` decision proceeds to the actual handler.

## Related

- [Authorization Deep Dive (Part 2)](parts/24-1b-authorization-deep-dive-part2.md) — event-driven authorization, the complete STRIDE threat model, and performance benchmarks
- [Executive Architecture & Authorization Fundamentals](23-executive-architecture.md)
- [Identity, Claims & Policy Design](25-identity-claims-policy.md)
