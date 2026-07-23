---
title: "Enterprise AI Architect — Skills Assessment (Part 1 of 2): Overview, Certifications, Competency Model & Learning Path"
doc_type: reference-architecture
domain: architecture
topic_id: enterprise-ai-skills-assessment
date_created: 2026-07-09
last_reviewed: 2026-07-23
status: current
supersedes:
  - docs/enterprise-architecture/ai-architecture/enterprise-ai-skills-assessment.md
source_type: native-md
---

This is Part 1 of 2. [Continue to Part 2: Scenario Questions, Review Checklist & Resources](pathname:///archon/architecture/parts/21-enterprise-ai-skills-assessment-part2).

---

# Enterprise AI Architect — Skills Assessment

**Audience:** Architects assessing their AI readiness, teams hiring or developing EA-AI capability, practitioners preparing for the CCA-F certification.

**Purpose:** A structured competency model, self-assessment tool, and learning path for Enterprise AI Architects — paired with 20 scenario-based interview/review questions that test real EA judgment.

**What this does NOT duplicate:**

- Governance policy details → [Governance & Compliance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance)
- Architecture pattern implementations → [Architecture Patterns](pathname:///archon/architecture/49-enterprise-ai-architecture-patterns)
- Claude model pricing and selection → [Models 2026](pathname:///archon/agentic-systems/coding-tools/35-claude-models-2026)
- CCA-F exam question practice → [CCA-F Exam Prep](pathname:///archon/career/37-cert-ccaf-exam-prep)

---

## 1. Overview

This assessment serves three purposes:

1. **Individual self-assessment** — benchmark your current AI architecture capability against the competency model, identify gaps, and select your learning path.
2. **Team capability planning** — map collective skills, spot coverage gaps, and plan targeted skill investments.
3. **CCA-F alignment** — every domain in the competency model maps to one or more CCA-F exam domains, so preparation for this assessment is preparation for the exam.

### Who Should Use This

| Role | How to use this assessment |
| ------ | --------------------------- |
| **Aspiring EA-AI** | Complete self-assessment, identify gaps, follow beginner or intermediate path |
| **Practicing EA-AI** | Use scenario questions as mock architecture review or interview prep |
| **Engineering manager** | Use competency table to define hiring criteria and growth plans |
| **Architect reviewing AI adoption** | Use the 30-point architecture review checklist for project evaluations |
| **Certification candidate** | Use CCA-F mapping to prioritise study effort |

---

## 2. Enterprise AI Architect Certifications (2026)

### 2026 Certification Landscape

The EA-AI certification landscape expanded significantly in 2026. Three credentials now cover the core of the role; a fourth (Google) is emerging. Choose based on your primary platform and role focus:

| Certification | Issuer | Cost | Focus | Status |
| --- | --- | --- | --- | --- |
| **CCA-F** — Claude Certified Architect, Foundations | Anthropic (via Pearson VUE) | $99 | Agentic architecture, MCP/tool design, prompt engineering, context management; Claude-centric | GA since Mar 12, 2026 |
| **AB-100** — Agentic AI Business Solutions Architect | Microsoft (via Microsoft Learn) | $165 | Multi-agent orchestration, Copilot Studio, Microsoft Foundry, MCP, A2A, enterprise deployment; Microsoft-centric | GA; updated July 22, 2026 |
| **AWS Certified AI Practitioner** | AWS | $150 | Foundational AI/ML on AWS, Bedrock, responsible AI; broad coverage, less architect-depth | GA; updated 2025 |
| **Professional Cloud Architect + GenAI** | Google Cloud | $200 | GCP infrastructure + Vertex AI; no agentic-specific cert as of July 2026 | Track: Professional Cloud Architect |

**For enterprise AI architects: CCA-F + AB-100 is the recommended combination.** CCA-F validates agentic design judgment independent of platform; AB-100 validates the Microsoft-specific stack that dominates enterprise deployments (Copilot Studio, Foundry, Entra Agent ID). Together they cover ~80% of what enterprise clients will ask for in RFPs and vendor assessments.

### AB-100 — Agentic AI Business Solutions Architect

The **AB-100** ([Microsoft Learn](https://learn.microsoft.com/en-us/credentials/certifications/agentic-ai-business-solutions-architect/)) is Microsoft's flagship architect credential for the agentic era, updated July 22, 2026:

| Item | Detail |
| ------ | -------- |
| Full name | Microsoft Certified: Agentic AI Business Solutions Architect |
| Exam code | AB-100 |
| Cost | $165 USD |
| Format | Online proctored; scenario-based |
| Prerequisite | None (but assumes familiarity with Azure and M365) |
| Study guide | [Microsoft Learn study guide — AB-100](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ab-100) |

**AB-100 domains** (July 2026 update):

| Domain | Coverage |
| --- | --- |
| Agent design principles | Bounded autonomy, decision-rights, HITL gates |
| Copilot Studio & Foundry | Agent creation, MCP server integration, publishing |
| Multi-agent orchestration | A2A v1.0, agent-to-agent delegation, registry patterns |
| Enterprise governance | Entra Agent ID, audit logging, compliance controls |
| Responsible AI | Microsoft RAI framework, content filters, transparency |

### CCA-F Certification for Enterprise Architects

### Why CCA-F Matters for EA Practitioners

The **Claude Certified Architect, Foundations (CCA-F)** exam — launched 12 March 2026 via Pearson VUE — is the first vendor-neutral certification specifically targeting practitioners who design and operate AI systems using Claude. For Enterprise AI Architects, it validates a precise set of skills that sit at the intersection of agentic design, tool orchestration, prompt engineering, and context reliability.

Unlike generic cloud certifications, CCA-F tests architecture judgment: the ability to select the right orchestration pattern, design safe tool interfaces, manage context windows under real production constraints, and evaluate model outputs systematically. These are exactly the decisions EA-AIs make daily.

For EA practitioners already working with Claude, CCA-F provides external credibility with clients, procurement stakeholders, and regulators who increasingly expect evidence of structured AI competency — not just engineering experience.

### Exam Facts at a Glance

| Item | Detail |
| ------ | -------- |
| Full name | Claude Certified Architect, Foundations |
| Launched | 12 March 2026 |
| Platform | Pearson VUE (online proctored) |
| Questions | 60 scenario-based multiple choice |
| Duration | 120 minutes |
| Passing score | 720 / 1000 |
| Cost | $99 USD |
| Cost (Partner Network) | Free for first 5,000 qualifying partner employees |
| Validity | 2 years |
| Prerequisite | None |

### CCA-F Domain Mapping to EA Responsibilities

| CCA-F Domain | Weight | Questions | EA Responsibility It Validates |
| ------------- | -------- | ----------- | ------------------------------- |
| D1: Agentic Architecture & Orchestration | 27% | ~16 | Multi-agent topology design, orchestrator vs. subagent patterns, delegation and error handling |
| D2: Tool Design & MCP Integration | 18% | ~11 | MCP server design, tool interface contracts, security boundaries, 10,000+ public MCP server ecosystem (~110M monthly SDK downloads; governed by the Linux Foundation's Agentic AI Foundation since Dec 2025) |
| D3: Claude Code Configuration & Workflows | 20% | ~12 | Developer toolchain governance, CI/CD integration, hooks and automations |
| D4: Prompt Engineering & Structured Output | 20% | ~12 | Prompt standards, output schemas, evaluation harness design, regression testing |
| D5: Context Management & Reliability | 15% | ~9 | Token budget governance, context window design, reliability patterns, cost optimisation |

:::tip EA exam strategy
    EA-AIs typically find D1 and D5 most challenging because they require architectural synthesis, not just feature recall. D2 and D4 reward practitioners who have shipped production systems. Prioritise D1 depth first — it carries the highest weight and tests the most complex judgment calls.

### Registration

1. Register via [Pearson VUE](https://home.pearsonvue.com/) — search for "Anthropic" or "Claude Certified Architect"
2. If your organisation is a Claude Partner Network member, check eligibility for the free first-5,000 voucher before paying
3. Full preparation: [CCA-F Exam Prep — Complete Guide](pathname:///archon/career/37-cert-ccaf-exam-prep)

---

## 3. Enterprise AI Architect Competency Model

Each competency area has three levels:

- **Awareness** — Understands the concept; can have an informed conversation; cannot design or build without assistance
- **Practitioner** — Can design and implement independently; has done it in real projects; can review others' work
- **Expert** — Leads architectural decisions; defines standards; mentors others; handles edge cases and failure modes

### 3.1 Technical Competencies

| Competency Area | Awareness | Practitioner | Expert |
| ---------------- | ----------- | -------------- | -------- |
| **LLM APIs & SDKs** | Understands request/response model; knows what a system prompt is | Builds production integrations; handles streaming, errors, retries | Designs multi-provider abstraction layers; owns token/cost strategy; tunes retry policies |
| **Agent Patterns** | Knows what an agent is; understands tool use conceptually | Implements sequential, fan-out, and DAG patterns; handles tool errors | Designs multi-agent topologies; makes orchestration vs. chaining vs. routing decisions at system level |
| **MCP** | Knows MCP exists; understands the tool/resource/prompt distinction | Builds and registers MCP servers; configures auth; uses public registry | Designs MCP server architecture for enterprise; governs a catalogue of 10+ internal servers; designs stateless vs. stateful MCP strategy |
| **RAG & Vector Databases** | Understands retrieval-augmented generation; knows what a vector store is | Builds production RAG pipelines; selects chunking and embedding strategies; evaluates faithfulness | Designs multi-stage retrieval; handles corpus scale, staleness, and citation accuracy; architects hybrid search |
| **Prompt Engineering** | Writes basic prompts; understands role of system prompts | Applies chain-of-thought, few-shot, structured output, and constitutional techniques | Runs prompt regression suites; designs prompt templates at enterprise scale; optimises for cost and accuracy simultaneously |
| **Token Economics** | Knows tokens = cost; understands context windows | Estimates token budgets; implements caching; manages context stuffing | Designs cost allocation frameworks; implements per-feature token budgets; builds cost dashboards; governs batch vs. real-time trade-offs |
| **Evaluation Harness** | Knows evals exist; has heard of LLM-as-a-judge | Builds offline eval datasets; implements basic LLM-as-a-judge pipelines; tracks metric baselines | Designs 3-layer eval frameworks (output, trajectory, business); integrates evals into CI/CD; defines acceptance thresholds with governance teams |
| **Observability** | Understands the need for logging; knows what OTel is | Instruments agents with OTel traces; ships to a backend; reads traces | Designs AI observability architecture; owns eval-to-trace integration; builds governance dashboards on top of trace data |

### 3.2 Architecture Competencies

| Competency Area | Awareness | Practitioner | Expert |
| ---------------- | ----------- | -------------- | -------- |
| **System Design** | Understands component diagrams; can read an architecture document | Designs AI-augmented systems end-to-end; makes make-vs-buy decisions; documents ADRs | Designs for scale, resilience, and cost simultaneously; leads architecture review boards; defines reference architectures |
| **Integration Patterns** | Knows REST and event-driven patterns exist | Integrates AI APIs into enterprise systems; handles async flows; manages API versioning | Designs AI gateway layer; governs API contract changes; handles backward compatibility at org scale |
| **Security Architecture** | Knows AI has security risks; understands prompt injection conceptually | Implements input/output filtering; designs secret management; applies least-privilege to tool access | Designs enterprise AI security model; conducts threat modelling; governs tool permission matrices; responds to prompt injection incidents |
| **Data Architecture** | Understands that AI needs data; knows what RAG is | Designs data pipelines for RAG; handles PII masking; implements data classification | Designs AI data governance at enterprise scale; owns data lineage for AI inputs; architects multi-tenant data isolation |
| **Cloud Platforms** | Has used one cloud provider; knows Claude is on Bedrock/Vertex/Azure | Deploys Claude on at least one cloud platform; configures VPC endpoints and IAM; estimates cloud costs | Designs multi-cloud AI strategy; makes platform selection decisions; governs cross-cloud cost and compliance |

### 3.3 Governance Competencies

| Competency Area | Awareness | Practitioner | Expert |
| ---------------- | ----------- | -------------- | -------- |
| **AI Policy** | Knows AI governance policies exist; has read their company's AI policy | Implements policy controls in AI systems; documents policy compliance; participates in policy reviews | Drafts and owns AI governance policies; leads policy review cycle; bridges technical and legal language |
| **Compliance** | Knows EU AI Act, GDPR, HIPAA names; understands high-risk classification exists | Maps specific AI systems to applicable regulations; identifies gaps; prepares compliance artefacts | Leads regulatory compliance programmes for AI; interprets new regulations for technical teams; manages regulatory relationship |
| **Risk Management** | Understands risk registers exist; can name AI risk categories | Maintains AI risk register; rates and tracks risks; escalates appropriately | Designs enterprise AI risk framework; owns risk appetite decisions; governs risk across portfolio of AI systems |
| **Vendor Management** | Knows the org uses AI vendors; understands DPA concept | Completes vendor assessments; reviews SLAs; monitors vendor compliance commitments | Owns AI vendor strategy; negotiates contracts; manages multi-vendor risk; governs vendor substitution plans |

### 3.4 Leadership Competencies

| Competency Area | Awareness | Practitioner | Expert |
| ---------------- | ----------- | -------------- | -------- |
| **Stakeholder Management** | Can present to technical peers; understands different stakeholders exist | Presents AI proposals to non-technical executives; manages competing stakeholder interests; builds consensus | Drives board-level AI investment decisions; manages C-suite relationships; translates AI risk into business language |
| **Change Management** | Understands change management exists; has participated in change programmes | Leads AI adoption initiatives; designs developer enablement programmes; manages resistance | Leads enterprise AI transformation; redesigns operating models; manages cultural change at scale |
| **AI Strategy** | Has read about AI strategy; understands the concept of an AI roadmap | Develops team-level AI roadmaps; prioritises AI investments within a domain | Develops enterprise AI strategy; aligns AI capability to business objectives; presents to board; governs strategy execution |

---

## 4. Self-Assessment Checklist

Answer Yes (1) or No (0) for each item. Score yourself at the end.

### Domain A: Technical Foundations (Questions 1–5)

| # | Question | Y/N |
| --- | ---------- | ----- |
| 1 | I can explain token pricing for at least two current Claude models and calculate a monthly cost estimate for a given workload | |
| 2 | I have built at least one production or near-production AI integration using a real LLM API (not just a UI wrapper) | |
| 3 | I can explain what an MCP server is, what resources/tools/prompts it exposes, and when you would build one vs. use an existing one | |
| 4 | I have designed or reviewed a RAG pipeline and can explain chunking, embedding, retrieval, and faithfulness evaluation | |
| 5 | I can implement prompt caching and explain when it saves money vs. increases cost | |

### Domain B: Agent Architecture (Questions 6–10)

| # | Question | Y/N |
| --- | ---------- | ----- |
| 6 | I can draw a multi-agent architecture diagram for a real use case and explain why I chose that topology over alternatives | |
| 7 | I understand the difference between an orchestrator agent and a subagent and can explain how error handling differs between them | |
| 8 | I can explain what HITL is, give three examples of action categories that should require human approval, and describe how to implement a HITL gate in an agent workflow | |
| 9 | I have designed or reviewed an evaluation harness for an AI agent (not just tested it manually) | |
| 10 | I know what "context window pressure" is and can describe at least two techniques to manage it in a long-running agent | |

### Domain C: Governance & Compliance (Questions 11–15)

| # | Question | Y/N |
| --- | ---------- | ----- |
| 11 | I can classify an AI system under the EU AI Act high-risk categories and explain what compliance obligations follow | |
| 12 | I have contributed to or reviewed an AI governance policy document (not just read one) | |
| 13 | I can explain the NIST AI RMF's four core functions (Govern, Map, Measure, Manage) and give one concrete action under each | |
| 14 | I can describe what ISO 42001 requires for an AI management system and how it relates to ISO 27001 | |
| 15 | I know what a Data Processing Agreement (DPA) is, why AI vendors require one, and what to check before signing | |

### Domain D: Enterprise Architecture Skills (Questions 16–20)

| # | Question | Y/N |
| --- | ---------- | ----- |
| 16 | I can make a build-vs-buy-vs-configure decision for an AI capability with a structured decision framework | |
| 17 | I have presented an AI architecture proposal to senior stakeholders and addressed questions about cost, risk, and business value | |
| 18 | I can design an AI observability stack (what to instrument, where to ship data, what dashboards to build) for a production agent system | |
| 19 | I know what prompt injection is, can explain how it differs from traditional injection attacks, and can describe three mitigation strategies | |
| 20 | I have conducted or participated in an AI architecture review using a structured checklist or framework | |

### Scoring

| Score | Level | Interpretation |
| ------- | ------- | --------------- |
| 0–8 | Beginner | Strong foundation in adjacent skills; focus first on the technical competency areas (Domains A and B) |
| 9–14 | Practitioner | Working knowledge across most areas; deepen governance competencies and target scenario-based practice |
| 15–20 | Expert | Broad EA-AI mastery; focus on leadership competencies and edge-case scenario depth |

---

## 5. Learning Path

### Beginner Path (0–6 Months)

Goal: Build the technical foundation and design first working AI systems.

**Months 1–2: Foundations**

- Read [Enterprise AI Architect — Foundations](pathname:///archon/architecture/48-enterprise-ai-architect-foundations) in full — this is your landscape map
- Complete [Models 2026](pathname:///archon/agentic-systems/coding-tools/35-claude-models-2026) — understand model selection, pricing tiers, and capability differences
- Build a simple LLM integration from scratch using the Anthropic API: no framework, just direct API calls with retry logic
- Read the [Prompt Engineering guide](pathname:///archon/agentic-systems/coding-tools/40-prompt-engineering-claude-4) and implement three different prompting techniques on a real problem

**Months 3–4: Agents and Tools**

- Read [MCP Deep Guide](pathname:///archon/agentic-systems/coding-tools/39-mcp-deep-guide) — understand the protocol, build a simple MCP server
- Read [Agent SDK Production](pathname:///archon/agentic-systems/coding-tools/30-claude-agent-sdk-production) — implement a two-agent workflow
- Study D1 and D2 of the [CCA-F Exam Prep guide](pathname:///archon/career/37-cert-ccaf-exam-prep)
- Build a small RAG pipeline: ingest a document corpus, embed, store in a vector DB, retrieve, and evaluate faithfulness

**Months 5–6: First Systems**

- Read [Architecture Patterns](pathname:///archon/architecture/49-enterprise-ai-architecture-patterns) — sections 1–8 cover the patterns you'll encounter most
- Design (on paper) an end-to-end AI system for a real problem in your organisation
- Study D4 and D5 of [CCA-F Exam Prep](pathname:///archon/career/37-cert-ccaf-exam-prep) and sit a mock exam
- Register for CCA-F if you score 70%+ on mock questions

### Intermediate Path (6–12 Months)

Goal: Ship production-grade AI systems with proper observability and governance.

**Months 7–8: Production Engineering**

- Study [Claude Enterprise 2026](pathname:///archon/agentic-systems/coding-tools/34-claude-enterprise-2026) — multi-cloud deployment, Bedrock/Vertex/Azure
- Implement a 3-layer evaluation harness (see Part 2, Section 6: Evaluation Harness Design)
- Add OTel instrumentation to an existing agent and ship traces to an observability backend
- Run your first load test on an AI endpoint and document the latency/cost profile

**Months 9–10: Governance**

- Read [Enterprise AI Governance & Compliance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance) in full
- Map a real AI system you own to EU AI Act risk categories and identify compliance gaps
- Draft an AI governance policy for your team using the NIST AI RMF structure
- Review [Constitutional AI & Safety](pathname:///archon/agentic-systems/coding-tools/38-constitutional-ai-safety-2026) for harm taxonomy and four-tier priority model

**Months 11–12: Multi-Agent at Scale**

- Read [Multi-Agent Orchestration](pathname:///archon/agentic-systems/coding-tools/41-ruflo-agentic-ai-guide) — study framework comparison, evaluation framework, and guardrail patterns
- Design and implement a multi-agent workflow with HITL gates
- Present your AI system design to a senior stakeholder and incorporate their feedback
- Build your first cost governance dashboard with per-feature token attribution

### Expert Path (12+ Months)

Goal: Lead AI architecture at organisational scale; define standards; govern a portfolio.

- Define a reference architecture for your organisation's primary AI pattern (agent, RAG, hybrid)
- Build and run an Architecture Review Board process for AI systems — use the 30-point checklist in Part 2
- Draft your organisation's AI vendor assessment framework and evaluate two vendors against it
- Contribute to or lead an EU AI Act compliance programme for a high-risk system
- Develop an enterprise AI strategy document and present it to C-suite
- Mentor two junior practitioners through the Beginner or Intermediate path above
- Sit CCA-F and pursue any available advanced certifications

---

## 6. Key Concepts an Enterprise AI Architect Must Master

### 6.1 Token Economics and Cost Modelling

Token economics is the discipline of translating AI API usage into predictable, controllable cost. Unlike compute instances with fixed hourly prices, LLM costs are proportional to both input and output token volumes — and both are driven by architectural decisions. A RAG pipeline that stuffs 40,000 tokens of context per query costs 20x more per call than one that retrieves 2,000 tokens of relevant context. Architects must own a token budget at the feature level, track actuals vs. budget in production, and make deliberate trade-offs between context richness and cost. Prompt caching, batching, model routing (use Haiku for simple classification, Sonnet for reasoning, Fable for complex multi-step), and output length controls are the primary levers. For pricing details by model, see [Models 2026](pathname:///archon/agentic-systems/coding-tools/35-claude-models-2026).

### 6.2 Evaluation Harness Design

An evaluation harness is the automated system that continuously measures whether an AI system performs as intended. A well-designed harness operates across three layers: output quality (is this response correct, relevant, and safe?), trajectory quality (did the agent use the right tools in the right order?), and business alignment (did the system achieve the goal at acceptable cost and latency?). The harness must run on every code change that touches agents, prompts, or tools — integrated into CI/CD as a deployment gate. LLM-as-a-judge scales quality assessment beyond what human reviewers can handle. Maintaining a baseline dataset that accumulates production failures prevents regression from going undetected. See [Architecture Patterns](pathname:///archon/architecture/49-enterprise-ai-architecture-patterns) for the LLM-as-judge harness pattern.

### 6.3 Guardrail Architecture

Guardrails are the technical controls that prevent AI systems from producing harmful, unsafe, or policy-violating outputs. They operate at two boundaries: input (what enters the model's context) and output (what leaves the system and reaches users or downstream tools). Input guardrails filter prompt injection attempts, PII, and adversarial content. Output guardrails detect hallucinations, safety violations, confidential data leakage, and format non-compliance. The design question is where guardrails run: as a pre/post-call wrapper in application code, as a dedicated guardrail service on the API path, or as a cloud-native service (e.g., Amazon Bedrock Guardrails). Each has different latency, cost, and coverage trade-offs. See [Governance & Compliance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance) for policy-as-code patterns.

### 6.4 Governance Framework Selection

Three frameworks dominate enterprise AI governance: EU AI Act (legally binding in the EU, risk-tiered, extraterritorial reach), NIST AI RMF (voluntary, process-oriented, widely adopted in the US), and ISO 42001 (certifiable management system standard, global). These are complementary, not competing: NIST AI RMF maps well to ISO 42001 clauses; EU AI Act compliance generates the artefacts that ISO 42001 audits expect. Most enterprise architects end up implementing all three in parallel. The key EA decision is which framework drives the primary governance operating model — typically the one with the highest regulatory exposure for the organisation — with the others layered on top. See [Governance & Compliance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance) for detailed framework breakdowns.

### 6.5 RAG System Design

Retrieval-Augmented Generation solves the knowledge currency problem for LLMs: foundation models have training cutoffs, but enterprise knowledge is always-changing. A production RAG system has five design dimensions: ingestion (how data enters the corpus and stays current), chunking (how documents are split for retrieval — fixed-size, semantic, hierarchical), embedding (which model, updated when models change), retrieval (dense vector, sparse keyword, or hybrid), and faithfulness evaluation (did the model actually use the retrieved context, or hallucinate over it?). The most common EA failure is underestimating corpus maintenance cost — embeddings must be re-indexed when source documents change, the embedding model is upgraded, or the chunking strategy changes. See [Architecture Patterns](pathname:///archon/architecture/49-enterprise-ai-architecture-patterns) for the RAG and Agentic RAG patterns.

### 6.6 Multi-Agent Orchestration at Scale

Multi-agent systems decompose complex tasks across specialised agents running in parallel or sequence. The EA-level decision is topology: hierarchical (orchestrator delegates to workers — predictable, auditable, good for complex coding and research), peer-to-peer (agents share a memory pool — higher coordination complexity, better for consensus tasks), or pipeline (sequential stages — simplest to reason about, lowest overhead). At enterprise scale, the additional concerns are agent failure isolation (one agent failing should not cascade), shared memory contention (agents writing to the same state simultaneously), token budget management per agent, and governance visibility (can you trace which agent made which decision?). See [Multi-Agent Orchestration](pathname:///archon/agentic-systems/coding-tools/41-ruflo-agentic-ai-guide) for framework options and patterns.

### 6.7 HITL Integration Patterns

Human-in-the-Loop is not a single pattern — it is a spectrum from full human oversight to near-full automation, with specific decision points for when humans must be consulted. The EA decision is which action categories require human approval before proceeding, which require human review after the fact, and which can run fully autonomously. Irreversible actions (production deployments, financial transactions, data deletion), high-impact decisions (contract approvals, customer-facing communications), and edge cases that fall outside the model's confidence should trigger human gates. Technical implementation options include async approval queues, synchronous blocking gates with timeout handling, and supervisor loops that monitor agent outputs and escalate anomalies. The HITL design must specify what happens when a human does not respond within the timeout window.

### 6.8 AI Vendor Management

AI vendor relationships carry specific risks that traditional software vendor management frameworks do not fully address: model behaviour changes between versions, training data opacity, subprocessor chains for data sent to model APIs, and the speed at which vendor capabilities change relative to contract cycles. The EA must establish a vendor assessment process that covers model cards and safety evaluations, DPA terms for data sent to model APIs, subprocessors and data residency, SLA and uptime commitments, version change notification and backward compatibility guarantees, and viable substitution options if the vendor relationship ends. Single-vendor dependency on a foundation model provider is a key enterprise risk — design for model portability from the beginning, even if you start with a single provider. See [Governance & Compliance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance) for the vendor assessment checklist.

---

[Continue to Part 2: Scenario Questions, Review Checklist & Resources](pathname:///archon/architecture/parts/21-enterprise-ai-skills-assessment-part2)
