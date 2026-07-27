---
title: "AI Gateway Comparison — 10 Tools"
doc_type: guide
domain: platforms
status: current
topic_id: ai-gateway-full-comparison
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/cloud-platforms/ai-gateway/AI_Gateway_Full_Comparison.md]
tags: [ai-gateway, platform-comparison, kong, litellm, aws-bedrock, azure, cloudflare]
covers_version: "N/A"
---

# AI Gateway Comparison — 10 Tools

This enterprise architect's reference evaluates the capabilities, trade-offs, and best practices for ten production AI gateways: Kong AI, LiteLLM Proxy, AWS Bedrock, Azure APIM, Portkey.ai, Cloudflare AI Gateway, Google Apigee, WSO2 Choreo, Traefik, and IBM watsonx. Each section includes a capability matrix, architectural guidance, best practices, anti-patterns, and reference implementations to help teams choose and deploy the right gateway for their workload and cloud strategy.

## Master Capability Comparison Matrix

The matrix below scores each gateway across 10 capability dimensions on a scale of 1–10. Scores reflect the out-of-box capability without significant customisation.

| Tool | Provider Routing | Extensibility | Sem. Cache | Security & Guards | Observability | Ease of Setup | Multi-tenant Isolation | Multi-Cloud | OSS Maturity | FinOps |
|---|---|---|---|---|---|---|---|---|---|---|
| Kong AI | 9/10 | 10/10 | 9/10 | 8/10 | 8/10 | 6/10 | 8/10 | 8/10 | 9/10 | 8/10 |
| LiteLLM Proxy | 10/10 | 6/10 | 8/10 | 6/10 | 7/10 | 9/10 | 6/10 | 9/10 | 8/10 | 9/10 |
| AWS Bedrock | 5/10 | 4/10 | 3/10 | 9/10 | 7/10 | 8/10 | 7/10 | 2/10 | 1/10 | 7/10 |
| Azure APIM | 5/10 | 6/10 | 7/10 | 7/10 | 7/10 | 7/10 | 7/10 | 3/10 | 2/10 | 7/10 |
| Portkey.ai | 9/10 | 6/10 | 7/10 | 6/10 | 9/10 | 9/10 | 6/10 | 8/10 | 6/10 | 8/10 |
| Cloudflare AI | 6/10 | 5/10 | 6/10 | 8/10 | 7/10 | 10/10 | 5/10 | 6/10 | 1/10 | 6/10 |
| Google Apigee | 5/10 | 7/10 | 8/10 | 7/10 | 8/10 | 6/10 | 8/10 | 3/10 | 1/10 | 7/10 |
| WSO2 Choreo | 7/10 | 7/10 | 6/10 | 6/10 | 7/10 | 5/10 | 7/10 | 7/10 | 8/10 | 6/10 |
| Traefik AI | 6/10 | 7/10 | 3/10 | 5/10 | 7/10 | 8/10 | 5/10 | 6/10 | 8/10 | 4/10 |
| IBM watsonx | 4/10 | 5/10 | 4/10 | 9/10 | 8/10 | 3/10 | 8/10 | 4/10 | 2/10 | 6/10 |

*Legend: 8–10 strong · 5–7 moderate · 1–4 weak.*

## 01. Kong AI Gateway

Kong Inc. (2024) · Apache 2 (OSS) / Enterprise · For enterprise & cloud-native platform teams — *the enterprise plugin-powered AI traffic controller.*

Kong AI Gateway extends the battle-tested Kong Gateway with a dedicated AI plugin suite. It sits in front of any LLM provider, enforcing rate limits, semantic caching, PII redaction, and prompt guards through a declarative plugin chain. The plugin ecosystem (Lua, WASM, Go) makes it the most extensible option for platform teams already running Kong for API management, enabling a single pane of glass across REST, GraphQL, gRPC, and AI traffic.

**Core capabilities:** Multi-provider Routing · Semantic Cache · Rate Limiting · Prompt Guard · PII Redaction · Plugin Ecosystem · mTLS · OpenTelemetry · RBAC / Workspaces · Kubernetes CRDs · AI Cost Tracking · Fallback Chains · Streaming SSE · Declarative Config (decK)

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 9/10 |
| Extensibility / Plugins | 10/10 |
| Semantic caching | 9/10 |
| Security & guardrails | 8/10 |
| Observability | 8/10 |
| Ease of setup | 6/10 |
| Multi-tenant isolation | 8/10 |
| Multi-cloud support | 8/10 |
| OSS maturity | 9/10 |
| FinOps | 8/10 |

### Pros

- Best-in-class plugin ecosystem — Lua, WASM, Go plugins for unlimited extensibility
- Native Kubernetes Ingress Controller (KIC) and Gateway Operator (KGO) for cloud-native ops
- Declarative config via decK CLI + GitOps — full IaC lifecycle
- Semantic cache plugin with pgvector/Redis reduces token costs by 40–70%
- Multi-workspace tenancy model for BU-level isolation out of the box
- Strong OSS community + enterprise support with SLA guarantees
- AI-specific plugins: ai-proxy, ai-rate-limiting, ai-semantic-cache, ai-prompt-guard
- Provider abstraction — single route serves OpenAI, Azure, Bedrock, Claude

### Cons

- Steeper learning curve than hosted alternatives — requires Kong expertise
- Enterprise features (RBAC, Vault, advanced analytics) behind paid license
- Plugin development requires Lua or WASM knowledge — not Python-native
- Control plane (Kong Manager / Konnect) adds operational overhead
- Semantic cache vector DB must be provisioned separately (pgvector, Redis Stack)
- No native eval/quality scoring — requires external tooling

### Best Practices

- Deploy Kong Manager on a dedicated control plane node separate from data plane
- Use decK sync in CI/CD to validate and apply config changes — never manual Admin API in prod
- Namespace all plugin configs under Workspaces matching tenant hierarchy
- Enable ai-semantic-cache with similarity threshold 0.85–0.90 to balance hit rate vs freshness
- Use Vault KV secrets engine for all provider API keys — never hardcode in decK files
- Set ai-rate-limiting-advanced with sliding_window strategy and per-consumer JWT sub claims
- Deploy Kong with at least 3 replicas behind an NLB for HA; use PodDisruptionBudgets
- Monitor gateway_ai_llm_usage_tokens metric to drive FinOps chargeback

### Anti-Patterns

- Running Kong in DB-less mode without a backup config store in production — single config loss point
- Installing too many plugins in the global scope — degrades all routes, not just AI routes
- Using API key auth without Vault rotation — keys in plaintext in decK YAML committed to git
- Setting rate limits by IP instead of JWT consumer — bypassed by shared NAT environments
- Ignoring Kong's upstream health checks — circuit breaker won't trigger without active probes
- Using the Community Edition for enterprise multi-tenancy — Workspaces require Enterprise
- Skipping load testing the semantic cache similarity threshold — too low = poor hit rate; too high = stale answers

### Reference Snippet

Kong AI Gateway — full AI route with guard + cache:

```yaml
services:
  - name: openai-service
    url: https://api.openai.com

routes:
  - name: chat-route
    paths: [/ai/v1]
    service: openai-service
    plugins:
      - name: openid-connect        # AuthN
        config: { issuer: https://idp.corp/oidc }
      - name: ai-proxy
        route_type: llm/v1/chat
        model: { provider: openai, name: gpt-4o }
        auth: { header_value: "Bearer {vault://gw/openai-key}" }
      - name: ai-prompt-guard       # Injection shield
        rules: [{ match: regex, pattern: 'ignore (all )?instructions', action: block }]
      - name: ai-semantic-cache
        vectordb: { strategy: redis, threshold: 0.87 }
      - name: ai-rate-limiting-advanced
        limit: [{ minute: 200, day: 20000 }]
        identifier: consumer
```

> **Verdict:** Best choice for platform teams who already operate Kong or need maximum extensibility. The plugin model is unmatched. Requires investment in Kong expertise and enterprise license for full multi-tenancy.

## 02. LiteLLM Proxy

BerriAI (2023) · MIT (OSS) / Enterprise · For dev teams & platform engineering — *the open-source 100+ provider unification layer.*

LiteLLM Proxy is the most popular open-source AI gateway, providing a unified OpenAI-compatible endpoint in front of 100+ LLM providers. Written in Python, it is the natural choice for Python-native ML/AI teams. It ships with built-in semantic caching, budget limits, virtual keys, load balancing, and a management UI. The proxy is lightweight enough to run as a sidecar and powerful enough to serve as a production gateway for mid-scale deployments.

**Core capabilities:** 100+ Provider Support · Virtual API Keys · Budget Limits · Semantic Cache (Redis) · Load Balancing · Fallback Chains · Retry Logic · Spend Tracking · Prometheus Metrics · OpenAI-compatible API · Team Management UI · Callback Hooks · Model Aliases · Async Batch Processing

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 10/10 |
| Extensibility / Plugins | 6/10 |
| Semantic caching | 8/10 |
| Security & guardrails | 6/10 |
| Observability | 7/10 |
| Ease of setup | 9/10 |
| Multi-tenant isolation | 6/10 |
| Multi-cloud support | 9/10 |
| OSS maturity | 8/10 |
| FinOps | 9/10 |

### Pros

- Supports 100+ providers out of the box — largest provider coverage in any gateway
- Python-native — callbacks, custom routers, and hooks written in native Python
- Virtual keys with per-key budget limits, model restrictions, and team assignment
- Built-in spend tracking and cost analytics dashboard without external tooling
- Latency-based routing and lowest-cost-routing strategies built in
- Seamless drop-in replacement — change OPENAI_BASE_URL, zero app code changes
- Active open-source community with weekly releases
- Lightest operational footprint — runs as a single Docker container

### Cons

- Isolation model is logical, not physical — all tenants share the same process
- Plugin extensibility limited to Python callbacks — no declarative plugin chain
- No native Kubernetes CRD / Operator — requires manual Helm chart management
- Prompt injection/guard features are callback-based, not inline pipeline plugins
- Performance ceiling lower than Nginx/Kong-based gateways at very high RPS (>10k/s)
- Multi-region deployment requires external orchestration — no native federation
- Enterprise support is commercial but less mature than Kong's offering

### Best Practices

- Store all provider keys in environment variables or Vault — never in config.yaml
- Use virtual keys per team with explicit model allow-lists and daily_budget_usd limits
- Enable Redis semantic cache with a similarity threshold of 0.85 for best cost vs quality
- Deploy behind a Kubernetes Deployment with 3+ replicas and readiness probes on /health
- Use router_settings.routing_strategy: latency-based-routing for production SLA compliance
- Implement custom callbacks for PII scanning (Presidio integration) before provider calls
- Export Prometheus metrics to Grafana; alert on litellm_requests_metric drop rate > 1%
- Use model_group_alias to abstract provider details from application teams

### Anti-Patterns

- Running LiteLLM as a single replica without Redis — all budget state is in-memory and lost on restart
- Using the master key for application teams — create per-team virtual keys with scoped permissions
- Setting fallback_models without health checking — fallback to a broken provider adds latency, not resilience
- Ignoring max_budget_duration — without TTL, budgets accumulate and never reset
- Deploying without a reverse proxy (Nginx/Traefik) in front — LiteLLM is not hardened for direct internet exposure
- Using success_callbacks for audit logging without async offload — blocks the request path
- Assuming OpenAI-compatible means identical — some providers return subtly different error codes that callbacks must handle

### Reference Snippet

LiteLLM Proxy — config.yaml with fallback + budget + cache:

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_KEY
  - model_name: gpt-4o            # Azure fallback
    litellm_params:
      model: azure/gpt-4o
      api_base: os.environ/AZURE_ENDPOINT
  - model_name: gpt-4o            # Bedrock fallback
    litellm_params:
      model: bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0

router_settings:
  routing_strategy: latency-based-routing
  allowed_fails: 2
  cooldown_time: 30

litellm_settings:
  cache: true
  cache_params: { type: redis, similarity_threshold: 0.85 }
  success_callbacks: [prometheus, langfuse]

general_settings:
  master_key: os.environ/MASTER_KEY
  database_url: os.environ/POSTGRES_URL
```

> **Verdict:** Best choice for Python-native ML/AI teams who need fast deployment and broad provider coverage. Ideal for startups and mid-market. At enterprise scale (multi-region, hard isolation), augment with infrastructure-level controls.

*Part 1 of 4. Continued in [Part 2](parts/05-ai-gateway-full-comparison-part2.md).*
