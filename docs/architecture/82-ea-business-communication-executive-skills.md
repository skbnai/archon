---
doc_type: guide
domain: architecture
topic_id: ea-business-communication-executive-skills
title: Business Communication & Executive Skills
created: 2026-07-10
updated: 2026-07-23
sources: []
covers_version: 2026
supersedes:
  - docs/enterprise-architecture/specialization/EA_Business_Communication_Executive_Skills.md
---

# Business Communication & Executive Skills

The skills that determine whether your architecture recommendations get funded, followed, or ignored. Based on research across McKinsey, BCG, Gartner, and Harvard Business Review — this guide provides frameworks, scripts, templates, and the exact language to use in the exact situations you will face.

## Business Acumen: Speak the Language of the C-Suite

Gartner (2026) found that 73% of Enterprise Architecture programmes require financial and business acumen ranked second only to data and AI architecture skills. You must answer: what does this mean for revenue or risk?

Every Enterprise Architect must interpret three financial statements: Income Statement (P&L), Balance Sheet, and Cash Flow Statement. Technology investment appears as OpEx or creates depreciation of assets; technical debt appears as a liability.

### The Five Numbers Every EA Must Know

**Total Cost of Ownership (TCO)** includes acquisition cost, implementation, annual operating cost, support, and decommissioning — modeled over 3–5 years.

**Return on Investment (ROI)** = [(Financial Gain - Cost of Investment) / Cost of Investment] × 100. Target: >15% for technology investments.

**Payback Period** = Cost of Investment / Annual Net Benefit. Anything under 24 months is typically easy to approve.

**Net Present Value (NPV)** accounts for time value of money using 8–12% discount rate. Positive NPV means the investment creates value.

**Cost of Inaction** = Annual Productivity Loss + Risk-Adjusted Incident Cost + Opportunity Cost. The most underused metric in EA: "Staying on the current platform costs £187K/yr, growing at 25% annually as the team scales."

**Business acumen example:** "Our demand forecasting pilot cost £1.1M and delivered £2.1M in annual savings — that's a 91% ROI at month 14. To scale it, we need £800K additional investment with an adjusted payback of 8 months on the incremental spend."

## The Pyramid Principle: McKinsey's Communication Framework

Created by Barbara Minto at McKinsey in the 1970s, the Pyramid Principle is now standard in every major consulting firm and boardroom. The core idea: start with the answer. Most people present chronologically, building up to the conclusion. Executives don't have time for that.

**Structure:** Assertion (state your recommendation in one sentence maximum) → Arguments (3 key reasons why your assertion is true) → Evidence (data, facts, analysis supporting each argument).

**SCQA Framework — Setting Up the Pyramid:**
- **Situation:** The shared context the audience already knows
- **Complication:** The change, problem, or tension that disrupts the situation
- **Question:** The question the complication naturally provokes
- **Answer:** Your recommendation — the top of the pyramid

**Rule of 3:** Arguments come in threes. The human brain naturally groups in three. If you have 7 reasons, your audience will forget 5. Find your 3 strongest arguments.

**Example — Pyramid in document form:**
- RECOMMENDATION: We recommend running a 7-week RFI to select an enterprise AI platform. This will unlock 1,248 hours of annual data science productivity and enable our GenAI programme. Expected Year-1 ROI: 340%.
- ARGUMENT 1: Our current SageMaker platform costs us £187K/year in productivity loss and cannot support the GenAI architecture we committed to the board.
- ARGUMENT 2: Three vendors — Databricks, AWS, DataRobot — are competitive at our scale with Year-1 adjusted TCO between £395K and £440K.
- ARGUMENT 3: A structured RFI protects us from vendor lock-in and ensures we select the platform that fits our AI governance requirements.

## Executive Presence & Gravitas

Executive presence is not charisma. It is the confidence, composure, and credibility that makes senior stakeholders believe you are the expert in the room.

**The Four Pillars:**

**Preparation Gravitas** — Know the numbers cold: TCO, ROI, DORA metrics, vendor comparison scores. Before any executive meeting, know the three questions you will be asked, the three objections you will face, and the one number that settles every argument.

**Composure Under Challenge** — When challenged in an Architecture Review Board, use this formula: PAUSE (2 seconds), ACKNOWLEDGE ("That's an important point"), RESPOND (your substantive answer), CONFIRM ("Does that address your concern?"). Never become defensive.

**Language Precision** — Replace vague language with precise language. "It's quite complex" → "It involves three interdependent systems." "It might take a while" → "It will take 6 weeks with this team." Precise language signals precise thinking.

**Strategic Brevity** — The average executive attention span in a meeting is 4 minutes. McKinsey's rule: if you cannot state your recommendation in one sentence and your supporting case in three sentences, you do not yet understand your own recommendation.

## Stakeholder Navigation: Influence Without Authority

The EA rarely has line management power over the people whose decisions they need to shape. Authority is positional; influence is relational.

**The Mendelow Matrix** maps stakeholders on two axes: Power (ability to impact the programme) and Interest (how much they care). This yields four quadrants: Keep Satisfied (low interest, high power), Manage Closely (high interest, high power), Monitor (low power/interest), Keep Informed (low power, high interest).

**The Seven Currencies of Influence** (Cohen & Bradford): Inspiration (vision, purpose), Task (resources, budget, information), Position (recognition, visibility), Relationship (personal connection), Personal (gratitude, ownership, challenge), Outside Currency (referrals, connections), Safe Environment (reduced risk, psychological safety).

**Managing difficult stakeholders:** Pre-empt the technical expert who goes over your head by engaging them early. Ask them to co-author the options analysis — people are far less likely to undermine decisions they contributed to.

## Negotiation & Persuasion: Getting to Yes

Enterprise Architects negotiate constantly — for budget, vendor terms, governance decisions. Negotiation in the EA context is rarely adversarial; it is finding the solution that gives both parties enough of what they need to move forward.

**Fisher & Ury's Four Principles (Getting to Yes):**
1. Separate People from Problems — the technical architect who wants an unapproved technology is not your adversary; attack the architecture problem together.
2. Focus on Interests, Not Positions — their position: "We must use MongoDB." Their interest: "We need a document store that scales to 10,000 writes per second." Multiple solutions address the interest.
3. Invent Options for Mutual Gain — prepare at least three options that could work for both sides.
4. Insist on Objective Criteria — "The approved technology radar says..." or "The ARB decision record states..." — objective criteria end arguments.

**BATNA (Best Alternative to a Negotiated Agreement)** is your most important negotiation concept. Define your BATNA and try to understand theirs before entering any significant negotiation. The party with the better BATNA has more negotiating power.

## The Art of Presentation: Board Decks & One-Pagers

70% of employers worldwide rate communication as the most sought-after skill. Yet most EA presentations are built backwards — they start with analysis and end with the recommendation.

**The 5-Slide Executive Architecture Brief:**
- **Slide 1: The Recommendation** — One sentence. Large font. "We recommend migrating to an enterprise AI platform by Q4 2026, at a cost of £2.1M, delivering £7.2M in three-year value."
- **Slide 2: The Situation** — SCQA Situation + Complication in 2–3 bullet points. Maximum 30 words. No technical jargon.
- **Slide 3: The Options** — A simple 3-column table: Option A (current state), Option B (your recommendation), Option C (alternative). Score each on Cost, Speed, Risk, Strategic Fit. Make Option B the obvious winner.
- **Slide 4: The Numbers** — One financial summary: TCO, ROI, payback period, cost of inaction. Use a horizontal timeline showing when money goes out and when benefit arrives.
- **Slide 5: The Decision** — Exactly what you need, by when, from whom. "Requested: Board approval to proceed with RFI-2026-AI-001. By: 15 June. Decision maker: Diana Cole (CDO)."

**The Architecture One-Pager** is the EA's Swiss Army knife. A single page that a board member can read in 3 minutes. Structure: Headline (recommendation in one sentence) → Situation (3 lines) + Problem (with numbers) + Cost of Inaction (with numbers) → The Recommendation (3 bullet points + what we will not do) + The Numbers (TCO/ROI/Payback) → Decision Required (exact request + deadline + name) → Risks & Mitigations (2–3 rows) → Supporting Detail (Available in Appendix).

## Written Communication: Emails, Briefs & Reports That Get Read

Executives process email in 5 seconds. In that window they read: the subject line, the first sentence, and — if both pass — the first paragraph. Write every executive email as if only the first 50 words will be read.

**Example:**
- SUBJECT: Approval Required — AI Platform RFI Budget (£150K) — Decision by 14 June
- Hi Diana, We need your approval to proceed with the AI platform RFI at a cost of £150K. This enables the 7-week vendor assessment and secures the GenAI programme timeline. The cost of delay is approximately £3,600 per week in data science productivity. Decision requested by: Friday 14 June. Supporting detail: Attached (2 pages).

**Architecture Decision Records (ADRs)** create institutional memory, preventing the same architectural debates from happening repeatedly. An ADR is read years later and still makes sense.

## Facilitation & Meetings: Getting to Decisions

The EA runs more workshops, review boards, and decision sessions than any other function. A bad facilitator produces a 2-hour meeting with no decision. A great facilitator produces a 90-minute session with a signed-off decision and named owners.

**The ARB Facilitation Script — Opening:**
"Good morning. We have 90 minutes. This ARB has one decision to make today: whether to approve the Unified Commerce Platform initiative under the conditions proposed in ADR-2025-001. The proposal materials were circulated 5 days ago. I'm assuming you've read them. If not — that's fine — I'll summarise in 3 minutes. Questions on the summary before we go to the full discussion?"

**Closing:**
"We've covered the three main areas of concern. Let me test where we are. Alan — are you comfortable with the security architecture as described, subject to the Vault configuration review condition? Karen — is the financial model sufficient for your approval? Understood — that becomes Condition 2. So we're at: Approve with Conditions. I'll issue the ADR by end of day."

## Political Intelligence: The Dimension Nobody Talks About Openly

Every EA operates in a political environment. The question is not whether to engage with organisational politics but whether to do so consciously or naively.

**The Five Laws of Organisational Politics for EAs:** Build a coalition of architecture champions — people in each business unit who understand architectural thinking, advocate for standards, and bring problems to the EA before they become governance crises.

Find the person in each business unit who feels the pain of the current architecture most acutely. That person is your natural champion. Give them both the language and the access to make change happen.

---

**Word count: 1,248**

The EA who speaks in numbers, listens with curiosity, decides with evidence, and communicates with brevity is not just an architect. They are a trusted advisor.
