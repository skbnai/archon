---
title: "Advanced Policy Engineering: SCIM, Cedar Templates & Delegated Administration"
doc_type: guide
domain: trust
status: current
topic_id: 2b-advanced-policy-engineering
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol2b_Advanced_Policy_Engineering.md]
tags: [authorization, policy-engineering, scim, cedar-templates]
covers_version: "as of 2026"
---

SCIM 2.0 claim enrichment, nested Entra ID group resolution at scale, and Cedar policy templates for delegated administration and multi-tenant SaaS deployments.

## SCIM 2.0 Integration for Claim Enrichment

**SCIM architecture for enterprise AI.** Microsoft Entra ID pushes SCIM 2.0 provisioning events on change to an enterprise SCIM endpoint. A SCIM Receiver Lambda validates the SCIM bearer token, transforms the SCIM schema into the enterprise schema, and writes the result to a DynamoDB User Attribute Store (partitioned by `userId`, with GSIs `by-department` and `by-geography`) containing department, cost center, clearance level, geography, legal entity, manager, project memberships, trading desk ID, regulatory captures, and data access scopes — with no TTL, since SCIM manages the record lifecycle directly. At authorization time, a PIP Lookup Lambda enriches the canonical claims with these SCIM attributes, caching the result in ElastiCache Redis with a 300-second TTL, producing the enriched Cedar authorization context.

**SCIM receiver implementation.** The receiver routes SCIM 2.0 requests by path and method: a `POST` to `/Users` provisions a new user, a `PUT` to `/Users/{id}` updates one, a `DELETE` deprovisions one, and a `GET` lists users. Provisioning transforms the SCIM payload into the enterprise schema — mapping the Entra ID object ID to `userId`, `userName` to `upn`, and pulling department and cost center from the SCIM enterprise extension, geography and clearance from custom extraction logic, and trading desk ID from a bank-specific SCIM extension — then writes the record to DynamoDB:

```python
def provision_user(scim_user: dict) -> dict:
    enterprise_user = {
        "userId": scim_user["id"],  # Entra ID object ID
        "upn": scim_user["userName"],
        "displayName": scim_user["displayName"],
        "department": scim_user.get(
            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User", {}
        ).get("department", "UNKNOWN"),
        "costCenter": scim_user.get(
            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User", {}
        ).get("costCenter", ""),
        "geography": extract_geography(scim_user),
        "clearanceLevel": extract_clearance(scim_user),
        "legalEntity": extract_legal_entity(scim_user),
        "tradingDeskId": scim_user.get(
            "urn:bank:scim:extension:trading", {}
        ).get("deskId", ""),
        "projectMemberships": [],  # populated by group sync
        "lastSyncedAt": get_iso_timestamp(),
        "active": scim_user.get("active", True),
    }
    table.put_item(Item=enterprise_user)
    return {"statusCode": 201, "body": json.dumps({"id": enterprise_user["userId"]})}

def update_user(path: str, scim_user: dict) -> dict:
    user_id = path.split("/")[-1]
    updates = build_update_expression(scim_user)
    table.update_item(
        Key={"userId": user_id},
        UpdateExpression=updates["expression"],
        ExpressionAttributeValues=updates["values"],
        ConditionExpression="attribute_exists(userId)",  # safety check
    )
    invalidate_pip_cache(user_id)
    return {"statusCode": 200, "body": json.dumps({"id": user_id})}

def deprovision_user(path: str) -> dict:
    user_id = path.split("/")[-1]
    # Mark inactive rather than delete — audit requirement
    table.update_item(
        Key={"userId": user_id},
        UpdateExpression="SET active = :false, deactivatedAt = :ts",
        ExpressionAttributeValues={":false": False, ":ts": get_iso_timestamp()},
    )
    invalidate_pip_cache(user_id)
    return {"statusCode": 204}
```

## Nested Group Resolution Algorithm

Microsoft Entra ID supports deeply nested security groups. A user's effective role set is the transitive closure of all direct and indirect group memberships, and this computation must be done efficiently at authorization time.

**The transitive closure problem.** Consider a group hierarchy `GlobalAdmins → EMEA_Admins → UK_Admins → London_Payments_Admins → john.smith`. The user's JWT contains only the direct membership, `{"groups": ["London_Payments_Admins_GUID"]}`, but the effective capability set should include `can_approve_payment` (from London_Payments_Admins), `can_view_emea_data` (from EMEA_Admins), and `can_access_global_reports` (from GlobalAdmins). Without nested resolution, the user is missing inherited capabilities; with resolution, the hierarchy is flattened into the full capability set.

**Efficient resolution with caching.** A resolver performs a breadth-first traversal of the group hierarchy, checking Redis first (300-second TTL) before walking parent groups via the directory API, and caches the resolved group set. Capability resolution then maps each resolved group GUID to a human-readable name and looks it up in a group-to-capability table (itself cached), unioning the capabilities across all resolved groups:

```python
def resolve_transitive_groups(user_id: str, direct_groups: list) -> set[str]:
    cache_key = f"groups:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return set(json.loads(cached))
    visited = set()
    queue = list(direct_groups)
    while queue:
        group_guid = queue.pop(0)
        if group_guid in visited:
            continue
        visited.add(group_guid)
        for parent in get_parent_groups(group_guid):
            if parent not in visited:
                queue.append(parent)
    r.setex(cache_key, 300, json.dumps(list(visited)))
    return visited

def resolve_capabilities(group_guids: set[str]) -> list:
    cache_key = f"caps:{hash_set(group_guids)}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    capabilities = set()
    for guid in group_guids:
        group_name = resolve_group_name(guid)  # GUID -> human name
        capabilities.update(GROUP_TO_CAPABILITY_MAP.get(group_name, []))
    result = list(capabilities)
    r.setex(cache_key, 300, json.dumps(result))
    return result

# Loaded from DynamoDB, managed by the IAM team
GROUP_TO_CAPABILITY_MAP = {
    "London_Payments_Admins": ["can_approve_payment", "can_view_payments"],
    "EMEA_Payments_Admins": ["can_approve_payment", "can_view_emea_data"],
    "GlobalAdmins": ["can_access_global_reports", "can_view_all_data"],
    "Finance_Readonly": ["can_view_financial_data"],
    "DBA_Production": ["can_query_production_db"],
    "Compliance_Auditors": ["can_export_audit_log", "can_view_all_data"],
    # ... hundreds more mappings managed in DynamoDB
}
```

**Role explosion mitigation.** Large enterprises often have thousands of AD groups; without mitigation, the JWT groups claim and the resolved capability set both explode in size, causing performance and token-size problems:

| Problem | Scale | Mitigation Strategy | Implementation |
|---|---|---|---|
| Too many groups in JWT | &gt;200 groups → JWT &gt;4KB, HTTP header overflow | Reference token + PIP lookup | JWT contains only a `jti`; full groups loaded from DynamoDB on demand |
| Group GUID explosion | Thousands of GUIDs with no semantic meaning | GUID-to-name cache in ElastiCache | Pre-loaded at normalization service startup; refreshed every 5 min |
| Capability set explosion | 1,000 groups → 3,000 capabilities | Scope resolution to only capabilities relevant to the requested resource | Lazy capability resolution: only resolve groups relevant to the action being authorized |
| Transitive resolution latency | 10+ levels deep → 50+ directory API calls | Pre-computed transitive closure in DynamoDB (SCIM-updated) | SCIM sync writes the full transitive group list; no real-time traversal needed |
| Policy evaluation with huge capability sets | Cedar policy with `contains` on a 3,000-element set | Segment capabilities by domain (`finance_caps`, `hr_caps`, etc.) | Cedar context uses typed sets per domain, not one flat list |

## Cedar Policy Templates & Delegated Administration

Cedar Policy Templates allow parameterized policies to be instantiated for many entities without writing individual policies for each — critical for multi-tenant SaaS deployments and delegated administration models.

**Cedar policy templates.** A template parameterized by `?principal` and `?resource` grants a specific user access to a specific resource they own:

```
// Template: resource-owner-access
@id("resource-owner-template")
permit(
  principal == ?principal,
  action in [BankAI::Action::"ReadDocument", BankAI::Action::"EditDocument"],
  resource == ?resource
);

// Instantiated for John's M&A document:
//   ?principal = BankAI::User::"john.smith"
//   ?resource  = BankAI::Document::"doc-ma-2025-001"
// 10,000 users x 10 documents = 100,000 policies, but only one template to maintain.
```

A second template grants project-member access to all documents in a project, gated on the principal being active:

```
@id("project-member-template")
permit(
  principal == ?principal,
  action in [BankAI::Action::"ReadDocument", BankAI::Action::"CommentDocument"],
  resource in BankAI::Project::"?project"
)
when { principal.active == true };
```

Template-linked policies are managed programmatically:

```python
avp_client.create_policy(
    policyStoreId=POLICY_STORE_ID,
    definition={
        "templateLinked": {
            "policyTemplateId": "resource-owner-template",
            "principal": {"entityType": "BankAI::User", "entityId": "john.smith"},
            "resource": {"entityType": "BankAI::Document", "entityId": "doc-ma-2025-001"},
        }
    },
)
```

**Delegated administration with Cedar.** Delegated administration allows department heads or project leads to manage authorization within their scope without touching the central policy store. A Finance Manager can be granted admin rights scoped strictly to Finance documents:

```
permit(
  principal == BankAI::User::"sarah.jones",
  action == BankAI::Action::"ManageAccess",
  resource in BankAI::DocumentScope::"Finance"
)
when { principal.capabilities.contains("can_admin_finance_scope") };
```

The delegated-admin workflow runs as: Sarah (the Finance Manager) requests to grant John access to `doc-X`; the API validates that Sarah has `ManageAccess` to the Finance scope; the system creates a template-linked policy for John plus `doc-X`; Cedar now evaluates that John can access `doc-X`; and CloudTrail records that Sarah granted John access. Guardrails prevent delegated admins from granting access beyond their own scope, granting access to classification levels above their own clearance, granting admin permissions (only read/edit), or granting access without an MFA challenge:

```
forbid(
  principal,
  action == BankAI::Action::"ManageAccess",
  resource
)
when {
  // Cannot elevate beyond own clearance
  resource.classification > principal.clearanceLevel
}
unless {
  principal.capabilities.contains("can_admin_global_scope")
};
```

**Cedar policy versioning strategy:**

| Version Type | Approach | Rollback Mechanism | Use Case |
|---|---|---|---|
| Major (breaking) | New policy store; traffic migration via canary | Switch canary back to 0% | Fundamental model change (e.g., new entity type) |
| Minor (additive) | Add new permit policies; shadow evaluate first | Delete new policies | New capability or resource type |
| Patch (fix) | Replace existing policy; validate with test suite | Git revert + pipeline redeploy | Bug fix in existing policy logic |
| Emergency (hotfix) | Direct AVP update with dual approver (break-glass) | Immediate AVP delete or disable | Active security incident requiring immediate policy change |

## Related

- [Advanced Policy Engineering (Part 2)](parts/26-2b-advanced-policy-engineering-part2.md) — OPA bundle distribution, partial evaluation, WASM edge authorization, shadow evaluation, test vectors, and policy governance
- [Identity, Claims & Policy Design](25-identity-claims-policy.md)
- [Agent, Tool & MCP Authorization](27-agent-tool-mcp-authorization.md)
