---
title: "Agent, Tool & MCP Authorization"
doc_type: guide
domain: trust
status: current
topic_id: agent-tool-mcp-authorization
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/policy/Vol3_Agent_Tool_MCP_Authorization.md]
tags: [authorization, mcp, agent-tools, cedar]
covers_version: "as of 2026"
---

The seven-point agent authorization lifecycle, tool authorization policies and capability taxonomy, context-aware authorization signals, MCP server security architecture, and multi-agent delegation with human-in-the-loop obligations.

## Agent Authorization Lifecycle

**Authorization decision points in an agent workflow.** Every agent request passes through up to seven independent Cedar policy evaluation points. A positive decision at any earlier point does not grant permission at later points — authorization is re-evaluated at every action boundary, the Zero Trust model applied to agents. The flow runs: a user request (JWT plus canonical claims) reaches the Agent Runtime's planner, which produces an action sequence evaluated as: **P1 — Agent Invocation Authorization** (can this user invoke this agent type?); **P2 — Tool Selection Authorization** (is this tool in the agent's allowed capability set?); **P3 — Tool Invocation Authorization** (can this principal invoke this specific tool call with these parameters?); tool execution proceeds only after P1-P3 all return `ALLOW`; **P4 — Memory Read Authorization** (can this agent read this memory scope?); **P5 — Knowledge/RAG Authorization** (can this agent retrieve this document?); **P6 — Output Classification Check** (can this agent return data at this classification level?); and **P7 — Human Approval Gate**, if required (does this action require human approval before execution?) — after which the authorized, classified, audited response is returned.

**Authorization decision matrix by agent step:**

| Step | Authorization Question | Principal | Policy Engine | Context Required |
|---|---|---|---|---|
| Agent Invocation | Can this user invoke agent type X? | User | Cedar AVP | capabilities, mfa, risk_score |
| Tool Selection | Is tool T in this agent's permitted toolset? | Agent | Cedar AVP | agent_type, user_capabilities |
| Tool Invocation | Can agent (on behalf of user) call this tool now? | Agent + User | Cedar AVP | time, risk, geo, mfa, data_class |
| Memory Read | Can agent read memory scope for this user session? | Agent | Cedar AVP | session_id, memory_scope, tenant |
| Knowledge Access | Can agent retrieve this document? | Agent | Cedar AVP | doc_classification, user_clearance |
| API Call | Can agent call this downstream API endpoint? | Agent | Cedar AVP | api_scope, rate_limit, tenant |
| Output Return | Is the output data classification permitted? | Agent | Cedar AVP | output_class, user_clearance |
| Human Approval | Does this action require human approval? | Action | Cedar AVP | amount, risk_score, action_type |
| Sub-Agent Spawn | Can this agent create a sub-agent? | Agent | Cedar AVP | agent_tier, scope_constraints |

## Tool Authorization Architecture

Tools are the action surface of an AI agent. Each tool invocation must be independently authorized, considering the tool's data classification, the invoking principal's capabilities, and the runtime context.

**Tool authorization policy examples.** A SQL query tool is restricted to DBA-capable principals during business hours with non-elevated risk, and bulk exports additionally require a separate capability:

```
permit(
  principal, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"SQLQueryTool"
)
when {
  principal.capabilities.contains("can_query_production_db") &&
  context.businessHours == true &&
  context.riskScore < 50 &&
  principal.mfaVerified == true
};

forbid(
  principal, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"SQLQueryTool"
)
when {
  context.queryType == "BULK_EXPORT" &&
  !principal.capabilities.contains("can_export_bulk_data")
};
```

A SAP ERP tool is scoped to the Finance department, the user's own geography, and a fresh session (under one hour):

```
permit(
  principal, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"SAPTool"
)
when {
  principal.capabilities.contains("can_access_sap") &&
  principal.businessUnit == "FINANCE" &&
  resource.allowedGeographies.contains(principal.geography) &&
  context.sessionAge < 3600
};
```

A destructive delete tool is forbidden unless business hours, low risk, the delete capability, and prior human approval all hold:

```
forbid(
  principal, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"DeleteRecordTool"
)
unless {
  context.humanApprovalStatus == "APPROVED" &&
  context.businessHours == true &&
  context.riskScore < 30 &&
  principal.capabilities.contains("can_delete_records")
};
```

And an external SaaS API tool enforces strict tenant isolation, permitting agents to call only tools within their own tenant and matching the delegating user's capability:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool",
  resource is BankAI::Tool
)
when {
  resource has tenantId &&
  principal.tenantId == resource.tenantId &&
  principal.delegatedFrom.capabilities.contains(resource.requiredCapability)
};
```

**Tool capability taxonomy:**

| Tool Category | Example Tools | Required Capability | Additional Controls |
|---|---|---|---|
| Data Query | SQL Tool, DynamoDB Tool, Athena Tool | can_query_database | Business hours, MFA, risk &lt; 50 |
| Financial Operations | Payment Tool, Transfer Tool, FX Tool | can_approve_payment | Dual approval for &gt;$10K, MFA, low risk |
| ERP/CRM Access | SAP Tool, Salesforce Tool | can_access_erp | Department match, geography, session age |
| Document Operations | SharePoint Tool, S3 Tool | can_access_documents | Classification-based, DLP active |
| Communication | Email Tool, Teams Tool, Slack Tool | can_send_communication | Recipient validation, DLP scan |
| Code Execution | Lambda Tool, CodeBuild Tool | can_execute_code | Sandbox only, output size limit |
| Destructive Operations | Delete Tool, Purge Tool | can_delete_records | Business hours, approval, risk &lt; 30 |
| External APIs | Vendor API Tool, Partner Tool | can_call_external_api | Tenant isolation, rate limit |
| HR Systems | Workday Tool, HR Portal Tool | can_view_hr_records | Own geography only, MFA |

## Context-Aware Authorization

Static role-based authorization is insufficient for Agentic AI. Authorization decisions must be context-aware, incorporating runtime signals that affect the risk and appropriateness of an action at the moment it is requested.

**Contextual signals catalog:**

| Signal | Source | Used For | Example Policy Impact |
|---|---|---|---|
| Timestamp / Business Hours | System clock | Restrict destructive actions to office hours | Delete operations forbidden 18:00-08:00 |
| Risk Score (0-100) | Risk Engine (AWS Fraud Detector) | Elevate controls for high-risk sessions | Risk &gt;70: require additional MFA step |
| Device Compliance | Microsoft Endpoint Manager / Intune | Require managed device for sensitive data | PII access denied on unmanaged device |
| Geographic Location | IP geolocation / VPN context | Enforce data residency, geo-restrictions | EU data cannot be accessed from US |
| MFA Method & Age | Entra ID AMR claim | Require strong auth for high-value actions | Payments: phishing-resistant MFA only |
| Session Age (minutes) | Token issuance time | Require re-authentication for aged sessions | Sessions &gt;60 min: step-up auth for admin |
| Network Zone | VPC subnet tags, Zero Trust NAC | Differentiate corporate vs. remote access | CORPORATE allows all; REMOTE restricted |
| Agent Confidence Score | LLM reasoning chain | Limit tool access if agent is uncertain | Confidence &lt;80%: require human review |
| Prompt Classification | Content classifier (Bedrock Guardrails) | Block prompt injection, jailbreak attempts | Injected prompt: deny and alert |
| Data Sensitivity | AWS Macie, data catalog | Enforce proportional access controls | TOP_SECRET: additional approval required |
| Purpose / Task Type | Agent task metadata | Restrict tools to task-appropriate subset | Tax task: only tax tools accessible |
| Approval Status | Workflow engine (Step Functions) | Gate on explicit prior approval | Payment &gt;$50K: APPROVED status required |
| Threat Score | AWS GuardDuty, SIEM | Emergency circuit breaker | Active threat: deny all non-essential access |

The context object passed to Cedar evaluation aggregates all of these signals into a single structured record for each request — request ID, timestamp, business-hours flag, risk score, device compliance, network zone, geography, MFA method and age, session age, agent confidence score, prompt classification, data classification, purpose code, human-approval status, threat score, DLP status, tenant ID, agent ID, and workflow ID.

## MCP Server Security Architecture

The Model Context Protocol (MCP) is the emerging standard for connecting AI agents to tools, APIs, and data sources. Every enterprise MCP deployment must treat the MCP boundary as a security perimeter requiring full policy enforcement.

**MCP authorization architecture.** The Agent Runtime's MCP client (agent-side, carrying a delegation token) calls through an MCP PEP gateway layer that runs four sequential authorization checks: Tool Discovery Authorization (can this agent discover these tools?); Tool Invocation Authorization (can this agent invoke this specific tool?); Parameter Validation (are inputs within schema and policy bounds?); and Output Classification Filter (can this agent receive output at this classification level?). Only after all four checks pass does the request reach the MCP server's tool handlers — the MCP server itself never authorizes its own requests.

**MCP security requirements:**

| Security Requirement | Implementation | Policy Engine |
|---|---|---|
| Tool Discovery Authorization | Cedar policy: agent type X may only discover tools in permitted tool group G | Cedar AVP |
| Tool Invocation Authorization | Every tool call passes through the PEP; Cedar evaluates per-tool policies | Cedar AVP |
| Dynamic Tool Registration | New tools cannot be registered without a policy-store update and CI/CD approval | Cedar PAP |
| MCP Authentication | MCP client must present a valid delegation token (RFC 8693) | JWT validation layer |
| Parameter Input Validation | Tool parameters validated against JSON Schema and policy constraints | Cedar + schema |
| Output Classification | MCP server tags outputs with data classification; PEP filters based on agent clearance | Cedar AVP |
| Remote MCP TLS | Remote MCP connections require mutual TLS; certificate pinning for production | AWS Certificate Manager |
| Local MCP Sandbox | Local MCP processes run in isolated containers with restricted IAM roles | OPA + IAM |
| Tool Rate Limiting | Per-agent, per-tool rate limits enforced at the MCP PEP | PEP middleware |
| Audit Logging | Every MCP tool invocation logged with principal, tool, parameters hash, outcome | CloudTrail |

**MCP tool Cedar policies.** Tool discovery is restricted by agent type and delegated capability:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"DiscoverTools",
  resource is BankAI::ToolGroup
)
when {
  resource == BankAI::ToolGroup::"PaymentTools" &&
  principal.agentType == "PaymentAgent" &&
  principal.delegatedFrom.capabilities.contains("can_approve_payment")
};
```

Tool invocation evaluates the full context, including a check that no prompt injection was detected:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeMCPTool",
  resource is BankAI::Tool
)
when {
  principal.delegatedFrom.capabilities.contains(resource.requiredCapability) &&
  context.riskScore < 60 &&
  context.tenantId == resource.tenantId &&
  context.promptClassification != "INJECTION"
};

forbid(
  principal, action == BankAI::Action::"InvokeMCPTool", resource
)
when {
  context.promptClassification == "INJECTION"
};
```

## Multi-Agent Workflow Authorization

Multi-agent architectures introduce the confused deputy problem: a downstream agent may be granted permissions by an orchestrating agent that the orchestrator does not itself possess. Cedar policies must explicitly address agent-to-agent delegation boundaries.

**Multi-agent trust architecture.** The user's JWT establishes a delegated scope for the Orchestrator Agent (Level 0), which is constrained by the user's own capabilities and cannot grant sub-agents more than its own scope. Each Specialist Agent (Level 1) receives a scope equal to the intersection of the orchestrator's scope and that specialist's own permitted tools — Cedar evaluates both the delegation and the tool permission at each hop, and there is no cross-contamination between specialist agents' scopes. A Human Approval Gate, triggered by a Cedar obligation on high-risk actions, runs as an AWS Step Functions human task, with the approval result stored in context and re-verified by Cedar at the next step. The governing principle: sub-agent scope is a subset of orchestrator scope, which is a subset of the user's delegated scope, which is a subset of the user's own capabilities.

**Human-in-the-loop authorization pattern.** Cedar can return obligations alongside Allow/Deny decisions — an obligation instructs the PEP to take a specific action before execution proceeds, most importantly requiring human approval. Payments at or below a threshold are permitted directly; payments above the threshold require a prior, time-bounded human approval:

```
permit(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"PaymentExecutionTool"
)
when {
  principal.delegatedFrom.capabilities.contains("can_approve_payment") &&
  context.paymentAmount <= 10000
};

permit(
  principal is BankAI::Agent, action == BankAI::Action::"InvokeTool",
  resource == BankAI::Tool::"PaymentExecutionTool"
)
when {
  principal.delegatedFrom.capabilities.contains("can_approve_payment") &&
  context.paymentAmount > 10000 &&
  context.humanApprovalStatus == "APPROVED" &&
  context.approvalTimestamp > (context.currentTime - 300)  // within 5 minutes
};
```

**Cedar obligation pattern:** when Cedar returns `ALLOW` with an obligation of `REQUIRE_HUMAN_APPROVAL`, the PEP must not execute the action immediately. Instead it must trigger the approval workflow (an AWS Step Functions human task), await the approval, and re-evaluate the Cedar policy with `humanApprovalStatus=APPROVED` in the context. Enforcing obligations is the PEP's responsibility, not the policy engine's.

## End-to-End Sequence Diagrams

**REST API agent authorization flow:** the client sends a request with a JWT to the API Gateway; the Lambda Authorizer validates the JWT signature; the Claims Service normalizes claims to canonical form; Cedar AVP's `IsAuthorized` is called and returns `ALLOW`; the Lambda Authorizer returns a cached IAM policy and API Gateway routes the request to the Agent Runtime; the Agent Runtime calls per-tool Cedar authorization, which also returns `ALLOW`; the agent invokes the tool and receives a result; the result is logged and the response returned to the client.

**Multi-agent workflow authorization sequence:** the user invokes the Orchestrator, which passes the P1 agent-invocation check; the Orchestrator plans a step and passes a delegation check; it delegates to Specialist Agent A; Specialist A's P3 tool authorization returns `ALLOW` plus an obligation (if the payment exceeds $10K, human approval is required); the Human Approval Gate is triggered and an approver reviews and approves; a re-authorization (P3b) with `humanApprovalStatus=APPROVED` returns `ALLOW`; Specialist A invokes the tool and a result is returned; the result flows back from Specialist A through the Orchestrator to the user.

## Related

- [Agent Authorization Deep Dive](28-3b-agent-authorization-deep-dive.md)
- [Advanced Policy Engineering](26-2b-advanced-policy-engineering.md)
- [RAG, Memory & Data Authorization](29-rag-memory-data-authorization.md)
