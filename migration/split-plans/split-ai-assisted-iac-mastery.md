# Split Plan: AI-Assisted IaC Mastery Guide

**Source:** `/workspace/knowledge-docs/docs/cloud-platforms/iac/terraform/ai-assisted-iac-mastery.md` (~6,240 words body)

**Reason:** Word count exceeds guide doc_type cap (2600 words hard cap)

## Split Boundary

**Part 1 (Main):** `docs/platforms/25-ai-assisted-iac-mastery.md`
- Source: Parts 1–6 (The AI-IaC Paradigm, IaC Autonomy Spectrum, Chat-Based Terraform Generation, AI Code Review & Static Analysis, AI-Assisted Plan Interpretation, Agentic IaC Workflows)
- Content: LLM selection for IaC, the 5-level autonomy spectrum, chat-to-Terraform prompt patterns, static analysis tool comparison, plan interpretation, agentic tool-use loops
- Target word count: ~2290 words

**Part 2 (Supplementary):** `docs/platforms/parts/25-ai-assisted-iac-mastery-part2.md`
- Source: Parts 7–13 (Multi-Layer Guardrail Architecture, Security & Compliance Automation, AI-Powered Drift Detection & Remediation, Cost Optimization with AI, AI-Assisted Troubleshooting, Internal AI-IaC Platform Architecture, Governance & Policy Frameworks)
- Content: 6-layer guardrail defense-in-depth, OPA/Sentinel policy examples, HIPAA compliance-as-code, drift detection/remediation pipelines, cost optimization prompts, troubleshooting decision tree, internal platform reference architecture, governance model
- Target word count: ~1890 words

**Part 3 (Supplementary):** `docs/platforms/parts/25-ai-assisted-iac-mastery-part3.md`
- Source: Parts 14–16 + Appendices A–C (Self-Healing Infrastructure Patterns, Multi-Agent IaC Orchestration, The Future — Autonomous Infrastructure, Tool Selection Matrix, Prompt Engineering for IaC, Production Readiness Checklist)
- Content: EventBridge-triggered drift response, multi-agent orchestration patterns, 5-year autonomy outlook, responsible-AI-IaC principles, tool/model selection matrices, prompt templates, production readiness checklist
- Target word count: ~2060 words

## Mapping

| Source Part | Target Part | Title |
|---|---|---|
| 1–6 | 1 | The AI-IaC Paradigm → Agentic IaC Workflows |
| 7–13 | 2 | Multi-Layer Guardrail Architecture → Governance & Policy Frameworks |
| 14–16, A–C | 3 | Self-Healing Infrastructure Patterns → Production Readiness Checklist |

## Navigation

- Part 1 ends with a pointer to Part 2 (guardrails, security, drift, cost, troubleshooting, platform architecture, governance).
- Part 2 ends with a pointer to Part 3 (self-healing patterns, multi-agent orchestration, future outlook, appendices).
- Topic ID: all three parts share the `ai-assisted-iac-mastery` topic family.
- Part 1 is canonical (`topic_id: ai-assisted-iac-mastery`).
- Part 2 uses `topic_id: ai-assisted-iac-mastery-part2`, Part 3 uses `topic_id: ai-assisted-iac-mastery-part3`; both `supersedes: []` (Part 1 carries the supersedes entry).
