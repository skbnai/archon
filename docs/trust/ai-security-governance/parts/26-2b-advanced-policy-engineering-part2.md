---
title: "Advanced Policy Engineering: OPA Patterns, Testing & Governance (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: 2b-advanced-policy-engineering-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol2b_Advanced_Policy_Engineering.md]
tags: [authorization, policy-engineering, opa, wasm, shadow-evaluation]
covers_version: "as of 2026"
---

Advanced OPA patterns (GitOps bundle distribution, partial evaluation for database-level authorization, WASM edge enforcement), shadow evaluation, policy test vectors, and the policy governance framework.

## OPA Advanced Patterns

**OPA bundle distribution via S3 + GitOps.** Policy bundles are built by CI/CD from a Git repository laid out as `/policies/kubernetes/`, `/policies/terraform/`, and `/policies/agent/` (each holding domain-specific `.rego` files), plus a `/data/` directory holding supporting JSON such as the tool-capability map, risk thresholds, and approved image lists, with a `.manifest` file recording the Git revision and bundle roots. OPA is configured to poll an S3 bundle server every 30-60 seconds, verify the bundle signature against a signing key, and ship decision logs to a central decision-log service. Bundles are signed in CI/CD (`opa build -b policies/ data/ --signing-key bundle-signing.pem`) and uploaded to S3 as part of the deploy pipeline.

**OPA partial evaluation for database-level authorization.** OPA's partial evaluation feature compiles a Rego policy against known inputs to produce a residual policy — typically a set of conditions that can be applied directly as a SQL `WHERE` clause or an OpenSearch filter. This is the most powerful OPA pattern for data-level authorization. Given a document-access policy that checks the user's capability, clearance level, tenant match, and embargo status:

```rego
package data.documents
import future.keywords.if

allow if {
  input.user.capabilities[_] == "can_view_financial_data"
  document_permitted(input.document)
}

document_permitted(doc) if {
  doc.classification <= input.user.clearance_level
  doc.tenant_id == input.user.tenant_id
  not doc.embargo_active
}
```

a partial-evaluation query against unknown document attributes for a specific user produces a residual policy of the form `doc.classification <= 3`, `doc.tenant_id == 'bank-prod'`, `doc.embargo_active == false` — which compiles directly to `WHERE classification <= 3 AND tenant_id = 'bank-prod' AND embargo_active = false`. The database then executes authorization as a native query filter, with zero post-retrieval scanning needed:

```python
def get_sql_filter_for_user(canonical_claims: dict) -> str:
    response = requests.post(
        "http://opa-sidecar:8181/v1/compile",
        json={
            "query": "data.documents.allow == true",
            "input": {
                "user": {
                    "capabilities": canonical_claims["capabilities"],
                    "clearance_level": canonical_claims["principal"].get("clearance_level", 1),
                    "tenant_id": canonical_claims["organization"]["tenant_id"],
                }
            },
            "unknowns": ["input.document"],
        },
    )
    conditions = extract_conditions(response.json())
    return f"WHERE {' AND '.join(conditions)}"

def get_opensearch_filter_for_user(canonical_claims: dict) -> dict:
    clearance = canonical_claims["principal"].get("clearance_level", 1)
    tenant = canonical_claims["organization"]["tenant_id"]
    return {
        "bool": {
            "must": [
                {"range": {"classification": {"lte": clearance}}},
                {"term": {"tenant_id": tenant}},
                {"term": {"embargo_active": False}},
            ]
        }
    }
```

**OPA WASM for edge authorization.** Rego policies can be compiled to WebAssembly, enabling policy enforcement at the CDN/edge layer — before requests reach the origin — with sub-millisecond evaluation and zero network I/O for the authorization check. A CI/CD step compiles the policy (`opa build -t wasm -e data/authz/allow policies/edge_authz.rego`) into a `policy.wasm` bundle; an edge function (Lambda@Edge or a CloudFront Function) loads and caches the WASM module, evaluates it against the request method, path, and extracted JWT claims, and returns a 403 if the policy denies, or forwards the request to the origin otherwise. WASM evaluation characteristics: latency under 0.5ms with no network I/O; the policy bundle updates via CDN cache invalidation; suited to rate limiting, geo-blocking, and basic capability checks; and limited to self-contained policies with no external data lookup.

## Policy Simulation, Shadow Evaluation & Testing

**Shadow evaluation architecture.** Shadow evaluation runs the new policy alongside the existing authorization system without changing production behavior, logging mismatches for investigation. A production request splits into two parallel paths: the primary path (existing authorization — embedded code or the old engine) returns the production decision, while an async shadow path evaluates the new Cedar policy via AVP `IsAuthorized`. Matching decisions log at `INFO`; mismatches log at `WARN` and are investigated for whether the new policy is too restrictive, the old code had a bug, there's an edge case in normalization, or an entity is missing from the schema. The target before Phase 3 enforcement is 99.9% decision parity.

**Policy test vector framework.** A comprehensive test-vector generator produces cases spanning happy paths, denial paths, boundary conditions, temporal conditions, and multi-tenant edge cases — for example, the full cross-product of capability sets, MFA state, business hours, and risk score against a payment-approval action:

```python
def generate_test_vectors():
    vectors = []
    capabilities = [["can_approve_payment"], ["can_view_financial_data"], []]
    mfa_states = [True, False]
    business_hours = [True, False]
    risk_scores = [0, 30, 70, 100]
    for caps, mfa, biz_hrs, risk in product(capabilities, mfa_states, business_hours, risk_scores):
        expected = compute_expected_decision(
            caps, mfa, biz_hrs, risk, action="InvokeTool", tool="PaymentApprovalTool"
        )
        vectors.append({
            "name": f"caps={caps},mfa={mfa},biz={biz_hrs},risk={risk}",
            "principal": {
                "type": "BankAI::User", "id": "test-user",
                "attributes": {"capabilities": caps, "mfaVerified": mfa,
                               "businessUnit": "FINANCE", "geography": "GB"},
            },
            "action": 'BankAI::Action::"InvokeTool"',
            "resource": 'BankAI::Tool::"PaymentApprovalTool"',
            "context": {"businessHours": biz_hrs, "riskScore": risk, "tenantId": "bank-prod"},
            "expected": expected,
        })
    return vectors

def run_test_suite(vectors: list, policy_store_id: str):
    results = {"passed": 0, "failed": 0, "failures": []}
    for vec in vectors:
        response = avp.is_authorized(
            policyStoreId=policy_store_id,
            principal=vec["principal"],
            action={"actionType": "BankAI::Action", "actionId": "InvokeTool"},
            resource={"entityType": "BankAI::Tool", "entityId": "PaymentApprovalTool"},
            context={"contextMap": build_context_map(vec["context"])},
        )
        actual = response["decision"]
        if actual == vec["expected"]:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["failures"].append({
                "test": vec["name"], "expected": vec["expected"], "actual": actual,
                "determining_policies": response.get("determiningPolicies", []),
            })
    coverage = results["passed"] / (results["passed"] + results["failed"])
    print(f"Coverage: {coverage:.1%} ({results['passed']}/{len(vectors)})")
    return results
```

## Policy Governance Framework

**Policy review board structure:**

| Role | Responsibility | Approval Required For |
|---|---|---|
| Policy Author (Developer) | Writes Cedar/Rego policies for new features or bug fixes | None — can open a PR |
| Security Engineer | Reviews policies for security correctness, over-permissiveness, missing denies | Must approve all policy PRs |
| Data Privacy Officer | Reviews policies touching PII, classification, cross-border data | Must approve: PII-related, data export, classification-change policies |
| IAM/Identity Team | Reviews claims normalization, role-capability mappings | Must approve: capability map changes, new role additions |
| Compliance Officer | Reviews policies for regulatory alignment (PCI, DORA, NIST) | Must approve: audit log policies, payment authorization policies |
| CISO (escalation) | Approves emergency policy changes, break-glass procedures | Required for: production emergency hotfix, policy rollback of &gt;100 policies |

**Policy drift detection.** An AWS Config rule Lambda triggers on CloudTrail `PutPolicy` events for AVP: it retrieves all current AVP policies, compares each against an approved-state hash stored in DynamoDB, and flags three violation types — an `UNAUTHORIZED_NEW_POLICY` when a policy ID has no approved-state entry, an `UNAUTHORIZED_MODIFICATION` when a policy's hash no longer matches its approved hash, and an `UNEXPECTED_DELETION` when an approved policy ID is missing from the current policy set. Any violation publishes a CloudWatch metric, files a Security Hub finding, and triggers a PagerDuty alert:

```python
def check_policy_drift():
    policies = list_all_policies()
    approved = get_approved_policy_state()
    violations = []
    for policy in policies:
        policy_id = policy["identifier"]["policyId"]
        policy_hash = compute_hash(policy["definition"])
        if policy_id not in approved:
            violations.append({"type": "UNAUTHORIZED_NEW_POLICY", "policyId": policy_id})
        elif approved[policy_id] != policy_hash:
            violations.append({
                "type": "UNAUTHORIZED_MODIFICATION", "policyId": policy_id,
                "expectedHash": approved[policy_id], "actualHash": policy_hash,
            })
    current_ids = {p["identifier"]["policyId"] for p in policies}
    for policy_id in approved:
        if policy_id not in current_ids:
            violations.append({"type": "UNEXPECTED_DELETION", "policyId": policy_id})
    if violations:
        cloudwatch.put_metric_data(
            Namespace="EnterpriseAuth/PolicyDrift",
            MetricData=[{"MetricName": "PolicyViolations", "Value": len(violations), "Unit": "Count"}],
        )
        publish_security_finding(violations)
        trigger_pagerduty_alert(violations)
```

## Related

- [Advanced Policy Engineering (Part 1)](../26-2b-advanced-policy-engineering.md)
- [Agent, Tool & MCP Authorization](../27-agent-tool-mcp-authorization.md)
- [AWS Implementation & Governance](../31-aws-implementation-governance.md)
