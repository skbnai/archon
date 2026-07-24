---
title: Decision Matrix - Choosing Your Orchestration Platform
domain: agentic-systems
doc_type: guide
topic_id: decision-matrix
status: current
supersedes:
  - ../knowledge-docs/docs/workflow-orchestration/20-decision-matrix.md
date_created: 2026-07-24
last_reviewed: 2026-07-24
source_type: native-md
covers_version: as of 2026-07-10
tags:
  - workflow-orchestration
---

# Decision Matrix: Platform Selection Guide

This matrix helps you choose the right orchestration platform(s) for your enterprise.

---

## Quick Reference: Platform Characteristics

### Temporal

```
Best for: Distributed transactions, SLA-critical workflows, microservices
Cost: Self-hosted or cloud SaaS
Learning curve: Moderate (code-first)
Determinism: Guaranteed
Scalability: Excellent (100M+ workflows)
Human approval: Supported (signals)
AI integration: Via activities (agents as black boxes)
```

### Camunda

```
Best for: Business process governance, visual modeling, compliance
Cost: Community (free) or enterprise license
Learning curve: Easy for business users, moderate for developers
Determinism: Supported
Scalability: Good (100k+ instances)
Human approval: Native (human task elements)
AI integration: Via external services or DMN replacement
```

### LangGraph

```
Best for: Agentic workflows, reasoning, dynamic tool invocation
Cost: Framework (free) + LLM API costs
Learning curve: Easy for Python developers
Determinism: Not required
Scalability: Depends on LLM latency
Human approval: Via tool, not native
AI integration: Native (agents all the way down)
```

### CrewAI

```
Best for: Multi-agent coordination, role-based teams
Cost: Framework (free) + LLM API costs
Learning curve: Moderate
Determinism: Not required
Scalability: Good for multi-agent (message passing)
Human approval: Via tools
AI integration: Native (agents + roles)
```

### Claude Code

```
Best for: Development tasks, meta-orchestration, complex reasoning
Cost: Per-session (Anthropic Claude API)
Learning curve: Easy (conversational)
Determinism: Not enforced
Scalability: Per-session (not continuous)
Human approval: In-flight guidance
AI integration: Native (extended thinking, tools)
```

### AWS Step Functions

```
Best for: AWS-centric workflows, Lambda coordination
Cost: Pay-per-execution
Learning curve: Easy for AWS developers
Determinism: Guaranteed
Scalability: Good (AWS-scale)
Human approval: Supported
AI integration: Via BedrockAgent or Lambda
```

### Azure Durable Functions

```
Best for: Azure-centric workflows, .NET-first shops
Cost: Azure compute pricing
Learning curve: Easy for .NET developers
Determinism: Guaranteed
Scalability: Good (Azure-scale)
Human approval: Supported
AI integration: Via Azure OpenAI or external
```

---

## Decision Matrix

### Row 1: Core Use Case

**Are you coordinating...?**

| Use Case | Temporal | Camunda | LangGraph | CrewAI | Claude Code | Step Func |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Microservice transactions | ✅✅✅ | ❌ | ❌ | ❌ | ❌ | ✅✅ |
| Business processes (compliance) | ✅ | ✅✅✅ | ❌ | ❌ | ❌ | ✅ |
| Agentic reasoning | ❌ | ❌ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ❌ |
| Multi-agent coordination | ❌ | ❌ | ✅✅ | ✅✅✅ | ✅✅ | ❌ |
| Development tasks | ❌ | ❌ | ❌ | ❌ | ✅✅✅ | ❌ |
| Financial settlement | ✅✅✅ | ❌ | ❌ | ❌ | ❌ | ✅✅ |
| Order fulfillment | ✅✅✅ | ✅✅ | ❌ | ❌ | ❌ | ✅✅ |
| Data pipeline | ✅✅ | ❌ | ✅✅ | ✅ | ✅ | ✅✅ |

---

### Row 2: Organizational Fit

**Your team and constraints...**

| Factor | Temporal | Camunda | LangGraph | CrewAI | Claude Code | Step Func |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Business users need visibility | ❌ | ✅✅✅ | ❌ | ❌ | ❌ | ❌ |
| Developers prefer code | ✅✅✅ | ❌ | ✅✅✅ | ✅✅ | ✅✅✅ | ✅✅ |
| Compliance/audit is critical | ✅✅✅ | ✅✅✅ | ❌ | ❌ | ⚠️ | ✅✅ |
| Non-technical process design | ❌ | ✅✅✅ | ❌ | ❌ | ❌ | ❌ |
| Python-first shop | ⚠️ | ⚠️ | ✅✅✅ | ✅✅✅ | ✅✅ | ❌ |
| Java/Go-first shop | ✅✅✅ | ✅✅ | ❌ | ⚠️ | ❌ | ❌ |
| .NET-first shop | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | ✅✅✅ |
| AWS-centric | ⚠️ | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅✅✅ |
| Azure-centric | ⚠️ | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅✅✅ |

---

### Row 3: Technical Requirements

**Critical capabilities...**

| Requirement | Temporal | Camunda | LangGraph | CrewAI | Claude Code | Step Func |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Guaranteed determinism | ✅✅✅ | ✅✅ | ❌ | ❌ | ❌ | ✅✅✅ |
| Adaptive decision-making | ❌ | ⚠️ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ❌ |
| Long-running workflows (days) | ✅✅✅ | ✅✅✅ | ❌ | ❌ | ❌ | ✅✅ |
| Parallel execution | ✅✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ |
| Dynamic tool invocation | ❌ | ❌ | ✅✅✅ | ✅✅✅ | ✅✅✅ | ❌ |
| Sub-second latency | ✅✅✅ | ⚠️ | ❌ | ❌ | ❌ | ✅✅ |
| Learning/memory | ❌ | ❌ | ✅✅ | ✅✅✅ | ✅✅✅ | ❌ |
| Human-in-the-loop | ✅✅ | ✅✅✅ | ⚠️ | ⚠️ | ✅✅ | ✅ |
| Automatic retry | ✅✅✅ | ✅✅ | ⚠️ | ⚠️ | ✅ | ✅✅✅ |
| Rollback capability | ✅✅✅ | ✅✅ | ❌ | ❌ | ⚠️ | ✅✅ |

---

### Row 4: Cost & Operations

**TCO and DevOps...**

| Factor | Temporal | Camunda | LangGraph | CrewAI | Claude Code | Step Func |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| Initial licensing cost | $ | $$$ | Free | Free | $/API | Free tier |
| Self-hosted option | ✅ | ✅ | ✅ | ✅ | N/A | ❌ |
| SaaS option | ✅ | ✅ | N/A | N/A | ✅ | ✅ |
| Operational complexity | ⚠️ | ⚠️ | Low | Low | Very low | Low |
| DevOps overhead | Moderate | Moderate | Low | Low | Minimal | Minimal |
| Vendor lock-in | Moderate | High | Low | Low | Medium | High |
| Cost at scale | Low $/workflow | High | LLM API | LLM API | Per-session | $/execution |

---

## Scenarios: Recommended Combinations

### Scenario A: Financial Services (Compliance-Heavy)

**Organization**: Bank, insurance, payment processor  
**Constraints**: Audit, determinism, regulatory

```
Primary: Temporal
  → For: Payment settlement, SLA-critical flows

Secondary: Camunda
  → For: Approval workflows, compliance dashboards

Tertiary: LangGraph (optional)
  → For: Risk scoring, fraud detection

Reasoning: Start with Temporal (reliability).
Use Camunda for processes that need audit + visual.
Add AI agents only for specific decisions.
```

---

### Scenario B: Retail E-commerce (Agility-Focused)

**Organization**: E-commerce platform, SaaS  
**Constraints**: Rapid iteration, personalization, cost

```
Primary: LangGraph
  → For: Order routing, personalization, recommendations

Secondary: Temporal (for critical path only)
  → For: Payment settlement, inventory sync

Tertiary: Claude Code
  → For: Cross-cutting concerns (logging, monitoring)

Reasoning: Start with LangGraph for flexible workflows.
Use Temporal only where reliability is non-negotiable.
Use Claude Code for coordination logic.
```

---

### Scenario C: Insurance Claims (Human-Heavy)

**Organization**: Insurance company  
**Constraints**: Human approval, visual processes, business rules

```
Primary: Camunda
  → For: Claims workflows, human tasks, business rules

Secondary: LangGraph
  → For: Claims assessment, fraud detection

Tertiary: Temporal (optional)
  → For: Back-end coordination if needed

Reasoning: Camunda shines with human tasks.
LangGraph adds AI assessment.
Temporal only if back-end resilience matters.
```

---

### Scenario D: Data Platform (ML-Centric)

**Organization**: Data engineering, ML ops  
**Constraints**: Reproducibility, optimization, experimentation

```
Primary: LangGraph (via Airflow integration)
  → For: Adaptive data pipelines

Secondary: Temporal
  → For: Long-running ETL with retries

Tertiary: Claude Code
  → For: Data exploration, schema optimization

Reasoning: LangGraph + Airflow for ML pipelines.
Temporal for batch jobs needing reliability.
Claude Code for ad-hoc data work.
```

---

### Scenario E: SaaS Platform (Everything)

**Organization**: Large SaaS platform  
**Constraints**: Multiple use cases, scale, governance

```
Tier 1: Temporal
  → For: Core infrastructure (payments, subscriptions)

Tier 2: Camunda
  → For: Customer-visible workflows (onboarding, billing)

Tier 3: LangGraph
  → For: AI features (recommendations, support)

Tier 4: Claude Code
  → For: Internal automation, deployments

Reasoning: Specialized tier for each concern.
Claude Code is meta-orchestrator for internal work.
```

---

## Selection Tree

```
START: "What are we building?"

  Q1: Is it a microservice orchestration problem?
      YES → Choose Temporal
      NO → Continue

  Q2: Do non-technical users need to see/modify the process?
      YES → Choose Camunda
      NO → Continue

  Q3: Does the process require reasoning and adaptation?
      YES → Choose LangGraph / CrewAI
      NO → Continue

  Q4: Is it coordinating multiple specialized agents?
      YES → Choose CrewAI / Claude Code
      NO → Continue

  Q5: Is it a development/deployment task?
      YES → Choose Claude Code
      NO → Continue

  Q6: Are you cloud-native (AWS/Azure/GCP)?
      YES → Choose Step Functions / Durable Functions
      NO → Choose Temporal (self-hosted)
```

---

## Red Flags: When NOT to Use

### ❌ Don't use Temporal for

- Processes requiring frequent reasoning
- Workflows that frequently change
- Situations where non-determinism is OK

### ❌ Don't use Camunda for

- Back-end microservice coordination
- Real-time, low-latency workflows
- Processes driven by AI reasoning

### ❌ Don't use LangGraph for

- Compliance-critical workflows (audit trail gaps)
- Sub-100ms latency requirements
- Workflows requiring guaranteed determinism

### ❌ Don't use Claude Code for

- Continuous, always-on processes
- Multi-month long-running work
- Compliance-heavy operations

---

## Migration Path (If Starting Fresh)

### Year 1: Foundation

```
Deploy Temporal for critical paths (payments, SLAs)
Add Camunda for business processes (governance)
```

### Year 2: Expansion

```
Introduce LangGraph for new features (recommendations, personalization)
Integrate Temporal + LangGraph (Temporal coordinates, agents decide)
```

### Year 3: Maturity

```
Add Claude Code for cross-platform orchestration
Establish governance layer (versioning, audit)
Potentially add CrewAI for multi-agent systems
```

---

## Cost Comparison at Scale

Assume: 100,000 workflow executions/month, 10M events/month

| Platform | Infrastructure | Licensing | LLM API | Total/Month |
| --- | --- | --- | --- | --- |
| **Temporal** | $5,000 (self-hosted) | $0 | $0 | $5,000 |
| **Camunda** | $2,000 (self-hosted) | $10,000 (license) | $0 | $12,000 |
| **LangGraph** | $1,000 (serverless) | $0 | $5,000 (Claude API) | $6,000 |
| **Hybrid** | $6,000 | $5,000 | $3,000 | $14,000 |

---

## The Practical Answer

**For most enterprises in 2026:**

**Recommended Platform Stack:**
- **Temporal**: Coordination + reliability (payments, SLAs)
- **LangGraph**: Reasoning + adaptation (complex decisions)
- **Camunda**: Governance + compliance (approvals, audit)
- **Coordinator**: Claude Code or internal dispatcher (meta-orchestration)

**Why?**

- Temporal handles "boring but critical" work
- LangGraph handles "complex decision" work
- Camunda handles "compliance and visibility" work
- They complement, don't compete

---

## Learning Opportunity: Your Turn

**Question for your enterprise context:**

Given your specific constraints (industry, scale, team, compliance), how would YOU prioritize these platforms? What's your biggest orchestration challenge that doesn't fit neatly?

Document it here so we can build [reference architectures](./19-reference-architectures.md) from real scenarios.

---

## Agent Selection Framework: When to Use What

This framework answers the primary enterprise question: **for a given task, should you use a prompt, a tool, a workflow, or an agent?** The answer determines the architecture, the governance overhead, and the operational complexity.

### Level 1: Does the Task Need Intelligence at All?

```
Is the task deterministic with known rules?
    YES → Use a rule engine, formula, or deterministic function
          (No AI needed; deterministic beats probabilistic for deterministic problems)
    NO  → Continue to Level 2
```

### Level 2: Does the Task Need Language Understanding?

```
Does the task require natural language understanding OR generation?
    NO  → Use a traditional service / API / microservice
    YES → Continue to Level 3
```

### Level 3: Single Inference or Multi-Step?

```
Can the task be completed in a single LLM inference (one prompt → one response)?
    YES → Use a Prompt (direct LLM call; no agent overhead)
          Examples: classification, extraction, translation, summarisation of a single document
    NO  → Continue to Level 4
```

### Level 4: Is the Multi-Step Sequence Fixed?

```
Is the sequence of steps known at design time (no branching, no tool selection)?
    YES → Use a Workflow / Pipeline
          (LangChain chain, Step Functions, Temporal workflow with fixed activities)
          Examples: document processing pipeline, fixed extraction → classify → format
    NO  → Continue to Level 5
```

### Level 5: Does the Task Need Tools?

```
Does the task need to call external APIs, read databases, or execute code?
    YES → Use an Agent (agent loop with tool use)
    NO  → If multi-step LLM-only: use a Chain / Pipeline with LLM at each step
```

### Level 6: Local or Remote Tool?

```
Is the tool on the same platform/organization?
    YES → Use an MCP Tool (MCP protocol; same trust boundary)
    NO  → Use A2A (cross-organization; independent identity)
```

### Level 7: Single Agent or Multi-Agent?

```
Can a single agent with tools complete the task within context limits?
    YES → Single Agent with Tools (simplest; lowest governance overhead)
    NO  → Multi-Agent System (see Multi-Agent Topology Patterns)
          Does the task have well-defined subtasks for specialists?
              YES → Supervisor-Worker or Planner-Executor
          Does the task need parallel execution?
              YES → Parallel Fan-Out
          Does the task need routing to specialist agents?
              YES → Router pattern
```

### Level 8: Durable Execution Required?

```
Is the task long-running (> 5 minutes) OR must it survive process restarts?
    YES → Wrap in a Durable Workflow Engine (Temporal / AWS Step Functions / LangGraph + checkpointer)
          Even if it's an agent internally, the envelope must be durable
    NO  → Standard agent invocation is sufficient
```

### Level 9: Does the Task Need External Orchestration?

```
Does the task span business process domains with human task steps AND SLA governance?
    YES → BPM Platform (Camunda / Flowable) with AI agents as service tasks
          (BPM provides the human task UI, SLA escalation, and compliance audit)
    NO  → Pure agent orchestration is sufficient
```

### Measurable Decision Criteria

| Criterion | Prompt | Tool | Chain/Pipeline | Single Agent | Multi-Agent | Durable Workflow | BPM |
|----------|--------|------|----------------|-------------|-------------|-----------------|-----|
| **Latency budget** | &lt;5s | &lt;10s | &lt;60s | &lt;5 min | &lt;30 min | Hours–days | Days–weeks |
| **Steps** | 1 | 1 | 2–10 (fixed) | 1–20 (dynamic) | Any | Any | Any |
| **External calls** | None | 1 type | Fixed set | Dynamic | Multiple agents | Any | Any |
| **Human approval** | Not needed | Not needed | Not needed | Optional | Optional | Optional | Native |
| **Failure recovery** | Caller retries | Caller retries | Partial restart | Agent retries | Per-agent retries | Durable resume | Native |
| **Governance overhead** | Minimal | Low | Low | Medium | High | High | Highest |
| **Cost** | Lowest | Low | Low | Medium | High | High | Highest |
| **Auditability** | Limited | Moderate | Good | Good | Complex | Excellent | Excellent |

### Quick Reference: Common Enterprise Scenarios

| Scenario | Recommended Approach |
|---------|---------------------|
| Extract entities from a document | Prompt (single inference) |
| Classify customer support ticket + route | Router Agent |
| Process invoice: extract → validate → post to ERP | Tool Chain (MCP tools) or Pipeline |
| Research a topic across 10 sources | Planner-Executor + Parallel Fan-Out |
| Generate a contract with legal review approval | Single Agent + HITL gate + Durable Workflow |
| Reconcile accounts across 5 systems | Multi-Agent (one agent per system) + Supervisor |
| Handle a customer refund with policy check | Single Agent + MCP tools + HITL for exceptions |
| Generate a board presentation from multiple data sources | Planner-Executor → Parallel Fan-Out → Synthesiser |
| Monitor network and auto-remediate low-risk issues | Event-driven Agent Loop + Kill switch + Human escalation |
| Process 100,000 documents per day | Manager-Worker Pool + Durable Workflow |
| Loan underwriting decision | BPM (Camunda) + AI Agent as decision service + HITL |
| On-call incident response triage | Router → Specialist Agents + Supervisor + Human escalation |

---

**Related:** [Multi-Agent Topology Patterns](../enterprise-architecture/ai-architecture/multi-agent-topology-patterns) | [Agent-as-Tool Composition](../enterprise-architecture/ai-architecture/agent-as-tool-composition) | [Reference Architectures](./19-reference-architectures.md)

**Next**: Study [Reference Architectures](./19-reference-architectures.md) for your scenario, or explore [Future Predictions](./21-future-predictions.md).
