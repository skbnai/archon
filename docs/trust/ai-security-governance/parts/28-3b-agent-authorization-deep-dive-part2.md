---
title: "Agent Authorization Deep Dive: Human-in-the-Loop, Audit & Capability Scoping (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: 3b-agent-authorization-deep-dive-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol3b_Agent_Authorization_Deep_Dive.md]
tags: [authorization, step-functions, audit-trail, agent-types]
covers_version: "as of 2026"
---

The Step Functions human-approval state machine, the enterprise authorization audit record schema and retention architecture, automated regulatory evidence generation, and Cedar policies for agent-type capability scoping.

## Human-in-the-Loop: Step Functions Implementation

When Cedar returns an obligation requiring human approval, the PEP must pause the agent workflow, trigger the approval process, and resume only after a human decision is recorded in the authorization context. AWS Step Functions with the Wait-for-Task-Token pattern is the reference implementation.

**Step Functions state machine.** The workflow starts with a `CedarPreCheck` task that calls the Cedar authorization Lambda; a `CheckDecision` choice state routes an `ALLOW` decision straight to `ExecuteAction`, and a `REQUIRE_HUMAN_APPROVAL` obligation to `SendApprovalRequest`. `SendApprovalRequest` sends a message to an SQS approval queue carrying the task token, action, principal, resource, context, and payment amount, waiting up to 24 hours (with a 1-hour heartbeat) for a human response before timing out to `ApprovalTimeout`. Once approved, `CedarPostApprovalCheck` re-evaluates Cedar with `humanApprovalStatus: "APPROVED"`, the approver ID, and the approval timestamp in context; `CheckPostApprovalDecision` routes a resulting `ALLOW` to `ExecuteAction`, which invokes the action and writes an audit log, or otherwise to `ActionDenied`, which logs the denial:

```json
{
  "Comment": "Human Approval Workflow for High-Risk Agent Actions",
  "StartAt": "CedarPreCheck",
  "States": {
    "CedarPreCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:::function:cedar-authz-check",
      "ResultPath": "$.authorization",
      "Next": "CheckDecision"
    },
    "CheckDecision": {
      "Type": "Choice",
      "Choices": [
        { "Variable": "$.authorization.decision", "StringEquals": "ALLOW", "Next": "ExecuteAction" },
        { "Variable": "$.authorization.obligation", "StringEquals": "REQUIRE_HUMAN_APPROVAL", "Next": "SendApprovalRequest" }
      ],
      "Default": "ActionDenied"
    },
    "SendApprovalRequest": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
      "Parameters": {
        "QueueUrl": "https://sqs.region.amazonaws.com/acct/approval-queue",
        "MessageBody": {
          "taskToken.$": "$$.Task.Token",
          "action.$": "$.action", "principal.$": "$.principal",
          "resource.$": "$.resource", "context.$": "$.context",
          "amount.$": "$.context.paymentAmount",
          "requestedAt.$": "$$.Execution.StartTime"
        }
      },
      "HeartbeatSeconds": 3600, "TimeoutSeconds": 86400,
      "Catch": [{ "ErrorEquals": ["States.HeartbeatTimeout"], "Next": "ApprovalTimeout" }],
      "Next": "CedarPostApprovalCheck"
    },
    "CedarPostApprovalCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:::function:cedar-authz-check",
      "Parameters": {
        "principal.$": "$.principal", "action.$": "$.action", "resource.$": "$.resource",
        "context": {
          "humanApprovalStatus": "APPROVED",
          "approvalTimestamp.$": "$.approvalTimestamp",
          "approverId.$": "$.approverId",
          "riskScore.$": "$.context.riskScore"
        }
      },
      "Next": "CheckPostApprovalDecision"
    },
    "CheckPostApprovalDecision": {
      "Type": "Choice",
      "Choices": [{ "Variable": "$.authorization.decision", "StringEquals": "ALLOW", "Next": "ExecuteAction" }],
      "Default": "ActionDenied"
    },
    "ExecuteAction": {
      "Type": "Task", "Resource": "arn:aws:lambda:::function:execute-agent-action", "Next": "AuditLog"
    },
    "AuditLog": { "Type": "Task", "Resource": "arn:aws:lambda:::function:write-audit-record", "End": true },
    "ActionDenied": { "Type": "Task", "Resource": "arn:aws:lambda:::function:log-denial", "End": true },
    "ApprovalTimeout": {
      "Type": "Task", "Resource": "arn:aws:lambda:::function:handle-approval-timeout",
      "Comment": "Approval not received within 24 hours — deny and notify", "End": true
    }
  }
}
```

## Enterprise Audit Trail Design

A comprehensive audit trail is not optional in regulated environments. The audit record must capture sufficient information to reconstruct the authorization decision and demonstrate compliance to regulators.

**Authorization audit record schema.** Each record carries a unique audit and correlation ID, the workflow ID, high-precision timestamps, the full principal chain (agent identity plus the delegating user), the action and resource with a hash of its parameters and their classification, the decision and its source, the policy store ID and determining policies, any obligations, the full context snapshot (business hours, risk score, MFA state, device compliance, network zone, geography, prompt classification, agent confidence, session age), a latency breakdown by pipeline stage, and cryptographic integrity fields:

```json
{
  "auditId": "aud-7f3a9b2e-4c1d-4e8f-a1b2-3c4d5e6f7a8b",
  "correlationId": "req-workflow-4421-step-3",
  "workflowId": "wf-payment-processing-89012",
  "timestamp": "2026-06-26T09:47:22.341Z",
  "principal": {
    "type": "AGENT",
    "id": "agent-bedrock-payments-01",
    "delegatedFrom": { "type": "USER", "id": "emp-48291", "upn": "john.smith@bank.com" },
    "tenantId": "bank-prod"
  },
  "action": {
    "type": "InvokeTool",
    "resourceType": "Tool",
    "resourceId": "PaymentApprovalTool",
    "parameters": { "hash": "sha256:a1b2c3d4e5f6...", "parametersClassification": "CONFIDENTIAL" }
  },
  "decision": "ALLOW",
  "decisionSource": "AVP_CEDAR",
  "policyStoreId": "ps-XXXXXXXXXXXXXXXXXX",
  "determiningPolicies": ["policy-payment-tool-finance-mfa", "policy-business-hours-mandatory"],
  "obligations": [],
  "context": {
    "businessHours": true, "riskScore": 22, "mfaVerified": true, "mfaMethod": "FIDO2",
    "deviceCompliant": true, "networkZone": "CORPORATE", "geography": "GB",
    "promptClassification": "BENIGN", "agentConfidenceScore": 93, "sessionAgeMinutes": 14
  },
  "latencyMs": { "claimsNormalization": 1.2, "pipEnrichment": 0.3, "cedarEvaluation": 2.8, "total": 4.3 },
  "integrityHash": "sha256:...",
  "kmsKeyId": "arn:aws:kms:...:key/...",
  "immutableAfter": "2026-06-26T09:47:22Z"
}
```

**Audit trail implementation architecture:**

| Audit Layer | Service | Retention | Purpose |
|---|---|---|---|
| Real-time decision log | DynamoDB (audit-decisions table) | 90 days hot + S3 archive | Operational queries, incident investigation |
| Immutable API audit | CloudTrail to S3 (WORM bucket) | 7 years (regulatory) | Non-repudiation, regulator evidence |
| Structured compliance log | CloudWatch Logs Insights | 13 months | Compliance queries, SOC 2 evidence |
| SIEM integration | Security Hub + Splunk/QRadar | Per SIEM retention | Threat detection, anomaly alerting |
| Agent workflow trace | AWS X-Ray + custom segments | 30 days | Distributed tracing for agent workflows |
| Policy change audit | CloudTrail + Config | 7 years | Policy lifecycle audit, change management |

**Regulatory evidence generation.** Automated jobs query the audit-decisions table to produce evidence packages for named frameworks. A PCI DSS Requirement 7 report queries all access-control decisions for cardholder-data resource types over a date range, tallying total decisions, allow/deny counts, unique principals, the policies that determined those decisions, and any detected anomalies, then signs the package with a dedicated compliance KMS key:

```python
def generate_pci_dss_evidence(start_date: str, end_date: str) -> dict:
    response = audit_table.query(
        IndexName="resource-type-index",
        KeyConditionExpression="resourceType = :rt AND #ts BETWEEN :start AND :end",
        FilterExpression="resourceClassification IN (:pci1, :pci2)",
        ExpressionAttributeNames={"#ts": "timestamp"},
        ExpressionAttributeValues={
            ":rt": "PaymentSystem", ":start": start_date, ":end": end_date,
            ":pci1": "CARDHOLDER_DATA", ":pci2": "SENSITIVE_AUTHENTICATION_DATA",
        },
    )
    decisions = response["Items"]
    return {
        "framework": "PCI DSS v4.0",
        "requirement": "Requirement 7 - Restrict Access to System Components",
        "period": {"start": start_date, "end": end_date},
        "totalDecisions": len(decisions),
        "allowDecisions": sum(1 for d in decisions if d["decision"] == "ALLOW"),
        "denyDecisions": sum(1 for d in decisions if d["decision"] == "DENY"),
        "uniquePrincipals": len(set(d["principal"]["id"] for d in decisions)),
        "policies": extract_unique_policies(decisions),
        "anomalies": detect_anomalies(decisions),
        "generatedAt": datetime.utcnow().isoformat(),
        "generatedBy": "automated-compliance-system",
        "signedBy": "KMS-COMPLIANCE-KEY",
    }

def generate_access_review_report(period_days: int = 90) -> dict:
    # SOC 2 CC6.3: logical access is reviewed periodically
    end = datetime.utcnow()
    start = end - timedelta(days=period_days)
    return {
        "reportType": "ACCESS_REVIEW",
        "period": period_days,
        "accessGrants": get_access_grants_summary(start, end),
        "orphanedAccess": detect_orphaned_access(),
        "roleViolations": detect_role_violations(),
        "reviewDueDate": (end + timedelta(days=90)).isoformat(),
    }
```

## Agent Capability Scoping Patterns

Different agent types should have different capability scopes. A customer service agent should not have the same tool access as an internal finance agent. Cedar's entity model naturally expresses this through agent type attributes.

**Agent type taxonomy:**

| Agent Type | Purpose | Permitted Tool Categories | Prohibited Tools | Max Risk Threshold |
|---|---|---|---|---|
| CustomerService Agent | Handle customer queries, account information | Account viewer, FAQ tool, ticket creator | Payment approval, data export, DB write | Risk &lt;40 |
| Payment Processing Agent | Initiate and approve payment transactions | Payment tool, exchange rate tool, account viewer | Data export, user management, admin tools | Risk &lt;30, MFA required |
| Finance Analytics Agent | Generate financial reports and analysis | SQL query (read-only), report tool, Excel export | Write operations, payment approval, HR tools | Risk &lt;60 |
| HR Assistant Agent | Handle HR queries for authorized employees | HR portal viewer (own geography only), calendar | Payment tools, financial data, legal docs | Risk &lt;50 |
| Compliance Agent | Audit log access and compliance reporting | Audit log reader, all-data viewer (read-only) | All write operations, payment tools | Risk &lt;20, MFA + phishing-resistant |
| Developer Assistant Agent | Code assistance, documentation queries | Code search, documentation tool, ticket viewer | Production DB, payment tools, customer data | Risk &lt;70 |
| Admin Orchestrator Agent | Internal orchestration of other agents | Agent spawn, tool routing, workflow management | Direct data access, external API calls | Risk &lt;25, MFA required |

**Cedar agent type policies.** Agent type is set at registration and verified via a signed credential — agents cannot self-report their type. A CustomerService agent gets a restrictive permit plus a hard block on financial tools:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool",
  resource in BankAI::ToolGroup::"CustomerServiceTools"
)
when {
  principal.agentType == "CUSTOMER_SERVICE" &&
  principal.delegatedFrom.capabilities.contains("can_use_cs_agent") &&
  context.riskScore < 40
};

forbid(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool", resource
)
when {
  principal.agentType == "CUSTOMER_SERVICE" &&
  resource in BankAI::ToolGroup::"FinancialOperationTools"
};
```

A Payment Processing agent is gated on MFA, low risk, business hours, and a per-user payment limit:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"PaymentApprovalTool"
)
when {
  principal.agentType == "PAYMENT_PROCESSING" &&
  principal.delegatedFrom.capabilities.contains("can_approve_payment") &&
  principal.delegatedFrom.mfaVerified == true &&
  context.riskScore < 30 && context.businessHours == true &&
  context.paymentAmount <= principal.delegatedFrom.paymentLimit
};
```

A Compliance agent is read-only across document, audit-log, and report actions, but requires FIDO2 MFA and a very low risk threshold:

```
permit(
  principal is BankAI::Agent,
  action in [BankAI::Action::"ReadDocument", BankAI::Action::"QueryAuditLog", BankAI::Action::"ExportReport"],
  resource
)
when {
  principal.agentType == "COMPLIANCE" &&
  principal.delegatedFrom.capabilities.contains("can_view_all_data") &&
  principal.delegatedFrom.mfaMethod == "FIDO2" &&
  context.riskScore < 20
};
```

Finally, a cross-type block prevents any agent from invoking a tool that requires a different registered agent type, closing off type-escalation entirely:

```
forbid(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool", resource
)
when {
  resource has requiredAgentType &&
  resource.requiredAgentType != principal.agentType &&
  resource.requiredAgentType != "ANY"
};
```

## Related

- [Agent Authorization Deep Dive (Part 1)](../28-3b-agent-authorization-deep-dive.md)
- [Agent, Tool & MCP Authorization](../27-agent-tool-mcp-authorization.md)
- [RAG, Memory & Data Authorization](../29-rag-memory-data-authorization.md)
