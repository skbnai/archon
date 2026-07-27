---
title: "AI Gateway Comparison — 10 Tools (Part 2: AWS Bedrock, Azure APIM, Portkey)"
doc_type: guide
domain: platforms
status: current
topic_id: ai-gateway-full-comparison-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [ai-gateway, platform-comparison, kong, litellm, aws-bedrock, azure, cloudflare]
covers_version: "N/A"
---

*Part 2 of 4 of [AI Gateway Comparison — 10 Tools](../05-ai-gateway-full-comparison.md). Continued in [Part 3](05-ai-gateway-full-comparison-part3.md).*

## 03. AWS Bedrock Gateway

Amazon Web Services (2023) · Proprietary (AWS managed) · For AWS-centric enterprises — *native AWS multi-model gateway with Guardrails.*

AWS Bedrock is Amazon's fully managed foundation model service that also functions as an AI gateway when combined with Bedrock Guardrails, IAM policies, VPC endpoints, and AWS API Gateway. It provides access to models from Anthropic, Meta, Mistral, Cohere, Amazon Titan, and Stability AI through a single AWS SDK call. Guardrails add content filtering, PII detection, grounding checks, and topic-based blocking. The integration with AWS IAM, CloudWatch, and PrivateLink makes it the natural fit for organisations deeply invested in the AWS ecosystem.

**Core capabilities:** Multi-model Catalog (Anthropic/Meta/Mistral/Amazon) · Bedrock Guardrails · IAM-based AuthN/AuthZ · VPC PrivateLink · CloudWatch Metrics · CloudTrail Audit · Knowledge Bases (RAG) · Agents for Bedrock · Model Evaluation · Provisioned Throughput · Cross-region Inference · Data Encryption (KMS) · Batch Inference

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 5/10 |
| Extensibility / Plugins | 4/10 |
| Semantic caching | 3/10 |
| Security & guardrails | 9/10 |
| Observability | 7/10 |
| Ease of setup | 8/10 |
| Multi-tenant isolation | 7/10 |
| Multi-cloud support | 2/10 |
| OSS maturity | 1/10 |
| FinOps | 7/10 |

### Pros

- Zero infrastructure to manage — fully serverless, scales to zero
- Native IAM integration — granular model access via IAM policies and SCPs
- Bedrock Guardrails: content filters, PII redaction, grounding checks, topic blocks
- VPC PrivateLink ensures prompts never traverse the public internet
- Provisioned Throughput for guaranteed TPS with no rate-limit surprises
- Knowledge Bases provides managed RAG with automatic embedding + vector store
- Agents for Bedrock orchestrates multi-step tool-use workflows natively
- CloudTrail provides immutable audit logs of every model invocation

### Cons

- Hard AWS lock-in — no cross-cloud portability of guardrails or routing logic
- Model selection limited to Bedrock catalog — no OpenAI GPT-4o, no on-prem models
- No semantic caching — every request hits the model and incurs cost
- Guardrails are coarse-grained compared to Kong's plugin granularity
- No concept of virtual keys or per-team budget enforcement at the gateway layer
- Cross-region inference latency can be unpredictable during failover
- Custom model fine-tuning and BYOM (Bring Your Own Model) workflow is complex
- API surface diverges from OpenAI schema — requires adapter code in applications

### Best Practices

- Use IAM condition keys (bedrock:InvokedModelId) for per-model access control per team
- Enable Bedrock Guardrails on every production inference profile — not just sensitive routes
- Use Provisioned Throughput for latency-critical workloads to avoid throttling at peak load
- Route via VPC PrivateLink + Interface Endpoint — never via public Bedrock endpoint for prod data
- Tag all Bedrock resources with CostCenter and TeamID for AWS Cost Explorer chargeback
- Use Cross-Region Inference profiles for disaster recovery — test failover quarterly
- Store KMS keys in AWS Secrets Manager, not in application config, for model-level encryption
- Enable CloudTrail data events for Bedrock — default trail only captures management events

### Anti-Patterns

- Using AdministratorAccess IAM role for Bedrock calls — violates least privilege
- Relying on Bedrock Guardrails alone for security — it does not cover prompt injection comprehensively
- Not setting on-demand concurrency limits — runaway agents can exhaust account-level TPS quotas
- Mixing multi-tenant data in the same Knowledge Base without namespace isolation — cross-tenant leakage
- Hardcoding model IDs (anthropic.claude-3...) in application code — breaks on model deprecation
- Ignoring Cross-Region inference latency SLAs — failover regions may be 200ms+ slower
- Not using Provisioned Throughput for production — on-demand throttling causes unpredictable P99 spikes

### Reference Snippet

AWS Bedrock — Guardrail creation (AWS CLI):

```bash
aws bedrock create-guardrail \
  --name prod-guardrail \
  --content-policy-config 'filtersConfig=[{type=HATE,inputStrength=HIGH,outputStrength=HIGH}]' \
  --sensitive-information-policy-config \
    'piiEntitiesConfig=[{type=EMAIL,action=ANONYMIZE},{type=SSN,action=BLOCK}]' \
  --topic-policy-config 'topicsConfig=[{name=Finance,definition=Investment advice,action=BLOCK}]'
```

IAM policy — per-team model access:

```json
{
  "Effect": "Allow",
  "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
  "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-*",
  "Condition": { "StringEquals": { "aws:PrincipalTag/Team": "platform-eng" } }
}
```

> **Verdict:** Best choice for AWS-native organisations with compliance requirements where data must stay within AWS. Not suitable as a multi-cloud or multi-provider gateway. Pair with a provider-agnostic proxy for OpenAI/Azure traffic.

## 04. Azure API Management + AI Gateway

Microsoft Azure (2024 AI extensions) · Proprietary (Azure managed) · For Azure / M365 enterprises — *Microsoft's enterprise API platform extended for AI.*

Azure API Management (APIM) gains AI Gateway capabilities through the GenAI Gateway Accelerator and native Azure OpenAI integration. APIM's policy engine (XML-based) can enforce token limits, retry logic, semantic caching (via Azure Cache for Redis), and backend load balancing across multiple Azure OpenAI deployments. The integration with Azure AD, Managed Identity, and Microsoft Entra ID makes it the default choice for Microsoft-centric enterprises running Copilot, M365, and Azure OpenAI workloads.

**Core capabilities:** Azure OpenAI Load Balancing · Token Rate Limiting · Semantic Cache (Redis) · Policy Engine (XML) · Managed Identity AuthN · Azure AD / Entra ID RBAC · Developer Portal · Mock Responses · Retry + Circuit Breaker · Cost Tracking (Azure Monitor) · Private Endpoints · Subscription Keys · Product-based Tenancy · OTel Export

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 5/10 |
| Extensibility / Plugins | 6/10 |
| Semantic caching | 7/10 |
| Security & guardrails | 7/10 |
| Observability | 7/10 |
| Ease of setup | 7/10 |
| Multi-tenant isolation | 7/10 |
| Multi-cloud support | 3/10 |
| OSS maturity | 2/10 |
| FinOps | 7/10 |

### Pros

- Native Azure OpenAI integration with deployment-level load balancing and PTU management
- Managed Identity eliminates credential management — no API keys in code
- Developer Portal provides self-service API discovery and subscription management
- XML policy engine is powerful and well-documented for common gateway patterns
- Product-based subscriptions map naturally to tenant/team quota management
- Azure Monitor + App Insights provide integrated observability without extra tooling
- Private Endpoint support keeps all traffic within Azure backbone
- GenAI Gateway accelerator provides reference implementation for token tracking + retry

### Cons

- XML policy language is verbose and difficult to test — no unit test framework for policies
- Semantic cache is add-on requiring Azure Cache for Redis — not built in
- Multi-cloud routing to non-Azure providers is possible but cumbersome
- Performance overhead of APIM policy engine compared to Nginx-native gateways
- Enterprise tier required for VNet injection and private endpoints (expensive)
- No native prompt injection detection — requires Azure AI Content Safety as separate service
- APIM v2 (2024) improves performance but the migration path from v1 is disruptive
- Lock-in to Azure policy engine — migration to another gateway requires full rewrite

### Best Practices

- Use Managed Identity for Azure OpenAI auth — never use api-key header in production
- Implement token rate limiting policy using the estimate-token-count + rate-limit-by-key built-in
- Load balance across multiple Azure OpenAI deployments in different regions for PTU spillover
- Use Named Values for all configuration parameters — never hardcode in policy XML
- Enable Application Insights correlation header injection for distributed traces across Azure services
- Create APIM Products per tenant/team — each product maps to a subscription with quota
- Deploy APIM in internal mode within a VNet for zero-public-exposure architecture
- Use the GenAI Gateway accelerator Bicep templates as baseline — do not start from scratch

### Anti-Patterns

- Writing complex business logic in APIM policy XML — use Azure Functions backends for logic > 20 lines
- Using Consumption tier for production AI workloads — no VNet support, cold starts on first request
- Hardcoding Azure OpenAI endpoint URLs in policy — use Named Values + Key Vault references
- Sharing one APIM subscription key across all teams — zero granularity for cost attribution
- Relying on APIM built-in cache for AI responses without Redis — limited to 5min TTL and 8KB response
- Not setting backend timeout policies — long LLM responses exceed default 30s gateway timeout
- Deploying without API revision management — breaking changes to AI routes cause immediate consumer impact

### Reference Snippet

Azure APIM — token rate limiting + multi-backend load balancing policy:

```xml
<policies>
  <inbound>
    <authentication-managed-identity resource="https://cognitiveservices.azure.com"/>
    <!-- Token estimation & rate limiting -->
    <azure-openai-token-limit
        counter-key="@(context.Subscription.Id)"
        tokens-per-minute="50000"
        estimate-prompt-tokens="true"
        remaining-tokens-header-name="x-ratelimit-remaining-tokens"/>
    <!-- Semantic cache lookup -->
    <azure-openai-semantic-cache-lookup
        score-threshold="0.85"
        embeddings-backend-id="ada-embedding-backend"/>
    <!-- Load balance across 2 AOAI deployments -->
    <set-backend-service backend-id="@(
        context.Request.Headers["x-priority"] == "high"
            ? "aoai-swedencentral-ptu"
            : "aoai-eastus-paygo")"/>
  </inbound>
  <outbound>
    <azure-openai-semantic-cache-store duration="3600"/>
  </outbound>
</policies>
```

> **Verdict:** Best choice for Azure-native enterprises standardised on Azure OpenAI and Microsoft identity. The Managed Identity + Entra ID integration is unmatched in the Microsoft ecosystem. Not recommended for multi-cloud or OpenAI-direct workloads.

## 05. Portkey.ai

Portkey (2023) · SaaS / OSS (portkey-gateway on GitHub) · For dev teams & scale-ups — *developer-first AI gateway with prompt versioning.*

Portkey is a developer-first AI gateway and observability platform. Its OSS core (portkey-gateway) provides multi-provider routing, fallbacks, retries, and caching. The SaaS platform adds prompt management, version control, A/B testing, analytics, and feedback loops. Portkey's prompt vault enables versioned, templated prompts managed centrally — a capability absent from infrastructure-focused gateways. It is the leading choice for product teams who treat prompts as first-class engineering artifacts.

**Core capabilities:** Multi-provider Routing · Provider Fallback · Semantic Cache · Retry Logic · Prompt Vault · Prompt Versioning & A/B Test · Request Tracing · Cost Analytics · Virtual Keys · Guardrails (SaaS) · Feedback Loops · SDKs (Python/JS/Go) · Metadata Tagging · Webhook Integrations

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 9/10 |
| Extensibility / Plugins | 6/10 |
| Semantic caching | 7/10 |
| Security & guardrails | 6/10 |
| Observability | 9/10 |
| Ease of setup | 9/10 |
| Multi-tenant isolation | 6/10 |
| Multi-cloud support | 8/10 |
| OSS maturity | 6/10 |
| FinOps | 8/10 |

### Pros

- Prompt Vault with versioning, A/B testing, and rollback — unique among gateways
- Fastest time-to-value — SDK drop-in, production in hours not days
- Best-in-class request tracing with per-request cost breakdown and latency waterfall
- Virtual keys with per-key model allow-list, budget, and metadata tagging
- Feedback loop API allows apps to mark responses as helpful/harmful — feeds analytics
- OSS portkey-gateway can be self-hosted for data-residency requirements
- Comprehensive SDK for Python, JavaScript, and Go with OpenAI-compatible interface
- Guardrails on SaaS tier with PII detection and content moderation

### Cons

- SaaS-first — self-hosted OSS lacks the full analytics and prompt management features
- Multi-tenant isolation is virtual-key-scoped, not process/namespace isolated
- No native Kubernetes Operator — deployment requires manual Helm/Docker management
- Guardrails are less configurable than Kong plugins or AWS Bedrock Guardrails
- Vendor dependency for prompt vault — migrating prompts out of Portkey requires export tooling
- Limited network-level security controls compared to infrastructure gateways
- Enterprise SLAs and support less established than Kong or AWS offerings
- Concurrent request limits on lower SaaS tiers can be hit by high-volume teams

### Best Practices

- Store all production prompts in Portkey Prompt Vault — never hardcode prompts in application code
- Use A/B testing for every significant prompt change before full rollout
- Tag every request with metadata (user_id, feature_id, session_id) for granular analytics
- Use virtual keys per microservice — rotate keys without changing application config
- Enable semantic cache with score_threshold=0.85 and monitor cache_hit_rate in dashboard
- Set up Portkey webhooks to fire on guardrail triggers — integrate with PagerDuty or Slack
- Self-host portkey-gateway on Kubernetes for HIPAA/GDPR workloads — disable SaaS telemetry
- Use Portkey feedback API to collect thumbs-up/down signals — feed into prompt optimisation loop

### Anti-Patterns

- Storing prompts in application code alongside Portkey SDK — defeats the entire prompt management value prop
- Using a single virtual key for all teams — lose granular cost attribution and cannot revoke per team
- Assuming SaaS Portkey is HIPAA-compliant by default — check BAA availability and data processing agreement
- Not versioning prompts before A/B tests — no rollback path when variant performs worse
- Relying on Portkey caching alone without TTL tuning — stale cached responses in dynamic-data contexts
- Using Portkey for security-critical guardrails without layering infrastructure controls — single point of bypass

### Reference Snippet

Portkey — multi-provider config with fallback + prompt vault:

```python
from portkey_ai import Portkey

portkey = Portkey(
    api_key='pk-virtual-key-team-a',
    config={
        'strategy': { 'mode': 'fallback' },
        'targets': [
            { 'virtual_key': 'openai-prod',    'weight': 1 },
            { 'virtual_key': 'azure-oai',      'weight': 1 },  # fallback
            { 'virtual_key': 'anthropic-prod', 'weight': 1 },  # fallback
        ],
        'cache': { 'mode': 'semantic', 'max_age': 3600 },
        'retry': { 'attempts': 3, 'on_status_codes': [429, 503] },
    }
)

# Use versioned prompt from Vault
resp = portkey.prompts.completions.create(
    prompt_id='prod-summariser-v3',
    variables={ 'document': doc_text },
)
```

> **Verdict:** Best choice for product teams who treat prompts as first-class engineering artifacts. The prompt vault and A/B testing are unique. For security-critical or multi-tenant enterprise deployments, layer with infrastructure-level controls.
