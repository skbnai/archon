---
title: "AI Cost Implementation: Model Routing & Semantic Caching"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ai-cost-implementation-guide-2026
maturity: practitioner
personas:
  - platform-engineer
  - finops-lead
  - ai-architect
last_reviewed: 2026-07-19
covers_version: ""
supersedes:
  - docs/ai-economics/AI_Cost_Implementation_Guide_2026.md
tags:
  - ai-economics
  - cost-optimization
  - token-management
  - model-routing
  - semantic-caching
sources: []
---

# AI Cost Implementation: Model Routing & Semantic Caching

## Why This Matters

AI inference costs scale linearly with token volume and model complexity. Without proactive cost architecture, agentic workloads can become economically untenable. This guide covers the tactical cost-control layer: complexity-based model routing (select the cheapest model capable of handling each request), semantic caching (eliminate duplicate LLM calls via vector similarity), and the gateway architecture that sits at the entry point to all AI consumption.

This is **part 1 of 3**. See companion parts:
- **Part 2:** [AI Cost Implementation: Budget Governance, FinOps & ROI](54-ai-cost-implementation-guide-2026-budget-finops-roi-measurement.md)
- **Part 3:** [AI Cost Implementation: Anti-Pattern Fixes & Deployment](55-ai-cost-implementation-guide-2026-anti-patterns-deployment-playbook.md)

---

## Model Routing: Tier Decision Framework

Route every request through a lightweight complexity classifier before dispatching to the LLM:

| **Tier** | **Models** | **Cost/1K tokens** | **Use Cases** |
|---|---|---|---|
| **Nano** | Claude Haiku, Gemini Flash, GPT-4o-mini | $0.00025–$0.0006 | Autocomplete, classification, formatting, syntax Q&A |
| **Mid** | Claude Sonnet, GPT-4o | $0.003–$0.005 | Chat, debugging, code review, multi-file context |
| **Frontier** | Claude Opus, o3 | $0.015–$0.075 | Architecture design, complex reasoning, security analysis |

**Cost reduction:** RouteLLM (Stanford) demonstrates 50% cost reduction at 95% quality parity by using a lightweight Sentence-BERT classifier (~80 MB, &lt;10 ms inference) to route trivial requests to nano models.

### Complexity Classifier

A simple in-process classifier using cosine similarity against anchor embeddings (trivial vs. complex reference prompts):

```python
from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")

_TRIVIAL_ANCHORS = [
    "What is the syntax for a for loop in Python?",
    "Format this JSON: {key: value}",
    "What does this error message mean?",
]

_COMPLEX_ANCHORS = [
    "Design a microservices architecture for a payment system",
    "Analyze security vulnerabilities in this authentication flow",
    "Refactor this class to follow SOLID principles",
]

def classify(prompt: str) -> float:
    """Returns complexity score 0.0 (trivial) → 1.0 (complex)."""
    emb = _model.encode([prompt], normalize_embeddings=True)[0]
    trivial_sim = float(np.max(emb @ _TRIVIAL_EMBS.T))
    complex_sim = float(np.max(emb @ _COMPLEX_EMBS.T))
    base_score = (complex_sim - trivial_sim + 1) / 2
    length_boost = min(len(prompt) / 2000, 0.15)
    code_boost = 0.10 if "```" in prompt else 0.0
    return min(base_score + length_boost + code_boost, 1.0)
```

---

## Semantic Caching

Embed user queries, find similar past queries via vector search (cosine similarity threshold 0.92), and return cached response — zero LLM cost. **Production impact: 30–60% LLM call reduction.**

| **Content Type** | **TTL** | **Threshold** | **Reason** |
|---|---|---|---|
| Syntax Q&A (stable knowledge) | 30 days | 0.93 | High repetition, stable answers |
| Framework docs questions | 7 days | 0.92 | Docs change slowly |
| Architecture patterns | 24 hours | 0.90 | Moderate reuse |
| Code review (generic) | 4 hours | 0.93 | Avoid specific PR context |
| Security guidance | 1 hour | 0.95 | Must be current |
| **PII-containing prompts** | **Never** | **N/A** | **Privacy violation risk** |

**Economic impact:** If a system prompt + RAG context (10,000 tokens) is identical across 1,000 daily requests: **88% reduction** in input token cost via caching.

---

## Related Documents

**Companion parts:**
- **Part 2:** [Budget Governance, FinOps & ROI](54-ai-cost-implementation-guide-2026-budget-finops-roi-measurement.md)
- **Part 3:** [Anti-Pattern Fixes & Deployment](55-ai-cost-implementation-guide-2026-anti-patterns-deployment-playbook.md)

**Related:**
- [AI Tokenomics Guide](07-ai-tokenomics-guide.md) — token mechanics and cost estimation
- [Enterprise AI Commercial Analysis 2026](09-enterprise-ai-commercial-analysis-2026.md) — vendor pricing and contracts

## Sources

_No external sources cited yet; grounding pending (tracked for wave-1 follow-up)._
