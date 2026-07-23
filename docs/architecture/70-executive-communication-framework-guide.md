---
title: "COMMUNICATION FRAMEWORKS MASTER GUIDE"
doc_type: guide
domain: architecture
topic_id: executive-communication-framework-guide
date_created: 2026-07-23
status: current
last_reviewed: 2026-07-23
covers_version: "N/A"
supersedes:
  - docs/enterprise-architecture/framework/Executive_Communication_Framework_Guide.md
---

# COMMUNICATION FRAMEWORKS MASTER GUIDE

For Enterprise Architects · Principal Architects · CTO Candidates. From Technical Fluency to Board-Level Strategic Communication.

## The Communication Pyramid

Every communication framework rests on one foundational insight: the audience determines the structure, the register, the length, and the level of abstraction. Architects who communicate the same way to a board member and a software engineer will fail with both.

**Board / Investors.** Strategic direction. Why this matters to the enterprise. Maximum 3 minutes / 1 page.

**C-Suite (CEO, CFO).** Decision support. What to decide and the risk of each option. 5 minutes / 2 pages.

**VP / Director.** Alignment. What we're doing and what they need to do. 10 minutes / 4 pages.

**Engineering Leaders.** Coordination. How we're doing it and the constraints. 30 minutes / detailed.

**Regulators / Audit.** Assurance. Evidence of control and compliance. As required / documented.

The cardinal rule: Never communicate at the level of your thinking. Communicate at the level of your audience's decision. Your job is not to show how hard the problem is — it is to make the decision or action obvious.

## Pyramid Principle / Minto Pyramid

Origin: Barbara Minto, McKinsey & Company, 1970s. Use when: Any written or verbal communication where the audience needs a clear recommendation, especially executives who read horizontally before vertically.

**The Structure:**

Governing Thought — The single most important thing you want the audience to take away. One sentence.

Key Lines — The three to five arguments or reasons that support the governing thought. Each must be mutually exclusive and collectively exhaustive (MECE). They answer 'Why?' or 'How?' relative to the governing thought.

Supporting Detail — The evidence, data, and analysis that support each key line. This exists to justify the key lines, not to be read in full by executives.

**Worked Example:**

Governing Thought: We must modernise our core banking platform in 24 months or risk regulatory action and a 40% increase in the cost of product delivery.

Key Line 1: The current platform is materially non-compliant with three incoming regulatory requirements.

Key Line 2: Our delivery cost per feature has grown 38% in two years due to technical debt on the current platform.

Key Line 3: Competitor platforms built on modern architecture are delivering equivalent features in one-third of our time-to-market.

Supporting Detail: [Regulatory citations, cost analysis, competitive benchmarks — available in appendix]

## Bottom Line Up Front (BLUF)

Origin: US Military. Use when: Any situation where you have 60 seconds or less — verbal briefings, email subject lines, Slack messages to executives, and opening statements.

**The Structure:**

Bottom Line — State the conclusion, decision, or action required — in the very first sentence. No preamble.

Level — Pitch the detail at the correct level for the audience. Add only enough context to make the bottom line credible.

Urgency — State the timeline or decision deadline explicitly.

Follow-up — State the specific action you need from the recipient.

**Example Transformation:**

Weak: "Hi Sarah, I wanted to follow up on our discussion last week about the cloud migration programme..."

Strong: "Sarah — we need a go/no-go decision on cloud provider by Friday 5pm. AWS is our recommended option based on cost, compliance posture, and migration risk. Delay beyond Friday pushes our Q2 launch by six weeks. Can you confirm approval or schedule 20 minutes to discuss blockers?"

## Situation · Background · Assessment · Recommendation (SBAR)

Origin: US Navy / Healthcare. Use when: High-stakes briefings, incident communication, regulatory updates, and any situation where the audience needs to take action quickly.

**The Structure:**

Situation — What is happening right now? One to two sentences. State the current state clearly and factually.

Background — What context does the audience need to understand the situation? Only what is relevant.

Assessment — What is your professional judgement? What does it mean? What is the severity? What are the options?

Recommendation — What specific action do you recommend? By whom? By when? What is the consequence of inaction?

## Situation · Complication · Resolution (SCR)

Origin: Narrative storytelling tradition. Use when: Strategic presentations, investment cases, transformation narratives, and any communication that needs to generate urgency before the recommendation.

**The Structure:**

Situation — Establish the stable world that the audience recognises. Common ground.

Complication — Introduce the disruption: the change, threat, gap, or risk that means the current situation cannot continue. This is where you create urgency.

Resolution — Present your recommendation as the answer to the complication. The resolution should feel inevitable given the complication.

**Why SCR works neurologically:** The human brain is a narrative processing machine. When you structure a business communication as SCR, you work with the brain's natural processing rather than against it. The complication creates a cognitive gap that the brain is compelled to close.

## Point · Reason · Example · Point (PREP)

Origin: Debate and advocacy training. Use when: Verbal communication under pressure — Q&A sessions, board challenges, panel discussions, and any situation requiring a structured oral response in 60–90 seconds.

**The Structure:**

Point — State your position in one clear sentence. No preamble.

Reason — Give the single strongest reason your position is correct. Not three reasons — one. The best one.

Example — Ground the reason in a specific, concrete example or data point.

Point — Restate your position — now reinforced by the reason and example.

**PREP Discipline Rules:** Time: 60–90 seconds maximum. Reason: choose one — the strongest. Example: must be specific. Second Point: do not introduce new information — close, don't continue.

## Situation · Behaviour · Impact (SBI)

Origin: Center for Creative Leadership. Use when: Delivering feedback to peers, senior engineers, and leaders — especially in situations where the behaviour has had a visible negative impact.

**The Structure:**

Situation — Anchor the feedback to a specific, observable situation. When and where?

Behaviour — Describe only the observable behaviour — what you saw or heard. Not your interpretation. Not their intention.

Impact — Describe the impact of that behaviour — on the team, the decision, the outcome.

**Why SBI Works:** SBI works because it is irrefutable at the Situation and Behaviour levels — you are reporting observation, not interpretation. The recipient cannot argue with what happened. They can only engage with the Impact, which opens the conversation.

## The Burning Platform Framework

Origin: Daryl Conner. Use when: Creating urgency for transformation and change — when the status quo is genuinely dangerous but the organisation has not yet recognised it.

**The Three Elements:**

The Platform is Burning — Make the cost of inaction visible, specific, and time-bound. "We risk regulatory action by Q3 if we do not act" is a burning platform. "We have technical debt" is not.

The Jump is Survivable — Define the transformation as achievable, not just necessary. If the audience believes the jump will kill them, they stay on the platform.

Staying is Not an Option — Remove the third alternative — doing nothing. Present the cost of inaction at least as prominently as the cost of change.

Ethical Guardrails: Use this only when the urgency is genuine. If you have to exaggerate the threat to create urgency, the problem is not the communication; it is the strategy.

## Risk-Adjusted Narrative

Origin: Executive communication practice. Use when: Any situation where you must communicate genuinely uncertain outcomes to an audience that desires certainty.

**The Structure:**

Anchor — State your current best estimate clearly and directly.

Range — Provide a confidence-weighted range — not a single point estimate.

Assumptions — State the two or three key assumptions the estimate rests on.

Uncertainty Type — Distinguish aleatory uncertainty (irreducible variability) from epistemic uncertainty (knowable with more analysis).

Decision Gate — Propose a specific checkpoint where the uncertainty will be materially reduced.

**Why This Works:** Executives who communicate false precision get short-term approval and long-term credibility damage. Accurate uncertainty is more credible than precisely wrong.

## The Three-Lens Communication Model

Origin: Executive communication practice. Use when: Framing any technology initiative for an executive or board audience.

**The Three Lenses:**

Business Lens — Why does this matter to the business? What customer, revenue, market, or competitive outcome does this enable or protect?

Risk Lens — What risk does this address or create? Regulatory, security, operational, reputational?

Investment Lens — What does this cost? What is the return and over what period?

Most architects communicate only through the Business Lens. Executives who approve investment are equally concerned with the Risk and Investment lenses. A communication that does not address all three leaves questions unanswered.

## Communication Anti-Patterns

**AP1 The Architecture Lecture.** Problem: Explaining the technical architecture in detail to an audience that needs the business outcome. Fix: Reframe: 'What does this enable the business to do that it cannot do today?'

**AP2 The Certainty Performance.** Problem: Projecting false confidence about uncertain outcomes. Fix: Use the Risk-Adjusted Narrative.

**AP3 The Endless Context.** Problem: Spending 80% of the communication on background before reaching the recommendation. Fix: Use BLUF or Pyramid Principle.

**AP4 The Passive Hedge.** Problem: Using passive voice to avoid accountability. Fix: Use active voice: 'I recommend...' 'We will...'

**AP5 The Jargon Shield.** Problem: Using technical vocabulary to signal expertise rather than as a communication tool. Fix: For every technical term, ask: 'What is the plain English equivalent?'

**AP6 The Disagreement Avoidance.** Problem: Softening a recommendation to avoid conflict. Fix: State your recommendation clearly. Then acknowledge the strongest counterargument. Then explain why your recommendation is still correct.

**AP7 The No-Ask Close.** Problem: Ending a presentation without a clear call to action. Fix: Every communication must end with: a specific action, a named owner, and a deadline.

## Master Checklist

Before every significant communication, run through this checklist:

**Audience.** Have I calibrated the register, abstraction level, and length to this specific audience?

**Framework.** Have I selected the right framework for this communication type?

**BLUF.** Does my opening sentence contain the recommendation or decision needed?

**3 Lenses.** Have I addressed the Business, Risk, and Investment dimensions?

**Objections.** Have I pre-empted the three most likely objections in the content?

**Uncertainty.** Have I communicated uncertainty accurately rather than performing false precision?

**Ask.** Does my communication end with a specific action, owner, and deadline?

**Register.** Is there any jargon, passive voice, or technical vocabulary that would require translation?
