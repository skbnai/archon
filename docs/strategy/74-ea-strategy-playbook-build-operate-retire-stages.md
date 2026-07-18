---
title: "EA Strategy Playbook: Build to Retire"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: ea-strategy-playbook-part2
maturity: expert
personas: ["Enterprise Architects", "Solution Architects", "Operations Teams"]
last_reviewed: 2026-07-19
covers_version: "N/A"
supersedes: []
tags: ["enterprise-architecture", "governance", "raci", "ea-lifecycle", "operations", "retirement"]
sources: []
---

Once architecture is designed and approved, EA transitions from author to guardian — ensuring what gets built matches what was approved, maintaining portfolio health through operations, and executing controlled retirements.

## Stage 4: Build / Deliver (varies: weeks to months)

**Strategic purpose:** The delivery team executes; EA's role is to ensure what gets built matches what was approved. This happens through structured compliance touchpoints that catch drift early, not through micromanagement.

**Key plays:**

1. **Run the 30% and 70% architecture reviews:** At 30%, review structural decisions — are the right systems being built in the right way? At 70%, review implementation fidelity — is the SAD being followed? Are integrations compliant? Log all deviations from the SAD as formal architecture exceptions with justification. Approve minor deviations; escalate significant ones to the ARB.

2. **Run the pre-production architecture sign-off:** Verify deployed architecture matches approved SAD — check for configuration drift. Confirm NFR testing completed: load test results, failover test, DR drill. Validate security controls: penetration test or DAST scan completed. Confirm observability stack is live: logging, metrics, alerts, distributed tracing. Update application portfolio inventory with production system details.

**Checklist - Architecture Governance During Delivery:**
- Log all architecture decisions made during build in the ADR register — include context, options considered, decision, and consequences
- Validate integration contracts (API specs, event schemas) against approved design

**Pre-Production Architecture Review:**
- Confirm all NFRs have been tested: load testing, failover testing, DR drill
- Review deployment pipeline and rollback procedure — rollback must be tested, not assumed

**RACI — Stage 4: Build**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Architecture review at 30% milestone | A | R | I | I | C |
| Architecture review at 70% milestone | A | R | I | I | C |
| Approve/escalate architecture exceptions | R | C | A | I | I |
| Pre-production compliance sign-off | A | R | C | I | I |
| Update application portfolio inventory | A | R | I | I | C |

**Key tip:** The 30% review is your most cost-effective intervention. Catching a structural mistake here saves 10x the cost of fixing it at 90%.

**Watch out:** 'We'll fix it post-launch' is the most common phrase that creates permanent technical debt. Hold the gate firmly.

**Gate: Architecture Compliance Gate (Pre-Production)**
- Output: Signed compliance sign-off. NFR tests passed. Observability confirmed.

---

## Stage 5: Operate / Run (ongoing; quarterly reviews)

**Strategic purpose:** Systems decay from the moment they go live — through technology obsolescence, integration drift, and accumulating exceptions. EA maintains portfolio hygiene through regular, systematic monitoring that catches issues before they become crises.

**Key plays:**

1. **Maintain the application portfolio:** Review portfolio metadata quarterly: ownership, criticality tier, data classification. Track all technology end-of-life dates — flag any component within 18 months of EOL. Monitor the architecture exceptions register — exceptions without resolution dates become permanent debt. Maintain integration dependency map as systems evolve.

2. **Run the quarterly compliance review:** Review standards compliance dashboard: security patch levels, API versions, EOL components. Review integration health metrics: error rates, latency trends, SLA performance. Review active architecture exceptions: resolve, extend, or escalate each one. Produce quarterly EA health summary for the CTO/CIO with RAG status per domain.

**Checklist - Portfolio Registration & Baseline:**
- Confirm system is registered in the application portfolio with full metadata
- Record business owner, technical owner, criticality tier, data classification (Tier 1 = mission critical, Tier 2 = business important, Tier 3 = supporting)
- Record licence details, contract renewal dates, and vendor SLA terms
- Baseline the total cost of ownership (annual run cost) for benchmarking

**Ongoing Compliance Monitoring:**
- Confirm system appears on the architecture standards compliance dashboard — track against security patches, EOL components, API version compliance
- Operational KPIs to track: EOL technology %, standards compliance %, integration error rate, system availability vs SLA

**RACI — Stage 5: Operate**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Quarterly portfolio metadata review | R | C | I | I | C |
| Technology EOL monitoring and flagging | R | I | I | I | C |
| Architecture exceptions management | A | C | I | I | R |
| Quarterly compliance review report | R | I | A | I | I |
| Escalation of critical compliance failures | R | I | A | C | I |

**Key tip:** Set automated alerts for technology EOL dates at 24, 18, and 12 months. Manual tracking always misses items.

**Watch out:** 'Temporary' exceptions that are never resolved. Every exception must have a named owner and a target resolution date.

**Gate: Annual Portfolio Health Review**
- Output: Annual portfolio health report. All exceptions reviewed. EOL risks escalated.

---

## Stage 6: Review / Optimise (annual cycle; 4–6 weeks)

**Strategic purpose:** Application rationalisation is the primary EA operational metric. It prevents the portfolio from growing unchecked and creates the strategic intelligence needed to direct future investment. Every system must earn its place in the portfolio annually.

**Key plays:**

1. **Run the application rationalisation assessment:** Score each system on Business Value (1–5): usage, strategic fit, revenue impact, regulatory necessity. Score each system on Technical Health (1–5): maintainability, security, support status, currency. Plot on the EA Value/Health 2×2 matrix to determine quadrant. Determine disposition: Retain / Invest / Migrate / Consolidate / Retire. Validate disposition with the business owner before finalizing.

2. **Apply the disposition matrix:**
   - High Value + High Health = RETAIN — maintain current investment, monitor annually
   - High Value + Low Health = INVEST — prioritise modernisation; technical debt is a business risk
   - Low Value + High Health = CONSOLIDATE/MIGRATE — find a better home for the capability
   - Low Value + Low Health = RETIRE — decommission; cost of ownership exceeds business return

**Checklist - Optimisation Actions (by disposition):**
- If Retain: document a refresh roadmap for the next 12 months
- If Invest: initiate a new Pitch/Demand request for the enhancement — restart the lifecycle
- If Migrate: define target platform and migration timeline, accounting for data migration and user transition
- If Consolidate: identify the target system and decommission plan for the survivor
- If Retire: proceed to Stage 7

**RACI — Stage 6: Review**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Application scoring (value + health) | R | C | I | C | C |
| 2×2 matrix analysis and disposition | R | C | I | C | – |
| Business owner validation of disposition | A | I | I | R | – |
| Approve rationalisation decisions | A | I | R | C | – |
| Update roadmap with rationalisation outputs | R | I | I | I | – |

**Key tip:** The business value score must be validated with the business owner. Technical health is EA's domain; business value is shared ownership. Use usage data, integration counts, and revenue attribution to anchor the conversation.

**Watch out:** Business owners will always score their system's value higher. Use data to drive objectivity.

**Gate: Annual Rationalisation Decision Gate**
- Output: Signed rationalisation decisions. Updated roadmap. Retire candidates identified.

---

## Stage 7: Retire / Decommission (3–12 months, depending on complexity)

**Strategic purpose:** Poor decommission practice creates orphaned integrations, data compliance risks, and zombie systems that keep drawing run cost long after they should have been switched off. Every retirement is a formal project.

**Key plays:**

1. **Dependency resolution:** Produce the full dependency map: every upstream producer and downstream consumer. Notify all dependent teams with minimum 90-day decommission notice. Confirm every integration has a migration path — no orphaned consumers at switch-off. Validate replacement system can handle the redirected load before cutover.

2. **Data, commercial, and portfolio close-out:** Define and execute data disposition: archive, migrate, or delete per regulatory requirements. Confirm GDPR/legal hold requirements with Legal before any data deletion. Issue formal contract termination notice to all vendors (check notice periods: 30–90 days). Decommission all infrastructure: servers, VMs, cloud resources, DNS, firewall rules. Remove system from all access control lists, identity directories, and monitoring. Archive all documentation (SAD, ADRs, runbooks) for minimum 7 years. Remove from application portfolio. Update all architecture diagrams. Issue decommission certificate.

**Checklist - Dependency & Impact Analysis:**
- Assess impact on business processes — obtain business sign-off on the transition plan

**Data & Knowledge Management:**
- Define data retention policy: archive, migrate, or delete per regulatory requirements
- Complete data migration to the target system and validate data integrity
- Transfer operational knowledge to the support team for any replacement system

**Commercial & Contractual Close-Out:**
- Confirm licence termination date and notify vendor — check contract notice periods
- Terminate SLAs and support contracts with confirmation from the vendor
- Recover and decommission all infrastructure (servers, VMs, cloud resources)
- Remove the system from all access control lists, firewalls, and identity directories

**Final Sign-Off & Portfolio Close:**
- Record lessons learned: what could have been retired sooner? what dependency issues arose?
- Update the TCO reduction tracker — record the cost saving realised from decommission

**RACI — Stage 7: Retire**

| Task | EA | Solution Architect | ARB | Business Owner | Delivery Lead |
|------|-----|------------------|-----|---|---|
| Produce full dependency map | R | C | I | I | C |
| Notify dependent teams (90-day notice) | R | C | I | A | C |
| Data disposition planning | A | R | I | C | I |
| Contract and vendor termination | I | I | I | A | R |
| Infrastructure decommission | A | C | I | I | R |
| Portfolio and documentation close-out | R | C | A | I | I |

**Key tip:** Run a lessons-learned session after every major decommission. Insights on dependency discovery and data migration improve every future retirement.

**Watch out:** Access not removed is an immediate security and audit finding. Build access removal into the decommission runbook as a mandatory last step.

**Gate: Decommission Completion Gate**
- Output: Decommission certificate signed by EA, Platform Owner, Legal, and Business Owner.

---

## Related

- [EA Strategy Playbook: Pitch to Design](32-ea-strategy-playbook.md)
- Architecture Review Board (ARB) Governance — not yet a standalone canonical page

## Sources

*No external sources; this is a consolidated operational playbook.*
