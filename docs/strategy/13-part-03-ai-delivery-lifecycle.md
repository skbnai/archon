---
title: "AI Delivery Lifecycle"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-03-ai-delivery-lifecycle
maturity: practitioner
personas: [program-manager, delivery-lead, architect]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-03-ai-delivery-lifecycle.md
tags: ["ai-delivery", "aidlc", "lifecycle", "mlops", "delivery-model"]
sources: []
---

# AI Delivery Lifecycle

Understanding the full AI delivery lifecycle is essential for managing AI programmes effectively. The AI delivery lifecycle differs significantly from traditional software delivery (SDLC) and data science workflows (MLOps).

## Lifecycle Overview

The complete AI delivery lifecycle spans from strategy through retirement:

**Strategy Phase:** Opportunity identification → AI portfolio management → business case → prioritization

**Discovery & Design:** Problem analysis → data assessment → architecture design → responsible AI review → security review

**Build Phase:** Model selection → prompt design → context engineering → knowledge engineering → agent design → tool design → memory design

**Evaluation & Testing:** Evaluation against acceptance criteria → pilot deployment → production readiness

**Operations:** Production deployment → continuous learning → monitoring → optimization

**Retirement:** Deprecation → decommissioning

## What Differentiates AI Delivery from Traditional SDLC

| Dimension | Traditional SDLC | AI Delivery |
|-----------|---|---|
| Definition of "done" | All requirements implemented | Evaluation thresholds met |
| Primary quality gate | Unit/integration tests pass | Evaluation scores meet acceptance criteria |
| Data phase | Data modelling for system | Data quality, lineage, and bias assessment |
| Change management | Code review + CI/CD | Model version + prompt version + eval regression |
| Risk profile | Defects and vulnerabilities | Hallucination, bias, drift, safety |
| Retirement trigger | End of business need | Model deprecation, performance degradation, regulatory change |

## Key Decision Gates

Each phase has exit criteria that must pass before proceeding:

| Gate | What Is Reviewed | Who Approves |
|------|---|---|
| Business Case Gate | Feasibility, ROI, priority ranking | Portfolio Board |
| Architecture Gate | Solution design, data assessment, feasibility | Architecture Review Board |
| Responsible AI Gate | Fairness, bias, transparency, safety | RAI Officer |
| Security Gate | Threat model, data protection, access control | CISO / Security Architect |
| Evaluation Gate | Quality scores meet acceptance thresholds | AI Product Manager + QA |
| Production Gate | All gates passed; runbook ready; monitoring live | Delivery Lead |

## Deep-Dive Resources

- [GenAI Delivery Lifecycle](14-part-04-genai-delivery.md) — How delivery differs for LLMs
- [Agentic AI Delivery Lifecycle (ADLC)](15-part-05-agentic-lifecycle.md) — ADLC extension for autonomous agents
- [Operating Processes](19-part-09-operating-processes.md) — Operational processes after production

## Related

- [AI Operating Models](12-part-02-operating-models.md)
- [Governance Model](16-part-06-governance.md)
- [Platform Operating Model](17-part-07-platform-operating-model.md)

## Sources

