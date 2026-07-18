---
title: "AI Service Catalog: Tiers, Governance & Developer Portal"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-10-service-catalog-part3
maturity: practitioner
personas: [platform-lead, architect, developer, governance-officer]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes: []
tags: ["service-catalog", "governance", "developer-experience", "self-service", "tiers", "sla"]
sources: []
---

# AI Service Catalog: Tiers, Governance & Developer Portal

This section covers service tiers, governance implementation, and the developer portal that makes all services accessible.

## Service Tiers

The platform offers tiered access to match risk and usage patterns:

**Tier 1 — Explore:** Free tier for experimentation and POC
- Limits: 100K tokens/month, limited models, shared infrastructure
- SLA: Best-effort (no SLA)
- Governance: Basic logging; no approval required
- Audience: Individual developers experimenting
- No cost allocation

**Tier 2 — Standard:** For production use cases with modest scale
- Limits: 10M tokens/month, standard models, dedicated capacity
- SLA: 99% availability
- Governance: Monitoring, cost tracking, moderate approval for high-risk
- Audience: Teams with 1-3 production AI systems
- Cost: Metered consumption billing

**Tier 3 — Premium:** For critical business systems requiring high reliability
- Limits: 100M+ tokens/month, all models, premium support
- SLA: 99.9% availability, <500ms latency guarantee
- Governance: Full governance workflow; mandatory responsible AI review
- Audience: Enterprise critical systems
- Cost: Reserved capacity with monthly commitment

**Tier 4 — Custom:** For specialized or very-high-volume needs
- Unlimited quota; negotiated SLA; dedicated support
- Full governance including dedicated governance officer
- Audience: Business-critical systems requiring custom terms
- Cost: Custom negotiated pricing

## Service Governance Integration

**Governance by Default:**
- Every service request logged and auditable
- All production deployments trigger governance review
- Guardrails apply automatically (cannot be disabled)
- Responsible AI review required for high-risk use cases

**Approval Matrix by Service & Risk Level:**

| Service | Low Risk | Medium Risk | High Risk |
|---------|----------|------------|-----------|
| Inference | Auto | PM review | RAI + PM |
| Embedding | Auto | Auto | PM review |
| Knowledge | Auto | RAI review | RAI + governance |
| Agent | PM review | RAI review | Governance board |
| Guardrails | N/A | Auto | Governance |

**Access Control:**
- API keys tied to team and use case
- Audit logging of all API access
- RBAC on sensitive services (guardrails, memory, agent operations)
- Secrets rotated quarterly minimum

## Developer Portal & Self-Service

**AI Developer Portal Features:**

**Service Catalog:** Browse all available services, read documentation, see SLAs, view pricing

**API Management:**
- Generate and manage API keys
- View real-time usage and costs
- Set budget alerts
- View API request history and logs

**Quickstart Templates:**
- Python notebook: "Get started with inference in 5 minutes"
- Code samples in JavaScript, Python, Go
- Architecture templates (RAG, agent, LLM chain)

**Documentation:**
- API reference for all services
- Best practices guide (how to use each service effectively)
- Troubleshooting guide (common issues and solutions)
- Cost optimization tips

**Self-Service Provisioning:**
- Tier 1 access: immediate (automated approval)
- Tier 2 access: 1-2 days (manager approval)
- Tier 3+ access: 5-10 days (governance review + procurement)

**Cost Dashboard:**
- Real-time cost breakdown by service, model, team, project
- Month-to-date spending vs. budget
- Cost trend chart (week-over-week, month-over-month)
- Cost optimization recommendations

**Feedback & Support:**
- Knowledge base (FAQ, troubleshooting)
- Community forum (developer-to-developer support)
- Office hours (weekly support session with platform team)
- Email support (ticket-based for platform issues)

## Supporting Services

**Service 15: API Gateway**

- Centralized entry point for all AI service access
- Rate limiting (prevent abuse)
- Request logging and audit trail
- Cost attribution (map request to team/use case)
- Authentication (API key validation)

**Service 16: Secrets Service**

- Secure storage of API keys, database passwords, etc.
- Automatic rotation policies
- Access control (only authorized agents/services access secrets)
- Audit logging of all access

**Service 17: Compliance Review Service**

- Automated compliance checks (EU AI Act, GDPR, sector-specific)
- Responsible AI assessment for high-risk systems
- Audit trail maintenance
- Annual third-party audit support

## Platform Success Metrics

**Adoption Metrics:**
- % of AI teams using platform (target: >80%)
- Monthly active users
- Services adoption rate (which services are most used)

**Operational Metrics:**
- Platform availability (target: >99.9%)
- API latency (target: <500ms p95)
- Incident MTTR (mean time to recovery)

**Cost Metrics:**
- Cost per AI use case (trending down over time)
- Cost savings vs. pre-platform baseline (target: 30-50% lower)

**Developer Experience:**
- NPS (Net Promoter Score) for developer satisfaction
- Time-to-first-deployment (hours via self-service)
- Support ticket resolution time

## Platform Maturity Progression

**Level 1:** Core inference access only; no governance

**Level 2:** Add knowledge service, embedding; basic governance

**Level 3:** Add agent runtime, guardrails, observability; full governance

**Level 4:** Add cost optimization, fine-tuning, compliance service; constitutional governance

**Level 5:** Platform is invisible; every team uses it natively as operating fabric

## Pricing & Chargeback Model

**Pricing Components:**
- Infrastructure cost (GPU, storage, networking): allocated per service
- Service overhead (engineering, support): 20% markup
- Profit margin (if internal chargeback): 10-15%

**Chargeback Options:**
1. **Full chargeback:** Business units pay per usage (metered)
2. **Hybrid chargeback:** Fixed platform fee + variable usage charges
3. **Centralized funding:** Single budget for entire AI platform (no per-team chargeback)

**Recommendation:** Hybrid model best aligns incentives (teams have stake in platform, platform team has stable funding)

---

## Related

- [AI Service Catalog: Core Inference & Data Services](20-part-10-service-catalog.md)
- [AI Service Catalog: Agent, Guardrail & Observability Services](71-part-10-service-catalog-agent-guardrail-observability.md)
- [Platform Operating Model](17-part-07-platform-operating-model.md)
- [Operating Models](12-part-02-operating-models.md)

## Sources

