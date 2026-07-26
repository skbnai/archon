---
title: "Agent Identity for AI Systems: Microsoft Entra Agent ID vs AWS AgentCore Identity"
doc_type: guide
domain: protocols
status: current
topic_id: agent-identity-entra-vs-awsagentcore
last_reviewed: 2026-07-25
supersedes:
  - docs/ai-protocols/auth/agent-identity-entra-vs-awsagentcore.md
---

# Agent Identity for AI Systems

Microsoft Entra Agent ID vs AWS AgentCore Identity — Complete Technical Comparison

*Enterprise Cloud Architecture Research · June 2026 · v1.0*

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What is Agent Identity?](#1-what-is-agent-identity)
3. [Microsoft Entra Agent ID](#2-microsoft-entra-agent-id)
4. [AWS AgentCore Identity](#3-aws-agentcore-identity)
5. [Cross-Cloud Integration Architecture](#4-cross-cloud-integration-architecture)
6. [Feature Comparison](#5-feature-comparison)
7. [Decision Framework](#6-decision-framework)
8. [Security Considerations](#7-security-considerations)
9. [Conclusion &amp; Recommendations](#8-conclusion--recommendations)

## Executive Summary

As AI agents move from prototypes to enterprise production, they expose a fundamental gap: existing identity systems designed for humans or traditional applications are insufficient for the dynamic, autonomous, and often ephemeral nature of AI workloads. In 2025–2026, both Microsoft and Amazon Web Services released dedicated agent identity platforms — Microsoft Entra Agent ID (GA: May 2026) and AWS AgentCore Identity (GA: October 2025) — both reaching enterprise maturity within months of each other.

This guide provides a deep technical comparison: architecture, authentication flows, governance models, code patterns, and a decision framework for architects choosing between, or combining, both systems in multi-cloud deployments.

**Key Finding:** The two platforms are designed for interoperability. AWS AgentCore Identity and Microsoft Entra Agent ID can be federated via OIDC/WIF, enabling AWS-native agents to carry Entra-governed identities — the recommended pattern for multi-cloud enterprise deployments.

---

## 1. What is Agent Identity?

Traditional identity systems recognise two principal types: human users (with interactive login, MFA, and session-based tokens) and service accounts / app registrations (with client secrets or certificates). AI agents fit neither model cleanly:

- Agents may be **ephemeral** — created and destroyed thousands of times per day
- Agents operate **autonomously** without interactive user sessions
- Agents may **act on behalf of users** without users being present
- Agents must call multiple downstream services with **scoped, least-privilege tokens**
- Agents need **auditability** — who the agent acted as, when, and what it accessed

Agent Identity systems solve this by introducing purpose-built identity constructs that support dynamic lifecycle management, delegated user authority (OBO), credential-less authentication via federation, and enterprise governance — all applied to non-human principals.

---

## 2. Microsoft Entra Agent ID

Microsoft Entra Agent ID reached general availability on May 1, 2026 as part of the broader Microsoft Entra suite. It extends Entra's existing identity infrastructure to AI agents, introducing three new identity constructs and specialised OAuth flows.

### 2.1 Core Constructs

Entra Agent ID introduces a three-tier identity hierarchy:

| **Tier** | **Object** | **Purpose** |
| --- | --- | --- |
| Blueprint | Agent Identity Blueprint | Reusable template defining the security envelope for a class of agents. Sets allowed scopes, lifecycle policies, owner/sponsor assignments, and Conditional Access requirements. |
| Identity | Agent Identity | The actual identity instance created from a Blueprint. A special service principal in Entra ID with no credentials of its own — tokens are acquired via the Blueprint. |
| User | Agent User Account | A backing user identity for on-behalf-of (OBO) scenarios. Enables an agent to acquire user-scoped tokens that carry the user's identity claims to downstream services. |

**Creating an Agent Identity Blueprint via Microsoft Graph API (Python):**

```python
import requests

# Step 1: Authenticate with Microsoft Entra (client credentials)
TOKEN_URL = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
creds = {
    "client_id": "&lt;client_id&gt;",
    "client_secret": "&lt;client_secret&gt;",
    "scope": "https://graph.microsoft.com/.default",
    "grant_type": "client_credentials"
}
token_resp = requests.post(TOKEN_URL, data=creds)
access_token = token_resp.json()["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Step 2: Create Agent Identity Blueprint
blueprint_payload = {
    "displayName": "FinanceAnalystAgent",
    "description": "Blueprint for financial analysis agents",
    "accessEnvelope": {
        "allowedScopes": ["User.Read", "Files.Read", "Mail.Read"]
    },
    "lifecyclePolicy": {
        "maxLifetimeDays": 90
    }
}
resp = requests.post(
    "https://graph.microsoft.com/v1.0/agentIdentityBlueprints",
    headers=headers,
    json=blueprint_payload
)
blueprint_id = resp.json()["id"]

# Step 3: Instantiate an Agent Identity from the Blueprint
agent_payload = {"blueprintId": blueprint_id, "displayName": "FinAgent-001"}
agent_resp = requests.post(
    "https://graph.microsoft.com/v1.0/agentIdentities",
    headers=headers,
    json=agent_payload
)
print(f"Agent Identity ID: {agent_resp.json()['id']}")
```

### 2.2 Workload Identity Federation with AWS

For AWS-hosted agents that need Microsoft resource access, Entra Agent ID supports Workload Identity Federation (WIF) — allowing an agent to exchange an AWS STS OIDC token directly for an Entra access token, with no secrets stored anywhere.

**AWS Agent exchanging STS OIDC token for Microsoft Entra token (WIF pattern):**

```python
import boto3
import requests

# Step 1: AWS agent acquires its own STS OIDC token
sts_client = boto3.client("sts", region_name="us-east-1")
assumed = sts_client.assume_role_with_web_identity(
    RoleArn="arn:aws:iam::123456789012:role/AgentEntraFederationRole",
    RoleSessionName="agent-session",
    WebIdentityToken=open("/var/run/secrets/eks.amazonaws.com/serviceaccount/token").read()
)
aws_oidc_token = assumed["Credentials"]["SessionToken"]

# Step 2: Exchange AWS OIDC token for Microsoft Entra token via WIF
TENANT_ID = "your-tenant-id"
ENTRA_APP_ID = "your-entra-app-id"

entra_resp = requests.post(
    f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
    data={
        "client_id": ENTRA_APP_ID,
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": aws_oidc_token,
        "scope": "https://graph.microsoft.com/.default",
        "requested_token_use": "on_behalf_of"
    }
)
entra_token = entra_resp.json()["access_token"]
print("Entra token acquired — no secrets stored anywhere")

# Step 3: Call Microsoft Graph as the agent
graph_resp = requests.get(
    "https://graph.microsoft.com/v1.0/me/messages?$top=5",
    headers={"Authorization": f"Bearer {entra_token}"}
)
```

### 2.3 Conditional Access &amp; Governance

A key differentiator of Entra Agent ID is that agents receive the same Conditional Access policies as human users — real-time risk signals, location controls, and device compliance requirements can all be applied to agent token issuance. Lifecycle Workflows automate sponsor notifications and access expiry. All agent authentication events appear in Entra Sign-in Logs and Microsoft Sentinel.

---

## 3. AWS AgentCore Identity

AWS AgentCore Identity reached general availability in October 2025, several months ahead of Microsoft's offering. It is a standalone service within Amazon Bedrock AgentCore that provides identity and credential management for agents running anywhere — on AWS compute (ECS, Lambda, EKS), on-premises, or on other clouds.

### 3.1 Core Constructs

AgentCore Identity is built around **Workload Identities** — a stable identity anchor that abstracts multiple credential types (IAM, OAuth2, API keys) behind a unified interface.

| **Component** | **Description** |
| --- | --- |
| Workload Identity | The primary identity object for an agent. Identified by a Workload Identity ARN. Created automatically via AgentCore Runtime/Gateway, or manually. |
| Token Vault | Secure storage for OAuth refresh tokens, enabling agents to maintain long-lived access to third-party services without re-authorisation. |
| Credential Providers | Configured connections to external OAuth services (Microsoft Graph, Salesforce, etc.). Agents call `GetResourceOauth2Token` for a scoped token per downstream service. |
| Secrets Manager Integration | As of June 2026, customers can reference existing Secrets Manager ARNs in Credential Providers with CMK encryption and automatic rotation. |

**Creating a Workload Identity and getting an access token (Python + boto3):**

```python
import boto3

agentcore = boto3.client("bedrock-agentcore", region_name="us-east-1")

# Create a workload identity for your agent
response = agentcore.create_workload_identity(
    name="finance-analyst-agent",
    description="Identity for the Q2 financial analysis agent",
    allowedClientIds=["arn:aws:iam::123456789012:role/AgentExecutionRole"],
    tags={"Environment": "production", "Team": "finance", "CostCenter": "AI-Ops"}
)
workload_identity_arn = response["workloadIdentityArn"]

# Get a workload access token (M2M — agent acting as itself)
token_resp = agentcore.get_workload_access_token(
    workloadIdentityArn=workload_identity_arn
)
access_token = token_resp["accessToken"]

# Configure a credential provider for Microsoft Graph access
cred_provider = agentcore.create_credential_provider(
    name="msgraph-provider",
    credentialProviderType="OAUTH2",
    oauth2Config={
        "authorizationEndpoint": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
        "tokenEndpoint": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        "clientId": "&lt;entra_app_client_id&gt;",
        "secretArn": "arn:aws:secretsmanager:us-east-1:123:secret:entra-client-secret",
        "scopes": ["https://graph.microsoft.com/Mail.Read", "https://graph.microsoft.com/Files.Read"]
    }
)
```

### 3.2 On-Behalf-Of (OBO) Token Exchange

Released in April 2026, OBO Token Exchange enables an agent to accept a user's JWT and exchange it for a downstream-scoped token that carries both the user's identity and the agent's identity — with no browser redirect and no additional consent prompt.

```python
import boto3, requests

agentcore = boto3.client("bedrock-agentcore", region_name="us-east-1")
WORKLOAD_ARN = "arn:aws:bedrock-agentcore:us-east-1:123456789:workloadIdentity/agent-001"

# Inbound: user JWT from your app's auth layer (Cognito, Entra, Okta, etc.)
user_jwt = "&lt;inbound_user_access_token&gt;"

# Step 1: Exchange user JWT for an AgentCore workload access token (OBO)
obo_resp = agentcore.get_workload_access_token_for_jwt(
    workloadIdentityArn=WORKLOAD_ARN,
    jwt=user_jwt
)
agent_token = obo_resp["accessToken"]

# Step 2: Use AgentCore to get a downstream OAuth token preserving user identity
cred_resp = agentcore.get_resource_oauth2_token(
    workloadIdentityArn=WORKLOAD_ARN,
    credentialProviderName="msgraph-provider",
    oauth2Flow="ON_BEHALF_OF_TOKEN_EXCHANGE",
    scopes=["https://graph.microsoft.com/Files.Read"]
)
downstream_token = cred_resp["accessToken"]

# Step 3: Call Microsoft Graph AS THE USER via the agent
graph_resp = requests.get(
    "https://graph.microsoft.com/v1.0/me/drive/root/children",
    headers={"Authorization": f"Bearer {downstream_token}"}
)
# SharePoint/Graph sees the USER's identity, not just the bot's
```

### 3.3 Bring Your Own Secrets (June 2026)

AgentCore Identity supports referencing existing Secrets Manager ARNs directly, enabling organisation-specific governance: custom CMKs, tagging strategies, automatic rotation policies, and resource-level IAM.

```python
import boto3

secrets_mgr = boto3.client("secretsmanager", region_name="us-east-1")
agentcore = boto3.client("bedrock-agentcore", region_name="us-east-1")

# Step 1: Create your own secret with CMK and rotation policy
secret = secrets_mgr.create_secret(
    Name="agentcore/prod/entra-client-secret",
    SecretString='{"client_secret": "your-secret-value"}',
    KmsKeyId="arn:aws:kms:us-east-1:123:key/cmk-key-id",
    Tags=[
        {"Key": "Environment", "Value": "production"},
        {"Key": "ManagedBy", "Value": "AgentCore"},
    ]
)
secrets_mgr.rotate_secret(
    SecretId=secret["ARN"],
    RotationRules={"AutomaticallyAfterDays": 30}
)

# Step 2: Reference the existing secret ARN in AgentCore (BYO pattern)
agentcore.create_credential_provider(
    name="entra-provider-cmk",
    credentialProviderType="OAUTH2",
    oauth2Config={
        "tokenEndpoint": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        "clientId": "&lt;entra_app_id&gt;",
        "secretArn": secret["ARN"],   # Reference existing secret — not service-managed
        "scopes": ["https://graph.microsoft.com/.default"]
    }
)
```

---

## 4. Cross-Cloud Integration Architecture

The most powerful enterprise pattern combines both platforms: agents built and deployed on AWS Bedrock with a Microsoft Entra Agent ID as their governed identity for accessing Microsoft 365 resources.

### 4.1 Architecture Flow

| **Step** | **Actor** | **Action** |
| --- | --- | --- |
| 1 | User | Authenticates via your app using Entra ID (or Cognito/Okta). App receives a user JWT. |
| 2 | App | Calls the AWS-hosted Bedrock agent, passing the user JWT as a bearer token. |
| 3 | AgentCore | Validates the inbound token via OIDC against your IdP (Entra/Cognito). |
| 4 | AgentCore | Exchanges the user JWT for a workload access token carrying the user's identity. |
| 5 | AgentCore | Calls Entra's token endpoint with the AWS workload token as a federated credential assertion (WIF). |
| 6 | Entra Agent ID | Validates the WIF trust relationship and issues a scoped Microsoft Graph token. |
| 7 | Bedrock agent | Calls Graph/SharePoint/Teams with the Entra-issued token. Graph sees the user's identity. |
| 8 | Both platforms | Both AgentCore (CloudWatch) and Entra (Sign-in Logs) record the complete auth chain. |

**Complete cross-cloud agent: AWS Bedrock (Claude) + Microsoft Entra Agent ID identity:**

```python
import boto3, requests, json

class CrossCloudAgent:
    """AWS Bedrock agent governed by Microsoft Entra Agent ID."""

    def __init__(self, tenant_id, entra_app_id, workload_identity_arn):
        self.tenant_id = tenant_id
        self.entra_app_id = entra_app_id
        self.workload_arn = workload_identity_arn
        self.agentcore = boto3.client("bedrock-agentcore", region_name="us-east-1")
        self.bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    def get_entra_token(self, user_jwt=None):
        """Get Microsoft Entra token via WIF — no stored secrets."""
        if user_jwt:
            aws_token = self.agentcore.get_workload_access_token_for_jwt(
                workloadIdentityArn=self.workload_arn, jwt=user_jwt
            )["accessToken"]
        else:
            aws_token = self.agentcore.get_workload_access_token(
                workloadIdentityArn=self.workload_arn
            )["accessToken"]

        resp = requests.post(
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
            data={
                "client_id": self.entra_app_id,
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": aws_token,
                "scope": "https://graph.microsoft.com/.default",
                "requested_token_use": "on_behalf_of"
            }
        )
        return resp.json()["access_token"]

    def call_graph(self, endpoint, user_jwt=None):
        """Call Microsoft Graph with federated Entra identity."""
        token = self.get_entra_token(user_jwt)
        return requests.get(
            f"https://graph.microsoft.com/v1.0/{endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        ).json()

    def run(self, user_query, user_jwt=None):
        """Invoke Claude on Bedrock with M365 context."""
        emails = self.call_graph("me/messages?$top=5&$select=subject,from,receivedDateTime", user_jwt)
        files = self.call_graph("me/drive/recent?$top=5&$select=name,lastModifiedDateTime", user_jwt)
        context = {
            "recent_emails": emails.get("value", []),
            "recent_files": files.get("value", [])
        }
        response = self.bedrock.invoke_model(
            modelId="us.anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "system": "You are an enterprise assistant with access to the user's M365 context.",
                "messages": [{"role": "user", "content": f"User M365 context:\n{json.dumps(context, indent=2)}\n\nQuery: {user_query}"}]
            })
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
```

---

## 5. Feature Comparison

| **Feature** | **Microsoft Entra Agent ID** | **AWS AgentCore Identity** |
| --- | --- | --- |
| **GA Date** | May 1, 2026 | October 2025 |
| **Identity Model** | Service Principal (Blueprint + Instance) | Workload Identity (auto or manual) |
| **User Delegation** | Native OBO via Entra grant | OBO Token Exchange (April 2026) |
| **Secret Management** | Keyless/WIF — no stored secrets | Secrets Manager BYO (June 2026, CMK support) |
| **Cross-cloud** | Native AWS Bedrock &amp; n8n WIF | Entra ID, Cognito, Okta integration |
| **Audit/Logging** | Entra Sign-in Logs + Conditional Access | CloudWatch + OTEL (Datadog, LangSmith) |
| **Governance** | Lifecycle Workflows, Entitlement Management | IAM Policies, VPC, Resource Tagging |
| **Auth Protocols** | OAuth 2.0, OIDC, SAML | OAuth 2.0, SigV4, OIDC, API Keys |
| **Agent Lifecycle** | Blueprint-driven + sponsor oversight | Auto by Runtime/Gateway or manual creation |
| **Pricing** | Entra P1/P2 + Agent 365 per-user license | Consumption-based per token operation |
| **OSS Frameworks** | Copilot Studio, via SDK/WIF | CrewAI, LangGraph, LlamaIndex, OpenAI SDK |
| **Zero Trust** | Conditional Access + real-time risk signals | Per-request verification, least-privilege OBO |

---

## 6. Decision Framework

### Choose Microsoft Entra Agent ID when…

- Your agents primarily call Microsoft 365, Azure, Teams, or SharePoint APIs
- Your organisation uses Conditional Access policies and wants agents under the same governance
- You need Blueprint-based identity templates to govern hundreds of agent instances consistently
- Your identity team manages everything in Entra/Active Directory already
- You require fine-grained lifecycle workflows with human sponsors for each agent

### Choose AWS AgentCore Identity when…

- Your agents run on AWS compute (ECS, Lambda, EKS) and primarily access AWS services
- You want consumption-based pricing with no per-seat licensing overhead
- Your agent framework is open-source (LangGraph, CrewAI, LlamaIndex)
- You need multi-IdP support from day one (Cognito, Entra, Okta in parallel)
- You want a bring-your-own-secrets model with CMK and automatic rotation

### Use Both (Cross-Cloud Federation) when…

- Agents live on AWS but need access to Microsoft Graph, SharePoint, or Teams
- You have a Microsoft-first enterprise (Entra, M365) with AWS-native AI workloads
- You want zero stored secrets anywhere — use AgentCore WIF + Entra WIF end-to-end
- Your audit requirements span both AWS CloudTrail/CloudWatch and Microsoft Sentinel
- You need OBO flows: agent acting as the user across both cloud ecosystems

---

## 7. Security Considerations

### Token Scope Creep

Agent tokens must be scoped to minimum required permissions. Both platforms support fine-grained scope definitions, but require explicit configuration. Default to the narrowest scope; expand only when a specific tool requires it.

### Credential Rotation

AWS AgentCore supports automatic secret rotation via Secrets Manager (30-day cycles). Microsoft Entra Agent ID avoids long-lived credentials entirely via WIF — the preferred approach when available, as it removes rotation risk completely.

### Token Lifetime

Agent access tokens typically expire in 1 hour (Entra) to 60 minutes (AgentCore). Do not cache tokens beyond their expiry. Use refresh tokens in the Token Vault (AgentCore) or re-acquire via WIF flow (Entra) for long-running agents.

### Audit &amp; Forensics

Entra logs appear in Microsoft Sentinel and can trigger alerts on anomalous agent behaviour. AgentCore logs ship to CloudWatch and are OTEL-compatible for Datadog, LangSmith, and Langfuse. In cross-cloud setups, maintain a unified SIEM view that correlates events from both platforms.

### Supply Chain Risk (Shadow AI)

Both platforms support shadow AI detection — agents operating outside defined blueprints (Entra) or without registered workload identities (AgentCore) can be detected and blocked. Enforce agent identity registration before any production deployment.

---

## 8. Conclusion &amp; Recommendations

Both Microsoft Entra Agent ID and AWS AgentCore Identity have reached enterprise maturity in 2026. They solve the same core problem — giving AI agents first-class, governed, auditable identities — but with different approaches reflecting each vendor's ecosystem strengths.

Critically, they are designed for interoperability, not competition. Microsoft explicitly lists AWS Bedrock as a supported third-party platform, and AWS lists Microsoft Entra ID as a supported identity provider.

**Recommended enterprise pattern for multi-cloud AI:** Use AgentCore Identity as the AWS-side anchor, federated into Entra Agent ID for Microsoft resource access — achieving zero stored secrets, full audit coverage across both clouds, and user-identity preservation via OBO token exchange.

**Practical starting point:**

- **AWS-native agents:** Start with AgentCore Identity and add Entra WIF federation when Microsoft API access is needed.
- **Microsoft-first organisations:** Use Entra Agent ID Blueprints for governance and add AWS STS federation for Bedrock workloads.

The federation trust between both systems can be established in under 30 minutes using published reference implementations from both Microsoft and Amazon.

## Related

- [Agent Identity for AI Systems — Research 2026](04-agentidentity-research-2026.md) — the broader identity landscape this comparison sits within.
- [EntraID 3LO Volume 1: Standards & Architecture](11-entra-3lo-agent-auth-standards-architecture.md) — deep dive on the Entra side of this comparison.
- [Identity, OBO & Sessions](05-identity-obo-sessions.md) — session and delegation patterns relevant to both platforms.
