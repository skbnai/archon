---
title: Evaluation & Quality Gates
doc_type: guide
domain: data-knowledge
status: current
canonical: true
topic_id: evaluation
maturity: practitioner
personas: [architect, engineer, data-engineer]
date_created: 2026-07-05
last_reviewed: 2026-07-10
covers_version: "as of 2026-07-10"
source_type: native-md
supersedes:
  - docs/knowledge-engineering/industry-practices/evaluation.md
tags: [knowledge-engineering, industry-practices]
sources: []
---

# Evaluation &amp; Quality Gates

How enterprises measure whether knowledge systems are accurate, grounded, and safe — from golden datasets and LLM-as-judge to CI gates and production monitoring. By 2026 an estimated **60% of enterprise deployments include systematic evaluation frameworks**. Research current as of July 2026.

---

## The evaluation stack

Mature teams run evaluation at three layers, each catching what the previous can't:

| Layer | When | Catches |
| --- | --- | --- |
| **Offline evals** (golden datasets) | Per change, pre-merge | Regressions in retrieval and generation quality |
| **CI quality gates** | Every deploy | Threshold violations before users see them |
| **Production monitoring** (tracing + online evals) | Continuously | Drift, novel query patterns, source-data decay |

## Core metrics: the RAGAS four

RAGAS established the four-metric pattern that everything else builds on — all computable **without ground-truth labels**, using LLM-as-judge:

- **Faithfulness** — does the answer make only claims supported by the retrieved context? (the hallucination metric)
- **Answer relevancy** — does the answer address the question?
- **Context precision** — was what we retrieved actually relevant?
- **Context recall** — did we retrieve everything needed?

The first two evaluate *generation*; the last two evaluate *retrieval* — which matters because they fail independently, and fixing the wrong stage wastes months. Commonly published production thresholds: **faithfulness ≥ 0.75, answer relevancy ≥ 0.80, context precision ≥ 0.70, context recall ≥ 0.80** — with the strictest citation-critical systems gating faithfulness as high as 0.97. By 2026, frameworks ship 6–12 RAG-specific metrics extending this core.

## Framework comparison: RAGAS vs DeepEval vs TruLens

The three dominant open-source frameworks all use LLM-as-judge but occupy different slots:

| | **RAGAS** | **DeepEval** | **TruLens** |
| --- | --- | --- | --- |
| Sweet spot | Fast experimentation | CI/CD regression gates | Production monitoring |
| Metrics | 4 core RAG metrics, ground-truth-free | 50+ metrics | Feedback functions |
| Integration | Lightweight Python | **Pytest-native** | **OpenTelemetry tracing** |
| Momentum (2026) | Strong community, application-layer features | Strong community, fast shipping | Post-TruEra-acquisition tilt toward enterprise data-platform integration |

A common production stack uses all three roles: RAGAS-style metrics to iterate, DeepEval-style Pytest gates in CI, TruLens-style tracing in production.

## LLM-as-judge, done carefully

Three tiers of evaluator, in increasing cost and flexibility:

1. **Deterministic** — exact match, citation-presence checks, schema validation.
2. **Statistical** — regex/heuristics, embedding similarity.
3. **LLM-as-judge** — with explicit rubrics, calibrated against human labels, and its own guardrails (bias toward verbosity, position, self-preference are known failure modes).

The pre-automation baseline is worth copying: McKinsey evaluated Lilli by **blind scoring** — humans rated outputs produced with and without the tool on a five-point scale for accuracy, content richness, and distinctiveness. Automated judges should be validated against exactly this kind of human-labeled sample before being trusted in gates.

## Golden datasets

The golden dataset is the eval backbone: representative queries × expected sources × reference answers, covering the head, the long tail, and — critically — **out-of-corpus questions where the correct behavior is refusal**.

Governance requirement (increasingly audited): annotate every element with **provenance, reviewer identity, annotation instructions, consent flags, and risk tags** so the dataset itself supports ISO/IEC 42001 and NIST AI RMF traceability.

## CI gates and production monitoring

- **CI:** evals run as Pytest-style suites per pull request; a metric dropping below threshold fails the build exactly like a unit test. Faithfulness gates block deploys of prompt, model, retriever, or corpus changes.
- **Production:** OpenTelemetry-style tracing captures query → retrieved chunks → answer → citations; online judges sample live traffic for groundedness; alerts fire on drift.

## The blind spot: when the *context* is wrong

Inference-layer evals (all three frameworks) can detect an answer that contradicts its retrieved context. They **cannot detect that the retrieved content itself was wrong** — stale, superseded, or unauthoritative. Catching that class of failure requires **context-layer monitoring**: freshness SLAs on sources, authority scoring, and lineage checks — i.e., the governance layer from [Governance &amp; Responsible AI for Knowledge Systems](./09-governance-rai.md). Evaluation and governance are two halves of one quality system, not separate concerns.

## Practical starting point

1. Build a 100–300 item golden dataset from real user queries (include refusal cases); annotate for traceability.
2. Wire the RAGAS four into CI with the published thresholds; tighten faithfulness as the system matures.
3. Validate your LLM judge against a human-scored sample before trusting it in gates.
4. Trace production traffic and sample it through the same judges.
5. Add context-layer checks (freshness, authority, lineage) — the failures evals can't see.

---

## Related

- [Grounding Architectures](10-grounding.md) — the retrieval patterns these evaluation gates measure.
- [Governance & Responsible AI for Knowledge Systems](09-governance-rai.md) — the regulatory context that makes systematic evaluation a compliance requirement, not just a quality nicety.
- [Operations Hub](../operations/index.md) — the broader evaluation and benchmark practice this domain-specific evaluation work plugs into.

## Sources

- [RAGAS, TruLens, DeepEval: LLM Evaluation Frameworks Compared (Atlan)](https://atlan.com/know/llm-evaluation-frameworks-compared/)
- [Ragas: Automated Evaluation of Retrieval Augmented Generation (arXiv)](https://arxiv.org/pdf/2309.15217)
- [What is RAG Evaluation? Frameworks, Metrics, and Gates in 2026 (Future AGI)](https://futureagi.com/blog/what-is-rag-evaluation-2026/)
- [DeepEval vs RAGAS vs TruLens: Pick Your RAG Eval Stack (Particula)](https://particula.tech/blog/deepeval-vs-ragas-vs-trulens-rag-evaluation-stack)
- [DeepEval vs Ragas (DeepEval)](https://deepeval.com/blog/deepeval-vs-ragas)
- [RAG evaluation: metrics, frameworks and best practices (N-iX)](https://www.n-ix.com/rag-evaluation/)
- [Building a Golden Dataset for AI Evaluation (Maxim)](https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/)
- [LLM Evaluation Tools: Complete Comparison Guide 2026 (Inference.net)](https://inference.net/content/llm-evaluation-tools-comparison/)
- [What McKinsey learned while creating its generative AI platform (McKinsey)](https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/what-mckinsey-learned-while-creating-its-generative-ai-platform)
- [RAG Evaluation Frameworks 2026 (Callsphere)](https://callsphere.ai/blog/rag-evaluation-frameworks-2026-ragas-trulens-deepeval)
