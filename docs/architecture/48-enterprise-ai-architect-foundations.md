---
title: "Enterprise AI Architect — Foundations (Part 1 of 2): Role, Landscape, Selection & Integration Patterns"
date_created: 2026-07-09
last_reviewed: 2026-07-23
status: current
doc_type: reference-architecture
domain: architecture
topic_id: enterprise-ai-architect-foundations
supersedes: ["docs/enterprise-architecture/ai-architecture/enterprise-ai-architect-foundations.md"]
source_type: split-migration
covers_version: "as of 2026-07-10"
---

**Part 1 of 2:** This document covers the Enterprise AI Architect role, landscape mapping, build-vs-buy frameworks, model selection, AI integration patterns, agentic AI fundamentals, context management, and token economics.  
See [Part 2 of 2](pathname:///archon/architecture/parts/23-enterprise-ai-architect-foundations-part2.md) for latency planning, integration architecture, data architecture, security, observability, career path, best practices, and antipatterns.

---

# Enterprise AI Architect — Foundations

**Audience:** Architects new to enterprise AI who need to understand the landscape, make informed decisions, and design AI systems that survive contact with production.

**What this guide covers:** Role definition, landscape map, build-vs-buy, model selection, integration patterns, agentic fundamentals, context management, token economics, latency planning, integration architecture, data architecture, security, observability, career path, best practices, and antipatterns.

**What it does NOT duplicate:**  
- MCP implementation → [MCP Deep Guide](pathname:///archon/protocols/mcp-deep-guide.md)
- Agent SDK code → [Agent SDK Production](pathname:///archon/coding-tools/claude-agent-sdk-production.md)
- Model pricing detail → [Models 2026](pathname:///archon/coding-tools/claude-models-2026.md)
- Governance rules → [Governance & Compliance](pathname:///archon/architecture/enterprise-ai-governance-compliance.md)

---

## 1. The Enterprise AI Architect Role

### 1.1 What the Role Is

The Enterprise AI Architect (EA-AI) sits at the intersection of AI/ML technology, enterprise integration, governance, and business strategy. Unlike a data scientist (who optimises models) or an ML engineer (who ships model code), the EA-AI decides:

- Which AI capabilities to adopt and at what layer
- How AI systems integrate with existing enterprise architecture
- What governance, compliance, and risk controls are required
- How to measure and optimise cost, quality, and latency at scale

### 1.2 Core Responsibilities

| Responsibility | Description |
| --------------- | ------------- |
| **AI strategy alignment** | Translate business objectives into AI capability roadmap |
| **Platform selection** | Choose cloud platforms, foundation models, and tooling |
| **Architecture design** | Design integration, data, security, and observability layers |
| **Governance ownership** | Define AI policies, review processes, and compliance controls |
| **Pattern establishment** | Create reusable patterns for teams to follow |
| **Risk assessment** | Identify and mitigate AI-specific risks (bias, safety, reliability) |
| **Cost governance** | Own AI spend planning and optimisation frameworks |
| **Skill enablement** | Coach teams on AI engineering practices and tools |

### 1.3 How EA-AI Differs from Traditional EA

| Dimension | Traditional EA | Enterprise AI Architect |
| ----------- | --------------- | ------------------------ |
| Change cadence | Months/quarters | Days/weeks (model updates) |
| Uncertainty | Deterministic systems | Probabilistic, non-deterministic outputs |
| Vendor lock-in | Infrastructure lock-in | Model lock-in, embedding lock-in |
| Quality measurement | Pass/fail testing | Statistical evaluation, LLM-as-judge |
| Failure modes | Downtime, bugs | Hallucination, bias, safety drift |
| Compliance surface | Data protection | Data + model + output compliance |
| Key skills | Architecture frameworks, integration | Above + prompt engineering, token economics, RAI |

### 1.4 Required Skills

**Technical:**

- Foundation model mechanics (tokens, context window, temperature, top-p)
- Prompt engineering and system design
- RAG architecture (retrieval, chunking, embedding, reranking)
- Agentic systems (orchestration, tool use, state management)
- API integration (REST, streaming, webhooks, event-driven)
- Vector stores and semantic search
- Observability for AI systems

**Architectural:**

- Enterprise integration patterns
- Security architecture (zero-trust, secret management, data classification)
- Cloud platform architecture (AWS, Azure, GCP)
- Cost modelling and FinOps

**Governance:**

- Regulatory frameworks (EU AI Act, NIST AI RMF, ISO 42001)
- Responsible AI principles
- Risk assessment and management
- Audit and documentation requirements

---

## 2. AI Landscape Map

### 2.1 The Four Layers

<!-- TODO(diagram): Replace ASCII box diagram with SVG visual showing 4-layer AI stack -->

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 4: ENTERPRISE AI PRODUCTS                        │
│  GitHub Copilot, Microsoft 365 Copilot, Vertex AI       │
│  Conversation, Microsoft Foundry services               │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: AGENTIC FRAMEWORKS                            │
│  Claude Agent SDK, LangGraph, Agent Framework, CrewAI   │
│  → Orchestration, tool use, multi-agent coordination    │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: ENHANCED MODELS                               │
│  Fine-tuning, RAG, prompt engineering                   │
│  → Domain adaptation, knowledge grounding               │
├─────────────────────────────────────────────────────────┤
│  LAYER 1: FOUNDATION MODELS                             │
│  Claude, GPT-5, Gemini, Llama — raw capabilities        │
│  → Language understanding, reasoning, generation        │
└─────────────────────────────────────────────────────────┘
```

### 2.2 What Each Layer Solves

**Foundation models (Layer 1):** Raw language intelligence. Use when you need flexible general-purpose capability and control. Accessed via API — pay per token.

**Enhanced models (Layer 2):** Domain adaptation and knowledge grounding.

- **Prompt engineering**: Free; no data required; fast iteration. Good for structured tasks.
- **RAG**: Keeps knowledge current without retraining. Gold standard for enterprise knowledge bases.
- **Fine-tuning**: Adapts style, format, or specialised domain. Requires labelled data; adds cost and complexity. Rarely the right first choice.

**Agentic frameworks (Layer 3):** Multi-step autonomous execution. Use when the task requires tool calls, planning, error recovery, or parallelism across sub-tasks.

**Enterprise AI products (Layer 4):** Turnkey solutions for defined use cases. Lower flexibility, faster time-to-value. Use when the product's scope matches your need exactly.

---

## 3. Build vs Buy Framework

### 3.1 Decision Dimensions

| Dimension | Build (API) | Buy (Product) |
| ----------- | ------------ | --------------- |
| Flexibility | Full control | Product scope only |
| Time to value | Weeks–months | Days–weeks |
| Cost structure | Variable (tokens) | Fixed (per user/seat) |
| Control over data flow | Complete | Limited to product controls |
| Maintenance burden | You own it | Vendor owns it |
| Customisation ceiling | Unlimited | Vendor roadmap |

### 3.2 When to Use Foundation Models via API

Use the API (Claude, GPT-5, Gemini) when:

- Your use case is custom and no product fits
- You need full control of prompts, context, and output format
- You require specific data governance (what data is sent, to where)
- You need to compose multiple AI capabilities in a single workflow
- Cost at scale demands granular token optimisation
- You are building a product on top of AI

**Note:** API use does not reduce governance burden. Calling an API directly puts the full governance burden on you — data handling, content filtering, safety controls, audit logging. Products sometimes do more of this for you.

### 3.3 When to Fine-tune

Fine-tune only when all of these are true:

1. You have **1,000+ high-quality labelled examples** of the target behaviour
2. The behaviour cannot be achieved with prompt engineering or RAG alone
3. The **latency** or **cost** of a large model is prohibitive
4. You have MLOps capability to manage model versions and retraining pipelines

Fine-tuning is appropriate for: specialised code generation in a proprietary language, consistent brand voice, domain-specific classification (medical coding, legal categorisation).

### 3.4 When to Build on Agentic Frameworks

Use frameworks (Claude Agent SDK, LangGraph, etc.) when:

- The task requires **multiple sequential steps** with intermediate decisions
- The workflow needs **tool calls** (web search, database query, code execution)
- You need **parallel execution** of sub-tasks (fan-out pattern)
- The system must **recover from errors** mid-workflow
- You need **human-in-the-loop** checkpoints at defined stages

**Note:** Microsoft's AutoGen is now in maintenance mode; its successor is the **Microsoft Agent Framework** (1.0 GA April 2026).

**Warning:** Every agent adds latency, cost, and failure surface. A single well-prompted model call often beats a multi-agent pipeline for simple tasks. Measure before you architect.

### 3.5 When to Use Enterprise AI Platforms

Use platforms (GitHub Copilot, Vertex AI Conversation, Microsoft Foundry (formerly Azure AI Foundry), Amazon Q) when:

- The use case maps exactly to the platform's defined scope (code generation, enterprise chat)
- The governance controls built into the platform satisfy your requirements
- Developer productivity is the primary objective
- You want SSO, RBAC, audit logging, and policy management without building it
- Time-to-value trumps customisation

### 3.6 Decision Matrix

| Scenario | Recommendation |
| ---------- | --------------- |
| Internal knowledge base Q&A | RAG on foundation model API |
| Code generation for developers | GitHub Copilot Enterprise |
| Customer-facing chatbot with custom brand voice | Foundation model API + prompt engineering |
| Automated multi-step research workflow | Agentic framework (Claude Agent SDK) |
| Medical report classification | Fine-tuned model (with MLOps) |
| Complex reasoning over large documents | Claude Fable 5 with extended context |
| High-volume simple classification (100M/day) | Haiku 4.5 or fine-tuned small model |
| Enterprise document summarisation at scale | Batch API with Sonnet 5 |

---

## 4. Model Selection for Enterprise

For the complete vendor-agnostic model landscape, cross-provider capability matrix, open-source model strategy, routing architectures, model registry design, and vendor lock-in prevention patterns, see [Enterprise Multi-Model AI Strategy](pathname:///archon/architecture/enterprise-multi-model-ai-strategy.md). This section covers Claude-specific details and the architectural principles that apply regardless of provider.

### 4.1 Claude Model Landscape (2026)

| Model | Cost (in/out per MTok) | Context | Capability tier | Best for |
| ------- | ---------------------- | --------- | ---------------- | --------- |
| **Claude Fable 5** | $10 / $50 | 1M | Highest | Complex multi-step agents, adversarial robustness, high-stakes decisions |
| **Claude Sonnet 5** | $2 / $10 (intro through Aug 31, 2026; $3 / $15 from Sept 1, 2026) | 1M | High | Most enterprise workloads — balanced cost/capability |
| **Claude Opus 4.8** | $5 / $25 (Fast mode $10 / $50, research preview) | 1M | High (extended thinking) | Deep research, mathematical reasoning, autonomous long-horizon tasks |
| **Claude Sonnet 4.6** | $3 / $15 | 1M | Mid-high | Existing integrations, stable baseline |
| **Claude Haiku 4.5** | $1 / $5 | 200K | Mid | High-volume routing, classification, triage, simple extraction |

All 1M-context models support up to 128K output tokens.

See [Models 2026](pathname:///archon/coding-tools/claude-models-2026.md) for the complete capability and pricing matrix.

### 4.1a Cross-Vendor Landscape Summary (2026)

Enterprises should evaluate Claude alongside other providers. The table below maps the competitive landscape; detailed analysis is in the [Multi-Model Strategy Guide](pathname:///archon/architecture/enterprise-multi-model-ai-strategy.md).

| Provider | Top Model | Context | Relative Strength | Self-host? |
| --- | --- | --- | --- | --- |
| **Anthropic** | Claude Fable 5 | 1M | Instruction following, safety, long docs, tool use | No |
| **OpenAI** | GPT-4o / o3 | 128K / 200K | Ecosystem breadth, multimodal, coding | Azure only |
| **Google** | Gemini 2.5 Pro | 1M | Multimodal, video, ultra-long context, GCP integration | Vertex only |
| **Amazon** | Nova Pro (Bedrock) | 300K | AWS-native, cost leadership, multimodal | No |
| **Meta (OSS)** | Llama 3.3 70B | 128K | Full data control, air-gap, no per-token cost | Yes |
| **Mistral (OSS)** | Mistral Large 2 | 128K | EU data sovereignty, multilingual, Apache-friendly | Yes |
| **DeepSeek (OSS)** | DeepSeek-R1 | 128K | Reasoning, math, cost-efficient self-hosting | Yes (check regs) |

**Key principle:** No single model leads on all dimensions. Multi-model routing extracts the best capability per task type while controlling cost.

### 4.2 Use-Case Fit (within Claude Tier)

<!-- TODO(diagram): Replace ASCII complexity/cost matrix with SVG grid -->

```
COMPLEXITY OF TASK
         High │ Fable 5          │ Fable 5
              │ (high volume)    │ (low volume)
              ├──────────────────┤
              │ Sonnet 5         │ Opus 4.8
              │ (production)     │ (extended thinking)
         Low  │ Haiku 4.5        │ Sonnet 5
              └──────────────────┘
              Low          High
              COST SENSITIVITY
```

For cross-provider task-to-model mapping, see [Dynamic Model Selection](pathname:///archon/architecture/enterprise-multi-model-ai-strategy.md).

### 4.3 Multi-Model Strategies

**Routing:** Use a classifier (Haiku 4.5) to score task complexity, then route to Haiku (simple) or Sonnet 5 (complex) or Fable 5 (critical). See [Cost Optimization Routing Pattern](pathname:///archon/architecture/enterprise-ai-architecture-patterns.md).

**Fallback:** Primary model → timeout/error → fallback model. Never let a single model be a hard dependency.

**Cascade:** Haiku → check output quality → if below threshold → Sonnet 5 → check → if below threshold → Fable 5. Optimises cost while guaranteeing quality floor.

**Cross-vendor fallback:** Primary provider down → AI gateway routes to secondary provider (e.g., GPT-4o as Claude Sonnet 5 fallback). Configure in LiteLLM or Kong AI Gateway router config. Test monthly — untested fallbacks are not reliable fallbacks.

For full routing architecture patterns (classifier routing, confidence cascade, latency-aware, risk-aware), see [Model Routing Architecture](pathname:///archon/architecture/enterprise-multi-model-ai-strategy.md).

### 4.4 Vendor Lock-in Risk and Mitigation

Lock-in is real. Embedding models, fine-tuned models, and proprietary APIs all create switching costs. Plan your exit strategy before you start.

| Risk | Mitigation |
| ------ | ----------- |
| API schema dependency | Wrap calls in an abstraction layer (AI gateway, internal SDK); use OpenAI-compatible schema as the common contract |
| Embedding lock-in | Store raw text alongside embeddings; re-embed on switch |
| Fine-tune lock-in | Keep labelled data; document training process; use open-source base models where possible |
| Feature dependency | Track which provider-specific features (e.g., extended thinking, Realtime API) you depend on; isolate behind feature flags |
| Pricing changes | Monitor costs; have alternative model tested and ready; run quarterly cross-vendor benchmarks |

**Multi-vendor strategy:** Maintain tested integration with at least two model providers. Test quarterly.

For the complete vendor lock-in prevention architecture — including LiteLLM configuration, prompt portability patterns, model registry design, and abstraction layer design — see [Vendor Lock-in Prevention](pathname:///archon/architecture/enterprise-multi-model-ai-strategy.md).

---

## 5. AI Integration Patterns

### 5.1 Augmentation

AI enhances a human workflow — the human remains in the loop, AI adds speed or quality.

**Examples:** Draft email → human edits → send. Code suggestion → developer accepts/rejects. Document summary → analyst reviews.

**Architecture:** Human-initiated request → AI call → AI response presented to human → human action.

**When to use:** High-stakes outputs, regulated domains, where errors are expensive. Low AI latency tolerance. Users are the quality gate.

### 5.2 Automation

AI replaces a manual step entirely — no human in the flow for the happy path, but exceptions escalate to human.

**Examples:** Automated invoice classification, IT ticket categorisation, email routing.

**Architecture:** Trigger → AI call → confidence check → if high confidence: auto-action; if low confidence: escalate to human queue.

**When to use:** High-volume, repetitive, well-defined tasks. Error rate is measurable and acceptable. Exceptions are handleable.

### 5.3 Orchestration

AI coordinates multiple systems, tools, and sub-tasks to complete a complex goal autonomously.

**Examples:** Research agent that searches the web, reads documents, synthesises, and emails a report. DevOps agent that diagnoses an alert, queries logs, proposes a fix, and opens a PR.

**Architecture:** Goal → orchestrator (LLM with tool use) → parallel/sequential tool calls → sub-agent calls → result aggregation → output.

**When to use:** Multi-step workflows, tool-heavy tasks, where the sequence is variable and model-decided.

---

## 6. Agentic AI Architecture Fundamentals

### 6.1 Single Agent vs Multi-Agent Systems

| Dimension | Single Agent | Multi-Agent |
| ----------- | ------------- | ------------- |
| Complexity | Lower | Higher |
| Parallelism | Limited | Full fan-out possible |
| Context management | One context window | Distributed context |
| Failure surface | One point | Multiple coordination points |
| Cost | Lower | Higher (multiple model calls) |
| Best for | Focused, sequential tasks | Parallel, specialised sub-tasks |

**Decision rule:** Start with a single agent. Add agents when (a) parallelism is genuinely needed, (b) sub-tasks require different specialisation, or (c) context window limits require splitting.

### 6.2 Orchestrator-Worker Pattern

<!-- TODO(diagram): Replace ASCII agent orchestrator diagram with SVG -->

```
                    ┌─────────────┐
                    │ ORCHESTRATOR│ ← Planner, router, goal holder
                    │  (Fable 5) │
                    └──────┬──────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ WORKER A │ │ WORKER B │ │ WORKER C │
        │ (Haiku)  │ │(Sonnet 5)│ │ (Haiku)  │
        │ Search   │ │ Synthesis│ │ Format   │
        └──────────┘ └──────────┘ └──────────┘
```

The orchestrator holds the overall goal and plan. Workers execute specific sub-tasks. Workers do not know about each other — communication flows through the orchestrator.

**Key design decisions:**

- Orchestrator model should be the most capable (Fable 5 or Sonnet 5) — it makes decisions
- Workers can be cheaper models (Haiku) for well-defined sub-tasks
- Pass only required context to each worker (not the full orchestrator context)
- Workers must return structured output the orchestrator can parse reliably

### 6.3 Hub-and-Spoke vs Peer-to-Peer

**Hub-and-spoke (recommended):** All agents communicate through an orchestrator. Easier to debug, monitor, and govern. Single point of coordination visibility.

**Peer-to-peer:** Agents communicate directly. Higher throughput potential, but:

- Hard to trace failures
- Difficult to monitor cost
- Governance gaps (who approved agent A calling agent B directly?)
- Avoid for enterprise deployments until you have mature agent observability

### 6.4 When to Go Agentic — and When NOT To

**Go agentic when:**

- Task requires more than 2–3 sequential decisions
- External tool calls are required (search, DB, API)
- Parallelism of independent sub-tasks provides meaningful speedup
- Task is long-horizon (minutes to hours, not seconds)

**Do NOT go agentic when:**

- A single well-crafted prompt produces acceptable output
- Latency SLA is < 2 seconds (single model call only)
- The workflow is fully deterministic (use code, not AI)
- Error recovery from agent failure is prohibitively expensive

---

## 7. Context Management at Enterprise Scale

### 7.1 The CALM Framework

CALM (Conversation, Augmentation, Long-term memory, Multi-turn) is a structured approach to managing context across complex AI interactions.

**C — Conversation context:** What is in the current conversation. Managed within the context window. Finite and expensive.

**A — Augmentation:** Retrieved context injected at inference time (RAG). Not stored in the model — retrieved from external knowledge. Enables dynamic, up-to-date knowledge without retraining.

**L — Long-term memory:** Persisted across sessions. Stored externally (vector DB, key-value store) and retrieved selectively. Enables personalisation, continuity, and accumulated knowledge.

**M — Multi-turn:** Strategies for managing long conversations. Context compression, summarisation, selective retention. Keep the most relevant recent turns plus key facts from earlier turns.

### 7.2 RAG Architecture

<!-- TODO(diagram): Replace ASCII RAG flow with SVG pipeline diagram -->

```
Query → [Embedder] → Query vector
                           ↓
                    [Vector Store] ← Retrieve top-k chunks
                           ↓
                   [Reranker] ← Score by relevance
                           ↓
              [Generator (Claude)] ← Prompt = query + top chunks
                           ↓
                       Response
```

**Naive RAG:** Query → retrieve → generate. Simple, fast, often good enough for structured knowledge bases.

**Advanced RAG techniques:**

| Technique | What it solves |
| ----------- | --------------- |
| **HyDE** (Hypothetical Document Embeddings) | Query-document mismatch — generate a hypothetical answer, embed it, retrieve against that |
| **Parent-child chunking** | Context loss — small chunks for retrieval precision, parent chunks sent to generator for full context |
| **Metadata filtering** | Irrelevant retrieval — filter by date, source, category before semantic search |
| **Hybrid search** | Keyword + semantic — BM25 for exact match, vector for semantic match, combine with RRF |
| **Self-query retrieval** | Structured knowledge — LLM generates filter conditions from natural language |
| **Recursive retrieval** | Multi-hop reasoning — retrieve → read → identify next retrieval need → retrieve again |

### 7.3 Prompt Caching Strategy for Cost Reduction

Claude supports prompt caching — frequently used prompt prefixes (system prompts, tool definitions, large document preambles) are cached server-side, reducing both cost and latency.

**Cache what:**

- System prompts (especially long ones with full instructions)
- Tool definitions
- Frequently referenced documents (company policies, API specs)
- Few-shot examples

**Cache design rules:**

- Place cacheable content at the start of the prompt
- Cache blocks must be > 1,024 tokens to be eligible
- Cache lifetime: 5 minutes by default (refreshed on each cache hit); a 1-hour cache tier is also available at a higher write price (2× base input, vs 1.25× for the 5-minute tier)
- Cached tokens typically cost ~10% of uncached input tokens

**Expected savings:** For a system prompt of 10K tokens reused 100 times per day: approximately 90% reduction in system prompt input cost.

---

## 8. Token Economics for Enterprise Architects

### 8.1 Token Budgeting

Token budgeting is the AI equivalent of memory allocation. Unlike memory, tokens directly translate to cost and latency.

**Budget components:**

```
Total tokens = System prompt + Few-shot examples + User message
             + Retrieved context (RAG) + Conversation history
             + Tool definitions + Tool results
             + Output tokens
```

**Rule of thumb allocations for a typical enterprise agent call:**

- System prompt: 500–2,000 tokens (cache it)
- Retrieved context (RAG): 2,000–8,000 tokens
- User message: 100–500 tokens
- Conversation history: 0–4,000 tokens (compress or summarise)
- Output: 500–2,000 tokens (set `max_tokens` explicitly)

**Extended thinking:** Claude Fable 5, Opus 4.8, and Sonnet 5 use **adaptive thinking** — a fixed `budget_tokens` value is rejected (HTTP 400) on these models. Enable it with `thinking: {type: "adaptive"}` (thinking is always-on for Fable 5) and control depth with `output_config.effort` (`low` / `medium` / `high` / `max`). Thinking tokens are billed but enable significantly better complex reasoning; note that Fable 5 never returns the raw chain of thought — responses carry summarized or omitted thinking blocks.

### 8.2 Cost Attribution per Team/Product

Implement cost attribution from day one. Without it, AI costs become invisible until they become a crisis.

**Attribution model:**

```python
# Tag every API call with the metadata body field
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    metadata={"user_id": "product-search:recommendation-engine:production"},
    messages=[...],
)
```

The API exposes a single `metadata.user_id` request field — encode team/product/environment into it. Combine with per-team API keys and workspaces, plus the Console usage reports, for full attribution.

Track: tokens consumed (input/output/cache), model version, team, product, environment, request ID.

Build cost dashboards: daily spend by team, cost per successful task, cache hit rate, output-to-input ratio.

### 8.3 Batch Processing for Non-Real-Time Workloads

Claude's Batch API processes requests asynchronously at significantly reduced cost. Use it for:

- Document classification at scale
- Bulk summarisation
- Periodic report generation
- Dataset annotation
- Overnight analysis jobs

**Cost reduction:** Batch API typically costs 50% of synchronous API rates for the same model.

**Implementation pattern:**

```python
# Submit batch
batch = client.messages.batches.create(
    requests=[{"custom_id": f"doc-{i}", "params": {...}} for i, doc in enumerate(documents)]
)

# Poll or webhook when complete
# Process results
```

### 8.4 Model Routing for Cost Optimisation

A routing layer classifies incoming requests and sends them to the most cost-effective model that can handle the task.

<!-- TODO(diagram): Replace ASCII routing flow diagram with SVG -->

```
Incoming request
       ↓
[Complexity Classifier] (Haiku — cheap, fast)
       ↓
  ┌────┴────┐
  │         │
Simple   Complex
  │         │
Haiku    Sonnet 5
(~$0.001) (~$0.03)
              │
         Very complex
              │
           Fable 5
          (~$0.20+)
```

**Classifier features:** Token count, domain keywords, structural complexity, presence of code, multi-step indicators.

### 8.5 AI FinOps as an Enterprise Discipline

AI costs behave differently from traditional software costs — they scale with *usage intensity* rather than instance count, and a single poorly-scoped prompt can cost 100× more than an optimised one. FinOps Foundation formalised AI FinOps as a discipline in 2025; the framework identifies nine distinct cost buckets that enterprise architects must track separately.

**The Nine AI Cost Buckets (FinOps Foundation)**

| Bucket | What drives cost | Typical share of AI feature spend |
| --- | --- | --- |
| **LLM inference — synchronous** | Tokens × price/token | 20–35% |
| **LLM inference — batch** | Same, at 50% discount | 5–10% |
| **Embedding generation** | Tokens × embedding model price | 3–7% |
| **RAG infrastructure** | Vector DB, indexing compute, retrieval API calls | 15–25% |
| **Agent orchestration compute** | Execution time for agent loops, tool calls, re-tries | 10–20% |
| **Fine-tuning / RLHF** | GPU hours × hourly rate | 2–5% (amortised) |
| **Storage** | Vector indices, model artefacts, eval datasets | 3–8% |
| **Evaluation infrastructure** | LLM-as-judge calls, eval harness runs | 2–5% |
| **Observability / tracing** | OTel ingest, trace storage, dashboard tools | 2–4% |

**Key insight:** RAG infrastructure plus agent orchestration compute typically account for **40–60% of total AI feature spend** — yet most cost visibility dashboards only track the LLM inference line item. Incomplete visibility leads to under-counting cost by 2–3 times.

**Neocloud and Cloud Commitment Strategy**

Hyperscalers (AWS, Azure, GCP) require **3–5 year capacity commitments** for frontier GPU allocations (H100/H200/B200 cluster reservations). Neoclouds (CoreWeave, Lambda Labs, Voltage Park, Oracle Cloud GPU) offer shorter-term commitments (6–18 months) with competitive pricing but fewer managed services.

| Procurement model | Commitment length | Cost saving vs on-demand | When to use |
| --- | --- | --- | --- |
| **Hyperscaler reserved** | 1–3 year | 30–50% | Stable production workloads with predictable token volume |
| **Hyperscaler Savings Plan** | 1–3 year | 20–40% | Mixed workloads, some flexibility on model/region |
| **Neocloud committed** | 6–18 months | 40–60% vs hyperscaler | High GPU-hour workloads (training, batch inference); accept ops overhead |
| **On-demand / API** | None | Baseline | Volatile, pilot, or prototype workloads |

**Enterprise FinOps Implementation**

1. **Tag every AI call** with `project`, `team`, `use-case`, and `environment` at the AI gateway layer — before the call reaches the provider. This enables showback and chargeback without touching individual application code.

2. **Set per-team budgets** with alerting at 70% and 90% thresholds. Alert goes to the team lead, not just the platform team. Soft budget caps (alerting only) are more effective than hard cut-offs that create surprise outages.

3. **Establish cost-per-task baselines** for your top 10 use cases (e.g., document summarisation = $0.003 per document, customer intent classification = $0.0008 per call). Drift above 20% is a signal of prompt bloat or model version regression.

4. **Model tier governance:** Require architectural justification to use a Tier-1 model (Fable 5, Opus 4.8) for tasks that benchmark equivalently on Tier-3 (Haiku 4.5). Save 30–95% per call on routine tasks.

5. **Optimise RAG economics separately:** Vector DB retrieval cost, indexing frequency, and chunk strategy are often the fastest levers for cost reduction — and independent of model choice.

```python
# Example: per-call cost attribution tag at the AI gateway layer
headers = {
    "X-Cost-Project": project_id,
    "X-Cost-Team": team_id,
    "X-Cost-UseCase": use_case_slug,
    "X-Cost-Env": environment,    # prod / staging / dev
}
# Gateway reads these tags and writes to cost ledger before forwarding to provider
```

**FinOps maturity stages for AI:**

- **Crawl:** Track total LLM spend by project. Establish per-task cost baselines.
- **Walk:** Tag all calls; per-team showback; identify top-10 cost drivers; model routing implemented.
- **Run:** Real-time cost dashboards; anomaly alerting; automated routing; chargeback to BU P&Ls; FinOps reviews as part of AI CoE governance cadence.
