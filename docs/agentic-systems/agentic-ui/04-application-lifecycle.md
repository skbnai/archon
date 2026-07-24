---
title: "Agentic Application Lifecycle"
date_created: 2026-07-24
last_reviewed: 2026-07-24
status: current
domain: agentic-systems
doc_type: guide
topic_id: application-lifecycle
covers_version: "as of 2026-07-10"
supersedes:
  - docs/agentic-ui/application-lifecycle.md
---

# Agentic Application Lifecycle

**Audience:** Enterprise architects, AI platform teams, and product owners governing the full delivery journey of production agentic applications from ideation through retirement.

**Related:**
[Architecture Patterns](../enterprise-architecture/ai-architecture/enterprise-ai-architecture-patterns.md) |
[Governance & Compliance](../enterprise-architecture/ai-architecture/enterprise-ai-governance-compliance.md) |
[Security & Identity](../enterprise-architecture/ai-architecture/agentic-ai-security-identity.md) |
[Observability](../enterprise-architecture/ai-architecture/agentic-ai-reliability-observability-governance.md) |
[Memory Architecture](../enterprise-architecture/ai-architecture/agent-memory-planning-architecture.md) |
[Auth Implementation](../ai-protocols/auth/entra-3lo-agent-auth-implementation.md)

---

## Lifecycle Overview

The full agentic application lifecycle comprises 17 stages from initial idea through retirement. Each stage has defined objectives, key activities, owners, and go/no-go gates.

| Stage | Typical Duration | Primary Owner | Key Gate |
| ------- | ----------------- | --------------- | ---------- |
| 1. Ideation | 1–2 weeks | Product Owner | AI Applicability Score ≥ 6/10 |
| 2. Discovery | 2–4 weeks | Architect + UX | Discovery Report signed off |
| 3. Business Case | 2–3 weeks | Product Owner + Finance | IRR/NPV approved by sponsor |
| 4. Architecture | 3–6 weeks | Principal Architect | ARB approval |
| 5. UX Research & Design | 3–6 weeks | UX Lead | Usability test pass rate ≥ 80% |
| 6. Context Engineering | 2–4 weeks | AI Engineer | Eval baseline established |
| 7. Agent Design | 2–4 weeks | AI Architect | Agent spec signed off |
| 8. Evaluation Design | 2–3 weeks | AI Engineer | Eval harness green |
| 9. Security Review | 2–3 weeks | Security Architect | No Critical findings open |
| 10. Development | 8–16 weeks | Engineering Team | All acceptance criteria met |
| 11. Testing | 3–6 weeks | QA + Red Team | All blockers resolved |
| 12. Deployment | 1–3 weeks | Platform / SRE | Canary stable at 10% |
| 13. Operations | Ongoing | SRE + Product | SLOs met for 30 days |
| 14. Continuous Improvement | Ongoing | AI Engineer + Product | Eval regression &lt; 2% |
| 15. Versioning | Ongoing | AI Engineer | No breaking changes unannounced |
| 16. Migration | Variable | Architect + Engineering | Zero data loss; rollback tested |
| 17. Sunsetting | 4–8 weeks | Product + Legal | Compliance archive complete |

---

## Stage 1 — Ideation

Identify a business problem that AI can solve, validate it is worth pursuing, and produce a clear problem statement before significant investment.

### Key Activities

- Business problem articulation → 1-page problem statement
- AI applicability assessment → Applicability score card (total ≥ 8 proceeds to Discovery)
- Agent vs. rule-based vs. ML decision → ADR-00: Technology Category
- Value hypothesis → Value Hypothesis Canvas
- Feasibility scan → Feasibility Assessment  
- Stakeholder alignment → Sponsor sign-off

### AI Applicability Assessment

Score each criterion 0–2: unstructured input, natural language requirement, context sensitivity, reasoning required, data availability, failure tolerance, volume, and existing automation constraints. Minimum score of 8 to proceed.

### Go / No-Go Criteria

- AI Applicability Score ≥ 8 / 16
- Business problem clearly articulated
- Executive sponsor identified
- Preliminary value hypothesis positive
- No show-stopping regulatory barrier identified

### Common Anti-patterns

- Technology-first ideation: AI becomes a solution looking for a problem
- Over-scoping: Platform ambitions when a targeted tool is needed
- Ignoring data readiness: Assuming data accessibility without validation
- Underestimating prompt brittleness: Treating AI as deterministic software

---

## Stage 2 — Discovery

Build deep, evidence-based understanding of the problem space, users, data, tools, and constraints before committing to a solution.

### Key Activities

- Stakeholder interviews (30–60 min structured) → Interview synthesis
- Current-state journey mapping (walkthrough + shadowing) → AS-IS journey map
- Pain point taxonomy (affinity mapping) → Pain point priority matrix
- User archetypes (interview clustering) → 3–5 persona cards
- Data discovery (schema review + sampling) → Data inventory
- Tool landscape assessment (API catalog review) → Tool availability matrix
- Regulatory scan (legal + compliance) → Regulatory risk register

### Pain Point Taxonomy

Classify discovered pain points: volume pain (AI scales), complexity pain (LLM synthesis), consistency pain (uniform application), knowledge pain (democratization), speed pain (async approval), access pain (search assistance).

### Go / No-Go Criteria

- At least 3 users interviewed
- Primary pain points validated with evidence
- Data availability confirmed for primary use case
- No blocking regulatory constraint
- UX feasibility interaction model identified

### Common Anti-patterns

- Survey-only discovery: Doesn't reveal actual user behavior
- Skipping data sampling: Risk of quality surprises at architecture stage
- Single user persona: Enterprise tools serve multiple archetypes
- Ignoring regulatory scan: Blockers are costlier to discover late

---

## Stage 3 — Business Case

Quantify the value, validate the investment, make the build/buy/partner decision, and secure funding approval.

### Value Model Framework

- **Productivity gain:** Hours saved per user × users × hourly rate × 50 weeks
- **Cost reduction:** Current cost − projected cost
- **Error reduction:** Error rate reduction × cost-per-error × volume
- **Revenue uplift:** Conversion improvement × revenue per conversion × volume
- **Risk reduction:** Probability reduction × expected loss
- **Opportunity capture:** New capability × market size × capture percentage

### Build vs. Buy vs. Partner

- **Buy (SaaS):** Speed, vendor domain expertise; risks: lock-in, residency, customization limits
- **Buy (platform, self-host):** Control + managed components; risks: integration effort, maintenance
- **Build (custom):** Differentiating capability, unique data; risks: cost, skills gap, time-to-value
- **Partner (SI/ISV):** Speed + customization; risks: IP ownership, dependency

### Go / No-Go Criteria

- IRR or NPV positive (or strategic rationale documented)
- Funding approved by financial sponsor
- Build/buy/partner decision made
- Platform selected
- Risk assessment reviewed by legal/compliance

### Common Anti-patterns

- Optimistic sensitivity analysis: Model upside only; require pessimistic scenario
- Ignoring run costs: LLM costs can be 5–10× build cost in year 2
- No exit clause: No escape hatch if vendor raises prices 5×
- Counting fully-loaded gains: Users rarely save 100% hours; apply 30–50% realization factor

---

## Stage 4 — Architecture

Produce complete, defensible architecture satisfying functional, non-functional, security, compliance, and operability constraints.

### Architecture Artifacts

- **Context diagram (C4 Level 1):** System with external actors
- **Container diagram (C4 Level 2):** Internal service decomposition
- **Integration map:** External systems and APIs
- **Data flow diagram:** Trust boundary annotations
- **Security architecture:** Auth flows, network zones, encryption
- **Deployment architecture:** Cloud resources, IaC topology
- **ADRs:** Technology decisions with justification

### Reference Architecture Selection

- Knowledge Q&A: RAG pattern
- Workflow automation: Agentic RAG + tool use + HITL gate
- Multi-department collaboration: Multi-agent orchestration
- Enterprise search: Search copilot (NLWeb + AG-UI)
- Code generation: IDE plugin + context injection + eval harness
- Decision support: Structured output + confidence + audit trail

### Non-functional Requirements

- P50 TTFT: &lt; 2 seconds
- P95 TTFT: &lt; 8 seconds
- Availability: 99.5%
- Context window usage: &lt; 80%
- LLM API cost: &lt; defined budget per interaction

### Go / No-Go Criteria (ARB Gate)

- Architecture review board approval
- No unmitigated Critical security risks
- Data residency requirements met
- All ADRs reviewed and accepted
- NFRs documented and testable
- Exit strategy for all vendor dependencies

### Common Anti-patterns

- Single-point-of-failure LLM: No fallback provider
- Synchronous everything: Blocking long-running tasks in HTTP connections
- Missing context window budget: Silent truncation errors at scale
- Shared mutable memory: Agents writing without conflict resolution

---

## Stage 5 — UX Research & Design

Design an agentic interface that supports user goals, builds trust, meets accessibility, and is validated with target users.

### Key Activities

- User research (contextual inquiry + shadowing): 1–2 weeks → Research synthesis
- Journey redesign (design workshop): 3 days → TO-BE journey map
- Prototype design (Figma/wireframes): 1–2 weeks → Interactive prototype
- Agent persona design (writing workshop): 2 days → Persona doc
- Approval flow design (UX walkthrough): 3 days → Approval flow spec
- Usability testing (5–8 moderated sessions): 1 week → Usability report

### Agent Persona Design

Specify: name, role description, tone (professional/friendly/formal/concise), capabilities (5 bullet max), explicit scope limits, uncertainty handling, error handling, language style samples, prohibited behaviors.

### Usability Testing Pass Criteria

- Complete primary use case: &gt; 80% success without assistance
- Locate and act on approval request: &gt; 90% success
- Understand confidence indicator: &gt; 75% correct interpretation
- Access audit log: &gt; 70% without training
- Cancel running task: &gt; 95% success
- Keyboard-only navigation: 100% of critical flows completable

### Go / No-Go Criteria

- Usability test pass rate on primary flow: ≥ 80%
- All P0 accessibility issues resolved
- Agent persona approved by product + legal
- Approval flow validated by compliance

### Common Anti-patterns

- Designing for the average: Serve both expert and novice with progressive disclosure
- Testing with developers: Use actual target users, not developers
- Skipping the refusal state: Design what happens when agent cannot answer
- Ignoring mobile: > 30% of enterprise workers use mobile; all features must work

---

**This is Part 1 of 3. [Continue with Part 2 →](pathname:///archon/agentic-systems/agentic-ui/parts/04-application-lifecycle-part2) for Stages 6–11 (Context Engineering through Testing).**
