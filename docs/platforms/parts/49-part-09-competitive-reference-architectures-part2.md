---
title: "Databricks Agentic AI, Part 9 (Part 2: Anti-Patterns, Decision Framework & Roadmap)"
doc_type: guide
domain: platforms
status: current
topic_id: part-09-competitive-reference-architectures-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags:
  - databricks
  - agentic-ai
  - anti-patterns
  - decision-framework
  - roadmap
covers_version: "2026"
---

*Part 2 of 2 of [Databricks Agentic AI, Part 9 — Competitive Comparison & Industry Reference Architectures](../49-part-09-competitive-reference-architectures.md).*

## 3. Anti-Patterns

### Anti-Pattern 1: Prompt-Layer Governance

**What:** Writing governance rules inside the system prompt ("Never access files outside /approved/").
**Why Bad:** The model can reason around these rules or be manipulated via injection.
**Fix:** Enforce at infrastructure layer via Omnigent or Unity AI Gateway Contextual Policies.

### Anti-Pattern 2: One Giant Agent for Everything

**What:** Building a single agent that handles customer support, order management, and financial reconciliation.
**Why Bad:** Impossible to govern (overly broad permissions), difficult to evaluate, single failure point, token costs explode.
**Fix:** Use Supervisor Agent + specialist sub-agents. Each specialist has minimum required permissions.

### Anti-Pattern 3: Shared Service Principal for All Agents

**What:** Using one service principal (`ai-agent-prod`) for every agent in the organization.
**Why Bad:** Breach of least-privilege; one compromised agent gives attacker access to all tables and tools the SP is authorized for.
**Fix:** One service principal per agent deployment. Scoped to exactly the data and tools that agent requires.

### Anti-Pattern 4: Skipping Evaluation Before Production

**What:** Deploying agents without running MLflow 3 evaluation against a curated dataset.
**Why Bad:** No quality baseline; no way to detect regression in future versions; hallucination rate unknown.
**Fix:** Mandatory evaluation gate in CI/CD (Lakeflow Jobs quality check) before promoting agent to production alias.

### Anti-Pattern 5: No Iceberg + Blind Delta Vendor Lock

**What:** Writing Delta tables without UniForm, never enabling Iceberg REST catalog.
**Why Bad:** Data is inaccessible to Snowflake, BigQuery, Trino, and any future platform without ETL.
**Fix:** Enable UniForm on all production tables. Expose Unity Catalog as Iceberg REST endpoint. Design for cross-engine portability.

### Anti-Pattern 6: ETL to Lakebase Instead of LTAP

**What:** Continuing to use ETL pipelines to copy operational data from Postgres to Delta for analytics.
**Why Bad:** Hours of latency, pipeline maintenance overhead, duplicate governance, stale agent knowledge.
**Fix:** Migrate operational Postgres to Lakebase; use LTAP so transactional and analytical workloads share the same storage natively.

### Anti-Pattern 7: Cost-Blind Agent Design

**What:** Using GPT-4o or Claude Opus for every step including simple classification tasks.
**Why Bad:** 10–50x overspend vs using a capable smaller model (Llama-3-8B) for simple steps.
**Fix:** Use Unity AI Gateway smart routing with complexity-based model selection. Profile agent steps; downgrade model for simple steps.

## 4. Decision Framework: When to Use Databricks vs Alternatives

### Build vs Buy Decision

| Scenario | Recommendation |
| --- | --- |
| You already have Delta Lake data in Databricks | **Databricks-first** — agents live where the data is |
| Analytics team is SQL-first, no ML | **Consider Snowflake Cortex** for simpler agent needs |
| AWS-native stack, no Databricks today | **AWS Bedrock + Strands** as entry point |
| Azure-native, Microsoft-heavy organization | **Azure AI Foundry** with ADB if data volumes justify |
| You need fine-tuning and custom model training | **Databricks Mosaic AI** (strongest ML training platform) |
| Multi-cloud governance at enterprise scale | **Databricks Unity Catalog** (broadest coverage) |
| You want open, vendor-neutral agent infrastructure | **Databricks + Omnigent** (open-source meta-harness) |
| Consumer-oriented no-code agentic apps | **Genie One / Snowflake CoWork** |

### The Iceberg Decision

| Scenario | Recommendation |
| --- | --- |
| Existing Delta Lake tables, want Snowflake access | Enable **Delta UniForm** (no migration required) |
| Greenfield, multi-engine strategy | **Native Iceberg v3** as primary format |
| Need Postgres + analytics together | **Lakebase + LTAP** (stores as Delta/Iceberg natively) |
| External catalogs (Glue, Snowflake, Salesforce) | **Unity Catalog Federation** (no data movement) |

## 5. Roadmap Analysis and Future Trends

### What's Coming (based on public signals, previews, and engineering blog posts)

| Capability | Evidence | Likely Timeline |
| --- | --- | --- |
| **Genie App Builder GA** | Private Preview announced DAIS 2026 | H2 2026 |
| **Genie ZeroOps GA** | Private Preview announced DAIS 2026 | H1 2027 |
| **Unity AI Gateway GA** | Beta at DAIS 2026 | H2 2026 |
| **Contextual Policies GA** | Beta at DAIS 2026 | H2 2026 |
| **Catalog Federation GA** (Google, Palantir) | Preview DAIS 2026 | H2 2026 |
| **Cross-engine ABAC GA** | Beta DAIS 2026 | H2 2026 |
| **Lakebase Search GA** | Beta 2026 | H1 2027 |
| **Agent-to-Agent (A2A) protocol** | MCP announced; A2A in progress | 2026–2027 |
| **Agent memory native service** | Lakebase + Vector Search today; managed memory service likely | 2027 |
| **Databricks on-prem / air-gapped** | Increasing enterprise demand signals | 2027+ |

### Strategic Implications for Enterprise Architects

**1. Governance is the new moat**
The question is no longer "which platform has the best model?" It's "which platform lets me govern 500 agents across 50 teams at enterprise scale?" Databricks is betting Unity AI Gateway + Omnigent wins this.

**2. The ETL stack is being replaced**
LTAP + Lakebase signals a world where operational databases and analytical stores merge. Architects maintaining dual-stack (OLTP + warehouse) should evaluate the Lakebase migration path seriously.

**3. Iceberg is the lingua franca**
Any data strategy that doesn't account for Iceberg interoperability will create technical debt. Plan for UniForm on all new Delta tables and evaluate native Iceberg for greenfield.

**4. Agents replace pipelines**
Genie ZeroOps replacing manual pipeline operations is the tip of the iceberg. Within 2–3 years, agentic orchestration will replace much of the Airflow/dbt DAG management work. Data engineers will shift from writing pipelines to governing agent behavior.

**5. Context engineering is the new data engineering**
Genie Ontology is Databricks' thesis that the bottleneck is no longer data access but business context. Architects who invest in semantic layers, business glossaries, and structured knowledge graphs will get disproportionate AI ROI.

## 6. Comprehensive Glossary

| Term | Definition |
| --- | --- |
| **A2A Protocol** | Agent-to-Agent communication standard (emerging; builds on MCP) |
| **ABAC** | Attribute-Based Access Control — policy-driven access using governed tags |
| **Agent Bricks** | Databricks' auto-optimizing agent construction and deployment platform |
| **Agent Lake** | Conceptual term for the lakehouse as persistence substrate for all agent artifacts |
| **AI Functions** | SQL-native LLM capabilities (ai_query, ai_classify, ai_summarize, etc.) |
| **Catalog Federation** | Unity Catalog governing external tables without data movement |
| **Contextual Service Policies** | Runtime policies defining what an agent can DO in a given interaction context |
| **DAIS** | Data + AI Summit — Databricks' annual user conference |
| **DBRX** | Databricks' proprietary open-weights LLM |
| **Delta Lake** | Apache-licensed open-source ACID table format on object storage |
| **Delta Sharing** | Apache-licensed open protocol for sharing live data without copying |
| **Delta UniForm** | Delta feature generating Iceberg metadata for cross-engine reads |
| **Deletion Vectors** | Iceberg v3 / Delta feature marking deleted rows without file rewrite |
| **Foundation Model APIs** | Pay-per-token access to built-in LLMs (Llama, DBRX, Mixtral, embedding models) |
| **Genie One** | Agentic AI coworker for business users (web, iOS, Android) |
| **Genie Ontology** | Self-improving context layer extracting business knowledge from data and apps |
| **Genie ZeroOps** | Background AI agent for autonomous data pipeline monitoring and self-healing |
| **HITL** | Human-in-the-Loop — requiring human approval before agent takes action |
| **Iceberg REST Catalog** | Standard API for catalog interoperability; implemented by Unity Catalog |
| **Lakebase** | Serverless Postgres database storing data in Delta/Iceberg on object storage |
| **Lakebase Search** | Hybrid vector + full-text retrieval extension for Lakebase |
| **Lakehouse RT** | Real-time analytics product (&lt;100ms) powered by Reyden compute engine |
| **Lakeflow** | Unified data engineering platform: ingestion + transformation + orchestration |
| **Lakewatch** | Databricks' lakehouse-native SIEM for security analysis of AI activity |
| **LTAP** | Lake Transactional/Analytical Processing — unified OLTP+OLAP on shared storage |
| **MCP** | Model Context Protocol — standard for connecting agents to tools and data sources |
| **Model Units** | Multi-tenant LLM inference abstraction enabling GPU bin-packing (80% cost reduction) |
| **Mosaic AI** | Databricks' brand for its full AI platform stack |
| **Omnigent** | Apache 2.0 open-source meta-harness for multi-agent governance |
| **Prompt Cache** | Caching of repeated system prompt prefix tokens to reduce inference cost |
| **Reyden** | Databricks' compute engine powering Lakehouse RT |
| **Row Lineage** | Iceberg v3 feature tracking which rows changed since a given sequence number |
| **Smart Routing** | AI Gateway capability to route requests to cheapest capable model automatically |
| **Supervisor Agent** | Managed multi-agent orchestrator that decomposes tasks and routes to workers |
| **TAO** | Test-Adaptive Optimization — fine-tuning-equivalent quality without training data |
| **UC** | Unity Catalog — Databricks' universal governance layer |
| **Unity AI Gateway** | Runtime governance layer for agent interactions (Beta, 2026) |
| **VARIANT** | New Iceberg v3 / Delta data type for semi-structured JSON/BSON data |
| **Vector Search** | Mosaic AI Vector Search (now AI Search) — native vector database backed by Delta |
| **Zerobus** | Lakeflow's high-volume event ingestion capability |

## Related

- [Part 1: Platform Comparison & Industry Reference Architectures](../49-part-09-competitive-reference-architectures.md)
- [Part 8: Observability, FinOps & Integration Ecosystem](../48-part-08-observability-finops-integration.md)
