---
title: "AI Gateway: Multi-Tenant, Multi-Cloud, Data Ownership (Part 2: Cost Attribution, Governance, Reference Patterns)"
doc_type: guide
domain: platforms
status: current
topic_id: ai-gateway-multitenant-multicloud-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [ai-gateway, multi-tenant, multi-cloud, data-sovereignty, finops]
covers_version: "N/A"
---

*Part 2 of 2 of [AI Gateway: Multi-Tenant, Multi-Cloud, Data Ownership](../06-ai-gateway-multitenant-multicloud.md).*

## Cost Attribution & FinOps at Scale

### F.1 Chargeback Models

At multi-tenant scale, cost attribution must be granular enough to drive engineering behaviour (prompt optimisation, cache leverage) and support accurate financial chargeback to business units or external customers:

#### Token-based Chargeback

Gateway emits per-request telemetry: prompt_tokens, completion_tokens, model, provider, tenant_id, team_id, feature_id. FinOps pipeline (OpenCost + custom Prometheus rules) aggregates cost = tokens × model_rate_per_token. Grafana dashboards show cost by tenant / team / model / feature with drill-down.

###### I **`Formula`**

```
cost_formula: (prompt_tokens * input_rate) + (completion_tokens * output_rate)
```

#### Request-based Chargeback

For tenants on flat-rate contracts, cost is allocated per request regardless of token count. Gateway tags each request with a request_unit (RU) weight by model tier. GPT-4o = 10 RU, GPT-4o-mini = 1 RU, Claude Haiku = 1.5 RU. Monthly RU consumption drives invoice generation.

###### I **`Formula`**

```
cost_formula: requests * model_request_unit_weight
```

#### Cache Savings Credit

Tenants who generate cache hits effectively subsidise their peers. FinOps model credits the cache-hitting tenant: if a cache hit returns a $0.05 completion at zero provider cost, the tenant is charged a cache_fee ($0.001) rather than full provider cost. Cache hit rate is a first-class metric in tenant cost dashboards.

###### I **`Formula`**

```
charge: min(provider_cost, cache_fee) # cache_fee << provider_cost
```

### F.2 Budget Guardrails per Tenant

I **`Budget exhaustion policy — Kong plugin config (snippet)`**

```
plugins:
- name: ai-quota-guardian
config:
tenant_id: '{{ jwt.tenant_id }}'
budgets:
- window: day
limit_usd: 500.00
```

```
on_exceed: throttle # 429 with Retry-After
warn_at_pct: 80 # alert at $400
- window: month
limit_usd: 10000.00
on_exceed: queue # queue in Redis, process when budget resets
escalate_to: finops@corp.com
model_overrides:
gpt-4o:
on_exceed: downgrade_to # auto-downgrade to gpt-4o-mini
downgrade_model: gpt-4o-mini
```

## Governance at Scale

### G.1 Policy Federation

At multi-tenant scale, a monolithic policy file is unmanageable. The gateway adopts a federated policy architecture using OPA's bundle mechanism: global base policies are authored by the Platform team; tenant-specific overrides are authored by Tenant Admins within a constrained sandbox, preventing privilege escalation.

I **`OPA Bundle hierarchy (snippet)`** <mark>`# Bundle server serves layered bundles: # /bundles/global/base.tar.gz — platform-authored, enforced everywhere # /bundles/tenant/{id}/policy.tar.gz — tenant-authored, sandboxed scope # Global base policy (enforced, cannot be overridden): package ai.gateway.global deny if { input.model in BANNED_MODELS_GLOBAL } # e.g. ['dall-e-2'] deny if { input.prompt_injection_score > 0.9 } # Tenant override (tenant can restrict further, not expand): package ai.gateway.tenant allow_model if { not ai.gateway.global.deny # global deny takes precedence input.model in data.tenant_allowed_models[input.tenant_id] }`</mark>

### G.2 Audit at Multi-Tenant Scale

Generating, storing, and querying audit logs for thousands of tenants at millions of requests per day requires a purpose-built audit architecture:

- Kafka topic-per-tenant for real-time audit event streaming; compacted topics for latest-state queries

- S3 with tenant-prefixed partition keys; S3 Object Lock (WORM) for tamper-proof retention

- Athena/BigQuery partitioned queries allow tenant-scoped audit export without cross-tenant data access

- Audit log schema is immutable once deployed; schema evolution only via additive fields (never delete/rename)

- Tenant self-service audit portal: tenants query their own audit log via scoped API credentials — no platform team involvement required

- Cross-tenant audit aggregation (for platform-level security analytics) uses separate anonymised data pipeline with PII removed

### G.3 Compliance Matrix by Cloud & Region

|**Regulation**|**Scope**|**AWS (us-east)**|**Azure (eu-west)**|**GCP (asia-se)**|**On-prem**|
|---|---|---|---|---|---|
|GDPR|EU persons' data|IDisallowed|IAllowed|IDisallowed|IAllowed|

|**Regulation**|**Scope**|**AWS (us-east)**|**Azure (eu-west)**|**GCP (asia-se)**|**On-prem**|
|---|---|---|---|---|---|
|HIPAA|US health data|IBAA signed|IBAA signed|IBAA signed|IAllowed|
|SOC 2 Type II|Service trust|ICovered|ICovered|ICovered|IISelf-cert|
|DPDP (India)|IN persons' data|IDisallowed|IDisallowed|IIMumbai PoP|IPreferred|
|FedRAMP High|US Gov data|IGovCloud|IGov Cloud|IDisallowed|ISILO only|
|EU AI Act|High-risk AI|IIEU mirror|INative EU|I|IFull ctrl|
|PCI DSS|Cardholder data|I+ no log|I+ no log|I+ no log|I+ no log|

##### CHAPTER H

## Reference Patterns & Snippets

### H.1 Multi-Tenant Gateway — Decision Checklist

|**Tenancy Model**|Silo / Bridge / Pool decided per tenant tier based on regulatory classification|
|---|---|
|**Identity**|Tenant_id sourced from verified JWT claim only — never HTTP header|
|**Cache**|Vector cache partitioned per tenant_id as primary key — cross-tenant lookups impossible|
|**Quota**|Redis keys prefixed gw:{tenant_id}: — ACL-enforced keyspace isolation|
|**Residency**|OPA policy enforces provider allow-list per tenant data_residency attribute|
|**Audit Logs**|Separate Kafka topic or S3 prefix per tenant — no shared stream|
|**Data Deletion**|Automated erasure pipeline with 72h SLA and signed deletion certificate|
|**Cost**|Per-request token telemetry→FinOps pipeline→chargeback dashboard|
|**Policy**|OPA bundle federation: global base (overrides all) + tenant sandbox (additive only)|
|**Scaling**|Stateless data plane pods + external Redis + vector cache→HPA on token throughput|
|**Multi-cloud**|Same-cloud-preferred routing + cross-cloud failover + Provider Abstraction Layer|
|**Model Pinning**|Per-tenant model version locked in control plane — upgrade via tenant-scoped canary|

### H.2 Capacity Sizing Reference

|**Scale Tier**|**Tenants**|**Peak RPS**|**Gateway Pods**|**Redis**|**Vector Cache**|**Audit**<br>**Storage**|
|---|---|---|---|---|---|---|
|Small|1–50|500|3 pods (2 CPU)|Single node 8GB|pgvector 1 node|100GB/mon<br>th S3|
|Medium|50–500|5,000|10 pods (4 CPU)|Cluster 3-shard|pgvector 3 node|1TB/month<br>S3|
|Large|500–5k|50,000|30 pods (8 CPU)|Cluster 6-shard|Qdrant 3-node|10TB/mont<br>h S3|
|Hyperscale|5k–50k|500,000|Cell arch (3 cells 50<br>pods each)|Redis Enterprise|Qdrant 9-node<br>cluster|100TB/mon<br>th + Glacier|

### H.3 Data Ownership RACI

|**Activity**|**Platform Team**|**Tenant Admin**|**Data Owner**|**DPO / Legal**|
|---|---|---|---|---|
|Define residency policy|Consult|Inform|Accountable|Responsible|

|**Activity**|**Platform Team**|**Tenant Admin**|**Data Owner**|**DPO / Legal**|
|---|---|---|---|---|
|Configure tenant residency|Responsible|Accountable|Inform|Consult|
|Enable content logging|Implement|Request|Accountable|Approve|
|Trigger data erasure|Execute|Accountable|Initiate|Audit|
|Audit log access (own data)|Provide access|Responsible|Review|Oversee|
|Cross-tenant security audit|Responsible|Informed|Informed|Accountable|
|Model version upgrade|Responsible|Approve/Veto|Inform|Consult|
|Budget limit configuration|Implement|Accountable|Inform|Consult|

*This addendum complements the Enterprise AI Gateway primary document. Multi-tenancy and multi-cloud topology choices are architecture decisions with long-term cost and compliance implications — review with your Data Protection Officer, Cloud Architect, and FinOps lead before committing to a tenancy model.*
