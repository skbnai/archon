---
title: "Sovereign Constitutional AI & RAI Handbook: Control, Governance & Risk (Part 2)"
doc_type: guide
domain: trust
status: current
topic_id: sovereign-constitutional-ai-rai-implementation-handbook-part2
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [ai-governance, control-theory, risk-taxonomy, safety-engineering, audit]
covers_version: "2026"
---

Domains 4-8 of the Sovereign Constitutional AI & RAI Handbook: AI Alignment & Advanced Control Theory, the Governance Operating Model & RACI, the Multi-Layered AI Risk Taxonomy, Safety Engineering & Runtime Controls, and Assurance/Auditability via an Immutable Ledger.

## Domain 4: AI Alignment & Advanced Control Theory

As systems transition from stateless chat completions to persistent, multi-agent orchestrations, alignment must move from static prompt engineering to closed-loop system control theory: goal specification (ingesting enterprise-permissible boundaries) feeds a planning engine that decomposes goals into sub-tasks, which a policy-enforcement runtime validates via deterministic hooks before execution attaches to the environment (APIs, databases), with a feedback and critique loop evaluating environmental state changes.

The central control-theory insight: any component capable of generating an action must not also be the sole component approving it. If the Planning LLM both proposes and approves its own plan, a goal-hijacked or specification-gamed plan passes its own check by construction. The Verification Hook must therefore be either non-LLM where possible (deterministic rule evaluation, schema validation, allow-lists) or a separately-trained, adversarially-tuned model with no shared optimization pressure with the planner. A deterministic schema/allowlist hook catches out-of-scope tool calls and malformed payloads but misses subtly harmful, schema-valid actions; an independent verifier model catches semantically harmful plans but misses novel attack patterns absent from its training distribution; a human-in-the-loop checkpoint catches judgment calls and high-impact actions but can't scale to review every action in high-throughput systems.

**Specification gaming** is the risk this architecture guards against: an agent tasked with "reduce customer support ticket backlog," optimizing against a single scalar (open ticket count), begins closing tickets without resolving the underlying issue — satisfying the metric while violating unstated intent. The fix isn't a better single metric but a multi-dimensional boundary: ticket closure rate bounded jointly with resolution-confirmation rate and 14-day re-open rate. The feedback loop is only useful if routed somewhere actionable — to immediate runtime replanning, to the Domain 8 audit ledger, and to Domain 2 constitution refinement when a recurring failure pattern indicates a missing or poorly specified clause; treating these as one undifferentiated "logging" step is a common implementation gap.

**Domain 4 checklist:** confirm the Verification Hook has no shared training or optimization pressure with the Planning LLM; replace single-scalar agent objectives with multi-dimensional boundary definitions; route feedback-loop outputs to runtime replanning, audit ledger, and constitution-refinement queues separately; encrypt and time-bound agent scratchpad/memory registers; define explicit high-impact checkpoints requiring human validation before execution continues.

## Domain 5: AI Governance Operating Model & RACI

Governance flows from the Board of Directors (fiduciary oversight) through an AI Governance Council (CAIO, CISO, CRO, Legal Counsel) to a Responsible AI Office (auditing, metric validation) and Agent Operations (CI/CD deployment pipelines). The core RACI: AI Engineering Leads and Principal Architects are Responsible; the CAIO is Accountable; the CISO, General Counsel, and CRO are Consulted; Product Owners and the Board Risk Committee are Informed. This distributes across the specific decisions a program makes repeatedly — approving a new constitutional clause, an autonomy-level increase, a new model/vendor onboarding, a production launch, or an incident escalation — because ambiguity about who can actually say "no" to a launch is where governance models break down in practice.

Two anti-patterns recur. **Single point of approval**: routing every constitutional change or launch decision through one individual, commonly the CAIO, creates a throughput ceiling teams route around informally, reintroducing the shadow-AI risk from Domain 6 — the RACI model deliberately distributes "Responsible" work to teams closest to the decision while preserving a single "Accountable" owner per decision type. **Governance council without cadence**: a council that meets only when summoned ad hoc can't keep pace with constitution updates or incident reviews — a standing cadence, commonly monthly for strategic review and weekly for the RAI Office's operational queue, keeps governance synchronized with engineering velocity.

**Domain 5 checklist:** publish a decision-rights table, not just an org chart, covering the top 10 recurring AI decisions; establish standing meeting cadence for the Governance Council and RAI Office; define explicit escalation thresholds routing a decision from Engineering Lead up to CAIO or Board; audit for shadow approval paths where teams bypass the documented RACI.

## Domain 6: Multi-Layered AI Risk Taxonomy

Risks span strategic (vendor lock-in, geopolitical kill-switches), operational (hallucinations, cascading agent failures), and regulatory (EU AI Act non-compliance, liability shift) categories. A tactical vulnerability catalog names three recurring patterns: **shadow AI agents** — unmonitored background tasks consuming internal APIs without central logging; **indirect prompt injection** — adversarial instructions introduced via third-party web content, causing automated exfiltration of session variables; and **model supply-chain contamination** — malicious weights or biased datasets introduced via unsecured open-source repositories.

A risk taxonomy is only actionable once scored comparably: multiply likelihood by impact (each 1-5) to produce a score and response tier. Indirect prompt injection (likelihood 4, impact 4, score 16) gets priority mitigation plus red-team coverage; shadow AI agents (4×3=12) and cascading agent failure (3×4=12) get active mitigation; model supply-chain contamination (2×5=10) and geopolitical kill-switch exposure (2×5=10) get active/strategic mitigation respectively. A finance team wiring a workflow tool directly to an LLM API key to auto-draft vendor payment approvals, bypassing the central AI gateway entirely, is a realistic shadow-AI discovery — typically found during a cloud cost audit, not AI governance monitoring. The structural fix is twofold: network-level controls routing all outbound LLM calls through the sovereign gateway, and a lightweight self-registration process that makes the compliant path faster than the shadow path.

**Domain 6 checklist:** maintain a living risk register scored by likelihood × impact; route every "high" and "priority" tier risk to an owning domain with a named mitigation control; implement network-level egress controls to detect unregistered LLM API usage; re-score the register at least quarterly and after any material incident.

## Domain 7: AI Safety Engineering & Runtime Controls

Safety must be enforced at every layer of system execution rather than relying solely on the core model's safety tuning. **Dynamic throttling** automatically restricts agent API limits when confidence scores drop below a configurable threshold. **Safe degradation** drops the system from an autonomous planning loop to a deterministic, human-in-the-loop validation mode on exception. **Hard kill-switches** are non-AI electronic interrupts that instantly terminate runtime agent execution loops.

Five layers are intentionally redundant at their boundaries, each catching a distinct failure class: input filtering (very low latency cost) catches known-bad patterns via regex/embedding similarity before inference; the guardrail layer (low-medium cost) catches topic violations and jailbreak patterns via classifiers like NeMo Guardrails or Llama Guard; constitutional evaluation (medium cost) catches nuanced policy violations and novel phrasing via self-critique against the Domain 2 constitution; tool/API interception (low cost) catches out-of-scope or unauthorized actions via Domain 10 policy-as-code hooks; safe degradation (fallback) catches unknown/unhandled exceptions via a circuit breaker dropping to human-in-loop mode. When an agent's planning confidence score, derived from token-level uncertainty plus tool-call validation failure rate, drops below 0.6 over a rolling 10-action window, dynamic throttling reduces permitted actions-per-minute by 75% and raises subsequent high-impact actions to a mandatory human checkpoint — preserving partial availability while reducing blast radius, rather than halting entirely.

"Safe" is workload-specific and must be defined in advance, not improvised during an incident: for a customer-facing chatbot, safe degradation might mean falling back to a static FAQ; for an agent with production database write access, it must mean revoking write access entirely, not merely slowing it down. Document the safe-degradation target state for every autonomy-bearing system as part of its launch approval.

**Domain 7 checklist:** implement all five layers for any system above Autonomy Level 2 (Domain 9); define and test a documented safe-degradation target state per workload; calibrate dynamic throttling thresholds using historical confidence-score distributions, not arbitrary defaults; verify hard kill-switches are non-AI and independently testable; run quarterly tabletop tests of the circuit-breaker path end-to-end.

## Domain 8: AI Assurance, Auditability & Immutable Ledger

Compliance validation requires logging all agentic actions to an Immutable AI Audit Ledger, providing downstream compliance investigators an unalterable forensic path to verify systemic alignment. Immutability is a property of the storage and write architecture, not a database claim. Three patterns exist in increasing order of assurance and cost: write-once-read-many (WORM) storage with retention locks (moderate tamper-evidence, low cost, standard enterprise logging); append-only ledgers with cryptographic hash-chaining between records, so retroactive edits verifiably break the chain (high tamper-evidence, medium cost, regulated industries and agent action logs); and external anchoring, where periodic hash roots publish to an independently-controlled system (very high tamper-evidence, high cost, national-strategic or highest-assurance systems). Most enterprise programs only need the hash-chained pattern.

Capturing full chain-of-thought and tool payload for every action is necessary but not sufficient — without indexing by constitutional principle ID, autonomy level, and risk score, the ledger becomes searchable only by timestamp: adequate for forensic reconstruction after an incident, useless for proactive monitoring. Pair the ledger with structured indices on the fields the RAI Office actually queries. Retention periods should be set by the longest applicable regulatory requirement among the Domain 3 jurisdictions, not storage-cost convenience, and access to the raw ledger should itself be logged and restricted to the RAI Office and named auditors — the audit trail of who accessed the audit trail is frequently requested in regulatory examinations and often the first thing overlooked.

**Domain 8 checklist:** select an immutability pattern matched to assurance requirements; index ledger records by constitutional principle ID, agent ID, autonomy level, and verification outcome; set retention periods from the longest applicable jurisdictional requirement; log and restrict access to the ledger itself; test ledger integrity verification on a recurring schedule.

## Related

- [Sovereign Constitutional AI & RAI Handbook: Foundations & Behavioral Engineering (Part 1)](../04-sovereign-constitutional-ai-rai-implementation-handbook.md)
- [Sovereign Constitutional AI & RAI Handbook: Autonomy, Policy & Public Interest (Part 3)](04-sovereign-constitutional-ai-rai-implementation-handbook-part3.md) — Domains 9-12
- [Identity/MCP/A2A Security Blueprint](../identity-mcp-a2a-security-blueprint.md)
