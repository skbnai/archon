---
title: "AI Tokenomics: Prompting, Model Selection & Fine-Tuning"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ai-tokenomics-guide-part2
maturity: practitioner
personas:
  - ai-architect
  - prompt-engineer
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - tokenomics
  - prompt-engineering
  - model-selection
  - fine-tuning
sources: []
pagination_prev: strategy/ai-tokenomics-guide
pagination_next: strategy/ai-tokenomics-guide-batch-processing-tco-scale
---

# AI Tokenomics: Prompting, Model Selection & Fine-Tuning

**Part 2 of 3** — token-efficient prompting, capability-price frontier, and fine-tuning vs. RAG economics.

## Prompt Engineering for Cost Efficiency

### Cost of Clarity Trade-Off

More explicit instructions ≠ better output. Instruction efficiency follows a curve: too sparse (ambiguous) and too verbose (redundant, contradictory) both miss the optimum.

**Most enterprise system prompts sit right of optimal** — they contain redundant instructions.

### Token-Efficient Patterns

**Pattern 1: Role + Constraint + Format (~94 vs. 487 tokens)**
```
Efficient: "Role: EA. Constraints: Production-grade only. Format: Decision → Rationale → Trade-offs."
```

**Pattern 2: Structured XML for Claude**
Reduces output tokens by 20–40% by eliminating preamble.

**Pattern 3: Few-Shot Economics**
- Zero-shot: baseline cost
- 1-shot: +100–500 tokens; +10–20% quality
- 3-shot: +300–1,500 tokens; +15–25% quality
- 5+ shot: diminishing returns; consider fine-tuning instead

**Pattern 4: Output Length Control**
Output tokens cost 3–5× more than input. Controlling output is often more impactful than reducing input.

---

## Capability-Price Frontier & Model Selection

Efficient frontier maps models where no alternative is both cheaper AND better. Select the cheapest model meeting your quality threshold.

| **Task** | **Recommended tier** | **Rationale** |
|---|---|---|
| Classification, routing | Nano (Haiku/Flash/mini) | Deterministic |
| Code completion (single) | Mid (Sonnet/GPT-4o) | Context needed |
| Architecture analysis | Mid–Frontier | High quality threshold |
| Complex reasoning | Frontier (Opus/o3) | Accuracy justified |
| Customer chat | Mid (+ HITL fallback) | Good enough for 90%+ |
| Legal/compliance analysis | Frontier | Hallucination risk |

---

## Fine-Tuning vs. RAG vs. In-Context Trade-Offs

| Approach | Cost/1000 requests | Quality gain | Use when |
|---|---|---|---|
| **Zero-shot** | Lowest | Baseline | Common, well-defined tasks |
| **In-context (few-shot)** | +1–5% | +10–30% | Output format novel |
| **RAG** | +10–30% (embedding cost) | +20–40% | Large knowledge base, frequent updates |
| **Fine-tuning** | +50–200% (training) | +30–60% at scale | Long-lived task, millions of calls, proprietary style |

**Decision rule:** Fine-tune if task lifetime ≥ 6 months AND call volume ≥ 1M.

---

## Related Documents

**Part 1:** [Token Mechanics & Context Economics](07-ai-tokenomics-guide.md)

**Part 3:** [Batch Processing, TCO & Scale](60-ai-tokenomics-guide-batch-processing-tco-scale.md)

## Sources

_No external sources cited yet; grounding pending (tracked for wave-1 follow-up)._
