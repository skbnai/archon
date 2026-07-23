---
title: "AI Operating Processes: Onboarding & Approval"
doc_type: guide
domain: strategy
status: current
canonical: true
topic_id: part-09-operating-processes
maturity: practitioner
personas: [program-manager, delivery-lead, governance-officer]
last_reviewed: 2026-07-19
covers_version: "as of 2026-07-14"
supersedes:
  - docs/enterprise-ai-report/part-09-operating-processes.md
tags: ["operating-processes", "approval-workflow", "governance", "ai-delivery", "human-oversight"]
sources: []
pagination_next: strategy/part-09-operating-processes-rollout-evaluation-redteam
---

# AI Operating Processes: Onboarding & Approval

Standardized operating processes ensure consistent, auditable governance of AI initiatives from intake through approval to deployment.

## Process 1: AI Use Case Intake & Portfolio Management

**Trigger:** Team identifies potential AI use case

**Inputs:** Use case description, estimated business impact, required resources, proposed timeline

**Steps:**
1. Business analyst conducts initial scoping call
2. Portfolio board prioritization against other use cases
3. Risk classification (Low / Medium / High / Critical)
4. Assignment to programme lane based on priority and risk
5. Kickoff with assigned delivery team and sponsors

**Decision Gate:** Portfolio board approves or defers use case

**Output:** Use case charter with business case, success metrics, resource allocation

**Timeline:** 1-2 weeks

**Responsible Parties:** Business owner (initiates), Portfolio board (approves), Programme manager (executes)

## Process 2: Prompt Approval Workflow

**Trigger:** Team develops a system prompt requiring deployment

**Inputs:** Prompt text, intended use case, evaluation results, risk classification

**Steps:**
1. Developer completes prompt template (role, task, constraints, examples)
2. Peer review within team (2 reviewers)
3. Responsible AI review (fairness, bias, harmful content)
4. Security review (prompt injection testing)
5. Versioning in prompt registry
6. Approval for production deployment

**Decision Gate:** Responsible AI officer and security sign-off

**Output:** Approved prompt version in registry, deployment authorization

**Timeline:** 3-5 days for standard prompts; 5-10 days for high-risk

**Responsible Parties:** Prompt owner (develops), peer reviewers (QA), responsible AI officer (approves)

## Process 3: Agent Approval (High-Risk)

**Trigger:** Team proposes autonomous agent for production

**Inputs:** Agent Charter (goal, task decomposition, tool set, constraints), safety testing results, evaluation metrics

**Steps:**
1. Agent owner completes Agent Charter (template required)
2. Technical review: architecture, tool configuration, safety design
3. Responsible AI review: fairness, ethical implications, harm prevention
4. Security review: identity, authorization, tool abuse testing
5. Business review: approval by business sponsor
6. Agent Governance Board final approval (monthly meeting)
7. Canary deployment authorization (production read-only first)

**Decision Gate:** Agent Governance Board approves or requires modifications

**Output:** Approved Agent Charter, deployment authorization for canary, operations runbook

**Timeline:** 10-15 days minimum (requires monthly Governance Board meeting)

**Responsible Parties:** Agent owner (develops), technical architect (reviews), responsible AI (reviews), business sponsor (approves), governance board (final approval)

**Agent Charter Components:**
- Agent name, purpose, primary goal
- Sub-goals and explicit non-goals
- Tool set and permissions (least privilege)
- Memory constraints and reasoning strategy
- Human approval gates for high-impact decisions
- Failure modes and mitigations
- Escalation procedures and kill switches

## Process 4: Model Onboarding & Governance

**Trigger:** Team wants to deploy a pre-trained or fine-tuned model

**Inputs:** Model card, fairness/bias assessment, performance benchmarks, data source documentation

**Steps:**
1. Data quality assessment (training data lineage, potential bias)
2. Fairness & bias evaluation against protected groups
3. Risk classification (Low / Medium / High / Critical)
4. Model card completion (metadata, limitations, use cases, ethical considerations)
5. Responsible AI review
6. Security review (adversarial robustness)
7. Model registry onboarding (versioning, tracking)
8. Deployment authorization

**Decision Gate:** Model governance board approves based on risk level

**Output:** Approved model card, model registered in registry, deployment authorization

**Timeline:** 5-10 days

**Responsible Parties:** Model owner (develops), data team (assesses), responsible AI (reviews), governance board (approves)

## Process 5: Data Governance for AI

**Trigger:** New data source identified for AI use (training, inference, knowledge base)

**Inputs:** Data schema, data source description, quality metrics, governance classification

**Steps:**
1. Data ownership assignment
2. PII and sensitive data identification
3. Data quality assessment
4. Access control design
5. Data freshness and maintenance plan
6. Responsible AI review (bias potential)
7. Data governance approval
8. Data lineage documentation

**Decision Gate:** Chief Data Officer approves for use in AI

**Output:** Data registered in data catalogue, access controls configured, data quality baseline established

**Timeline:** 1-2 weeks

**Responsible Parties:** Data owner (owns data), data governance team (reviews), responsible AI (assesses bias risk)

---

## Related

- [Operating Processes: Rollout, Evaluation & Red Teaming](69-part-09-operating-processes-rollout-evaluation-redteam.md)
- [Operating Processes: Incident Response & Rollback](70-part-09-operating-processes-incident-response-rollback.md)
- [Governance Model](16-part-06-governance.md)
- [Operating Models](12-part-02-operating-models.md)

## Sources

