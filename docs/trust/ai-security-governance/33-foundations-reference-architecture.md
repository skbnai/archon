---
title: "Foundations & Reference Architecture: Enterprise Frameworks for Agentic AI"
doc_type: guide
domain: trust
status: current
topic_id: foundations-reference-architecture
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/01-Foundations-Reference-Architecture.md]
tags: [ai-security, enterprise-architecture, sabsa, togaf, zachman, agentic-ai]
covers_version: "as of 2026"
---

Adapting SABSA, TOGAF, and Zachman enterprise security architecture frameworks to agentic AI, plus the security engineering principles that apply to a new class of autonomous execution principal.

## The Architectural Premise

An AI agent is not a feature of an application. It is a new class of execution principal — with its own identity, its own blast radius, its own lifecycle, and its own failure modes — that must be designed, governed, and operated with the same rigor as a privileged service account, and arguably more, because it can reason about how to circumvent the controls placed around it.

The agentic AI ecosystem in 2026 resembles distributed computing circa 2010 and API security circa 2015: powerful, proliferating faster than governance can track it, built on protocols still hardening in production, and increasingly the subject of real, disclosed incidents rather than theoretical risk. The OWASP Top 10 for Agentic Applications (published December 2025) documents real-world incidents — prompt-injection-driven data exfiltration in enterprise copilots, tool misuse in cloud coding assistants, remote code execution in autonomous frameworks, memory poisoning in production assistants — that mirror the early years of web application security almost exactly.

This guide covers four areas that together form an architectural spine: established enterprise security architecture frameworks adapted for agents, the security model for the agent lifecycle itself, the runtime and isolation layer agents execute within, and the security mesh pattern that ties identity, policy, memory, and observability together at scale.

## Security Architecture Frameworks for Agentic AI

Enterprise security architecture did not get rebuilt from scratch for cloud, and it should not be rebuilt from scratch for agents. The discipline's existing frameworks — SABSA, TOGAF, and Zachman — remain the right starting vocabulary. What changes is the population of things being modeled: a SABSA business attribute now has to account for autonomous decision-making; a TOGAF ADM cycle now has to govern a fleet of agents that can be spun up by developers outside formal change control; a Zachman cell for "Who" now has to represent non-human principals that vastly outnumber human ones.

**SABSA for agentic systems.** SABSA's core discipline — deriving security architecture from business attributes rather than technology controls — translates directly to agents, but the attribute set needs extension. Traditional attributes (confidentiality, integrity, availability, accountability) remain necessary but not sufficient. Agentic systems require additional first-class attributes: agency boundedness (the degree to which an agent's autonomy is constrained to a defined, auditable action space — sometimes called "Least Agency," where autonomy is a feature an agent earns through demonstrated reliability, not a default it starts with); reversibility (whether an agent's actions can be undone, compensated, or contained before they propagate downstream — a database write, a wire transfer, and a public API call each carry very different reversibility profiles); explainability under audit (whether the chain of reasoning, tool calls, and memory reads that produced an action can be reconstructed after the fact for a regulator, auditor, or incident responder); and trust derivability (whether the agent's current trust level can be computed from verifiable signals — identity attestation, behavioral history, content provenance — rather than asserted once at deployment and never revisited).

The practical deliverable is an Agent Trust Level Derivation model: a scoring function combining workload identity assurance, the sensitivity of the data and tools the agent can reach, its autonomy level, and its historical behavioral conformance, mapped onto the organization's existing SABSA risk-attribute taxonomy so agent risk can be reported in the same business language as every other risk in the enterprise risk register.

**TOGAF security architecture and the agent fabric.** TOGAF's Architecture Development Method needs two structural adaptations. First, Phase B (Business Architecture) and Phase D (Technology Architecture) need an explicit "Agent Fabric" viewpoint — a horizontal layer cutting across business capabilities the way a service mesh or integration layer does today, because agents are rarely scoped to a single business capability; they are increasingly shared infrastructure that many business processes draw on. Second, and more consequentially, Phase G (Implementation Governance) needs a fast-path review track for agents: the standard TOGAF review cadence — periodic, document-heavy, aligned to project milestones — cannot keep pace with an organization where a developer can stand up a new agent, register a new MCP tool, or grant a new scope in minutes. The mature pattern is a lightweight, automatable "Agent Architecture Compliance" gate: a machine-checkable policy (Cedar or OPA) that runs at registration time and blocks non-compliant agents from being provisioned, backed by periodic human-led architecture review for anything above a defined risk threshold.

**Zachman Framework mapping.** The Zachman Framework's six interrogatives map cleanly onto the agentic stack and are useful precisely because they force completeness — it is easy to design an agent platform that answers "How" (orchestration logic) in exhaustive detail while leaving "Why" (the business justification for the agent's existence and scope) almost entirely implicit.

| Interrogative | Traditional Enterprise Mapping | Agentic AI Mapping |
|---|---|---|
| What | Data entities, data models | Agent memory (episodic, semantic, procedural), context windows, embeddings, RAG corpora |
| How | Business processes, application logic | Agent reasoning loops, planning, tool invocation chains, orchestration graphs |
| Where | Network nodes, locations, data centers | Runtime sandboxes, MCP servers, A2A endpoints, cloud regions, edge inference |
| Who | Organizational units, roles, human identity | Human identities, non-human/workload identities, compound user+agent identity, agent-to-agent trust relationships |
| When | Business events, processing cycles | Agent lifecycle states (provisioned, active, suspended, retired); session and task lifecycles |
| Why | Business goals, strategy, motivation | Agent purpose statement, authorized objective, governance approval, autonomy-level justification |

The deliverable from this exercise is an Agent Security Architecture Repository — a single structured, ideally machine-readable inventory where every registered agent has a populated cell for each interrogative. In practice this becomes the backbone of the agent registry: an agent with an undefined "Why" or an unbounded "Where" is, definitionally, ungoverned.

**How the hyperscalers are positioning this.** Microsoft's Azure AI Foundry and Entra Agent ID materials describe agent governance largely through an identity-first lens, extending Entra ID's existing RBAC/PIM model to agents. Google's Agentspace and Vertex AI Agent Builder lean on Google Cloud's existing IAM and BeyondCorp zero-trust patterns. AWS's Bedrock Agents and the emerging AgentCore runtime lean on IAM roles and Verified Permissions (Cedar-based). None of the three hyperscalers has published a SABSA- or TOGAF-native reference architecture; each is extending its own cloud-native identity and policy stack outward to cover agents — a meaningful gap an enterprise architecture function can fill by translating each hyperscaler's agent-security primitives into the enterprise's existing SABSA/TOGAF vocabulary, rather than adopting three incompatible mental models for a multi-cloud agent estate.

## Security Engineering Principles Applied to Agents

The classical security engineering principles do not need replacing; they need a precise mapping onto agent-specific mechanisms, because "defense in depth for agents" is meaningless until it specifies which layers:

| Principle | Application to Agents / MCP / A2A / Memory / Runtime |
|---|---|
| Secure by Design | Agent capability manifests, tool scopes, and autonomy levels are defined and reviewed before an agent is built, not retrofitted after a pilot succeeds and gets promoted to production |
| Security by Default | New agents are provisioned with zero standing tool access; capabilities are explicitly granted, never inherited from a broad template or a permissive default service account |
| Defense in Depth | Independent controls at the identity layer (workload identity, OAuth scopes), the MCP/A2A protocol layer (schema validation, signed agent cards), the runtime layer (sandboxing, egress control), and the memory layer (provenance tagging, poisoning detection) — no single control is load-bearing |
| Zero Trust | Every tool call, every inter-agent message, and every memory read is authenticated and authorized at the point of use; an agent's network location or prior successful actions confer no implicit trust for the next action |
| Assume Breach | Architecture assumes at least one agent, MCP server, or A2A peer is compromised or behaving maliciously at any given time, and is designed to contain blast radius (capability scoping, egress allowlisting, circuit breakers) rather than to prevent compromise outright |
| Resilience Engineering | Agent reliability engineering practices — SLOs, error budgets, graceful degradation, circuit breakers on tool chains — treat agent misbehavior as an expected operating condition to be engineered around, not an exception |
| Safety by Design | Irreversible or high-consequence actions (financial transactions, infrastructure changes, external communications) require human-in-the-loop approval gates regardless of the agent's measured trust score |
| Privacy by Design | Memory and context layers classify and minimize personal data at write time; retention and right-to-erasure are lifecycle properties of agent memory, not an afterthought bolted onto a data warehouse |

## Related

- [Foundations & Reference Architecture: Threat Modeling (Part 2)](parts/33-foundations-reference-architecture-part2.md) — layered threat modeling with STRIDE, PASTA, MITRE ATT&CK/ATLAS, and CSA MAESTRO
- [Identity/MCP/A2A Security Blueprint](34-identity-mcp-a2a-security-blueprint.md)
- [AI Control Architecture](08-ai-control-architecture.md)
