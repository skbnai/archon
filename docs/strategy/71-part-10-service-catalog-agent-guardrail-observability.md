---
title: "AI Service Catalog: Agent, Guardrail & Observability Services"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-10-service-catalog-part2
maturity: practitioner
personas: [platform-lead, architect, developer]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes: []
tags: ["service-catalog", "agent-platform", "guardrails", "observability", "monitoring", "safety"]
sources: []
pagination_prev: strategy/part-10-service-catalog
pagination_next: strategy/part-10-service-catalog-tiers-governance-developer-portal
---

# AI Service Catalog: Agent, Guardrail & Observability Services

These services support autonomous agents, safety controls, and comprehensive observability across all AI usage.

## Service 8: Agent Runtime

**Purpose:** Managed deployment and execution of AI agents

**Features:**
- Agent execution engine (supports multiple frameworks: LangGraph, CrewAI, Claude SDK)
- Tool integration and MCP server support
- Human-in-the-loop workflows (approval gates before agent actions)
- Agent versioning (model + prompt + tools + memory as compound version)
- Agent lifecycle management (create, update, deprecate, retire)

**SLA:** 99.9% availability; &lt;500ms per agent step

**Governance:**
- Agent Charter requirement (documented goal, constraints, tools)
- Agent Governance Board approval for high-risk agents
- Action audit logging (every tool call audited)
- Kill switch capability (immediate agent shutdown)

**Monitoring:** Task completion rate, human handoff rate, tool errors, unexpected behavior

**Access:** REST API, agent framework SDKs, web portal

**Quotas:** 100 concurrent agents default; scale via request

## Service 9: Tool Registry & MCP Service

**Purpose:** Catalog and manage tools available to agents

**Features:**
- Tool/MCP server registry (discoverable by agents)
- Tool versioning and lifecycle management
- Tool documentation (API schema, required permissions, limitations)
- Tool composition (combine multiple tools in workflows)
- Least-privilege enforcement (each agent gets exactly needed permissions)

**Tool Types:**
- API integrations (REST, GraphQL)
- Database queries (read-only by default)
- Code execution (sandboxed Python)
- Web search and information retrieval
- Custom business tools

**SLA:** 99.9% availability

**Governance:**
- Security review of all new tools
- Responsible AI review for high-impact tools
- Access control per agent (RBAC on tools)
- Audit logging of all tool calls

**Access:** Portal for tool registration, SDKs for tool consumption

## Service 10: Guardrail Service

**Purpose:** Input filtering and output safety controls

**Input Guardrails:**
- Prompt injection detection (catch adversarial inputs)
- Jailbreak attempt blocking
- PII input masking (before sending to LLM)
- Malicious input detection

**Output Guardrails:**
- Hallucination detection (comparing response to retrieval sources)
- Harmful content filtering (violence, hate speech, etc.)
- Regulatory compliance filtering (e.g., no medical advice)
- Sensitive data filtering (prevent accidental exposure)

**SLA:** 99.5% availability; &lt;50ms per request (low latency for inline safety)

**Configuration:** Per use case (different guardrails for different domains)

**Governance:**
- Central guardrail governance (cannot be disabled by individual teams)
- Audit logging of guardrail violations
- Regular updates as threats evolve

**Access:** Automatic (built into inference pipeline); API for custom checks

## Service 11: Content Moderation Service

**Purpose:** Automated moderation of user-generated and agent-generated content

**Capabilities:**
- Toxicity detection
- Hate speech detection
- Sexual content detection
- Violence/gore detection
- Spam detection

**Models Supported:** Azure Content Safety, Perspective API, custom enterprise models

**SLA:** 99% availability; &lt;200ms per moderation request

**Pricing:** Per-request; batch processing available

**Access:** REST API, SDKs, batch upload

## Service 12: AI Observability Service

**Purpose:** Comprehensive visibility into all AI usage and performance

**Monitoring Dimensions:**
- **Quality Metrics:** Accuracy, relevance, coherence, hallucination rate
- **Performance:** Latency, throughput, error rates
- **Cost:** Tokens consumed per model, cost per transaction, cost trends
- **Usage:** Request volume, active users, features used
- **Safety:** Safety filter activations, guardrail violations, safety incidents

**Features:**
- Real-time dashboards (cost, quality, performance)
- Alerting on threshold breaches (quality drop, cost overrun)
- Historical trend analysis (detect slow drift)
- Per-team usage visibility (cost allocation)
- Root cause analysis tools (investigate performance issues)

**SLA:** 99.9% availability for dashboards; &lt;1 minute lag for metrics

**Retention:** 1 year of data (searchable); archive historical data

**Access:** Web portal (dashboards), REST API (programmatic), Grafana integration

**Governance:** Role-based access (teams see only their own data; leadership sees aggregated)

## Service 13: AI FinOps Service

**Purpose:** Cost optimization and financial management for AI

**Features:**
- Cost tracking by team, project, model, use case
- Budget enforcement (alerts when approaching limits)
- Cost optimization recommendations (e.g., switch to cheaper model)
- Reserved capacity discounts (negotiate volume with vendors)
- Usage anomaly detection (alert on cost spike)
- Chargeback reporting (bill back to business units)

**Pricing Models Supported:**
- Pay-as-you-go (per token, per API call)
- Reserved capacity (monthly/annual commitment for discount)
- Tiered pricing (volume discounts)

**Reports:**
- Monthly cost reconciliation by team
- Quarterly trend analysis
- Annual ROI by use case

**Access:** Web portal (cost dashboards), export to finance systems

## Service 14: Evaluation-as-a-Service

**Purpose:** Automated quality evaluation of AI outputs

**Evaluation Methods:**
- Reference-based (compare to gold standard)
- Reference-free (evaluate without ground truth)
- RAG-specific metrics (retrieval quality, faithfulness)
- Agent-specific metrics (task completion, safety)
- LLM-based evaluation (use LLM to score quality)

**Common Metrics:**
- Accuracy, precision, recall, F1 (classification)
- ROUGE, BLEU (text generation)
- Faithfulness, relevance (RAG/QA)
- Task success rate (agents)

**SLA:** 99% availability; async processing (results in 1-24 hours depending on size)

**Pricing:** Per-evaluation-request; batch discounts available

**Access:** Web portal for one-off evaluation, batch API for automated pipelines

---

## Related

- [AI Service Catalog: Core Inference & Data Services](20-part-10-service-catalog.md)
- [AI Service Catalog: Tiers, Governance & Developer Portal](72-part-10-service-catalog-tiers-governance-developer-portal.md)
- [Platform Operating Model](17-part-07-platform-operating-model.md)

## Sources

