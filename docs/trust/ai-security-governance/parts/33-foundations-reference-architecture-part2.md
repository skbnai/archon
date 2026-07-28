---
title: "Foundations & Reference Architecture: Threat Modeling (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: foundations-reference-architecture-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/01-Foundations-Reference-Architecture.md]
tags: [ai-security, threat-modeling, stride, maestro, mitre-atlas]
covers_version: "as of 2026"
---

Layering STRIDE, PASTA, MITRE ATT&CK/ATLAS, and the agent-native CSA MAESTRO framework to produce complete threat models for agentic systems.

## Threat Modeling for Agentic Systems

Threat modeling agentic systems requires layering frameworks rather than picking one. STRIDE and PASTA remain useful for the conventional application and infrastructure surface an agent sits on top of, but neither was designed to reason about a system that forms its own intent at runtime. Three newer frameworks fill that gap, and a mature program uses all three together rather than treating them as competitors.

**STRIDE and PASTA — what still applies, and where they stop.** STRIDE's six categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) map cleanly onto agent identity spoofing, memory tampering, insufficient audit logging, context leakage, resource-exhaustion attacks on agent budgets, and privilege escalation through delegation chains — a sound checklist for the infrastructure an agent runs on. Its blind spot is cognitive: STRIDE has no native category for an agent being talked into doing something harmful through legitimate-looking input, because that is not a spoofing or tampering attack against the system — it is a successful, well-formed instruction that happens to be malicious. PASTA's seven-stage, risk-centric process (defining business objectives and technical scope, decomposing the application, analyzing threats, identifying vulnerabilities, modeling attacks, and quantifying risk) is valuable for tying agent risk back to business impact, but suffers the same blind spot at the decomposition stage unless explicitly extended.

**MITRE ATT&CK and MITRE ATLAS.** ATT&CK remains the right taxonomy for everything that happens once an agent (or the infrastructure underneath it) is compromised and an adversary is operating within the environment — lateral movement, credential access, persistence. ATLAS extends this specifically to the ML/AI attack surface: adversarial inputs, model extraction, training-data poisoning, and, in its more recent additions, agent-specific tactics. A mature threat model cross-references ATLAS techniques against the agent's specific architecture — which techniques are even reachable given this agent's tool access, memory configuration, and autonomy level.

**CSA MAESTRO — the agent-native framework.** MAESTRO (Multi-Agent Environment, Security, Threat, Risk, and Outcome), published by the Cloud Security Alliance, is purpose-built for agentic systems and has become the closest thing to a standard agent threat-modeling methodology. It decomposes an agentic system into seven layers and requires the threat modeler to work through both traditional and agentic threats at each layer, then explicitly analyze cross-layer threats — because the most damaging agent failures rarely stay contained to one layer:

| Layer | What It Covers | Representative Threats |
|---|---|---|
| L1 — Foundation Models | The base/fine-tuned LLMs providing reasoning and tool-use capability | Adversarial inputs, model extraction, training-data and fine-tuning backdoors |
| L2 — Data Operations | Data pipelines, labeling, embeddings, RAG ingestion | Data poisoning, embedding manipulation, pipeline tampering |
| L3 — Agent Frameworks | Orchestration logic, planning, decision-making (LangGraph, AutoGen, etc.) | Goal hijacking, insecure tool integration, prompt injection propagation |
| L4 — Deployment & Infrastructure | Containers, cloud hosting, network configuration | Misconfiguration, container escape, insecure secrets handling |
| L5 — Evaluation & Observability | Testing, monitoring, logging, audit trails | Blind spots in monitoring, evaluation gaming, log tampering |
| L6 — Security & Compliance (vertical) | Cross-cutting controls applied at every layer | Inconsistent policy enforcement across layers, compliance drift |
| L7 — Agent Ecosystem | Multi-agent interaction, marketplaces, A2A/MCP discovery | Agent impersonation, marketplace manipulation, collusion, supply-chain compromise via third-party agents |

MAESTRO's real value is forcing analysis of cross-layer cascades: a poisoned embedding at L2 reaches an agent's planning logic at L3, which selects a tool at L4 with broader permissions than the original task required, and the resulting action is never flagged because the observability layer (L5) was only watching for anomalies in single-agent behavior, not for an L7-level pattern of one compromised agent influencing a peer through A2A messaging. No single-layer review catches this; only an explicit cross-layer pass does.

**Producing the required threat models.** Enterprises should build fully worked threat models — using MAESTRO as the primary structure, cross-referenced against ATLAS and STRIDE — for representative system types, each as a standalone artifact (data flow diagram, trust boundaries, layer-by-layer threat enumeration, prioritized control list) reviewed at least annually or on material architecture change:

1. **Single Agent** — a bounded, single-purpose agent (e.g., a customer support agent with read access to a CRM and a knowledge base). Establishes the baseline pattern and the minimum control set every agent should carry regardless of complexity.
2. **Multi-Agent System** — a planner/orchestrator coordinating two or more specialist sub-agents (e.g., a research agent delegating to a web-search agent and a code-execution agent). Surfaces delegation-abuse, state-poisoning, and goal-hijack-propagation risks absent in the single-agent case.
3. **MCP Ecosystem** — an enterprise with a central MCP gateway fronting dozens of internal and third-party MCP servers. Surfaces tool poisoning, schema manipulation, and tenant-isolation risks.
4. **Banking AI Platform** — a regulated, high-consequence composite: agents with access to payment rails, customer PII, and external A2A counterparties (correspondent-bank agents, payment-network agents). This reference model should incorporate every control surfaced by the prior three models plus regulatory-specific constraints (DORA, PCI DSS, SOC 2).

## How the Frameworks in This Volume Relate

No single framework covers the full problem, and the frameworks are not competitors — they operate at different altitudes and answer different questions:

| Framework | Altitude | Primary Question It Answers |
|---|---|---|
| SABSA / TOGAF / Zachman | Enterprise architecture | How does agent risk and capability map onto our existing business and technology architecture? |
| STRIDE / PASTA | Application security | What conventional security flaws exist in the systems an agent runs on? |
| MITRE ATT&CK / ATLAS | Adversary tactics | What does a real-world attacker do once inside, and what AI-specific techniques apply? |
| CSA MAESTRO | Agent-native threat modeling | What can go wrong, layer by layer and across layers, in this specific agentic system? |
| OWASP ASI Top 10 | Risk taxonomy / prioritization | Which of the highest-prevalence, highest-impact agentic risks are present here? |
| AI Security Mesh | Operating architecture | How do we enforce identity, policy, memory, and observability consistently at scale? |

## Related

- [Foundations & Reference Architecture (Part 1)](../33-foundations-reference-architecture.md)
- [Foundations & Reference Architecture: Lifecycle, Runtime & Mesh (Part 3)](33-foundations-reference-architecture-part3.md) — agent lifecycle security, multi-agent orchestration threats, runtime isolation, and the AI Security Mesh
- [Enterprise Threat Modeling](../07-enterprise-threat-modeling.md)
