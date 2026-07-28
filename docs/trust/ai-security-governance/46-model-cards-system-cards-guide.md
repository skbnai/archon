---
title: "Model Cards & System Cards: AI Transparency Documentation Standards"
doc_type: guide
domain: trust
status: current
topic_id: model-cards-system-cards-guide
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/Model-Cards-System-Cards-Guide.md]
tags: [model-card, system-card, ai-transparency, eu-ai-act, responsible-ai]
covers_version: "as of 2026"
---

Structured documentation artifacts for AI systems — what they do, how they were built, what they were evaluated on, and where they fail — now functionally mandatory for high-risk AI systems under the EU AI Act.

## What Are Model Cards and System Cards?

Model cards and system cards are documents published alongside AI models and systems describing their capabilities, limitations, evaluation results, intended use, and safety properties, serving several audiences: developers ask whether a model fits their use case and what its limitations are; end users ask what to expect and when not to trust it; procurement teams ask whether it meets compliance requirements and what data trained it; auditors and regulators ask what risks it poses and how it was evaluated; and the broader research community compares models on consistent dimensions.

**Model card vs. system card:**

| Aspect | Model Card | System Card |
|---|---|---|
| Subject | The AI model (weights, training, capabilities) | The deployed AI system (model + product + safeguards) |
| Scope | Model-level: architecture, training data, benchmarks | System-level: use case, HITL design, abuse mitigations, deployment context |
| Published by | The model developer | The product/system builder deploying the model |
| Audience | Developers and researchers | Regulators, users, procurement, safety teams |
| Examples | Hugging Face model cards, Google Model Card Toolkit | Vendor system cards published alongside major model/product releases |

## Why Documentation Is Now Mandatory

**EU AI Act.** Article 11 and Annex IV require high-risk AI providers to maintain technical documentation covering a general description of the system and its intended purpose; a description of the system's elements and how they interact; a detailed description of the training methodology and training data; the design choices and trade-offs made; validation and testing procedures and results; the standards applied and solutions adopted for compliance; and reasonably foreseeable risks with their mitigation measures. A model card or system card covering these areas is the primary mechanism for meeting these requirements.

**GPAI Code of Practice (EU).** General-purpose AI model providers face additional documentation requirements under the EU GPAI Code of Practice, including training data transparency, evaluation results on standardized benchmarks, and documented known capabilities and limitations at scale.

**US AI Executive Order.** Requires AI developers providing dual-use foundation models to the government to submit documentation of capabilities, evaluations, and safety properties — functionally requiring model cards.

## Model Card Structure

Following the foundational Mitchell et al. (2019) academic framework, augmented with current practice, a complete model card covers six sections. **Model Details** records the model name and version, architecture family, developer, training completion date, license and restrictions, citation format, and a contact point. **Intended Use** documents the primary intended uses and users, out-of-scope uses, and uses explicitly prohibited by license or policy. **Training Data** documents which datasets were used, the collection methodology, data characteristics (size, domains, languages, time period), known biases or representation gaps, and consent/licensing status. **Evaluation Results** covers standard performance benchmarks, disaggregated evaluation across demographic groups and languages, safety evaluation (harmful content, refusal behavior, adversarial robustness), documented limitations, and out-of-distribution behavior. **Ethical Considerations** covers sensitive use cases requiring additional caution, known fairness and bias disparities, what private information the model might expose, and environmental impact (training compute and estimated emissions). **Caveats and Recommendations** closes with best practices for deployment, documented failure modes, and the policy for how the card itself will be updated as the model evolves.

## System Card Structure (Enterprise)

For deployed AI systems — agents, copilots, applications — the system card extends beyond the model itself. **System Overview** captures the essentials in structured form:

```yaml
system_name: Customer Support Agent v2.3
deployer: Acme Corp, Customer Experience Team
model_used: claude-sonnet-4-6 (via Anthropic API)
deployment_date: 2026-06-15
eu_ai_act_risk_class: Limited Risk (Art. 52 transparency obligation)
intended_use: Answer customer support questions; escalate to humans for complex issues
```

**Capability and Limitation Statement** spells out what the system can and cannot do — for example, it can answer product questions from the knowledge base and initiate returns via the Returns API, but cannot handle legal, medical, or financial advice and cannot access customer payment information.

**Safeguards and Mitigations** maps each known risk to its control:

| Risk | Mitigation |
|---|---|
| Harmful content generation | Output guardrail (safety classifier + custom rules) |
| PII leakage | Real-time PII detection and redaction before logging |
| Hallucination | RAG-grounded responses; confidence threshold |
| Manipulation | Prompt injection detection (AIDR) |
| Bias in responses | Regular bias auditing; disaggregated eval by demographics |

**Human Oversight Design** maps each trigger to the required human action:

| Trigger | Human Action Required |
|---|---|
| Customer dissatisfaction signal | Escalate to a human agent |
| Legal/regulatory question detected | Hard block; route to the legal team |
| Confidence below threshold | Disclose uncertainty; offer a human option |
| AIDR security alert | Session terminated; SOC notified |

**Evaluation and Monitoring** documents the ongoing measurement regime: a pre-deployment evaluation suite combining a domain-specific eval set with adversarial red teaming; production monitoring via LLM-as-judge on a sample of sessions each week; human QA review of a separate weekly sample; and automated statistical drift detection that alerts when the quality score drops materially.

**Regulatory Compliance** tracks status against each applicable requirement — EU AI Act Article 52 transparency (users notified they're interacting with AI), GDPR data minimization (bounded conversation retention), ISO 42001 review under the AI management system, and jurisdiction-specific consent regulations (e.g., India's DPDP Act) — each marked complete or open.

## Quality of Model Card Documentation: A Research Finding

Research analyzing model cards in production found substantial gaps between well-covered and poorly-covered documentation elements: model architecture and evaluation metrics are documented in over 90% of published cards, compute requirements in over 85%, and intended use in over 80% — but bias and fairness appear in only around 45%, safety evaluation in around 40%, out-of-scope uses in around 35%, and interpretability in only around 20%.

**The critical gap:** safety, bias, and out-of-scope documentation — the elements most needed by regulators — are present in fewer than half of published model cards. Enterprise model cards should fill these gaps explicitly rather than following the industry-average pattern.

## Tools for Generating Model Cards

| Tool | Description |
|---|---|
| Google Model Card Toolkit | Open-source Python library; structured output |
| Hugging Face Model Card template | Web-based; YAML front matter plus Markdown, auto-rendered on the Hub |
| Microsoft Responsible AI Dashboard | GUI-driven; integrates with Azure ML; generates structured cards |
| MLflow Model Registry | Stores model metadata; can export structured documentation |
| CycloneDX ML-BOM | Machine-readable; overlaps with the model card for supply-chain use |

## Integration with AIBOM

Model cards and AIBOMs are complementary and should be generated together: the AIBOM is the machine-readable inventory (provenance, integrity, license), while the model card is the human-readable documentation (capabilities, limitations, evaluation) — together they form the complete picture for developers, users, auditors, and regulators. For EU AI Act compliance, both are needed: the AIBOM for Annex IV supply-chain documentation, and the model card for capability and risk documentation.

## Key Metrics

| KPI | Target |
|---|---|
| Model card publication rate | 100% of models before production deployment |
| System card coverage | 100% of deployed AI systems |
| Card freshness | Updated within 30 days of any material change |
| Required section completeness | 100% of sections populated (no "TBD" in production cards) |
| Safety evaluation documented | 100% (this is the common industry gap) |
| EU AI Act Annex IV completeness | 100% for high-risk systems |

## Related

- [AI Bill of Materials Guide](41-ai-bill-of-materials-guide.md)
- [AI TRiSM Complete Guide](43-ai-trism-complete-guide.md)
- [AIDR: AI Detection & Response](44-aidr-ai-detection-response-complete-guide.md)
