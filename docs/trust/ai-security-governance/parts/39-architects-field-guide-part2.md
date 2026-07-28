---
title: "Architect's Field Guide: MCP/A2A Under Pressure & Governance Crunch (Part 2)"
doc_type: case-study
domain: trust
status: current
topic_id: architects-field-guide-part2
last_reviewed: 2026-07-27
maturity: practitioner
supersedes: []
tags: [ai-security, case-study, mcp, a2a, governance]
covers_version: "as of 2026"
---

Meridian Trust Bank, weeks 4-12: consolidating unmanaged MCP servers, launching A2A under a vendor deadline, and closing an EU AI Act gap analysis with five weeks left on the clock.

**Fictionalization note:** Meridian Trust Bank and this engagement are fictional, composited from realistic patterns. Every technical mechanism and tradeoff described is grounded in the same 2026 material underlying the rest of this program.

## Chapter 3: MCP and A2A Under Deadline Pressure

*Weeks 4-9, overlapping the identity rebuild.*

By week four, commercial lending's A2A integration with their loan-origination SaaS vendor is two weeks from its committed launch, and the lending VP has escalated to the CTO twice about the security review being a blocker. This is the predictable consequence of the Chapter 1 sequencing decision: the team that needed to wait, waited, and is unhappy about it. Part of this chapter is technical; an equal part is managing a stakeholder with a legitimate deadline and a less legitimate but very real frustration that security wasn't involved when this project started.

**First, the MCP gateway consolidation.** Before any A2A work, the four unmanaged MCP servers from Chapter 1 needed to come under the gateway or be shut down — two had direct relevance to the lending agent's eventual tool access, and leaving them unmanaged while standing up A2A trust infrastructure would mean building a sophisticated control on a foundation already known to be weak. The internal document-search server (Marketing) migrated cleanly, low risk, in active use, no schema issues. A "quick prototype" pricing-calculator server (Lending, built by a contractor) was decommissioned and rebuilt under the gateway from scratch — a discovery-time scan found its tool descriptions referenced an undocumented internal pricing API with no rate limiting; rebuilding was faster and safer than retrofitting. A legacy HR-policy lookup server migrated easily, with clean tool definitions and already-narrow scope. A vendor-provided MCP server for a third-party document OCR tool migrated with additional vendor-specific controls; its third-party origin triggered the heightened checklist, and the vendor initially would not provide a signed tool manifest, which became a real negotiating point with their account team.

**The Architect's Reasoning.** The pricing-calculator finding is worth dwelling on: a near-perfect real-world instance of tool poisoning risk (ASI02/ASI04) discovered through routine process, not an exotic red-team exercise. Nobody attacked this server. A contractor, working fast, built a functionally accurate but operationally dangerous tool description — it called an internal pricing API with no rate limiting, because it was never designed to be invoked hundreds of times in a loop. The discovery-time scan flagged the missing rate-limit behavior not because it detected malice, but because it detected a pattern its scanning rules are tuned to flag regardless of intent. This is the practical argument for gateway scanning that a purely incident-response framing misses: most of what it catches in year one isn't attackers, it's exactly this kind of well-intentioned gap.

**Now, the A2A integration.** The lending agent exchanges loan documents and status updates with the vendor's agent over A2A. The vendor's integration documentation described a fairly typical 2025-era deployment: Agent Cards, but not yet consistently signed across all endpoints, and no explicit per-task spend or rate cap beyond a generic API rate limit.

**Decision Point: do you launch on the original two-week timeline?** The vendor's production endpoint is signed; their sandbox/staging endpoint, which lending had been testing against, is not, and the vendor's account team says full signing rollout is "on the roadmap, no committed date." Three options: launch against the production endpoint only, treating staging as informational (meets the deadline by avoiding the gap entirely in production, but requires discipline to ensure production traffic never silently falls back to an unsigned endpoint); delay launch until the vendor signs all endpoints (cleanest posture, but gives away leverage and a firm timeline to a vendor already showing no urgency, at real business cost to lending); or **launch on schedule with a Meridian-side compensating control** — reject any Agent Card without a valid signature regardless of claimed environment, with hard-coded production-endpoint pinning (meets the deadline and closes the gap on Meridian's side regardless of vendor follow-through, at the cost of gateway configuration complexity). The third was chosen.

**Rationale:** this reflects a pattern that recurs constantly in vendor relationships — you frequently cannot force a counterparty's security posture onto their timeline, but you can almost always control what your own gateway accepts. Production-endpoint pinning plus unconditional signature enforcement let the launch proceed on schedule, made the staging gap operationally irrelevant, and — critically — the compensating control was documented as a tracked exception with a follow-up date, not a quiet workaround everyone forgets about in three months.

**Exhibit — A2A gateway policy excerpt (lending agent outbound rule):**

```yaml
rule: lending-agent-outbound-a2a
  applies_to: agent:lending/document-exchange
  allow_endpoints:
    - https://api.loanvendor.example/a2a/v1   # production, signed only
  require:
    - agent_card.signature.valid == true
    - agent_card.signature.domain == "loanvendor.example"
    - tls_version >= 1.3
  deny_endpoints:
    - https://staging-api.loanvendor.example/a2a/v1  # explicit deny, not just omission
  per_task_spend_cap_usd: 0   # this integration exchanges documents, never payments
  audit: full_payload_capture
```

Notice the explicit deny rule for the staging endpoint, rather than simply omitting it from the allowlist — intentional defense in depth. If a future configuration change accidentally adds a broader allow pattern that would match the staging URL, the explicit deny still blocks it, whereas a simple omission relies on every future change correctly preserving the absence.

**Trust broker — starting score for a new external counterparty.** The lending vendor's agent is Meridian's first production external A2A counterparty, so the trust-broker design had no existing population to calibrate against. The team set an initial score deliberately conservative — enough to permit the document-exchange use case the launch required, not enough to permit anything beyond it — with an explicit 90-day review. Identity assurance scored moderate (signed cards on production only, SOC 2 Type II reviewed); behavioral conformance scored neutral, not credited (no history yet — a new counterparty); content provenance scored moderate-low, flagged as the weakest signal (all exchanged documents vendor-asserted, no independent verification); operator standing scored moderate-high (an established player with existing banking-sector clients and a named security contact). The resulting composite score permitted document exchange but was explicitly configured to deny any future request to expand scope toward direct system-to-system financial data exchange without a fresh, manual trust review — a future engineer cannot accidentally widen this relationship's blast radius by changing a config flag.

**Field Note.** A brand-new external counterparty should never inherit a "fresh start" high trust score just because nothing bad has happened yet — neutral behavioral conformance is not the same as good behavioral conformance, and conflating the two is how trust-score systems get gamed over time. Score what you can actually verify today, and make the score's ceiling, not just its floor, an explicit design choice.

## Chapter 4: The Governance and Compliance Crunch

*Weeks 7-12.*

Legal's original eight-week estimate to confirm EU AI Act exposure slips, as these things do, and by the time a definitive answer arrives — yes, two specific services (an AI-assisted credit-decisioning support tool and a portion of the customer support agent's workflow touching account-status determinations) plausibly fall under Annex III high-risk classification — only five weeks remain before the Act's high-risk obligations become enforceable.

**Building the crosswalk under time pressure.** This is where having already done the identity and MCP/A2A foundational work in Chapters 2 and 3 pays off directly: a meaningful fraction of what the Act requires is evidence that controls exist and operate, and those controls now actually exist rather than needing to be invented under deadline pressure. By week seven, risk management (Art. 9) was substantially in place, backed by MAESTRO threat models and the newly-chartered Governance Board charter. Data governance (Art. 10) was partially in place — the customer support agent's memory governance lifecycle existed, but the credit-decisioning tool's data lineage required new work, the single biggest gap found. Technical documentation (Art. 11, Annex IV) was largely new work — compiling architecture diagrams, Agent Registry entries, and threat models into the Act's specific format, administrative but genuinely time-consuming. Human oversight (Art. 14) was in place, since Chapter 2's autonomy-level assignments directly satisfied it once mapped to the Act's language. Accuracy, robustness, and cybersecurity (Art. 15) were substantially in place, supported by the identity substrate, MCP/A2A gateway controls, and the not-yet-executed red-team plan. Conformity assessment and registration was pure new work, not a control gap but a process gap — no internal control mapped onto it; it required engaging Legal and an external conformity assessment body on a timeline the technical team couldn't accelerate.

**The Architect's Reasoning.** Five of six rows showed real progress by week seven specifically because Chapters 2 and 3 weren't governance work in disguise — they were genuinely necessary architecture work that happened to also produce most of the evidence a regulator would want. This is the actual payoff of identity-first sequencing made concrete: not just a security argument, a compliance-velocity argument. The one row that didn't benefit — conformity assessment — is revealing differently: pure process and legal work that no amount of good architecture accelerates. Recognizing early which obligations are technical-evidence problems versus pure administrative/legal problems is itself a skill, because it tells you where to spend engineering time under deadline versus where to just escalate to Legal and wait.

**Standing up the AI Governance Board — late, but not too late.** The board gets formally chartered in week five, deliberately timed to exist before the crosswalk work needed an accountable approval body, rather than as a reactive afterthought once the deadline was already missed. You chair it (an explicit, documented interim arrangement, not a permanent dual-hat) until a dedicated AI CISO is hired. Legal & Compliance is the Deputy General Counsel, who brought the EU AI Act findings to the first meeting. Enterprise Architecture is the existing Chief Architect, providing continuity with the bank's TOGAF practice. Model Risk Management is the Head of MRM — a critical seat, since MRM's existing SR 11-7 governance experience translated more directly to agentic governance than anyone expected going in. Business representation rotates; the Lending VP from Chapter 3 was the first rotating seat-holder, which incidentally repaired some of the relationship friction from the A2A delay.

**Field Note.** Putting the previously frustrated Lending VP on the board as its first rotating business seat wasn't originally planned — it emerged as a relationship-repair move once the A2A launch succeeded. It turned out to be one of the better decisions of the engagement: a stakeholder who's been through the review process from the inside becomes one of the most credible internal advocates for it with peer business units, in a way no architecture documentation can replicate.

**Autonomy classification for the whole fleet.** With the board chartered, the full population — 47 agents, now 49, two more found during the MCP consolidation work — gets formally classified against the five-level autonomy scale, the first time every agent in the bank has a documented, board-visible level. L0 Advisory only: 9 agents (research summarizers, meeting-notes tools). L1 Supervised execution: 14 (marketing-content drafting, post-incident scope-tightened, plus the credit-decisioning support tool). L2 Bounded autonomy: 19 (customer support ticket triage and reply drafting, HR policy Q&A). L3 Delegated autonomy: 6 (the document-exchange lending agent, internal IT-helpdesk automation). L4 Full autonomy: 1 — a low-stakes internal meeting-room booking agent, deliberately the only L4 agent in the bank at this stage. The board's first real policy decision was that L4 would be granted sparingly, only to genuinely low-consequence use cases, until the AI SOC (Chapter 5) had a full operating quarter of track record — a conservative posture explicitly revisited at the 90-day mark rather than left as an unstated default forever.

## Related

- [Architect's Field Guide: Inherited Mess & Identity Rebuild (Part 1)](../39-architects-field-guide.md)
- [Architect's Field Guide: Operations & the Incident (Part 3)](39-architects-field-guide-part3.md)
- [Identity/MCP/A2A Security Blueprint: MCP Security](../parts/34-identity-mcp-a2a-security-blueprint-part2.md)
