---
title: "Sovereign Constitutional AI & RAI Handbook: Autonomy, Policy & Public Interest (Part 3)"
doc_type: guide
domain: trust
status: current
topic_id: sovereign-constitutional-ai-rai-implementation-handbook-part3
last_reviewed: 2026-07-28
maturity: practitioner
supersedes: []
tags: [ai-governance, autonomy, policy-as-code, democratic-ai, opa]
covers_version: "2026"
---

Domains 9-12 of the Sovereign Constitutional AI & RAI Handbook: Agent Governance & Autonomy Framework, Policy-as-Code for Real-Time Runtime Enforcement, Democratic AI & Public Interest Architecture, and Future Horizon Vector Mapping (2026-2030).

## Domain 9: Agent Governance & Autonomy Framework

Six discrete levels of operational AI autonomy map system actions directly to risk boundaries. **Level 0, Advisory**: the system generates text with zero execution capacity, human-only execution. **Level 1, Assisted**: the system creates drafts requiring human authentication before API routing. **Level 2, Conditional Autonomy**: the system executes low-risk tasks with real-time human intervention capability. **Level 3, High Autonomy**: the system executes long-horizon tasks, pausing only at designated high-impact checkpoints. **Level 4, Bounded Autonomy**: the system operates fully within strict, hardcoded sandbox parameters without human review. **Level 5, Mission Sovereign**: the system governs its own infrastructure allocation, task planning, and recovery routines within a sovereign perimeter.

Autonomy level should never be static — it's a promotion ladder, and promotion to each level requires evidence, not optimism. L0→L1 requires draft quality above a defined accuracy threshold over a 30-day sample, approved by the Engineering Lead. L1→L2 requires a human-in-loop override rate below 5% on the low-risk task class, approved by Engineering Lead plus RAI Office. L2→L3 requires zero unresolved high-severity incidents in the trailing 90 days with the full Domain 7 safety stack live, approved by the CAIO. L3→L4 requires the Verification Hook independently audited and the sandbox boundary penetration-tested, approved by CAIO plus CRO. L4→L5 requires board-level risk sign-off and full sovereignty tier 4 infrastructure, approved by the Board of Directors.

Promotion criteria are incomplete without automatic demotion triggers — conditions dropping a system back a level without waiting for the next governance review, implemented as a runtime rule rather than a process reminder: Verification Hook override/failure rate exceeding 2% over a rolling 7-day window; any single Sev-1 incident involving the system; a constitutional principle violated and not caught until post-hoc audit; or the underlying model/vendor changing without re-certification. A Level 3 procurement agent approving purchase orders that, while individually within policy, collectively exceed a department's quarterly budget — a pattern the per-transaction Verification Hook wasn't designed to catch — gets automatically demoted to Level 2 on detection, restoring real-time human intervention, while the hook is updated with a rolling budget-aggregate check before promotion is reconsidered.

**Domain 9 checklist:** document evidence gates for every promotion between autonomy levels; implement automatic, runtime-enforced demotion triggers, not manual review-dependent ones; maintain a registry mapping every agent/system to its current certified autonomy level; re-certify autonomy level whenever the underlying model, vendor, or tool surface changes.

## Domain 10: Policy-as-Code for Real-Time Runtime Enforcement

Constitutional principles must compile into executable policies that intercept system behaviors before they execute. A base Rego (Open Policy Agent) policy governs whether a request is allowed at all — denying by default, allowing only when no critical infraction is flagged (prompt injection detected, protected PII present), the calculated risk score stays under 0.7, and the compute-residency context matches the sovereign zone. A second policy layer governs which specific tools and parameter ranges an already-allowed request may invoke, directly enforcing Domain 9's autonomy-level boundaries: tool calls are scoped so, for example, `send_email` requires autonomy level 1, `modify_database_record` requires level 3, and `execute_financial_transfer` requires level 4 with a $50,000 parameter cap.

Policy evaluation must sit synchronously in the critical path of every tool call, not as an asynchronous audit step: the agent proposes a tool call, OPA/Rego policy evaluation runs synchronously (target under 20ms), a denial returns a structured rejection to the planner for replanning, an allowance executes against the environment, and the decision plus rationale logs to the Immutable Audit Ledger asynchronously and non-blocking. Rego policies should carry their own test suite, exercised in CI on every change, asserting both that known-bad inputs are denied and known-good inputs aren't over-blocked — a policy change not paired with a test case is treated the same as an unreviewed code change.

**Domain 10 checklist:** implement request-level allow/deny policy covering jurisdiction, risk score, and infraction detection; implement tool-scoping policy tied to certified autonomy level; place policy evaluation synchronously in the critical path with a defined latency budget; route every policy decision, allow and deny, to the audit ledger asynchronously; maintain a CI-enforced unit test suite for all policy code.

## Domain 11: Democratic AI & Public Interest Architecture

This framework balances central sovereignty with citizen-driven oversight, using distributed consensus to steer core alignment variables for public-utility platforms — health, law, education. Not every enterprise system warrants citizen-panel-level oversight; it's most relevant for systems materially affecting public access to essential services (healthcare triage, benefits eligibility, public education tools, civic information systems) where the affected population has no commercial alternative and limited individual leverage. Internal enterprise tools don't require this architecture, though the transparency principle — a public ledger — often transfers usefully as a lighter-weight internal practice.

Structuring a citizen alignment panel requires deliberate design: composition should be a demographically representative sample, not self-selected volunteers, to avoid participation bias; scope of input should be bounded to value tradeoffs (precision vs. recall in a triage system), not raw technical parameters; cadence should be recurring, tied to material system changes, not a one-time consultation; and the feedback loop needs a published response showing how panel input did or didn't change the system, to preserve legitimacy. A municipal benefits-eligibility assistant publishing a simplified, non-technical summary of its decision criteria and aggregate approval/denial statistics monthly, while withholding implementation details that could enable gaming, illustrates the central design tension: calibrated transparency — enough for public accountability, not so much it creates exploitable specification gaming.

## Domain 12: Future Horizon Vector Mapping (2026-2030)

This is directional capability planning, not a procurement commitment, re-assessed annually alongside the Domain 1 and Domain 5 recurring reviews. By **2026**, a "Constitutional OS" horizon moves policy enforcement below the application layer into firmware/kernel hooks, reducing bypass risk from application-level exploits — prepare now by evaluating hardware vendors with firmware-level policy hook roadmaps and avoiding lock-in to pure software-layer enforcement. By **2028**, "cross-border nests" turn static jurisdictional compliance maps (Domain 3) into dynamic, real-time brokered compliance as systems move across borders — prepare by investing in machine-readable compliance representations now, not just legal documents, so future brokering systems can consume them. By **2030**, "machine-to-machine autonomy" has agents transacting and governing interactions with other organizations' agents directly, via autonomous micro-tariffs and model-to-model governance, requiring inter-organizational trust protocols — prepare by tracking emerging M2M identity and trust standards and piloting constrained M2M interactions in low-stakes domains first.

## Related

- [Sovereign Constitutional AI & RAI Handbook: Control, Governance & Risk (Part 2)](04-sovereign-constitutional-ai-rai-implementation-handbook-part2.md)
- [Sovereign Constitutional AI & RAI Handbook: Lifecycle, Assurance & Operating Disciplines (Part 4)](04-sovereign-constitutional-ai-rai-implementation-handbook-part4.md) — Domains 13-18
- [Identity/MCP/A2A Security Blueprint: MCP Security](../parts/identity-mcp-a2a-security-blueprint-part2.md)
