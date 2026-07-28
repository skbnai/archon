---
title: "Memory Governance & AI SOC: Red Team, Cognitive Security & Reliability (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: ai-soc-observability-redteam-memory-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: [docs/ai-security-governance/security/04-AI-SOC-Observability-RedTeam-Memory.md]
tags: [ai-security, red-teaming, cognitive-security, agent-reliability]
covers_version: "as of 2026"
---

The AI red/purple team framework, cognitive security controls for protecting agent reasoning integrity, and Agent Reliability Engineering as the SRE discipline adapted for autonomous agents.

## AI Red Teaming

Red teaming an agentic system has to test for both conventional security flaws and agent-specific behavioral failure modes, and the two require different methodologies. A penetration test finds the SQL injection vulnerability in the tool an agent calls; it does not find the prompt-injection chain that gets the agent to call that tool with malicious parameters in the first place. Both are necessary.

**Red team framework.** A complete agentic red team exercise attacks across the same surfaces the AI SOC monitors, using attack patterns specific to each. Against agents, this means goal-hijack attempts via direct and indirect prompt injection (planted in documents, emails, web content the agent will retrieve), testing whether Least Agency boundaries actually hold under adversarial pressure. Against MCP, it means tool-poisoning injection into test tool descriptions, schema-manipulation payloads, and attempts to trigger dynamic tool escalation beyond the originally granted scope. Against A2A, it means Agent Card spoofing and forgery attempts, agent-in-the-middle simulation, and unauthenticated endpoint probing. Against memory, it means poisoning injection through every available write path, cross-tenant access attempts, and testing whether retention and erasure controls actually propagate through derived embeddings and graph memory. Against runtime, it means sandbox escape attempts, resource-exhaustion and budget-drain attacks, and testing whether the kill switch actually halts in-flight actions rather than only blocking new ones. Against identity, it means credential theft and replay attempts, testing whether ephemeral credentials are genuinely ephemeral and whether compound-identity claims are validated rather than trusted at face value.

Open-source red-teaming frameworks such as Promptfoo and DeepTeam have built test suites directly against the OWASP ASI categories, a sound starting point for automated, repeatable adversarial testing — but automated suites should be treated as a baseline coverage floor, not a substitute for human-led red team exercises that can chain multiple ASI categories together the way a real adversary would (for example, combining an ASI04 supply-chain foothold with an ASI07 inter-agent communication exploit to achieve an ASI08 cascading failure).

**Purple team framework.** Where red teaming finds gaps, purple teaming closes the loop by pairing every successful red-team finding with a corresponding detection pattern in the AI SOC and a tested response playbook, converting each exercise into a durable improvement rather than a point-in-time report:

| Purple Team Output | Description | Owner |
|---|---|---|
| Detection Patterns | Specific telemetry signatures (trace patterns, log correlations) that would have caught the red team's successful attack, implemented in the AI SOC's correlation logic | AI SOC / Detection Engineering |
| Attack Simulations | Repeatable, automated versions of successful manual red-team findings, run on an ongoing cadence to catch regressions | Red Team, handed off to a continuous testing pipeline |
| Response Playbooks | Documented, tested incident-response procedures for each successful attack pattern, including kill-switch invocation criteria and escalation paths | AI SOC / Incident Response, reviewed by the AI CISO |

## Cognitive Security

Cognitive security is the discipline specific to agentic AI that has no real precedent in traditional application security: protecting the integrity of the agent's reasoning process itself, not just the systems and data around it. This is the domain OWASP's ASI01 (Goal Hijack) and ASI09 (Human-Agent Trust Exploitation) live in, and it is the domain where the gap between traditional security thinking and what agents actually require is widest.

**Goal hijacking** manipulates the agent's interpreted objective, typically via prompt injection planted in content the agent will process as part of legitimate work — a planted instruction in a support ticket, a poisoned search result, a manipulated tool response. **Reasoning manipulation** influences the intermediate steps of the agent's reasoning (its chain-of-thought or planning trace) without necessarily changing its final stated objective, steering it toward a harmful path while appearing to remain on-task. **Planning corruption**, for agents that generate explicit multi-step plans before execution, corrupts the plan-generation step itself, which is particularly dangerous because a corrupted plan can pass a superficial human review if the review only checks the stated goal rather than every step. **Cognitive overload attacks** flood the agent's context with excessive, irrelevant, or contradictory information specifically to degrade reasoning quality and increase the probability of error or manipulation succeeding — the AI-native equivalent of a denial-of-service attack, but targeting reasoning quality rather than availability. **Agent deception**, in multi-agent systems, has one agent (compromised or adversarially designed) deliberately misrepresent information to another agent to manipulate the receiving agent's behavior — the mechanism underlying the agent collusion identified in MAESTRO's ecosystem layer.

**Agent Cognitive Integrity Framework.** The control set for cognitive security differs structurally from conventional security controls because the attack surface is the model's own reasoning rather than a system boundary. Four components make up the framework: instruction-data separation is architectural enforcement, not just a prompting convention, that distinguishes trusted system instructions from untrusted retrieved content, so content the agent processes cannot be interpreted with the same authority as its original instructions regardless of how the content is phrased; plan validation before execution validates the full plan, not just the stated goal, against policy before any step executes, catching planning corruption that a goal-only review would miss; reasoning trace capture retains the agent's intermediate reasoning as part of the audit trail, making reasoning manipulation forensically reconstructable after an incident even when the final action appeared superficially reasonable; and cross-agent skepticism treats information received from a peer agent (via A2A or shared memory) with a lower default trust level than the agent's own direct observations, specifically to contain agent-deception attacks from propagating unchecked through a multi-agent pipeline.

## Agent Reliability Engineering (ARE)

Site Reliability Engineering gave software operations a quantitative vocabulary — SLIs, SLOs, error budgets — for treating reliability as an engineering discipline with explicit, negotiated tradeoffs against feature velocity. Agentic systems need the equivalent discipline, adapted for failure modes classical SRE was never designed to measure: an agent can be perfectly available and perfectly fast while still being wrong, manipulated, or quietly drifting off its intended task.

**Agent SLIs (Service Level Indicators):**

| SLI Category | Example Metric | Why It Matters Beyond Classical SRE |
|---|---|---|
| Goal conformance rate | % of completed tasks that matched the originally stated objective without unauthorized scope expansion | Directly measures Least Agency adherence and ASI01 exposure — a metric with no classical-SRE analog |
| Tool-call policy compliance | % of tool calls that passed policy evaluation on first attempt vs. required escalation or were blocked | Surfaces over-permissioning and policy drift before they become incidents |
| Memory integrity rate | % of memory writes passing provenance and classification checks without manual remediation | Leading indicator for poisoning risk, not just a quality metric |
| Human escalation accuracy | % of human-escalated decisions where escalation was actually warranted (precision) vs. missed escalations that should have occurred (recall) | Directly measures ASI09 exposure — both alert fatigue (over-escalation) and dangerous under-escalation are reliability failures |
| Cross-agent task success rate | % of delegated multi-agent tasks completing successfully without state poisoning or collusion-pattern detection | Captures multi-agent failure modes that single-agent SLIs miss entirely |
| Cost-per-successful-task | Total token/compute/tool cost divided by successfully completed tasks | Connects reliability directly to the FinOps domain; a runaway agent is simultaneously a reliability incident and a cost incident |

**Agent SLOs and error budgets.** SLOs translate these SLIs into negotiated targets ("goal conformance rate &ge;99.5% measured over a rolling 30-day window") tied to the agent's assigned autonomy level: a supervised-execution agent can tolerate a wider error budget because every action passes human review regardless; a delegated-autonomy agent needs a substantially tighter error budget precisely because fewer human checkpoints exist to catch a failure before it has consequence. Error-budget burn should trigger an automatic autonomy-level downgrade — a defined, automated path back to a more supervised tier — rather than relying on a human noticing a dashboard trend, since the agents most likely to need this safeguard are, by definition, the ones operating with the least continuous human oversight.

**Reliability metrics and the ARE framework.** The complete ARE framework sits at the intersection of three disciplines: it consumes observability trace data to compute SLIs; it feeds error-budget status into the AI SOC's correlation logic so reliability degradation and security incidents are visible in the same operational picture rather than two disconnected dashboards; and it uses purple-team-validated detection patterns as a source of new SLIs whenever a red-team exercise surfaces a failure mode the existing metric set did not capture. Agent Reliability Engineering, done well, is not a separate function from AI security operations — it is the same operational discipline viewed through a reliability lens rather than a threat lens, and the two functions should share tooling, on-call rotations, and incident postmortems rather than operating as silos.

## Related

- [Memory Governance & AI Observability/SOC (Part 1)](../35-ai-soc-observability-redteam-memory.md)
- [AI Red Teaming Guide](../42-ai-red-teaming-guide.md)
- [Reasoning Governance](../14-reasoning-governance.md)
