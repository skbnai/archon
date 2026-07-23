---
title: "AI Operating Processes: Rollout, Evaluation & Red Teaming"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-09-operating-processes-part2
maturity: practitioner
personas: [delivery-lead, qa-lead, security-lead]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes: []
tags: ["operating-processes", "rollout", "evaluation", "red-team", "testing", "safety"]
sources: []
pagination_prev: strategy/part-09-operating-processes
pagination_next: strategy/part-09-operating-processes-incident-response-rollback
---

# AI Operating Processes: Rollout, Evaluation & Red Teaming

Robust rollout, evaluation, and safety testing processes ensure AI systems perform as intended before and during production.

## Process 1: Evaluation & Acceptance

**Trigger:** AI system completed; ready for quality validation

**Inputs:** AI system (model, prompt, agent), golden dataset or test scenarios, evaluation metrics, acceptance thresholds

**Steps:**
1. Define evaluation criteria before testing (prevent bias toward desired results)
2. Select appropriate metrics based on use case (accuracy, F1, RAGAS for RAG, task completion for agents)
3. Create golden dataset or test scenarios (human-annotated ground truth)
4. Run automated evaluation suite
5. Conduct human evaluation by domain expert (10-20% sampling minimum)
6. Analyze failure modes and edge cases
7. Compare against acceptance thresholds
8. Document evaluation results and limitations

**Decision Gate:** Evaluation scores meet or exceed acceptance thresholds

**Output:** Evaluation report, failure mode analysis, limitations documentation

**Timeline:** 1-3 weeks depending on dataset size

**Responsible Parties:** AI QA Engineer (runs eval), domain expert (human eval), product manager (sets acceptance thresholds)

**Key Metrics by System Type:**
- **GenAI Systems:** Faithfulness (grounded in sources?), relevance (answers question?), coherence, safety
- **RAG Systems:** Retrieval quality (hit rate, MRR), generation quality, hallucination rate
- **Agents:** Task completion rate, tool usage correctness, human handoff rate, safety violations
- **ML Models:** Accuracy/F1/AUC by segment, fairness metrics, drift against baseline

## Process 2: Pilot & Monitoring

**Trigger:** Evaluation passed; ready for limited production deployment

**Inputs:** Approved system, monitoring configuration, runbook, support procedures

**Steps:**
1. Canary deployment to 1-5% of production traffic/users
2. Configure monitoring and alerting (quality metrics, cost, errors)
3. Monitor for 1-4 weeks (depends on use case frequency)
4. Collect user feedback and incident reports
5. Monitor KPIs (business metrics, cost, quality degradation)
6. Evaluate against success criteria
7. Decision point: expand, rollback, or iterate

**Decision Gate:** Pilot KPIs meet targets; no critical safety incidents; business sponsor approval

**Output:** Pilot success report, operational runbook, monitoring dashboards

**Timeline:** 1-4 weeks

**Responsible Parties:** Delivery lead (orchestrates), LLMOps/AgentOps (monitors), business sponsor (decides)

## Process 3: Red Teaming & Safety Testing

**Trigger:** High-risk system (agents, high-consequence decisions); before production

**Inputs:** System specification, threat model, safety requirements, attack scenarios

**Steps:**
1. Define threat model based on use case (what could go wrong?)
2. Identify attack scenarios (prompt injection, tool abuse, privilege escalation, goal misalignment)
3. Design test cases for each scenario
4. Execute manual red team testing (adversarial inputs)
5. Execute automated testing for known attack patterns
6. Document failures and successful attacks
7. Assess severity (Critical / High / Medium / Low)
8. Require mitigations for Critical/High vulnerabilities before production

**Decision Gate:** All critical/high severity vulnerabilities mitigated

**Output:** Red team report, vulnerability register, mitigation plan

**Timeline:** 2-4 weeks (10-20 hours of red team effort)

**Responsible Parties:** Red team (AI security specialists), system owner (mitigates), responsible AI officer (approves remediation)

**Common Agent Red Team Scenarios:**
- **Prompt Injection:** Can adversarial input override agent instructions?
- **Tool Abuse:** Can agent misuse permitted tools? (e.g., delete data, escalate privileges)
- **Goal Misalignment:** Can the agent be induced to pursue unintended goals?
- **Infinite Loops:** Does the agent detect and exit infinite loops?
- **Privilege Escalation:** Can the agent access resources outside its authorization?

## Process 4: A/B Testing Variants

**Trigger:** Multiple model/prompt versions competing; need data-driven selection

**Inputs:** Control version (baseline), treatment version (new approach), traffic allocation (typical: 10% test, 90% control)

**Steps:**
1. Define success metric (what wins?)
2. Calculate required sample size for statistical significance
3. Route traffic: 10% to variant, 90% to control (gradually increase variant if winning)
4. Collect metrics over 1-2 weeks minimum
5. Run significance test (is improvement statistically significant or just chance?)
6. If variant wins: promote to full deployment
7. If control wins: iterate on variant or rollback
8. Document learnings for future iterations

**Decision Gate:** Statistical significance achieved (p &lt; 0.05) plus business metric improvement

**Output:** A/B test report, winner promotion, learnings documented

**Timeline:** 1-3 weeks minimum

**Responsible Parties:** AI product manager (designs test), analyst (runs test), delivery lead (executes deployment decision)

## Process 5: Continuous Monitoring

**Trigger:** System deployed to production

**Inputs:** Monitoring dashboards, alerting thresholds, runbooks

**Steps:**
1. Daily monitoring of quality metrics (accuracy, relevance, hallucination rate)
2. Weekly analysis of cost trends and optimization opportunities
3. Monthly review of user feedback and incident trends
4. Quarterly external audit of responsible AI practices
5. Continuous drift detection (compare current to baseline)
6. Alert on threshold breaches (quality &lt; 85%, cost increase >20%, error rate > 5%)

**Escalation:** Critical alerts → on-call engineer → incident response; quality drift → product manager → iteration discussion

**Output:** Daily/weekly/monthly reports, incident tickets, optimization recommendations

**Timeline:** Continuous

**Responsible Parties:** LLMOps/AgentOps (operates), analyst (reports), product manager (drives iteration)

---

## Related

- [AI Operating Processes: Onboarding & Approval](19-part-09-operating-processes.md)
- [Operating Processes: Incident Response & Rollback](70-part-09-operating-processes-incident-response-rollback.md)
- [AI Delivery Lifecycle](13-part-03-ai-delivery-lifecycle.md)

## Sources

