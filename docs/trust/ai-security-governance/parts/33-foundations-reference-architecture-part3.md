---
title: "Foundations & Reference Architecture: Lifecycle, Runtime & Mesh (Part 3)"
doc_type: guide
domain: trust
status: current
topic_id: foundations-reference-architecture-part3
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/01-Foundations-Reference-Architecture.md]
tags: [ai-security, agent-lifecycle, runtime-isolation, ai-security-mesh]
covers_version: "as of 2026"
---

Agent lifecycle security controls, multi-agent orchestration framework threat surfaces, runtime isolation technology selection, the secure agent operating system pattern, and the AI Security Mesh architecture.

## Agent Lifecycle Security

Every agentic interaction, regardless of framework, decomposes into the same five-stage lifecycle: a user or trigger initiates a request, a planner interprets intent and forms a plan, an agent (or agents) executes steps of that plan, tools are invoked to take action or retrieve information, memory is read and written throughout, and actions land in the world. Each stage has a distinct threat profile, a distinct control set, and a distinct audit requirement:

| Stage | Primary Threats | Primary Controls | Audit Requirement |
|---|---|---|---|
| User → Planner | Prompt injection (direct and indirect via RAG/email/documents), intent manipulation | Input sanitization, content provenance tagging, instruction-vs-data separation | Full input capture with provenance metadata |
| Planner → Agent | Goal hijacking, plan tampering, excessive-scope plan generation | Plan validation against policy before execution, bounded planning depth, human approval for high-risk plans | Plan diff logging (intended vs. executed) |
| Agent → Tool | Tool misuse, parameter injection, excessive permissions, toxic tool combinations | Capability-scoped tokens, schema validation at invocation, tool allowlisting, approval workflows for sensitive calls | Every tool call logged with parameters, caller identity, and policy decision |
| Tool → Memory | Memory/context poisoning, cross-tenant memory leakage, unauthorized persistence | Write-time classification, provenance tagging, tenant isolation, retention policy enforcement | Memory mutation log with source attribution |
| Memory/Tool → Action | Irreversible or high-consequence actions taken without sufficient review | Reversibility classification, human-in-the-loop gates for irreversible actions, rate limiting, circuit breakers | Immutable action log, tamper-evident, tied to originating session |

**Multi-agent orchestration frameworks and their threat surface.** The production orchestration landscape has consolidated around a handful of frameworks, each with a distinct trust model that materially changes the threat surface. LangGraph's graph-based orchestration with explicit state carries state poisoning as its principal risk, since shared graph state is often trusted implicitly by downstream nodes. CrewAI's role-based crews with delegation between agents make delegation abuse the dominant risk, where a low-privilege agent convinces a higher-privilege peer to act on its behalf. The Microsoft Agent Framework (the successor combining Semantic Kernel and AutoGen patterns), with native Entra Agent ID integration, gains identity-aware delegation as its main architectural advantage — but that also means identity misconfiguration has an outsized blast radius. AutoGen's conversational multi-agent patterns carry the highest infinite-loop and goal-drift risk, since agent-to-agent conversations can continue without a hard termination condition unless explicitly bounded. Semantic Kernel's plugin-centric orchestration makes tool/plugin supply-chain risk dominant, since its extensibility model is built around third-party plugin ecosystems.

The five threats common across all five frameworks — agent collusion, goal hijacking, delegation abuse, state poisoning, and infinite loops — are precisely what OWASP's ASI07 (Insecure Inter-Agent Communication), ASI08 (Cascading Failures), and ASI10 (Rogue Agents) are designed to catch. The architectural control that matters here is structural: bound every multi-agent conversation with a maximum turn count, a maximum cost budget, and a maximum wall-clock duration, enforced outside the orchestration framework itself, so a compromised or malfunctioning orchestrator cannot disable its own circuit breaker.

## Agent Runtime Security

If identity answers "who is acting" and policy answers "what are they allowed to do," the runtime layer answers the question that actually contains the blast radius when the first two fail: what can this process physically reach? Runtime isolation is the last line of defense, and for agents that execute generated code or shell commands, it is not optional.

**Runtime isolation technology comparison:**

| Technology | Isolation Model | Best Fit for Agent Workloads | Tradeoff |
|---|---|---|---|
| Firecracker microVMs | Hardware-virtualized, minimal device model, AWS-originated | High-trust-boundary agent code execution (e.g., user-submitted code agents); the de facto standard referenced by current MCP gateway guidance for "one ephemeral sandbox per task" | Higher cold-start latency than containers; requires KVM |
| Kata Containers | OCI-compatible container interface backed by lightweight VMs | Drop-in replacement for container-based agent runtimes needing VM-grade isolation without rearchitecting orchestration | Operational complexity of managing a hypervisor layer in a Kubernetes estate |
| gVisor | User-space kernel intercepting syscalls | General-purpose agent sandboxing where full VM isolation is unnecessary but syscall-level containment is required | Syscall interception overhead; some syscall compatibility gaps |
| WASM / WASI | Capability-based, sandboxed bytecode execution | Tool execution and untrusted plugin code where startup latency must be near-zero; increasingly used for MCP tool sandboxing | Language/runtime ecosystem still maturing for general-purpose agent code |
| Hardened standard containers (seccomp + AppArmor) | Namespace and cgroup isolation with restricted syscall/capability surface | Lowest-overhead option for lower-trust-boundary agents; acceptable when paired with strict network egress controls | Weakest isolation guarantee of the options listed; shared kernel risk |

The recommended pattern is tiered: classify agents by the trust boundary they cross — does this agent execute model-generated code? does it process untrusted external content? does it have network egress to sensitive internal systems? — and assign isolation strength accordingly, rather than applying one isolation technology uniformly. A read-only reporting agent with no code execution does not need Firecracker-grade isolation; a coding agent executing arbitrary generated Python against production-adjacent infrastructure does.

**Runtime controls.** Capability-based security gives agents unforgeable capability tokens scoped to specific resources and operations rather than ambient authority — possessing the capability is both necessary and sufficient, which makes scope review tractable in a way role-based ambient permissions are not. Dynamic permissions are granted just-in-time for the duration of a specific task and revoked on completion, rather than provisioned as standing access, directly addressing the overpermissioning pattern current non-human-identity research identifies as the most operationally urgent gap in enterprise agent deployments. Runtime authorization re-evaluates every tool call and action against policy at the moment of execution, not only at session start, so a token issued for a benign initial task cannot be silently reused for an unrelated, higher-risk action later in the same session. Action approval workflows route irreversible or high-consequence actions through a human approval gate or a secondary automated control before execution, with the approval itself captured in the immutable audit log.

**Secure agent operating system pattern.** Across vendors and frameworks, the architecture converging as best practice resembles a minimal operating system built specifically for agent execution, with four layers stacked between the agent's reasoning loop and the outside world: the Agent layer is the reasoning/planning loop itself, treated as untrusted input to everything below it; the Sandbox layer is the isolation boundary (Firecracker/Kata/gVisor/WASM per the tiering above) that contains what the agent can directly touch; the Policy Engine layer is the authorization decision point (commonly OPA or Cedar) that every action must clear before reaching a tool; and the Tool Broker / Runtime Controller is the only component with actual credentials to downstream systems — it receives a policy-approved request and a scoped, ephemeral credential, executes the call, and returns only the result, never the credential, to the agent.

The structural property worth emphasizing: the agent itself never holds standing credentials to anything. It holds, at most, a short-lived capability token whose actual exchange for a usable credential happens inside the tool broker, after a policy check. This single design decision — credential custody lives outside the agent process — eliminates an entire category of incidents where a compromised or manipulated agent simply exfiltrates whatever secrets it was holding.

## AI Security Mesh Architecture

As agent populations scale past a few dozen into the hundreds or thousands, point-to-point security controls between every agent, tool, and data source stop being tractable — the same inflection point that drove the industry from point-to-point service integration toward service mesh architecture a decade ago. The AI Security Mesh pattern applies that same architectural move to agentic systems.

**The five mesh planes:**

| Mesh Plane | Function | Representative Technology Pattern |
|---|---|---|
| Identity Mesh | Issues and verifies workload identity for every agent, tool, and MCP/A2A endpoint uniformly | SPIFFE/SPIRE trust domain spanning all agent infrastructure |
| Policy Mesh | Centralizes authorization decisions so policy is defined once and enforced consistently at every enforcement point | OPA or Cedar policy bundles distributed to sidecars/brokers at each agent and MCP gateway |
| Agent Mesh | Manages discovery, routing, and trust establishment between agents and agent-to-agent calls | A2A trust broker with signed Agent Card verification |
| Memory Mesh | Governs how memory is shared, isolated, and classified across agents and sessions | Tenant-isolated vector stores and graph memory with provenance tagging |
| Observability Mesh | Aggregates traces, logs, and behavioral signals across every plane into a unified view | OpenTelemetry-based tracing feeding a central AI SOC |

**Comparison with service mesh and Zero Trust.** The AI Security Mesh is best understood as a service mesh's conceptual sibling, not its replacement — most enterprises will run both, with the AI Security Mesh as an agent-aware layer on top of (or alongside) an existing Istio/Linkerd-class service mesh:

| Property | Traditional Service Mesh | AI Security Mesh |
|---|---|---|
| Unit of identity | Service / workload (often per-deployment) | Individual agent instance, often ephemeral and per-task |
| Primary trust question | Is this service authorized to call that service? | Is this agent authorized to take this action, with this data, on behalf of this principal, right now? |
| Policy granularity | Network-level (which services can talk to which) | Action-level (which specific tool calls, with which parameters, are permitted) |
| Failure mode of concern | Service unavailability, latency, network partition | Goal hijacking, cascading multi-agent failure, autonomous over-reach |
| Relationship to SPIFFE/Zero Trust | SPIFFE commonly used as the identity substrate; zero trust is the governing principle | Same substrate (SPIFFE/SPIRE), extended with agent-specific attestation and behavioral trust scoring layered on top |

**Design recommendation:** do not build a parallel identity system for agents. Extend the organization's existing SPIFFE/SPIRE (or equivalent workload identity) trust domain to cover agent workloads, and layer agent-specific policy and behavioral-trust evaluation on top of that shared identity substrate. This is the path the most mature production implementations have taken, and it avoids the fragmentation that has plagued early agent-identity tooling.

## Related

- [Foundations & Reference Architecture (Part 1)](../33-foundations-reference-architecture.md)
- [Foundations & Reference Architecture: Threat Modeling (Part 2)](33-foundations-reference-architecture-part2.md)
- [Identity/MCP/A2A Security Blueprint](../34-identity-mcp-a2a-security-blueprint.md)
