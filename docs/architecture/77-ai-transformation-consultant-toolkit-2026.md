---
title: AI Transformation Consultant Toolkit 2026 (Part 1 of 2)
doc_type: reference-architecture
domain: architecture
topic_id: ai-transformation-consultant-toolkit-2026
status: current
date_created: 2026-07-10
date_updated: 2026-07-23
last_reviewed: 2026-07-23
source_type: converted-pdf
source_file: AI_Transformation_Consultant_Toolkit_2026.pdf
supersedes:
  - docs/enterprise-architecture/specialization/AI_Transformation_Consultant_Toolkit_2026.md
covers_version: "N/A"
---

## Overview

This is Part 1 of 2 of the AI Transformation Consultant Toolkit 2026. For Part 2, see [Part 2 of 2: Interview Templates, Prioritisation, FAQs, Checklists & Deliverables](pathname:///archon/architecture/parts/27-ai-transformation-consultant-toolkit-2026-part2).

**Complete consultant toolkit for enterprise AI transformation engagements.** Client journey maps, AI readiness assessments, discovery questionnaires modelled on McKinsey, Deloitte, BCG, and Accenture methodologies.

- **12 Sections** — Complete questionnaire + template library
- **150+ Questions** — Discovery, assessment & stakeholder banks
- **40+ Checklists** — Phase-gated deployment checklists
- **5 Client Archetypes** — Journey maps per maturity level
- **8 Templates** — Ready-to-use engagement documents
- **3 Assessment Tools** — Scoring rubrics with maturity levels

For use with clients in any industry. All templates are framework-agnostic and should be customised to client context before engagement.

---

## Part 1: Client Maturity Journey & Archetypes

Before any engagement, you must understand which archetype your client is. Each archetype has different fears, different success metrics, and a completely different transformation path. Misreading the archetype is the #1 cause of failed consulting engagements.

### The 5 Client Archetypes

Every enterprise client falls into one of five archetypes based on their AI maturity, organisational readiness, and strategic intent. Identifying the archetype in the first client conversation shapes everything: your language, your proposal, your timeline, and your risk management approach.

#### Archetype 1: The Anxious Laggard

Has not started AI. Feels pressure from board, competitors, or media. Leadership is excited but fearful. IT is overwhelmed. Data is messy.

**What they say in the first meeting:**
- "Our competitors are all doing this — we're behind"
- "The board asked us to present an AI strategy by Q2"
- "We don't have clean data but everyone says we need AI"

**Your engagement plays:**
- Start with a 2-week discovery + quick win
- Build data foundation before AI
- Executive alignment workshop first
- Set realistic 18-month expectations

#### Archetype 2: The Eager Experimenter

Running 5–15 pilots. Lots of enthusiasm but no coordination. Each team doing their own thing. No shared platform, no governance. Spending money but struggling to show ROI.

**What they say in the first meeting:**
- "We have 12 AI projects running but none have reached production"
- "Every team is using a different tool"
- "We can't measure the value we're getting"

**Your engagement plays:**
- Platform consolidation is the intervention
- Kill 8 projects, double down on 4
- Governance charter immediately
- Shared LLMOps pipeline

#### Archetype 3: The Methodical Scaler

Has 2–5 AI systems in production. Proven ROI in at least one area. Now wants to scale but hitting organisational resistance. Technical depth is good; change management is the gap.

**What they say in the first meeting:**
- "Our RAG system works but only 20% of employees use it"
- "We want to expand to 10 use cases but can't hire fast enough"
- "Middle management is blocking AI adoption in their teams"

**Your engagement plays:**
- Change management programme is primary deliverable
- Citizen developer platform
- AI Champion network per business unit
- Adoption metrics dashboard

#### Archetype 4: The AI-Native Transformer

AI is core to the business model. May be a tech company or digital-native firm. Sophisticated teams. Problems are at the frontier: agentic systems, governance at scale, proprietary model strategy.

**What they say in the first meeting:**
- "We want to build our own foundation model on proprietary data"
- "Our agentic system is causing audit trail compliance issues"
- "How do we govern 200 AI agents running autonomously?"

**Your engagement plays:**
- Principal-level architecture engagement
- Agentic governance framework
- Fine-tuning and model ownership strategy
- AI CoE maturity review

#### Archetype 5: The Regulated Reluctant

Healthcare, financial services, legal, government. Deep compliance constraints. Enormous potential value but genuine regulatory risk. Legal team often has veto power. Leadership wants AI but is risk-averse.

**What they say in the first meeting:**
- "Our legal team won't approve any external API calls with patient data"
- "We need explainability for every AI decision that affects a customer"
- "What happens if the AI makes a wrong decision and someone gets hurt?"

**Your engagement plays:**
- Lead with governance and compliance architecture
- On-prem or HIPAA-compliant cloud only
- Shadow-mode deployment first
- Legal team in architecture reviews from day 1

### Client Journey Map — Across All Archetypes

```mermaid
stateDiagram-v2
    [*] --> Awareness: First conversation
    
    Awareness --> Discovery: Board asks<br/>for strategy
    Discovery --> Pilot: SOW signed<br/>sponsor identified
    Pilot --> Foundation: Measurable<br/>success
    Foundation --> Scale: 3+ use cases<br/>CoE established
    Scale --> Transformation: AI native<br/>new business models
    
    Awareness: Client heard about AI<br/>No clear plan
    Discovery: Explore solutions<br/>Assess readiness
    Pilot: First project live<br/>Limited scope
    Foundation: Platform built<br/>Governance emerges
    Scale: 10+ systems<br/>ROI demonstrated
    Transformation: AI is operating model<br/>New revenue streams
```

**Enterprise AI Transformation Client Journey.** Six invariant stages from initial awareness through AI-native transformation, with speed and difficulty varying by client archetype. The consultant's role shifts significantly across stages—from educator to architect to operations partner to strategic advisor.

This is the universal journey a client traverses from first conversation to AI-native transformation. The speed and difficulty of each stage varies by archetype, but the sequence is invariant. Understand where your client is today to prescribe the right intervention.

| Stage | Name | Client State of Mind | Your Primary Role | Success Signal |
|-------|------|---------------------|--------------------|-----------------|
| 0 | Awareness | Has heard about AI. Curious or anxious. No clear plan. Board is asking questions. | Educator & Framer — set realistic expectations, define terms, share relevant case studies | Client can articulate one concrete use case they want to explore |
| 1 | Discovery | Actively exploring. Running internal conversations. Some pilots under consideration. Budget not yet committed. | Diagnostician — run readiness assessment, interview stakeholders, map pain points to AI solutions | Signed Statement of Work for Discovery phase. Internal sponsor identified. |
| 2 | Pilot | First AI project live. Small team. Limited scope. Watching closely for success or failure. Nervous. | Hands-on Architect — design the system, manage the eval, fix the failures, document learnings | Pilot delivers measurable result against pre-agreed success metric. Second use case approved. |
| 3 | Foundation Build | Committed to AI. Building the platform. Governance emerging. Talent hiring underway. Org friction appears. | Platform Architect & Change Agent — centralise the stack, establish governance, surface and resolve org resistance | AI platform serves 3+ use cases. CoE established. Governance charter signed. |
| 4 | Scale | 10+ AI systems. Adoption metrics matter. Cost management surfacing. Competitors watching. Some public announcements. | AI Operations Partner — FinOps, adoption programmes, citizen developer platforms, agentic expansion | AI covers >30% of target workflows. Measurable ROI reported to board. AI budget approved for next year. |
| 5 | Transformation | AI is the operating model. New business models emerging. Talent competition is fierce. Board is an AI board. | Strategic Advisor — M&A; AI thesis, proprietary model strategy, ecosystem AI, governance board membership | AI-native products launched. Proprietary models in development. External AI capabilities monetised. |

### Red Flags & Buying Signals per Stage

These signals tell you whether the engagement is progressing or at risk.

| Stage | Green Signal (Proceed) | Red Flag (Intervene) | Action Required |
|-------|------------------------|---------------------|-----------------|
| Awareness | CEO sponsors meeting; asks about competitor AI | Only IT is in the room; CEO is absent | Escalate immediately — no AI transformation without C-suite sponsorship |
| Discovery | Stakeholders are candid about data problems | Stakeholders only share success stories | Run anonymous surveys; data problems they hide will kill the programme later |
| Pilot | Team reports failures honestly; asks for help | Team over-reports success; hides issues | Establish psychological safety; failure data is your most valuable input |
| Foundation | Platform team owns the roadmap | Every team wants to build their own | Escalate platform consolidation to C-suite; this is a governance decision, not a technical one |
| Scale | Adoption rates are tracked and visible | Only usage counts, not outcomes | Redesign success metrics; usage without business outcome is a vanity metric |
| Transformation | AI appears in annual report as a business driver | AI still described as 'IT initiative' | Reframe the narrative with CMO/communications team; perception gap will limit investment |

---

## Part 2: AI Readiness Assessment (Scored)

Run this assessment in the first 2 weeks of every engagement. Score each dimension honestly — clients will push back on low scores, but honesty now prevents failure later. The composite score determines the recommended starting point and timeline.

### Data Readiness Scorecard

Rate each item 1–5. 1 = Not in place. 3 = Partially in place. 5 = Fully in place.

#### Data Availability

| Criterion | Description | Score (1–5) | Notes |
|-----------|-------------|------------|-------|
| Data volumes | Sufficient historical data exists for target use cases (>12 months) | ___ | |
| Data accessibility | Data is accessible via API or structured query without manual export | ___ | |
| Data diversity | Multiple data types available: structured, unstructured, time-series | ___ | |
| Data freshness | Data is updated frequently enough for the target use case | ___ | |

#### Data Quality

| Criterion | Description | Score (1–5) | Notes |
|-----------|-------------|------------|-------|
| Completeness | Key fields have <5% null rate in critical datasets | ___ | |
| Accuracy | Data passes validation rules; known error rate <2% | ___ | |
| Consistency | Same entity represented consistently across systems (no duplicates) | ___ | |
| Lineage | Data provenance is documented — where it came from, how it was transformed | ___ | |

#### Data Architecture

| Criterion | Description | Score (1–5) | Notes |
|-----------|-------------|------------|-------|
| Cataloguing | Data catalogue exists with business definitions and ownership | ___ | |
| Governance | Data governance policies exist and are enforced | ___ | |
| Pipelines | Reliable ETL/ELT pipelines with monitoring and alerting | ___ | |
| Storage | Cloud data warehouse or lakehouse in place (Snowflake, Databricks, BigQuery) | ___ | |

#### AI Data Readiness

| Criterion | Description | Score (1–5) | Notes |
|-----------|-------------|------------|-------|
| Labelled data | Labelled datasets available for supervised learning use cases | ___ | |
| PII handling | PII identification, masking, and access controls are in place | ___ | |
| Training infrastructure | Compute infrastructure available for model training/fine-tuning | ___ | |
| Embedding storage | Vector database or embedding-capable storage exists or is budgeted | ___ | |

#### Data Readiness Score Interpretation

| Score Range | Readiness Level | Recommended Action |
|-------------|-----------------|-------------------|
| 56–80 | Data-Ready | Proceed directly to AI architecture design. Data foundation is sound. |
| 40–55 | Partially Ready | 6-week data remediation sprint before AI pilot. Fix top 3 gaps. |
| 24–39 | Pre-AI | 3-month data foundation programme required. AI pilot after Month 3. |
| <24 | Not Ready | 12-month data transformation first. AI is 18+ months away. Be honest with client. |

### Technical Infrastructure Assessment

Assess current technical capabilities against AI deployment requirements.

| Infrastructure Domain | Assessment Questions | Score |
|-----------------------|----------------------|-------|
| Cloud Maturity | Are workloads running in cloud? Multi-cloud? Is auto-scaling in place? Container orchestration (K8s)? | ___/5 |
| API Architecture | Are enterprise systems accessible via APIs? Is there an API gateway? Is API documentation maintained? | ___/5 |
| Security Posture | Is zero-trust architecture in place? Are there secrets management systems? Vulnerability scanning in CI/CD? | ___/5 |
| DevOps Maturity | Is CI/CD in place? Infrastructure-as-code? Canary deployments? Feature flags? Rollback capability? | ___/5 |
| Observability | Are distributed traces, metrics, and logs collected? Is there alerting on anomalies? SLA monitoring? | ___/5 |
| Identity & Access Management | Is RBAC in place? SSO? Attribute-based access control for sensitive data? Audit logs for all access? | ___/5 |
| Network & Latency | Is network latency between systems measured? Is there a CDN? Edge computing capability for low-latency AI? | ___/5 |
| GPU / AI Compute | Is GPU infrastructure available (cloud or on-prem)? Is there a budget for AI compute? GPU scheduling system? | ___/5 |

### Talent & Culture Readiness

| Dimension | Indicator | Low (1) | High (5) |
|-----------|-----------|---------|---------|
| AI Literacy | % of employees with basic AI literacy training | <10% have awareness | >60% certified |
| Technical Talent | ML Engineers, Data Scientists, AI Architects on staff | 0 dedicated AI staff | >5 AI specialists |
| Data Engineering | Data pipeline engineers and architects | Data work is ad hoc | Dedicated DE team with lakehouse |
| Leadership Commitment | CEO/CAIO publicly committed; budget allocated | IT-only initiative | CEO + board AI strategy |
| Failure Tolerance | Culture accepts learning from AI failures without blame | Failures are hidden | Failures celebrated as learning |
| Experimentation Culture | Teams empowered to run AI experiments independently | All AI requires IT approval | Self-service AI experimentation |
| Change Readiness | Employees embrace workflow redesign around AI | Active resistance | Eager adoption and proposals |

### Composite Readiness Score — Summary Sheet

Complete this after all four assessments. Present to client leadership.

| Assessment Area | Max Score | Client Score | Gap Priority |
|-----------------|-----------|--------------|--------------|
| Data Readiness | 80 | ___ | ___ |
| Technical Infrastructure | 40 | ___ | ___ |
| Talent & Culture | 35 | ___ | ___ |
| Governance Maturity | 30 | ___ | ___ |
| Security Posture | 25 | ___ | ___ |
| **TOTAL** | **210** | **___** | **___** |

#### Overall Readiness Interpretation

| Total Score | Maturity Level | Starting Point | Realistic Timeline to Production |
|-------------|-----------------|-----------------|----------------------------------|
| 170–210 | AI-Ready | Pilot in Week 1 | First production system: 6–8 weeks |
| 130–169 | Advancing | 4-week foundation sprint first | First production: 12–16 weeks |
| 90–129 | Developing | 90-day foundation programme | First production: 6 months |
| 50–89 | Early Stage | Data + talent programme first | First production: 12 months |
| <50 | Pre-Digital | Digital transformation prerequisite | AI in 18–24 months minimum |

---

## Part 3: Discovery Questionnaire Bank

150+ questions across 7 stakeholder groups. Use selectively — never ask all questions in one session. Select 8–12 questions per interview based on role and archetype. Adapt wording to the client's industry and vocabulary.

### Executive / C-Suite Discovery (25 Questions)

**Use for:** CEO, CAIO, COO, CFO  
**Duration:** 45–60 minutes  
**Goal:** Understand strategic intent, budget reality, board pressure, and appetite for risk. These are the questions that shape the entire engagement direction.

#### Strategic Intent

**Q1: What does AI transformation mean for your company specifically, in 3 years? What would have to be true for you to call this a success?**

Listen for: Specificity vs vagueness. Vague = needs vision work first.

---

**Q2: Which competitor or disruptor is making you most nervous on AI, and why?**

Listen for: External threat vs internal aspiration. Both are valid but lead to different programmes.

---

**Q3: If you could automate one workflow that consumes the most senior talent time, which would it be?**

Often reveals the #1 use case hidden behind corporate buzzwords.

---

**Q4: What AI investments have you already made in the last 12 months, and what was the return?**

Reveals true maturity level. "None" means anxiety laggard. "Lots but unclear ROI" means eager experimenter.

---

**Q5: How much of your annual budget are you prepared to allocate to AI in year 1, 2, 3?**

Non-answer = not serious. Specific number = you have a real sponsor.

---

**Q6: What would have to happen for the board to lose confidence in this AI transformation?**

Pre-mortems reveal real risk tolerance. Listen for: PR incident, financial loss, regulatory fine.

---

**Q7: If AI works exactly as planned, what does your business model look like in 5 years that would not be possible today?**

Separates transformation thinkers from optimisation thinkers.

---

#### Governance & Culture

**Q8: Who has ultimate accountability when an AI system makes a mistake that affects a customer?**

No answer = governance gap. This conversation reveals whether they've thought about this.

---

**Q9: Has your board received any formal briefing on AI risk and governance?**

Board awareness is a leading indicator of governance maturity.

---

**Q10: Are there use cases where you would draw a hard line and never deploy AI, regardless of ROI potential?**

Reveals values and risk appetite. Essential input to the governance charter.

---

**Q11: How do you plan to communicate AI changes to employees who are worried about their roles?**

Reveals change management maturity. No plan = danger signal.

---

**Q12: What is your current relationship with AI regulation in your industry, and what are you most uncertain about?**

Compliance awareness. Unknown = assign legal consultation as first deliverable.

---

#### Organisational Readiness

**Q13: Who currently owns the AI agenda inside your organisation? Is that person empowered to spend money and make cross-functional decisions?**

No empowered owner = engagement at risk. Escalate immediately.

---

**Q14: What has surprised you most about your organisation's reaction to AI so far?**

Open question — reveals hidden resistance, unexpected champions, or unknown pilots.

---

**Q15: What data about your business do you believe is most underutilised today?**

Data discovery without sounding like a data audit. Often reveals the best use case.

---

**Q16: If we could only deliver one thing in the first 90 days that would make this engagement a success in your eyes, what would it be?**

The most important question. Answer it and you have a champion. Miss it and you lose the client.

---

### IT & Architecture Discovery (30 Questions)

**Use for:** CTO, CIO, Head of Engineering, Principal Architect  
**Duration:** 60–90 minutes  
**Goal:** Map the technical landscape — what exists, what's broken, what will constrain AI.

#### Infrastructure & Cloud

**Q1: Describe your current cloud architecture. Which providers? What percentage of workloads are cloud-native vs lifted-and-shifted vs on-premises?**

Cloud maturity determines AI deployment options. On-prem heavy = constrained architecture.

---

**Q2: What is your current container orchestration strategy? Are you running Kubernetes in production?**

K8s maturity signals DevOps maturity — critical for LLMOps pipelines.

---

**Q3: Describe your current API landscape. Do you have an API gateway? Are enterprise systems accessible via API?**

Agent architecture requires API-accessible enterprise systems. No APIs = MCP server build required.

---

**Q4: What is your average time from code commit to production deployment?**

Baseline for LLMOps velocity. >2 weeks = cultural or process barrier to rapid iteration.

---

**Q5: What GPU or AI-specific compute do you have available today? What is the process to provision more?**

Critical for fine-tuning and on-prem inference. Long provisioning time = cloud-first strategy.

---

#### Integration & Connectivity

**Q6: List your top 10 enterprise systems by business criticality. For each: is there an API? Is the data clean? Who owns it?**

Maps the MCP server build list. Systems without APIs require integration work before AI.

---

**Q7: How do you currently handle real-time vs batch data processing?**

Streaming capability is required for real-time agent memory and event-driven architectures.

---

**Q8: What is your current state of master data management? Is there a single source of truth for key entities (customer, product, employee)?**

MDM gaps create AI hallucinations about core business entities.

---

**Q9: Describe your current authentication and authorisation architecture. Is SSO in place? How are service-to-service credentials managed?**

Agent identity management requires mature IAM. Missing = security architecture design required.

---

**Q10: What are the top 3 technical debts that you believe will most constrain an AI deployment in the next 12 months?**

The architects know where the bodies are buried. This question gives them permission to tell you.

---

#### Security & Compliance

**Q11: What is your data classification policy? How is PII identified, tagged, and controlled across systems?**

PII in LLM inputs = compliance violation. Must understand before any AI deployment.

---

**Q12: What would prevent you from sending business data to an external LLM API? Is there a whitelist process?**

Identifies data residency and sovereignty constraints early.

---

**Q13: Describe your current security incident response process. Have you run an AI-specific red-team exercise?**

AI-specific threats (prompt injection, data exfiltration via agents) require distinct IR plans.

---

### Data & Analytics Discovery (25 Questions)

**Use for:** CDO, Head of Data, Data Engineering Lead, Analytics Manager  
**Duration:** 60 minutes  
**Goal:** Understand true data quality, accessibility, and readiness for AI workloads. Data teams know the truth. Create psychological safety for candour.

#### Data Quality Reality Check

**Q1: If I asked you for 12 months of clean, labelled training data for a customer churn prediction model, what would you give me and in what timeframe?**

The most honest signal of data readiness. Their confidence (or panic) tells you everything.

---

**Q2: What percentage of your data pipelines failed last month? What was the mean time to detect and resolve?**

Pipeline reliability is a prerequisite for production AI that depends on fresh data.

---

**Q3: Describe the worst data quality issue currently affecting business decisions. Why hasn't it been fixed?**

Reveals systemic issues and organisational dynamics around data ownership.

---

**Q4: If you had to bet your job on the accuracy of your customer data, which fields would you stake it on and which wouldn't you touch?**

Field-level quality assessment done the honest way.

---

**Q5: What data does your company collect but never use? Why?**

Often reveals the richest AI training datasets — the ones no one thinks about.

---

#### Data Architecture & Access

**Q6: Walk me through how a business analyst accesses data today. From question to answer, how long does it take?**

Time-to-insight reveals data accessibility. >1 day = AI will face the same friction.

---

**Q7: Do you have a data catalogue? Who uses it and how often?**

Unused catalogues are as bad as no catalogue — signals cultural disconnect between DE and users.

---

**Q8: How many data platforms are you running in parallel? (Snowflake, Databricks, Redshift, BigQuery, legacy DW, etc.)**

Platform sprawl = integration complexity. More than 3 = consolidation conversation.

---

**Q9: What is your policy on using production data for AI model training?**

No policy = risk. Too restrictive = data access bottleneck for fine-tuning.

---

**Q10: How do you currently handle schema changes in upstream systems breaking downstream pipelines?**

Schema drift management = pipeline maturity signal. "We find out from broken dashboards" = not mature.

---

### Business Unit Leader Discovery (20 Questions)

**Use for:** VP Sales, Head of Operations, CMO, Head of Customer Service, CFO  
**Duration:** 30–45 minutes  
**Goal:** Find the real pain, identify the champion, and understand workflow dynamics. Business leaders describe symptoms; your job is to diagnose the underlying cause and map it to an AI solution.

#### Pain Discovery

**Q1: Walk me through your team's most time-consuming weekly task that requires the most senior/expensive people. What makes it hard to delegate or automate?**

The answer to this question is often your first use case.

---

**Q2: If your team had 20% more capacity starting tomorrow, what would you do with it?**

Reveals priorities and opportunities. Also tests imagination — can they think beyond current constraints?

---

**Q3: What decisions does your team make repeatedly that are driven by similar data patterns each time?**

Repetitive decision-making is a classic ML/AI opportunity.

---

**Q4: Where do errors or rework happen most frequently in your team's workflows?**

Error hotspots = AI quality control opportunity.

---

**Q5: What information do you wish you had that you currently can't get, or can't get fast enough?**

Information gaps often map directly to RAG or analytics AI use cases.

---

#### Adoption Readiness

**Q6: How has your team reacted to new technology changes in the past? What made adoptions succeed or fail?**

Change readiness pattern matching. "We never adopt anything" = cultural challenge.

---

**Q7: What would make your team trust an AI recommendation enough to act on it without double-checking?**

Trust calibration. Builds the specification for the explainability and validation features.

---

**Q8: Which members of your team do you think would be the most enthusiastic early adopters of AI tools?**

Your future AI Champions. Get their names — involve them in the pilot.

---

**Q9: What would a failure look like in the first 90 days of an AI system in your team? What would the impact be?**

Risk calibration and success metric definition by stealth.

---

**Q10: If the AI tool worked exactly as you hope, what would your team's work look like differently in 12 months?**

Future state vision. Check for alignment with the executive vision you heard earlier.

---

### Security & Compliance Discovery (20 Questions)

**Use for:** CISO, General Counsel, Chief Compliance Officer, DPO  
**Duration:** 45–60 minutes  
**Goal:** Identify hard constraints before architecture is designed. These are veto-holders. Their concerns shape the architecture — never fight them, design for them.

**Q1: What are your data residency requirements? Can business data leave your jurisdiction for processing?**

Determines cloud provider and API strategy.

---

**Q2: What regulatory frameworks govern your AI deployments? (EU AI Act, HIPAA, SOX, GDPR, FCA, FFIEC, etc.)**

Compliance landscape determines governance architecture.

---

**Q3: Have you conducted a Data Protection Impact Assessment (DPIA) for any AI system?**

DPIA maturity signals GDPR readiness for AI.

---

**Q4: What is your current process for approving new SaaS vendors with access to company data? How long does it take?**

Vendor approval timeline affects AI deployment schedule significantly.

---

**Q5: Have you run any AI-specific threat modelling exercises? Are you aware of prompt injection and model inversion attacks?**

AI-specific security awareness. Most security teams are not yet trained on AI attack surfaces.

---

**Q6: What would be your response if an AI system produced a discriminatory output that affected a customer and was covered by media?**

Incident response readiness and reputational risk management.

---

**Q7: What contractual guarantees would you require from an AI vendor regarding data handling, model training, and breach notification?**

Vendor requirements that need to be addressed in solution design (BAA, DPA, etc.)

---

**Q8: Are there any pending regulatory examinations or audits in the next 12 months that would affect our timeline?**

Hidden timeline constraints. Regulatory exams often halt AI deployments.

---

### Change Management Discovery (15 Questions)

**Use for:** CHRO, Head of L&D, Change Management Lead, Union Representatives  
**Duration:** 30–45 minutes  
**Goal:** Understand human dynamics. Technical failure rate: 20%. Organisational failure rate: 60%. This interview shapes your entire workforce enablement strategy.

**Q1: How have employees typically heard about this AI transformation programme so far? What is the informal narrative?**

Informal narratives are more powerful than official ones. Know them before they know you.

---

**Q2: Which employee groups are most concerned about AI, and what specifically are they afraid of?**

Fear mapping. Each fear needs a specific communication and design response.

---

**Q3: What has been your most successful large-scale change programme in the last 5 years? What made it work?**

Successful patterns are reusable. Build on what worked before.

---

**Q4: What change programmes have failed, and what was the cause?**

Failure patterns to avoid. Often reveals political landmines.

---

**Q5: Is there a formal AI reskilling budget? Who approves it?**

Budget reveals commitment. No budget = aspirational programme with no teeth.

---

**Q6: How do you measure employee adoption of new technology? What metrics do you track?**

Adoption measurement maturity. "We don't measure it" = biggest gap.

---

**Q7: Are there any union agreements or works council requirements that affect how we implement AI that changes job roles?**

Employment law constraints vary significantly. Must know before programme design.

---

**Q8: Who are the informal influencers in the organisation — the people others look to when deciding whether to trust a new initiative?**

Your AI Champions. These are the people you need on your side.

---

---

*This toolkit is Part 1 of 2. Part 2 contains Stakeholder Interview Templates, Use Case Prioritisation Framework, FAQ Bank, Phase-Gated Checklists, and Templates & Deliverable Frameworks.*

*Adapt all templates to your client's industry, vocabulary, and risk profile. The structure is more important than the exact wording. Update questions and checklists as your engagement experience grows — the best consultants don't use templates mechanically; they use them as a foundation for the judgment that only experience can provide.*
