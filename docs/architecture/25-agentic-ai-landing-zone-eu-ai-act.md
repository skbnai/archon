---
title: "Agentic AI Landing Zone: EU AI Act Compliance (Digital Omnibus Update — July 2026)"
date_created: 2026-07-09
last_reviewed: 2026-07-10
status: current
source_type: native-md
doc_type: reference-architecture
domain: architecture
topic_id: agentic-ai-landing-zone-eu-ai-act
supersedes: ["docs/ai-foundations/agentic_ai_landing_zone_eu_ai_act.md"]
tags: ["ai-foundations"]
covers_version: "as of 2026-07-10"
---

# Agentic AI Landing Zone: EU AI Act Compliance (Digital Omnibus Update — July 2026)

*This guide de-risks compliance and avoids €35M penalties.*

> **⚖️ Digital Omnibus update (final Council approval 29 June 2026).** The AI Act simplification package changed the deadlines this guide was originally written against:
> - **Annex III high-risk obligations: deferred from 2 Aug 2026 → 2 December 2027**
> - **Annex I (AI embedded in regulated products): deferred from 2 Aug 2027 → 2 August 2028**
> - **Article 50 transparency obligations: UNCHANGED — in force from 2 August 2026**
> - **Article 5 prohibitions (social scoring etc.): already in force since 2 February 2025**
>
> The deferral buys time for high-risk conformity work — it does not remove it, and transparency duties bite now.

---

## CRITICAL TIMELINE

**Current Status (July 2026):**

- **Article 5 prohibitions:** IN FORCE (since Feb 2, 2025)
- **Article 50 transparency obligations:** IN FORCE from Aug 2, 2026
- **High-risk systems (Annex III):** deadline Dec 2, 2027 (Digital Omnibus deferral)
- **High-risk embedded in Annex I products:** deadline Aug 2, 2028
- **Penalties:** €35M or 7% global turnover

**Compliance Roadmap:**

```mermaid
graph LR
    A["Now<br/>(Jul 2026)"] -->|"Agent inventory<br/>+ risk classification"| B["Q3 2026"]
    B -->|"Article 50<br/>transparency<br/>compliance"| C["Q4 2026"]
    C -->|"High-risk gap<br/>assessment +<br/>roadmap"| D["2027"]
    D -->|"High-risk<br/>remediation &<br/>audit readiness"| E["Dec 2, 2027"]
    E -->|"Ongoing"| F["Operations"]
    
    style A fill:#fff4e6
    style B fill:#ffe0cc
    style C fill:#ffccb3
    style D fill:#ffb399
    style E fill:#ff9980
    style F fill:#f0f0f0
```

**Compliance Roadmap by Deadline:**
1. **Now (July 2026):** Agent inventory + risk classification
2. **Q3 2026:** Article 50 transparency compliance (chatbot disclosure, AI-content labeling)
3. **Q4 2026:** High-risk gap assessment + conformity roadmap
4. **2027:** High-risk remediation, documentation, audit readiness (before Dec 2, 2027)
5. **Ongoing:** Operational compliance

---

## PART 1: AGENT CLASSIFICATION (Days 1-3)

### Step 1.1: Inventory All Agents

**Action:** List every AI agent your organization has or is developing.

**Discovery Questions:**

*Where are agents running?*
- Production systems (web, mobile, backend)
- Internal tools (employee productivity)
- Experimental/pilot projects
- Shadow systems (teams built without IT approval)
- Proof-of-concepts (not yet deployed)

*Who knows about them?*
- Official IT/AI team
- Business units (Finance, HR, Operations)
- Skunkworks/innovation teams
- Individual engineers (personal projects)
- External agencies (outsourced development)

*What are they doing?*
- Customer-facing (customer service, support)
- Business-critical (approvals, decisions, transactions)
- Back-office (analytics, reporting)
- Monitoring (compliance, fraud detection)
- Administrative (scheduling, notifications)

**Agent Inventory Template:**

```yaml
agents:
  - id: "cust-service-v2.4"
    name: "Customer Service Chatbot"
    status: "production"
    owner: "Customer Operations"
    users: "100K+ customers/month"

  - id: "loan-approval-v1.0"
    name: "Loan Decisioning Agent"
    status: "staging"
    owner: "Credit Risk"
    users: "Processing ~500 loans/day"

  - id: "compliance-monitor-v1"
    name: "Regulatory Compliance Monitor"
    status: "production"
    owner: "Compliance & Risk"
    users: "Internal (monitoring ~200 transactions/hour)"

  - id: "research-assistant-pilot"
    name: "Research & Market Intelligence"
    status: "pilot"
    owner: "Strategy Team"
    users: "Internal (10 users in pilot)"

  # ... continue for all agents
```

**Timeline:** 1-2 days (depends on organization size)

---

### Step 1.2: Classify Each Agent

**EU AI Act Risk Framework:**

| Risk Level | Definition | Requirements | Examples |
| ----------- | ----------- | -------------- | ---------- |
| **UNACCEPTABLE** | Prohibited systems | ❌ BANNED (remove immediately) | Social credit scoring, manipulation, subliminal techniques |
| **HIGH-RISK** (Annex III) | Critical systems needing conformity assessment | ⚠️ MUST COMPLY by Dec 2, 2027 | Lending decisions, employment screening, law enforcement tools, critical infrastructure |
| **LIMITED-RISK** | Transparency required | ⚠️ MUST DISCLOSE by Aug 2, 2026 | Chatbots, content generation, recommendation systems |
| **MINIMAL-RISK** | No specific requirements | ✅ No immediate action | Spam filters, autocorrect, simple analytics |

### Classification Decision Tree

**Agent Risk Classification Flowchart:**

```mermaid
flowchart TD
    A["Does your agent make<br/>decisions affecting<br/>fundamental rights?"]
    
    A -->|YES| B["HIGH-RISK<br/>Annex III"]
    B -->|Examples:| C["Employment, Credit/Finance,<br/>Law Enforcement, Border Control,<br/>Infrastructure, Migration/Asylum,<br/>Justice System"]
    
    A -->|NO| D["Does your agent interact<br/>with humans/users?"]
    D -->|YES| E["LIMITED-RISK<br/>Transparency Required"]
    E -->|Examples:| F["Chatbots, Recommendations,<br/>Content Generation,<br/>Virtual Assistants"]
    
    D -->|NO| G["MINIMAL-RISK<br/>No Special Requirements"]
    G -->|Examples:| H["Spam Filters,<br/>Internal Analytics,<br/>Log Analysis"]
    
    style B fill:#ffcccc
    style E fill:#ffffcc
    style G fill:#ccffcc
```

### Classification Template

Fill this out for **EACH agent**:

```yaml
classification:
  agent_id: "loan-approval-v1.0"
  agent_name: "Loan Decisioning Agent"

  risk_assessment:
    # Does it affect fundamental rights?
    affects_fundamental_rights: true
    # Which rights? (employment, credit, justice, migration, safety, etc.)
    rights_affected: ["credit_access", "financial_wellbeing"]

    # Is it a use case in Annex III?
    in_annex_iii: true
    annex_iii_category: "Credit provision (4.1)"

    # Final classification
    risk_level: "HIGH-RISK"
    requires_conformity_assessment: true
    compliance_deadline: "2026-08-02"

  decision_impact:
    # How many people affected?
    users_affected: 500  # loans/day × 250 days/year

    # What are the consequences of wrong decisions?
    consequences_of_error: "Loan rejection (financial harm), unfair treatment"

    # Can user appeal or understand why?
    explainability_required: true
    appeals_process_required: true

  remediation:
    # Can you fix this before the Dec 2, 2027 high-risk deadline?
    compliance_possible: true
    estimated_effort: "3-4 weeks"
    priority: "CRITICAL"
```

**Timeline:** 1 day (mark all high-risk agents)

---

## PART 2: HIGH-RISK AGENT AUDIT (Days 4-10)

### Step 2.1: For Each High-Risk Agent, Complete Audit

**High-Risk Requirements (EU AI Act, Article 8-51):**

| # | Requirement | Status | Evidence Needed |
|---|---|---|---|
| 1 | Risk Management System | [ ] | Documentation |
| 2 | Data Governance & Quality | [ ] | Data collection logs |
| 3 | Technical Documentation | [ ] | Architecture, code, models |
| 4 | Record-Keeping | [ ] | Audit logs, decision logs |
| 5 | Transparency & Information | [ ] | User-facing disclosures |
| 6 | Human Oversight & Appeal | [ ] | Process documentation |
| 7 | Robustness & Accuracy | [ ] | Test results, metrics |
| 8 | Incident Response Plan | [ ] | Runbook, escalation |

### Step 2.2: Risk Management System

**What is it?** A documented process showing how you identify, assess, and mitigate risks.

**Template:**

```markdown
# Risk Management System for [Agent Name]

## 1. Risk Identification
### Known Risks:
- **Risk 1**: Model bias against [protected class]
  - Likelihood: Medium
  - Impact: High (loan rejections)
  - Mitigation: [What you're doing]

- **Risk 2**: Hallucinated justifications (model invents reasons for decisions)
  - Likelihood: Low
  - Impact: Medium (poor customer experience)
  - Mitigation: [What you're doing]

- **Risk 3**: Adversarial inputs (someone tricks agent into wrong decision)
  - Likelihood: Low
  - Impact: High (fraud)
  - Mitigation: [What you're doing]

### How you identified risks:
- Threat modeling session (date)
- Expert interviews (CISO, compliance, business stakeholders)
- Literature review (known LLM/AI risks)
- Historical incidents (if any)

## 2. Risk Assessment
For each risk:
- Probability (Low/Medium/High)
- Severity (Low/Medium/High)
- Risk Score = Probability × Severity
- Tolerance Level (acceptable?)

## 3. Risk Mitigation
For each HIGH-risk item:
- Technical controls (code, model, data)
- Organizational controls (policies, processes)
- Monitoring (how to detect when mitigation fails)
- Response (what to do if risk materializes)

Example Mitigation:
Risk: Bias against women in loan decisions
- Technical: Debiasing at training time + post-hoc fairness checks
- Organizational: Quarterly bias audits, mandatory accuracy testing
- Monitoring: Track approval rates by gender (daily dashboard)
- Response: If disparity > 5%, escalate to Chief Risk Officer

## 4. Ongoing Monitoring
- Frequency: Daily (for production agent)
- Metrics: Accuracy, fairness, drift detection
- Escalation: If any metric out of bounds
- Review: Quarterly risk reassessment
```

### Step 2.3: Data Governance & Quality

**What is it?** Evidence that your training/operational data is fit for purpose.

**Requirements:**

```
✓ Data collection documented (where did data come from?)
✓ Data quality checked (is it accurate, complete, representative?)
✓ Bias assessment (does data reflect historical discrimination?)
✓ Privacy controls (is sensitive data protected?)
✓ Data retention (how long do you keep data?)
```

**Documentation Template:**

```yaml
data_governance:
  agent: "loan-approval-v1.0"

  training_data:
    source: "Historical loan decisions (2020-2025)"
    volume: "50,000 approved loans + 30,000 rejected loans"

    quality_assurance:
      completeness: "99.2% (0.8% missing fields)"
      accuracy: "Audited by compliance team (spot-check 500 records)"
      timeliness: "Data refreshed monthly"

    bias_assessment:
      protected_classes_checked: ["gender", "age", "race", "disability"]
      disparate_impact_test: "Passed (approval rate difference < 5%)"
      mitigation: "Removed proxy features (zip code, name) that correlate with protected class"

    privacy_controls:
      pii_handling: "Social Security numbers encrypted at rest, masked in logs"
      data_minimization: "Only features required for prediction"
      retention: "Deleted after 7 years (GDPR compliance)"

  operational_data:
    # What data does agent see in production?
    sources:
      - loan_application_db
      - credit_score_api
      - income_verification_service

    freshness: "Real-time (within 5 minutes)"
    validation: "Automated schema validation before inference"
    pii_protection: "Customer SSN masked, only last 4 digits used"
```

### Step 2.4: Technical Documentation

**What is it?** Detailed description of how your system works.

**Checklist:**

- **System Architecture Diagram**
  - Components (agent, model, databases, APIs)
  - Data flows
  - Decision points

- **Model Card**
  - Model name, version, last update
  - Intended use (what decisions?)
  - Training data (what? how much?)
  - Performance metrics (accuracy by subgroup)
  - Known limitations & failure modes
  - Bias testing results

- **Decision Logic Documentation**
  - Input requirements
  - Processing steps
  - Policy/rule constraints
  - Output format & explanations
  - Escalation criteria (when to send to human)

- **API Specifications**
  - Request format
  - Response format
  - Error codes
  - Rate limits

- **Code Quality Documentation**
  - Static analysis results
  - Security scanning results
  - Test coverage (unit, integration, end-to-end)
  - Known vulnerabilities (and fixes)

### Step 2.5: Record-Keeping & Audit Logs

**What is it?** Immutable record of every decision and rationale.

**Requirements:**

For each decision made by agent, record:
- Timestamp
- Input data (what did agent see?)
- Agent ID & version
- Decision made
- Confidence/probability
- Explanation/reasoning (why this decision?)
- User identity (who requested?)
- Data sources consulted
- Outcome (if known: was decision correct?)

Audit Log Must:
- Be immutable (can't be edited after creation)
- Be cryptographically signed (tamper detection)
- Be retained for 7 years (GDPR requirement)
- Be accessible to regulators/auditors
- Be queryable (can find decisions affecting specific person)

**Implementation Example:**

```json
{
  "timestamp": "2026-07-09T14:30:15Z",
  "audit_log_id": "LOG-2026-0847201",

  "input": {
    "loan_amount": 250000,
    "credit_score": 720,
    "income": 95000,
    "employment_years": 8,
    "debt_to_income": 0.28
  },

  "agent": {
    "id": "loan-approval-v1.0",
    "version": "1.2.3",
    "model": "claude-opus-4-8"
  },

  "decision": {
    "recommendation": "APPROVE",
    "approved_amount": 250000,
    "approved_rate": 4.25,
    "confidence": 0.94,
    "reasoning": "Strong credit profile, stable employment, acceptable debt ratio"
  },

  "policy_check": {
    "applied_policies": ["lending-policy-v2.1", "fair-lending-policy-v3.0"],
    "policy_satisfied": true,
    "constraints": "No issues detected"
  },

  "human_review": {
    "required": false,
    "status": "N/A"
  },

  "user_context": {
    "user_id": "advisor-456",
    "organization": "Wealth Management Division"
  },

  "signature": "sha256:abc123...", // Cryptographic signature
  "retention_until": "2033-07-09"  // 7-year retention
}
```

**Timeline:** 3-5 days (most effort)

---

## PART 3: TRANSPARENCY OBLIGATIONS (Days 11-18)

### Article 50: Transparency Requirements (IN FORCE from Aug 2, 2026 — unchanged by the Omnibus)

**What you must do:** Inform users when they're interacting with AI.

### For Each Agent, Implement Disclosure

**Option A: Chatbot/Conversational AI**

User sees at start of conversation:

> 🤖 **You're talking to an AI Assistant**
>
> This is an AI-powered customer service agent. While I aim to help, I may make mistakes.
>
> For complex issues, you can ask to speak with a human representative.
>
> **[Talk to human] [Continue]**

**Option B: Automated Decision System**

User sees after decision:

> ⚠️ **This decision was made by AI**
>
> Your loan application was decided using automated decision-making.
>
> **Decision:** APPROVED for $250,000 at 4.25% APR
>
> **Reason:** Strong credit profile
>
> Want to understand this decision?
>
> **[Request explanation] [Appeal]**

**Option C: Behind-the-Scenes AI**

Email to user:

> **Subject:** Your Support Ticket Response
>
> Hello,
>
> Your support ticket was initially reviewed by our AI-assisted system to categorize your issue and prioritize it for our team.
>
> Your actual response came from a human support specialist.
>
> Learn more: [Company AI Disclosure Policy]

### Disclosure Requirements Checklist

For each agent, ensure users see:

```
✓ Clear statement: "This decision was made by AI"
✓ What AI did: "Analyzed your application to determine eligibility"
✓ Limitations: "AI can make mistakes; not perfect"
✓ Human option: "You can request review by a human"
✓ Appeal process: "You can appeal this decision"
✓ Privacy: "Your data is protected [link to privacy policy]"
✓ Contact: "Questions? Contact [support email]"
```

**Timeline:** 2-3 days (website/app changes)

---

## PART 4: HUMAN OVERSIGHT & APPEALS (Days 11-18)

### Requirement: Humans Must Review High-Risk Decisions

**When is human review required?**

**When is human review required?**

Always:
- First-time user (new customer)
- High-value decisions (> $100K)
- Refusal/rejection decisions (deny loan, no hire)
- Complaint/appeal requests

Sometimes:
- Low confidence scores (&lt; 70%)
- Unusual patterns detected
- Customer explicitly requests human review

Never (if all conditions met):
- Routine approval, returning customer, low-risk

### Human Review SLA

**Template — HIGH-RISK AGENT: Loan Approval**

Human Review SLA:
- First-time decisions: &lt; 24 hours
- Appeals/complaints: &lt; 48 hours
- Escalations: &lt; 4 hours
- Critical cases: &lt; 1 hour

Process:
1. Agent makes decision + confidence score
2. If confidence &lt; 75%: Queue for human review
3. Human reviews: Input data, decision, reasoning
4. Human decides: Approve, modify, or reject agent decision
5. Final decision made by human (agent is input, not authority)
6. Document: Why human agreed/disagreed with agent

### Appeals Process Documentation

**What you need:**

```markdown
# Appeals Process for [Agent Name]

## User Rights:
1. Right to explanation (why was I rejected?)
2. Right to appeal (I disagree with this decision)
3. Right to human review (I want a human to reconsider)
4. Right to know (what data was used?)

## How to Appeal:
1. Click "Appeal this decision" in notification
2. Provide reason for appeal
3. Submit supporting documents
4. AI review team receives appeal
5. Human decision-maker reviews within SLA
6. You receive explanation of human's decision

## Typical Appeal Timeline:
- Day 1: You submit appeal
- Days 2-3: Human review
- Day 4: You receive decision
- Day 5+: If still disagreed, escalate to executive review

## Success Rate:
- ~15% of appeals result in decision reversal
- [Link to historical appeals data]
```

**Timeline:** 2 days (process + website)

---

## PART 5: CONTINUOUS MONITORING (Days 19-24)

### Set Up Daily Compliance Checks

**Dashboard Template — COMPLIANCE MONITORING DASHBOARD**

Updated: 2026-07-09 16:00 UTC

**Agent: loan-approval-v1.0**
- Status: ✅ IN COMPLIANCE
- Last audit: 2026-07-08
- Next audit: 2026-07-22 (bi-weekly)

**Daily Checks (Last 24 hours):**
- Decisions made: 487
- Human reviews triggered: 73 (15%)
  - Human reversals: 8 (11% of reviews)
- Appeals received: 2
- Audit logs created: 487 (100% coverage)
- Audit logs signed: 487 ✓

**Monthly Metrics:**
- Bias audit (approval rate by gender): ✓ PASS
  - Men: 78% approval
  - Women: 76% approval
  - Difference: 2% (within 5% threshold)
- Accuracy (vs. human reviewers): ✓ PASS
  - Agent-human agreement: 94%
  - Target: > 90%
- Privacy (PII incidents): ✓ PASS
  - Incidents: 0

**Compliance Items:**
- Risk Management System: ✓ Documented
- Data Governance: ✓ Documented
- Technical Documentation: ✓ Current
- Human Oversight: ✓ Operational
- Transparency Disclosure: ✓ Live
- Appeals Process: ✓ Live
- Audit Logs: ✓ Immutable, signed
- Incident Response: ✓ Tested

**Alerts:**
- None currently

**Next Actions:**
- Monthly bias audit (scheduled 2026-07-15)
- Quarterly risk reassessment (scheduled 2026-10-09)
- Annual external audit (scheduled 2026-12-15)

**Timeline:** 3 days (dashboard setup)

---

## AUDIT READINESS CHECKLIST

**Print this. Check off as you complete each item.**

### Before the deadlines (Art. 50 transparency: Aug 2, 2026 · Annex III high-risk: Dec 2, 2027)

### Agent Inventory & Classification
- [ ] List all agents (production, staging, pilots, shadow)
  - [ ] For each: document purpose, users, scope

### High-Risk Agent Remediation (For each HIGH-RISK agent)
- [ ] Risk Management System documented
- [ ] Data Governance & Quality documented
- [ ] Technical Documentation completed
- [ ] Model Card completed
- [ ] Decision Logic documented
- [ ] Audit log system operational
  - [ ] Logs immutable & cryptographically signed
  - [ ] 7-year retention configured
  - [ ] Access controls for regulators/auditors
- [ ] Bias testing completed & documented
- [ ] Fairness testing completed & documented
- [ ] Accuracy metrics documented

### Transparency Obligations (ALL agents)
- [ ] Disclosure language reviewed by Legal
- [ ] Disclosure implemented on website/app
- [ ] User-facing explanations tested
- [ ] Privacy policy updated
- [ ] FAQs created

### Human Oversight (HIGH-RISK agents)
- [ ] Appeal process defined & documented
- [ ] Human review workflow established
- [ ] SLAs set (review time, decision time)
- [ ] Training for human reviewers completed
- [ ] Appeal system tested with sample cases
- [ ] Documentation published to users

### Incident Response (ALL agents)
- [ ] Incident response plan written
- [ ] Escalation procedure defined
- [ ] Emergency contact list created
- [ ] Incident log template prepared
- [ ] Team training scheduled

### Compliance Monitoring
- [ ] Daily compliance dashboard live
- [ ] Bias metrics tracked daily
- [ ] Accuracy metrics tracked daily
- [ ] Alert thresholds configured
- [ ] Weekly compliance report scheduled

### Regulatory Readiness
- [ ] All documentation centralized
- [ ] Organized by: Agent → Requirement → Evidence
- [ ] Legal review of all documentation
- [ ] Executive sign-off obtained
- [ ] Audit team briefing held
- [ ] Public-facing "AI Governance" page created

---

## REAL-WORLD SCENARIOS

### Scenario 1: HIGH-RISK Agent (Loan Approval)

**Your Agent:** Loan decisioning (approves/rejects loans)
**EU AI Act Classification:** HIGH-RISK (Annex III)
**Compliance Deadline:** December 2, 2027 (Digital Omnibus deferral)

**What you MUST have:**
- Risk management system (documented risks + mitigations)
- Data governance (training data quality, bias testing)
- Technical documentation (how system works)
- Audit logs (every decision + reasoning + signature)
- Transparency (users know AI made decision)
- Human oversight (human can review/override)
- Appeals process (users can request review)
- Bias monitoring (daily fairness checks)

**If you DON'T have all 8 items by Dec 2, 2027:**
- System cannot be deployed/operated
- Regulator can fine you €35M or 7% turnover
- Potential criminal liability for executives

**Action Plan:**
- Days 1-3: Document risk management system
- Days 4-7: Complete data governance audit
- Days 8-11: Finish technical documentation
- Days 12-14: Implement audit logging
- Days 15-18: Add transparency + human oversight
- Days 19-24: Monitor + audit readiness
- Day 25+: Ongoing compliance

### Scenario 2: LIMITED-RISK Agent (Chatbot)

**Your Agent:** Customer service chatbot
**EU AI Act Classification:** LIMITED-RISK (Article 50 — unchanged by the Omnibus)
**Compliance Deadline:** August 2, 2026 (in force)

**What you MUST have:**
- Transparency (users know they're talking to AI)
- Privacy policy (how you use their data)
- Disclosure of limitations ("I can make mistakes")

**What you DON'T need (unlike high-risk):**
- Full risk management system (simpler)
- Human appeal process (no decisions being made)
- Audit logs (not required)
- Bias audits (lower stakes)

**Action Plan:**
- Days 1-2: Add disclosure to chat interface
- Days 3-4: Update privacy policy
- Days 5+: Monitor for issues

### Scenario 3: UNACCEPTABLE Agent (Social Scoring)

**Your Agent:** Scores customers on "trustworthiness" for credit
**EU AI Act Classification:** UNACCEPTABLE (Article 5)
**Compliance Deadline:** ALREADY IN FORCE (since February 2, 2025)

**What you MUST do:**
- STOP using this system immediately
- REMOVE it from production
- NOTIFY affected customers
- DELETE all score data

**Why:**
- EU AI Act prohibits "social scoring"
- This violates human dignity
- Penalties are criminal + €35M fine
- No amount of documentation makes this legal

**Action Plan:**
- Day 1: Executive decision to discontinue
- Day 2-3: Plan migration to alternative system
- Day 4-7: Notify customers affected
- Day 8-14: Delete personal data
- Day 15+: Audit trail to prove deletion

---

## YOUR ORG: COMPLIANCE ACTION PLAN TEMPLATE

**Fill this in and execute:**

**EU AI Act Compliance Plan Template — [YOUR ORGANIZATION]**

### Inventory (Complete by July 11)

**Agent Count by Risk Level:**
- Unacceptable: [ ] (must discontinue immediately)
- High-Risk: [ ] (conformity assessment required)
- Limited-Risk: [ ] (transparency required)
- Minimal-Risk: [ ] (no immediate action)

**High-Risk Agents Requiring Conformity Assessment:**
- Agent 1: [name, owner, status]
- Agent 2: [name, owner, status]
- ...

### Compliance Status by Agent

For each high-risk agent:

**Agent Name:** _______________
- Risk Management System: [ ] In progress [ ] Complete
- Data Governance: [ ] In progress [ ] Complete
- Technical Docs: [ ] In progress [ ] Complete
- Audit Logs: [ ] In progress [ ] Complete
- Transparency: [ ] In progress [ ] Complete
- Human Oversight: [ ] In progress [ ] Complete
- Appeals Process: [ ] In progress [ ] Complete
- Target Completion: _____ (date)

### Week-by-Week Execution

**Week 1 (Jul 9-13): Classification & Inventory**
- [ ] All agents identified
- [ ] Risk levels assigned
- [ ] Executive steering meeting

**Week 2 (Jul 16-20): High-Risk Audit Starts**
- [ ] Risk management system drafted
- [ ] Data governance audit initiated
- [ ] Steering committee check-in

**Week 3 (Jul 23-27): Documentation & Implementation**
- [ ] Technical docs completed
- [ ] Audit log system operational
- [ ] Transparency deployed

**Week 4: Final Audit & Compliance Verification**
- [ ] All requirements checked
- [ ] Internal audit passed
- [ ] Regulatory readiness confirmed
- [ ] Deadline met (Art. 50: Aug 2, 2026 · Annex III: Dec 2, 2027) ✓

### Resources Allocated

- Team lead: [name]
- Legal counsel: [name]
- Technical team: [size]
- Budget: [amount]
- Timeline: [per deadline — Art. 50 now; Annex III by Dec 2, 2027]

### Risks & Mitigations

**Risk 1:** Insufficient resources
- Impact: Can't meet deadline
- Mitigation: [your plan]

**Risk 2:** High-risk agent in production, not compliant
- Impact: Legal liability + €35M fine
- Mitigation: [your plan]

**Risk 3:** Missing agents in inventory
- Impact: Regulator discovers undisclosed system
- Mitigation: [your plan]

---

## IF YOU MISS THE DEADLINE

**What happens August 3?**

1. **Article 50 Enforcement Begins**
   - Regulators can audit your systems
   - You must prove compliance within 14 days

2. **Potential Penalties**
   - €35M or 7% of annual global revenue (whichever is higher)
   - For large orgs: could be €500M+
   - Criminal liability for executives (France, Germany)

3. **Remediation Path**
   - Demonstrate good-faith effort (started before deadline)
   - Implement compliance plan within grace period
   - Regulators often give 30-90 day remediation window if you show effort

**Recommendation:**
> Even if you're not 100% done by Aug 2, have evidence that you started in good faith. A partial compliance plan with demonstrable progress is better than nothing.

---

## RESOURCES & CONTACTS

### EU AI Act Official Resources

- EU AI Act Text: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32023R1689
- NIST AI RMF Crosswalk: https://airc.nist.gov/
- Your country's competent authority (see table below)

### Competent Authorities by Country

| Country | Authority | Contact |
| --------- | ----------- | --------- |
| **Germany** | Bundesamt für Arbeit und Soziales (BAS) | [contact] |
| **France** | CNIL (Data Protection) + others | [contact] |
| **Spain** | AEPD | [contact] |
| **Italy** | Garante per la Protezione dei Dati | [contact] |
| **Netherlands** | Autoriteit Persoonsgegevens | [contact] |
| **EU-wide** | European Commission | [contact] |

---

**Document Status:** CRITICAL - Action Required
**Deadlines:** Art. 50 transparency — Aug 2, 2026 (in force) · Annex III high-risk — Dec 2, 2027
**Next Update:** After classification complete
**Owner:** Chief Compliance Officer / General Counsel
