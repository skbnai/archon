---
title: "Part 11 — AI DevSecOps"
doc_type: guide
domain: strategy
topic_id: part-11-devsecops
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "engineer", "operations"]
supersedes: ["docs/enterprise-ai-report/part-11-devsecops.md"]
tags: ["devsecops", "mlops", "llmops", "agentops", "promptops", "dataops", "gitops", "cicd"]
sources: []
---

# Part 11 — AI DevSecOps

AI DevSecOps extends traditional DevSecOps with AI-specific operational disciplines. This page maps the full AI DevSecOps landscape and links to authoritative guidance in specialized sections.

## The AI DevSecOps Stack

AI DevSecOps combines traditional practices with AI-specific disciplines:

- **Traditional:** CI/CD, SecurityOps, GitOps, PlatformOps
- **AI-Specific:** ModelOps, LLMOps, AgentOps, PromptOps, DataOps, KnowledgeOps, EvaluationOps, ContextOps, MemoryOps

Each discipline ensures reliable, secure, observable AI deployments at every stage of the pipeline.

## Discipline Definitions & Key Practices

### CI/CD for AI

Standard continuous integration and deployment practices extended for AI artifacts. Every change to model configuration, prompt, agent, or knowledge base triggers a pipeline.

**What triggers the pipeline?**
- Code change → standard CI tests + AI integration tests
- Prompt version change → prompt evaluation suite
- Model version change → regression evaluation + canary deployment
- Agent configuration change → agent simulation tests
- Knowledge base update → retrieval quality check

**Key AI-specific CI gates:**
- Evaluation score threshold (don't deploy if quality drops)
- Hallucination rate check (reject if rate exceeds threshold)
- Safety test pass (required before any customer-facing deployment)
- Cost budget check (estimated cost of new version within approved budget)

### ModelOps

Operationalisation of ML model training, deployment, monitoring, and retraining. This is the "traditional" ML engineering discipline.

**Key practices:** Feature store management, training pipelines, model registry, model serving, model monitoring, automated retraining triggers.

**Tooling:** MLflow, Kubeflow, SageMaker Pipelines, Azure ML, Vertex AI Pipelines.

### LLMOps

Operational discipline for large language model deployment and management in production.

**Key practices:** LLM deployment pipelines, model version pinning, prompt version management, A/B testing, cost optimisation (caching, routing), latency monitoring, fine-tuning pipelines.

**Tooling:** LangSmith, Langfuse, Helicone, LiteLLM, OpenRouter, GPTCache.

### AgentOps

Operational discipline for AI agent deployment, monitoring, and lifecycle management.

**Key practices:** Agent deployment pipelines, agent health monitoring (loop detection, tool error tracking), HITL queue management, emergency shutdown procedures, agent fleet management, version management of compound agent artifacts.

### PromptOps

Version control, testing, deployment, and monitoring of system prompts.

**Key practices:** Prompt registry, semantic versioning, approval workflow automation, A/B test management, prompt performance monitoring, hot-swap without redeployment.

### DataOps

Data pipeline automation and quality management for AI training and knowledge base data.

**Key practices:** Data versioning, pipeline orchestration, data quality monitoring, lineage tracking, schema evolution management.

**Tooling:** Airflow, dbt, Great Expectations, Delta Lake, DVC.

### KnowledgeOps

Operational discipline for managing enterprise knowledge bases used in RAG systems.

**Key practices:** Document ingestion pipelines, freshness monitoring, PII scanning automation, access control synchronisation, retrieval quality monitoring, knowledge base versioning.

### EvaluationOps

Continuous automated evaluation of AI system quality across all deployment stages.

**Key practices:** Evaluation test suite management, LLM-as-judge pipelines, human annotation queue, regression detection, quality dashboards, drift alerting.

### ContextOps

Operational management of the context assembly pipeline — ensuring context quality, freshness, and efficiency.

**Key practices:** Context pipeline monitoring, retrieval quality tracking, context cache management, context compression pipeline, token budget monitoring.

### MemoryOps

Operational management of agent and conversational memory systems.

**Key practices:** Memory store health monitoring, retention policy enforcement, privacy deletion automation, memory index maintenance, episodic memory pruning.

### SecurityOps (AI-Specific)

AI security operations extending traditional SecOps with AI-specific threat monitoring.

**Key practices:** Prompt injection monitoring, jailbreak attempt detection, data exfiltration via AI monitoring, agent action anomaly detection, AI SBOM management.

### GitOps for AI

Infrastructure-as-code and configuration-as-code for AI platform components.

**Key practices:** AI platform config in Git (model routing rules, guardrail config, policy definitions), GitOps reconciliation loops, drift detection for AI platform config.

### PlatformOps

Operation of the AI platform itself — the infrastructure that all other AI ops disciplines depend on.

**Key practices:** AI platform SRE, capacity planning, cost optimisation, vendor SLA management, GPU cluster operations.

## AI DevSecOps Pipeline Pattern

A typical AI DevSecOps pipeline flows through these stages:

1. Code/prompt/config commit triggers automated checks (lint, format)
2. Unit tests + AI integration tests validate functionality
3. Security scanning includes SAST, secrets detection, AI SBOM
4. Evaluation gate ensures quality score meets threshold
5. Safety gate confirms no high-severity safety failures
6. Cost gate validates estimated cost is within budget
7. Staging deployment and integration test suite runs
8. Canary deployment (5% traffic) monitors for issues
9. Production monitoring (24h window) tracks quality and cost
10. Promote to 100% or rollback based on observed metrics

## Comparison: AI DevSecOps vs Traditional DevSecOps

| Practice | Traditional | AI DevSecOps |
|----------|------------|--------------|
| Test artifact | Source code | Code + model + prompt + evaluation suite |
| Quality gate | Tests pass | Evaluation score threshold met |
| Security scan | SAST, DAST, SCA | + Prompt injection test, adversarial test, SBOM for AI |
| Deployment strategy | Blue/green, rolling | + Shadow, canary with quality monitoring, A/B prompt test |
| Monitoring | Uptime, error rate, latency | + Quality drift, hallucination rate, cost per token, agent task completion |
| Rollback trigger | Error rate spike | + Quality degradation, safety incident, cost overrun |
| Release cadence | Days/weeks | Prompts: hours; Models: weeks; Agents: days–weeks |

## Authoritative Guides

Specialized documentation for each discipline is available in the **Agentic Systems**, **AI Development**, and **AI Security Governance** domains:

- **AIDLC guides** cover AI CI/CD pipelines and sprint cadence
- **Agentic UI DevSecOps** guide covers full DevSecOps for AI applications
- **Enterprise PromptOps** guide covers prompt lifecycle management
- **AI Agent Evaluation Framework** covers evaluation pipelines
- **AI Observability guides** cover monitoring stages in the pipeline

## Related

- [Part 10 — Service Catalog](20-part-10-service-catalog.md) — Evaluation Service, Guardrail Service used in pipelines
- [Part 13 — Security Model](23-part-13-security-model.md) — Security controls embedded in DevSecOps pipelines
- [Part 14 — Observability](24-part-14-observability.md) — Observability powering monitoring stages
- [Part 9 — Operating Processes](19-part-09-operating-processes.md) — Model rollout and canary deployment procedures

## Sources

[No external sources for this page.]
