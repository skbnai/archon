---
title: "AIDLC Agile & CI/CD Transformation: Roles, Disciplines, Roadmap & Principles"
doc_type: guide
domain: architecture
status: current
canonical: true
topic_id: aidlc-agile-cicd-ai-transformation-2026-part3
maturity: expert
personas: [architect, engineer, manager, leader]
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags: [aidlc, agile, cicd, ai-transformation, devops, mlops, llmops, agentops, roles]
sources: []
---

# AIDLC Agile & CI/CD Transformation: Roles, Disciplines, Roadmap & Principles

Part 3 of 3 — continues from [Part 2: Agile Evolution & CI/CD Transformation](./10-aidlc-agile-cicd-agile-evolution-cicd-transformation.md).

New developer roles, operational disciplines, transformation roadmap, and principles for AI-native engineering.

**Audience:** Engineering Leaders, Platform Engineers, DevOps Teams, Enterprise Architects

**Coverage:** Developer Roles · Operational Disciplines · Transformation Roadmap · Engineering Principles

**As of:** March 2026

---

## The New Developer Roles & Workflows

The developer role is not disappearing — it is bifurcating. One direction elevates to AI orchestration and system architecture. The other direction deepens into domain expertise and human judgment that AI cannot replicate. In between, entirely new roles are emerging.

| **New Role** | **What They Do** | **Replaces / Evolves From** | **Key Skills** |
|---|---|---|---|
| AI Orchestration Engineer (Conductor Developer) | Designs agent systems, writes AGENTS.md and context files, reviews AI-generated PRs for architectural integrity | Senior Backend Developer — elevated to system architect who codes intent rather than implementation | Context engineering, LangGraph/CrewAI, agent architecture, MCP server design, multi-model routing |
| Context Engineer | Owns the information environment AI agents operate within: prompt libraries, AGENTS.md files, knowledge bases, RAG pipelines | Prompt Engineer (evolved) + Technical Writer — now a strategic engineering role, not a support role | Markdown spec writing, RAG architecture, vector DB management, AI agent behaviour patterns |
| AI Quality Engineer (Eval Engineer) | Designs evaluation frameworks, maintains golden datasets, builds LLM-as-Judge pipelines, defines quality thresholds | QA Engineer — massively elevated from test script writing to evaluation science | Evals framework design, LLM-as-Judge patterns, statistical quality analysis, human preference labeling |
| Spec-Driven Developer (Product Engineer) | Writes requirements.md, design.md, tasks.md. Business-facing developer who translates product intent into executable AI specifications | Full-Stack Developer — now writing specs that AI implements rather than writing code directly | SDD methodology, AWS Kiro, GitHub Spec Kit, BMAD; domain expertise + technical translation |
| AgentOps Engineer | Builds and maintains the operational infrastructure for AI agents: monitoring, cost optimisation, security, self-healing pipelines | DevOps/SRE — evolved to manage AI agents as infrastructure components with unique operational characteristics | LangSmith, AgentOps, distributed tracing, agent cost budgets, security sandboxing, rollback systems |
| AI Security Engineer | Conducts OWASP LLM Top 10 assessments, threat models MCP/A2A integrations, red-teams agent systems for prompt injection | Application Security Engineer — now specialised in AI-specific attack surfaces | Prompt injection, tool poisoning, MITRE ATLAS, adversarial prompting, agent sandboxing, secret management |

---

## The Four Operational Disciplines Compared

There are now four distinct AI operational disciplines, each addressing a different class of AI system.

| **Dimension** | **MLOps** | **LLMOps** | **AgentOps** | **AIOps** |
|---|---|---|---|---|
| What It Manages | Traditional ML models (classifiers, regressors, image models) | Large language models and their applications (RAG, chatbots, summaries) | Autonomous AI agents: planning, tool use, multi-step workflow execution | IT operations augmented by AI: incident detection, anomaly, self-healing infra |
| Primary Artifact | Trained model weights (.pkl, .onnx, .pt) | Prompt + model + RAG pipeline + guardrails (multiple components) | Agent graph + prompts + tools + memory + state + guardrails | Operational runbooks, alert definitions, infrastructure config |
| Testing Paradigm | Deterministic: accuracy, F1, RMSE on holdout set | Semantic: LLM-as-Judge, human preference, RAG faithfulness scores | Behavioral: task completion rate, multi-step trace evaluation, goal alignment | Infrastructure: uptime, MTTR, false positive rate on alert systems |
| Key Failure Mode | Data drift, model staleness, label drift | Hallucination, prompt brittleness, context overflow, cost explosion | Goal drift, tool misuse, infinite loops, cost runaway, security breach | Alert fatigue, missed incidents, false automation in critical systems |
| Monitoring Focus | Prediction accuracy, feature distribution drift | Output quality, token cost, latency, hallucination rate | Task traces, tool call success rates, cost per task, security events | Anomaly detection, incident correlation, infra health scoring |
| Human Role | Data scientist; trains, validates, deploys, monitors models | Prompt engineer + ML engineer; manages evaluation and quality | Agent architect + AgentOps engineer; designs, governs, reviews | SRE/DevOps; defines rules, reviews AI recommendations, approves actions |
| Primary Tools | MLflow, DVC, Kubeflow, SageMaker, Evidently | LangSmith, Braintrust, PromptLayer, Weights &amp; Biases Weave | AgentOps, LangSmith, Arize, Helicone, Azure AI Foundry | Splunk AI, Dynatrace Davis AI, New Relic AI, IBM watsonx IT Ops |
| Maturity Level (2026) | Mature — well-understood patterns and tooling | Maturing — tooling stabilised; best practices emerging | Early — tooling emerging; best practices being written now | Growing — embedded in ITSM; expanding to full AIOps autonomy |

---

## Executive Transformation Roadmap

### Phase 1 — Now (Month 1-3): Stop the Technical Debt Accumulation

**Establish Spec-First Policy:** Mandate that ALL new features start with a written specification (requirements.md) before any AI agent generates code. No spec = no AI coding. This single rule prevents 80% of vibe-coding technical debt.

**Implement AGENTS.md Immediately:** Every production repository gets an AGENTS.md file this week. Document: architecture decisions, forbidden patterns, naming conventions, API contracts, test requirements.

**Version Control Your Prompts:** Move all prompts out of dashboards, chat UIs, and spreadsheets into version control. Create /prompts/v1/ directory structure. Add golden test cases for critical prompts.

**Classify Stories into 3 Tiers:** Introduce the three-tier story classification: Zero-point (AI fully executes), Standard (human-led with AI assistance), Review-and-Integrate (AI generates, human validates).

**Add OWASP LLM Check to CI:** Add a lightweight OWASP LLM Top 10 scan to your CI/CD pipeline. Focus on prompt injection (#1) and excessive agency (#8) first.

### Phase 2 — 6 Months: Build the AI-Native Engineering Culture

- **Hire or develop Context Engineers:** 2+ engineers per product team dedicated to AI context, prompt libraries, AGENTS.md management
- **Deploy LLMOps evaluation platform:** Braintrust, LangSmith, or equivalent with golden datasets for all critical AI workflows
- **Rebuild CI/CD for probabilistic outputs:** Replace binary assertions with LLM-as-Judge evaluation for all AI agent tests
- **Introduce AgentOps monitoring:** Full trace observability for every production AI agent
- **Train all engineers in SDD:** GitHub Spec Kit or AWS Kiro for all engineers
- **Adopt 3-tier Agile estimation:** Full adoption of Zero-point / Standard / Review stories

### Phase 3 — 12 Months: AI-Native Engineering at Scale

- **Fully AI-native CI/CD pipeline:** Agents embedded at every stage
- **AgentOps as operational baseline:** Every agent in production has full trace observability, cost budget, quality threshold
- **ISO/IEC 42001 certification aligned with AIDLC:** AI management system standard integrates with your AIDLC
- **Continuous eval as product metric:** Eval scores treated as product quality KPIs
- **Context-as-code org standard:** AGENTS.md and spec files are first-class engineering artifacts
- **Developer role portfolio completed:** Every team has: Orchestration Engineer, Context Engineer, AI Quality Engineer, AgentOps Engineer

---

## The 10 Principles of AI-Native Engineering

1. **Specs before code.** No AI coding without a written specification. Spec is the source of truth, not the code.
2. **Context as infrastructure.** AGENTS.md, CLAUDE.md, and context files are maintained with the same rigour as infrastructure code.
3. **Prompts are code.** Every prompt lives in version control, passes through CI, and has rollback capability.
4. **Evaluation is not optional.** No AI feature ships without an automated eval suite. 'It ran without error' is not a quality signal.
5. **Probabilistic ≠ untestable.** LLM-as-Judge patterns make non-deterministic outputs measurable and pipeline-integrable.
6. **Human oversight scales differently.** Humans review AI output, not AI input. Focus human judgment on architectural decisions and quality thresholds.
7. **Agents need budgets.** Every agent has cost limits, step count limits, and action whitelists. Unbounded agents are a security and financial risk.
8. **Trace everything.** Every agent action is logged with input, output, model, version, cost, and latency.
9. **The test of autonomy.** Can the agent fail gracefully? Can you roll back in 30 seconds? If not, it's not ready for production.
10. **Governance and speed are not opposites.** Well-governed AI systems move faster because they can be trusted.

---

## Related

- [../13-aidlc-agile-cicd-ai-transformation-2026.md](../13-aidlc-agile-cicd-ai-transformation-2026.md) — Part 1: The Grand Transformation &amp; Lifecycle
- [./10-aidlc-agile-cicd-agile-evolution-cicd-transformation.md](./10-aidlc-agile-cicd-agile-evolution-cicd-transformation.md) — Part 2: Agile Evolution &amp; CI/CD Transformation
- [../01-aidlc-artifacts-discovery-to-model.md](../01-aidlc-artifacts-discovery-to-model.md) — AIDLC Phases 1–4 artifact templates
- [../02-aidlc-artifacts-development-to-retirement.md](../02-aidlc-artifacts-development-to-retirement.md) — AIDLC Phases 5–8 artifact templates
- [../14-aidlc-enterprise-framework-2025.md](../14-aidlc-enterprise-framework-2025.md) — Enterprise AI framework

## Sources

InfoQ (Feb 2026), Thoughtworks SDD Guide (Dec 2025), O'Reilly Signals 2026, IBM Think, Microsoft Azure AI Foundry (Jan 2026), AWS Kiro Documentation, AWS Prescriptive Guidance CI/CD for AI, BMAD-METHOD (Jan 2026), Optimum Partners (Dec 2025), DevOps.com (Feb 2026), mabl Blog (Jan 2026), Unosquare Agile 2026, Medium (Agile Practitioner's Guide), Pulumi Blog AI Predictions 2026, XenonStack AgentOps (Jan 2026), ResearchGate: LLMOps AgentOps MLOps Review, WeBuild-AI Context Engineering (Feb 2026), Alex Cloudstar SDD 2026 (Mar 2026)
