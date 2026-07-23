---
title: "Enterprise AI Architect — Skills Assessment (Part 2 of 2): Scenario Questions, Review Checklist & Resources"
doc_type: reference-architecture
domain: architecture
topic_id: enterprise-ai-skills-assessment-part2
date_created: 2026-07-09
last_reviewed: 2026-07-23
status: current
supersedes: []
source_type: native-md
---

This is Part 2 of 2. [Return to Part 1: Overview, Certifications, Competency Model & Learning Path](pathname:///archon/architecture/52-enterprise-ai-skills-assessment).

---

## 7. EA-Level Scenario Questions

These 20 scenarios reflect real architecture review, consulting, and incident situations. Each has a model answer (3–5 sentences). Use them for interview prep, architecture review practice, or CCA-F scenario practice.

---

**Scenario 1: Data Exfiltration via LLM**

*The CISO raises a concern: "If our customer data is in the LLM context window, what prevents it from being exfiltrated — either by a malicious prompt or by the API provider?" How do you respond architecturally?*

You address three distinct attack surfaces. First, for prompt injection, implement strict input sanitisation at the API gateway layer and use a dedicated guardrail service to detect and block attempts to override system instructions. Second, for internal threats, apply data minimisation by ensuring only necessary data enters the context window — use field-level masking for sensitive identifiers before they hit the prompt. Third, for provider-side risk, reference the DPA and data processing terms with your provider (Anthropic, AWS, Google, Microsoft) which contractually govern how prompt content is handled; ensure you are on an enterprise agreement with no-training commitments on your data. Supplement with output scanning to detect if sensitive data appears in responses bound for external destinations, and implement OTel-based audit logging so every prompt/completion pair is traceable.

---

**Scenario 2: EU Financial Institution Compliance**

*A tier-1 bank in Germany wants to deploy Claude for internal credit memo summarisation and external customer query responses. Walk through the compliance architecture.*

Start by risk-classifying each use case under the EU AI Act: credit memo summarisation that influences lending decisions is likely high-risk under Annex III (creditworthiness assessment); customer query responses may be lower-risk but require transparency obligations if the customer may not know they are interacting with AI. High-risk requirements include conformity assessment, technical documentation, human oversight, accuracy and robustness testing, and registration in the EU database before deployment. Data residency must be confirmed — EU data must remain in EU-hosted infrastructure; use AWS Frankfurt or Azure Germany North via Microsoft Foundry (formerly Azure AI Foundry) with EU Data Boundary enabled. Apply DORA (Digital Operational Resilience Act) requirements: the AI system is an ICT third-party dependency, so the bank must have exit plans, concentration risk assessment, and contractual DORA provisions with Anthropic or the cloud intermediary. Implement HITL gates for any credit decision that is materially influenced by the AI output.

---

**Scenario 3: Business Unit Wants Copilot Enterprise**

*A business unit head wants to roll out GitHub Copilot Enterprise to 200 developers immediately. What governance policies must you have in place before approving?*

Before approval, establish four governance controls. First, a code-in-context policy: define what repositories and data Copilot indexes for the knowledge base — confirm no confidential IP, client data, or regulated data is included in the indexed corpus. Second, a data residency and DPA review: GitHub Copilot Enterprise processes code in Microsoft Azure; confirm the enterprise agreement excludes prompt data from model training and aligns with your jurisdiction's data protection requirements. Third, a licence compliance policy: Copilot can suggest code that matches training data, including potentially licenced code — implement the optional filter for public code suggestions and define your organisation's acceptable use policy for AI-suggested code. Fourth, a measurement baseline: define what success looks like before rollout (developer productivity metrics, code review cycle time, test coverage) so you can evaluate ROI. Require pilot governance with a defined cohort before the full 200-seat rollout.

---

**Scenario 4: Board AI ROI Framework**

*The board asks: "We've invested $2M in AI tooling this year. What's the return?" How do you build the measurement framework?*

ROI for AI investment requires a three-layer measurement model. Layer 1 (efficiency) captures direct productivity gains: developer cycle time reduction, ticket resolution time, document processing throughput — measure before-and-after with control groups. Layer 2 (quality) captures defect reduction, error rates in AI-assisted tasks, and rework rates — AI-assisted code reviews or document drafts should produce measurably fewer post-delivery corrections. Layer 3 (strategic value) captures outcomes that were not previously possible at all: new product features enabled by AI, faster market entry, risks avoided through AI-assisted compliance checking. Attribution is the hardest problem — use a combination of telemetry (token spend correlated to task completion rates) and periodic surveys. Present the board with a simple unit economics view: cost per AI-assisted task, business outcome per cohort, and forward trajectory as adoption scales.

---

**Scenario 5: Production Agent Hallucination Incident**

*A production agent that summarises financial reports starts producing summaries with invented figures. Users have already received 50 incorrect summaries before it was caught. What is your incident response process?*

Execute in four phases. Containment (immediate): disable the agent or route traffic to a fallback; notify all users who received affected summaries; preserve logs of all affected completions for investigation. Investigation: retrieve OTel traces for the affected period; identify what changed — model version, prompt, retrieval corpus, or input data format; determine whether the hallucinations are consistent (same incorrect pattern) or random. Root cause: a likely cause is retrieval failure — the RAG corpus returned no relevant context, and the model hallucinated plausible-sounding figures rather than refusing to answer. Fix: add explicit instructions to cite sources and refuse when no relevant context is retrieved; add a faithfulness guardrail that blocks responses with factual claims not grounded in retrieved context. Post-incident: run the fix through your offline eval harness against the cases that failed, add them to the regression dataset, and implement a faithfulness metric in your production monitoring before reactivating.

---

**Scenario 6: EU AI Act High-Risk Classification**

*Legal has reviewed your AI system that helps HR rank job applicants and flagged it as likely high-risk under the EU AI Act. What are the next steps?*

A recruitment ranking system falls squarely in Annex III, category 4 (employment and workers management), making it high-risk by definition. Required actions before continuing operation: conduct a full conformity assessment covering technical documentation, data governance for training and inference data, human oversight mechanism (no hiring decision can be made solely on the AI's ranking), accuracy and bias testing across protected characteristics, and logging of every AI output for the legal minimum retention period. Register the system in the EU AI Act database. Appoint a responsible person accountable for compliance. Implement a mandatory human review gate — the ranking is advisory only; a human decision-maker must review and approve before candidate progression. If the system was already in operation before the high-risk obligations took effect, you have a transition period but must begin the conformity process immediately and document progress. Involve your DPO given the HR data processing implications.

---

**Scenario 7: Legacy System AI Integration**

*A core banking system from 2004 has no APIs. The business wants AI summarisation of its transaction data. What integration architecture do you propose?*

Without native APIs, the integration must go through the data layer rather than the application layer. Extract transaction data via a scheduled ETL job (reading from the database directly or via an approved reporting interface) into a data intermediary — an event stream or data warehouse — that the AI pipeline can access. The AI system reads from this intermediary, never from the production database directly. Implement a data masking step in the ETL that removes PII and account identifiers before data reaches the LLM context, replacing them with consistent pseudonyms for the session. The summarisation output is returned to a modern interface layer, not written back to the legacy system. This architecture also protects the legacy system from instability: the AI pipeline's load never touches the production system. Document the data flow fully for the DPO review.

---

**Scenario 8: Token Cost Runaway**

*Finance reports that AI API costs doubled month-on-month for the third consecutive month, but business-reported AI usage only grew 20%. How do you investigate and fix?*

The gap between usage growth and cost growth indicates a systemic inefficiency rather than adoption. Start with attribution: segment API costs by application, endpoint, and team using your API gateway logs or cloud cost explorer — identify which workload is growing fastest. Common causes of super-linear cost growth: context window bloat (a RAG pipeline including increasingly large retrieved documents), prompt engineering changes that expanded system prompt length, removal or bypass of prompt caching on high-frequency endpoints, a new feature with uncapped output length, or a model tier upgrade applied broadly. Once the root cause is identified, remediate with targeted interventions: re-enable caching, implement output length caps, swap over-provisioned model tiers to cheaper alternatives for appropriate tasks, add per-feature cost budgets with alerts. Implement a cost governance dashboard that shows cost per feature and alerts when any single feature exceeds its monthly budget by 20%.

---

**Scenario 9: Multi-Cloud AI Strategy**

*The CTO wants to avoid single-cloud lock-in for AI workloads. How do you design a multi-cloud AI architecture without sacrificing coherence?*

Multi-cloud AI strategy requires a portability layer above the cloud-specific SDKs. Design against a unified AI gateway interface that abstracts the underlying cloud — your application code calls the gateway, not Bedrock or Vertex directly. The gateway handles provider routing, credential management, request format translation, and failover. Model portability is harder than platform portability: Claude on Bedrock and Claude on Vertex AI have the same model API but different authentication, network, and compliance properties. Maintain a single semantic model for what each model capability is supposed to do, and test regularly across providers to detect provider-specific drift. The practical multi-cloud strategy for most enterprises is active-passive: primary on one cloud for cost and operational simplicity, with automated failover to a second cloud for resilience. True active-active multi-cloud for AI adds significant orchestration complexity that is rarely worth it for workloads below enterprise scale.

---

**Scenario 10: RAG with Confidential Data**

*The legal team wants a RAG system over 50,000 internal legal documents, many of which are attorney-client privileged. What are the architectural constraints?*

Attorney-client privilege creates strict data handling requirements that most standard RAG architectures violate by default. The entire pipeline must run within the organisation's security boundary — no data sent to third-party embedding APIs or cloud-hosted vector stores without explicit legal clearance. Use self-hosted embedding models (e.g., on-premises or private cloud) and a self-hosted vector database. Implement document-level access control in the retrieval layer: the system must only retrieve documents that the querying user is authorised to access, enforced by ACL checks before documents enter the context window. Add metadata-based privilege marking to the corpus so the retrieval layer can exclude privileged documents from queries where privilege is not established. All query logs are themselves potentially discoverable — store them with appropriate retention policies and under the same privilege controls as the underlying documents. Have legal review the data handling architecture before any data enters the pipeline.

---

**Scenario 11: Developer Productivity Measurement**

*After six months of Copilot Enterprise rollout, the CFO asks whether the $390K annual investment is justified. What data do you present?*

Present a three-metric framework: velocity (did developers ship faster?), quality (did fewer defects reach production?), and developer experience (do developers report higher job satisfaction and reduced toil?). Velocity data comes from your project management and CI/CD tooling — compare lead time, cycle time, and deployment frequency between Copilot cohorts and a matched control group. Quality data comes from defect tracking and code review metrics — compare post-release defect rates, MTTR, and the proportion of code review comments that Copilot-assisted code eliminates. Developer experience comes from periodic surveys with consistent questions across the measurement period. Translate to financial terms by estimating the cost of developer time saved and defects avoided, then compare to the $390K investment. Be clear about what cannot be attributed to Copilot (business-driven scope changes, team composition changes) — credibility with the CFO requires intellectual honesty about attribution limits.

---

**Scenario 12: Shadow AI Proliferation**

*Security discovers 47 teams are using unapproved AI tools — personal ChatGPT accounts, various browser extensions, and multiple unlicensed API integrations. How do you respond?*

This is a governance and cultural issue as much as a security one — prohibition without a good alternative will drive usage further underground. Respond in three tracks simultaneously. Safety track: assess the highest-risk exposures immediately — personal API keys hardcoded in company repositories, client data in ChatGPT conversations, and unauthorised SaaS connected to company SSO — and remediate critical exposures. Governance track: issue a clear AI acceptable use policy that defines what is approved, what requires review, and what is prohibited, with rationale for each category. Enablement track: understand why teams chose unsanctioned tools by interviewing a cross-section of users — the answer is almost always that the approved tooling was absent, slow, or inadequate. Accelerate access to sanctioned tools that meet the most common use cases. Follow up with monitoring via your CASB or network proxy to detect continued unsanctioned use, but frame this to teams as safety monitoring, not surveillance.

---

**Scenario 13: AI Model Drift**

*Six months after deployment, the customer service AI agent's accuracy on complex query types has degraded from 87% to 71%. No code changes were made. What is the cause and remediation?*

When accuracy degrades without code changes, the likely causes are model-side changes, data drift, or corpus drift. Investigate in order: first, check whether the model provider updated the model version — Claude versions can change minor behaviour with releases; confirm whether you are pinned to a specific model version or tracking the latest. Second, check for input data drift — has the distribution of query types changed (e.g., new product launch generating unfamiliar query patterns)? Third, check retrieval corpus drift — if this is a RAG system, has the underlying knowledge base changed in ways that broke retrieval quality for the affected query types? Remediate by re-running your offline eval harness against the affected query categories, identifying the specific failure pattern, updating your eval dataset to include the new failure cases, and retuning prompts or retrieval parameters for the degraded categories. Implement continuous production monitoring so drift is detected automatically — an 87% to 71% drop over six months should have been caught within days with a simple accuracy metric in production.

---

**Scenario 14: Prompt Injection Incident**

*A security pen test finds that users can escape the system prompt of your customer service agent and instruct it to reveal internal documents. What is your architectural response?*

Prompt injection in customer-facing agents is a critical vulnerability because the attack surface is any user input. Remediate with a defence-in-depth approach across four layers. Input layer: implement a dedicated prompt injection classifier (a lightweight model or rule-based scanner) that analyses user input before it reaches the primary agent; block or transform inputs that match injection patterns. Context isolation: ensure internal documents and system instructions are in clearly delimited sections that the model is instructed to treat as authoritative over user instructions; use Anthropic's recommended system prompt structure that distinguishes operator instructions from user input. Output layer: implement output scanning that detects if internal document content (identified by metadata markers) appears in responses. Least privilege: audit what the agent can actually access — internal documents that are not needed for customer query resolution should not be in the retrieval corpus at all. Add this scenario to your red-team evaluation suite so it is tested on every deployment.

---

**Scenario 15: HIPAA Compliance for Healthcare AI**

*A hospital wants to use Claude to assist clinicians in drafting clinical notes. Walk through the HIPAA requirements.*

Clinical notes contain Protected Health Information (PHI) by definition. HIPAA requires a Business Associate Agreement (BAA) with any vendor who processes PHI — confirm Anthropic or your cloud intermediary (AWS, Google, Microsoft) has a BAA in place for the specific service configuration you are using, as BAAs are service-specific and enterprise-tier. All PHI must remain within the covered infrastructure boundary — no logging of PHI in standard access logs, no PHI in error reporting or telemetry that flows to unapproved destinations. Implement audit logging that records who accessed what AI functionality and when, without logging the PHI content itself (log metadata, not content). The clinical note drafting output is the clinician's work product — the AI is a drafting aid, not the author. Ensure the clinical workflow requires explicit clinician review and edit before the note is committed to the EHR — this is both good clinical practice and your HITL control for a high-stakes context. Conduct a HIPAA Security Rule risk assessment specific to this AI integration before go-live.

---

**Scenario 16: AI Vendor Consolidation**

*Your organisation uses five different AI vendors across business units. Procurement wants to consolidate to two. How do you evaluate and recommend?*

Consolidation should be driven by capability coverage and strategic alignment, not cost alone — the cheapest consolidation that forces teams off the best tool for their use case will be resisted and fail. Start with a capability matrix: document what each of the five vendors does for each business unit, and whether that capability is available from the candidate consolidated vendors. Identify true gaps — use cases where the consolidated vendor's model is materially weaker. Calculate total cost of ownership including migration effort, not just per-seat licensing. Evaluate vendor strategic trajectory: which vendor is investing in the capabilities that align with your 3-year AI roadmap? Apply risk scoring: concentration risk increases with consolidation, so the two survivors must have different failure modes (e.g., one Anthropic-based, one Google-based) to avoid common-cause failure. Build a substitution plan — even for your primary vendors — so procurement can negotiate from a position of genuine alternatives. Require the shortlisted vendors to complete your AI vendor security and compliance assessment before selection.

---

**Scenario 17: AI Reliability SLA**

*A business process that previously ran on rule-based automation is being replaced by an LLM agent. The process has a 99.9% uptime SLA. How do you architect for reliability?*

LLM APIs have different reliability characteristics than rule-based systems: model API availability is typically 99.5–99.9%, but response quality can degrade without availability dropping. Design a hybrid architecture rather than full replacement: keep the rule-based system as a fallback for inputs that fall within its deterministic coverage. Implement circuit breakers on the LLM API path with automatic fallback to the rule-based system when the API returns errors or exceeds latency SLA. Add a quality gate on LLM outputs — if the output confidence score or format validation fails, route to the rule-based fallback rather than returning a degraded result. For the 99.9% uptime requirement, note that the LLM API downtime must be invisible to users — the fallback must activate in under 2 seconds. Test the fallback activation path as a first-class scenario in your reliability testing suite. Implement synthetic monitoring that continuously sends representative inputs through the full path and alerts when success rates drop.

---

**Scenario 18: M&A AI Integration**

*Your company acquires a company that has deployed extensive AI systems you know nothing about. What is your 90-day assessment plan?*

The 90-day plan has three phases. Discovery (days 1–30): inventory all AI systems — applications, APIs, models, vendors, data flows, and costs. Map each system to a business process and risk category. Identify which systems process regulated data (PII, PHI, financial data) and which affect consequential decisions. This is also your prompt injection and model security audit phase — red-team the highest-risk systems. Assessment (days 31–60): apply your AI governance framework to each system — which ones meet your standards, which have gaps, which are unacceptable risks. Evaluate vendor contracts for exit clauses, BAAs, and DPA alignment with your standards. Identify the systems with the most technical debt (no evals, no observability, no human oversight) — these are your highest remediation priorities. Remediation planning (days 61–90): for each system, classify as adopt (meets standards), remediate (fixable within 180 days), replace (rebuild on your stack), or retire (decommission). Build the roadmap with resource estimates and risk-ordered sequencing. Brief the CISO and CPO on findings before day 90.

---

**Scenario 19: Cross-Jurisdictional Privacy Conflict**

*Your AI system processes data from users in the EU (GDPR), California (CCPA), and Brazil (LGPD). The system logs all prompts for safety monitoring. How do you manage the conflict between safety monitoring needs and privacy regulation?*

All three regulations require a lawful basis for processing personal data, and all three give data subjects rights (access, deletion, portability) that create obligations on your log store. The safety monitoring purpose is legitimate and can usually be grounded in legitimate interests (GDPR) or business purpose (CCPA/LGPD) — document this in your Record of Processing Activities. Implement data minimisation in logs: strip or pseudonymise personal identifiers before storing, retain only what is necessary for the safety monitoring purpose. Define and enforce retention periods — safety logs rarely need to be retained beyond 90 days for their primary purpose; implement automated deletion at the retention boundary. Build a data subject request workflow that can fulfil GDPR access and deletion requests against the log store — this is technically complex for pseudonymised data but required. Consult your DPO on whether the log data crosses into special category data territory (health, political opinions) for any of your user populations — this triggers stricter GDPR requirements.

---

**Scenario 20: Board AI Strategy Presentation**

*The board allocates 90 minutes for an AI strategy review. What do you present and in what order?*

Structure the 90 minutes in four segments. Segment 1 — Current state (15 min): where you are today — deployed systems, costs, measured ROI, capability inventory, and the three highest risks on your AI risk register. Boards need a clear picture of what they already own before evaluating what to do next. Segment 2 — Market and competitive context (15 min): what the technology landscape looks like in 2026, what your competitors are doing, and the cost of inaction. Keep this factual and brief — boards are sophisticated but not AI specialists. Segment 3 — Strategic options (30 min): present three credible alternative AI strategies (conservative/moderate/aggressive adoption), each with 3-year cost, capability, and risk profiles. Include a recommended option with clear rationale. Segment 4 — Governance and risk (30 min): the board's primary AI responsibility is governance, not strategy execution. Spend disproportionate time on: AI governance structure (who is responsible?), regulatory compliance status and roadmap, risk register top items and mitigations, and what decisions you are asking the board to make. End with explicit asks: approve strategy, fund programme, delegate authority.

---

## 8. AI Architecture Review Checklist

Use this 30-point checklist when reviewing a new AI system design or auditing an existing one. Each item is a binary check: pass or fail with a finding note.

### Security (5 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| S1 | Prompt injection risk assessed; mitigations designed and documented | | |
| S2 | All secrets (API keys, credentials) stored in a secrets manager — no hardcoding | | |
| S3 | Tool and MCP server access follows least-privilege — each agent has only the permissions it requires | | |
| S4 | Sensitive data is masked or excluded before entering LLM context | | |
| S5 | Output scanning implemented to prevent data leakage in responses | | |

### Compliance & Governance (5 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| C1 | EU AI Act risk classification completed and documented; high-risk obligations identified | | |
| C2 | Data Processing Agreement (DPA) executed with all AI vendors processing personal data | | |
| C3 | Data residency requirements met; confirmed no cross-border transfer violations | | |
| C4 | AI acceptable use policy covers this system's capabilities and users | | |
| C5 | Incident response plan includes AI-specific failure scenarios (hallucination, drift, outage) | | |

### Cost & Token Economics (4 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| T1 | Per-feature token budget defined and enforced | | |
| T2 | Prompt caching enabled on all high-frequency, stable system prompt content | | |
| T3 | Model tier matched to task complexity — no over-provisioning of expensive models for simple tasks | | |
| T4 | Monthly cost alert configured; finance notified of cost attribution approach | | |

### Performance & Reliability (4 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| P1 | Latency SLA defined; P95 latency measured in load test | | |
| P2 | Circuit breaker implemented on LLM API path with documented fallback behaviour | | |
| P3 | Retry logic implemented with exponential backoff and jitter | | |
| P4 | System tested under 2x expected peak load without degradation beyond SLA | | |

### Human-in-the-Loop (3 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| H1 | Action categories requiring human approval identified and documented | | |
| H2 | HITL gates implemented and tested for all irreversible or high-impact actions | | |
| H3 | Timeout handling defined for HITL gates — system knows what to do if human does not respond | | |

### Observability (4 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| O1 | OTel tracing instrumented on all agent actions, tool calls, and decision branches | | |
| O2 | Traces shipped to an observability backend with defined retention period | | |
| O3 | Alert configured for anomalous error rates, latency spikes, or cost events | | |
| O4 | Governance dashboard exists showing system health, cost, and evaluation scores | | |

### Evaluation & Quality (4 items)

| # | Check | Pass/Fail | Finding |
| --- | ------- | ----------- | --------- |
| E1 | Offline evaluation dataset exists with at least 50 representative test cases | | |
| E2 | Evaluation runs in CI/CD and blocks deployment on regression | | |
| E3 | Acceptance thresholds defined collaboratively with governance stakeholders | | |
| E4 | Production sampling implemented; flagged outputs routed to human review | | |

### Documentation (1 item)

| # | Check | Pass/Fail | Finding |
|---|-------|-----------|---------|
| D1 | Architecture decision records (ADRs) exist for all major design choices; data flow diagram current and accurate | | |

A failing check is a finding, not a blocker by default. Each finding requires a remediation plan with a target date. Systems with more than 5 open findings in the Security or Compliance categories should not proceed to production until critical items are addressed.

---

## 9. Resources and Communities

### Guides in This Site to Study (by Learning Path Stage)

**Beginner:**

- [Enterprise AI Architect — Foundations](pathname:///archon/architecture/48-enterprise-ai-architect-foundations) — start here
- [Models 2026](pathname:///archon/agentic-systems/coding-tools/35-claude-models-2026) — model selection and pricing
- [Prompt Engineering](pathname:///archon/agentic-systems/coding-tools/40-prompt-engineering-claude-4) — the craft of prompting
- [CCA-F Exam Prep — Complete Guide](pathname:///archon/career/37-cert-ccaf-exam-prep) — certification preparation

**Intermediate:**

- [MCP Deep Guide](pathname:///archon/agentic-systems/coding-tools/39-mcp-deep-guide) — MCP protocol and server development
- [Agent SDK Production](pathname:///archon/agentic-systems/coding-tools/30-claude-agent-sdk-production) — multi-agent code and patterns
- [Enterprise Deployment](pathname:///archon/agentic-systems/coding-tools/34-claude-enterprise-2026) — cloud platforms, security, cost
- [Constitutional AI & Safety](pathname:///archon/agentic-systems/coding-tools/38-constitutional-ai-safety-2026) — harm taxonomy and safety design
- [Architecture Patterns](pathname:///archon/architecture/49-enterprise-ai-architecture-patterns) — the canonical 15-pattern reference

**Expert:**

- [Governance & Compliance](pathname:///archon/architecture/51-enterprise-ai-governance-compliance) — regulatory frameworks and policy
- [Multi-Agent Orchestration](pathname:///archon/agentic-systems/coding-tools/41-ruflo-agentic-ai-guide) — orchestration frameworks and evaluation
- [GitHub Copilot Enterprise](pathname:///archon/agentic-systems) — enterprise developer AI tooling
- [API Mastery](pathname:///archon/agentic-systems/coding-tools/31-claude-api-mastery) — advanced API patterns

### External Resources

| Resource | What it covers | URL |
| ---------- | --------------- | ----- |
| Anthropic Documentation | Claude API reference, model cards, safety policies | docs.anthropic.com |
| MCP Specification | Model Context Protocol official spec and registry | modelcontextprotocol.io |
| EU AI Act Text | Full regulation text and implementing acts | eur-lex.europa.eu |
| NIST AI RMF | Risk Management Framework, playbook | nist.gov/system/files/documents/2023/01/26/AI RMF 1.0.pdf |
| ISO 42001 Overview | AI management system standard | iso.org/standard/81230.html |
| Anthropic Partner Network | CCA-F voucher eligibility, partner resources | anthropic.com/partners |
| Pearson VUE | CCA-F exam registration | home.pearsonvue.com |
| GitHub Copilot Documentation | Copilot Enterprise admin and governance | docs.github.com/en/copilot |
| AGENTSAFE Framework | Agentic AI governance methodology | arxiv.org/pdf/2512.03180 |
| OpenTelemetry | Vendor-neutral tracing specification | opentelemetry.io |

---

*Assessment current as of July 2026. CCA-F exam domains and passing scores are as published by Anthropic at launch on 12 March 2026. Review [Anthropic's official certification page](https://anthropic.com) for any updates to exam format or domain weights.*

[Return to Part 1: Overview, Certifications, Competency Model & Learning Path](pathname:///archon/architecture/52-enterprise-ai-skills-assessment)
