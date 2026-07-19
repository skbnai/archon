---
title: "Enterprise AI Platform, Data & Agentic Architecture"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: enterprise-ai-platform-and-data-architecture
maturity: expert
personas: ["CTOs", "Enterprise Architects", "Data Officers", "Platform Engineers"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: ["docs/enterprise-architecture/transformation/03_Enterprise_AI_Platform_and_Data_Architecture.md"]
tags: ["enterprise-ai", "platform-architecture", "data-architecture", "agentic-ai", "mcp"]
sources: []
---

One paved road for every AI workload. The platform must be the easiest way to ship an AI feature — golden paths, templates, self-service — or teams will route around it. This is the architecture that enables scale without governance becoming a queue.

## Architecture Principles

1. **Model-agnostic by construction:** All model access flows through a gateway; frontier models are swappable commodities and no use case binds directly to a vendor SDK.

2. **Paved road, not police road:** The platform must be the easiest way to ship an AI feature — or teams will route around it. Golden paths, templates, and self-service are non-negotiable.

3. **Permissions travel with data:** Source-system entitlements are enforced at retrieval time; an AI system must never widen a user's effective access.

4. **Everything observable, everything evaluated:** No production AI without logging, tracing, evaluation suites, and cost attribution.

5. **Autonomy is earned, not granted:** Agents progress through defined autonomy levels based on demonstrated evaluation performance.

6. **Build the scarce, buy the commodity:** Buy models, vector stores, and orchestration primitives; build the knowledge corpus, evaluation assets, domain agents, and integration fabric — that is where advantage lives.

---

## Reference Platform Blueprint: Seven Layers

| Layer | Capabilities | Approach & Key Decisions |
|---|---|---|
| **7. Experience** | Enterprise assistant, in-app copilots, API/embedded AI | One assistant surface with function-specific skills; copilots embedded where work happens (IDE, CRM, ITSM) |
| **6. Agent orchestration** | Agent runtime, multi-agent collaboration, planner/executor patterns, HITL gates, agent registry | Buy orchestration framework; build domain agents. Every agent registered with owner, scope, autonomy level, tool entitlements |
| **5. Tool & integration fabric** | MCP servers over enterprise systems; A2A patterns for agent cooperation; API management | Standardize on MCP as the enterprise tool contract: one governed MCP server per system-of-record (CRM, ERP, ITSM, HRIS, KB) |
| **4. Knowledge & memory** | RAG pipelines, vector databases, hybrid search, knowledge graph, conversation/task memory | Central retrieval service consumed by all use cases; document-level ACLs enforced at query time; memory tiered with privacy-driven TTLs |
| **3. Model layer** | Frontier LLMs (multi-vendor), specialized/small models, embeddings, fine-tuned adapters, classical ML | AI gateway provides routing, failover, caching, rate limits, per-team cost metering; model choice per task is a routing policy, not a code change |
| **2. Data platform** | Lakehouse, streaming, data products, semantic layer, feature store, quality & lineage | Detailed below |
| **1. Infrastructure** | Primary hyperscaler for core; secondary cloud for resilience; GPU capacity strategy; on-prem integration | Multi-cloud pragmatism: portable at gateway and data layers; capacity reserved for predictable inference, burst for training |
| **0. Cross-cutting** | Identity (human + non-human), secrets, network segmentation, observability, evaluation, FinOps, CI/CD | Detailed in governance section |

---

## Data & Knowledge Architecture: From Data Estate to Decision Fuel

| Component | Purpose | Design Notes |
|---|---|---|
| **Data products** | Governed, contract-backed datasets owned by domains (customer, product, finance, supply) | Each has owner, SLA, quality metrics, consumers; funded as products, not projects |
| **Semantic layer** | One set of definitions for core metrics and entities | Prerequisite for trustworthy decision support; Horizon 1 deliverable scoped to ~50 core metrics |
| **Unstructured knowledge pipeline** | Ingest, chunk, enrich, and index documents, wikis, tickets, emails, call transcripts | Metadata and ACL capture at ingestion; freshness SLAs; deletion propagation to honor privacy requests |
| **Knowledge graph** | Entities and relationships (customers, products, contracts, assets) that ground retrieval and reasoning | Start narrow (customer 360 + product) and grow by use-case pull, not big-bang modeling |
| **Feature store & ML data** | Reusable features for classical ML (forecasting, risk scoring) | Shared with LLM workloads where hybrid patterns apply |
| **Knowledge engineering program** | Systematic capture of expert know-how (interviews, process mining, annotation) into retrievable form | Treat expert time as the scarcest input; prioritize domains with retirement-driven knowledge risk |

---

## Agentic AI Strategy: Graduated Autonomy & MCP

### Autonomy Levels: From Assist to Autonomous

| Level | Description | Human Role | Gates to Advance |
|---|---|---|---|
| **A0 — Assist** | Drafts, summarizes, suggests; no system writes | Human performs all actions | Baseline evaluation suite passed |
| **A1 — Act with approval** | Agent prepares transactions; human approves each | Human-in-the-loop per action | ≥95% suggestion acceptance in pilot; zero critical errors over defined volume |
| **A2 — Act with oversight** | Agent executes within hard limits; humans review samples and exceptions | Human-on-the-loop | Sustained A1 performance; rollback tested; limits encoded |
| **A3 — Autonomous in bounds** | End-to-end execution in narrow, reversible domain | Human sets policy, audits outcomes | Independent risk sign-off; kill switch proven in game-day exercise |

### Multi-Agent Standards

- **MCP as the tool contract:** Agents never integrate point-to-point; they call governed MCP servers whose scopes are permissioned per agent identity. Turns integration sprawl into a managed catalog.

- **Agent-to-agent (A2A) collaboration:** Permitted only between registered agents, with typed task contracts, budget limits (tokens, time, spend), and full trace propagation for end-to-end auditability.

- **Orchestration patterns:** Prefer supervisor/worker and pipeline patterns with explicit checkpoints over free-form agent swarms; determinism at workflow layer, flexibility inside each step.

- **Every agent has an owner:** A named human accountable for its scope, entitlements, evaluation results, and retirement — no orphan agents.

---

## Platform Engineering, Observability, Evaluation & FinOps

| Discipline | Minimum Standard at Scale |
|---|---|
| **Golden paths** | Templates for top patterns (RAG app, copilot, A1 agent) with logging, evals, security, cost metering pre-wired; team-to-production in days |
| **Observability** | Full tracing of prompts, retrievals, tool calls, outputs; PII-aware log redaction; drift and quality dashboards per use case |
| **Evaluation service** | Central eval harness: golden datasets per use case, automated regression on every model/prompt change, red-team suites, human review queues |
| **LLMOps / CI-CD** | Prompts, agent configs, eval suites are versioned artifacts; promotion between environments gated on eval scores, not vibes |
| **FinOps for AI** | Per-use-case token and GPU cost attribution; routing policies downshift to smaller models; caching; monthly unit-economics review |
| **Resilience** | Multi-model failover at gateway; degraded-mode design (fall back to search/human); AI outage never equals business outage |

**Platform success metric:** Median time for a business team to go from idea to governed production deployment — target under 30 days by month 18.

---

## Related

- [Executive Summary & AI Vision](35-executive-summary-and-ai-vision.md)
- [Governance, Responsible AI & Security Architecture](39-governance-responsible-ai-and-security.md)
- [Target Operating Model, Organization & Change](40-target-operating-model-and-change.md)

## Sources

- OWASP — Model Context Protocol specification
- Gartner — Platform Engineering maturity study (2026)
- Forrester — Data platform strategy report (2026)
