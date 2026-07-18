---
title: "Agentic AI Delivery Lifecycle (ADLC)"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-05-agentic-lifecycle
maturity: practitioner
personas: [program-manager, delivery-lead, architect, agent-engineer]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-05-agentic-lifecycle.md
tags: ["adlc", "agent-lifecycle", "agentops", "mcp", "a2a", "multi-agent", "safety-testing"]
sources: []
---

# Agentic AI Delivery Lifecycle (ADLC)

The Agent Delivery Lifecycle (ADLC) extends the GenAI delivery lifecycle to cover the additional complexity of autonomous agents. Agents must be designed, safety-tested, and operationally monitored with rigor exceeding GenAI systems.

## ADLC Phases

1. **Agent Discovery & Goal Definition** — Identify automation opportunities; define agent's primary goal and constraints
2. **Task Modelling** — Decompose goal into task graph with decision points and branching
3. **Reasoning Strategy** — Choose reasoning architecture (ReAct, chain-of-thought, plan-and-execute, delegation)
4. **Memory Design** — Define what agent remembers across steps and sessions
5. **Tool & MCP Configuration** — Define agent's tool set and configure MCP servers
6. **Workflow Design** — Design multi-step workflows, approval gates, delegation patterns
7. **Safety Testing** — Rigorous testing for goal alignment, prompt injection, loops, tool abuse, privilege escalation
8. **Human Approval Design** — Define human-in-the-loop checkpoints
9. **Policy Engine** — Configure authorization and policy constraints
10. **Evaluation & Simulation** — Simulate agent behaviour; evaluate against acceptance criteria
11. **Deployment** — Canary deployment with emergency shutdown capability
12. **Operations** — Monitor task completion, human handoff rate, tool errors
13. **Lifecycle Management** — Versioning, updates, retirement

## ADLC vs Adjacent Lifecycles

| Dimension | SDLC | MLOps | LLMOps | ADLC |
|---|---|---|---|---|
| Primary artifact | Source code | Trained model | Prompt + LLM | Agent (model + prompt + tools + memory + identity) |
| Version unit | Code commit | Model version | Prompt + model | Agent compound version |
| Testing | Unit/integration | Accuracy benchmarks | Evaluation suites | Simulation, adversarial, safety |
| Deployment | Rolling, blue/green | Shadow, canary | Canary, A/B | Canary with emergency shutdown |
| Failure mode | Defects, crashes | Drift, degradation | Hallucination, injection | Runaway actions, goal misalignment |
| Monitoring | Uptime, error rate | Model drift | Quality, cost | Task completion, HITL rate, tool errors |
| Governance artifact | Code review, change ticket | Model card, bias report | Prompt log, eval report | Agent charter, action audit log |

## Key Agent Design Considerations

**Reasoning Strategy:** ReAct (reason-and-act) is most common for single-agent tasks with interleaved reasoning and tool use. Chain-of-thought suits complex multi-step analysis. Plan-and-execute is best for structured workflows.

**Memory Design:** Define working memory (short-term context), episodic memory (task history), semantic memory (learned facts), and procedural memory (learned skills).

**Tool Design:** Apply least privilege—grant only permissions necessary for the stated goal. Every tool call must be logged for audit and safety review.

**Safety Testing Mandatory:** Before production, agents must pass goal alignment tests, prompt injection tests, infinite loop detection, tool abuse tests, and privilege escalation tests.

## Agent Charter Template

Every production agent requires an **Agent Charter** documenting:

- **Agent Name & Purpose** — Clear statement of what the agent does
- **Primary Goal** — The outcome the agent is designed to achieve
- **Sub-Goals** — Tasks required to achieve the primary goal
- **Explicit Non-Goals** — What the agent must never do
- **Tool Set & Permissions** — Authorized actions and resources
- **Memory Constraints** — What it remembers across sessions
- **Human Approval Gates** — Decisions requiring human review
- **Failure Modes** — Known risks and mitigations
- **Owner & Stakeholders** — Accountability and oversight

## ADLC vs GenAI Delivery

| Aspect | GenAI | ADLC |
|---|---|---|
| Human role | Prompter | Overseer (sets goals, reviews exceptions) |
| Risk tolerance | Moderate | Very low (agents take real-world actions) |
| Deployment | Typically single LLM call | Multi-step workflows with feedback loops |
| Reversibility | Easy to stop | May require manual remediation if agent acts |
| Governance | RAI review + guardrails | RAI review + Agent Governance Board + kill switch |
| Testing | Evaluation suites | Simulation + adversarial + safety + human-in-the-loop |
| Monitoring | Quality, cost | Task completion, HITL rate, tool errors, unexpected actions |

## Deep-Dive Resources

- [AI Delivery Lifecycle](13-part-03-ai-delivery-lifecycle.md) — Parent lifecycle ADLC extends
- [GenAI Delivery](14-part-04-genai-delivery.md) — GenAI foundation agents build on
- [Governance Model](16-part-06-governance.md) — Agent governance and approval processes
- [Operating Processes](19-part-09-operating-processes.md) — Agent Approval and Rollback processes

## Related

- [AI Operating Models](12-part-02-operating-models.md)
- [Organizational Roles](18-part-08-organizational-roles.md)
- [AI Platform](17-part-07-platform-operating-model.md)

## Sources

