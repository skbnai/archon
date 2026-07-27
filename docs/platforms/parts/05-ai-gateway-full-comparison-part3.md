---
title: "AI Gateway Comparison — 10 Tools (Part 3: Cloudflare, Apigee, WSO2)"
doc_type: guide
domain: platforms
status: current
topic_id: ai-gateway-full-comparison-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [ai-gateway, platform-comparison, kong, litellm, aws-bedrock, azure, cloudflare]
covers_version: "N/A"
---

*Part 3 of 4 of [AI Gateway Comparison — 10 Tools](../05-ai-gateway-full-comparison.md). Continued in [Part 4](05-ai-gateway-full-comparison-part4.md).*

## 06. Cloudflare AI Gateway

Cloudflare (2024) · SaaS (Cloudflare managed) · For web-first / global SaaS teams — *edge-native AI gateway with global PoPs and WAF.*

Cloudflare AI Gateway runs at the edge of Cloudflare's global network (300+ PoPs), providing the lowest-latency first-hop for AI requests from globally distributed users. It combines AI-specific features (request logging, caching, rate limiting) with Cloudflare's existing WAF, DDoS protection, and Zero Trust (WARP/Access) capabilities. The zero-infrastructure model (workers-based, no servers to manage) makes it uniquely easy to deploy for teams already running on Cloudflare.

**Core capabilities:** Global Edge Cache · Rate Limiting · Request Logging · WAF Integration · DDoS Protection · Zero Trust (Access) · Workers AI (edge inference) · Provider Routing · Cost Analytics · Real-time Dashboard · Caching TTL Control · Retry Logic · Custom Workers Middleware · AI Binding (Workers AI)

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 6/10 |
| Extensibility / Plugins | 5/10 |
| Semantic caching | 6/10 |
| Security & guardrails | 8/10 |
| Observability | 7/10 |
| Ease of setup | 10/10 |
| Multi-tenant isolation | 5/10 |
| Multi-cloud support | 6/10 |
| OSS maturity | 1/10 |
| FinOps | 6/10 |

### Pros

- Fastest setup of any gateway — operational in minutes via Cloudflare dashboard
- Global edge network eliminates origin latency for geographically distributed users
- Built-in WAF + DDoS protection on every AI request without additional configuration
- Workers AI provides on-device inference at the edge for low-latency, offline-capable apps
- Zero Trust integration gates AI access to authenticated corporate users (Cloudflare Access)
- Real-time request dashboard with latency, cost, and error metrics built in
- Caching automatically reduces costs for repeated requests — content-addressed

### Cons

- Semantic similarity caching is basic compared to vector-DB-backed solutions
- Multi-tenant isolation is limited — no workspace or namespace concept
- Extensibility requires Cloudflare Workers (JavaScript/WASM) — Lua/Python not supported
- Full prompt/response content logging raises GDPR concerns for EU data
- Vendor lock-in — all config lives in Cloudflare dashboard, no GitOps export
- No native OPA policy integration or structured RBAC beyond Access rules
- Provider support limited compared to LiteLLM (no on-prem models without Workers proxy)
- Pricing per request can become expensive at very high volume vs self-hosted alternatives

### Best Practices

- Route only public-facing AI endpoints through Cloudflare AI Gateway — keep internal model traffic on private network
- Enable Cloudflare Access in front of AI Gateway for authenticated corporate AI tools
- Set cache TTL per endpoint based on content freshness requirements — never use default for dynamic data
- Use Workers middleware to inject tenant ID from Access JWT into gateway logs for attribution
- Enable rate limiting per Cloudflare Access user identity, not per IP — handles mobile/CGNAT
- Monitor Cloudflare Analytics for cache hit ratio — target > 30% for cost efficiency
- Use Cloudflare AI Gateway with Workers AI for edge inference to reduce round-trip to cloud providers

### Anti-Patterns

- Sending PHI/PII through Cloudflare AI Gateway SaaS logging without a signed BAA — HIPAA violation
- Assuming WAF rules cover prompt injection — they do not without custom WAF rules for LLM attack patterns
- Using Cloudflare AI Gateway as the only gateway layer for complex enterprise routing — it lacks RBAC depth
- Not disabling content logging for sensitive endpoints — all prompts/completions are stored in Cloudflare
- Treating Cloudflare cache as a semantic cache — it is exact-match content hash, not similarity-based
- Over-relying on Cloudflare for resilience — a Cloudflare-wide incident affects all AI endpoints simultaneously

### Reference Snippet

Cloudflare AI Gateway — Workers middleware with tenant tagging:

```js
// Cloudflare Worker wrapping AI Gateway
export default {
  async fetch(request, env) {
    // Extract tenant from Cloudflare Access JWT
    const identity = await env.ACCESS.getIdentity(request)
    const tenantId = identity?.custom?.tenant_id ?? 'unknown'

    // Forward to Cloudflare AI Gateway with metadata
    const gwUrl = 'https://gateway.ai.cloudflare.com/v1/{account}/{gateway}'
    const response = await fetch(`${gwUrl}/openai/chat/completions`, {
      method: 'POST',
      headers: {
        ...request.headers,
        'cf-aig-metadata': JSON.stringify({ tenant: tenantId }),
        'Authorization': `Bearer ${env.OPENAI_KEY}`,
      },
      body: request.body,
    })
    return response
  }
}
```

> **Verdict:** Best choice for teams already on Cloudflare who need rapid deployment and global edge presence. Not suitable as the sole enterprise AI gateway — lacks RBAC depth and multi-tenant isolation. Excellent as a front-edge layer composited with a deeper gateway.

## 07. Google Apigee AI Gateway

Google Cloud / Apigee (2024) · Proprietary (GCP managed) · For GCP enterprises — *enterprise API management extended for Vertex AI and Gemini.*

Apigee AI Gateway extends Google's enterprise API management platform with AI-specific capabilities: Vertex AI model routing, Gemini integration, token-aware rate limiting, semantic caching via Vertex AI Embeddings, and AI safety via Vertex AI content filtering. Apigee's proven policy engine (XML/JavaScript), developer portal, and analytics platform bring enterprise API governance to AI traffic. The deep GCP integration — Vertex AI, Gemini, Cloud Armor, Duet AI — makes it the natural fit for GCP-first organisations.

**Core capabilities:** Vertex AI Model Routing · Gemini Native Integration · Token Rate Limiting · Semantic Cache (Vertex Embeddings) · Content Safety (Vertex AI) · Cloud Armor WAF · Identity Platform AuthN · API Products & Monetisation · Developer Portal · Analytics (Advanced API Ops) · Shared Flow Reuse · Private Cloud (Hybrid) · Cloud Trace Integration · gRPC Support

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 5/10 |
| Extensibility / Plugins | 7/10 |
| Semantic caching | 8/10 |
| Security & guardrails | 7/10 |
| Observability | 8/10 |
| Ease of setup | 6/10 |
| Multi-tenant isolation | 8/10 |
| Multi-cloud support | 3/10 |
| OSS maturity | 1/10 |
| FinOps | 7/10 |

### Pros

- Native Vertex AI and Gemini integration — zero adapter code for GCP model catalog
- Shared Flows allow reusable AI policy bundles (auth, rate limit, cache) across all APIs
- Developer Portal provides self-service AI model access with subscription and quota management
- API Products and monetisation enable external AI product revenue with metered billing
- Advanced API Operations provides ML-based anomaly detection on API traffic
- Hybrid deployment (Apigee hybrid) allows on-prem data plane with GCP control plane
- Cloud Armor integration provides DDoS and WAF protection without additional config

### Cons

- Steep learning curve — Apigee policy XML + Shared Flows require dedicated expertise
- Expensive — Apigee X pricing is among the highest in the API management market
- Non-GCP provider routing (OpenAI, Anthropic direct) requires custom JavaScript policy
- Semantic cache depends on Vertex Embeddings — additional cost per embedding call
- No native prompt injection detection — requires Vertex AI Safety Attributes parsing in policy
- Migration from Apigee Edge (legacy) to Apigee X is a major re-implementation project
- Community support is limited; documentation quality varies across features

### Best Practices

- Use Shared Flows for all cross-cutting AI concerns — auth, token limit, cache, safety
- Model Vertex AI backends as Apigee TargetServers — decouple endpoint URLs from policy
- Use API Products to gate model access per team/product — each product maps to a Gemini model tier
- Enable Advanced API Ops anomaly detection to catch AI-specific traffic anomalies
- Apply Cloud Armor security policy at load balancer level before Apigee — first line of defence
- Use Apigee hybrid data plane in EU/regulated regions with GCP control plane for data residency
- Instrument all AI proxy flows with custom analytics variables (token counts, model, cost) for chargeback

### Anti-Patterns

- Writing AI routing logic directly in proxy flows instead of Shared Flows — creates policy duplication across hundreds of proxies
- Using Apigee Eval (free tier) for production AI workloads — no SLA, rate limited, not suitable for prod
- Not setting target timeout extensions for LLM streaming — default 55s Apigee timeout drops long completions
- Hardcoding Vertex AI project/location in policy — use environment-specific KVM (Key Value Map) instead
- Sharing one API Product across all consumers — no granular quota attribution
- Ignoring Apigee's quota sync latency (~30s) — brief over-quota requests possible in distributed deployments

### Reference Snippet

Apigee AI Gateway — Vertex AI proxy with token rate limit + cache:

```xml
<!-- Apigee proxy flow — AI inbound policies -->
<Flow name="AI-Chat-Flow">
  <Request>
    <!-- Auth via Google Identity Platform -->
    <Step><Name>VerifyIDToken</Name></Step>
    <!-- Token rate limiting from KVM -->
    <Step><Name>TokenRateLimitPolicy</Name></Step>
    <!-- Semantic cache lookup -->
    <Step><Name>SemanticCacheLookup</Name></Step>
    <!-- Route to Vertex AI Gemini -->
    <Step><Name>SetVertexAITarget</Name></Step>
  </Request>
  <Response>
    <!-- Store response in semantic cache -->
    <Step><Name>SemanticCacheStore</Name></Step>
    <!-- Extract token counts for analytics -->
    <Step><Name>ExtractTokenUsage</Name></Step>
  </Response>
</Flow>
```

> **Verdict:** Best choice for GCP-first enterprises with existing Apigee investment and Vertex AI/Gemini workloads. The Shared Flows and Developer Portal are powerful for large API programs. High cost and GCP lock-in make it unsuitable as a multi-cloud solution.

## 08. WSO2 Choreo / API Manager

WSO2 (2024 AI extensions) · Apache 2 (OSS) / Enterprise · For OSS-first enterprises — *open-source enterprise API gateway with AI extensions.*

WSO2 API Manager and its cloud-native evolution (Choreo) extend the mature open-source API management platform with AI-specific capabilities: LLM rate limiting, semantic caching, AI traffic analytics, and integration with OpenAI, Azure OpenAI, and Anthropic. WSO2's strength is its fully open-source, vendor-neutral positioning — no proprietary lock-in. Choreo adds a developer platform layer with built-in CI/CD, observability, and a component marketplace. Ideal for regulated industries that require source-code-visible infrastructure.

**Core capabilities:** Multi-provider LLM Routing · Token Rate Limiting · AI Traffic Analytics · Semantic Cache · AI Subscription Management · Ballerina Integration · GraphQL AI APIs · Developer Portal · API Monetisation · Open-source Core · On-prem Deployment · Kubernetes Microgateway · Policy-as-Code · OIDC / OAuth2

### Capability Scores

| Dimension | Score |
|---|---|
| Multi-provider routing | 7/10 |
| Extensibility / Plugins | 7/10 |
| Semantic caching | 6/10 |
| Security & guardrails | 6/10 |
| Observability | 7/10 |
| Ease of setup | 5/10 |
| Multi-tenant isolation | 7/10 |
| Multi-cloud support | 7/10 |
| OSS maturity | 8/10 |
| FinOps | 6/10 |

### Pros

- Fully open-source under Apache 2 — source-auditable for regulated industries
- No vendor lock-in — deploy on any cloud, on-prem, or hybrid
- Mature API management platform with 10+ years of production deployments
- Kubernetes-native microgateway (Choreo Connect) for lightweight sidecar deployments
- Ballerina language integrations provide type-safe AI service compositions
- Built-in API marketplace and developer portal for internal AI product catalogue
- Strong community in banking, healthcare, and government sectors
- Policy-as-code approach aligns with enterprise governance frameworks

### Cons

- AI-specific features are newer and less mature than Kong or LiteLLM equivalents
- Complex installation — WSO2 API Manager has significant operational overhead
- Smaller AI/ML community compared to LiteLLM or Portkey
- Semantic cache implementation requires additional configuration versus out-of-box solutions
- Limited prompt guard / injection detection — requires custom mediators
- Documentation for AI features lags behind product releases
- Choreo SaaS is regionally limited — self-hosted is the only option for all-region coverage

### Best Practices

- Use Choreo Connect (microgateway) for AI traffic — lighter weight than full API Manager for LLM routes
- Define AI APIs as separate API Products in WSO2 Developer Portal with distinct subscription tiers
- Implement token counting in custom mediation sequences before enforcing rate limits
- Use WSO2 Key Manager with external identity providers (Keycloak, Azure AD) for federated authN
- Enable API Analytics for AI traffic — monitor latency, error rates, and consumer usage trends
- Run WSO2 API Manager on Kubernetes with Operator — enables GitOps-managed API lifecycle
- Use Ballerina AI library for type-safe multi-provider orchestration in integration flows

### Anti-Patterns

- Deploying full WSO2 API Manager for a simple LLM proxy — use Choreo Connect microgateway instead
- Using WSO2's default in-memory cache for AI responses — switch to Redis for production semantic cache
- Not separating the API Manager control plane from Choreo Connect data plane — single failure domain
- Treating WSO2 subscriptions as security boundaries alone — enforce network policies separately
- Using XML-based synapse mediators for new AI integrations — prefer Ballerina or REST connector approach

### Reference Snippet

WSO2 Choreo Connect — AI API definition with token rate limit:

```yaml
openapi: '3.0.0'
info:
  title: AI Chat API
x-wso2-throttling-tier: AIGoldTier
x-wso2-cors:
  corsConfigurationEnabled: true
paths:
  /chat/completions:
    post:
      x-auth-type: Application
      x-throttling-tier: AITokenLimit_100K_PerMin
      x-wso2-backend:
        url: https://api.openai.com/v1/chat/completions
        type: HTTP
      security:
        - apiKey: []
```

> **Verdict:** Best choice for regulated industries (banking, healthcare, government) requiring fully open-source, source-auditable AI gateway infrastructure. Expect higher operational effort than managed alternatives. Not yet AI-feature-complete compared to Kong or LiteLLM.
