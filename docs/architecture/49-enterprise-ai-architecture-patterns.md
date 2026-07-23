---
title: "Enterprise AI Architecture Patterns"
doc_type: reference-architecture
domain: architecture
status: current
canonical: true
topic_id: enterprise-ai-architecture-patterns
maturity: practitioner
personas: [architect, senior-engineer, platform-engineer]
last_reviewed: 2026-07-19
covers_version: "as of July 2026"
supersedes:
  - docs/enterprise-architecture/ai-architecture/enterprise-ai-architecture-patterns.md
tags:
  - enterprise-architecture
  - ai-architecture
  - patterns
  - rag
  - multi-agent
  - guardrails
sources: []
---

# Enterprise AI Architecture Patterns

**Audience:** Architects and senior engineers designing production AI systems.

**Purpose:** Canonical reference for 15 enterprise AI patterns. Each pattern includes: what problem it solves, architecture diagram, key components, implementation guidance, evaluation approach, best practices, and antipatterns.

---

## Pattern Catalog Overview

| # | Pattern | Problem | Complexity |
| --- | --------- | --------- | ------------ |
| 1 | Retrieval-Augmented Generation (RAG) | Knowledge grounding, factual accuracy | Medium |
| 2 | Agentic RAG | Dynamic retrieval decisions | High |
| 3 | Multi-Agent Orchestration | Parallel sub-tasks, specialisation | High |
| 4 | Parallel Fan-Out | Throughput, map-reduce AI workloads | Medium |
| 5 | AI Gateway | Centralised AI control plane | Medium |
| 6 | Semantic Caching | Cost reduction for similar queries | Medium |
| 7 | LLM-as-Judge | AI output quality evaluation | Medium |
| 8 | Human-in-the-Loop (HITL) | High-stakes action approval | Low |
| 9 | Guardrail Pipeline | Safety, compliance, content control | Medium |
| 10 | Explainability Pipeline | Audit trails, compliance, transparency | Medium |
| 11 | Cost Optimisation Routing | Token cost reduction | Medium |
| 12 | Stress Testing | Performance validation | Medium |
| 13 | Evaluation Harness | Regression and A/B testing | High |
| 14 | Blue-Green AI Deployment | Safe model/prompt rollout | Medium |
| 15 | CALM Context Management | Enterprise-scale context strategy | High |

---

## 1. Retrieval-Augmented Generation (RAG)

### Problem

Foundation models have a knowledge cutoff and no access to your enterprise data. Without grounding, they hallucinate or refuse to answer. Fine-tuning is expensive and quickly stale. RAG provides current, authoritative knowledge without retraining.

### Naive RAG → Advanced RAG

**Naive RAG:** Fixed chunk size → embed → retrieve top-k → generate. Works for structured, homogeneous corpora. Fails for:

- Long, complex documents (context loss at chunk boundaries)
- Questions requiring multi-hop reasoning
- Mixed content types (tables, code, prose)

**Advanced RAG techniques:**

**HyDE (Hypothetical Document Embeddings):** Generate a hypothetical answer to the query, embed the hypothetical answer, retrieve against that embedding. Bridges the query–document embedding gap.

**Parent-Child Chunking:** Index small child chunks for precision retrieval; when a child chunk is retrieved, return its full parent chunk to the generator for complete context.

**Hybrid Search:** Combine BM25 (keyword) and vector (semantic) search. Use Reciprocal Rank Fusion (RRF) to merge results.

**Metadata Filtering:** Restrict vector search to chunks matching structured filters (date range, source, category, security classification).

### Best Practices

- Use a reranker after vector search — precision jumps 15–30% with minimal latency cost
- Chunk at semantic boundaries (paragraph, section) not fixed character counts
- Store chunk metadata (source URL, date, author) for filtering and citation
- Test with adversarial queries — questions that should return "I don't know"
- Monitor retrieval quality in production — track when no relevant chunks are found

---

## 2. Agentic RAG

### Problem

Standard RAG uses a fixed retrieval strategy for every query. Some queries need no retrieval (the model knows the answer). Others need multiple retrieval rounds (multi-hop reasoning). Agentic RAG lets the model decide when and what to retrieve.

### Implementation Pattern

```
User Query
    ↓
[ROUTING AGENT]
    ├─ Direct Answer (model knows)
    └─ [Retrieval Tool]
         ├─ [Vector Store]
         ├─ [Read Results]
         ├─ Need more? → [Retrieval Tool] again
         └─ Synthesise Answer
```

### Key Components

**Router/Planner:** Decides the retrieval strategy. Should be a capable model (Sonnet 5 or Fable 5) — this decision is where quality matters most.

**Retrieval tool:** Exposed as a tool call. The agent invokes it with a query string; the tool returns top chunks.

**Self-reflection:** After reading retrieved chunks, the agent assesses whether the information is sufficient to answer, then either answers or retrieves more.

### Antipatterns

- **Unbounded retrieval loops:** Implement a max-retrieval-steps limit (e.g., 5) to prevent infinite loops
- **Retrieval without budget tracking:** Each retrieval adds tokens and cost; track and cap
- **Single retrieval tool for all sources:** Different sources have different schemas; specialise tools

---

## 3. Multi-Agent Orchestration

### Problem

Some tasks are too large for a single agent's context window, benefit from parallelism across specialised agents, or require different model capabilities for different sub-tasks.

### Task Decomposition Strategies

**Sequential decomposition:** Tasks must happen in order (A → B → C). Use when each step depends on prior output.

**Parallel decomposition:** Tasks are independent. Run all concurrently. Use when sub-tasks do not share state.

**Hierarchical decomposition:** Orchestrator spawns sub-orchestrators, each with their own workers. Use for very complex tasks requiring 3+ levels of planning.

**Dynamic decomposition:** Orchestrator decides task breakdown at runtime based on input. Use when task structure is not known in advance (agentic research, open-ended coding).

### Result Aggregation

| Pattern | When to use |
| --------- | ------------- |
| **Merge all results** | Sub-tasks produce complementary outputs (sections of a report) |
| **Vote/consensus** | Run same task N times; take majority answer (increases reliability, 3× cost) |
| **Best-of-N** | Run N times; judge selects best output (LLM-as-judge or rule-based) |
| **Critique-revise** | Worker generates; critic evaluates; worker revises |

### Best Practices

- Orchestrator model should be the most capable (Fable 5 or Sonnet 5) — it holds the plan
- Workers can be cheaper (Haiku) for well-defined sub-tasks
- Pass minimal context to each worker — not the full orchestrator context
- Implement a total task timeout (not just per-step timeout)
- Log the full agent trace (orchestrator plan + worker calls + results)
- Design worker output schemas first; orchestrator aggregation logic follows from output structure

---

## 4. Parallel Fan-Out

### Problem

A large batch of independent AI tasks needs to complete in acceptable time. Sequential processing is too slow; a map-reduce approach is needed.

### Concurrency Limits and Rate Limit Management

**Rate limit types:**

- **Requests per minute (RPM):** Number of API calls per minute
- **Tokens per minute (TPM):** Total tokens (input + output) per minute
- **Tokens per day (TPD):** Some tiers have daily limits

**Safe concurrency formula:**

```
Max concurrent = min(
    your_RPM_limit / average_call_duration_seconds,
    your_TPM_limit / average_tokens_per_call / 60
)
```

Start at 10, measure 429 rate, adjust upward until 429s exceed 0.5%.

**Exponential backoff pattern:** Use full jitter, not equal or additive jitter. This prevents synchronized retry waves.

### Result Validation After Fan-Out

Not all AI outputs are valid. Validate before aggregation to ensure quality thresholds are met.

---

## 5. AI Gateway Pattern

### Problem

Multiple teams, services, and applications each implement their own AI integration — with no unified auth, no centralised cost tracking, no rate limiting, and no ability to swap models. The AI Gateway centralises all AI traffic through a single control plane.

### Gateway Capabilities

| Capability | Business value |
| ----------- | --------------- |
| **Unified authentication** | One API key per team; gateway holds provider keys |
| **Rate limiting per team** | Prevent one team from consuming all capacity |
| **Cost tracking** | Token usage attributed per team, product, environment |
| **Model routing** | Route by complexity, cost threshold, or A/B test |
| **Semantic caching** | Reduce duplicate calls; cut costs 20–40% |
| **Fallback logic** | Provider A fails → Provider B automatically |
| **Request logging** | Centralised audit log for all AI calls |
| **Prompt injection detection** | WAF-style rules on all inbound prompts |

### Implementation Options

**Kong AI Gateway:** Open-source plugin ecosystem. AI proxy plugin for Claude, OpenAI, Cohere. Rate limiting, caching, logging plugins available.

**AWS API Gateway + Lambda:** Serverless AI gateway for AWS-native shops. Lambda handles routing and auth; API Gateway handles TLS and rate limiting.

**Custom (FastAPI/Express):** Full control. Higher maintenance burden. Appropriate when you need capabilities not available in off-the-shelf gateways.

---

## 6. Semantic Caching

### Problem

Many AI applications receive near-identical queries repeatedly (FAQ bots, search assistants, document Q&A). Calling the model for every query is wasteful when a cached response would serve equally well.

### Similarity Threshold Configuration

| Threshold | Effect |
|-----------|--------|
| 0.95+ | Very conservative — only near-identical queries hit cache |
| 0.90–0.94 | Standard setting for factual Q&A |
| 0.85–0.89 | Aggressive — risk of returning wrong cached answer |

**Recommendation:** Start at 0.92. Evaluate cache hit quality manually (sample 20 cache hits/day). Adjust threshold based on false-positive rate.

**Never cache:** Queries involving personal data, real-time information, or user-specific context.

### Cost Impact Analysis

Typical semantic cache impact for a high-traffic Q&A system:

```
Without cache: 100,000 queries/day × $0.030 avg = $3,000/day
Cache hit rate: 40%
With cache:    60,000 API calls/day × $0.030 = $1,800/day
               + 40,000 vector lookups × $0.0001 = $4/day
Net saving: $1,196/day — ~40% cost reduction
```

---

## 7. LLM-as-Judge Evaluation

### Problem

Evaluating AI output quality at scale is expensive if done by humans and impossible to do manually for every output. Using a capable AI model to judge another model's output provides scalable quality measurement.

### Avoiding Judge Bias

LLM judges exhibit biases:

- **Position bias:** Prefers the first option when comparing two responses
- **Verbosity bias:** Prefers longer, more elaborate responses regardless of accuracy
- **Self-preference bias:** Claude tends to prefer Claude-generated text

**Mitigations:**

- **Blind evaluation:** Remove model name from input; judge doesn't know which model generated the output
- **Swap positions:** If comparing A vs B, run twice with positions swapped; count only agreements
- **Reference anchor:** Provide a human-written reference answer; score against it, not just A vs B
- **Chain-of-thought scoring:** Require the judge to reason before scoring (reduces snap judgements)
- **Ensemble judges:** Use multiple judge models; take average score

---

## 8. Human-in-the-Loop (HITL) Gates

### Problem

AI agents make mistakes. For high-stakes, irreversible, or regulated actions, the cost of an unreviewed AI error exceeds the benefit of full automation.

### When to Insert HITL

| Trigger | Example |
| --------- | --------- |
| **High-stakes action** | Send mass email, delete records, execute financial transaction |
| **Low confidence output** | Model's self-assessed confidence &lt; 0.75 |
| **Sensitive domain** | Medical, legal, financial advice to end users |
| **Novel scenario** | Input type not seen in training data; low retrieval relevance |
| **Irreversible action** | Any action that cannot be undone (publish, submit, deploy) |
| **Regulatory requirement** | Actions in regulated processes requiring documented human approval |

### Escalation Policies

```
Tier 1 (auto): Confidence > 0.90, known action type → execute
Tier 2 (peer review): Confidence 0.75–0.90 → route to team queue
Tier 3 (senior review): Confidence < 0.75 or high-stakes domain → route to senior reviewer
Tier 4 (no-AI): Edge cases; human handles entirely without AI assistance
```

---

## 9. Guardrail Pipeline

### Problem

Raw model output can contain: harmful content, PII, off-topic responses, competitor mentions, regulatory violations, prompt leaks. A guardrail pipeline validates both inputs and outputs before they reach users or downstream systems.

### Layered Defense

**Layer 1 — System prompt guardrails:** Instruct the model on what NOT to do. First line of defence; zero added latency.

**Layer 2 — Input/output classifiers:** Lightweight models (Haiku or small fine-tuned classifiers) that check content before and after the main call. Add 50–200ms latency.

**Layer 3 — Post-processing rules:** Deterministic checks (regex, schema validation). Zero AI cost; add &lt;10ms latency.

**Layer 4 — AI-based output review:** Full LLM evaluation of output quality and safety. Use for high-stakes domains; adds 500–1,500ms.

---

## 10. Explainability Pipeline

### Problem

Regulated industries (finance, healthcare, HR) require explanations for AI-assisted decisions. Auditors need to trace how conclusions were reached. End users may have a right to explanation (GDPR Article 22).

### Capturing Chain-of-Thought for Audits

Store reasoning traces separately from answers. Use thinking blocks (adaptive) to capture model reasoning while respecting token budgets. Maintain an audit lake with:
- Decision ID and timestamp
- Model version and parameters
- Retrieved context (anonymised)
- Reasoning trace (thinking blocks)
- Human override records

---

## Trade-Offs: Pattern Selection Tradeoffs

### RAG vs. Fine-Tuning

| Dimension | RAG | Fine-Tuning |
|-----------|-----|------------|
| **Update latency** | Minutes | Hours/days |
| **Knowledge freshness** | Current | Stale after training |
| **Cost** | Inference cost only | Training + inference |
| **Explainability** | High (retrieved chunks cited) | Low (weights opaque) |
| **When to choose** | Enterprise data, frequent updates | Specialized behavior/style |

### Multi-Agent vs. Single-Agent with Tools

| Dimension | Multi-Agent | Single-Agent + Tools |
|-----------|------------|---------------------|
| **Context efficiency** | High (each agent gets clean window) | Low (all tools in context) |
| **Token cost** | 4–15× higher | Baseline |
| **Failure isolation** | Good (one agent failure contained) | Poor (cascading failure) |
| **Latency** | Longer (orchestration overhead) | Shorter |
| **Auditability** | Strong (clear delegation chain) | Weaker (monolithic decision) |
| **When to choose** | Complex tasks, high stakes | Simple, well-defined tasks |

---

## Further Reading

- [Agentic AI Reliability, Observability & Governance](43-agentic-ai-reliability-observability-governance.md)
- [AI Harness Architecture & Orchestration](pathname:///archon/architecture/ai-harness-architecture-orchestration)
- [Multi-Agent Topology Patterns](59-multi-agent-topology-patterns.md)

---

## Related

- [LLM-as-Judge Evaluation](43-agentic-ai-reliability-observability-governance.md)
- [Guardrail Architecture](agentic-ai-security-guardrails.md)

---

## Sources

- RAGAS: Automated Evaluation Framework for Retrieval-Augmented Generation Systems (Zetian et al.)
- OpenAI Agents SDK documentation
- Anthropic Agent Engineering guides
- Kong API Gateway documentation
- Semantic Caching research (Anthropic 2024)
