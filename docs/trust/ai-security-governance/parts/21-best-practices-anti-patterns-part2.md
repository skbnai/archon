---
title: "Best Practices & Anti-Patterns (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: best-practices-anti-patterns-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/deep-mind/Part17_Best_Practices_Anti_Patterns.md]
tags: [ai-security, best-practices, deepmind, anti-patterns, maturity-model]
covers_version: "as of 2026"
---

Six named security anti-patterns, scaling pitfalls at fleet scale, eight lessons learned from enterprise deployments, a production readiness checklist, the five-level AI Control Maturity Model, and a phased implementation roadmap.

## Security Anti-Patterns

**The Omnipotent Agent.** A single agent is granted broad permissions to complete complex tasks efficiently, often justified by "it's easier to give it everything it needs." A compromised omnipotent agent becomes an insider threat with enterprise-wide reach — single agents with broad permissions have enabled complete data exfiltration in documented incidents, and the blast radius is essentially unlimited. **Mitigation:** never build omnipotent agents; decompose complex tasks into narrowly scoped sub-agents with minimal capabilities each.

**The Invisible Agent.** Agents deployed without full observability, often on the reasoning that "it's just a simple agent, we don't need full telemetry" — usually a result of cost pressure on logging and monitoring infrastructure. Without behavioral telemetry, compromise, policy violation, or behavioral drift cannot be detected. **Mitigation:** every agent must have full observability with no exceptions; the cost of observability is trivial compared to the cost of an undetected incident persisting for weeks.

**The Trusted Prompt.** Treating content from authorized sources (internal systems, trusted APIs, known users) as inherently safe and bypassing input validation. Indirect prompt injection attacks inject malicious instructions through trusted content channels — documents, emails, database records, API responses. **Mitigation:** all inputs must be validated and sanitized regardless of source; trust the channel, but validate the content.

**The Permanent Agent.** Agents run indefinitely as always-on services, accumulating session state and maintaining persistent connections to enterprise systems. Long-running agents accumulate attack surface over time, and memory poisoning attacks can build up gradually across sessions. **Mitigation:** prefer short-lived, task-scoped agents with clean state on each invocation — ephemeral is safer than persistent.

**The Human-Free Pipeline.** Fully automated agent pipelines with no human checkpoints, justified by speed and efficiency requirements. When an agent malfunctions or is compromised, fully automated pipelines allow damage to propagate at machine speed before detection. **Mitigation:** all high-risk autonomous pipelines must have mandatory human checkpoint gates, even if they introduce latency — design for safety first and optimize for speed second.

**The Model-as-Security-Boundary.** Relying on the AI model's training to prevent harmful actions — "the model is trained not to do X." Model-level safety training is a valuable defense layer, but it is not a security boundary: models can be jailbroken, fine-tuned adversarially, or simply replaced by attackers. **Mitigation:** security must be enforced at the infrastructure level, independent of model behavior; model safety is defense-in-depth, not the primary boundary.

## Scaling Pitfalls

**Policy engine bottlenecks.** At scale, centralized policy engines become latency bottlenecks: each agent action requiring policy evaluation adds round-trip latency, and with thousands of concurrent agents a single OPA or Cedar instance becomes the system's critical path and a single point of failure. Mitigations: implement policy decision caching with short TTLs (30-60s) for repeated identical queries; deploy policy engines as regional shards with eventual consistency for non-critical policies; use policy compilation to pre-compute common decision paths into optimized bundles; implement local policy evaluation for low-risk actions with central evaluation reserved for high-risk; set SLA targets of &lt;10ms p99 for low-risk and &lt;100ms p99 for high-risk policy evaluations; deploy policy engines with N+2 redundancy and never a single instance in production.

**Observability data volume.** Full behavioral telemetry from thousands of agents generates enormous data volumes. Organizations that capture everything without a sampling and tiering strategy quickly exhaust storage budgets and overwhelm analysis systems, leading to dropped data at the worst possible moment.

| Tier | Data Type | Retention | Storage Cost | Access Pattern |
|---|---|---|---|---|
| Hot (0-7 days) | Full reasoning traces, tool calls, all actions | 7 days | High | Real-time investigation |
| Warm (7-90 days) | Sampled traces, policy decisions, anomalies | 90 days | Medium | Incident investigation |
| Cold (90d-7yr) | Aggregated metrics, audit events, compliance records | 7 years | Low | Compliance, forensics |

**Identity management at scale.** Managing thousands of agent identities using traditional IAM approaches creates administrative overhead that scales poorly — static role assignments and manual certificate management break down at agent-fleet scale. Implement SPIFFE/SPIRE for automated workload identity issuance and rotation to eliminate manual certificate management; use hierarchical identity namespaces of the form `spiffe://corp/agents/{team}/{function}/{instance-id}`; automate certificate rotation with zero-downtime renewal, rotating at 50% of lifetime by default; use identity federation for cross-cloud deployments rather than static cross-account credential sharing; implement identity lifecycle automation integrated with agent deployment pipelines.

**Approval gate fatigue.** Human approval gates are essential for high-risk actions, but poorly calibrated gates create approval fatigue — approvers faced with hundreds of daily approvals begin rubber-stamping without review, defeating the purpose of human oversight entirely. Calibration guidelines: target no more than 10-15 high-risk human approvals per approver per day; automate all low-risk approvals with audit logging rather than routing them to humans; use ML-based risk scoring to route only genuinely uncertain cases to human review; rotate approvers to prevent habituation and maintain alertness; track approval-to-reject ratios, since ratios above 99:1 likely indicate calibration problems; survey approvers quarterly for fatigue signals and adjust thresholds proactively.

## Lessons Learned from Enterprise Deployments

1. **Identity before capabilities.** Organizations that attempted to deploy agents without solving the identity problem first consistently encountered serious security issues — least privilege cannot be enforced without knowing who the agent is. Solve workload identity (SPIFFE/SPIRE or equivalent) before any agent accesses production data.
2. **Start with read-only agents.** The safest starting point for any new agent class is read-only capabilities: establish behavioral baselines, refine observability, and validate policy effectiveness before granting write or action capabilities. Organizations that started with write-capable agents had significantly higher incident rates during the first 90 days of deployment.
3. **Governance overhead is real — plan for it.** Early enterprise deployments consistently underestimated the operational overhead of agent governance. A 10-agent deployment typically requires 0.5 FTE for ongoing policy management, 0.25 FTE for incident response capacity, and 0.25 FTE for compliance reporting; budget accordingly.
4. **The first incident will expose your gaps.** Every organization's first serious AI agent incident reveals gaps that were invisible during planning. The most common discoveries: kill switch procedures not documented, observability that didn't capture the right data, and recovery procedures that had never been tested. Conduct red team exercises before the first incident, not after.
5. **Tool sprawl is the dominant risk vector.** Across documented incidents, unauthorized or unreviewed tool usage was the most common root cause — agents with access to many tools have a correspondingly large attack surface. Rigorous tool governance consistently reduces incident rates more than any other single control; prioritize tool governance above all.
6. **Memory is an underappreciated attack surface.** Memory poisoning — where adversarial content is injected into agent long-term memory to influence future behavior — was almost universally underestimated in pre-deployment threat models. Persistent memory must be treated as a critical security asset from day one, with classification, access controls, integrity verification, and anomaly detection on access patterns.
7. **Compliance teams need early involvement.** Organizations that involved legal and compliance teams late in the deployment process consistently faced costly redesigns. Key compliance requirements — audit trail formats, data residency, retention periods, right-to-explanation obligations — are architectural requirements that are expensive to retrofit. Involve compliance from the initial design phase.
8. **The 90-day behavioral drift pattern.** Deployed agents consistently show measurable behavioral drift after approximately 60-90 days in production, appearing to result from accumulated memory updates, evolving prompt libraries, and tool API changes. Schedule formal behavioral re-baseline assessments at 30, 90, and 180 days post-deployment.

## Production Readiness Checklist

Before any AI agent progresses to production, all checklist items must be verified and signed off by the responsible team. Attach a completed checklist to the agent deployment record and retain for audit.

**Identity & authentication:**

- [ ] Unique cryptographic workload identity assigned (SPIFFE SVID or cloud-native equivalent)
- [ ] Identity attestation validated against authoritative identity provider
- [ ] Certificate rotation configured with zero-downtime renewal
- [ ] No shared credentials with other agents or services
- [ ] Identity revocation procedure documented and tested

**Authorization & policy:**

- [ ] Capability inventory documented — every tool and data source the agent can access
- [ ] Least-privilege review completed — no unnecessary capabilities granted
- [ ] Formal policies written in Cedar/OPA and peer-reviewed by AI Security Team
- [ ] Policy tests written and passing in CI/CD pipeline
- [ ] Approval gate thresholds defined and configured in policy engine
- [ ] JIT capability token configuration validated with expiry testing

**Runtime controls:**

- [ ] Kill switch implemented, documented, tested, and operator-trained
- [ ] Circuit breakers configured for all external tool dependencies
- [ ] Checkpoint/rollback capability validated in staging environment
- [ ] Blast radius analysis completed and documented in agent record
- [ ] Rate limits configured for all tool APIs and outbound requests
- [ ] Execution timeout limits set for all agent task types

**Observability:**

- [ ] Full reasoning telemetry enabled and validated end-to-end
- [ ] Tool call logging confirmed with complete audit trail
- [ ] Memory access audit logging enabled and tested
- [ ] Behavioral baseline established from minimum 48h staging data
- [ ] Anomaly detection rules configured, tested, and alert routing confirmed
- [ ] SIEM integration validated with synthetic test alerts
- [ ] Monitoring dashboard created and accessible to on-call team

**Governance & compliance:**

- [ ] RACI matrix defined for this agent with named owners
- [ ] Data classification completed for all data accessed by the agent
- [ ] Regulatory compliance review completed (GDPR, HIPAA, SOX as applicable)
- [ ] Audit trail format validated against retention and format requirements
- [ ] Right-to-explanation mechanism implemented where legally required
- [ ] Incident response runbook created, reviewed, and distributed to on-call team
- [ ] Recovery procedures documented and tested in staging
- [ ] 90-day formal review scheduled in team calendar

**Security validation:**

- [ ] Prompt injection testing completed — both direct and indirect attack vectors
- [ ] Capability escalation testing completed with no critical findings unresolved
- [ ] Memory poisoning simulation completed
- [ ] Tool abuse scenario testing completed
- [ ] Identity spoofing resistance validated against all agent endpoints
- [ ] Data exfiltration path analysis completed
- [ ] Supply chain review of all tool and model dependencies completed

## AI Control Maturity Model

Organizations can assess their AI control maturity across five levels. Honest self-assessment is essential — most enterprises entering production agent deployment begin at Level 1 or 2. Progress through the levels requires sustained organizational commitment, not just tooling.

| Level | Name | Characteristics | Target Timeline |
|---|---|---|---|
| 1 | Ad Hoc | No formal AI security policies; agents deployed with broad permissions; minimal logging; no incident response plan | Starting point |
| 2 | Developing | Basic IAM integration; some policy documentation; audit logging enabled; manual incident response procedures | 0-90 days |
| 3 | Defined | Formal policy-as-code; workload identity implemented; behavioral monitoring active; documented playbooks; regular security reviews | 90-180 days |
| 4 | Managed | Automated policy enforcement; continuous behavioral analytics; integrated SOC; governance operating model established; regular red team exercises | 180-365 days |
| 5 | Optimizing | Adaptive risk-based controls; ML-driven anomaly detection; automated incident response; continuous compliance; proactive threat hunting | 12+ months |

**Assessment approach:** evaluate maturity independently for each control domain (identity, policy, runtime, observability, governance) rather than assigning a single overall score. It is common and acceptable to be at Level 4 in observability while still at Level 2 in governance — build a domain-by-domain improvement roadmap rather than trying to advance all domains simultaneously.

## Implementation Roadmap

The following phased roadmap provides a practical sequence for organizations building enterprise AI control capabilities. Phases are designed to deliver security value incrementally while building toward full operational maturity.

| Phase | Timeline | Key Deliverables | Success Metrics |
|---|---|---|---|
| Phase 1: Foundation | Days 1-30 | Workload identity deployed; basic policy-as-code implemented; audit logging enabled; incident response runbook drafted | 100% agents with verified identity; zero standing credentials |
| Phase 2: Control | Days 31-90 | Policy engine in production; approval gates active; behavioral monitoring deployed; kill switches tested | &lt;50ms policy evaluation p99; kill switch test &lt;60s activation |
| Phase 3: Governance | Days 91-180 | RACI model operational; agent registry complete; tool governance program launched; SOC integration complete | 100% agents in registry; all tools reviewed and approved |
| Phase 4: Optimization | Days 181-365 | Automated anomaly detection; risk-adaptive controls; red team program established; compliance reporting automated | MTTD &lt;15 min; compliance reports fully automated |
| Phase 5: Excellence | Year 2+ | Proactive threat hunting; behavioral AI in SOC; full supply chain verification; continuous maturity improvement | Zero critical incidents; Level 5 maturity across all domains |

## Related

- [Best Practices & Anti-Patterns (Part 1)](../21-best-practices-anti-patterns.md)
- [Reference Architecture](../20-reference-architecture.md)
- [AI Control Series Overview](../01-ai-control-series-overview.md)
