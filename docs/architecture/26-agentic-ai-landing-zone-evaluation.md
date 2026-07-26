---
title: "Agentic AI Landing Zone: Evaluation Framework"
date_created: 2026-07-09
last_reviewed: 2026-07-10
status: current
source_type: native-md
doc_type: reference-architecture
domain: architecture
topic_id: agentic-ai-landing-zone-evaluation
supersedes: ["docs/ai-foundations/agentic_ai_landing_zone_evaluation.md"]
tags: ["ai-foundations"]
covers_version: "as of 2026-07-10"
---

# Agentic AI Landing Zone: Evaluation Framework

*Production agentic AI requires systematic evaluation at every stage: design, staging, deployment, operations.*

---

## Why Evaluation Matters

**Production Reality (2026):**

- 92% of agentic AI failures happen post-deployment, not in testing
- Most orgs skip evaluation, deploy based on "feels right"
- Average cost of a production incident: $50K–$500K (via wrong decisions)
- Regulatory audits now require documented evaluation evidence (NIST AI RMF, ISO 42001, EU AI Act)

**Evaluation Strategy:**
Systematic testing across multiple dimensions (accuracy, safety, fairness, cost) at multiple stages (design, staging, canary, production).

---

## EVALUATION LIFECYCLE

```mermaid
graph TD
    A["STAGE 1: Design-Time<br/>(Pre-coding)<br/><br/>Does this idea work?<br/>Method: Manual reasoning,<br/>expert review"]
    
    A -->|Proceed| B["STAGE 2: Offline<br/>(Lab, synthetic data)<br/><br/>Works in controlled conditions?<br/>Method: Golden dataset,<br/>synthetic test cases"]
    
    B -->|Ready| C["STAGE 3: Staging<br/>(Pre-prod environment)<br/><br/>Works with real data?<br/>Method: Replay production data,<br/>simulated users"]
    
    C -->|Ready| D["STAGE 4: Canary<br/>(1-5% real traffic)<br/><br/>Works with real users?<br/>Method: Shadow mode,<br/>A/B testing"]
    
    D -->|Proceed| E["STAGE 5: Production<br/>(100% traffic)<br/><br/>Maintaining quality?<br/>Method: Continuous monitoring,<br/>anomaly detection"]
    
    E -->|Incident| F["STAGE 6: Forensic<br/>(Post-incident)<br/><br/>Root cause analysis &<br/>prevention planning"]
    
    F -->|Recurrence Fixed| E
    
    style A fill:#fff4e6
    style B fill:#ffe0cc
    style C fill:#ffccb3
    style D fill:#ffb399
    style E fill:#ff9980
    style F fill:#ffcccc
```

---

## GOLDEN DATASET: The Foundation

### What is a Golden Dataset?

**A curated collection of test cases** representing real scenarios that the agent must handle correctly.

**Golden Dataset: "Customer Service Agent v2.4"**

**Format:**
- Input: User request (e.g., "Can I return my order?")
- Context: Agent context (customer data, order info)
- Expected Output: Correct agent response (e.g., "Yes, you have 30 days")
- Success Criteria: How to judge if response is correct
- Metadata: Difficulty, category, business impact

**Example 1:**
- **ID:** CS-001
- **Category:** Happy Path
- **Difficulty:** Easy
- **Input:** "What's my order status?"
- **Context:** `{customer_id: 12345, order_id: 98765, status: "shipped"}`
- **Expected:** "Your order 98765 is currently shipped and will arrive by July 12"
- **Success:** Response mentions order ID, status, and ETA
- **Coverage:** Basic happy path ✓

**Example 2:**
- **ID:** CS-047
- **Category:** Edge Case / High Impact
- **Difficulty:** Hard
- **Input:** "I want to return my order"
- **Context:** `{customer_id: 12345, order_id: 98765, return_window_days: 5, days_purchased: 8, return_policy: "30 days for eligible items"}`
- **Expected:** "Unfortunately, your order is outside the 30-day return window. However, I can escalate this to our supervisor if you'd like."
- **Success:** 
  - Acknowledges return request ✓
  - Provides reason (outside window) ✓
  - Offers escalation path ✓
- **Coverage:** Policy boundary, escalation ✓

### Building a Golden Dataset

#### Step 1: Identify Scenarios

**Business Process Mapping:**

- Happy paths: What should normally happen? (70% of traffic)
- Edge cases: What unusual situations occur? (20%)
- Error cases: What goes wrong? (10%)
- Compliance cases: What scenarios require audit? (mandatory)

**Customer Service Agent Scenarios:**

Happy Path (70%):
- CS-001: Basic order status
- CS-002: Simple return request
- CS-003: Billing question

Edge Cases (20%):
- CS-047: Return outside window (policy boundary)
- CS-048: Multiple orders (ambiguous reference)
- CS-049: High-value order (escalation needed)

Error Cases (10%):
- CS-080: Invalid customer ID (defensive)
- CS-081: Malformed request (robustness)
- CS-082: Hostile/abusive input (safety)

Compliance (Mandatory):
- CS-200: GDPR deletion request
- CS-201: PII handling
- CS-202: Audit log completeness

#### Step 2: Collect Real Examples

**Data Sources:**
- Customer feedback / surveys (what users actually ask)
- Support team transcripts (real conversations)
- Known bugs / past incidents (don't repeat)
- Competitor benchmarks (what should we handle?)
- Regulatory requirements (compliance cases)

**Example Collection:**
- Audit past 1000 support tickets
- Identify top 50 distinct scenarios
- For each scenario: collect 3-5 real examples
- Total: ~200 test cases (good starting point)

#### Step 3: Annotate with Expected Outputs

**For Each Test Case:**
- What should the agent say/do? (expected output)
- Why is this the right response? (reasoning)
- How to judge if agent got it right? (success criteria)
- Who owns this test case? (for updates)

**Example Annotation:**

**ID:** CS-047
**Input:** "I want to return my order"

**Expected Response:**
"I'd be happy to help. Let me check your order. Your order was placed 8 days ago and qualifies for our standard 30-day return window. Here's how to process your return: [steps]. Would you like me to start a return now?"

**Success Criteria:**
- Identifies return request ✓
- Checks return window (8 days &lt; 30 days) ✓
- Confirms eligibility (true) ✓
- Provides next steps ✓
- Offers to proceed ✓
- No hallucinated policies ✓
- Tone is helpful, not defensive ✓

**Owner:** Customer_Service_Team
**Last Updated:** 2026-07-09

### Golden Dataset Maintenance

**Versioning:**
- v1.0: Initial 200 test cases (July 2025)
- v1.1: Added 50 edge cases from real failures (Oct 2025)
- v2.0: Reorganized by business process (Jan 2026)
- v2.1: Updated expected outputs for v2.3 model (May 2026)
- v2.4: Current (after recent incidents)

**Refresh Triggers:**
- After each major incident (add failing case)
- After model upgrade (validate compatibility)
- Quarterly (review coverage gaps)
- On business process changes (update scenarios)

**Size Targets:**
- Minimum: 50 test cases (small MVP)
- Recommended: 200-500 test cases
- Enterprise: 1000+ test cases (comprehensive)
- Rule: 20% of test cases should be edge/error cases

---

## OFFLINE EVALUATION: Lab Testing

### Evaluation Metrics Framework

#### Accuracy Metrics

**Task Success Rate**
- Definition: % of test cases where agent completes task correctly
- Formula: (successful_tasks / total_tasks) × 100
- Target: > 95%

Example:
- Total test cases: 200
- Passed: 195
- Success rate: 97.5% ✓
- Failed cases: 5 (need investigation)

**Semantic Similarity**
- Definition: How similar is agent response to expected output?
- Method: Embedding similarity (cosine distance)
- Range: 0.0 (completely different) to 1.0 (identical)
- Target: > 0.85

Use case: When multiple correct answers exist
- Expected: "Your order will arrive July 12"
- Agent response: "Delivery expected by July 12th"
- Similarity: 0.92 (close enough) ✓
- Pass or fail based on threshold

**Accuracy by Category**
Track success rate by test category:
- Happy path: 98% (simple cases)
- Edge cases: 92% (complex logic)
- Compliance: 100% (must be perfect)
- Error cases: 88% (defensive programming)
- Overall: 95%

#### Safety & Compliance Metrics

**Hallucination Rate**
- Definition: % of responses containing false or made-up information
- Target: &lt; 2%

Examples of hallucinations:
- "Your order will definitely ship today" (made up)
- "Our return window is 45 days" (policy says 30)
- "I personally reviewed your case" (agent is not human)
- Customer ID "12345" references person without verification (wrong identity)

Detection:
- Automated: Regular expressions (e.g., "definitely", "guarantee")
- Manual review: Human reads 10% of outputs
- User feedback: Flag "this is wrong" responses

**Policy Compliance**
- Definition: % of responses adhering to company policies
- Target: 100% for high-risk policies, 98% for low-risk

Policies checked:
- Return policy (window, conditions)
- Pricing (no unauthorized discounts)
- Data handling (no SSN sharing)
- Tone (professional, empathetic)
- Escalation (when required)
- Legal disclaimers (when needed)

**PII Handling**
- Definition: Agent correctly handles sensitive personal info
- Target: 100% compliance (zero violations)

Checks:
- Never exposes credit card numbers ✓
- Masks SSN in outputs ✓
- Doesn't share medical records with unauthorized agents ✓
- Logs PII access for audit ✓

**Escalation Detection**
- Definition: Agent correctly identifies when human is needed

Cases:
- High-value decision (refund > $500)
- Complaint from VIP customer
- Request outside agent authority
  - Angry/upset customer
  - Ambiguous situation

Target: > 95% detection rate

#### Quality Metrics

```yaml
Relevance:
  Definition: Is the response relevant to the user's request?
  Method: Human judges "yes/no" for 10% of test cases
  Target: > 98%

  Example bad relevance:
  User: "What's my order status?"
  Agent: "Here's general info about shipping..." (not specific)

Conciseness:
  Definition: Response length appropriate to complexity
  Target:
  - Simple query: < 100 tokens
  - Complex query: < 300 tokens
  - No unnecessary verbosity

Clarity:
  Definition: Can user understand the response?
  Method: Readability score, human review
  Target: Reading level ≤ 8th grade

Tone:
  Definition: Does response match brand voice?
  Check:
  - Professional but friendly ✓
  - Empathetic to customer frustration ✓
  - Not defensive or dismissive ✓
  - Appropriate for interaction (formal for legal, casual for chat)
  Target: > 95% tone appropriateness

#### Fairness Metrics

Demographic Parity:
  Definition: Agent treats different customer groups equally
  Measure:
  - Success rate for high-value vs. low-value customers
  - Response time for different regions
  - Escalation likelihood by customer segment
  - Tone/politeness varies by customer type? (should not)
  Target: No statistical difference (p > 0.05)

Bias Detection:
  Scenarios:
  - Does agent refuse request for customer of certain identity?
  - Does agent give different pricing for different names?
  - Does agent escalate more for certain customer types?
  - Does agent make stereotypical assumptions?

  Test:
  - Run same query with different customer profiles
  - Compare responses
  - Flag any unfair treatment

Calibration:
  Definition: Is agent confident when it should be, uncertain when needed?
  Measure: Confidence score alignment with actual accuracy
  - When agent says "I'm 90% sure": Is it actually correct 90% of time?
  - Target: Within 5% (90% confidence ≈ 85-95% actual accuracy)

### Offline Evaluation Workflow

**Run Evaluation:**
1. Load golden dataset (200 test cases)
2. For each test case:
   - Run agent with test input + context
   - Capture output
   - Compare against expected output (automated + manual)
   - Score: Pass/Fail + confidence

3. Aggregate results
   - Success rate: 195/200 = 97.5%
   - Hallucination rate: 2/200 = 1.0%
   - Compliance: 198/200 = 99%
   - Tone appropriateness: 198/200 = 99%

4. Identify failures
   - CS-047: Expected escalation, agent tried to handle
   - CS-082: Hostile input, agent responded defensively
   - CS-150: Ambiguous query, agent hallucinated

5. Decision:
   - If metrics ≥ targets: PASS → proceed to staging
   - If metrics < targets: FAIL → fix and re-run
   - If edge cases failing: ESCALATION → review with team

---

## STAGING EVALUATION: Pre-Production Validation

### Staging Deployment

**Staging Environment:**
- Production data (anonymized/redacted for compliance)
- Production infrastructure (same scale as prod, smaller)
- No real users (internal team only)
- Full monitoring/observability enabled
- Can be destroyed and recreated

**Deployment Strategy:**
- Deploy agent alongside current version
- Shadow mode: Agent runs alongside production agent but output not used
- Collect metrics for 24 hours
- Compare behavior
- Decision: Ready for canary or needs work?

### Shadow Mode Evaluation

**Shadow Mode:**
- User query comes in
- Current agent responds (returned to user)
- Test agent responds in parallel (not returned)
- Both responses logged and compared
- Cost: Double processing, no user impact

**Metrics Tracked:**
- Task success: Does test agent give same result?
- Latency: Is test agent faster/slower?
- Cost: Cost per call difference?
- Errors: Does test agent fail differently?
- Safety: Any concerning differences?

**Example Results (24 hours shadow):**
- Task alignment: 94.2% (mostly same responses)
- Latency delta: Test agent 15% slower (acceptable)
- Cost delta: Test agent 10% cheaper (due to better context compression)
- Errors: Test agent fails on 3 edge cases (need fixes)
- Safety: No hallucinations detected in shadow

---

## CANARY EVALUATION: Live Traffic (1-5%)

### Canary Deployment Metrics

**Canary Deployment:**
- Duration: 4 hours
- Traffic: 5% of requests (100 agents × 5% = 5 actual users)
- Rollback: Automatic if error rate > 5%
- Monitoring: Real-time alerts

**Key Metrics:**

Error Rate:
- Target: < 1%
- Current: 0.3%
- Status: ✓ Healthy

Task Success:
- Target: > 95%
- Current: 96.1%
- Status: ✓ Slightly better

Latency p95:
- Target: < 2000ms
- Current: 1,850ms
- Status: ✓ Within budget

Cost per request:
- Target: < $0.25
- Current: $0.23
- Status: ✓ Better than expected

User Satisfaction:
- Target: > 4.0 / 5.0
- Current: 4.1 / 5.0 (from feedback)
- Status: ✓ Positive

**Decision After 4 Hours:**
- All metrics healthy → PROCEED TO 100%
- One metric concerning → HOLD, investigate
- Any critical failure → ROLLBACK, fix

---

## PRODUCTION EVALUATION: Continuous Monitoring

### Production Monitoring Dashboard

**Real-Time Metrics (Updated Every Minute):**

Availability:
- Last 1 hour: 99.8%
- Last 24 hours: 99.7%
- Last 7 days: 99.5%
- Target: 99.5% ✓

Quality:
- Task success rate: 96.3%
- Customer satisfaction: 4.2 / 5.0
- Escalation rate: 14.2%
- Hallucination rate: 0.8%
- All within targets ✓

Cost:
- This hour: $142
- Today (MTD): $2,847 / $15,000 budget (19%)
- Projected month: $12,350
- On track ✓

**Alerts (if triggered):**
- 🚨 Error rate spiked: 5.2% (vs 0.5% baseline) → Action: Page on-call engineer
- ⚠️ Latency elevated: p95 = 2,100ms (vs 1,800ms baseline) → Action: Check MCP tool performance
- ℹ️ New error pattern detected (3 similar failures) → Action: Tag for next retrospective

### Regression Testing in Production

**Weekly Regression Test:**
- Every Monday at 2 AM (low-traffic window)
- Run 500 test cases from golden dataset
- Compare results against baseline (previous version)
- Generate report

**Report:**
- Baseline version: v2.3
- Current version: v2.4
- Tests passed: 490 / 500 (98%)
- Regression detected: 10 test cases now fail
  - All in new "high-value refund" logic
- Recommendation: Fix high-value refund handling
- Next test: Friday (after fixes)

---

## MULTI-DIMENSIONAL EVALUATION MATRIX

### Comprehensive Evaluation Plan

| Dimension | Offline | Staging | Canary | Production | Frequency |
|---|---|---|---|---|---|
| Accuracy | ✓ | ✓ | ✓ | ✓ | Weekly / Continuous |
| Safety | ✓ | ✓ | ✓ | ✓ | Daily / Continuous |
| Fairness | ✓ | ○ | ○ | ○ | Monthly |
| Cost | ✓ | ✓ | ✓ | ✓ | Hourly / Continuous |
| Latency | ✓ | ✓ | ✓ | ✓ | Minute / Continuous |
| Compliance | ✓ | ✓ | ○ | ✓ | Daily |
| User Feedback | ○ | ○ | ✓ | ✓ | Real-time / Continuous |

Legend: ✓ = Measured, ○ = Sampled/spot-check

---

## TODO: Evaluation Strategy for Your Organization

Before production deployment:

1. **Golden Dataset**: Build your first 100-200 test cases
2. **Evaluation Pipeline**: Automate offline testing in CI/CD
3. **Monitoring Dashboard**: Set up real-time metric tracking
4. **Regression Testing**: Weekly or bi-weekly baseline comparisons
5. **Incident Response**: Process for acting on evaluation failures
6. **Benchmarking**: Baseline current agent performance (if migrating legacy system)

---

**Related Documents:**

- AI Agent Evaluation Framework Guide
- Platform Layer: Certification Program

---

**Document Status:** DRAFT (July 2026)
**Owner:** Quality Assurance + Platform Engineering
**Audience:** Everyone deploying agents

## Related

- [Agentic AI Landing Zone Architecture](22-agentic-ai-landing-zone-architecture.md) — the architecture this evaluation framework validates.
- [Operations Hub](../operations/index.md) — the broader evaluation and benchmark catalog this domain-specific framework connects to.

