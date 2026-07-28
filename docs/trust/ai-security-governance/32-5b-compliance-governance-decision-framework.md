---
title: "Compliance & Governance: Regulatory Control Mapping"
doc_type: guide
domain: trust
status: current
topic_id: 5b-compliance-governance-decision-framework
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol5b_Compliance_Governance_Decision_Framework.md]
tags: [authorization, compliance, nist, pci-dss, dora, eu-ai-act]
covers_version: "as of 2026"
---

A complete regulatory control mapping from the enterprise authorization architecture to NIST 800-53, the NIST AI RMF, PCI DSS v4.0, DORA, and the EU AI Act.

This volume provides a complete regulatory control mapping for NIST 800-53, the NIST AI Risk Management Framework, PCI DSS v4.0, SOC 2 Type II, DORA, and the EU AI Act, deep-dive enterprise case studies with implementation evidence, the definitive Cedar vs. OPA vs. hybrid decision framework, and a complete anti-pattern catalogue with remediation.

## NIST 800-53: Access Control and Audit Families

NIST 800-53 is the control framework underlying FedRAMP and much of US federal and financial-sector security compliance. The authorization architecture directly implements the Access Control (AC) and Audit and Accountability (AU) control families.

**Access Control family (AC):**

| Control ID | Control Name | Architecture Implementation | Evidence Artifact |
|---|---|---|---|
| AC-2 | Account Management | Cedar entity store tracks all principals (users and agents); SCIM provisioning creates and removes principals automatically | SCIM sync logs, Cedar entity audit, deprovisioning CloudTrail events |
| AC-3 | Access Enforcement | Cedar PDP enforces access control decisions for every request; PEP at the API Gateway and middleware; default-deny posture | AVP `IsAuthorized` CloudTrail logs, Lambda Authorizer execution logs |
| AC-4 | Information Flow Enforcement | Cedar output classification policies control what data can flow to which principals; DLP scan on all outputs | Cedar output policy decisions, Bedrock Guardrails logs, Macie findings |
| AC-5 | Separation of Duties | Policy authors cannot deploy without security review; agents cannot accumulate permissions across steps; human approval for sensitive actions | GitHub PR approvals, Step Functions approval records, Cedar forbid policies |
| AC-6 | Least Privilege | Agents receive minimum scope at delegation time; capabilities scoped to specific task type; tool access restricted by agent type | Delegation token scope claims, Cedar agent type policies, tool access logs |
| AC-7 | Unsuccessful Logon Attempts | JWT replay detection blocks replayed tokens; risk score increases on repeated denials; GuardDuty monitors for brute force | ElastiCache `jti` blacklist, GuardDuty findings, CloudWatch denial metrics |
| AC-17 | Remote Access | VPN zone check in Cedar context; restricted tool access from non-corporate networks; MFA re-authentication for remote sessions | Network zone claim in canonical claims, Cedar network zone policies |
| AC-23 | Data Mining Protection | RAG pre-retrieval filter limits bulk document access; Cedar policy restricts query volume; bulk export requires an explicit capability | OpenSearch filter logs, Cedar bulk export policies, export audit records |

**Audit and Accountability family (AU):**

| Control ID | Control Name | Architecture Implementation | Evidence Artifact |
|---|---|---|---|
| AU-2 | Event Logging | Every Cedar `IsAuthorized` call logged to CloudTrail; agent tool invocations logged at the MCP PEP; RAG access logged per chunk | CloudTrail event history, MCP PEP logs, RAG access DynamoDB records |
| AU-3 | Content of Audit Records | Audit schema captures timestamp, principal, action, resource, decision, policy ID, context hash, latency, and obligation | Audit record schema (DynamoDB), CloudTrail event detail format |
| AU-6 | Audit Record Review | Automated anomaly detection via CloudWatch Metrics Insights; monthly access review reports; SIEM integration for continuous monitoring | CloudWatch alarms, access review reports, SIEM dashboard |
| AU-9 | Protection of Audit Information | S3 Object Lock (WORM) for CloudTrail logs; separate security account for log storage; KMS encryption; log integrity validation | S3 Object Lock config, cross-account log bucket policy, CloudTrail validation status |
| AU-11 | Audit Record Retention | CloudTrail logs retained 7 years (regulatory minimum); DynamoDB audit table: 90 days hot, 7 years in S3 Glacier | S3 lifecycle policy, DynamoDB TTL configuration, Glacier vault |
| AU-12 | Audit Record Generation | Lambda Authorizer generates an audit record for every authorization decision including denials; async write to DynamoDB and CloudWatch | Lambda Authorizer audit code, CloudWatch log groups, DynamoDB write throughput |

## NIST AI Risk Management Framework (AI RMF)

The NIST AI RMF is the emerging standard for managing risk in AI systems. The authorization architecture implements controls across all four core functions: GOVERN, MAP, MEASURE, and MANAGE.

| AI RMF Function | Sub-Category | Authorization Architecture Control | Evidence |
|---|---|---|---|
| GOVERN 1.1 | AI risk governance policies | Policy-as-code with PR review and approval gates ensures all AI agent behaviors are governed by written, auditable policies | GitHub policy repository, PR approval records, Cedar policy store |
| GOVERN 1.2 | Accountability structures | Cedar decision logs attribute every action to a principal and a policy; a human-approval obligation creates clear accountability for high-risk actions | CloudTrail AVP events, Step Functions approval records |
| GOVERN 4.1 | Organizational teams | The Policy Review Board (security, privacy, compliance, IAM) reviews all policy changes; delegated administration scopes are defined and documented | Policy Review Board charter, PAP governance policy |
| MAP 2.3 | AI system categorization | Agent types are categorized (customer service, payment, compliance) with explicit permitted tool sets; the capability taxonomy documents agent risk levels | Agent type taxonomy table, Cedar agent type policies |
| MAP 3.5 | Risk identification | The STRIDE threat model is applied to the authorization layer; risk scoring integrates GuardDuty and Fraud Detector signals | STRIDE threat model doc, risk score computation code |
| MEASURE 2.6 | Policy compliance metrics | Shadow evaluation measures policy decision accuracy before production; CloudWatch tracks allow/deny rates, policy drift, and latency | Shadow evaluation comparison reports, CloudWatch dashboards |
| MEASURE 2.9 | AI performance monitoring | Agent confidence score impacts authorization; low-confidence agent actions require human approval; the audit trail captures confidence at decision time | Cedar confidence-score policy, Step Functions HITL records |
| MANAGE 1.3 | Incident response | Emergency policy rollback in under 5 minutes; automated policy drift detection; a break-glass procedure for production policy access | Rollback runbook, Config rule alarm, break-glass IAM policy |
| MANAGE 2.4 | Decommissioning | Agent deprovisioning removes delegation scope immediately via SCIM sync; Cedar entities are deactivated in AVP; the audit trail is preserved | SCIM deprovisioning logs, Cedar entity deactivation, retention policy |

## PCI DSS v4.0 Control Implementation

PCI DSS v4.0 introduces enhanced requirements for access control, multi-factor authentication, and targeted risk analysis. The authorization architecture implements the following PCI DSS requirements:

| Requirement | Description | Implementation | Testing Evidence |
|---|---|---|---|
| Req 7.2 | Access control system | Cedar AVP is the centralized access control system for all cardholder data environments; default deny, explicit permit only | Cedar policy store configuration, AVP `IsAuthorized` call logs |
| Req 7.3.1 | All access to system components is by individual identity | Each agent has a unique identity (not shared); user delegation preserves individual identity in the `act` claim | Delegation token claims, agent identity registration records |
| Req 8.3.6 | MFA for all personnel | Cedar policy requires `mfaVerified=true` for all payment tool access; MFA method is validated, with phishing-resistant MFA required for high value | Cedar MFA policies, `mfaMethod` claim in canonical claims, denial logs for non-MFA |
| Req 8.3.9 | User passwords changed every 90 days | Entra ID password policy enforced upstream; the authorization layer checks session age and requires re-authentication after 1 hour | Entra ID password policy screenshot, Cedar session-age policy |
| Req 10.2 | Audit logs capture required events | Audit records capture user, date/time, action, affected data system, type of activity, and originating location | Audit record schema comparison with the Req 10.2 checklist |
| Req 10.3 | Protect audit logs from destruction | S3 Object Lock (compliance mode) on the CloudTrail log bucket; cross-account storage in the Security account; KMS encryption | S3 Object Lock policy, S3 bucket policy, KMS key policy |
| Req 10.4 | Review audit logs daily | CloudWatch alarms for anomalous authorization patterns (spike in denials, off-hours access, cross-tenant attempts) with PagerDuty integration | CloudWatch alarm configurations, PagerDuty escalation policy |
| Req 12.6 | Security awareness training | The Policy Review Board includes a training requirement; Cedar policies encode business rules that developers must understand | Training records, Policy Review Board attendance log |

## DORA and EU AI Act Compliance

**DORA (Digital Operational Resilience Act).** DORA mandates ICT risk management and operational resilience for financial entities in the EU. The authorization architecture addresses DORA's most critical ICT risk requirements: Article 5 (ICT Risk Management) via a STRIDE threat model for the authorization layer, continuous GuardDuty threat detection, risk-score integration, and quarterly threat-model review; Article 9 (Protection & Prevention) via Cedar output classification policies, a DLP scan on all agent outputs, tenant isolation, and data-residency enforcement via geography claims; Article 10 (Detection) via CloudWatch anomaly detection on authorization decisions, GuardDuty findings routed to Security Hub, and SIEM integration for real-time alerting; Article 11 (Response & Recovery) via an emergency policy rollback procedure under 5 minutes, circuit breakers in the PEP for PDP failures, and a playbook for authorization-related incidents; Article 12 (Backup & Recovery) via GitOps-backed AVP policy stores (Git as the source of truth), multi-AZ ElastiCache Redis, and DynamoDB point-in-time recovery; Article 17 (ICT-related incidents) via severity-classified authorization security incidents and an auto-generated CloudTrail evidence package for regulatory reporting within 72 hours; and Article 28 (Third-party risk) by treating AWS (AVP, Bedrock, ECS) as a critical ICT third party with a contractual exit strategy and policies stored in Git rather than vendor-locked solely in AVP.

**EU AI Act compliance.** The EU AI Act establishes requirements for AI systems deployed in regulated sectors including financial services; AI agents that make or influence credit decisions, fraud detection, or financial advice are likely classified as high-risk AI systems. Article 9 (Risk Management) is addressed through Cedar policy lifecycle management (the PAP), the STRIDE threat model, risk-scoring integration, and a quarterly policy-review cadence. Article 10 (Data Governance) is addressed through RAG authorization that prevents unauthorized or irrelevant data from entering agent context, with document classification controlling data quality. Article 13 (Transparency) is addressed through authorization decision logs that capture the policy IDs determining each decision and human-readable policy descriptions required in Cedar policy metadata. Article 14 (Human Oversight) is addressed through the Step Functions human-approval workflow, an emergency policy rollback that can halt all agent tool access in under 5 minutes, and human override of Cedar deny decisions via the approval workflow. Article 17 (Quality Management) is addressed through shadow evaluation that detects policy regression before production, CloudWatch monitoring of authorization decision quality (unexpected allow-rate changes), and automated regression tests. Article 26 (Obligations for Deployers) is addressed through a compliance dashboard showing authorization decision metrics, automated access review reports, and anomaly alerts routed to a designated compliance officer.

## Related

- [Compliance & Governance Decision Framework (Part 2)](parts/32-5b-compliance-governance-decision-framework-part2.md) — the complete anti-pattern catalogue with remediation and the definitive Cedar vs. OPA vs. hybrid decision framework
- [AWS Implementation & Governance](31-aws-implementation-governance.md)
- [Policy & Authorization Series Overview](02-policy-authorization-series-overview.md)
