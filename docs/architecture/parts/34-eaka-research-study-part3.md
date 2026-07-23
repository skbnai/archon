---
title: "Enterprise Agent Knowledge Architecture (EAKA) Research Study (Part 3 of 3): Context Engineering, Reliability, Reference Architecture, Lifecycle & Maturity Model"
doc_type: research-report
domain: architecture
topic_id: eaka-research-study-part3
date_created: 2026-07-11
last_reviewed: 2026-07-23
status: current
supersedes: []
tags: [enterprise-architecture, research, knowledge-architecture, study, eaka]
covers_version: "2026"
---

<!-- Part 3 of 3 - See also: Part 1 (pathname:///archon/architecture/81-eaka-research-study) and Part 2 (pathname:///archon/architecture/parts/33-eaka-research-study-part2) -->

## Enterprise Agent Knowledge Architecture (EAKA) Research Study

Part 3 of 3: Context Engineering, Reliability, Reference Architecture, Lifecycle & Maturity Model

### 10. Knowledge Context Engineering

Context Engineering is the discipline of optimally managing what knowledge an agent loads, compresses, summarises, retrieves, forgets, and refreshes within a bounded context window. Poor context management is the primary driver of hallucination and stale-knowledge errors in enterprise AI systems.

#### 10.1 Context Budget Framework

| **Context Zone** | **Budget Allocation** | **Content** | **Eviction Policy** |
|---|---|---|---|
| System Context | 5–10% | Agent identity, active skill specs, governance rules | Pinned — never evicted |
| Goal & KEP | 10–15% | User goal, Knowledge Execution Plan, validation rules | Pinned until task complete |
| Active Skills | 20–30% | Executing skill prompts, retrieval strategies | LRU within skill budget |
| Retrieved Knowledge | 30–40% | Chunked knowledge artefacts with provenance | Relevance + trust decay |
| Tool Results | 10–15% | MCP tool outputs, structured data | Summarised after use |
| Working Memory | 5–10% | Intermediate reasoning steps, entity state | Checkpoint + compress |

#### 10.2 Context Lifecycle Operations

- **Load** — inject knowledge chunk into context, tagged with source, trust score, and TTL.
- **Compress** — summarise verbose tool output or long documents to essential claims.
- **Forget** — evict low-relevance, low-trust, or expired chunks on LRU + trust-weighted policy.
- **Refresh** — re-retrieve a chunk whose TTL has expired or whose source has been updated.
- **Checkpoint** — serialise working memory for long-horizon tasks that exceed one context window.
- **Summarise** — distil multi-turn reasoning into compact facts for handoff to next agent.

#### 10.3 When to Retrieve vs. Use Cached Knowledge

Retrieve freshly when: (a) source freshness TTL has expired, (b) task is safety-critical or compliance-driven, (c) knowledge was flagged as recently updated in the EKG. 

Use cached knowledge when: (a) TTL is valid, (b) task is low-risk exploratory, (c) retrieval latency would exceed SLA budget.

#### 10.4 Hallucination Reduction Through Context Engineering

- Ground every factual claim to a retrieved chunk with provenance (not model parametric memory).
- Enforce a 'no-claim-without-citation' rule in skill output schemas.
- Use trust-score thresholds: only chunks with trust ≥ 65 are used for safety-critical claims.
- Cross-validate critical facts across ≥ 2 independent sources before including in response.

### 11. Agent Reliability

Reliability in enterprise AI is not simply about model accuracy — it encompasses knowledge currency, retrieval fidelity, tool robustness, and architectural consistency. EAKA defines a multi-dimensional reliability framework.

#### 11.1 Failure Taxonomy

| **Failure Type** | **Root Cause** | **EAKA Mitigation** |
|---|---|---|
| Knowledge hallucination | Model parametric memory overriding retrieved facts | Citation-mandatory output schema; grounding checks |
| Stale documentation | Index not updated after source change | Change-event-driven re-indexing; TTL freshness gates |
| Incorrect SDK version | Version-agnostic retrieval; no version pinning | SDK version nodes in EKG; version-aware retrieval |
| Wrong implementation pattern | Low-trust source ranked above authoritative source | Trust score hierarchy enforced in retrieval fusion |
| Conflicting ADRs | Multiple ADRs without supersedes relationship | EKG conflict detection; governance resolution protocol |
| Retrieval failure | Source system downtime; index corruption | Multi-source redundancy; degraded-mode fallback policy |
| Tool failure | MCP server timeout or schema mismatch | Fallback server cascading; retry with exponential backoff |
| Composition error | Skill dependency cycle or budget exhaustion | DAG cycle detection; budget enforcement in Skill Composer |

#### 11.2 Reliability Metrics

- **Knowledge Grounding Rate (KGR)** — % of factual claims traceable to a retrieved chunk.
- **Source Freshness Score (SFS)** — weighted average freshness of all chunks used in a response.
- **Tool Success Rate (TSR)** — % of MCP tool calls that succeed within SLA.
- **Skill Composition Accuracy (SCA)** — % of compositions that satisfy goal requirements.
- **Conflict Resolution Time (CRT)** — average time to resolve a detected knowledge conflict.
- **Hallucination Detection Rate (HDR)** — % of hallucinations caught by the Evaluation Engine.

#### 11.3 Reliability Measurement Architecture

- **Online evaluation** — real-time fact-checking via Evaluation Engine on every KEP execution.
- **Offline evaluation** — scheduled batch runs of Skill evaluation suites against golden datasets.
- **Adversarial testing** — red-team probing of skills with known-bad or conflicting inputs.
- **User feedback loop** — thumbs-up/down and correction signals fed back to Trust Engine.
- **A/B skill versioning** — canary deployments of new skill versions with statistical comparison.

### 12. Enterprise Reference Architecture

The EAKA Reference Architecture defines a layered, loosely coupled platform with clear separation between knowledge representation, skill execution, governance, and observability. All components communicate through well-defined APIs, enabling vendor-neutral deployment.

#### 12.1 Platform Component Inventory

| **Component** | **Responsibility** | **Key Interfaces** |
|---|---|---|
| Knowledge Registry | Stores and indexes all knowledge artefacts with provenance | Ingest API, Search API, Change Event Stream |
| Skill Registry | Governs skill lifecycle: publish, version, discover, retire | Skill CRUD API, Discovery API, Subscription Events |
| Agent Registry | Tracks agent identities, capabilities, and active tasks | Agent Register API, Health API, Task Lifecycle API |
| MCP Registry | Manages MCP server catalogue, capability index, and health | Server Register API, Tool Discovery API, Health Stream |
| Context Planner | Allocates context budgets and manages window lifecycle | Budget Allocation API, Eviction Policy Engine |
| Knowledge Planner | Constructs Knowledge Execution Plans from user goals | Goal Parse API, KEP Generate API, KEP Archive |
| Skill Composer | Assembles skill DAGs and manages execution orchestration | Compose API, Execute API, DAG Visualisation API |
| Retrieval Broker | Routes retrieval queries to correct sources with fusion | Query API, Source Selector, Fusion Engine |
| Trust Engine | Computes and maintains trust scores for all artefacts | Score API, Decay Jobs, Feedback Ingestion API |
| Governance Engine | Enforces policies, approvals, conflicts, and compliance | Policy API, Approval Workflow, Audit Log API |
| Evaluation Engine | Runs evaluation suites and hallucination detection | Eval Run API, Metric Store, Alert Dispatch |
| Knowledge Graph | Persists and queries the Enterprise Knowledge Graph | Graph Query API (SPARQL/Cypher), Change Stream |
| Observability | Centralised telemetry, tracing, and alerting | OpenTelemetry collector, Dashboard API, Alert API |
| Feedback Loop | Collects user and agent signals to improve knowledge quality | Feedback Ingest API, Signal Processing, Trust Update |

#### 12.2 Layered Architecture

**EAKA Layered Reference Architecture**

- User / Agent Interface Layer (Natural language, API, Copilot plugins)
- Orchestration Layer (Knowledge Planner, Skill Composer, Context Planner)

![Figure 6](/img/enterprise-architecture/ea-p27-6.png)

#### 12.3 Technology Stack Recommendations

| **Layer** | **Open-Source Options** | **Cloud-Managed Options** |
|---|---|---|
| Vector Store | Qdrant, Weaviate, Milvus | Azure AI Search, AWS OpenSearch, Google Matching Engine |
| Graph Database | Neo4j Community, Apache Age (Postgres) | Neo4j Aura, Amazon Neptune, TigerGraph Cloud |
| Message Bus | Apache Kafka, NATS.io | Azure Service Bus, AWS EventBridge, GCP Pub/Sub |
| Observability | OpenTelemetry + Grafana + Tempo | Azure Monitor, AWS X-Ray, Google Cloud Trace |
| MCP Runtime | Open-source MCP SDK (Anthropic) | Vendor-integrated (Azure AI Foundry) |
| Workflow Engine | Temporal.io, Apache Airflow | AWS Step Functions, Azure Durable Functions |
| API Gateway | Kong, Envoy, Traefik | Azure APIM, AWS API Gateway, GCP API Gateway |

### 13. AI-Assisted Knowledge Lifecycle

Enterprise knowledge must not merely be indexed but continuously curated, validated, and evolved. EAKA's Knowledge Lifecycle Engine uses AI to automate the pipeline from raw document creation to governed skill generation — with human oversight at key gates.

#### 13.1 Lifecycle Pipeline

**AI-Assisted Knowledge Lifecycle Pipeline**

![Figure 7](/img/enterprise-architecture/ea-p28-7.png)

Deprecation Trigger (Conflict detected or TTL expired) → Archival (Immutable archive with lineage preserved)

#### 13.2 AI-Generated Skill Drafts

When new documentation is ingested, the Lifecycle Engine analyses knowledge gaps in the Skill Registry and automatically drafts new skills:

- Identify concepts in new document not covered by any active skill.
- Draft skill metadata: purpose, scope, required knowledge, retrieval strategy.
- Generate initial prompt templates using in-context examples from similar skills.
- Create skeleton evaluation suite with auto-generated test cases.
- Submit draft to Skill Registry with status 'Draft — Pending SME Review'.

#### 13.3 Drift Detection

- **Semantic drift** — embedding distance between current skill prompts and updated source docs exceeds threshold.
- **Version drift** — SDK or API version referenced in skill no longer matches latest released version.
- **Policy drift** — governing policy has been updated since skill last validated against it.
- **Usage drift** — skill success rate drops below reliability threshold in production metrics.

Detected drift triggers an automated notification to the skill owner with a diff between current skill specification and the updated source material. Owners have 30 days to publish an update before the skill is flagged as 'At Risk'.

### 14. Maturity Model & Roadmap

Enterprises should not attempt to implement the full EAKA platform in a single programme. The EAKA Maturity Model defines five progressive levels, each delivering measurable value while building towards the complete architecture.

#### 14.1 Enterprise AI Knowledge Maturity Model

| **Level** | **Name** | **Capabilities** | **Key Deliverable** |
|---|---|---|---|
| L1 | Ad-hoc RAG | Single vector index; no governance; manual tool config | Working AI assistant with document search |
| L2 | Governed Retrieval | Multi-source connectors; provenance tracking; trust scoring | Knowledge Registry + Source Tiers |
| L3 | Skill-Enabled | Skill Registry; basic skill composition; versioned skills | Enterprise Skills Platform v1 |
| L4 | Knowledge-Planned | KEP engine; EKG; dynamic MCP; context engineering | Knowledge Planner + EKG live |
| L5 | Autonomous Evolution | AI-assisted lifecycle; drift detection; self-improving skills | Full EAKA Platform — continuous improvement |

#### 14.2 Implementation Roadmap

| **Phase** | **Duration** | **Milestones** | **Success Metrics** |
|---|---|---|---|
| Phase 0 Foundation | 0–3 months | Source connector pilot (3 systems); vector index; basic trust scoring | ≥3 sources indexed; trust scores live |
| Phase 1 Skill MVP | 3–6 months | Skill Registry; 10 pilot skills; governance workflow; eval suite | ≥80% skill eval pass rate |
| Phase 2 KEP Engine | 6–9 months | Knowledge Planner; EKG beta; dynamic MCP discovery; context budgeting | KEP reduces hallucination ≥30% |
| Phase 3 Composition | 9–14 months | Dynamic Skill Composer; multi-MCP orchestration; Microsoft ecosystem join | ≥5-skill compositions working |
| Phase 4 Lifecycle | 14–20 months | AI-assisted lifecycle; drift detection; auto skill drafting; full audit | Skill currency ≥90% across registry |
| Phase 5 Scale | 20–28 months | Enterprise-wide rollout; open platform publication; community governance | ≥1,000 skills; ≥50 MCP servers governed |

#### 14.3 Gap Analysis — Unsolved Research Problems

- **Cross-agent knowledge negotiation** — no standard protocol for agents to agree on conflicting knowledge in multi-agent systems.
- **Real-time graph consistency** — maintaining EKG consistency under concurrent high-frequency updates without locking.
- **Skill transfer learning** — automatically adapting skills from one enterprise domain to another with minimal re-curation.
- **Context compression quality** — lossless compression of complex technical knowledge within tight token budgets.
- **Trust score calibration** — ground-truth labelling of trust scores at enterprise scale remains labour-intensive.
- **Adversarial knowledge injection** — detecting and mitigating attempts to poison enterprise knowledge sources.
- **Cognitive load of governance** — SME review bottlenecks at scale; automation of approval without sacrificing rigour.

### Decision Matrix — Platform Comparison

The following matrix compares leading enterprise AI platforms against the fourteen EAKA capability dimensions. Scores are based on publicly available documentation and analyst assessments as of the publication date.

| **Capability** | **EAKA (this work)** | **Azure AI Foundry** | **AWS Bedrock Agents** | **Google Vertex AI** | **LangChain/LangGraph** | **Cohere Compass** |
|---|---|---|---|---|---|---|
| Knowledge Discovery | ##### | ####I | ###II | ####I | ###II | ####I |
| Knowledge Classification | ##### | ###II | ##III | ###II | ##III | ####I |
| Knowledge Planning (KEP) | ##### | ##III | ##III | ##III | ###II | #IIII |
| Skill Architecture | ##### | ####I | ###II | ###II | ###II | ###II |
| Dynamic Composition | ##### | ###II | ##III | ###II | ####I | ##III |
| Governance | ##### | ##### | ####I | ###II | ##III | ###II |
| Knowledge Graph | ##### | ###II | ##III | ###II | ##III | ###II |
| MCP Integration | ##### | ###II | ##III | ##III | ##### | #IIII |
| Context Engineering | ##### | ###II | ###II | ###II | ###II | ##III |
| AI Knowledge Lifecycle | ##### | ###II | ##III | ###II | ##III | ####I |
| Reliability Framework | ##### | ####I | ####I | ###II | ##III | ###II |
| Vendor Neutrality | ##### | ##III | ##III | ##III | ##### | ##III |

**Legend:** ##### = Full support | ####I = Strong | ###II = Partial | ##III = Limited | #IIII = None

---

**End of Part 3 of 3**

**See also:** [Part 1 of 3](pathname:///archon/architecture/81-eaka-research-study), [Part 2 of 3](pathname:///archon/architecture/parts/33-eaka-research-study-part2)
