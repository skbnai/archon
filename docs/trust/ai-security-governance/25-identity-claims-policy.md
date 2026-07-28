---
title: "Identity, Claims & Policy Design"
doc_type: guide
domain: trust
status: current
topic_id: identity-claims-policy
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol2_Identity_Claims_Policy.md]
tags: [authorization, identity, policy, cedar, entra-id]
covers_version: "as of 2026"
---

ADFS and Entra ID identity federation, the claims normalization pipeline and canonical enterprise claims model, and Cedar entity schema and policy design patterns.

## Identity Federation: ADFS & Microsoft Entra ID

**Federation architecture.** An on-premises user authenticates through ADFS, which issues a SAML assertion into the Entra ID tenant via a federation trust; Entra ID issues a JWT with claims, which flows into the Claims Normalization Layer (Lambda/ECS), populates the Canonical Claims Store, and is finally evaluated by the policy engine (Cedar/OPA). A cloud-native user authenticates directly against Entra ID via OIDC/JWT and joins the same pipeline from Claims Normalization onward.

**Token types and claims.** Both ADFS and Entra ID issue tokens with different claim sets. The claims normalization layer must handle all variations and produce a consistent canonical representation:

| Claim Type | ADFS Example | Entra ID Example | Canonical Form |
|---|---|---|---|
| User Principal | `upn: john.smith@bank.com` | `upn: j.smith@bank.onmicrosoft.com` | `principal_id: john.smith` |
| Department | `department: Finance` | `extension_department: FINANCE` | `business_unit: FINANCE` |
| Security Groups | `groups: [GUID-1, GUID-2]` | `groups: [GUID-A, GUID-B]` | `roles: [payments_approver, trade_viewer]` |
| Country/Region | `l: United Kingdom` | `country: GB` | `geography: GB` |
| Manager | `manager: cn=mgr,dc=bank` | `manager: GUID-of-manager` | `manager_id: emp-42891` |
| App Roles | `roles: [FinanceAdmin]` | `roles: [Payments.Approve]` | `capabilities: [can_approve_payment]` |
| Tenant | Not present | `tid: TENANT-GUID` | `tenant_id: bank-prod` |
| MFA | Not standard | `amr: [mfa, pwd]` | `mfa_verified: true` |
| Cost Center | `costCenter: CC-4421` | `extension_costCenter: 4421` | `cost_center: CC-4421` |

## Claims Normalization Architecture

Claims normalization is the most critical and most frequently under-engineered component of enterprise authorization. Without it, every policy is tightly coupled to the identity store implementation.

**The normalization pipeline** proceeds in eight stages: (1) receive the raw JWT from Entra/ADFS; (2) validate the token signature (RS256/ES256) against the JWKS endpoint; (3) extract known claims, handling missing or null claims; (4) resolve group GUIDs to human-readable group names via a cached directory lookup; (5) flatten nested group membership, resolving transitive relationships such as `Payments_Admins ⊇ Finance_Team ⊇ ...`; (6) map roles to business capabilities (e.g., `Finance_Approver` maps to `can_approve_payment`); (7) enrich via the PIP with additional attributes such as `risk_score`, `data_classification`, `business_hours`, and `approval_status`; and (8) assemble the structured, versioned, typed canonical claims object of the form `{ principal, roles, context }`.

**Canonical enterprise claims model.** The canonical claims object is the contract between the identity layer and the policy engine — it must be stable, versioned, and independent of the underlying identity store:

```json
{
  "schema_version": "2.1",
  "principal": {
    "id": "emp-48291",
    "upn": "john.smith@bank.com",
    "display_name": "John Smith",
    "employee_type": "FULL_TIME"
  },
  "organization": {
    "tenant_id": "bank-prod",
    "business_unit": "FINANCE",
    "department": "CAPITAL_MARKETS",
    "cost_center": "CC-4421",
    "geography": "GB",
    "legal_entity": "BANK_UK_LTD",
    "manager_id": "emp-12045"
  },
  "capabilities": ["can_approve_payment", "can_view_trade", "can_export_report"],
  "context": {
    "mfa_verified": true,
    "session_age_minutes": 14,
    "auth_strength": "AAL2",
    "device_compliant": true,
    "network_zone": "CORPORATE",
    "risk_score": 12,
    "business_hours": true
  },
  "issued_at": "2026-06-26T09:14:22Z",
  "expires_at": "2026-06-26T10:14:22Z"
}
```

**Role-to-capability mapping: avoiding group coupling.** The most important design decision in claims normalization is to never write Cedar or Rego policies that reference Entra group names or GUIDs directly — instead, map identity-layer constructs to domain-level capabilities.

**Anti-pattern:** `permit(principal, action, resource) when principal.groups contains 'Payments_Admins_APAC_GBP';` — this policy breaks whenever the AD group is renamed, restructured, or the user moves region, encoding identity-store implementation details directly into the policy.

**Best practice:** map Entra groups to business capabilities in the normalization layer, so the Cedar policy references capabilities only: `permit(principal, action::'approve_payment', resource) when principal.capabilities contains 'can_approve_payment';` — this policy is stable regardless of identity-store changes.

| Entra Group / Role | Maps To Capability | Policy Uses |
|---|---|---|
| Payments_Admins_APAC | can_approve_payment | `principal.capabilities contains 'can_approve_payment'` |
| Payments_Admins_EMEA | can_approve_payment | Same policy — geography context handles region |
| Finance_Readonly | can_view_financial_data | `principal.capabilities contains 'can_view_financial_data'` |
| DBA_Production | can_query_production_db | `principal.capabilities contains 'can_query_production_db'` |
| HR_Global_Admin | can_view_all_hr_records | `principal.capabilities contains 'can_view_all_hr_records'` |
| Compliance_Auditor | can_export_audit_log | `principal.capabilities contains 'can_export_audit_log'` |

**Large JWT mitigation strategies:** JWT trimming at the PEP (strip claims not needed for authorization at the API Gateway before forwarding — never pass megabyte JWTs to downstream services); capability token exchange (exchange the raw Entra JWT for a smaller, application-scoped capability token via the normalization service, per RFC 8693 Token Exchange); the reference token pattern (issue an opaque reference token to the client, and the PEP introspects it at the normalization service to get the full claim set); claim caching (cache normalized claim objects in ElastiCache/Redis keyed by token hash, with TTL aligned to token expiry, reducing PIP lookups by &gt;95%); and SCIM attribute push (use SCIM 2.0 to pre-populate a user attribute store in DynamoDB rather than embedding all attributes in the JWT).

## Cedar Policy Design

AWS Cedar is a purpose-built, formally verified policy language developed by Amazon for fine-grained authorization. Cedar policies are type-safe, decidable, and provably correct — properties that make it ideal for enterprise AI authorization.

**Cedar entity schema.** The schema defines entity types (`User`, `Agent`, `Tool`, `Resource`, `Role`, `ToolGroup`) and the actions that apply to them:

```json
{
  "namespaces": {
    "BankAI": {
      "entityTypes": {
        "User": {
          "memberOfTypes": ["Role"],
          "shape": {
            "type": "Record",
            "attributes": {
              "businessUnit": { "type": "String", "required": true },
              "geography": { "type": "String", "required": true },
              "mfaVerified": { "type": "Boolean", "required": true },
              "riskScore": { "type": "Long", "required": false },
              "capabilities": { "type": "Set", "element": { "type": "String" } }
            }
          }
        },
        "Agent": {
          "shape": {
            "type": "Record",
            "attributes": {
              "agentType": { "type": "String" },
              "delegatedFrom": { "type": "Entity", "name": "User" },
              "confidenceScore": { "type": "Long" }
            }
          }
        },
        "Tool": {
          "memberOfTypes": ["ToolGroup"],
          "shape": {
            "type": "Record",
            "attributes": {
              "dataClassification": { "type": "String" },
              "requiresMFA": { "type": "Boolean" },
              "allowedGeographies": { "type": "Set", "element": { "type": "String" } }
            }
          }
        },
        "Resource": {}, "Role": {}, "ToolGroup": {}
      },
      "actions": {
        "InvokeTool": { "appliesTo": { "principalTypes": ["User", "Agent"], "resourceTypes": ["Tool"] } },
        "ApprovePayment": { "appliesTo": { "principalTypes": ["User"], "resourceTypes": ["Resource"] } },
        "QueryDatabase": { "appliesTo": { "principalTypes": ["Agent"], "resourceTypes": ["Resource"] } }
      }
    }
  }
}
```

**Cedar policy patterns.** Every Cedar policy set should begin with an explicit default-deny statement, even though Cedar's evaluation is deny-by-default — policies only grant, never imply:

```
forbid(principal, action, resource);
```

RBAC — capability-based tool access permits invocation only when the principal holds the required capability, has MFA verified, and the request falls within business hours:

```
permit(
  principal,
  action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"PaymentApprovalTool"
)
when {
  principal.capabilities.contains("can_approve_payment") &&
  principal.mfaVerified == true &&
  context.businessHours == true
};
```

ABAC — geography-scoped authorization restricts HR tool access to the principal's own geography:

```
permit(
  principal,
  action == BankAI::Action::"InvokeTool",
  resource is BankAI::Tool
)
when {
  principal.capabilities.contains("can_view_hr_records") &&
  resource.allowedGeographies.contains(principal.geography)
};
```

ReBAC — agent delegation permits an agent to invoke tools only within the scope of the delegating user, gated on a minimum confidence score:

```
permit(
  principal is BankAI::Agent,
  action == BankAI::Action::"InvokeTool",
  resource
)
when {
  principal.delegatedFrom.capabilities.contains("can_approve_payment") &&
  principal.delegatedFrom.mfaVerified == true &&
  context.agentConfidenceScore >= 85
};
```

A temporal policy restricts destructive operations to business hours and low risk:

```
forbid(
  principal,
  action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"DeleteRecordTool"
)
when {
  context.businessHours == false || context.riskScore > 70
};
```

Tenant isolation is enforced as a mandatory forbid whenever the resource and principal tenant IDs mismatch:

```
forbid(principal, action, resource)
when {
  resource has tenantId && principal has tenantId &&
  resource.tenantId != principal.tenantId
};
```

**Cedar policy lifecycle management:**

| Phase | Activity | Tooling |
|---|---|---|
| Authoring | Policy authored in Cedar DSL | IDE plugins, `cedar` CLI, AVP console |
| Schema Validation | Type-check against the entity schema | `cedar validate --schema cedar-schema.json` |
| Unit Testing | Test individual policies with test vectors | `cedar test` (test suite YAML) |
| Shadow Evaluation | Run new policy alongside existing and compare decisions | AVP Shadow Mode, decision log comparison |
| PR Review | Security team reviews policy changes as code | GitHub PR, automated Cedar lint |
| Staging Deploy | Deploy to a non-production AVP policy store | CI/CD pipeline (GitHub Actions/CodePipeline) |
| Production Deploy | Phased rollout with monitoring | CodeDeploy blue/green, CloudWatch alarms |
| Drift Detection | Alert on unauthorized policy changes | CloudTrail events on AVP, automated diff |
| Emergency Rollback | Revert to the previous policy version | Git revert + pipeline trigger, &lt;5 min target |

## Related

- [Identity, Claims & Policy Design (Part 2)](parts/25-identity-claims-policy-part2.md) — Rego/OPA policy design, Cedar vs. Rego decision matrix, hybrid architecture, token exchange and on-behalf-of flows
- [Authorization Deep Dive](24-1b-authorization-deep-dive.md)
- [Advanced Policy Engineering](26-2b-advanced-policy-engineering.md)
