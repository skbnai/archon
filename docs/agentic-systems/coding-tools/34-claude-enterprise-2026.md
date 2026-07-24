---
title: Claude Enterprise Deployment 2026
domain: agentic-systems
status: current
doc_type: guide
topic_id: claude-enterprise-2026
date_published: 2026-07-24
last_reviewed: 2026-07-24
supersedes:
  - docs/coding-tools/claude/claude-enterprise-2026.md
related_docs:
  - reliability-engineering
---

# Claude Enterprise Deployment 2026

Reference guide for enterprise architects and platform engineers deploying Claude at scale across cloud platforms, with comprehensive coverage of security, compliance, cost governance, guardrails, explainability, human-in-the-loop patterns, and responsible AI.

---

## 1. Deployment Options Overview

| Platform | Description | Auth | Billing | Best For |
| ---------- | ------------- | ------ | --------- | ---------- |
| **Claude API (Direct)** | Anthropic-hosted, direct access | Anthropic API keys | Anthropic invoices | Startups, developers, prototyping |
| **Claude Platform on AWS** | Anthropic-managed infrastructure on AWS; AWS billing and IAM auth | AWS IAM | AWS bill | Enterprises already on AWS, unified billing |
| **Amazon Bedrock** | AWS-managed service; Claude models alongside other foundation models | AWS IAM | AWS bill | AWS-native workloads, Bedrock Agents, Knowledge Bases |
| **Google Cloud Vertex AI** | GCP-managed; Model Garden access | GCP service accounts, ADC | GCP bill | GCP-native workloads, BigQuery integration, Vertex Pipelines |
| **Azure AI Foundry** | Azure Marketplace; Claude models via Azure cognitive services | Azure AD / Managed Identity | Azure bill | Microsoft 365 shops, Azure compliance frameworks |

:::tip Choosing a platform
    If your data is already in AWS (S3, RDS, Redshift), prefer Bedrock or Claude Platform on AWS for minimal egress and unified IAM. If you need EU data residency with minimal config, Vertex AI EU regions or Azure EU regions are the simplest path. For Microsoft 365 shops needing Conditional Access Policies and Purview integration, Azure AI Foundry is the natural fit.

---

## 2. Claude Platform on AWS

Announced in 2026, Claude Platform on AWS places Anthropic-managed infrastructure within AWS, delivering the full Claude API surface through AWS billing and IAM authentication. This differs from Bedrock: Bedrock is an AWS-managed service with AWS's abstraction layer; Claude Platform on AWS is Anthropic's own infrastructure accessed via AWS identity primitives.

### 2.1 Supported APIs

Claude Platform on AWS exposes the complete Anthropic API:

| API | Description |
| ----- | ------------- |
| Messages API | Core conversational and reasoning API |
| Files API | Upload once, reference by `file_id` across requests |
| Batch API | Async batch processing at 50% discount |
| Managed Agents | Scheduled agent deployments with durable state |
| Agent Skills | Modular skill packages for common agent tasks |
| Code Execution | Sandboxed code running for agent workflows |
| Tool Use | Structured tool calling with JSON schemas |

### 2.2 IAM Authentication

```python
import boto3
import anthropic

# Claude Platform on AWS uses AWS STS for token exchange
def get_claude_platform_client():
    sts = boto3.client("sts")
    # Exchange AWS credentials for a short-lived Claude Platform token
    assumed = sts.assume_role(
        RoleArn="arn:aws:iam::123456789012:role/ClaudePlatformRole",
        RoleSessionName="ClaudeSession"
    )
    creds = assumed["Credentials"]

    client = anthropic.Anthropic(
        # Claude Platform on AWS endpoint
        base_url="https://api.claude-platform.aws.anthropic.com",
        api_key=creds["SessionToken"],  # STS session token
    )
    return client

client = get_claude_platform_client()
response = client.messages.create(
    model="claude-sonnet-4-6-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Analyse this architecture."}]
)
```

### 2.3 Billing Integration

- All Claude Platform on AWS usage appears on your AWS bill under the `anthropic` service namespace
- Standard AWS Cost Explorer tags (`CostCenter`, `Project`, `Team`) flow through
- Consolidated billing across AWS Organization accounts is supported
- AWS Budgets can trigger alerts at configurable thresholds

---

## 3. Amazon Bedrock

### 3.1 Model IDs

Use the following model IDs for 2025-vintage Claude models on Bedrock:

| Model | Single-Region ID | Cross-Region Inference ID |
| ------- | ----------------- | -------------------------- |
| Claude Sonnet 4.6 | `anthropic.claude-sonnet-4-6-20250514-v1:0` | `us.anthropic.claude-sonnet-4-6-20250514-v1:0` |
| Claude Haiku 4.5 | `anthropic.claude-haiku-4-5-20250714-v1:0` | `us.anthropic.claude-haiku-4-5-20250714-v1:0` |
| Claude Opus 4.8 | `anthropic.claude-opus-4-8-20251101-v1:0` | `us.anthropic.claude-opus-4-8-20251101-v1:0` |

:::warning Never use future dates
    Model IDs use the model's actual release date. Do not construct IDs with future dates. If a model ID fails, verify in the Bedrock console under Foundation Models.

### 3.2 Basic Setup

```python
import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

response = bedrock.invoke_model(
    modelId="anthropic.claude-sonnet-4-6-20250514-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [
            {"role": "user", "content": "Analyse this architecture for scalability issues."}
        ]
    })
)
result = json.loads(response["body"].read())
print(result["content"][0]["text"])
```

### 3.3 Anthropic SDK with Bedrock

```python
import anthropic

client = anthropic.AnthropicBedrock(
    aws_region="us-east-1"
    # Uses boto3 credential chain automatically (instance profile, env vars, ~/.aws/)
)

response = client.messages.create(
    model="anthropic.claude-sonnet-4-6-20250514-v1:0",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Explain this code."}]
)
print(response.content[0].text)
```

### 3.4 Cross-Region Inference

Cross-region inference automatically routes requests to the region with available capacity:

```python
# Use cross-region prefix to enable automatic routing
response = bedrock.invoke_model(
    modelId="us.anthropic.claude-sonnet-4-6-20250514-v1:0",  # us. prefix = cross-region
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": "..."}]
    })
)
```

Supported cross-region prefixes: `us.` (routes across US regions), `eu.` (routes across EU regions), `ap.` (routes across APAC regions).

### 3.5 IAM Policies

Minimal IAM policy for Bedrock access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvokeModel",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6-20250514-v1:0",
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-haiku-4-5-20250714-v1:0"
      ]
    },
    {
      "Sid": "CrossRegionInference",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
      "Resource": "arn:aws:bedrock:*::foundation-model/us.anthropic.claude-*"
    }
  ]
}
```

:::note Principle of least privilege
    Scope model ARNs to exactly the models your application uses. Do not use `anthropic.claude-*` wildcards in production IAM policies.

### 3.6 VPC PrivateLink

Keep all API traffic off the public internet:

```hcl
# Terraform: Bedrock VPC Interface Endpoint
resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.us-east-1.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnet_ids
  security_group_ids  = [aws_security_group.bedrock_endpoint.id]
  private_dns_enabled = true

  tags = {
    Name        = "bedrock-runtime-endpoint"
    Environment = var.environment
  }
}

resource "aws_security_group" "bedrock_endpoint" {
  name   = "bedrock-endpoint-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]  # Only internal traffic
  }
}
```

With PrivateLink, configure your application:

```python
# boto3 automatically uses VPC endpoint when private_dns_enabled = true
# No client-side code changes needed — DNS resolves to private IP
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
    # Automatically routes through VPC endpoint
)
```

### 3.7 Guardrails for Amazon Bedrock

Bedrock Guardrails add a content filtering layer independent of the model:

```python
# Create a guardrail (one-time setup via Bedrock console or API)
bedrock_cp = boto3.client("bedrock", region_name="us-east-1")

guardrail = bedrock_cp.create_guardrail(
    name="enterprise-content-filter",
    contentPolicyConfig={
        "filtersConfig": [
            {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "INSULTS", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
        ]
    },
    topicPolicyConfig={
        "topicsConfig": [
            {
                "name": "competitor-discussion",
                "definition": "Discussion of competitor products or services",
                "examples": ["How does our product compare to X?"],
                "type": "DENY"
            }
        ]
    },
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": "EMAIL", "action": "ANONYMIZE"},
            {"type": "PHONE", "action": "ANONYMIZE"},
            {"type": "AWS_ACCESS_KEY", "action": "BLOCK"},
        ]
    },
    wordPolicyConfig={
        "managedWordListsConfig": [{"type": "PROFANITY"}]
    },
    description="Enterprise safety guardrail"
)

GUARDRAIL_ID = guardrail["guardrailId"]
GUARDRAIL_VERSION = "DRAFT"

# Apply guardrail to every model invocation
def invoke_with_guardrail(prompt: str) -> dict:
    response = bedrock.invoke_model(
        modelId="anthropic.claude-sonnet-4-6-20250514-v1:0",
        guardrailIdentifier=GUARDRAIL_ID,
        guardrailVersion=GUARDRAIL_VERSION,
        trace="ENABLED",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        })
    )

    # Check if guardrail intervened
    body = json.loads(response["body"].read())
    if body.get("amazon-bedrock-guardrailAction") == "GUARDRAIL_INTERVENED":
        trace = body.get("amazon-bedrock-trace", {})
        raise GuardrailTriggered(f"Guardrail blocked request: {trace}")

    return body
```

### 3.8 Knowledge Bases Integration

```python
# Create a Knowledge Base retrieval query
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

def retrieve_and_generate(query: str, knowledge_base_id: str) -> str:
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={"text": query},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": knowledge_base_id,
                "modelArn": f"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6-20250514-v1:0",
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {
                        "numberOfResults": 10,
                        "overrideSearchType": "SEMANTIC"
                    }
                }
            }
        }
    )
    return response["output"]["text"]
```

### 3.9 Bedrock Agents vs Claude Agent SDK

| Dimension | Bedrock Agents | Claude Agent SDK |
| ----------- | --------------- | ----------------- |
| Infrastructure | AWS-managed | Your infrastructure |
| Orchestration code | Visual / YAML configuration | Python/TypeScript code |
| Tool integration | Lambda functions, OpenAPI schemas | Any callable Python/TypeScript |
| State management | AWS-managed DynamoDB | Your choice of store |
| Trace / observability | Built-in Bedrock Trace | Custom (OTel, LangSmith) |
| Multi-agent | Bedrock multi-agent collaboration | Full SDK orchestration |
| Best for | Teams wanting managed infra with AWS tooling | Teams needing custom orchestration logic |
| Flexibility | Lower | Higher |

---

## 4. Google Cloud Vertex AI

### 4.1 Model IDs

| Model | Vertex AI Model ID |
| ------- | -------------------- |
| Claude Sonnet 4.6 | `claude-sonnet-4-6@20250514` |
| Claude Haiku 4.5 | `claude-haiku-4-5@20250714` |
| Claude Opus 4.8 | `claude-opus-4-8@20251101` |

### 4.2 Service Account Authentication

```bash
# Create service account for Claude API access
gcloud iam service-accounts create claude-api-sa \
  --display-name="Claude API Service Account"

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding my-gcp-project \
  --member="serviceAccount:claude-api-sa@my-gcp-project.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# For Workload Identity (recommended for GKE)
gcloud iam service-accounts add-iam-policy-binding claude-api-sa@my-gcp-project.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:my-gcp-project.svc.id.goog[my-namespace/my-k8s-sa]"
```

### 4.3 Python SDK Setup

```python
import anthropic

# Application Default Credentials (ADC) — preferred for server environments
client = anthropic.AnthropicVertex(
    project_id="my-gcp-project",
    region="us-east5"
)

response = client.messages.create(
    model="claude-sonnet-4-6@20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Explain this architecture."}]
)
print(response.content[0].text)
```

### 4.4 VPC Service Controls

VPC-SC creates a perimeter that prevents data exfiltration from Vertex AI:

```yaml
# VPC-SC perimeter configuration (via gcloud or Terraform)
access_policy:
  title: "Claude Enterprise Perimeter"
  scopes:
    - projects/my-gcp-project
  restricted_services:
    - aiplatform.googleapis.com
  access_levels:
    - accessPolicies/123456/accessLevels/corporate-network
  ingress_policies:
    - ingress_from:
        identities:
          - serviceAccount:claude-api-sa@my-gcp-project.iam.gserviceaccount.com
      ingress_to:
        operations:
          - service_name: aiplatform.googleapis.com
            method_selectors:
              - method: google.cloud.aiplatform.v1.PredictionService.Predict
```

### 4.5 Customer-Managed Encryption Keys (CMEK)

```python
from google.cloud import aiplatform

aiplatform.init(
    project="my-gcp-project",
    location="us-east5",
    encryption_spec_key_name=(
        "projects/my-project/locations/global/keyRings/my-ring/cryptoKeys/my-key"
    )
)
```

### 4.6 Vertex AI Enterprise Features

| Feature | Description |
| --------- | ------------- |
| Cloud DLP integration | Automatically scan inputs/outputs for PII, PHI, financial data |
| Cloud Audit Logs | All Vertex AI API calls logged to Cloud Logging with principal identity |
| Model Garden | Browse and evaluate Claude alongside Gemini, Llama, and other models |
| Organization Policies | `constraints/aiplatform.restrictAllowedModels` to control which models can be used |
| VPC-SC | Prevent data exfiltration across service perimeters |
| CMEK | Customer controls encryption keys for data at rest |

---

## 5. Azure AI Foundry

### 5.1 Claude via Azure Marketplace

Claude models are available in Azure AI Foundry via the Azure Marketplace. Access requires:

1. An Azure AI Foundry project
2. A Claude model deployment in the project
3. Azure role assignment (`Cognitive Services User` or `Azure AI Developer`)

### 5.2 Managed Identity Authentication

```python
import anthropic
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import httpx

# Managed Identity (recommended for production — no secrets)
credential = ManagedIdentityCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")

client = anthropic.Anthropic(
    base_url=f"https://{AZURE_ENDPOINT}.openai.azure.com/openai/deployments/claude-sonnet-4-6",
    api_key=token.token,
    default_headers={"api-version": "2025-01-01-preview"}
)

response = client.messages.create(
    model="claude-sonnet-4-6-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Summarise this document."}]
)
```

### 5.3 Azure Private Endpoint

```hcl
# Terraform: Azure Private Endpoint for AI Foundry
resource "azurerm_private_endpoint" "claude_ai_foundry" {
  name                = "claude-ai-foundry-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.private.id

  private_service_connection {
    name                           = "claude-ai-foundry-psc"
    private_connection_resource_id = azurerm_ai_services.claude.id
    subresource_names              = ["account"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "ai-foundry-dns"
    private_dns_zone_ids = [azurerm_private_dns_zone.cognitive.id]
  }
}
```

### 5.4 Azure Responsible AI Filters

Azure AI Foundry includes content safety filters independent of the model:

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions

cs_client = ContentSafetyClient(endpoint=CONTENT_SAFETY_ENDPOINT, credential=credential)

def check_content_safety(text: str) -> bool:
    """Returns True if content passes all safety checks."""
    result = cs_client.analyze_text(
        AnalyzeTextOptions(
            text=text,
            categories=["Hate", "SelfHarm", "Sexual", "Violence"],
            output_type="FourSeverityLevels"
        )
    )

    for category in result.categories_analysis:
        if category.severity >= 2:  # Block medium and above
            return False
    return True

# Pre-screen user input before sending to Claude
def safe_invoke(user_message: str) -> str:
    if not check_content_safety(user_message):
        raise ContentPolicyViolation("Input failed content safety check")

    response = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text
```

### 5.5 Azure Enterprise Features

| Feature | Description |
| --------- | ------------- |
| Azure AD SSO | Users authenticate with Microsoft 365 credentials |
| Conditional Access | Enforce MFA, device compliance, location-based access per app |
| Microsoft Purview | Data governance, sensitivity labels, compliance reporting |
| Azure Monitor | Diagnostic logs, metrics, and alerts for all AI Foundry activity |
| Microsoft Defender for Cloud | Threat detection for AI Foundry workloads |
| Data residency | EU data processed in EU Azure regions; UK data in UK regions |

---

## 6. Claude Enterprise Plan

### 6.1 Admin Console Features

The Claude Enterprise admin console (`console.anthropic.com`) provides:

| Feature | Description |
| --------- | ------------- |
| Usage analytics | Request volume, token consumption, cost by model and team |
| Model-level entitlements | Grant or restrict specific models per user group |
| Spend alerts | Configurable alerts at percentage thresholds (50%, 80%, 100%) |
| Per-team cost attribution | Track spend by team, project, or cost centre |
| Productivity trends | Output volume over time for teams and individuals |
| Audit log export | Full request/response logs for SIEM ingestion |

### 6.2 Model-Level Access Controls

```json
{
  "entitlements": {
    "engineering": {
      "models": ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-8"],
      "max_tokens_per_request": 100000,
      "monthly_token_budget": 50000000
    },
    "support": {
      "models": ["claude-haiku-4-5"],
      "max_tokens_per_request": 8192,
      "monthly_token_budget": 5000000
    },
    "executives": {
      "models": ["claude-sonnet-4-6"],
      "max_tokens_per_request": 32768,
      "monthly_token_budget": 10000000
    }
  }
}
```

### 6.3 SSO / SAML Integration

Claude Enterprise supports SAML 2.0 and OIDC for single sign-on:

- **Okta**: Native SAML app available in Okta Integration Network
- **Azure AD**: Enterprise app with SAML federation
- **Google Workspace**: SAML application with group-based provisioning
- **JIT provisioning**: Users provisioned on first login with role from IdP attributes
- **SCIM**: Automated deprovisioning when user is offboarded from IdP

### 6.4 Audit Logs

Audit logs capture every interaction at the message level:

```json
{
  "timestamp": "2026-07-04T10:23:45.123Z",
  "event_type": "message.create",
  "user_id": "user_abc123",
  "team_id": "engineering",
  "model": "claude-sonnet-4-6-20250514",
  "input_tokens": 1247,
  "output_tokens": 823,
  "cost_usd": 0.016,
  "session_id": "sess_xyz789",
  "ip_address": "10.0.1.45",
  "request_id": "req_def456"
}
```

Export audit logs to SIEM:

```bash
# Export via API (Enterprise plan)
curl -H "Authorization: Bearer $ANTHROPIC_ADMIN_KEY" \
  "https://api.anthropic.com/v1/admin/audit-logs?start=2026-07-01&end=2026-07-04&format=jsonl" \
  -o audit-2026-07-01-to-07-04.jsonl
```

---

**This is Part 1 of 3. [Continue with Part 2 →](./parts/34-claude-enterprise-2026-part2.md) for Managed Agents, Security, Compliance, and Cost Governance. [See Part 3 →](./parts/34-claude-enterprise-2026-part3.md) for Guardrails, Explainability, Responsible AI, and Deployment Checklists.**
