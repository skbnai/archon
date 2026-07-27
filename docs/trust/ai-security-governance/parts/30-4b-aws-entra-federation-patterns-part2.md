---
title: "AWS & Entra ID Federation: Network Security, Cross-Account & DR (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: 4b-aws-entra-federation-patterns-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol4b_AWS_Entra_Federation_Patterns.md]
tags: [authorization, aws, privatelink, disaster-recovery, multi-account]
covers_version: "as of 2026"
---

VPC PrivateLink and security group design for the authorization plane, AWS IAM Identity Center's dual identity plane, cross-account authorization architecture, and authorization disaster recovery patterns.

## Network Security: PrivateLink & VPC Endpoints

All authorization traffic must traverse AWS's private network, never the public internet. VPC endpoints for AVP, DynamoDB, ElastiCache, and S3 ensure that authorization calls never leave the AWS backbone.

**Required VPC endpoints for the authorization architecture:**

| Service | Endpoint Type | Purpose |
|---|---|---|
| Amazon Verified Permissions | Interface endpoint (PrivateLink) | Cedar AVP `IsAuthorized` API calls — no internet egress |
| DynamoDB | Gateway endpoint | PIP attribute lookups, audit log writes |
| S3 | Gateway endpoint | OPA bundle downloads, audit log archive |
| Secrets Manager | Interface endpoint | Agent credential retrieval |
| AWS STS | Interface endpoint | Token exchange, assume role for OBO |
| ElastiCache | Not applicable (VPC-native) | Claims cache (Redis) — already in the VPC |
| CloudWatch Logs | Interface endpoint | Audit log delivery without NAT |
| EventBridge | Interface endpoint | Authorization event publishing |

**Security group configuration.** The authorization tier (Lambda Authorizer, Claims Normalization ECS) accepts inbound HTTPS only from the API Gateway and agent-runtime security groups, and its outbound rules are scoped to the AVP/Secrets/STS VPC endpoint, the Redis security group, the DynamoDB endpoint, and — for Entra ID JWKS retrieval only — general internet egress via NAT. The Redis security group accepts inbound connections only from the auth and PIP-Lambda security groups and initiates no outbound connections of its own. The agent-runtime security group accepts inbound responses from the MCP gateway and sends outbound traffic only to the authorization layer, the MCP PEP gateway, and the Bedrock/AVP VPC endpoints. A network ACL provides defense in depth on top of the security groups, denying all traffic that doesn't originate from an authorized source security group and explicitly denying cross-subnet RFC 1918 traffic outside the approved authorization paths.

## AWS IAM Identity Center Integration

AWS IAM Identity Center (formerly AWS SSO) bridges Entra ID to AWS IAM permissions. For Agentic AI, it provides the AWS-side identity for agent task roles while Entra ID provides the business identity — two parallel identity planes that must both be properly configured.

**Dual identity plane architecture:**

| Plane | System | Purpose |
|---|---|---|
| Business Identity | Microsoft Entra ID | User JWT with capabilities, department, MFA claims |
| AWS Resource Identity | AWS IAM Identity Center | ECS task role / IAM role, e.g. `AgentRuntimeRole-FINANCE` |

These two planes flow into different downstream systems: the business identity feeds Claims Normalization and Cedar authorization; the AWS resource identity feeds the ECS task role and IAM authorization. Cedar and IAM are independent — Cedar cannot see IAM roles, and IAM cannot see Cedar claims. Both must allow an action for it to succeed. For example, when a task calls Bedrock and then invokes a payment tool: IAM checks whether `AgentRuntimeRole` has `bedrock:InvokeModel` (yes); Cedar checks whether the delegating user `john.smith` has `can_approve_payment` (yes); only because both independently allow does the action proceed.

**IAM Identity Center SCIM sync.** IAM Identity Center is configured with Entra ID as its external identity provider via SCIM, syncing users and groups from Entra ID and mapping groups to AWS permission sets (which become IAM roles). This SCIM sync controls AWS *service* access (the IAM plane) and must never be used as a substitute for Cedar's business-authorization plane. Recommended permission-set mappings for the agent architecture: `AgentRuntimeUser` grants `bedrock:InvokeModel` and `bedrock:InvokeAgent` scoped to specific ARNs, `verifiedpermissions:IsAuthorized` (read-only, for the Lambda Authorizer), `dynamodb:GetItem`/`Query` on the audit table, and `secretsmanager:GetSecretValue` with a resource-tag condition, all constrained to approved regions; `AuthorizationServiceUser` grants `verifiedpermissions:IsAuthorized` and `IsAuthorizedWithToken`, `elasticache:Connect`, and tag-scoped `dynamodb:*` on audit tables; `PolicyAdminUser` grants `verifiedpermissions:PutPolicy`/`DeletePolicy`/`UpdatePolicy` with a condition requiring MFA to be present.

## Cross-Account Authorization Architecture

Enterprise AWS environments commonly span multiple accounts: a shared services account for authorization infrastructure, workload accounts for agent runtimes, and a security account for audit logs. Cross-account authorization requires careful IAM trust configuration.

**Multi-account architecture.** The **Security Account** holds the CloudTrail organization trail into a WORM S3 bucket, Security Hub as the finding aggregator, GuardDuty as the threat-detection master, a Config aggregator, and the KMS CMKs used for cross-account encryption. The **Shared Services Account** hosts the Amazon Verified Permissions policy store, the ElastiCache Redis claims-normalization cache, the DynamoDB PIP attribute store, Secrets Manager agent credentials, the OPA bundle S3 bucket, and the SCIM receiver Lambda; a Lambda in a workload account reaches AVP by assuming a `SharedServicesRole` that carries `verifiedpermissions:IsAuthorized`. The **Production Workload Account** runs the Agent Runtime (ECS Fargate/EKS), API Gateway with the Lambda Authorizer, the MCP PEP Gateway, Bedrock AgentCore, and OpenSearch for RAG vector search, with an `AgentTaskRole` that assumes the shared-services role for AVP and PIP lookups. A **Non-Production Workload Account** runs staging and dev agent environments against a separate, non-production AVP policy store, with shadow evaluation run against the production policy store to validate parity before promotion.

**Best practice — security control.** The AVP policy store in the Shared Services account is protected by Service Control Policies at the AWS Organization level that deny `verifiedpermissions:PutPolicy`/`DeletePolicy`/`UpdatePolicy` unless the calling principal is the approved CI/CD pipeline role in the Security account. This prevents any workload account from modifying policies, even if that account is fully compromised.

## Authorization Disaster Recovery

The authorization layer is critical infrastructure — a failure in the PDP must not bring down the entire platform. The following DR patterns ensure continued operation while maintaining the security posture.

**Authorization DR scenarios:**

| Failure Scenario | Impact | Response | Recovery Time Target |
|---|---|---|---|
| AVP regional outage | Cedar evaluation unavailable | Fail-closed: deny all non-cached requests; cached decisions (300s TTL) continue serving cached traffic | Automatic; RTO 0 (cached) to 5 min (cache expiry) |
| ElastiCache failure | Claims normalization falls to a cold path (~30ms) | Auto-failover to replica; if both fail, the Lambda Authorizer calls LDAP directly | Automatic ElastiCache failover: ~30s |
| Claims Normalization ECS down | Cannot normalize new JWT tokens | Lambda Authorizer retries 3x, then fails closed; existing cached claims still work | ECS service auto-recovery ~2 min; full RTO with cache: 0 |
| Entra ID JWKS unavailable | Cannot validate new JWT signatures | JWKS cached in Lambda memory (1 hour); serve from cache and alert at 45 min | Cache serves for 1 hour; MTTR target 30 min |
| DynamoDB PIP table failure | Cannot enrich claims with SCIM attributes | Fail to cached attributes; if no cache, use minimal claims from the JWT only (limited policies apply) | DynamoDB multi-AZ automatic; single-AZ failover 1-5 min |
| Policy store corruption | Policies return unexpected decisions | Automated drift detection triggers rollback to the last known-good Git SHA via the pipeline | Pipeline rollback RTO 10-15 min |

**Multi-region authorization.** For global deployments or region failover, the policy store must remain consistent across regions. AWS does not yet natively support AVP policy replication, so the recommended pattern is GitOps-driven multi-region deployment: the CI/CD pipeline deploys the same policy definitions from Git to each region's AVP store in sequence (staging in each region, then production in each region behind a human approval gate), and regional Lambda Authorizers evaluate against their own local AVP store. An EventBridge-scheduled consistency check runs every five minutes, computing a canonical hash of each region's policy set and alarming if any region diverges from the reference (primary) region:

```python
def check_cross_region_policy_consistency():
    regions = ["eu-west-1", "us-east-1", "ap-southeast-1"]
    policy_hashes = {}
    for region in regions:
        avp = boto3.client("verifiedpermissions", region_name=region)
        policies = list_all_policies(avp, POLICY_STORE_IDS[region])
        policy_hashes[region] = compute_canonical_hash(policies)
    reference = policy_hashes["eu-west-1"]
    for region, hash_val in policy_hashes.items():
        if hash_val != reference:
            trigger_alarm(f"POLICY_INCONSISTENCY: {region} differs from primary")
```

## Related

- [AWS & Entra ID Federation (Part 1)](../30-4b-aws-entra-federation-patterns.md)
- [AWS Implementation & Governance](../31-aws-implementation-governance.md)
- [Compliance & Governance Decision Framework](../32-5b-compliance-governance-decision-framework.md)
