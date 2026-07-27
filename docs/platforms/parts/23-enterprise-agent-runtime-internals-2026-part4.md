---
title: "Enterprise AI Agent Runtime Internals: AWS, Azure & GCP (2026) (Part 4)"
doc_type: guide
domain: platforms
status: current
topic_id: enterprise-agent-runtime-internals-2026-part4
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [aws, azure, gcp, authentication, authorization]
covers_version: "as of 2026-07-11 — AWS Bedrock AgentCore GA, Azure AI Foundry Agent Service, Google Vertex AI Agent Engine"
---

> Continues from [Enterprise AI Agent Runtime Internals: AWS, Azure & GCP (2026)](../23-enterprise-agent-runtime-internals-2026.md), covering the full request execution pipeline for each platform, authentication, and authorization.

## Request Execution Pipeline

### AWS Bedrock AgentCore — Full Pipeline

1. **Client Request** — User/app sends `POST /agents/{agentId}/sessions/{sessionId}/turns`; auth via SigV4-signed request (access key/secret or IAM Role).
2. **API Gateway / CloudFront Edge** — TLS 1.3 termination at CloudFront PoP; WAF rules (rate limiting, IP allowlist, OWASP rules); route to regional AgentCore API.
3. **AgentCore API (control plane)** — Validate SigV4 signature; authenticate via STS AssumeRole validation; authorize via IAM policy check (`bedrock:InvokeAgent`); resolve session → runtime mapping.
4. **Cedar Policy Evaluation** — Amazon Verified Permissions evaluates `agent.allowed_tools`, `user.risk_class`, `session.context`; LOG_ONLY mode during rollout → ENFORCE mode in production; deny by default, explicit permit required.
5. **Session Routing** — Sticky session: route to existing Fargate task if session is warm; cold session: trigger Fargate task creation + session restore from DynamoDB.
6. **Bedrock Guardrails (pre-model)** — Prompt Shield (prompt injection detection); PII detection and masking; denied topics; grounding/hallucination-risk detection.
7. **Agent Runtime (Fargate Task)** — Planner selects tools and builds a reasoning trace; context assembly loads memory, session history, tool schemas; memory retrieval via semantic search over AgentCore Memory.
8. **Bedrock Model Inference** — Route to the appropriate Bedrock model (Claude, Titan, etc.); Cross-Region Inference for availability; token counting and quota enforcement.
9. **Tool Execution (Lambda / MCP Gateway)** — For Lambda tools, STS AssumeRole for tool-specific permissions; for MCP tools, AgentCore Gateway authenticates to the MCP server; Cedar policy re-evaluated for each tool invocation.
10. **Response Assembly** — Tool results merged into model context; additional model turns if needed (agentic loop).
11. **Output Guardrails** — PII masking on output; content safety filter; sensitive-data detection (GuardDuty/Macie integration).
12. **Audit Logging** — CloudTrail records every API call, IAM decision, and policy evaluation; CloudWatch Logs capture detailed agent execution trace; Bedrock Invocation Logs record model inputs/outputs (if enabled).
13. **Session Checkpoint** — Updated session state written to DynamoDB; memory extraction triggered asynchronously.
14. **Response to Client** — Streaming (SSE) or synchronous response; token-usage metadata in response headers.

### Azure AI Foundry Agent Service — Full Pipeline

1. **Client Request** — `POST /openai/assistants/{assistant_id}/threads/{thread_id}/runs`; auth via Entra Bearer token (MSAL) or API key.
2. **Azure API Management (APIM)** — TLS 1.3 termination; JWT validation (Entra token); rate limiting (TPM, RPM policies); content-type validation.
3. **AI Foundry API (control plane)** — Validate Managed Identity or Bearer token; authorize via Azure RBAC check (`Cognitive Services User`/`Contributor` role); resolve assistant → ACA runtime mapping.
4. **Azure Policy Evaluation** — Built-in policies (content safety, resource limits, geography); custom policies via OPA integration (preview); initiative assignment evaluation.
5. **Session Routing** — ACA session affinity routes to an existing replica if active; new replica scales out (scale-to-zero if idle); Cosmos DB thread load.
6. **Azure Content Safety (pre-model)** — Prompt Shield (prompt injection detection); Hate/Violence/Sexual/Self-harm classification; groundedness detection via Azure Content Safety Groundedness API.
7. **Agent Runtime (ACA Replica)** — Azure AI SDK runtime; tool resolution across registered tools and MCP servers; Dapr state store loads conversation context.
8. **Azure OpenAI / Model Inference** — PTU (Provisioned Throughput Unit) deployment tried first; fallback to paygo deployment on capacity; OBO token used for cross-service auth within the tenant.
9. **Tool / Function Execution** — Azure Functions invoked via Managed Identity; Code Interpreter runs sandboxed Python execution in an isolated container; Bing Search via managed AI Foundry integration; MCP servers invoked via the APIM MCP proxy.
10. **Response Assembly + Additional Turns** — Model turns repeat as needed for the agentic loop.
11. **Output Safety Filter** — Jailbreak detection on output; PII classification; custom blocklist matching.
12. **Audit and Monitoring** — Azure Monitor tracks metrics (token usage, latency, error rates); Application Insights captures distributed traces; Azure Diagnostic Logs record all API calls to Log Analytics.
13. **Thread State Persistence** — Messages appended to the Cosmos DB thread container; run status updated in Cosmos DB.
14. **Response to Client** — Polling model (retrieve Run) or streaming (SSE).

### Google Cloud Vertex AI Agent Engine — Full Pipeline

1. **Client Request** — `POST /v1/projects/{project}/locations/{location}/reasoningEngines/{id}:query`; auth via OAuth 2.0 Bearer token (service account or user credential).
2. **Cloud Load Balancing + Cloud Armor** — TLS 1.3 termination at GFE (Google Front End); Cloud Armor WAF (OWASP rules, rate limiting, adaptive ML-based DDoS protection); global anycast routing to nearest Google PoP.
3. **Vertex AI API (control plane)** — Validate OAuth 2.0 token against Google auth servers; authorize via IAM policy check (`roles/aiplatform.user` or custom role); VPC Service Controls boundary check (if configured).
4. **IAM + VPC Service Controls** — Perimeter evaluation (is this access from within the VPC perimeter?); attribute-based access conditions evaluation; service-account impersonation check for OBO patterns.
5. **Session Resolution** — Resolve `session_id` → Cloud Run instance via session-affinity cookie; new session allocates a Cloud Run instance from the warm pool; Firestore loads session events.
6. **Vertex AI Safety / Guardrails (pre-model)** — Gemini built-in safety filters (Harm Categories API); Vertex AI Model Armor (prompt injection detection, GA 2026); PII detection via Cloud DLP.
7. **Agent Runtime (Cloud Run / gVisor)** — Google ADK/LangChain runtime; Memory API retrieves relevant memories; tool schema resolution via the Extensions registry.
8. **Vertex AI Model Inference (Gemini / custom)** — Gemini 1.5 Pro / Gemini 2.0 Flash (region-specific); Model Garden access for open-source models; quota enforcement (tokens per minute, requests per minute).
9. **Tool Execution (Extensions / Cloud Functions / MCP)** — Vertex AI Extensions invoked via the internal Anthos service mesh; Cloud Functions triggered via an internal GCP service account; Vertex AI Toolbox (MCP server for databases); Workload Identity Federation for external service calls.
10. **Response Iteration** — Agentic loop repeats as needed.
11. **Output Safety + Data Governance** — Vertex AI safety filters on output; Cloud DLP PII detection (streaming or batch); data-catalog policy-tag enforcement.
12. **Observability** — Cloud Logging captures structured agent execution logs; Cloud Trace provides distributed tracing across all GCP services; Cloud Monitoring tracks custom Agent Engine metrics; BigQuery export for long-term audit and analytics.
13. **Session Persistence** — Events appended to the Firestore session collection; Memory API extracts and stores long-term memories asynchronously.
14. **Response to Client** — Streaming or synchronous response; usage metadata (token counts, latency) included in the response.

## Authentication

### AWS Authentication Stack

**Inbound (client → AgentCore):** [DOCUMENTED]

- SigV4 signed requests (AWS Signature Version 4)
- IAM roles via STS AssumeRole / AssumeRoleWithWebIdentity
- Cognito User Pool tokens for end-user-facing agent APIs
- API Keys for testing (not recommended for production)

**Within platform (AgentCore → AWS services):** [DOCUMENTED]

- Task IAM Role: Fargate task assumes a unique IAM role per session
- STS GetSessionToken / AssumeRole for scoped temporary credentials
- IAM Roles Anywhere for hybrid cloud (on-premises agent calling AWS services)

**Cross-service token propagation:** [DOCUMENTED]

- SigV4 is used for all AWS service calls (Bedrock, DynamoDB, Lambda, S3)
- Agent identity is always the Task IAM Role, not the calling user
- User identity passed as a claim in the request body; policy uses `aws:PrincipalTag` or session context

**MCP server authentication:** [DOCUMENTED]

- AgentCore Gateway uses IAM Role to authenticate to MCP servers via SigV4 (for AWS-hosted MCP)
- OAuth 2.0 client credentials for external (non-AWS) MCP servers

### Azure Authentication Stack

**Inbound (client → AI Foundry):** [DOCUMENTED]

- Entra ID Bearer token (MSAL authentication flow)
- API Key (via AI Foundry resource key — not recommended for production)
- Managed Identity (for app-to-agent scenarios)

**Within platform (AI Foundry → Azure services):** [DOCUMENTED]

- System-assigned or User-assigned Managed Identity for the ACA app
- MI token obtained from IMDS (Instance Metadata Service, 169.254.169.254)
- Azure OpenAI accessed via MI with the Cognitive Services User role
- Cosmos DB accessed via MI with the Cosmos DB Built-in Data Contributor role
- Key Vault accessed via MI for secret retrieval

**On-Behalf-Of (OBO):** [DOCUMENTED]

- AI Foundry supports OBO flows for delegated user permissions
- Entra OBO grant: agent acts on behalf of the signed-in user for SharePoint, Graph API access
- OBO token exchange: user access token → agent-scoped token for the downstream resource

**MCP server authentication:** [DOCUMENTED + INFERRED]

- APIM policy: extract the incoming Managed Identity token, exchange for an MCP server OAuth token
- Custom auth header injection in APIM policy for proprietary MCP servers

### GCP Authentication Stack

**Inbound (client → Agent Engine):** [DOCUMENTED]

- OAuth 2.0 Bearer token (Google auth: user or service account)
- Service Account JSON key (not recommended) or Workload Identity Federation
- API Key (for public, low-risk APIs only)

**Within platform (Agent Engine → GCP services):** [DOCUMENTED]

- Service Account attached to the Cloud Run instance
- Workload Identity binding: Kubernetes SA → GCP SA (no key file)
- Short-lived token obtained from the metadata server (169.254.169.254/computeMetadata/v1/)
- Impersonation: Cloud Run SA impersonates a specific SA for scoped access to sensitive services

**Cross-service token propagation:** [DOCUMENTED]

- `Authorization: Bearer {access_token}` for all GCP API calls from Cloud Run
- Service Account is the agent's identity (not the end user)
- End-user identity passed in `X-Goog-Authenticated-User-*` headers or as request context

**External MCP authentication:** [INFERRED]

- Cloud Run workload identity token presented to external MCP servers via Workload Identity Federation
- OIDC token from the metadata server used as a bearer token for third-party OAuth MCP servers

### Authentication Comparison

| Mechanism | AWS | Azure | GCP |
|---|---|---|---|
| **Primary auth standard** | SigV4 + IAM | Entra Bearer + MSAL | OAuth 2.0 Bearer |
| **Workload identity** | IAM Task Role (IRSA) | Managed Identity | Workload Identity Federation |
| **Short-lived credentials** | STS (15min–1h) | MI token (1h) | Access token (1h) |
| **Token source** | STS service | Entra ID (MSAL) | Google metadata server |
| **User delegation** | Cognito + STS Federation | Entra OBO | IAM service account impersonation |
| **No-secret auth** | IRSA / Roles Anywhere | System Managed Identity | Workload Identity |
| **Cross-cloud** | IAM Roles Anywhere + OIDC | Workload Identity Federation (preview) | Workload Identity Federation |
| **Hybrid cloud** | IAM Roles Anywhere | Entra hybrid joined machines | Cloud Identity + BeyondCorp |

## Authorization

### AWS Authorization — Cedar + IAM

**Two-layer authorization model:** [DOCUMENTED]

1. **IAM Layer:** Coarse-grained — "Can this identity call this AWS service/operation?"
2. **Cedar (Verified Permissions) Layer:** Fine-grained — "Can this agent perform this specific action on this specific resource, given this context?"

**IAM policy for AgentCore:** [DOCUMENTED]

```json
{
  "Action": ["bedrock:InvokeAgent", "bedrock:InvokeAgentWithResponseStream"],
  "Resource": "arn:aws:bedrock:us-east-1:*:agent-alias/AGENT123/AGALIAS456",
  "Condition": { "StringEquals": { "aws:RequestedRegion": "us-east-1" } }
}
```

**Cedar policy for tool authorization:** [DOCUMENTED]

```cedar
permit(
  principal is AgentUser,
  action == Action::"InvokeTool",
  resource is Tool::"payment_processor"
) when {
  principal.risk_classification == "low" &&
  context.request_time.hour >= 8 &&
  context.request_time.hour <= 18
};
```

**Authorization evaluation sequence:** [DOCUMENTED]

1. IAM policy evaluation (AWS authorization service — fast, coarse)
2. Session policy restrictions (scoped temporary credentials)
3. Cedar policy evaluation (fine-grained, agent-specific)
4. Resource-based policy (if applicable — S3 bucket policy, etc.)

### Azure Authorization — Azure RBAC + Conditional Access

**RBAC roles for AI Foundry:** [DOCUMENTED]

- `Cognitive Services User`: invoke agents, create threads
- `Cognitive Services Contributor`: manage agents and assistants
- `Cognitive Services OpenAI User`: use OpenAI models
- Custom RBAC roles with fine-grained permissions

**Conditional Access (Entra ID):** [DOCUMENTED]

- Risk-based: require MFA for admin operations based on sign-in risk
- Device compliance: require a compliant device for accessing AI Foundry
- Location: restrict access to specific IP ranges or named locations
- Frequency: require fresh auth for session-sensitive operations

**Azure Policy for AI governance:** [DOCUMENTED]

- Allowed AI model deployments: restrict which models can be deployed
- Network: enforce Private Endpoint requirement
- Tagging: require compliance tags on AI Foundry resources
- Diagnostic settings: require logging to Log Analytics

**OPA integration (preview):** [EVIDENCE]

- Azure Arc + OPA Gatekeeper for custom fine-grained policy enforcement
- Policy bundles served from Azure Blob Storage
- Admission controller pattern for agent registration

### GCP Authorization — IAM Conditions + VPC Service Controls

**IAM roles for Vertex AI Agent Engine:** [DOCUMENTED]

- `roles/aiplatform.user`: invoke reasoning engines, create sessions
- `roles/aiplatform.admin`: deploy and manage agent engines
- Custom roles with fine-grained Vertex AI permissions

**IAM Conditions:** [DOCUMENTED]

```python
# IAM condition for time-restricted access
{
    "title": "Business hours only",
    "expression": "request.time.getHours('America/New_York') >= 8 && request.time.getHours('America/New_York') <= 18"
}
```

**VPC Service Controls:** [DOCUMENTED]

- Service perimeter defines which services can communicate
- Data exfiltration prevention: even authenticated requests are blocked if outside the perimeter
- Ingress/egress rules control access from specific identities or VPCs
- Particularly important for regulated industries: PHI data must not leave the GCP environment

**OPA on GKE:** [INFERRED]

- Vertex AI's internal policy enforcement likely uses OPA + Gatekeeper for Kubernetes-level admission
- Agent deployments validated against policy before being admitted to the cluster

## Related

- [Enterprise Agent Runtime Internals](../23-enterprise-agent-runtime-internals-2026.md) — executive summary, runtime architecture, compute isolation
- [Enterprise Agent Runtime Internals (Part 3)](23-enterprise-agent-runtime-internals-2026-part3.md) — Memory architecture, MCP runtime integration, sidecars & service mesh
- [Enterprise Agent Runtime Internals (Part 5)](23-enterprise-agent-runtime-internals-2026-part5.md) — Zero trust, service-to-service trust, guardrails, middleware, policy engine
