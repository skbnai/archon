---
title: "How Tech Companies Build & Serve Knowledge Systems"
date_created: 2026-07-05
last_reviewed: 2026-07-10
status: current
domain: data-knowledge
doc_type: guide
topic_id: tech-companies
supersedes:
  - docs/knowledge-engineering/industry-practices/tech-companies.md
covers_version: "as of 2026-07-10"
tags: ["knowledge-engineering", "industry-practices"]
source_type: native-md
---

# How Tech Companies Build &amp; Serve Knowledge Systems

How Big Tech serves data and knowledge internally — the platforms, the knowledge graphs, and the governance patterns the rest of the industry later adopted. Research current as of July 2026.

---

## The pattern: metadata first, LLMs second

Before generative AI, the hyperscalers had already solved the hard problem: **making organizational data discoverable, trustworthy, and access-controlled at scale**. Their metadata hubs and ML platforms became the governance substrate that grounded LLM serving was later built on. This is the single biggest difference from most enterprises, which tried to bolt RAG onto ungoverned data.

## Uber — Michelangelo

Uber's **Michelangelo** is the canonical internal ML-as-a-service platform, designed to cover the end-to-end workflow: manage data, train, evaluate, deploy, predict, and monitor.

- **Scale (2024–2026):** ~400 active ML projects, 20K+ model training jobs per month, 5K+ models in production, ~10 million real-time predictions per second at peak.
- **Feature governance:** the **Palette** feature store hosts 20,000+ features shared across teams — a single governed source for both batch features (Spark over historical data) and real-time features (Kafka/Flink streams).
- **Generative evolution:** Michelangelo 3.0 extended the same platform discipline to generative AI — Uber's "From Predictive to Generative" journey reuses the platform's evaluation, deployment, and monitoring rails for LLM workloads rather than building a parallel stack.

**Takeaway:** treat features, prompts, and retrieval corpora as governed, shared, versioned assets — not per-team artifacts.

## LinkedIn — DataHub + the Economic Graph

- **DataHub** (open-sourced) is LinkedIn's metadata platform: a one-stop discovery and lineage portal indexing not just datasets but metrics, jobs, charts, people, and groups. Ingestion is **push-based** via APIs and Kafka streams, which keeps metadata fresh at scale rather than relying on periodic crawls.
- The **Economic Graph** is LinkedIn's production knowledge graph — professionals, companies, educational institutions, and skills and the relationships between them — powering talent matching, labor-market analytics, and learning-path recommendations.

**Takeaway:** lineage and discovery as a *product* (with people and teams as first-class entities) is what later made permissions-aware AI serving feasible.

## Netflix — Metacat

Netflix's **Metacat** provides a unified API to access metadata across the heterogeneous data stores in Netflix's ecosystem — plugging the gap between many storage engines and one consistent governance view. The lesson generalizes: federate metadata rather than forcing data centralization.

## Airbnb — Dataportal &amp; Knowledge Repo

Airbnb built **Dataportal** for data exploration, discovery, and *trust*: employees search an inventory spanning logging schemas, tables, charts, dashboards, employees, and teams. The earlier **Knowledge Repo** did the same for analysis write-ups — peer-reviewed, versioned data science knowledge. Airbnb made **trust signals** (ownership, freshness, usage) part of the search experience, anticipating the "authoritative source" problem that now dominates enterprise RAG.

## Microsoft — Graph, semantic index, permissions-aware grounding

Microsoft's approach to serving knowledge to its own employees and M365 customers is the clearest public blueprint for **permissions-aware grounding**:

- The **semantic index for Copilot** interprets query intent and appends grounding data drawn from the **Microsoft Graph** (mail, files, chats, people, org structure) to the LLM prompt.
- Access to tenant data in Microsoft Graph is gated by **role-based access control**; the index stores per-document permissions so retrieval is filtered **dynamically at query time** — the model never sees content the querying user couldn't open themselves.
- Ranking aggregates signals across workplace applications, including collaborators' activity.

**Takeaway:** enforce ACLs at retrieval time, per chunk/document, using the same identity system as the source applications. Post-generation filtering is too late.

## Meta — social graph + Purple Llama

- Meta's **social knowledge graph** (friendships, groups, events, interests, communications) is one of the largest production knowledge graphs, powering personalization across its apps.
- On the Responsible AI side, Meta's **Purple Llama** initiative ships **Llama Guard** — an open safeguard model that classifies both prompts and responses into safety risk categories (toxicity, hate speech, etc.), used as an input/output filter around serving.

## Amazon — Bedrock Guardrails as productized RAI

Amazon operationalized internal responsible-AI practice into **Bedrock Guardrails**: six configurable safeguard policies — content moderation, prompt-attack detection, topic controls, PII redaction, hallucination/grounding checks, and **Automated Reasoning checks** that produce mathematically verifiable explanations for validation decisions (99% verification accuracy claimed). Notably, the guardrails apply across *any* foundation model, including third-party and self-hosted ones — governance decoupled from the model.

## Google — knowledge graph heritage and grounded serving

Google's Knowledge Graph pioneered entity-grounded search, and that heritage shapes its enterprise offerings: Vertex AI's grounding services check generations against Google Search or enterprise corpora and return citation metadata. Internally, Google's engineering knowledge culture (monorepo, code search, internal search over docs/people) follows the same discoverability-first pattern as the other hyperscalers.

## The buy-side echo: Glean

The pattern the hyperscalers built internally is what **Glean** productized for everyone else: a per-customer **enterprise knowledge graph** assembled from 100+ connectors, weighting relationships between content, people, and activity, with permissions mirrored from source systems. Its traction (ARR doubling to ~$200M; customers consuming 20+ trillion tokens/year) is evidence of how central the governed-knowledge-graph pattern has become. Independent research underlines why: LLMs answering complex enterprise questions scored **16.7% accuracy without knowledge-graph grounding vs 54.2% with it**.

## Pattern summary

| Pattern | Pioneered by | Now standard as |
| --- | --- | --- |
| Metadata hub with lineage | LinkedIn DataHub, Netflix Metacat | Data catalogs / context layer under RAG |
| Feature/asset store with sharing &amp; governance | Uber Palette | Governed embedding &amp; prompt stores |
| Trust signals in discovery | Airbnb Dataportal | Authoritative-source curation |
| Permissions-aware semantic index | Microsoft 365 Copilot | Query-time ACL-filtered retrieval |
| Knowledge graph as grounding substrate | Google, LinkedIn, Meta | GraphRAG / enterprise knowledge graphs |
| Model-agnostic runtime guardrails | Amazon Bedrock, Meta Llama Guard | Runtime RAI enforcement |

---

## Related

- [Consulting Firm AI Knowledge Platforms](07-consulting-firms.md) — the parallel case-study set for consultancies' internal knowledge platforms.
- [Governance & Responsible AI for Knowledge Systems](09-governance-rai.md) — the governance patterns these tech companies' approaches informed industry-wide.

## Sources

- [Meet Michelangelo: Uber's Machine Learning Platform](https://www.uber.com/us/en/blog/michelangelo-machine-learning-platform/)
- [From Predictive to Generative — How Michelangelo Accelerates Uber's AI Journey](https://www.uber.com/us/en/blog/from-predictive-to-generative-ai/)
- [How LinkedIn, Uber, Lyft, Airbnb and Netflix are Solving Data Management and Discovery (KDnuggets)](https://www.kdnuggets.com/2019/08/linkedin-uber-lyft-airbnb-netflix-solving-data-management-discovery-machine-learning-solutions.html)
- [A Dive Into Metadata Hubs (Holistics)](https://www.holistics.io/blog/a-dive-into-metadata-hubs/)
- [Semantic indexing for Microsoft 365 Copilot (Microsoft Learn)](https://learn.microsoft.com/en-us/microsoftsearch/semantic-index-for-copilot)
- [Amazon Bedrock Guardrails (AWS)](https://aws.amazon.com/bedrock/guardrails/)
- [Glean: Enterprise Graph](https://www.glean.com/product/enterprise-graph)
- [Glean Doubles ARR to $200M (Futurum)](https://futurumgroup.com/insights/glean-doubles-arr-to-200m-can-its-knowledge-graph-beat-copilot/)
- [7 Knowledge Graph Examples of 2026 (PuppyGraph)](https://www.puppygraph.com/blog/knowledge-graph-examples)
- [How knowledge graphs work and why they are key to context for enterprise AI (Glean)](https://www.glean.com/blog/knowledge-graph-agentic-engine)
