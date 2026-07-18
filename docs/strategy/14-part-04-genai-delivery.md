---
title: "GenAI Delivery Lifecycle"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-04-genai-delivery
maturity: practitioner
personas: [program-manager, delivery-lead, architect]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-04-genai-delivery.md
tags: ["genai", "llm", "rag", "prompt-engineering", "evaluation", "guardrails", "llmops"]
sources: []
---

# GenAI Delivery Lifecycle

GenAI delivery differs fundamentally from traditional ML development. Foundation models eliminate the need for task-specific training in many cases, compressing the timeline from months to weeks or days.

## GenAI Delivery Phases

1. **Problem Identification** — Determine if the problem is a good GenAI fit
2. **LLM Selection** — Choose model based on capability, cost, latency, data residency
3. **Prompt Engineering** — Iteratively design system prompts, role assignment, output format
4. **Context Engineering** — Design information context (retrieval sources, chunking, ordering)
5. **RAG (if needed)** — Implement retrieval-augmented generation for knowledge grounding
6. **Knowledge Base** — Build and maintain the document corpus
7. **Evaluation** — Define quality metrics (faithfulness, relevance, coherence, safety)
8. **Guardrails** — Implement safety controls at input and output
9. **Deployment** — Deploy via managed inference service
10. **Observability** — Monitor quality, cost, and user satisfaction
11. **Optimization** — Tune prompts, models, context based on live feedback
12. **Business Value Measurement** — Track ROI against project baseline

## How GenAI Differs from Traditional ML

| Dimension | Traditional ML | GenAI |
|---|---|---|
| Primary skill | Feature engineering, model training | Prompt engineering, context design |
| Training data | Labelled dataset (task-specific) | Pre-trained on internet scale |
| Time-to-first-output | Weeks–months | Hours–days |
| Failure mode | Overfitting, drift | Hallucination, prompt injection |
| Quality gate | Accuracy / F1 / AUC benchmarks | Evaluation against golden dataset |
| Versioning | Model version | Model × prompt × retrieval index |
| Explainability | Feature importance (SHAP, LIME) | Chain-of-thought, citation attribution |
| Monitoring | Model performance drift | Quality drift, prompt drift, knowledge drift, cost |
| Regulatory artifact | Model card, bias assessment | Prompt log, RAG source attribution |

## Problem-by-Problem Guidance

**Natural Language Understanding & Generation:** GenAI excels. Use case: conversational interfaces, summarization, content generation.

**Document Extraction & Q&A:** GenAI excels with RAG. Use case: contract analysis, regulatory document intelligence, technical documentation assistants.

**Code Generation:** GenAI excels. Use case: GitHub Copilot-style features, code refactoring, boilerplate generation.

**Precise Numerical Computation:** GenAI not suitable. Requirement: deterministic results.

**Strict Deterministic Logic:** GenAI not suitable. Example: financial transaction routing where hallucination is unacceptable.

**Image Generation:** Depends on model. GPT-4V and Claude Vision excel at image understanding; image generation requires specialized models.

## Key GenAI Design Principles

1. **Grounding is critical** — Use RAG to ground responses in enterprise knowledge and reduce hallucination
2. **Evaluation before scaling** — Define success metrics before building; test on golden datasets
3. **Cost monitoring is mandatory** — LLM costs scale linearly with usage; implement FinOps from day one
4. **Guardrails are required** — Implement input filtering (prompt injection) and output filtering (safety)
5. **Prompt versioning is versioning** — Treat prompt updates with same rigor as code releases

## Deep-Dive Resources

- [AI Delivery Lifecycle](13-part-03-ai-delivery-lifecycle.md) — Full parent lifecycle
- [Agentic AI Delivery Lifecycle (ADLC)](15-part-05-agentic-lifecycle.md) — How delivery differs for agents
- [AI Service Catalog](20-part-10-service-catalog.md) — Services that support GenAI delivery

## Related

- [Enterprise Operating Models](12-part-02-operating-models.md)
- [AI Governance](16-part-06-governance.md)
- [AI Platform](17-part-07-platform-operating-model.md)

## Sources

