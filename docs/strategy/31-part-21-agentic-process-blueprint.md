---
title: "Part 21 — Agentic Process Design Methodology & Patterns"
doc_type: guide
domain: strategy
topic_id: part-21-agentic-process-blueprint
status: current
canonical: true
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
maturity: practitioner
personas: ["architect", "process-owner"]
supersedes: ["docs/enterprise-ai-report/part-21-agentic-process-blueprint.md"]
tags: ["agentic-process", "process-blueprint", "agent-infused-teams", "digital-workforce", "process-redesign"]
sources: []
---

# Part 21 — Agentic Process Design Methodology & Patterns

An **Agentic Process Blueprint** is a redesigned process specification that reimagines how a business process executes when AI agents replace, augment, or orchestrate the steps traditionally performed by humans.

It is not simply adding a chatbot to an existing process. It is a fundamental rethinking of who (human, agent, or hybrid) performs each step, when human judgement is essential vs. overhead, what the agent needs to know and access, how exceptions are handled, and what governance is required.

## The Agentic Process Design Methodology

### Step 1 — Map the Current Process (As-Is)

Document the current process with full granularity:
- Every step, decision point, and handoff
- Who performs each step (role, team, system)
- What data, tools, and knowledge are required
- What decisions are made (and on what basis)
- Where the process slows down, errors occur, or rework happens

**Tools:** BPMN swimlane diagram, value stream map, process narrative.

### Step 2 — Classify Each Step

For each process step, classify its automation potential:

| Classification | Description | Agentic Pattern |
|---------------|-------------|-----------------|
| **Fully Automatable** | Deterministic, rule-based, data-driven — no judgment required | Full agent execution |
| **AI-Augmented** | Judgment required, but AI can provide recommendation/draft | Agent proposes, human approves |
| **AI-Assisted** | Human decides but AI provides information/analysis | Agent informs human |
| **Human-Essential** | Requires empathy, legal accountability, novel judgment | Human only (AI may support) |
| **Eliminatable** | Step exists only because prior steps were slow | Remove the step |

### Step 3 — Design the Agentic Process (To-Be)

Redesign the process with agent actors alongside human actors.

**Actor taxonomy:**
- **Orchestrator Agent** — coordinates overall process; delegates to specialist agents
- **Specialist Agents** — perform specific tasks (data extraction, analysis, communication, action)
- **Human Decision Makers** — approvals, exceptions, relationship-sensitive interactions
- **Oversight Roles** — HOTL (Human-on-the-Loop) monitoring agent fleet

**Design principles:**
1. Default to agent; escalate to human — agents handle routine; humans handle exceptions
2. Human oversight by design — every agent has a human escalation path
3. Audit every action — every agent decision and action is logged
4. Confidence thresholds — agents act below threshold; escalate above threshold
5. Agent rights and limits — explicitly scope what each agent can and cannot do

### Step 4 — Define the Human-in-the-Loop Architecture

For each human touchpoint in the redesigned process, define:
- **HITL trigger:** What condition causes escalation to human? (confidence score, value threshold, exception type)
- **HITL interface:** How is the human notified? (dashboard alert, email, Slack, embedded in workflow tool)
- **HITL timeout:** What happens if the human does not respond? (escalate further, default action, pause process)
- **HITL logging:** How is the human decision recorded? (for audit, for future agent training)

### Step 5 — Specify the Agent Fleet

For each agent in the redesigned process, document:

```markdown
## Agent Specification: [Agent Name]

**Goal:** [What outcome this agent achieves]
**Inputs:** [Data, documents, events this agent receives]
**Outputs:** [What the agent produces or does]
**Tools:** [APIs, databases, services the agent can access]
**Memory:** [What the agent remembers across steps/sessions]
**Confidence Model:** [How the agent scores its own decisions]
**HITL Triggers:** [When the agent escalates to human]
**Constraints:** [What the agent must never do]
**Risk Class:** [Observe-only / Low / Medium / High / Critical]
```

### Step 6 — Define Metrics & Measurement

For each redesigned process, define how success is measured:

| Metric Category | Metrics |
|----------------|---------|
| **Efficiency** | Cycle time, throughput, cost per transaction |
| **Quality** | Error rate, rework rate, exception rate |
| **Autonomy** | % steps completed by agent vs. human |
| **Oversight** | HITL escalation rate, human override rate |
| **Business Outcome** | KPI the process is designed to drive |

## Agentic Process Patterns

### Pattern 1 — Sequential Agent Chain

Each agent in a pipeline processes the output of the previous agent. Classic assembly-line pattern for linear processes.

**Flow:** Input Event → Agent 1 (Data Extraction) → Agent 2 (Validation & Enrichment) → Agent 3 (Decision / Classification) → HITL (if triggered) → Agent 4 (Action / Communication) → Outcome + Audit Log

**Best for:** Document processing, loan underwriting, claims processing, order management.

### Pattern 2 — Parallel Agent Fan-Out

An orchestrator agent dispatches multiple specialist agents simultaneously; results are aggregated and synthesised.

**Flow:** Input Event → Orchestrator Agent → [Specialist A, Specialist B, Specialist C in parallel] → Orchestrator synthesises → Output

**Best for:** Investment research, due diligence, M&A analysis, RFP response generation.

### Pattern 3 — Hierarchical Delegation

An orchestrator agent manages a team of sub-agents, each of which may further delegate to specialist agents.

**Structure:** CEO Agent / Strategy Orchestrator → Finance Agent → [FP&A Agent, Reporting Agent] / Operations Agent → [Procurement Agent, Logistics Agent] / Customer Agent → [Service Agent, Retention Agent]

**Best for:** Complex enterprise workflows, digital workforce management, cross-functional process automation.

### Pattern 4 — Event-Driven Reactive Agent

Agent monitors an event stream and reacts autonomously when conditions are met.

**Flow:** Event Stream (Orders, Alerts, Sensor Data, Price Changes) → Monitor Agent (continuously evaluates) → Action Agent (if triggered) → Human Notification (if high-stakes)

**Best for:** Supply chain monitoring, SOC threat response, trading alerts, operations control tower.

### Pattern 5 — Human-Agent Collaborative Workflow

Agents and humans pass work back and forth fluidly, each handling what they are best at.

**Flow:** Human (Relationship conversation) → passes context to Agent → Agent (Research, draft response, analysis) → returns to Human → Human (Reviews, refines, sends) → Outcome logged for agent learning

**Best for:** Sales, account management, legal review, complex customer service.

## Process Blueprint Template

Use this template for any process redesign engagement:

```markdown
# Agentic Process Blueprint: [Process Name]

## 1. Process Overview
- **Business Function:** [Finance / Operations / Customer / HR / etc.]
- **Process Owner:** [Human role]
- **Volume:** [Transactions per day/week/month]
- **Current Cycle Time:** [Average time, end-to-end]
- **Current Cost:** [Cost per transaction]

## 2. Current State (As-Is) Pain Points
| Pain Point | Frequency | Impact |
|-----------|-----------|--------|
| [Step X takes too long] | Daily | High |

## 3. Agent Opportunity Assessment
| Step | Automation Class | Priority |
|------|-----------------|---------|
| [Step 1] | Fully Automatable | High |

## 4. Agentic Process Design (To-Be)
[Swimlane diagram: Human / Orchestrator Agent / Specialist Agents / Systems]

## 5. Agent Fleet Specification
[Agent Charter for each agent in the process]

## 6. HITL Architecture
| Trigger Condition | HITL Type | Timeout | Default |
|------------------|-----------|---------|---------|
| [Confidence < 0.7] | Review | 4 hours | Escalate |

## 7. Target Metrics
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|

## 8. Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|

## 9. Implementation Roadmap
| Phase | Duration | Scope |
|-------|---------|-------|
| Phase 1 | Month 1–2 | Shadow mode |
| Phase 2 | Month 2–4 | HITL mode |
| Phase 3 | Month 4–6 | Autonomy for routine |
```

## Related

- [Part 21 — Agentic Blueprints by Function & Agent-Infused Teams](73-part-21-agentic-process-blueprint-blueprints-by-function-teams.md) — Industry-specific process blueprints and team design patterns
- [Part 2 — Operating Models](12-part-02-operating-models.md) — Digital Workforce and Agent Factory operating models
- [Part 5 — Agentic AI Delivery Lifecycle](15-part-05-agentic-lifecycle.md) — How to build the agents in this blueprint
- [Part 9 — AI Operating Processes](19-part-09-operating-processes.md) — Agent approval, rollback, and monitoring processes

## Sources

[No external sources for this page.]
