---
title: "Best Practices & Anti-Patterns"
doc_type: guide
domain: trust
status: current
topic_id: best-practices-anti-patterns
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part17_Best_Practices_Anti_Patterns.md]
tags: [ai-security, best-practices, deepmind, design-principles]
covers_version: "as of 2026"
---

The twelve principles of enterprise AI control, the layered control stack and four-zone trust boundary model, implementation patterns (capability tokens, supervisor agents, canary deployment), operational playbooks, and common production mistakes.

## Foundational Design Principles

Decades of enterprise security experience, combined with lessons from early AI agent deployments, have yielded a consolidated set of principles that should guide every production AI control architecture.

**The twelve principles of enterprise AI control:**

1. **Minimal Capability by Default.** Every AI agent must operate with the minimum set of capabilities required to complete its assigned task. Capabilities should be granted explicitly, audited continuously, and revoked automatically when tasks complete. Never grant standing permissions to AI agents.
2. **Explicit Trust — Never Implicit.** AI agents must earn trust through verifiable identity, behavioral consistency, and cryptographic attestation. No agent should be trusted simply because it claims a role. All trust assertions must be verified against authoritative identity providers using cryptographic proof.
3. **Defense in Depth for Reasoning.** Multiple independent controls must govern agent behavior: policy engines, behavior monitors, supervisor agents, and human approval gates. No single control layer should be relied upon exclusively. Assume each layer will occasionally fail and design accordingly.
4. **Human Override is Non-Negotiable.** Every autonomous operation must have a defined human override path. Kill switches, approval gates, and circuit breakers must be implemented at every trust boundary. Override mechanisms must be tested regularly and must function even when the primary control plane is degraded.
5. **Immutable Audit Trails.** Every agent action, tool invocation, memory read/write, and decision must be recorded to tamper-evident, append-only audit logs. Audit systems must be logically and physically isolated from the agents they monitor. Logs must capture reasoning context, not just action outcomes.
6. **Policy as Code.** All agent policies must be version-controlled, peer-reviewed, tested, and deployed through CI/CD pipelines. Policies expressed in natural language are insufficient for production systems. Use Cedar, OPA/Rego, or equivalent formal policy languages with automated compliance testing.
7. **Blast Radius Containment.** Every agent deployment must have defined blast radius limits. If an agent is compromised or malfunctions, the maximum possible damage must be bounded by architecture — not by hoping the agent behaves correctly. This includes data access limits, outbound network restrictions, and resource quotas.
8. **Verifiable Provenance.** Every output, action, and decision must carry cryptographically verifiable provenance: which agent produced it, with which model version, at what time, with what inputs. Provenance chains enable forensic investigation and regulatory compliance reporting.
9. **Graceful Degradation.** AI systems must fail safely. When control plane components are unavailable, agents must degrade to minimal-capability or safe-halt modes. Never allow control plane failures to result in unrestricted agent operation with no oversight.
10. **Continuous Behavioral Validation.** Agent behavior must be continuously compared against established behavioral baselines. Drift from baseline — even within policy boundaries — must trigger investigation. Behavioral anomalies often precede security incidents by days or weeks.
11. **Separation of Concerns Across Planes.** Identity, policy, execution, observability, and governance must operate as independent planes with well-defined interfaces. Monolithic designs create dangerous single points of failure and make incident response significantly more difficult.
12. **Treat Agents as Privileged Employees.** Apply the same security standards to AI agents as to privileged human employees: background verification (model provenance checks), least privilege, dual control for sensitive operations, mandatory re-evaluation cycles, and immediate revocation upon decommission.

## Reference Architecture Patterns

**The layered control stack.** Production AI systems must implement a layered control stack where each layer provides independent enforcement. The following five-layer model has emerged as a consensus pattern across enterprise deployments:

| Layer | Component | Responsibility | Failure Mode |
|---|---|---|---|
| L1 — Identity | SPIFFE/SPIRE, Cloud IAM | Cryptographic agent identity, workload attestation | Identity spoofing, credential theft |
| L2 — Policy | Cedar, OPA/Rego, OpenFGA | Authorization, capability grants, policy evaluation | Policy bypass, misconfiguration |
| L3 — Runtime | Interception proxy, circuit breakers | Action interception, live risk scoring, kill switches | Policy engine failure, proxy bypass |
| L4 — Observability | OpenTelemetry, Langfuse, SIEM | Behavioral telemetry, anomaly detection, alerting | Log tampering, monitoring blind spots |
| L5 — Governance | RACI processes, approval workflows | Human oversight, policy lifecycle, compliance | Governance fatigue, process bypass |

**The four-zone trust boundary model.** Every AI architecture must explicitly define trust boundaries. The standard enterprise model defines four zones, each with distinct enforcement characteristics:

- **Zone 0 — Untrusted External:** everything outside enterprise control — external APIs, third-party MCP servers, user inputs, web content. Nothing from this zone is trusted. All inputs are validated, sanitized, and treated as potentially adversarial.
- **Zone 1 — DMZ / Mediation Layer:** gateway components that translate between external and internal zones. Input validation, prompt sanitization, rate limiting, and authentication occur here. No raw external content reaches Zone 2 unprocessed.
- **Zone 2 — Controlled Execution:** where agents operate. Tightly scoped capabilities, full observability, policy enforcement at every action. Agents in Zone 2 operate under continuous behavioral monitoring.
- **Zone 3 — Trusted Core:** enterprise data systems, identity providers, policy engines, audit infrastructure. Minimal agent access. Accessed only through well-defined, audited APIs with JIT permissions.

**The approval gate pattern.** High-risk actions must pass through approval gates before execution. Risk tiers determine gate behavior:

| Risk Tier | Criteria | Gate Behavior | Timeout Behavior |
|---|---|---|---|
| Low | Reversible, limited blast radius, no sensitive data | Auto-approve, audit log entry only | N/A |
| Medium | Moderate blast radius, some sensitive data access | Async human notification, 30-min window | Safe-halt — no auto-approve |
| High | Large blast radius, sensitive data, irreversible | Synchronous human approval required | Safe-halt with escalation |
| Critical | Irreversible, maximum blast radius, regulated data | Dual human approval required | Automatic safe-halt + alert |

## Implementation Patterns

**The sidecar security pattern.** Borrowed from service mesh architectures, the sidecar pattern deploys a security proxy alongside each agent container. The sidecar intercepts all agent communications, enforces policy, and emits telemetry without modifying agent code. This provides consistent enforcement across heterogeneous agent implementations.

**Implementation:** Deploy security sidecars using Kubernetes admission webhooks that automatically inject the sidecar into every agent pod. The sidecar must share no process namespace with the agent.

**The capability token pattern.** Rather than assigning static permissions to agents, issue short-lived capability tokens scoped to specific tasks. Tokens are cryptographically signed, carry mandatory expiry timestamps, and enumerate exactly which tools and data resources the agent may access during the current task execution.

| Token Field | Description | Example Value |
|---|---|---|
| `agent_id` | Cryptographic agent identifier | `spiffe://corp/agents/hr-assistant/prod/abc123` |
| `task_id` | Unique task identifier | `task_20260625_hr_onboard_emp99` |
| `capabilities` | Explicit capability grants | `['read:hr_db', 'write:slack', 'call:workday_api']` |
| `not_before` | Token validity start | `2026-06-25T09:00:00Z` |
| `expires_at` | Mandatory expiry (max 4h) | `2026-06-25T13:00:00Z` |
| `max_actions` | Action count hard limit | `50` |
| `blast_radius` | Maximum data exposure class | `CONFIDENTIAL` |
| `human_override` | Override contact | `agent-oversight@corp.com` |

**The supervisor agent pattern.** For complex multi-step workflows, deploy a dedicated supervisor agent whose sole responsibility is monitoring worker agents for policy compliance, behavioral consistency, and goal alignment. The supervisor runs with a separate identity and independent policy evaluation chain.

**Anti-pattern:** Never allow the supervisor and worker agents to share the same model instance, policy engine, or identity provider. Shared infrastructure creates single points of failure that can compromise the entire oversight system simultaneously.

**The canary deployment pattern.** Before full production deployment, route a small percentage of real traffic through new agent versions under heightened monitoring. Compare behavioral profiles between canary and baseline. Promote only when behavioral equivalence is confirmed within acceptable variance bounds. Recommended initial canary: 5% traffic, minimum 72-hour observation window before promotion to 25%, then to 100%.

**The memory versioning pattern.** Agent memory must be versioned using immutable snapshots, similar to database point-in-time recovery. Each significant memory update creates a new version with full provenance metadata. In the event of memory poisoning, agents can be rolled back to a known-good memory state without full redeployment. Minimum recommended retention: 30 snapshot versions per agent.

**The federated policy pattern.** In enterprises with multiple business units or cloud environments, maintain a federated policy architecture. A central policy authority defines enterprise-wide baseline policies. Business units may define additional constraints but may never relax enterprise baseline policies. Policy evaluation occurs at the local level with periodic reconciliation against the central authority. Policy conflicts resolve in favor of the more restrictive policy.

## Operational Playbooks

**Agent onboarding playbook.** Every new agent must pass through a structured onboarding process before production access:

1. **Architecture Review (Week 1-2):** submit architecture design to the Architecture Review Board. Review must cover threat model, trust boundaries, capability requirements, data classification, blast radius analysis, and recovery procedures. Board sign-off required.
2. **Security Assessment (Week 2-3):** red team assessment including prompt injection testing, capability escalation attempts, identity spoofing tests, memory poisoning simulation, and tool abuse scenarios. Minimum passing score: 85/100. Critical findings must be resolved before proceeding.
3. **Policy Definition (Week 3):** define formal policies in Cedar/OPA covering permitted tools, data access classes, action limits, approval gate thresholds, and behavioral baselines. Policies peer-reviewed by the AI Security Team and version-controlled.
4. **Staging Validation (Week 4):** deploy to a staging environment with full observability enabled. Run the standard behavioral test suite. Establish behavioral baseline metrics for anomaly detection. Document the baseline in the agent inventory.
5. **Limited Production Pilot (Week 5-6):** canary deployment to 5% of traffic with human review of all high-risk actions. Monitor for behavioral drift, policy violations, and unexpected capability usage. Minimum 72-hour observation at each traffic level.
6. **Full Production Deployment (Week 7+):** promote to full production after pilot success criteria are met. Maintain elevated monitoring for 30 days. Schedule the first quarterly review at 90 days post-deployment. Record the deployment in the agent registry.

**Incident response playbook:**

- **Phase 1 — Detection (0-5 minutes):** automated behavioral anomaly detection triggers an alert. SIEM correlation identifies the incident pattern. The on-call ADR analyst receives a page. An incident ticket is auto-created with full context capture.
- **Phase 2 — Containment (5-15 minutes):** execute agent quarantine — revoke capability tokens, disconnect from tool APIs, suspend memory writes. If agent compromise is confirmed, activate the kill switch. Preserve all execution state for forensics before any cleanup.
- **Phase 3 — Investigation (15-60 minutes):** retrieve immutable audit logs for the affected agent. Reconstruct the execution timeline. Identify the attack vector (prompt injection, tool poisoning, memory corruption, identity compromise?). Determine the blast radius.
- **Phase 4 — Eradication (1-4 hours):** remove compromised components — roll back memory to the last known-good snapshot, revoke and reissue identity credentials, patch the exploited vulnerability, update policy to prevent recurrence.
- **Phase 5 — Recovery (4-24 hours):** restore the agent in an isolated environment with enhanced monitoring. Validate behavioral equivalence to the pre-incident baseline. Gradual traffic restoration with human oversight at each traffic increment.
- **Phase 6 — Post-Incident (24-72 hours):** document root cause analysis. Update the threat model. Distribute lessons learned. Update detection rules. Regulatory notification if required. Executive briefing if material business impact.

**Agent retirement playbook.** Retiring agents is as security-critical as deploying them. Execute this sequence in order:

1. Issue a 30-day deprecation notice to all dependent systems and users.
2. Identify all active sessions — complete gracefully or hand off to replacement agents.
3. Export and archive agent memory with full provenance metadata to cold storage.
4. Revoke all capability tokens, API keys, and service account credentials.
5. Remove the agent from tool registries and API gateway routing configurations.
6. Delete or archive agent container images from all registries.
7. Retain audit logs per regulatory retention schedule (minimum 7 years for regulated industries).
8. Document retirement in the agent inventory with reason code, date, and responsible owner.
9. Notify all downstream systems of agent retirement with a deprecation date.
10. Conduct post-retirement validation: confirm no residual access or running instances remain.

## Common Mistakes in Production Deployments

**Architecture mistakes:**

- **Trusting Agent Self-Reporting.** Never accept an agent's self-reported identity, capabilities, or task context at face value. All claims must be verified against authoritative systems. Agents can be manipulated via prompt injection to misrepresent their identity or authorized scope. *Correct approach:* verify all identity and capability claims cryptographically against your identity provider. Policy decisions must be based on verified attestations, not agent-supplied claims.
- **Sharing Policy Engines Across Trust Levels.** Using the same policy engine instance to evaluate policies for both low-trust and high-trust agents creates a lateral movement path. A compromise of a low-trust agent could affect high-trust policy evaluation. *Correct approach:* deploy separate policy engine instances per trust tier with no shared configuration state. Policy engine isolation is a security boundary, not an optimization choice.
- **Logging Only Final Outcomes.** Recording only what agents did (final action) without capturing reasoning context makes forensic investigation nearly impossible. You cannot determine if an action was legitimate without the full reasoning chain. *Correct approach:* log full reasoning traces, intermediate decisions, and tool call chains alongside final actions. Reasoning telemetry is not optional for production AI systems.
- **Static Capability Assignment.** Granting fixed, standing permissions to agents creates unnecessary persistent attack surface. Agents retain capabilities even when idle, enabling persistent exploitation if credentials are compromised. *Correct approach:* use short-lived, task-scoped capability tokens that expire automatically. No agent should hold standing permissions beyond 4 hours without re-attestation.
- **Treating Prompt Engineering as Security.** Relying on instructions in system prompts to enforce security boundaries is a critical error. System prompts can be overridden by sufficiently sophisticated prompt injection or model manipulation. *Correct approach:* enforce all security through cryptographic controls and code, never through model instructions alone. Prompts are configuration; security boundaries must be enforced at the infrastructure level.

**Operational mistakes:**

- **Setting Kill Switches and Never Testing Them.** Many organizations deploy kill switches in theory but never validate they function correctly under production load. When an actual incident occurs, the kill switch fails due to configuration drift, dependency failures, or operator unfamiliarity with the procedure. *Correct approach:* test kill switch activation quarterly in production (with controlled agents) and after every major infrastructure change. Document the test results and operator training.
- **Insufficient Blast Radius Analysis.** Underestimating what a compromised agent can reach leads to devastating incidents. Teams often scope blast radius to direct tool access without accounting for data an agent can read and exfiltrate, or systems reachable via chained tool calls. *Correct approach:* conduct full attack path analysis including multi-hop tool chains and data access reachability graphs. Treat tool chaining as a first-class threat vector.
- **Governance Theater.** Creating elaborate RACI matrices, approval workflows, and review boards that exist on paper but are routinely bypassed due to friction or urgency. Governance that is too cumbersome will be circumvented, often silently. *Correct approach:* design governance for the realistic operational tempo. Automate low-risk approvals. Reserve human review for genuinely high-risk decisions. Measure governance compliance and investigate bypasses.
- **Neglecting Memory Hygiene.** Allowing agent memory to accumulate indefinitely without classification, retention policies, or access controls creates compounding regulatory and security risk. Old memories may contain sensitive data that should have been deleted under GDPR or similar regulations. *Correct approach:* implement automated memory lifecycle management — classify on creation, enforce retention limits, audit access patterns, and provide deletion verification for compliance requests.

## Related

- [Best Practices & Anti-Patterns (Part 2)](parts/21-best-practices-anti-patterns-part2.md) — security anti-patterns, scaling pitfalls, lessons learned, production readiness checklist, maturity model, implementation roadmap
- [Reference Architecture](20-reference-architecture.md)
- [AI Control Series Overview](01-ai-control-series-overview.md)
