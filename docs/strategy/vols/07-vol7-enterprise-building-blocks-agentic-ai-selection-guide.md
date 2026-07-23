---
title: "Enterprise Building Blocks: Agentic AI & Selection Guide"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: vol7-enterprise-building-blocks-part4
maturity: practitioner
personas:
  - enterprise-architect
  - cto
last_reviewed: 2026-07-19
covers_version: ""
supersedes: []
tags:
  - agentic-ai
  - agent-framework
  - selection
sources: []
pagination_prev: strategy/vols/vol7-enterprise-building-blocks-ai-infrastructure-platform-engineering
---

# Enterprise Building Blocks: Agentic AI & Selection Guide

## Agentic AI Building Blocks

### Agent Harness

**Purpose:** Execution environment hosting, monitoring, managing AI agents. Handles tool registration, conversation management, error recovery, telemetry.

| Solution | Language |
|----------|---------|
| **Claude Agent SDK** | Python/TypeScript |
| **LangChain / LangGraph** | Python |
| **AutoGen (Microsoft)** | Python |
| **CrewAI** | Python |

### Tool Registry (MCP Server Catalog)

**Purpose:** Governed catalog of tools available to AI agents. Built on Model Context Protocol (MCP).

Tool registry entries include ID, name, server, description, input schema, authorization requirements, rate limits, owner, SLA, tags.

### Agent Gateway

**Purpose:** Routing layer for multi-agent architectures. Routes requests to appropriate agent based on capability, availability, load.

**Capabilities:**
- Capability-based routing
- Load balancing across agent instances
- Circuit breaking
- Agent discovery
- Cross-agent authorization
- Audit logging

### Context Engine

**Purpose:** Manages information flowing into agent's context window. Assembles system instructions, memory, tool results, conversation history.

**Context Assembly:**
1. System Prompt: Role definition, constraints, persona
2. Memory Retrieval: Relevant past interactions
3. Knowledge Retrieval: Relevant documents (RAG)
4. Tool Results: Results from previous tool calls
5. Conversation History: Recent turns
6. Current Message: User or orchestrator instruction

### Skill Registry

**Purpose:** Library of reusable agent capabilities. Pre-built, tested, governed skills agents can acquire.

**Skill Definition includes:** ID, name, version, description, inputs, outputs, prompt template, tools required, avg latency, avg cost, eval score, tags.

---

## Building Block Selection Decision Matrix

### Decision Criteria

| Criterion | Weight | Assessment |
|-----------|--------|-----------|
| **Strategic fit** | 25% | Aligns with cloud strategy? |
| **Functional coverage** | 25% | Meets capability requirements? |
| **Enterprise readiness** | 20% | Security, compliance, SLA? |
| **Total cost of ownership** | 15% | License, ops, migration, training? |
| **Ecosystem integration** | 10% | Connects to existing tools? |
| **Talent availability** | 5% | Can we hire/train? |

### AI Building Block Selection Guide

| Use Case | Recommended ABB Combination |
|----------|---------------------------|
| **Simple chatbot** | LLM Gateway + Safety Guardrails + Knowledge Base |
| **Enterprise RAG** | LLM Gateway + Knowledge Base + Evaluation + Safety |
| **AI agent** | Agent Runtime + Tool Registry + Memory Store + LLM Gateway |
| **Multi-agent** | Agent Gateway + Agent Runtime × N + Context Engine + Memory |
| **ML serving** | Model Registry + Feature Store + Training Pipeline + Evaluation |

### Build vs. Buy vs. Configure Decision Tree

```
START: New AI capability needed
       ↓
Is this a commodity capability?
(messaging, identity, storage)
     YES → Buy SaaS / use cloud-managed service
     NO  ↓
Is there a mature open source option?
     YES → Evaluate OSS; consider managed distribution
     NO  ↓
Is this a differentiated capability for the enterprise?
     YES → Build (invest in proprietary advantage)
     NO  → Partner (system integrator or specialized vendor)
```

---

## Related

- [Enterprise Building Blocks: Concept & Business Blocks](../50-vol7-enterprise-building-blocks.md)
- [Enterprise Building Blocks: Application & Core AI Blocks](05-vol7-enterprise-building-blocks-application-core-ai-blocks.md)
---

*Volume 7 of 10 — Part 4 of 4*
