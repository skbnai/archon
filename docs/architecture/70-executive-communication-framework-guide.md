---
title: "COMMUNICATION FRAMEWORKS MASTER GUIDE"
doc_type: reference-architecture
domain: architecture
topic_id: executive-communication-framework-guide
date_created: 2026-07-10
status: current
last_reviewed: 2026-07-23
covers_version: "N/A"
supersedes:
  - docs/enterprise-architecture/framework/Executive_Communication_Framework_Guide.md
---

# COMMUNICATION FRAMEWORKS MASTER GUIDE

**EXECUTIVE · ARCHITECTURE · LEADERSHIP SERIES**

For Enterprise Architects · Principal Architects · CTO Candidates  
From Technical Fluency to Board-Level Strategic Communication

## Key Frameworks Covered

- Minto Pyramid
- Pyramid Principle
- SBI Feedback
- BLUF (Bottom Line Up Front)
- STAR
- SBAR
- SCR
- 5 Whys
- PREP
- The Burning Platform
- Risk-Adjusted Narrative

## Audience Levels Covered

Board · C-Suite · Executive Committee · Engineering · Operations · Regulators

---

## TABLE OF CONTENTS

- **SECTION 01** — The Communication Pyramid: Why your audience determines everything
- **SECTION 02** — Pyramid Principle / Minto: Lead with the answer — structure downward
- **SECTION 03** — BLUF — Bottom Line Up Front: Military precision for executive communication
- **SECTION 04** — SBAR — Situation · Background · Assessment · Recommendation: Clinical clarity for high-stakes briefings
- **SECTION 05** — SCR — Situation · Complication · Resolution: Narrative arc for strategic communication
- **SECTION 06** — PREP — Point · Reason · Example · Point: Structured verbal communication under pressure
- **SECTION 07** — SBI — Situation · Behaviour · Impact: Precision feedback for senior leaders
- **SECTION 08** — The Burning Platform: Creating urgency without manufacturing crisis
- **SECTION 09** — Risk-Adjusted Narrative: Communicating uncertainty with credibility
- **SECTION 10** — The Stakeholder Register Framework: Tailoring every message to its audience
- **SECTION 11** — The 3-Lens Model: Business · Risk · Investment framing
- **SECTION 12** — Objection Pre-emption Framework: Answering questions before they are asked
- **SECTION 13** — Difficult Conversation Framework: Navigating conflict and delivering hard news
- **SECTION 14** — Written Communication Standards: Executive memos, board papers, decision notes
- **SECTION 15** — Communication Anti-Patterns: What kills credibility — and how to fix it

---

## Overview

This guide covers every communication framework an Enterprise Architect or CTO-level leader needs to master. Each framework includes its structure, when to use it, worked examples at executive level, common mistakes, and a contrast between strong and weak application.

## Framework Selection Guide

```mermaid
flowchart TD
    A["What is your communication need?"] --> B{"What is the<br/>context?"}
    
    B -->|Written & needs<br/>clear recommendation| C["Pyramid Principle<br/>(Sections 02)"]
    B -->|Urgent verbal<br/>60 seconds| D["BLUF<br/>(Section 03)"]
    B -->|High-stakes<br/>briefing needed| E["SBAR<br/>(Section 04)"]
    B -->|Strategic story<br/>generating urgency| F["SCR<br/>(Section 05)"]
    B -->|Board challenge<br/>Q&A response| G["PREP<br/>(Section 06)"]
    B -->|Feedback to<br/>senior leader| H["SBI<br/>(Section 07)"]
    B -->|Need to create<br/>transformation urgency| I["Burning Platform<br/>(Section 08)"]
    B -->|Must communicate<br/>uncertain outcomes| J["Risk-Adjusted<br/>Narrative<br/>(Section 09)"]
    B -->|Hard conversation<br/>conflict/feedback| K["Difficult Conversation<br/>Framework<br/>(Section 13)"]
    B -->|Formal written<br/>memo/ADR| L["Written Communication<br/>Standards<br/>(Section 14)"]
    
    C --> M["Apply 3-Lens Model<br/>Business/Risk/Investment"]
    D --> M
    E --> M
    F --> M
    G --> M
    H --> M
    I --> M
    J --> M
    K --> M
    L --> M
    
    M --> N["Pre-empt objections<br/>(Section 12)"]
    N --> O["Review Master<br/>Checklist"]
    O --> P["Avoid Anti-Patterns<br/>(Section 15)"]
    
    style C fill:#e3f2fd
    style D fill:#e3f2fd
    style E fill:#f3e5f5
    style F fill:#e8f5e9
    style G fill:#fff3e0
    style H fill:#fce4ec
    style I fill:#ffebee
    style J fill:#f1f8e9
    style K fill:#e0f2f1
    style L fill:#ede7f6
    style M fill:#fff9c4
    style N fill:#fff9c4
    style O fill:#fff9c4
    style P fill:#ffe0b2
```

**Diagram 1: Framework Selection Guide** — Use this flowchart to quickly identify which framework matches your communication need. All frameworks integrate with the 3-Lens Model (Business/Risk/Investment) and benefit from objection pre-emption and anti-pattern avoidance.

---

## SECTION 01: THE COMMUNICATION PYRAMID

### Foundational Principle

Every communication framework rests on one foundational insight: the audience determines the structure, the register, the length, and the level of abstraction. Architects who communicate the same way to a board member and a software engineer will fail with both. Mastering communication means developing fluency across the full spectrum — and switching registers instantly and invisibly.

### The Five Registers

| **Audience** | **Level** | **What They Need** | **Max Length** | **Abstraction** |
|---|---|---|---|---|
| **Board / Investors** | Strategic | Why this matters to the enterprise | Maximum 3 minutes / 1 page | High (outcome-focused) |
| **C-Suite (CEO, CFO)** | Executive | What to decide and the risk of each option | High: 5 minutes / 2 pages | Medium-High (business impact) |
| **VP / Director** | Tactical | What we're doing and what they need to do | Medium: 10 minutes / 4 pages | Medium (action-oriented) |
| **Engineering Leaders** | Operational | How we're doing it and the constraints | Low: 30 minutes / detailed | Low (technical detail) |
| **Regulators / Audit** | Formal | Evidence of control and compliance | As required / documented | Formal (compliance-focused) |

### The Cardinal Rule

**Never communicate at the level of your thinking. Communicate at the level of your audience's decision.** Your job is not to show how hard the problem is — it is to make the decision or action obvious.

### Register Match (Strong)

- Opens with the outcome or decision needed
- Uses the audience's vocabulary, not yours
- Length calibrated to the audience's time
- Complexity hidden, clarity front-loaded

### Register Mismatch (Weak)

- Opens with context, history, or technical detail
- Uses architecture or engineering vocabulary with executives
- Overlong for the audience's patience
- Makes the audience work to find the point

---

## SECTION 02: PYRAMID PRINCIPLE / MINTO PYRAMID

**Origin:** Barbara Minto, McKinsey & Company, 1970s

**Use when:** Any written or verbal communication where the audience needs a clear recommendation, especially executives who read horizontally before vertically.

### The Structure

| **Element** | **Definition** |
|---|---|
| **Governing Thought** | The single most important thing you want the audience to take away. One sentence. Answerable in one sentence. This goes first, always. |
| **Key Lines** | The three to five arguments or reasons that support the governing thought. Each must be mutually exclusive and collectively exhaustive (MECE). They answer 'Why?' or 'How?' relative to the governing thought. |
| **Supporting Detail** | The evidence, data, and analysis that support each key line. This is the bottom of the pyramid — it exists to justify the key lines, not to be read in full by executives. |

### Worked Example: Architecture Modernisation Case

**Pyramid Applied:**

- **GOVERNING THOUGHT:** We must modernise our core banking platform in 24 months or risk regulatory action and a 40% increase in the cost of product delivery.

- **KEY LINE 1:** The current platform is materially non-compliant with three incoming regulatory requirements.

- **KEY LINE 2:** Our delivery cost per feature has grown 38% in two years due to technical debt on the current platform.

- **KEY LINE 3:** Competitor platforms built on modern architecture are delivering equivalent features in one-third of our time-to-market.

- **SUPPORTING DETAIL:** [Regulatory citations, cost analysis, competitive benchmarks — available in appendix]

### The SCQA Variant: Situation · Complication · Question · Answer

For strategic communications that require a narrative setup before the recommendation, use SCQA as the entry point into the pyramid.

| **Element** | **Definition** |
|---|---|
| **S — Situation** | Establish common ground — what both you and the audience already know to be true. |
| **C — Complication** | Introduce the change, threat, or problem that disrupts the situation. |
| **Q — Question** | Surface the question the complication naturally raises in the audience's mind. |
| **A — Answer** | Deliver your governing thought as the direct answer to that question. |

### Strong Application

- Recommendation in the first sentence
- Key lines are genuinely MECE
- Detail in appendix — not in the main narrative
- Board reads the governing thought and key lines only

### Weak Application

- Builds to the recommendation over multiple pages
- Key lines overlap or leave gaps
- Evidence embedded in the narrative — buries the point
- Audience must read everything to find the recommendation

---

## SECTION 03: BOTTOM LINE UP FRONT (BLUF)

**Origin:** US Military, adapted for executive communication

**Use when:** Any situation where you have 60 seconds or less — verbal briefings, email subject lines, Slack messages to executives, and opening statements.

### The Structure

| **Element** | **Definition** |
|---|---|
| **B — Bottom Line** | State the conclusion, decision, or action required — in the very first sentence. No preamble. No context-setting. The answer first. |
| **L — Level** | Pitch the detail at the correct level for the audience. Add only enough context to make the bottom line credible. |
| **U — Urgency** | State the timeline or decision deadline explicitly. When does this need a response? What happens if it doesn't get one? |
| **F — Follow-up** | State the specific action you need from the recipient. Not 'let me know your thoughts' — a specific, time-bound request. |

### Worked Examples

**BEFORE BLUF (Weak):**  
"Hi Sarah, I wanted to follow up on our discussion last week about the cloud migration programme. As you know, we've been working through several options and the team has done a thorough analysis. I thought it would be helpful to share some of the findings..."

**AFTER BLUF (Strong):**  
"Sarah — we need a go/no-go decision on cloud provider by Friday 5pm. AWS is our recommended option based on cost, compliance posture, and migration risk. Delay beyond Friday pushes our Q2 launch by six weeks. Can you confirm approval or schedule 20 minutes to discuss blockers?"

### BLUF for Email Subject Lines

Executive email is scanned, not read. The subject line must contain the bottom line.

**Subject Line Transformation:**

- WEAK: "Cloud Migration Update"  
  STRONG: "DECISION NEEDED by Fri: Cloud Provider — AWS Recommended"

- WEAK: "Re: Architecture Review Board Meeting"  
  STRONG: "ARB APPROVED: Payment Platform Modernisation — Phase 1 Green"

- WEAK: "Technical Debt Analysis"  
  STRONG: "ACTION: £4M Technical Debt Risk Requires CFO Sign-off by EOW"

---

## SECTION 04: SBAR — SITUATION · BACKGROUND · ASSESSMENT · RECOMMENDATION

**Origin:** US Navy / Healthcare, adapted for technology leadership

**Use when:** High-stakes briefings, incident communication, regulatory updates, and any situation where the audience needs to take action quickly.

### The Structure

| **Element** | **Definition** |
|---|---|
| **S — Situation** | What is happening right now? One to two sentences. State the current state clearly and factually. |
| **B — Background** | What context does the audience need to understand the situation? Only what is relevant — not a full history. |
| **A — Assessment** | What is your professional judgement of the situation? What does it mean? What is the severity? What are the options? |
| **R — Recommendation** | What specific action do you recommend? By whom? By when? What is the consequence of inaction? |

### Worked Example: Security Incident Escalation

| **Element** | **Content** |
|---|---|
| **Situation** | At 14:23 today, our security monitoring detected unauthorised access to the customer data environment. Approximately 40,000 customer records may have been exposed. |
| **Background** | The access was via a compromised service account created during last month's infrastructure migration. The account had broader permissions than required. We identified this through routine anomaly detection. |
| **Assessment** | This is a high-severity incident with regulatory notification obligations under GDPR Article 33. The 72-hour notification window begins now. The access has been contained. Customer impact is under assessment but may require direct notification. |
| **Recommendation** | I recommend: (1) legal and compliance engaged immediately, (2) ICO notification drafted by 17:00 today, (3) CEO informed before end of business. I need your authorisation to proceed. Decision needed in the next 30 minutes. |

### SBAR Strengths

- Forces completeness — situation, context, and action
- Works under extreme time pressure
- Used by the audience receiving the briefing — they know the structure
- Prevents the common failure of reporting without recommending

### SBAR Limitations

- Too structured for relationship communication
- Can feel clinical in emotionally sensitive situations
- Not suitable for exploratory or ambiguous conversations
- Requires that you have a recommendation — do not use it if you don't

---

## SECTION 05: SCR — SITUATION · COMPLICATION · RESOLUTION

**Origin:** Narrative storytelling tradition, adapted for business communication

**Use when:** Strategic presentations, investment cases, transformation narratives, and any communication that needs to generate urgency before the recommendation.

### The Structure

| **Element** | **Definition** |
|---|---|
| **S — Situation** | Establish the stable world that the audience recognises. This is common ground — what everyone already knows and agrees on. |
| **C — Complication** | Introduce the disruption: the change, the threat, the gap, or the risk that means the current situation cannot continue. This is where you create urgency. |
| **R — Resolution** | Present your recommendation as the answer to the complication. The resolution should feel inevitable given the complication. |

### Why SCR Works Neurologically

The human brain is a narrative processing machine. We understand the world through story structure — stable state, disruption, resolution. When you structure a business communication as SCR, you work with the brain's natural processing rather than against it. The complication creates a cognitive gap that the brain is compelled to close — making your resolution feel earned rather than imposed.

### Worked Example: Platform Investment Case

| **Element** | **Content** |
|---|---|
| **Situation** | For the past five years, our technology platform has supported strong growth. We have delivered 40 new products and grown revenue by 180%. Our engineering teams are experienced and our architecture has served us well. |
| **Complication** | The same architecture that enabled our growth is now becoming our constraint. Delivery cycle times have doubled in three years. Our largest competitor launched six equivalent features last quarter in the time it took us to launch two. Three regulatory requirements due in 18 months cannot be built on our current platform without fundamental redesign — at greater cost than a planned modernisation. |
| **Resolution** | A two-year platform modernisation programme, funded at £18M, will restore our delivery velocity, eliminate the regulatory risk, and position us to deliver the next five years of growth. The cost of inaction — continued velocity degradation, regulatory exposure, and competitive disadvantage — exceeds £40M over the same period. |

### Craft Principles

- The Situation must be genuinely stable — if you introduce tension in the Situation, the Complication loses its impact
- The Complication must be specific and credible — vague threats do not create urgency
- The Resolution must flow directly from the Complication — it should be the obvious answer, not a surprise
- Use data in the Complication — numbers make threats concrete and memorable

---

## SECTION 06: PREP — POINT · REASON · EXAMPLE · POINT

**Origin:** Debate and advocacy training

**Use when:** Verbal communication under pressure — Q&A sessions, board challenges, panel discussions, and any situation requiring a structured oral response in 60–90 seconds.

### The Structure

| **Element** | **Definition** |
|---|---|
| **P — Point** | State your position in one clear sentence. No preamble. No 'that's a great question.' Straight to the point. |
| **R — Reason** | Give the single strongest reason your position is correct. Not three reasons — one. The best one. |
| **E — Example** | Ground the reason in a specific, concrete example or data point. Abstract reasoning without evidence is not persuasive at executive level. |
| **P — Point** | Restate your position — now reinforced by the reason and example. This closes the loop and drives the point home. |

### Worked Example: Board Challenge

**BOARD MEMBER:** "Why should we trust your team to deliver this when the last platform programme was two years late?"

- **P — POINT:** "The programme design is fundamentally different from the one that ran over."

- **R — REASON:** "The previous programme tried to do everything at once — 47 workstreams, no staged gating, and a fixed scope. This programme is staged: each phase must prove value before funding is released for the next."

- **E — EXAMPLE:** "Phase 1 is three months and £2M. It delivers one measurable outcome: payment processing latency below 200ms. If we miss that, the programme stops. That gate structure did not exist before."

- **P — POINT:** "The architecture of this programme prevents the failure mode of the last one. I am accountable for that design, and I am confident it holds."

### PREP Under Time Pressure

PREP is designed for the 60-second executive response. When challenged, the instinct is to add more context. PREP prevents this — it forces you to select the single strongest argument and deploy it with precision. Practice PREP until it is automatic. You should be able to structure any oral response in PREP within five seconds of hearing the question.

### PREP Discipline Rules

- **Time:** 60–90 seconds maximum per PREP response
- **Reason:** Choose one — the strongest. Adding three reasons dilutes all three
- **Example:** Must be specific. "We've seen this before" is not an example
- **Second Point:** Do not introduce new information — close, don't continue
- **Recovery:** If challenged after your PREP response, deploy a second PREP rather than extending the first

---

## SECTION 07: SBI — SITUATION · BEHAVIOUR · IMPACT

**Origin:** Center for Creative Leadership

**Use when:** Delivering feedback to peers, senior engineers, and leaders — especially in situations where the behaviour has had a visible negative impact.

### The Structure

| **Element** | **Definition** |
|---|---|
| **S — Situation** | Anchor the feedback to a specific, observable situation. When and where did it happen? Be precise — avoid 'you always' or 'you never.' |
| **B — Behaviour** | Describe only the observable behaviour — what you saw or heard. Not your interpretation. Not their intention. Only what happened. |
| **I — Impact** | Describe the impact of that behaviour — on the team, the decision, the outcome, or on you. This is where you connect the behaviour to why it matters. |

### Worked Example: Senior Architect Feedback

**SBI Example — Psychological Safety**

- **SITUATION:** "In yesterday's design review, when the junior engineer presented the API proposal..."

- **BEHAVIOUR:** "...you interrupted them three times before they completed their first slide, and you characterised their approach as naive without asking any questions."

- **IMPACT:** "The engineer stopped contributing for the rest of the session. Two other junior engineers in the room told me afterwards they are now reluctant to present in reviews. We lose the perspectives we most need to hear."

### Why SBI Works

SBI works because it is irrefutable at the Situation and Behaviour levels — you are reporting observation, not interpretation. The recipient cannot argue with what happened. They can only engage with the Impact, which opens the conversation. It removes the most common feedback failure: character judgements ('you're dismissive') that trigger defensiveness and close the conversation.

### SBI Done Well

- Situation is specific — date, meeting, event
- Behaviour is observable — seen or heard, not inferred
- Impact is real — on people, decisions, or outcomes
- Delivered promptly — within 24–48 hours of the event

### SBI Done Poorly

- Situation is vague — 'you often do this'
- Behaviour is interpreted — 'you were trying to undermine me'
- Impact is about your feelings only — no organisational consequence
- Delivered weeks later, attached to a performance review

---

## SECTION 08: THE BURNING PLATFORM FRAMEWORK

**Origin:** Daryl Conner, Managing at the Speed of Change, 1993

**Use when:** Creating urgency for transformation and change — when the status quo is genuinely dangerous but the organisation has not yet recognised it.

### The Metaphor

The Burning Platform metaphor describes a North Sea oil worker who jumped from a burning platform into freezing water — choosing certain discomfort over certain death. Conner used it to explain why people change: not because the new state is attractive, but because the current state is intolerable. This framework is for creating that recognition in an organisation or executive audience.

### The Three Elements

**1. The Platform is Burning**

Make the cost of inaction visible, specific, and time-bound. Vague threats do not create urgency. Quantified, dated consequences do. "We risk regulatory action by Q3 if we do not act" is a burning platform. "We have technical debt" is not.

**2. The Jump is Survivable**

Define the transformation as achievable, not just necessary. If the audience believes the jump will kill them, they stay on the platform. Your case must include evidence that the change is deliverable — comparable examples, staged milestones, and risk mitigation.

**3. Staying is Not an Option**

Remove the third alternative — doing nothing. Present the cost of inaction at least as prominently as the cost of change. The audience must believe that the current trajectory leads to a worse outcome than the disruption of transformation.

### Ethical Guardrails

The Burning Platform is a powerful framework that can be misused. Use it only when the urgency is genuine — manufactured urgency erodes trust permanently when it is discovered. If you have to exaggerate the threat to create urgency, the problem is not the communication; it is the strategy. Revisit whether the initiative is genuinely necessary.

### Burning vs Not Burning

**The platform IS burning:**  
"Our three largest competitors have launched AI-native products in the past six months. Our largest customer has issued an RFP that our current platform cannot respond to. If we do not have a credible AI capability by Q4, we are not on the shortlist."

**The platform IS NOT burning:**  
"AI is transforming every industry and we need to move fast or we will be left behind." [Too vague — no specific threat, no timeline, no evidence]

---

## SECTION 09: RISK-ADJUSTED NARRATIVE

**Origin:** Executive communication practice, uncertainty management

**Use when:** Any situation where you must communicate genuinely uncertain outcomes to an audience that desires certainty — boards, investment committees, regulatory bodies.

### The Structure

| **Element** | **Definition** |
|---|---|
| **1 — Anchor** | State your current best estimate clearly and directly. Do not bury it in caveats. Give the number, the outcome, or the recommendation first. |
| **2 — Range** | Provide a confidence-weighted range — not a single point estimate. Name the upper and lower bounds and what drives the variance. |
| **3 — Assumptions** | State the two or three key assumptions the estimate rests on. Explicit assumptions are more credible than hidden ones. |
| **4 — Uncertainty Type** | Distinguish aleatory uncertainty (irreducible variability) from epistemic uncertainty (knowable with more analysis). Show what actions will reduce the uncertainty. |
| **5 — Decision Gate** | Propose a specific checkpoint where the uncertainty will be materially reduced and the estimate revised. This converts open-ended uncertainty into managed risk. |

### Worked Example: Investment Case with Uncertainty

**Risk-Adjusted Narrative Applied:**

- **ANCHOR:** Our current estimate for the modernisation programme is £14M over 24 months.

- **RANGE:** The range is £11M–£18M, depending primarily on the complexity of the legacy data migration.

- **ASSUMPTIONS:** This estimate assumes (1) no significant regulatory requirement changes in the period, (2) third-party API dependencies remain stable, and (3) we can recruit four senior engineers at market rate within 60 days.

- **UNCERTAINTY TYPE:** The data migration complexity is epistemic — we will know more after a 6-week discovery spike. The regulatory environment is aleatory — we cannot eliminate it but have built a 15% contingency.

- **DECISION GATE:** We will return to the board at week 8 with a revised estimate after the discovery spike. At that point the range narrows to approximately ±10%.

### Why This Works

Executives who communicate false precision get short-term approval and long-term credibility damage when reality diverges from the forecast. The Risk-Adjusted Narrative builds credibility by being accurately uncertain rather than precisely wrong.

---

## SECTION 10: STAKEHOLDER REGISTER FRAMEWORK

**Origin:** Programme management and executive communication practice

**Use when:** Before any major communication — board paper, investment case, transformation narrative, or difficult conversation — to ensure the message is tailored to each audience.

### The Audience Matrix

| **Audience** | **Register** | **Focus** | **Length** | **Tone** |
|---|---|---|---|---|
| **Board** | Strategic | Why this matters to the enterprise and its risk profile | 3 min | Measured, confident, decisive |
| **CEO** | Executive | What to decide and what I need from you | 5 min | Direct, business-outcome focused |
| **CFO** | Financial | What does this cost, what is the return, and what is the risk | 10 min | Quantified, scenario-based |
| **CIO/CTO** | Technical | What are we building and what are the risks and dependencies | 30 min | Structured, rigorous, options-based |
| **CISO** | Risk | What are the security and compliance implications | 20 min | Risk-tiered, compliance-linked |
| **Eng. Leaders** | Operational | What are we doing, in what sequence, and what do we need | Detailed | Specific, actionable, technically grounded |
| **Regulators** | Formal | Evidence of control, compliance, and governance | Formal | Precise, evidenced, no ambiguity |

### Stakeholder Influence Map

Before any major initiative, map your stakeholders across two axes: decision power (high/low) and disposition (supportive/resistant). This produces four segments that require different communication strategies.

**A — High Power / Supportive**

Engage deeply. Keep informed. Use as sponsors and validators. Equip them to carry your message to others.

**B — High Power / Resistant**

Invest most heavily here. Understand the source of resistance. Tailor the narrative to their specific concerns. One-on-one meetings before any group session.

**C — Low Power / Supportive**

Build the coalition. These are your credibility validators and ground-level advocates. Keep them engaged and visible.

**D — Low Power / Resistant**

Monitor but do not over-invest. Address their concerns through the high-power stakeholders they align with.

---

## SECTION 11: THE THREE-LENS COMMUNICATION MODEL

**Origin:** Executive communication and strategic framing practice

**Use when:** Framing any technology initiative for an executive or board audience — ensuring the business, risk, and investment dimensions are all covered.

### The Three Lenses

| **Lens** | **Focus** |
|---|---|
| **Business Lens** | Why does this matter to the business? What customer, revenue, market, or competitive outcome does this enable or protect? This lens is for the CEO and CPO. |
| **Risk Lens** | What risk does this address or create? Regulatory, security, operational, reputational? What is the cost of inaction? This lens is for the CFO, CRO, CISO, and Board. |
| **Investment Lens** | What does this cost? What is the return and over what period? What are the staged commitment options? This lens is for the CFO and Audit Committee. |

### Critical Insight

Most architects communicate only through the Business Lens — they explain what the technology does and why it is valuable. Executives who approve investment are equally concerned with the Risk and Investment lenses. A communication that does not address all three leaves questions unanswered — and unanswered questions become objections.

### All Three Lenses Applied

- **BUSINESS:** This modernisation restores our product delivery velocity to competitive parity — we can ship features 3x faster and respond to customer needs without 9-month lead times.

- **RISK:** Without this investment, we face three material risks: regulatory non-compliance (£5M+ fine exposure), inability to respond to the incoming PSD3 requirement, and an 18-month window where a competitor with modern architecture can outpace us in every product category.

- **INVESTMENT:** £14M over 24 months, with a £6M value realisation in year 3 through reduced delivery cost and platform licensing consolidation. Staged gating at months 6, 12, and 18 limits committed exposure to £4M at each gate.

---

## SECTION 12: OBJECTION PRE-EMPTION FRAMEWORK

**Origin:** Courtroom advocacy and executive communication

**Use when:** Major investment cases, board presentations, executive steering committees — any high-stakes communication where objections are predictable.

### The Framework

| **Step** | **Action** |
|---|---|
| **1 — Map Objections** | Before any major communication, list every objection the audience is likely to raise. Be genuinely adversarial — make the strongest version of each objection. |
| **2 — Classify** | Sort objections into three categories: (A) objections you can pre-empt in the presentation itself, (B) objections you should prepare PREP responses for, (C) objections that reveal a genuine gap in your proposal. |
| **3 — Pre-empt in Content** | For Category A objections, address them proactively in your narrative — 'You may be wondering why we chose AWS over Azure — here is our analysis.' |
| **4 — Prepare Responses** | For Category B objections, have a prepared PREP response ready. Rehearse it until it is fluent and natural. |
| **5 — Revise or Disclose** | For Category C objections — genuine gaps — either revise the proposal to address them, or disclose the gap with a plan to resolve it. Never hope the audience doesn't notice. |

### Common Architecture Objections and Pre-Emptions

**OBJECTION:** "Why didn't you consider [alternative]?"  
**PRE-EMPTION:** Include an explicit options analysis with your recommendation. Show that you considered it, evaluated it, and explain why your recommendation is superior.

**OBJECTION:** "This is too expensive."  
**PRE-EMPTION:** Lead with the cost of inaction. "At £14M, this programme costs less than the regulatory exposure we face if we do not act, and less than the accumulated delivery cost over three years."

**OBJECTION:** "The last programme ran over — why should we trust this one?"  
**PRE-EMPTION:** Include a specific section on how the governance model of this programme is designed to prevent the failure modes of the previous one. Be explicit about what is different.

---

## SECTION 13: DIFFICULT CONVERSATION FRAMEWORK

**Origin:** Harvard Negotiation Project — Difficult Conversations (Stone, Patton, Heen)

**Use when:** Delivering hard news, managing conflict, giving critical feedback, and any conversation where the stakes are high and emotions are involved.

### The Three Conversations

| **Conversation** | **Focus** |
|---|---|
| **1 — What Happened** | Separate the facts from the story you are telling about the facts. In any difficult conversation, both parties have a different story. Start by sharing your view as a perspective, not a truth: "From where I sit, what I observed was..." not "What actually happened was..." |
| **2 — The Feelings Conversation** | Acknowledge the emotional dimension — yours and theirs. Unexpressed feelings drive difficult conversations underground. Naming emotions reduces their power: "I want to be direct — this conversation matters to me." |
| **3 — Identity** | Understand that difficult conversations threaten identity — for both parties. The other person's resistance is often about protecting their sense of competence, integrity, or belonging. Address this directly. |

### The Opening Move

The first 60 seconds of a difficult conversation determine whether it becomes productive or defensive. The opening must signal that you are entering a conversation, not delivering a verdict.

### Opening Move Contrast

**VERDICT OPENING (avoid):**  
"I wanted to talk to you because your behaviour in the design review yesterday was unacceptable."

**CONVERSATION OPENING (use):**  
"I wanted to talk about yesterday's design review because I think something happened there that affected the team, and I want to understand it from your perspective before sharing mine."

### Principles for Difficult Conversations

- Prepare the conversation, not your arguments. Know what you want the outcome to be — not just what you want to say.
- Listen for the version of the story you haven't heard. Ask before advocating.
- Name what is difficult: "This is a hard conversation for me to have, and I want to have it well."
- End with a shared understanding, not a verdict: "What would you like to happen from here?"

---

## SECTION 14: WRITTEN COMMUNICATION STANDARDS

**Origin:** C-suite and board communication practice

**Use when:** Board papers, executive memos, decision notes, architecture decision records, and any written communication to a senior audience.

### The Executive Memo Standard

| **Element** | **Guidance** |
|---|---|
| **1 — Subject Line** | State the decision needed or the outcome of reading: "DECISION: Cloud Provider Selection — AWS Recommended" not "Cloud Update". |
| **2 — Executive Summary** | Three sentences maximum. Recommendation, rationale, and action required. The entire document should be readable from the executive summary alone. |
| **3 — Recommendation** | State the recommendation before the analysis. Executives read to validate or challenge — they need the recommendation first. |
| **4 — Options Considered** | Show that you considered alternatives. Include a brief options table with the top two or three options and the key differentiators. |
| **5 — Risk & Mitigation** | Name the top three risks and the mitigation for each. Do not bury risk in footnotes. |
| **6 — Decision Required** | State exactly what decision you need, from whom, and by when. Never end a document without a clear next action. |

### Architecture Decision Record (ADR) Standard

An ADR is the written artefact of an architectural decision. At executive level, ADRs serve as governance documentation and audit trail. They must be comprehensible to a non-technical executive.

| **Element** | **Definition** |
|---|---|
| **1 — Context** | What is the situation and the force that requires a decision? |
| **2 — Decision** | What was decided? State it clearly in one sentence. |
| **3 — Rationale** | Why this option? The three to five strongest reasons. |
| **4 — Alternatives** | What else was considered and why was it not chosen? |
| **5 — Consequences** | What are the positive and negative consequences of this decision? |
| **6 — Review Date** | When will this decision be reconsidered in light of new evidence? |

### Writing That Works

- Subject line contains the decision or outcome
- Recommendation before analysis — always
- Plain English — no architecture jargon
- Active voice: "We recommend" not "It is recommended"
- One idea per sentence
- Decision and owner clearly named

### Writing That Fails

- Subject line is a topic, not an action
- Analysis builds to the recommendation — buried at the end
- Technical vocabulary without translation
- Passive voice throughout — removes accountability
- Dense paragraphs with multiple ideas
- Document ends without a clear next action

---

## SECTION 15: COMMUNICATION ANTI-PATTERNS

These are the most common communication failures that destroy credibility at the executive and board level. Each one is observable, diagnosable, and correctable. Review this section before every major communication.

### AP1: The Architecture Lecture

**Problem:** Explaining the technical architecture in detail to an audience that needs the business outcome. Triggered by the belief that if the audience understood the technical complexity, they would approve the investment.

**Fix:** Reframe: "What does this enable the business to do that it cannot do today?" Start there. The architecture is the appendix, not the presentation.

### AP2: The Certainty Performance

**Problem:** Projecting false confidence about uncertain outcomes because the audience signals a preference for certainty. Builds short-term approval and long-term credibility damage.

**Fix:** Use the Risk-Adjusted Narrative. Accurate uncertainty is more credible than false precision.

### AP3: The Endless Context

**Problem:** Spending 80% of the communication on background and context before reaching the recommendation. By the time the recommendation arrives, the audience has stopped listening.

**Fix:** Use BLUF or Pyramid Principle. Recommendation first. Context is the appendix.

### AP4: The Passive Hedge

**Problem:** Using passive voice and hedged language to avoid accountability: "It might be considered that..." "There could be a case for..." This reads as low confidence, regardless of the content.

**Fix:** Use active voice with accountability: "I recommend..." "We will..." "The risk is..."

### AP5: The Jargon Shield

**Problem:** Using technical vocabulary as a signal of expertise rather than as a communication tool. Forces the audience to translate rather than engage.

**Fix:** For every technical term, ask: "What is the plain English equivalent?" If a CFO would need to Google it, replace it.

### AP6: The Disagreement Avoidance

**Problem:** Softening a recommendation to avoid conflict, until the recommendation no longer exists. Presenting 'options' when you have a clear view is a failure of leadership, not sensitivity.

**Fix:** State your recommendation. Then acknowledge the strongest counterargument. Then explain why your recommendation is still correct. Avoiding conflict in communication is not diplomacy.

### AP7: The No-Ask Close

**Problem:** Ending a presentation or document without a clear call to action. "I hope this was useful" is not a close. "I need a decision by Friday" is.

**Fix:** Every communication must end with: a specific action, a named owner, and a deadline.

---

## THE MASTER CHECKLIST

Before every significant communication, run through this checklist:

| **Checkpoint** | **Question** |
|---|---|
| **Audience** | Have I calibrated the register, abstraction level, and length to this specific audience? |
| **Framework** | Have I selected the right framework for this communication type? (Board→PP/SCR, Briefing→SBAR, Verbal→PREP) |
| **BLUF** | Does my opening sentence contain the recommendation or decision needed? |
| **3 Lenses** | Have I addressed the Business, Risk, and Investment dimensions? |
| **Objections** | Have I pre-empted the three most likely objections in the content? |
| **Uncertainty** | Have I communicated uncertainty accurately rather than performing false precision? |
| **Ask** | Does my communication end with a specific action, owner, and deadline? |
| **Register** | Is there any jargon, passive voice, or technical vocabulary that would require translation? |

## Related

- [Business Communication & Executive Skills](82-ea-business-communication-executive-skills.md) — the skills-level companion to this frameworks guide.
- [EA Architect Deep Dive: The Five Arenas](06-ea-architect-deep-dive-five-arenas.md) — the executive-stakeholder arena these frameworks serve.

